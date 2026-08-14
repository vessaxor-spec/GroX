import json
import unittest

from tests._support import temp_vessel
from grox.contracts import MissionMode, RiskClass


class BrokenExecutor:
    def execute(self, order):
        raise RuntimeError("programming defect sentinel")


class PilotTest(unittest.TestCase):
    def test_inspection_routes_and_completes(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect architecture and report", mode=MissionMode.inspect)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["crew"], "systems-architect")
        finally:
            td.cleanup()

    def test_repair_is_verified_by_different_crew(self):
        td, root, p = temp_vessel()
        try:
            result = p.repair_write("docs/x.txt", "hello")
            self.assertEqual(result["status"], "completed")
            self.assertTrue(result["verification"]["ok"])
            self.assertNotEqual(result["crew"], result["verification"]["verifier"])
            self.assertEqual((root / "docs/x.txt").read_text(), "hello")
        finally:
            td.cleanup()

    def test_repair_keywords_without_explicit_mode_cannot_mutate(self):
        td, root, p = temp_vessel()
        try:
            target = root / "docs/implicit.txt"
            result = p.command(
                "Fix and write this change",
                parameters={"operation": "write_text", "path": "docs/implicit.txt", "content": "unsafe"},
                scope="docs/implicit.txt",
            )
            self.assertEqual(result["mode"], "execute")
            self.assertFalse(target.exists())
            mission = p.store.mission(result["mission_id"])
            payload = json.loads(mission["orders"][0]["payload"])
            self.assertNotIn("fs_write", payload["allowed_actions"])
        finally:
            td.cleanup()

    def test_unexpected_executor_defect_is_distinct_and_evidenced(self):
        td, root, p = temp_vessel()
        try:
            p.executor = BrokenExecutor()
            result = p.command("Inspect architecture", mode=MissionMode.inspect)
            self.assertEqual(result["status"], "unexpected_defect")
            self.assertEqual(result["exception"]["type"], "unexpected_defect")
            self.assertEqual(result["exception"]["exception_type"], "RuntimeError")
            self.assertIn("Traceback", result["exception"]["traceback"])
            self.assertEqual(result["exception"]["context"]["operation"], "command")
            mission = p.store.mission(result["mission_id"])
            defect_evidence = [e for e in mission["evidence"] if e["kind"] == "unexpected_defect"]
            self.assertEqual(len(defect_evidence), 1)
            content = json.loads(defect_evidence[0]["content"])
            self.assertEqual(content["exception_type"], "RuntimeError")
            self.assertIn("programming defect sentinel", content["traceback"])
        finally:
            td.cleanup()

    def test_persistence_survives_reopen(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect vessel", mode=MissionMode.inspect)
            mission_id = result["mission_id"]
            reopened = type(p)(root)
            self.assertIsNotNone(reopened.store.mission(mission_id))
        finally:
            td.cleanup()

    def test_missing_capability_returns_to_pilot_as_bounded_routing_exception(self):
        td, root, p = temp_vessel()
        try:
            result = p.command(
                "Repair file",
                mode=MissionMode.repair,
                crew_id="systems-architect",
                parameters={"operation": "write_text", "path": "x", "content": "x"},
                scope="x",
            )
            self.assertEqual(result["status"], "needs_pilot_decision")
            self.assertEqual(result["exception"]["type"], "routing_exception")
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
