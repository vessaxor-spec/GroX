from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fitness import ConfiguredCognitionMissionFitness
from grox.configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionPolicy,
)
from grox.configured_openai_cognition import ConfiguredOpenAICognition
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
INTENT = "Inspect configured cognition safely"
ROSTER = [
    {"crew_id": "backend-engineer", "title": "Backend Engineer"},
    {"crew_id": "application-security-engineer", "title": "Application Security Engineer"},
]
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}


class ConfiguredCognitionSelectionIntegrationTests(unittest.TestCase):
    def test_qualified_governed_cognition_selects_without_second_provider_or_secret_activity(self):
        with tempfile.TemporaryDirectory() as td:
            broker = SecretBroker({ALIAS: "SECRET-SENTINEL"})
            gateway = LayoutToolGateway(
                VesselLayout.legacy(Path(td)),
                policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
                secret_broker=broker,
            )
            resource = ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]
            order = MissionOrder.new(
                "MSN-configured-cognition-selection-integration",
                INTENT,
                "select configured cognition",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
                parameters={
                    "operation": ConfiguredOpenAICognition.operation,
                    "resource_id": resource["resource_id"],
                    "provider_kind": resource["provider_kind"],
                    "model": resource["model"],
                    "endpoint": resource["endpoint"],
                    "credential_alias": ALIAS,
                    "allowed_origins": [ORIGIN],
                    "secret_grants": [ALIAS],
                },
            ).seal()
            interpretation = MissionInterpretation.from_mapping(
                {
                    "commander_intent": INTENT,
                    "objective": "Inspect configured cognition",
                    "ambiguous": False,
                    "ambiguities": [],
                    "assumptions": [],
                    "information_needs": [],
                    "candidate_crew_ids": ["backend-engineer"],
                    "options": [
                        {
                            "name": "inspect",
                            "rationale": "Use bounded inspection.",
                            "advantages": ["bounded"],
                            "risks": [],
                            "crew_ids": ["backend-engineer"],
                        },
                        {
                            "name": "inspect-with-security",
                            "rationale": "Use bounded inspection with security review.",
                            "advantages": ["bounded", "reviewed"],
                            "risks": [],
                            "crew_ids": ["application-security-engineer"],
                        },
                    ],
                    "recommended_option": "inspect",
                    "confidence": 0.9,
                    "proposed_mode": "inspect",
                    "proposed_risk": "low",
                },
                expected_intent=INTENT,
            )
            transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp_selection_integration",
                "response_model": MODEL,
                "interpretation": interpretation,
                "raw_response_returned": False,
            }
            with patch.object(gateway, "openai_responses_cognition", return_value=transport) as invoke:
                result = ConfiguredOpenAICognition(CONFIG, gateway).invoke(order=order, roster=ROSTER)
                fitness = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
                self.assertEqual(invoke.call_count, 1)
                self.assertTrue(fitness.qualified_fit)

                selector = ConfiguredCognitionSelection(CONFIG)
                with patch.object(
                    broker,
                    "materialize_env",
                    side_effect=AssertionError("selection must not materialize a secret"),
                ) as materialize, patch.object(
                    gateway,
                    "openai_responses_cognition",
                    side_effect=AssertionError("selection must not invoke cognition"),
                ) as second_invoke:
                    selection = selector.select(
                        result,
                        fitness,
                        order=order,
                        policy=ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id),
                    )
                materialize.assert_not_called()
                second_invoke.assert_not_called()

            evidence = selection.evidence()
            self.assertTrue(evidence["selected"])
            self.assertFalse(evidence["observed"])
            self.assertFalse(evidence["network_invoked"])
            self.assertFalse(evidence["secret_materialized"])
            self.assertFalse(evidence["cognition_invoked"])
            self.assertFalse(evidence["fallback_enabled"])
            self.assertFalse(evidence["switching_enabled"])
            self.assertFalse(evidence["adaptive_routing_enabled"])
            self.assertFalse(evidence["authority_changed"])
            selector.validate_active(selection, order=order)


if __name__ == "__main__":
    unittest.main()
