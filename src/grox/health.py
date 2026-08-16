from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
import tomllib
from typing import Callable

from . import __version__
from .crew.roster import CrewRoster
from .persistence import PersistenceManager
from .tools.workspace import docker_backend_available, namespace_backend_available


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class HealthCheck:
    check_id: str
    domain: str
    status: str
    detail: str
    critical: bool = False
    evidence: dict | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HealthReport:
    disposition: str
    checks: tuple[HealthCheck, ...]
    generated_at: str
    vessel_root: str

    def to_dict(self) -> dict:
        counts = {status: sum(check.status == status for check in self.checks) for status in (PASS, WARN, FAIL, UNKNOWN)}
        return {
            "disposition": self.disposition,
            "generated_at": self.generated_at,
            "vessel_root": self.vessel_root,
            "summary": counts,
            "checks": [check.to_dict() for check in self.checks],
        }


class VesselHealth:
    """Read-only Vessel diagnostic surface built from existing GroX truth.

    The health surface never opens the operational database in write mode and
    never performs repair. Each detector is isolated so one broken detector is
    itself a finding rather than a reason to lose the rest of the report.
    """

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.db_path = self.root / "configs/state/grox.sqlite3"

    def collect(self) -> HealthReport:
        checks: list[HealthCheck] = []
        detectors: tuple[tuple[str, str, bool, Callable[[], HealthCheck]], ...] = (
            ("command_integrity", "command", True, self._check_command_integrity),
            ("operational_state", "operations", True, self._check_operational_state),
            ("persistence_readiness", "persistence", False, self._check_persistence_readiness),
            ("authority_integrity", "authority", True, self._check_authority_integrity),
            ("memory_integrity", "memory", True, self._check_memory_integrity),
            ("source_version", "source", True, self._check_source_version),
            ("source_repository", "source", False, self._check_source_repository),
            ("verification_readiness", "verification", True, self._check_verification_readiness),
            ("isolation_readiness", "environment", False, self._check_isolation_readiness),
        )
        for check_id, domain, critical, detector in detectors:
            checks.append(self._safe(check_id, domain, critical, detector))
        checks.append(self._recovery_readiness(checks))
        return HealthReport(
            disposition=self._disposition(checks),
            checks=tuple(checks),
            generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            vessel_root=str(self.root),
        )

    @staticmethod
    def _disposition(checks: list[HealthCheck]) -> str:
        if any(check.status == FAIL for check in checks):
            return "UNHEALTHY"
        if any(check.status in {WARN, UNKNOWN} for check in checks):
            return "DEGRADED"
        return "HEALTHY"

    @staticmethod
    def _safe(check_id: str, domain: str, critical: bool, detector: Callable[[], HealthCheck]) -> HealthCheck:
        try:
            result = detector()
        except Exception as exc:
            return HealthCheck(
                check_id,
                domain,
                FAIL if critical else UNKNOWN,
                f"detector raised {type(exc).__name__}: {exc}",
                critical=critical,
                recommendation="Inspect the named detector; health inspection did not attempt repair.",
            )
        if result.check_id != check_id or result.domain != domain:
            return HealthCheck(
                check_id,
                domain,
                FAIL if critical else UNKNOWN,
                "detector returned mismatched identity",
                critical=critical,
            )
        return result

    def _open_db_read_only(self) -> sqlite3.Connection | None:
        if not self.db_path.exists():
            return None
        uri = f"file:{self.db_path.resolve().as_posix()}?mode=ro"
        db = sqlite3.connect(uri, uri=True)
        db.row_factory = sqlite3.Row
        return db

    def _check_command_integrity(self) -> HealthCheck:
        manifest_path = self.root / "configs/crew/company-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        roster = CrewRoster(self.root / "configs/crew/dossiers")
        ids = {d.crew_id for d in roster.all()}
        expected = int(manifest["total_expected_dossiers"])
        declared = set(manifest["roles"]) | set(manifest.get("native_support_roles", []))
        verifier_count = sum(bool(d.verification) and d.crew_id == "independent-verifier" for d in roster.all())
        problems: list[str] = []
        if len(ids) != expected:
            problems.append(f"expected {expected} Standing Crew, found {len(ids)}")
        if ids != declared:
            missing = sorted(declared - ids)
            extra = sorted(ids - declared)
            problems.append(f"manifest/roster mismatch missing={missing} extra={extra}")
        if verifier_count != 1:
            problems.append(f"expected one native independent-verifier, found {verifier_count}")
        if problems:
            return HealthCheck("command_integrity", "command", FAIL, "; ".join(problems), True)
        return HealthCheck(
            "command_integrity",
            "command",
            PASS,
            f"GorXu command boundary source is consistent with {len(ids)} Standing Crew",
            True,
            {"standing_crew": len(ids), "native_independent_verifier": verifier_count},
        )

    def _check_operational_state(self) -> HealthCheck:
        db = self._open_db_read_only()
        if db is None:
            return HealthCheck(
                "operational_state",
                "operations",
                PASS,
                "no private operational database is present; source-only Vessel has no runtime state to recover",
                True,
                {"database_present": False},
            )
        try:
            integrity = str(db.execute("PRAGMA integrity_check").fetchone()[0])
            if integrity != "ok":
                return HealthCheck("operational_state", "operations", FAIL, f"SQLite integrity_check={integrity}", True)
            mission_counts = {str(row["status"]): int(row["n"]) for row in db.execute("SELECT status,COUNT(*) n FROM missions GROUP BY status")}
            node_counts = {str(row["status"]): int(row["n"]) for row in db.execute("SELECT status,COUNT(*) n FROM graph_nodes GROUP BY status")}
        finally:
            db.close()
        interrupted = mission_counts.get("interrupted", 0) + node_counts.get("interrupted", 0)
        if interrupted:
            return HealthCheck(
                "operational_state",
                "operations",
                WARN,
                f"SQLite integrity ok; {interrupted} interrupted Mission/graph record(s) require bounded recovery",
                True,
                {"database_present": True, "mission_status": mission_counts, "graph_node_status": node_counts},
                "Use the existing GroX resume/recovery path; do not recreate interrupted work from memory.",
            )
        return HealthCheck(
            "operational_state",
            "operations",
            PASS,
            "SQLite integrity ok; no interrupted Mission/graph records",
            True,
            {"database_present": True, "mission_status": mission_counts, "graph_node_status": node_counts},
        )

    def _runtime_state_rows(self) -> int:
        db = self._open_db_read_only()
        if db is None:
            return 0
        try:
            return sum(
                int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("missions", "orders", "evidence", "memories", "crew_performance")
            )
        finally:
            db.close()

    def _check_persistence_readiness(self) -> HealthCheck:
        snapshot_dir = self.root / "configs/state/snapshots"
        snapshots = sorted(snapshot_dir.glob("*.groxstate"), key=lambda path: path.stat().st_mtime, reverse=True) if snapshot_dir.exists() else []
        runtime_rows = self._runtime_state_rows()
        if not snapshots:
            if runtime_rows:
                return HealthCheck(
                    "persistence_readiness",
                    "persistence",
                    WARN,
                    f"private runtime state has {runtime_rows} record(s) but no recovery snapshot is present",
                    False,
                    {"runtime_rows": runtime_rows, "snapshot_present": False},
                    "Create and verify a private `.groxstate` snapshot before relying on host-loss recovery.",
                )
            return HealthCheck(
                "persistence_readiness",
                "persistence",
                PASS,
                "no persisted operational history requires recovery snapshot coverage",
                False,
                {"runtime_rows": 0, "snapshot_present": False},
            )
        latest = snapshots[0]
        result = PersistenceManager(self.root).verify_snapshot(latest)
        if result.valid:
            return HealthCheck(
                "persistence_readiness",
                "persistence",
                PASS,
                f"latest private snapshot verifies against current Vessel source: {latest.name}",
                False,
                {"snapshot": latest.name, "state_sha256": result.state_sha256},
            )
        detail = result.error or "snapshot verification failed"
        status = WARN if "source" in detail.lower() or "ancestor" in detail.lower() else FAIL
        return HealthCheck(
            "persistence_readiness",
            "persistence",
            status,
            f"latest snapshot is not directly restorable: {detail}",
            False,
            {"snapshot": latest.name},
            "Create a current-source snapshot or use only the explicit compatible-ancestor recovery path when justified.",
        )

    def _check_authority_integrity(self) -> HealthCheck:
        policy_path = self.root / "configs/tool-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        problems: list[str] = []
        if int(policy.get("version", 0)) != 2:
            problems.append("Tool Gateway host policy must be version 2")
        if policy.get("secrets", {}).get("persistence") != "memory-only":
            problems.append("secret persistence is not memory-only")
        db = self._open_db_read_only()
        checked_orders = 0
        if db is not None:
            try:
                for row in db.execute("SELECT order_id,mode,payload FROM orders"):
                    checked_orders += 1
                    payload = json.loads(row["payload"])
                    grants = set(payload.get("allowed_actions", []))
                    if str(row["mode"]) != "repair" and grants & {"fs_write", "mcp_mutate"}:
                        problems.append(f"non-Repair Order {row['order_id']} carries mutation grant(s) {sorted(grants & {'fs_write', 'mcp_mutate'})}")
            finally:
                db.close()
        if problems:
            return HealthCheck("authority_integrity", "authority", FAIL, "; ".join(problems), True, {"orders_checked": checked_orders})
        return HealthCheck(
            "authority_integrity",
            "authority",
            PASS,
            f"host policy boundary valid; {checked_orders} persisted Order(s) checked for mutation-grant widening",
            True,
            {"orders_checked": checked_orders, "tool_policy_version": 2, "secret_persistence": "memory-only"},
        )

    def _check_memory_integrity(self) -> HealthCheck:
        db = self._open_db_read_only()
        if db is None:
            return HealthCheck("memory_integrity", "memory", PASS, "no private memory state is present", True, {"active_memories": 0})
        problems: list[str] = []
        active = 0
        try:
            for row in db.execute("SELECT id,kind,scope,crew_id,memory_key,provenance,confidence,active FROM memories"):
                if int(row["active"]) != 1:
                    continue
                active += 1
                try:
                    provenance = json.loads(row["provenance"])
                except (TypeError, json.JSONDecodeError):
                    provenance = None
                if not isinstance(provenance, dict) or not provenance:
                    problems.append(f"memory {row['id']} lacks valid provenance")
                if str(row["kind"]) not in {"semantic", "procedural", "vessel"}:
                    problems.append(f"memory {row['id']} has invalid kind {row['kind']!r}")
                if str(row["scope"]) not in {"crew", "vessel"}:
                    problems.append(f"memory {row['id']} has invalid scope {row['scope']!r}")
                if str(row["scope"]) == "crew" and not row["crew_id"]:
                    problems.append(f"memory {row['id']} is crew-scoped without crew_id")
                if str(row["scope"]) == "vessel" and row["crew_id"] is not None:
                    problems.append(f"memory {row['id']} is Vessel-scoped but carries crew_id")
                confidence = float(row["confidence"])
                if not 0.0 <= confidence <= 1.0:
                    problems.append(f"memory {row['id']} confidence out of bounds")
            duplicates = db.execute(
                """SELECT kind,scope,COALESCE(crew_id,''),memory_key,COUNT(*) n FROM memories
                   WHERE active=1 GROUP BY kind,scope,COALESCE(crew_id,''),memory_key HAVING COUNT(*)>1"""
            ).fetchall()
            if duplicates:
                problems.append(f"{len(duplicates)} active memory key collision(s)")
        finally:
            db.close()
        if problems:
            return HealthCheck("memory_integrity", "memory", FAIL, "; ".join(problems), True, {"active_memories": active})
        return HealthCheck("memory_integrity", "memory", PASS, f"{active} active memory record(s) have valid bounded metadata and provenance", True, {"active_memories": active})

    def _check_source_version(self) -> HealthCheck:
        pyproject = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))
        package_version = str(pyproject["project"]["version"])
        source_init = (self.root / "src/grox/__init__.py").read_text(encoding="utf-8")
        marker = f"__version__='{package_version}'"
        if package_version != __version__ or marker not in source_init:
            return HealthCheck(
                "source_version",
                "source",
                FAIL,
                f"version disagreement package={package_version} imported={__version__}",
                True,
                {"package_version": package_version, "imported_version": __version__},
            )
        return HealthCheck("source_version", "source", PASS, f"source/package version aligned at {package_version}", True, {"version": package_version})

    def _check_source_repository(self) -> HealthCheck:
        if not (self.root / ".git").exists():
            return HealthCheck(
                "source_repository",
                "source",
                UNKNOWN,
                "Git metadata is unavailable in this materialization; source commit binding cannot be observed locally",
                False,
            )
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, text=True, capture_output=True, timeout=5)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=self.root, text=True, capture_output=True, timeout=5)
        if head.returncode != 0 or status.returncode != 0:
            return HealthCheck("source_repository", "source", UNKNOWN, "Git source state could not be read", False)
        dirty = [line for line in status.stdout.splitlines() if line.strip()]
        return HealthCheck(
            "source_repository",
            "source",
            WARN if dirty else PASS,
            f"Git HEAD {head.stdout.strip()[:12]}; {'working tree has changes' if dirty else 'working tree clean'}",
            False,
            {"head": head.stdout.strip(), "dirty_entries": len(dirty)},
            "Review uncommitted source before treating the checkout as canonical." if dirty else None,
        )

    def _check_verification_readiness(self) -> HealthCheck:
        workflow = (self.root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        harness = self.root / "tests/mutation/run_critical_invariants.py"
        matrix = self.root / "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md"
        requirements = {
            "python_3_11": "'3.11'" in workflow,
            "python_3_12": "'3.12'" in workflow,
            "python_3_13": "'3.13'" in workflow,
            "python_3_14": "'3.14'" in workflow,
            "wheel_bootstrap": "Wheel bootstrap portability" in workflow,
            "mutation_step": "Critical invariant mutation proof" in workflow,
            "mutation_harness": harness.is_file(),
            "mutation_matrix": matrix.is_file(),
        }
        missing = sorted(name for name, present in requirements.items() if not present)
        if missing:
            return HealthCheck("verification_readiness", "verification", FAIL, f"verification source contract missing: {missing}", True, requirements)
        return HealthCheck(
            "verification_readiness",
            "verification",
            PASS,
            "canonical regression, wheel-bootstrap, and critical mutation-proof contracts are present in source",
            True,
            requirements,
        )

    def _check_isolation_readiness(self) -> HealthCheck:
        policy = json.loads((self.root / "configs/tool-policy.json").read_text(encoding="utf-8"))
        workspace = policy.get("workspace", {})
        if not workspace.get("enabled"):
            return HealthCheck("isolation_readiness", "environment", WARN, "governed workspace execution is disabled by host policy", False)
        image = workspace.get("docker_image")
        namespace = namespace_backend_available()
        docker = docker_backend_available(image) if image else False
        if namespace or docker:
            return HealthCheck(
                "isolation_readiness",
                "environment",
                PASS,
                f"qualified workspace isolation available via {'namespace' if namespace else 'docker'} backend",
                False,
                {"namespace": namespace, "docker": docker, "docker_image": image},
            )
        return HealthCheck(
            "isolation_readiness",
            "environment",
            WARN,
            "no qualified A5 workspace backend is currently available; governed shell/code execution will fail closed",
            False,
            {"namespace": False, "docker": False, "docker_image": image},
            "Commission a qualified namespace backend or pre-provision the pinned Docker fallback before workspace execution.",
        )

    @staticmethod
    def _recovery_readiness(checks: list[HealthCheck]) -> HealthCheck:
        by_id = {check.check_id: check for check in checks}
        blockers = [
            check_id
            for check_id in ("command_integrity", "operational_state", "authority_integrity", "memory_integrity", "source_version")
            if by_id.get(check_id) and by_id[check_id].status == FAIL
        ]
        if blockers:
            return HealthCheck(
                "recovery_readiness",
                "recovery",
                FAIL,
                f"reconstitution must remain paused; critical health blocker(s): {blockers}",
                True,
                {"blockers": blockers},
            )
        interrupted = by_id.get("operational_state")
        persistence = by_id.get("persistence_readiness")
        reasons: list[str] = []
        if interrupted and interrupted.status == WARN:
            reasons.append("interrupted operational state requires bounded resume")
        if persistence and persistence.status in {WARN, UNKNOWN}:
            reasons.append("persistence evidence is not fully current")
        if reasons:
            return HealthCheck(
                "recovery_readiness",
                "recovery",
                WARN,
                "; ".join(reasons),
                True,
                {"reasons": reasons},
                "Use full bounded reconstitution until all required recovery evidence is current.",
            )
        return HealthCheck("recovery_readiness", "recovery", PASS, "no critical health evidence blocks bounded reconstitution", True)
