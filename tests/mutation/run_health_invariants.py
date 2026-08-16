#!/usr/bin/env python3
"""Mutation-prove critical Stage 2 Vessel health detectors.

Mutations exist only in the CI checkout. Each exact production seam must make
its targeted health regression fail, then the source is restored byte-for-byte
and the same regression must pass. All proofs run even if one fails.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Spec:
    name: str
    invariant: str
    old: str
    new: str
    nodeid: str


@dataclass
class Result:
    name: str
    invariant: str
    nodeid: str
    source_match_count: int
    red_returncode: int | None = None
    target_failed: bool = False
    restored_green: bool = False
    restored_exact: bool = False
    status: str = "ERROR"
    detail: str = ""


HEALTH = "src/grox/health.py"

SPECS: tuple[Spec, ...] = (
    Spec(
        "health-detector-isolation",
        "One broken health detector must become one finding rather than abort the report.",
        "        except Exception as exc:\n",
        "        except () as exc:\n",
        "tests/unit/test_health.py::VesselHealthTests::test_one_detector_exception_does_not_blind_other_results",
    ),
    Spec(
        "health-interrupted-state",
        "Interrupted Mission or graph state must be surfaced for bounded recovery.",
        "        if interrupted:\n            return HealthCheck(\n",
        "        if False and interrupted:\n            return HealthCheck(\n",
        "tests/unit/test_health.py::VesselHealthTests::test_operational_state_warns_on_interrupted_mission",
    ),
    Spec(
        "health-unsnapshotted-runtime",
        "Persisted runtime history without a recovery snapshot must not be reported ready.",
        "        if not snapshots:\n            if runtime_rows:\n",
        "        if not snapshots:\n            if False and runtime_rows:\n",
        "tests/unit/test_health.py::VesselHealthTests::test_persistence_warns_when_runtime_history_has_no_snapshot",
    ),
    Spec(
        "health-authority-widening",
        "Persisted non-Repair Orders carrying mutation grants must be reported as authority failure.",
        "                    if str(row[\"mode\"]) != \"repair\" and grants & {\"fs_write\", \"mcp_mutate\"}:\n",
        "                    if False and str(row[\"mode\"]) != \"repair\" and grants & {\"fs_write\", \"mcp_mutate\"}:\n",
        "tests/unit/test_health.py::VesselHealthTests::test_authority_detector_rejects_non_repair_mutation_grant_in_persisted_order",
    ),
    Spec(
        "health-memory-provenance",
        "Active memory without valid provenance must be reported as integrity failure.",
        "                if not isinstance(provenance, dict) or not provenance:\n                    problems.append(f\"memory {row['id']} lacks valid provenance\")\n",
        "                if False:\n                    problems.append(f\"memory {row['id']} lacks valid provenance\")\n",
        "tests/unit/test_health.py::VesselHealthTests::test_memory_detector_rejects_invalid_active_provenance",
    ),
    Spec(
        "health-source-version-drift",
        "Source/package version disagreement must be reported as critical failure.",
        "        if package_version != __version__ or marker not in source_init:\n",
        "        if False:\n",
        "tests/unit/test_health.py::VesselHealthTests::test_source_version_detector_rejects_metadata_drift",
    ),
    Spec(
        "health-recovery-fail-closed",
        "Critical health failures must keep reconstitution paused.",
        "        if blockers:\n            return HealthCheck(\n",
        "        if False and blockers:\n            return HealthCheck(\n",
        "tests/unit/test_health.py::VesselHealthTests::test_recovery_readiness_fails_closed_on_critical_health_failure",
    ),
)


def run(nodeid: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", nodeid],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )


def target_failed(nodeid: str, cp: subprocess.CompletedProcess[str]) -> bool:
    output = cp.stdout + "\n" + cp.stderr
    leaf = nodeid.rsplit("::", 1)[-1]
    return cp.returncode != 0 and leaf in output and "failed" in output.lower()


def prove(spec: Spec) -> Result:
    path = ROOT / HEALTH
    original = path.read_text(encoding="utf-8")
    count = original.count(spec.old)
    result = Result(spec.name, spec.invariant, spec.nodeid, count)
    if count != 1:
        result.detail = f"source drift: expected exactly one mutation seam, found {count}"
        return result
    try:
        path.write_text(original.replace(spec.old, spec.new, 1), encoding="utf-8")
        red = run(spec.nodeid)
        result.red_returncode = red.returncode
        result.target_failed = target_failed(spec.nodeid, red)
    except Exception as exc:
        result.detail = f"mutation execution error: {type(exc).__name__}: {exc}"
    finally:
        path.write_text(original, encoding="utf-8")
        result.restored_exact = path.read_text(encoding="utf-8") == original

    if not result.restored_exact:
        result.detail = "failed to restore exact source bytes"
        return result
    green = run(spec.nodeid)
    result.restored_green = green.returncode == 0
    if result.target_failed and result.restored_green:
        result.status = "KILLED"
        result.detail = "target health regression red under mutation and green after exact restoration"
    elif not result.target_failed:
        result.status = "SURVIVED"
        result.detail = "target health detector did not fail under mutation"
    else:
        result.status = "RESTORE_FAILED"
        result.detail = "target health detector did not return green after restoration"
    return result


def main() -> int:
    results = []
    for spec in SPECS:
        result = prove(spec)
        results.append(result)
        print(f"HEALTH_MUTATION {result.name}: {result.status} — {result.detail}")

    clean = subprocess.run(
        ["git", "diff", "--exit-code", "--", HEALTH],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    report = {
        "schema": "grox-health-invariant-mutations-v1",
        "mutations": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "killed": sum(result.status == "KILLED" for result in results),
            "survived": sum(result.status == "SURVIVED" for result in results),
            "other_failures": sum(result.status not in {"KILLED", "SURVIVED"} for result in results),
            "source_restored_clean": clean,
        },
    }
    print("HEALTH_MUTATION_MATRIX_JSON=" + json.dumps(report, sort_keys=True))
    return 0 if all(result.status == "KILLED" for result in results) and clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
