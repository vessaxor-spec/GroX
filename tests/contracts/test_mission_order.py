import unittest

from grox.contracts import MissionMode, MissionOrder, RiskClass


class MissionOrderTest(unittest.TestCase):
    def test_order_serializes_native_values(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.inspect, "systems-architect",
            risk_class=RiskClass.medium,
            allowed_actions=["fs_read"],
        )
        data = order.to_dict()
        self.assertEqual(data["mode"], "inspect")
        self.assertEqual(data["risk_class"], "medium")
        self.assertEqual(data["exception_channel"], "GorXu")
        self.assertEqual(data["allowed_actions"], ["fs_read"])

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

    def test_allowed_actions_are_snapshotted_as_immutable_tuple(self):
        actions = ["fs_read"]
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.execute, "backend-engineer",
            allowed_actions=actions,
        )
        actions.append("fs_write")
        self.assertEqual(order.allowed_actions, ("fs_read",))
        self.assertNotIn("fs_write", order.allowed_actions)
        with self.assertRaises(AttributeError):
            order.allowed_actions.append("fs_write")

    def test_allowed_actions_cannot_be_reassigned_after_construction(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.execute, "backend-engineer",
            allowed_actions=["fs_read"],
        )
        with self.assertRaisesRegex(AttributeError, "immutable"):
            order.allowed_actions = ("fs_read", "fs_write")
        self.assertEqual(order.allowed_actions, ("fs_read",))


if __name__ == "__main__":
    unittest.main()
