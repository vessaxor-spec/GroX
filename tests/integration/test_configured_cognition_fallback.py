from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fallback import (
    ConfiguredCognitionFallback,
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
)
from grox.configured_cognition_fitness import ConfiguredCognitionMissionFitness
from grox.configured_openai_cognition import ConfiguredOpenAICognition
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Inspect configured cognition with explicit timeout fallback"
MISSION_ID = "MSN-configured-cognition-fallback-integration"
MODEL_A = "remote-model-primary"
MODEL_B = "remote-model-fallback"
ALIAS_A = "openai-primary"
ALIAS_B = "openai-fallback"
ROSTER = [
    {"crew_id": "backend-engineer", "title": "Backend Engineer"},
    {"crew_id": "application-security-engineer", "title": "Application Security Engineer"},
]


def config(model: str, alias: str) -> dict[str, str]:
    return {
        "GROX_REASONER_PROVIDER": "openai",
        "GROX_REASONER_MODEL": model,
        "GROX_REASONER_ENDPOINT": ENDPOINT,
        "GROX_REASONER_CREDENTIAL_ALIAS": alias,
    }


def interpretation() -> MissionInterpretation:
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
                }
            ],
            "recommended_option": "inspect",
            "confidence": 0.9,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        },
        expected_intent=INTENT,
    )


