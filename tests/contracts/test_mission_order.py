import unittest

from grox.contracts import MissionMode, MissionOrder, RiskClass


class MissionOrderTest(unittest.TestCase):
    def test_order_serializes_native_values(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.inspect, "systems-architect",
            risk_class=RiskClass.medium,
        )
        data = order.to_dict()
        self.assertEqual(data["mode"], "inspect")
        self.assertEqual(data["risk_class"], "medium")
        self.assertEqual(data["exception_channel"], "GorXu")

    def test_non_repair_order_cannot_carry_filesystem_mutation_grant(self):
        with self.assertRaisesRegex(ValueError, "explicit Repair authority"):
            MissionOrder.new(
                "M", "intent", "obj", MissionMode.execute, "backend-engineer",
                allowed_actions=["fs_read", "fs_write"],
            )

    def test_non_repair_order_cannot_carry_mcp_mutation_grant(self):
        with self.assertRaisesRegex(ValueError, "explicit Repair authority"):
            MissionOrder.new(
                "M", "intent", "obj", MissionMode.execute, "platform-engineer",
                allowed_actions=["mcp_call", "mcp_mutate"],
            )

    def test_explicit_repair_order_may_carry_mutation_grants(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.repair, "backend-engineer",
            allowed_actions=["fs_read", "fs_write"],
        )
        self.assertIn("fs_write", order.allowed_actions)


if __name__ == "__main__":
    unittest.main()
