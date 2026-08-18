import unittest

from grox.contracts import Evidence, MissionMode, TourResult
from tests._support import temp_vessel


class FailedRollbackExecutor:
    def execute(self, order):
        return TourResult(
            order.order_id,
            order.assigned_crew,
            "exception",
            "Repair verification failed and rollback could not safely reconcile target state",
            [
                Evidence("mutation", {"operation": "write_text", "path": "docs/x.txt"}),
                Evidence("mutation_rollback", {"status": "failed"}),
            ],
            {
                "type": "mutation_state_diverged",
                "irreversible": True,
                "recommendation": "Return to GorXu; do not overwrite divergent state",
            },
        )


class MissionOutcomeFailureTruthfulnessTests(unittest.TestCase):
    def test_failed_repair_with_unresolved_mutation_reports_mutation_present(self):
        td, root, pilot = temp_vessel()
        try:
            pilot.executor = FailedRollbackExecutor()
            result = pilot.command(
                "Repair docs/x.txt",
                mode=MissionMode.repair,
                scope="docs/x.txt",
                parameters={"operation": "write_text", "path": "docs/x.txt", "content": "x"},
            )
            self.assertEqual(result["status"], "exception")
            self.assertEqual(result["mission_status"], "needs_pilot_decision")
            self.assertEqual(result["outcome"]["effect"], "mutation_state_unresolved")
            self.assertEqual(result["outcome"]["objective"], "not_delivered")
            self.assertTrue(result["outcome"]["mutation"])
            self.assertEqual(result["outcome"]["next_authority"], "pilot_recovery")
            self.assertIn("mutation=yes", result["summary"])
            self.assertIn("next_authority=pilot_recovery", result["summary"])
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
