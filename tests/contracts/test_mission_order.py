import unittest

from grox.contracts import MissionMode, MissionOrder, RiskClass


class MissionOrderTest(unittest.TestCase):
    def test_order_serializes_native_values(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.inspect, "test-architecture-specialist",
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

    def test_authority_fields_are_snapshotted_and_immutable_after_construction(self):
        required = ["repo_read"]
        forbidden = ["mcp_mutate"]
        scope = ["docs"]
        verification = ["independent"]
        stop = ["scope_change"]
        parameters = {
            "allowed_origins": ["https://example.com"],
            "mcp_grants": {"adapter": ["read"]},
        }
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.repair, "backend-engineer",
            required_capabilities=required,
            allowed_actions=["fs_read", "fs_write"],
            forbidden_actions=forbidden,
            scope=scope,
            verification_requirements=verification,
            stop_conditions=stop,
            parameters=parameters,
        )
        required.append("repo_write")
        forbidden.clear()
        scope[:] = ["."]
        verification.clear()
        stop.clear()
        parameters["allowed_origins"].append("https://evil.example")
        parameters["mcp_grants"]["adapter"].append("mutate")

        self.assertEqual(order.required_capabilities, ("repo_read",))
        self.assertEqual(order.forbidden_actions, ("mcp_mutate",))
        self.assertEqual(order.scope, ("docs",))
        self.assertEqual(order.verification_requirements, ("independent",))
        self.assertEqual(order.stop_conditions, ("scope_change",))
        self.assertEqual(order.parameters["allowed_origins"], ["https://example.com"])
        self.assertEqual(order.parameters["mcp_grants"]["adapter"], ["read"])

        with self.assertRaisesRegex(AttributeError, "immutable"):
            order.scope = (".",)

        order.parameters = {**dict(order.parameters), "_task_class": "general"}
        order.seal()
        self.assertTrue(order.sealed)
        self.assertEqual(order.parameters["allowed_origins"], ("https://example.com",))
        self.assertEqual(order.parameters["mcp_grants"]["adapter"], ("read",))
        with self.assertRaisesRegex(AttributeError, "immutable"):
            order.parameters = {"allowed_origins": ["https://evil.example"]}
        with self.assertRaises(TypeError):
            order.parameters["mcp_grants"]["adapter"] = ("mutate",)

    def test_immutable_order_serializes_native_json_shapes(self):
        order = MissionOrder.new(
            "M", "intent", "obj", MissionMode.execute, "researcher",
            required_capabilities=["repo_read", "net_fetch"],
            allowed_actions=["net_fetch"],
            forbidden_actions=["fs_write"],
            scope=["docs"],
            parameters={"allowed_origins": ["https://example.com"], "nested": {"items": [1, 2]}},
        )
        data = order.to_dict()
        self.assertEqual(data["required_capabilities"], ["repo_read", "net_fetch"])
        self.assertEqual(data["scope"], ["docs"])
        self.assertEqual(data["parameters"]["allowed_origins"], ["https://example.com"])
        self.assertEqual(data["parameters"]["nested"]["items"], [1, 2])
        self.assertEqual(MissionOrder(**{
            **data,
            "mode": MissionMode(data["mode"]),
            "risk_class": RiskClass(data["risk_class"]),
        }).to_dict(), data)


if __name__ == "__main__":
    unittest.main()
