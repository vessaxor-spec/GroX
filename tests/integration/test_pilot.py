import json
import unittest

from tests._support import temp_vessel
from grox.contracts import MissionMode, RiskClass


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

    def test_persistence_survives_reopen(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect vessel", mode=MissionMode.inspect)
            mission_id = result["mission_id"]
            reopened = type(p)(root)
            self.assertIsNotNone(reopened.store.mission(mission_id))
        finally:
            td.cleanup()

    def test_missing_capability_returns_to_pilot(self):
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
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
