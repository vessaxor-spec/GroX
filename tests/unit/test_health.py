from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from grox import cli
from grox.health import FAIL, PASS, UNKNOWN, HealthCheck, VesselHealth
from grox.state import StateStore, now


REPO = Path(__file__).resolve().parents[2]


def health_vessel() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "configs/crew").mkdir(parents=True)
    shutil.copytree(REPO / "configs/crew/dossiers", root / "configs/crew/dossiers")
    shutil.copy2(REPO / "configs/crew/company-manifest.json", root / "configs/crew/company-manifest.json")
    shutil.copy2(REPO / "configs/tool-policy.json", root / "configs/tool-policy.json")
    shutil.copy2(REPO / "pyproject.toml", root / "pyproject.toml")
    (root / "src/grox").mkdir(parents=True)
    shutil.copy2(REPO / "src/grox/__init__.py", root / "src/grox/__init__.py")
    (root / ".github/workflows").mkdir(parents=True)
    shutil.copy2(REPO / ".github/workflows/ci.yml", root / ".github/workflows/ci.yml")
    (root / "tests/mutation").mkdir(parents=True)
    shutil.copy2(REPO / "tests/mutation/run_critical_invariants.py", root / "tests/mutation/run_critical_invariants.py")
    (root / "docs/verification").mkdir(parents=True)
    shutil.copy2(REPO / "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md", root / "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md")
    return td, root


