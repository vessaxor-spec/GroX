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
from grox.selected_configured_cognition import SelectedConfiguredCognition
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
INTENT = "Inspect selected configured cognition safely"
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


class SelectedConfiguredCognitionIntegrationTests(unittest.TestCase):
    @staticmethod
    def _interpretation():
        return MissionInterpretation.from_mapping(
            {
                "commander_intent": INTENT,
                "objective": "Inspect selected configured cognition",
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
                    }
                ],
                "recommended_option": "inspect",
                "confidence": 0.9,
                "proposed_mode": "inspect",
                "proposed_risk": "low",
            },
            expected_intent=INTENT,
        )

    def test_selected_exact_resource_invokes_existing_governed_path_and_records_observation(self):
        with tempfile.TemporaryDirectory() as td:
            broker = SecretBroker({ALIAS: "SECRET-SENTINEL"})
            gateway = LayoutToolGateway(
                VesselLayout.legacy(Path(td)),
                policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
                secret_broker=broker,
            )
            resource = ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]
            order = MissionOrder.new(
                "MSN-selected-configured-cognition-integration",
                INTENT,
                "invoke selected configured cognition",
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
            interpretation = self._interpretation()
            qualification_transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp_qualification",
                "response_model": MODEL,
                "interpretation": interpretation,
                "raw_response_returned": False,
            }
            selected_transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp_selected_execution",
                "response_model": MODEL,
                "interpretation": interpretation,
                "raw_response_returned": False,
            }
            observed = []
            with patch.object(
                gateway,
                "openai_responses_cognition",
                side_effect=[qualification_transport, selected_transport],
            ) as cognition_gateway:
                qualified_result = ConfiguredOpenAICognition(CONFIG, gateway).invoke(
                    order=order,
                    roster=ROSTER,
                )
                fitness = ConfiguredCognitionMissionFitness.evaluate(
                    qualified_result,
                    order=order,
                    roster=ROSTER,
                )
                selector = ConfiguredCognitionSelection(CONFIG)
                selection = selector.select(
                    qualified_result,
                    fitness,
                    order=order,
                    policy=ConfiguredCognitionSelectionPolicy(resource_id=qualified_result.resource_id),
                )
                runner = SelectedConfiguredCognition(
                    CONFIG,
                    gateway,
                    selector,
                    observation_recorder=lambda **kwargs: observed.append(kwargs),
                )
                report = runner.invoke(selection, order=order, roster=ROSTER)

            self.assertEqual(cognition_gateway.call_count, 2)
            self.assertEqual(report.response_id, "resp_selected_execution")
            self.assertEqual(report.response_model, MODEL)
            self.assertEqual(report.interpretation.commander_intent, INTENT)
            evidence = report.evidence()
            self.assertTrue(evidence["selected"])
            self.assertTrue(evidence["observed"])
            self.assertTrue(evidence["cognition_succeeded"])
            self.assertFalse(evidence["authority_changed"])
            self.assertFalse(evidence["fallback_enabled"])
            self.assertFalse(evidence["switching_enabled"])
            self.assertFalse(evidence["adaptive_routing_enabled"])
            self.assertFalse(evidence["raw_response_returned"])
            self.assertEqual(len(observed), 1)
            identity = observed[0]["identity"]
            self.assertEqual(identity["resource_id"], selection.resource_id)
            self.assertEqual(identity["selection_id"], selection.selection_id)
            self.assertEqual(identity["response_id"], "resp_selected_execution")
            self.assertNotIn("credential_alias", identity)
            self.assertNotIn("interpretation", identity)
            self.assertNotIn("raw_response", identity)


if __name__ == "__main__":
    unittest.main()
