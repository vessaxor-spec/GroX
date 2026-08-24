from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_connection_awareness import (
    ConfiguredConnectionAuthorizationError,
    ConfiguredConnectionPolicyAwareness,
)
from grox.contracts import MissionMode, MissionOrder
from grox.tools.gateway import ToolGateway
from grox.tools.policy import GatewayPolicy


class ConfiguredConnectionPolicyAwarenessTests(unittest.TestCase):
    def _gateway(self, *, allowed: bool = True) -> ToolGateway:
        root = Path(self.tempdir.name)
        policy = GatewayPolicy(
            network_enabled=True,
            allowed_origins=frozenset({"https://api.openai.com"} if allowed else {"https://example.invalid"}),
        )
        return ToolGateway(root, policy=policy)

    @staticmethod
    def _config() -> dict[str, str]:
        return {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "gpt-test-model",
            "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
        }

    def _resource(self) -> dict:
        inventory = ConfiguredCognitionDiscovery(self._config()).inventory()
        self.assertEqual(inventory["status"], "ok")
        return inventory["resources"][0]

    def _order(self, *, resource_id: str, endpoint: str, seal: bool = True) -> MissionOrder:
        order = MissionOrder.new(
            "MSN-connection-awareness",
            "inspect configured connection policy",
            "inspect configured connection policy",
            MissionMode.inspect,
            "backend-engineer",
            allowed_actions=("net_fetch",),
            parameters={
                "operation": "configured_cognition_connection_authorization",
                "resource_id": resource_id,
                "endpoint": endpoint,
                "allowed_origins": ["https://api.openai.com"],
            },
        )
        return order.seal() if seal else order

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_host_policy_never_implies_mission_authorization(self):
        resource = self._resource()
        awareness = ConfiguredConnectionPolicyAwareness(self._gateway())
        snapshot = awareness.inventory(resource=resource)
        self.assertTrue(snapshot["discovered"])
        self.assertTrue(snapshot["host_policy_permitted"])
        self.assertFalse(snapshot["authorized"])
        self.assertFalse(snapshot["ready"])
        self.assertFalse(snapshot["qualified_fit"])
        self.assertFalse(snapshot["selected"])
        self.assertFalse(snapshot["observed"])
        self.assertFalse(snapshot["network_invoked"])
        self.assertFalse(snapshot["authority_changed"])

    def test_exact_presealed_order_authorizes_connection_without_network_or_readiness(self):
        resource = self._resource()
        gateway = self._gateway()
        awareness = ConfiguredConnectionPolicyAwareness(gateway)
        order = self._order(resource_id=resource["resource_id"], endpoint=resource["endpoint"])
        with patch.object(gateway, "fetch_url", side_effect=AssertionError("awareness must not fetch")):
            snapshot = awareness.inventory(resource=resource, order=order)
        self.assertTrue(snapshot["host_policy_permitted"])
        self.assertTrue(snapshot["authorized"])
        self.assertEqual(snapshot["authorization_status"], "sealed_mission_order_authorized")
        self.assertFalse(snapshot["ready"])
        self.assertFalse(snapshot["network_invoked"])
        self.assertFalse(snapshot["credential_inspected"])
        self.assertFalse(snapshot["provider_constructed"])

    def test_unsealed_order_is_rejected_without_becoming_sealed(self):
        resource = self._resource()
        order = self._order(resource_id=resource["resource_id"], endpoint=resource["endpoint"], seal=False)
        awareness = ConfiguredConnectionPolicyAwareness(self._gateway())
        with self.assertRaises(ConfiguredConnectionAuthorizationError):
            awareness.inventory(resource=resource, order=order)
        self.assertFalse(order.sealed)

    def test_wrong_resource_id_never_authorizes_connection(self):
        resource = self._resource()
        order = self._order(
            resource_id="cognition:configured:openai:wrong",
            endpoint=resource["endpoint"],
        )
        snapshot = ConfiguredConnectionPolicyAwareness(self._gateway()).inventory(
            resource=resource,
            order=order,
        )
        self.assertFalse(snapshot["authorized"])
        self.assertEqual(snapshot["authorization_status"], "resource_mismatch")
        self.assertFalse(snapshot["ready"])

    def test_resource_endpoint_operation_and_origin_binding_fail_closed(self):
        resource = self._resource()
        awareness = ConfiguredConnectionPolicyAwareness(self._gateway())
        cases = [
            {"resource_id": resource["resource_id"], "endpoint": "https://api.openai.com/v1/other", "operation": "configured_cognition_connection_authorization", "origins": ["https://api.openai.com"]},
            {"resource_id": resource["resource_id"], "endpoint": resource["endpoint"], "operation": "other_operation", "origins": ["https://api.openai.com"]},
            {"resource_id": resource["resource_id"], "endpoint": resource["endpoint"], "operation": "configured_cognition_connection_authorization", "origins": ["https://example.invalid"]},
        ]
        for case in cases:
            with self.subTest(case=case):
                order = MissionOrder.new(
                    "MSN-connection-awareness",
                    "inspect configured connection policy",
                    "inspect configured connection policy",
                    MissionMode.inspect,
                    "backend-engineer",
                    allowed_actions=("net_fetch",),
                    parameters={
                        "operation": case["operation"],
                        "resource_id": case["resource_id"],
                        "endpoint": case["endpoint"],
                        "allowed_origins": case["origins"],
                    },
                ).seal()
                snapshot = awareness.inventory(resource=resource, order=order)
                self.assertFalse(snapshot["authorized"])
                self.assertFalse(snapshot["ready"])

    def test_host_policy_denial_and_local_configuration_are_not_promoted(self):
        remote = self._resource()
        denied = ConfiguredConnectionPolicyAwareness(self._gateway(allowed=False)).inventory(resource=remote)
        self.assertFalse(denied["host_policy_permitted"])
        self.assertFalse(denied["authorized"])

        local = ConfiguredCognitionDiscovery(
            {
                "GROX_REASONER_PROVIDER": "local-llama-cpp",
                "GROX_REASONER_MODEL": "qwen-seed",
            }
        ).inventory()["resources"][0]
        not_applicable = ConfiguredConnectionPolicyAwareness(self._gateway()).inventory(resource=local)
        self.assertEqual(not_applicable["status"], "not_applicable")
        self.assertFalse(not_applicable["discovered"])
        self.assertFalse(not_applicable["authorized"])
        self.assertFalse(not_applicable["ready"])


if __name__ == "__main__":
    unittest.main()
