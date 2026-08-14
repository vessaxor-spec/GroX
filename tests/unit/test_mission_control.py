import unittest

from grox.contracts import MissionMode, RiskClass
from grox.mission_control.core import MissionControl


class MCTest(unittest.TestCase):
    def setUp(self):
        self.mc = MissionControl()

    def test_inspect_mode(self):
        self.assertEqual(self.mc.infer_mode("Inspect the vessel"), MissionMode.inspect)

    def test_repair_requires_verification(self):
        self.assertTrue(self.mc.verification_required(MissionMode.repair, RiskClass.low))

    def test_critical_sensitive_mutation(self):
        self.assertEqual(self.mc.assess_risk("rotate credentials"), RiskClass.critical)

    def test_review_repair_plan_is_inspect_not_repair(self):
        mode = self.mc.infer_mode("Review the repair plan")
        self.assertEqual(mode, MissionMode.inspect)
        self.assertNotIn("fs_write", self.mc.default_actions(mode))
        self.assertTrue(self.mc.suggests_repair("Review the repair plan"))

    def test_repair_keywords_are_advisory_only_without_explicit_authority(self):
        for directive in (
            "Fix the serializer",
            "Write the updated configuration",
            "Change the deployment record",
            "Modify the source file",
            "Repair the broken document",
        ):
            with self.subTest(directive=directive):
                mode = self.mc.infer_mode(directive)
                self.assertEqual(mode, MissionMode.execute)
                self.assertNotIn("fs_write", self.mc.default_actions(mode))
                self.assertTrue(self.mc.suggests_repair(directive))

    def test_explicit_repair_is_the_write_authority_path(self):
        mode = self.mc.infer_mode("Review the repair plan", explicit=MissionMode.repair)
        self.assertEqual(mode, MissionMode.repair)
        self.assertIn("fs_write", self.mc.default_actions(mode))

    def test_explicit_low_cannot_lower_deterministic_risk_floor(self):
        self.assertEqual(
            self.mc.assess_risk("delete production credentials", explicit=RiskClass.low),
            RiskClass.critical,
        )
        self.assertEqual(
            self.mc.assess_risk("Deploy the service", explicit=RiskClass.low),
            RiskClass.high,
        )

    def test_explicit_risk_may_raise_the_floor(self):
        self.assertEqual(
            self.mc.assess_risk("Inspect harmless metadata", explicit=RiskClass.high),
            RiskClass.high,
        )

    def test_negated_destructive_action_does_not_become_critical(self):
        self.assertEqual(
            self.mc.assess_risk("Do not delete production credentials"),
            RiskClass.high,
        )
        mode = self.mc.infer_mode("Do not delete production credentials")
        self.assertNotEqual(mode, MissionMode.repair)
        self.assertNotIn("fs_write", self.mc.default_actions(mode))


if __name__ == "__main__":
    unittest.main()