class ConfiguredCognitionFallbackIntegrationTests(unittest.TestCase):
    @staticmethod
    def _order(cfg: dict[str, str], *, alias: str, crew_id: str) -> MissionOrder:
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        return MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"fallback candidate {resource['model']}",
            MissionMode.inspect,
            crew_id,
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": ConfiguredOpenAICognition.operation,
                "resource_id": resource["resource_id"],
                "provider_kind": resource["provider_kind"],
                "model": resource["model"],
                "endpoint": resource["endpoint"],
                "credential_alias": alias,
                "allowed_origins": [ORIGIN],
                "secret_grants": [alias],
            },
        ).seal()

    def test_timeout_switches_only_to_explicit_independently_gated_fallback_and_observes_actual_execution(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_a = config(MODEL_A, ALIAS_A)
            cfg_b = config(MODEL_B, ALIAS_B)
            order_a = self._order(cfg_a, alias=ALIAS_A, crew_id="backend-engineer")
            order_b = self._order(cfg_b, alias=ALIAS_B, crew_id="application-security-engineer")
            self.assertNotEqual(order_a.order_id, order_b.order_id)

            gateway = LayoutToolGateway(
                VesselLayout.legacy(Path(td)),
                policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
                secret_broker=SecretBroker({ALIAS_A: "SECRET-A", ALIAS_B: "SECRET-B"}),
            )
            parsed = interpretation()
            qualification_a_transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp-primary-qualification",
                "response_model": MODEL_A,
                "interpretation": parsed,
                "raw_response_returned": False,
            }
            qualification_b_transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp-fallback-qualification",
                "response_model": MODEL_B,
                "interpretation": parsed,
                "raw_response_returned": False,
            }
            fallback_success_transport = {
                "schema": "grox-openai-responses-cognition-transport-v1",
                "status": 200,
                "response_id": "resp-fallback-execution",
                "response_model": MODEL_B,
                "interpretation": parsed,
                "raw_response_returned": False,
            }
            observed = []
            with patch.object(
                gateway,
                "openai_responses_cognition",
                side_effect=[
                    qualification_a_transport,
                    qualification_b_transport,
                    TimeoutError("primary provider timeout"),
                    fallback_success_transport,
                ],
            ) as cognition_gateway:
                qualified_a = ConfiguredOpenAICognition(cfg_a, gateway).invoke(
                    order=order_a,
                    roster=ROSTER,
                )
                qualified_b = ConfiguredOpenAICognition(cfg_b, gateway).invoke(
                    order=order_b,
                    roster=ROSTER,
                )
                fitness_a = ConfiguredCognitionMissionFitness.evaluate(
                    qualified_a,
                    order=order_a,
                    roster=ROSTER,
                )
                fitness_b = ConfiguredCognitionMissionFitness.evaluate(
                    qualified_b,
                    order=order_b,
                    roster=ROSTER,
                )
                self.assertTrue(fitness_a.qualified_fit)
                self.assertTrue(fitness_b.qualified_fit)

                candidate_a = ConfiguredCognitionFallbackCandidate(
                    config=cfg_a,
                    gateway=gateway,
                    qualification=qualified_a,
                    fitness=fitness_a,
                    order=order_a,
                )
                candidate_b = ConfiguredCognitionFallbackCandidate(
                    config=cfg_b,
                    gateway=gateway,
                    qualification=qualified_b,
                    fitness=fitness_b,
                    order=order_b,
                )
                fallback = ConfiguredCognitionFallback(
                    [candidate_a, candidate_b],
                    ConfiguredCognitionFallbackPolicy(
                        (candidate_a.resource_id, candidate_b.resource_id)
                    ),
                    observation_recorder=lambda **kwargs: observed.append(kwargs),
                )
                report = fallback.invoke(roster=ROSTER)

            self.assertEqual(cognition_gateway.call_count, 4)
            self.assertTrue(report.switched)
            self.assertEqual(
                report.attempted_resource_ids,
                (candidate_a.resource_id, candidate_b.resource_id),
            )
            self.assertEqual(report.timed_out_resource_ids, (candidate_a.resource_id,))
            self.assertEqual(report.executed.resource_id, candidate_b.resource_id)
            self.assertEqual(report.executed.model, MODEL_B)
            self.assertEqual(report.executed.order_id, order_b.order_id)
            self.assertEqual(report.executed.response_id, "resp-fallback-execution")
            self.assertEqual(report.interpretation.commander_intent, INTENT)
            self.assertEqual([item.outcome for item in report.attempt_performance], ["provider_timeout", "success"])
            self.assertEqual(report.attempt_performance[0].resource_id, candidate_a.resource_id)
            self.assertEqual(report.attempt_performance[0].model, MODEL_A)
            self.assertEqual(report.attempt_performance[0].credential_alias, ALIAS_A)
            self.assertEqual(report.attempt_performance[0].order_id, order_a.order_id)
            self.assertIsNone(report.attempt_performance[0].observation_id)
            self.assertEqual(report.attempt_performance[1].resource_id, candidate_b.resource_id)
            self.assertEqual(report.attempt_performance[1].model, MODEL_B)
            self.assertEqual(report.attempt_performance[1].credential_alias, ALIAS_B)
            self.assertEqual(report.attempt_performance[1].order_id, order_b.order_id)
            self.assertEqual(report.attempt_performance[1].observation_id, report.executed.observation_id)
            self.assertEqual(len(observed), 1)
            observed_identity = observed[0]["identity"]
            self.assertEqual(observed_identity["resource_id"], candidate_b.resource_id)
            self.assertEqual(observed_identity["order_id"], order_b.order_id)
            self.assertNotIn("credential_alias", observed_identity)
            self.assertNotIn("interpretation", observed_identity)
            self.assertNotIn("raw_response", observed_identity)

            evidence = report.evidence()
            self.assertTrue(evidence["fallback_enabled"])
            self.assertTrue(evidence["switching_occurred"])
            self.assertEqual(evidence["fallback_reason"], "provider_timeout")
            self.assertTrue(evidence["timeout_only_fallback"])
            self.assertFalse(evidence["candidate_expansion"])
            self.assertFalse(evidence["adaptive_routing_enabled"])
            self.assertFalse(evidence["ranking_enabled"])
            self.assertFalse(evidence["learning_enabled"])
            self.assertFalse(evidence["credential_material_returned"])
            self.assertFalse(evidence["raw_response_returned"])
            self.assertFalse(evidence["mission_created"])
            self.assertFalse(evidence["authority_changed"])
            self.assertEqual(
                [item["outcome"] for item in evidence["attempt_performance"]],
                ["provider_timeout", "success"],
            )
            self.assertNotIn("SECRET-A", repr(evidence))
            self.assertNotIn("SECRET-B", repr(evidence))
            self.assertFalse(any(item["ranking_applied"] for item in evidence["attempt_performance"]))
            self.assertFalse(any(item["learning_applied"] for item in evidence["attempt_performance"]))


if __name__ == "__main__":
    unittest.main()