class VesselHealthTests(unittest.TestCase):
    def collect(self, root: Path):
        with patch("grox.health.namespace_backend_available", return_value=True), patch(
            "grox.health.docker_backend_available", return_value=False
        ):
            return VesselHealth(root).collect()

    def test_source_only_health_uses_roster_without_creating_runtime_state(self) -> None:
        td, root = health_vessel()
        try:
            report = self.collect(root)
            by_id = {check.check_id: check for check in report.checks}
            self.assertEqual(by_id["command_integrity"].status, PASS)
            self.assertEqual(by_id["command_integrity"].evidence["standing_crew"], 82)
            self.assertEqual(by_id["operational_state"].status, PASS)
            self.assertEqual(by_id["memory_integrity"].status, PASS)
            self.assertEqual(by_id["source_version"].status, PASS)
            self.assertEqual(by_id["verification_readiness"].status, PASS)
            self.assertEqual(by_id["source_repository"].status, UNKNOWN)
            self.assertFalse((root / "configs/state/grox.sqlite3").exists())
        finally:
            td.cleanup()

    def test_one_detector_exception_does_not_blind_other_results(self) -> None:
        td, root = health_vessel()
        try:
            with patch.object(VesselHealth, "_check_command_integrity", side_effect=RuntimeError("injected detector failure")), patch(
                "grox.health.namespace_backend_available", return_value=True
            ), patch("grox.health.docker_backend_available", return_value=False):
                report = VesselHealth(root).collect()
            by_id = {check.check_id: check for check in report.checks}
            self.assertEqual(by_id["command_integrity"].status, FAIL)
            self.assertIn("injected detector failure", by_id["command_integrity"].detail)
            self.assertEqual(by_id["source_version"].status, PASS)
            self.assertEqual(by_id["verification_readiness"].status, PASS)
            self.assertEqual(report.disposition, "UNHEALTHY")
        finally:
            td.cleanup()

    def test_health_read_does_not_mutate_existing_sqlite_state(self) -> None:
        td, root = health_vessel()
        try:
            store = StateStore(root / "configs/state/grox.sqlite3")
            store.create_mission("MSN-health-readonly", "read only health", "inspect", "low")
            store.update_mission("MSN-health-readonly", "completed", "done")
            store.close()
            db_path = root / "configs/state/grox.sqlite3"
            before = hashlib.sha256(db_path.read_bytes()).hexdigest()
            self.collect(root)
            after = hashlib.sha256(db_path.read_bytes()).hexdigest()
            self.assertEqual(before, after)
        finally:
            td.cleanup()

    def test_memory_detector_rejects_invalid_active_provenance(self) -> None:
        td, root = health_vessel()
        try:
            store = StateStore(root / "configs/state/grox.sqlite3")
            store.db.execute(
                """INSERT INTO memories(kind,scope,crew_id,task_class,memory_key,content,provenance,confidence,active,supersedes_id,created_at,updated_at)
                   VALUES('semantic','vessel',NULL,NULL,'bad','bad','not-json',0.8,1,NULL,?,?)""",
                (now(), now()),
            )
            store.db.commit()
            store.close()
            result = VesselHealth(root)._check_memory_integrity()
            self.assertEqual(result.status, FAIL)
            self.assertIn("valid provenance", result.detail)
        finally:
            td.cleanup()

    def test_authority_detector_rejects_non_repair_mutation_grant_in_persisted_order(self) -> None:
        td, root = health_vessel()
        try:
            store = StateStore(root / "configs/state/grox.sqlite3")
            t = now()
            payload = {
                "order_id": "ORD-forged-health",
                "mission_id": "MSN-forged-health",
                "mode": "inspect",
                "assigned_crew": "code-reviewer",
                "allowed_actions": ["fs_read", "fs_write"],
            }
            store.db.execute(
                "INSERT INTO orders(order_id,mission_id,crew_id,mode,status,payload,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                ("ORD-forged-health", "MSN-forged-health", "code-reviewer", "inspect", "issued", json.dumps(payload), t, t),
            )
            store.db.commit()
            store.close()
            result = VesselHealth(root)._check_authority_integrity()
            self.assertEqual(result.status, FAIL)
            self.assertIn("non-Repair Order", result.detail)
            self.assertIn("fs_write", result.detail)
        finally:
            td.cleanup()

    def test_source_version_detector_rejects_metadata_drift(self) -> None:
        td, root = health_vessel()
        try:
            text = (root / "pyproject.toml").read_text(encoding="utf-8")
            mutated = text.replace('version = "0.7.1"', 'version = "9.9.9"')
            self.assertNotEqual(mutated, text, "fixture mutation must actually change package metadata")
            (root / "pyproject.toml").write_text(mutated, encoding="utf-8")
            result = VesselHealth(root)._check_source_version()
            self.assertEqual(result.status, FAIL)
            self.assertIn("version disagreement", result.detail)
        finally:
            td.cleanup()

    def test_recovery_readiness_fails_closed_on_critical_health_failure(self) -> None:
        checks = [
            HealthCheck("command_integrity", "command", FAIL, "bad", True),
            HealthCheck("operational_state", "operations", PASS, "ok", True),
            HealthCheck("authority_integrity", "authority", PASS, "ok", True),
            HealthCheck("memory_integrity", "memory", PASS, "ok", True),
            HealthCheck("source_version", "source", PASS, "ok", True),
            HealthCheck("persistence_readiness", "persistence", PASS, "ok"),
        ]
        result = VesselHealth._recovery_readiness(checks)
        self.assertEqual(result.status, FAIL)
        self.assertIn("reconstitution must remain paused", result.detail)

    def test_cli_health_json_does_not_construct_pilot(self) -> None:
        td, root = health_vessel()
        try:
            out = io.StringIO()
            with patch.object(cli, "ROOT", root), patch.object(cli, "pilot", side_effect=AssertionError("health must not construct Pilot")), patch(
                "grox.health.namespace_backend_available", return_value=True
            ), patch("grox.health.docker_backend_available", return_value=False), redirect_stdout(out):
                cli.main(["health", "--json"])
            payload = json.loads(out.getvalue())
            self.assertIn(payload["disposition"], {"HEALTHY", "DEGRADED"})
            self.assertTrue(any(item["check_id"] == "recovery_readiness" for item in payload["checks"]))
            self.assertFalse((root / "configs/state/grox.sqlite3").exists())
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
