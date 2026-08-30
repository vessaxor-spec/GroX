from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_readiness import ConfiguredCognitionReadiness
from grox.configured_openai_probe import ConfiguredOpenAIAuthenticatedModelProbe
from grox.contracts import MissionMode, MissionOrder
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}


class ConfiguredCognitionReadinessIntegrationTests(unittest.TestCase):
    def test_authenticated_probe_becomes_fresh_readiness_without_second_runtime_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            gateway = LayoutToolGateway(
                VesselLayout.legacy(Path(tmp)),
                policy=GatewayPolicy(
                    network_enabled=True,
                    allowed_origins=frozenset({ORIGIN}),
                ),
                secret_broker=SecretBroker({ALIAS: "SECRET-SENTINEL"}),
            )
            resource = ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]
            order = MissionOrder.new(
                "MSN-configured-readiness",
                "establish fresh configured cognition visibility",
                "probe exact configured model visibility",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("net_fetch", "secret_use"),
                parameters={
                    "operation": ConfiguredOpenAIAuthenticatedModelProbe.operation,
                    "resource_id": resource["resource_id"],
                    "provider_kind": "openai",
                    "model": MODEL,
                    "endpoint": ENDPOINT,
                    "credential_alias": ALIAS,
                    "allowed_origins": [ORIGIN],
                    "secret_grants": [ALIAS],
                },
            ).seal()
            transport = {
                "schema": "grox-openai-authenticated-model-probe-v1",
                "origin": ORIGIN,
                "status": 200,
                "classification": "authenticated_model_visible",
                "requested_model": MODEL,
                "model_identity": MODEL,
                "metadata_valid": True,
                "credential_alias": ALIAS,
                "credential_accepted_for_model_visibility": True,
                "credential_rejected": False,
                "secret_materialized": True,
                "network_invoked": True,
                "response_body_returned": False,
                "cognition_invoked": False,
                "ready": False,
                "qualified_fit": False,
                "selected": False,
                "authority_changed": False,
            }
            service = ConfiguredOpenAIAuthenticatedModelProbe(
                CONFIG,
                gateway,
                clock=lambda: 500.0,
            )
            with patch.object(gateway, "openai_model_probe", return_value=transport) as probe_mock:
                probe = service.probe(order=order)
                readiness = ConfiguredCognitionReadiness(
                    CONFIG,
                    clock=lambda: 515.0,
                    max_age_seconds=60.0,
                ).evaluate(probe)

            probe_mock.assert_called_once_with(
                order,
                resource_id=resource["resource_id"],
                responses_endpoint=ENDPOINT,
                model=MODEL,
                credential_alias=ALIAS,
            )
            self.assertEqual(probe["observed_monotonic_seconds"], 500.0)
            self.assertEqual(probe["observation_clock"], "process_monotonic")
            self.assertFalse(probe["persistable_readiness_evidence"])
            self.assertTrue(readiness.ready)
            self.assertEqual(readiness.observation_age_seconds, 15.0)
            evidence = readiness.evidence()
            self.assertFalse(evidence["secret_materialized_by_evaluator"])
            self.assertFalse(evidence["network_invoked_by_evaluator"])
            self.assertFalse(evidence["selected"])
            self.assertFalse(evidence["qualified_fit"])
            self.assertFalse(evidence["observed"])
            self.assertFalse(evidence["adaptive_scoring_enabled"])


if __name__ == "__main__":
    unittest.main()
