from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.tool_awareness import ToolCapabilityAuthorizationError, ToolCapabilityAwareness
from grox.tools.gateway import ToolGateway
from grox.tools.mcp import MCPAdapterSpec
from grox.tools.policy import GatewayPolicy


class ToolCapabilityAwarenessTests(unittest.TestCase):
    def _gateway(self, root: Path) -> ToolGateway:
        policy = GatewayPolicy(
            workspace_enabled=True,
            network_enabled=True,
            browser_enabled=True,
            mcp_enabled=True,
            allowed_origins=frozenset({"https://example.test"}),
            workspace_docker_image="workspace:test",
            browser_docker_image="browser:test",
        )
        registry = {
            "reader": MCPAdapterSpec(
                argv=("/bin/echo",),
                allowed_tools=frozenset({"read", "write"}),
                mutating_tools=frozenset({"write"}),
            )
        }
        return ToolGateway(root, policy=policy, mcp_registry=registry)

    @staticmethod
    def _order(*, mode=MissionMode.execute, actions=(), parameters=None) -> MissionOrder:
        return MissionOrder(
            mission_id="MSN-awareness",
            order_id="ORD-awareness",
            commander_intent="Use one governed capability",
            objective="bounded capability check",
            mode=mode,
            assigned_crew="backend-engineer",
            allowed_actions=tuple(actions),
            forbidden_actions=(),
            scope=(".",),
            risk_class=RiskClass.medium,
            parameters=dict(parameters or {}),
        )

    @staticmethod
    def _by_id(inventory: dict) -> dict[str, dict]:
        return {item["resource_id"]: item for item in inventory["resources"]}

    def test_host_ready_never_implies_mission_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            with patch("grox.tool_awareness._workspace_readiness", return_value=(True, "namespace")), patch(
                "grox.tool_awareness._browser_readiness", return_value=(True, "namespace")
            ), patch("grox.tool_awareness._mcp_readiness", return_value=(True, 1)):
                inventory = awareness.inventory()
            resources = self._by_id(inventory)
            self.assertEqual(set(resources), {"tool:workspace", "tool:network", "tool:browser", "tool:mcp"})
            self.assertTrue(all(item["discovered"] for item in resources.values()))
            self.assertTrue(all(item["host_enabled"] for item in resources.values()))
            self.assertTrue(all(item["ready"] for item in resources.values()))
            self.assertTrue(all(item["authorized"] is False for item in resources.values()))
            self.assertTrue(all(item["requested"] is False for item in resources.values()))
            self.assertFalse(inventory["authority_changed"])
            self.assertFalse(inventory["auto_invocation"])

    def test_unsealed_order_is_rejected_without_being_sealed(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            order = self._order(actions=("workspace_exec",), parameters={"operation": "workspace_shell"})
            self.assertFalse(order.sealed)
            with self.assertRaisesRegex(ToolCapabilityAuthorizationError, "already sealed"):
                awareness.inventory(order=order)
            self.assertFalse(order.sealed)

    def test_exact_sealed_network_grant_authorizes_only_requested_capability(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            order = self._order(
                actions=("net_fetch",),
                parameters={
                    "operation": "http_fetch",
                    "url": "https://example.test/data",
                    "allowed_origins": ["https://example.test"],
                },
            ).seal()
            with patch("grox.tool_awareness._workspace_readiness", return_value=(True, "namespace")), patch(
                "grox.tool_awareness._browser_readiness", return_value=(True, "namespace")
            ), patch("grox.tool_awareness._mcp_readiness", return_value=(True, 1)):
                resources = self._by_id(awareness.inventory(order=order))
            self.assertTrue(resources["tool:network"]["requested"])
            self.assertTrue(resources["tool:network"]["authorized"])
            for resource_id in ("tool:workspace", "tool:browser", "tool:mcp"):
                self.assertFalse(resources[resource_id]["requested"])
                self.assertFalse(resources[resource_id]["authorized"])

    def test_browser_requires_both_browser_and_network_grants_and_allowed_origin(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            missing_network = self._order(
                actions=("browser_capture",),
                parameters={
                    "operation": "browser_capture",
                    "url": "https://example.test/page",
                    "allowed_origins": ["https://example.test"],
                },
            ).seal()
            denied_origin = self._order(
                actions=("browser_capture", "net_fetch"),
                parameters={
                    "operation": "browser_capture",
                    "url": "https://denied.test/page",
                    "allowed_origins": ["https://denied.test"],
                },
            ).seal()
            allowed = self._order(
                actions=("browser_capture", "net_fetch"),
                parameters={
                    "operation": "browser_capture",
                    "url": "https://example.test/page",
                    "allowed_origins": ["https://example.test"],
                },
            ).seal()
            with patch("grox.tool_awareness._workspace_readiness", return_value=(True, "namespace")), patch(
                "grox.tool_awareness._browser_readiness", return_value=(True, "namespace")
            ), patch("grox.tool_awareness._mcp_readiness", return_value=(True, 1)):
                self.assertFalse(self._by_id(awareness.inventory(order=missing_network))["tool:browser"]["authorized"])
                self.assertFalse(self._by_id(awareness.inventory(order=denied_origin))["tool:browser"]["authorized"])
                self.assertTrue(self._by_id(awareness.inventory(order=allowed))["tool:browser"]["authorized"])

    def test_mcp_mutation_requires_repair_and_explicit_mutation_grant(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            denied = self._order(
                actions=("mcp_call",),
                parameters={
                    "operation": "mcp_call",
                    "adapter": "reader",
                    "tool": "write",
                    "mcp_grants": {"reader": ["write"]},
                },
            ).seal()
            allowed = self._order(
                mode=MissionMode.repair,
                actions=("mcp_call", "mcp_mutate"),
                parameters={
                    "operation": "mcp_call",
                    "adapter": "reader",
                    "tool": "write",
                    "mcp_grants": {"reader": ["write"]},
                },
            ).seal()
            with patch("grox.tool_awareness._workspace_readiness", return_value=(True, "namespace")), patch(
                "grox.tool_awareness._browser_readiness", return_value=(True, "namespace")
            ), patch("grox.tool_awareness._mcp_readiness", return_value=(True, 1)):
                self.assertFalse(self._by_id(awareness.inventory(order=denied))["tool:mcp"]["authorized"])
                self.assertTrue(self._by_id(awareness.inventory(order=allowed))["tool:mcp"]["authorized"])

    def test_inventory_never_invokes_governed_capabilities_and_readiness_is_fresh(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = self._gateway(Path(td))
            awareness = ToolCapabilityAwareness(gateway)
            with patch.object(gateway, "workspace_shell") as workspace, patch.object(
                gateway, "fetch_url"
            ) as network, patch.object(gateway, "browser_capture") as browser, patch.object(
                gateway, "mcp_call"
            ) as mcp, patch(
                "grox.tool_awareness._workspace_readiness", side_effect=[(False, None), (True, "namespace")]
            ), patch("grox.tool_awareness._browser_readiness", return_value=(False, None)), patch(
                "grox.tool_awareness._mcp_readiness", return_value=(False, 0)
            ):
                first = self._by_id(awareness.inventory())
                second = self._by_id(awareness.inventory())
            self.assertFalse(first["tool:workspace"]["ready"])
            self.assertTrue(second["tool:workspace"]["ready"])
            workspace.assert_not_called()
            network.assert_not_called()
            browser.assert_not_called()
            mcp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
