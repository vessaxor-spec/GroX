from __future__ import annotations

import unittest
from unittest.mock import patch

from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.pilot import PilotGorXu
from grox.tools.policy import GatewayPolicy
from tests._support import temp_vessel


class PilotToolCapabilityAwarenessTests(unittest.TestCase):
    def test_pilot_reports_fresh_tool_inventory_without_creating_mission_or_widening_authority(self):
        td, root, bootstrap = temp_vessel()
        try:
            bootstrap.store.close()
            policy = GatewayPolicy(
                workspace_enabled=True,
                network_enabled=True,
                browser_enabled=False,
                mcp_enabled=False,
                allowed_origins=frozenset({"https://example.test"}),
                workspace_docker_image="workspace:test",
            )
            pilot = PilotGorXu(root, reasoner=None, gateway_policy=policy)
            try:
                before = pilot.store.recent_missions()
                order = MissionOrder(
                    mission_id="MSN-awareness",
                    order_id="ORD-awareness",
                    commander_intent="Fetch one governed origin",
                    objective="bounded network read",
                    mode=MissionMode.execute,
                    assigned_crew="backend-engineer",
                    allowed_actions=("net_fetch",),
                    scope=(".",),
                    risk_class=RiskClass.medium,
                    parameters={
                        "operation": "http_fetch",
                        "url": "https://example.test/data",
                        "allowed_origins": ["https://example.test"],
                    },
                ).seal()
                with patch("grox.tool_awareness._workspace_readiness", return_value=(True, "namespace")), patch(
                    "grox.tool_awareness._browser_readiness", return_value=(False, None)
                ), patch("grox.tool_awareness._mcp_readiness", return_value=(False, 0)):
                    inventory = pilot.live_tool_capability_inventory(order=order)
                by_id = {item["resource_id"]: item for item in inventory["resources"]}
                self.assertEqual(inventory["schema"], "grox-live-tool-capability-inventory-v1")
                self.assertEqual(inventory["mission_order_id"], "ORD-awareness")
                self.assertTrue(by_id["tool:network"]["authorized"])
                self.assertTrue(by_id["tool:network"]["requested"])
                self.assertFalse(by_id["tool:browser"]["authorized"])
                self.assertFalse(inventory["authority_changed"])
                self.assertFalse(inventory["auto_invocation"])
                self.assertEqual(pilot.store.recent_missions(), before)
            finally:
                pilot.store.close()
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
