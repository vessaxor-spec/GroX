from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_credential_use_authorization import ConfiguredCredentialUseAuthorization
from grox.configured_remote_reasoner import ConfiguredRemoteReasonerActivation
from grox.contracts import MissionMode, MissionOrder
from grox.tools.gateway import ToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


OPENAI_CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": "remote-model-sentinel",
    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
    "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
}


class ConfiguredRemoteReasonerIntegrationTests(unittest.TestCase):
    def test_exact_configured_alias_moves_from_non_materializing_awareness_to_bounded_provider_construction(self):
        secret = "INTEGRATION-CREDENTIAL-SENTINEL"
        with tempfile.TemporaryDirectory() as tempdir:
            gateway = ToolGateway(
                Path(tempdir),
                policy=GatewayPolicy(),
                secret_broker=SecretBroker({"openai-primary": secret}),
            )
            resource = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]

            awareness_order = MissionOrder.new(
                "MSN-awareness",
                "inspect credential use",
                "inspect credential use",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("secret_use",),
                parameters={
                    "operation": "configured_cognition_credential_use_authorization",
                    "resource_id": resource["resource_id"],
                    "provider_kind": "openai",
                    "model": "remote-model-sentinel",
                    "endpoint": "https://api.openai.com/v1/responses",
                    "credential_alias": "openai-primary",
                    "secret_grants": ["openai-primary"],
                },
            ).seal()
            awareness = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
                order=awareness_order
            )
            self.assertTrue(awareness["resources"][0]["credential_use_authorized"])
            self.assertFalse(awareness["secret_materialized"])
            self.assertFalse(awareness["provider_constructed"])

            activation_order = MissionOrder.new(
                "MSN-activation",
                "activate configured remote reasoner",
                "activate configured remote reasoner",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("secret_use",),
                parameters={
                    "operation": "configured_cognition_remote_reasoner_activation",
                    "resource_id": resource["resource_id"],
                    "provider_kind": "openai",
                    "model": "remote-model-sentinel",
                    "endpoint": "https://api.openai.com/v1/responses",
                    "credential_alias": "openai-primary",
                    "secret_grants": ["openai-primary"],
                },
            ).seal()
            handle = ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(
                order=activation_order
            )
            evidence = handle.evidence()

            self.assertEqual(handle.resource_id, resource["resource_id"])
            self.assertEqual(handle.provider_kind, "openai")
            self.assertEqual(handle.model, "remote-model-sentinel")
            self.assertEqual(handle.endpoint, "https://api.openai.com/v1/responses")
            self.assertFalse(hasattr(handle, "provider"))
            self.assertTrue(evidence["secret_materialized"])
            self.assertTrue(evidence["provider_constructed"])
            self.assertFalse(evidence["credential_validated"])
            self.assertFalse(evidence["network_invoked"])
            self.assertFalse(evidence["cognition_invoked"])
            self.assertFalse(evidence["ready"])
            self.assertNotIn(secret, repr(handle))
            self.assertNotIn(secret, repr(evidence))


if __name__ == "__main__":
    unittest.main()
