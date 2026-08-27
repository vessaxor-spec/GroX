from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fitness import ConfiguredCognitionMissionFitness
from grox.configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionError,
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


class ConfiguredCognitionSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
            secret_broker=SecretBroker({ALIAS: "SECRET-SENTINEL"}),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource(config=CONFIG):
        return ConfiguredCognitionDiscovery(config).inventory()["resources"][0]

    def _order(self):
        resource = self._resource()
        return MissionOrder.new(
            "MSN-configured-cognition-selection",
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

    @staticmethod
    def _interpretation():
        return MissionInterpretation.from_mapping(
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

    def _qualified(self, order):
        transport = {
            "schema": "grox-openai-responses-cognition-transport-v1",
            "status": 200,
            "response_id": "resp_selection",
            "response_model": MODEL,
            "interpretation": self._interpretation(),
            "raw_response_returned": False,
        }
        with patch.object(self.gateway, "openai_responses_cognition", return_value=transport):
            result = ConfiguredOpenAICognition(CONFIG, self.gateway).invoke(order=order, roster=ROSTER)
        fitness = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        self.assertTrue(fitness.qualified_fit)
        return result, fitness

    def test_exact_qualified_resource_is_selected_without_promoting_later_states(self):
        order = self._order()
        result, fitness = self._qualified(order)
        selector = ConfiguredCognitionSelection(CONFIG)
        policy = ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id)
        selection = selector.select(result, fitness, order=order, policy=policy)
        evidence = selection.evidence()
        self.assertTrue(evidence["discovered"])
        self.assertTrue(evidence["authorized"])
        self.assertTrue(evidence["ready"])
        self.assertTrue(evidence["qualified_fit"])
        self.assertTrue(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["fallback_enabled"])
        self.assertFalse(evidence["switching_enabled"])
        self.assertFalse(evidence["adaptive_routing_enabled"])
        self.assertFalse(evidence["network_invoked"])
        self.assertFalse(evidence["secret_materialized"])
        self.assertFalse(evidence["cognition_invoked"])
        self.assertFalse(evidence["authority_changed"])
        selector.validate_active(selection, order=order)

    def test_failed_fitness_never_selects(self):
        order = self._order()
        result, fitness = self._qualified(order)
        failed = replace(fitness, status="FAIL")
        selector = ConfiguredCognitionSelection(CONFIG)
        policy = ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id)
        with self.assertRaisesRegex(ConfiguredCognitionSelectionError, "not qualified fit"):
            selector.select(result, failed, order=order, policy=policy)

    def test_current_credential_binding_rebind_invalidates_prior_qualification(self):
        order = self._order()
        result, fitness = self._qualified(order)
        rebound = dict(CONFIG)
        rebound["GROX_REASONER_CREDENTIAL_ALIAS"] = "rotated-alias"
        selector = ConfiguredCognitionSelection(rebound)
        policy = ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id)
        with self.assertRaisesRegex(ConfiguredCognitionSelectionError, "binding differs"):
            selector.select(result, fitness, order=order, policy=policy)

    def test_policy_cannot_silently_select_another_resource(self):
        order = self._order()
        result, fitness = self._qualified(order)
        selector = ConfiguredCognitionSelection(CONFIG)
        policy = ConfiguredCognitionSelectionPolicy(resource_id="cognition:configured:openai:other")
        with self.assertRaisesRegex(ConfiguredCognitionSelectionError, "policy does not name"):
            selector.select(result, fitness, order=order, policy=policy)

    def test_different_order_cannot_replay_selection_evidence(self):
        order = self._order()
        result, fitness = self._qualified(order)
        other = self._order()
        self.assertNotEqual(order.order_id, other.order_id)
        selector = ConfiguredCognitionSelection(CONFIG)
        policy = ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id)
        with self.assertRaisesRegex(ConfiguredCognitionSelectionError, "exact source Order"):
            selector.select(result, fitness, order=other, policy=policy)

    def test_reconstitution_invalidates_previously_active_selection(self):
        order = self._order()
        result, fitness = self._qualified(order)
        selector = ConfiguredCognitionSelection(CONFIG)
        selection = selector.select(
            result,
            fitness,
            order=order,
            policy=ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id),
        )
        selector.validate_active(selection, order=order)
        report = selector.reconstitute()
        self.assertEqual(report["cleared_selection_count"], 1)
        self.assertFalse(report["selected"])
        with self.assertRaisesRegex(ConfiguredCognitionSelectionError, "no longer active"):
            selector.validate_active(selection, order=order)


if __name__ == "__main__":
    unittest.main()
