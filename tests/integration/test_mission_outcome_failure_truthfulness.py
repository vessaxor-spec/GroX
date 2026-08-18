import unittest

from grox.contracts import Evidence, MissionMode, TourResult
from tests._support import temp_vessel


class MutationExceptionExecutor:
    def __init__(self, rollback_status):
        self.rollback_status = rollback_status

    def execute(self, order):
        return TourResult(
            order.order_id,
            order.assigned_crew,
            "exception",
            "Repair verification failed after mutation",
            [
                Evidence("mutation", {"operation": "write_text", "path": "docs/x.txt"}),
                Evidence("mutation_rollback", {"status": self.rollback_status}),
            ],
            {
                "type": "mutation_state_diverged" if self.rollback_status == "failed" else "post_repair_test_failure",
                "irreversible": self.rollback_status == "failed",
                "recommendation": "Return to GorXu",
            },
        )


class MissionOutcomeFailureTruthfulnessTests(unittest.TestCase):
    def test_failed_repair_with_unresolved_mutation_reports_mutation_present(self):
        td, root, pilot = temp_vessel()
        try:
            pilot.executor = MutationExceptionExecutor("failed")
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

    def test_failed_repair_with_completed_rollback_reports_no_remaining_mutation(self):
        td, root, pilot = temp_vessel()
        try:
            pilot.executor = MutationExceptionExecutor("rolled_back")
            result = pilot.command(
                "Repair docs/x.txt",
                mode=MissionMode.repair,
                scope="docs/x.txt",
                parameters={"operation": "write_text", "path": "docs/x.txt", "content": "x"},
            )
            self.assertEqual(result["status"], "exception")
            self.assertEqual(result["outcome"]["effect"], "mutation_rolled_back")
            self.assertFalse(result["outcome"]["mutation"])
            self.assertIsNone(result["outcome"]["next_authority"])
            self.assertIn("mutation=no", result["summary"])
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
