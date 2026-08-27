from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fitness import (
    ConfiguredCognitionFitnessError,
    ConfiguredCognitionMissionFitness,
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


class ConfiguredCognitionMissionFitnessTests(unittest.TestCase):
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
    def _resource():
        return ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]

    def _order(self, *, seal: bool = True):
        resource = self._resource()
        order = MissionOrder.new(
            "MSN-configured-cognition-fitness",
            INTENT,
            "qualify configured cognition fitness",
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
        )
        return order.seal() if seal else order

    @staticmethod
    def _interpretation(*, candidate_ids=None, option_crew_ids=None, option_names=None):
        candidate_ids = ["backend-engineer"] if candidate_ids is None else candidate_ids
        option_crew_ids = ["backend-engineer"] if option_crew_ids is None else option_crew_ids
        option_names = ["inspect", "inspect-with-security"] if option_names is None else option_names
        options = [
            {
                "name": name,
                "rationale": f"Use bounded strategy {index}.",
                "advantages": ["bounded"],
                "risks": [],
                "crew_ids": list(option_crew_ids),
            }
            for index, name in enumerate(option_names)
        ]
        return MissionInterpretation.from_mapping(
            {
                "commander_intent": INTENT,
                "objective": "Inspect configured cognition",
                "ambiguous": False,
                "ambiguities": [],
                "assumptions": [],
                "information_needs": [],
                "candidate_crew_ids": list(candidate_ids),
                "options": options,
                "recommended_option": option_names[0] if option_names else "",
                "confidence": 0.9,
                "proposed_mode": "inspect",
                "proposed_risk": "low",
            },
            expected_intent=INTENT,
        )

    def _result(self, order, *, interpretation=None, response_model=MODEL):
        transport = {
            "schema": "grox-openai-responses-cognition-transport-v1",
            "status": 200,
            "response_id": "resp_fitness",
            "response_model": response_model,
            "interpretation": interpretation or self._interpretation(),
            "raw_response_returned": False,
        }
        with patch.object(self.gateway, "openai_responses_cognition", return_value=transport):
            return ConfiguredOpenAICognition(CONFIG, self.gateway).invoke(order=order, roster=ROSTER)

    def test_successful_exact_result_qualifies_only_mission_interpretation(self):
        order = self._order()
        result = self._result(order)
        report = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        evidence = report.evidence()
        self.assertEqual(report.status, "PASS")
        self.assertTrue(report.qualified_fit)
        self.assertTrue(all(report.checks.values()))
        self.assertEqual(evidence["placement"], "mission_interpretation")
        self.assertEqual(evidence["fitness_scope"], "mission_interpretation_only")
        self.assertEqual(evidence["mission_id"], order.mission_id)
        self.assertEqual(evidence["order_id"], order.order_id)
        self.assertFalse(evidence["general_model_quality_claim"])
        self.assertFalse(evidence["crew_cognition_fit_claim"])
        self.assertFalse(evidence["routing_fit_claim"])
        self.assertFalse(evidence["fallback_fit_claim"])
        self.assertFalse(evidence["cognition_invoked"])
        self.assertFalse(evidence["secret_materialized"])
        self.assertFalse(evidence["network_invoked"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["authority_changed"])

    def test_different_sealed_order_cannot_replay_successful_fitness_evidence(self):
        source_order = self._order()
        result = self._result(source_order)
        other_order = self._order()
        self.assertNotEqual(source_order.order_id, other_order.order_id)
        report = ConfiguredCognitionMissionFitness.evaluate(result, order=other_order, roster=ROSTER)
        self.assertEqual(report.status, "FAIL")
        self.assertFalse(report.checks["exact_order_identity"])
        self.assertFalse(report.qualified_fit)

    def test_out_of_roster_crew_reference_never_qualifies_fit(self):
        order = self._order()
        interpretation = self._interpretation(
            candidate_ids=["backend-engineer", "nonexistent-crew"],
            option_crew_ids=["backend-engineer"],
        )
        result = self._result(order, interpretation=interpretation)
        report = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        self.assertEqual(report.status, "FAIL")
        self.assertFalse(report.checks["crew_references_roster_constrained"])
        self.assertFalse(report.qualified_fit)

    def test_response_model_identity_mismatch_never_qualifies_fit(self):
        order = self._order()
        result = self._result(order, response_model="different-model")
        report = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        self.assertEqual(report.status, "FAIL")
        self.assertFalse(report.checks["response_model_consistent"])
        self.assertFalse(report.qualified_fit)

    def test_duplicate_strategy_names_never_qualify_fit(self):
        order = self._order()
        result = self._result(order, interpretation=self._interpretation(option_names=["same", "same"]))
        report = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        self.assertEqual(report.status, "FAIL")
        self.assertFalse(report.checks["strategy_bounded"])
        self.assertFalse(report.qualified_fit)

    def test_unsealed_source_order_is_rejected_without_sealing_it(self):
        source_order = self._order()
        result = self._result(source_order)
        unsealed = self._order(seal=False)
        with self.assertRaisesRegex(ConfiguredCognitionFitnessError, "already sealed"):
            ConfiguredCognitionMissionFitness.evaluate(result, order=unsealed, roster=ROSTER)
        self.assertFalse(unsealed.sealed)


if __name__ == "__main__":
    unittest.main()
