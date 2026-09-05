from __future__ import annotations

from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_attempt import ConfiguredCognitionAttempt
from grox.configured_cognition_attempt_performance import ConfiguredCognitionAttemptPerformance
from grox.configured_cognition_fallback import (
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
)
from grox.configured_cognition_fitness import ConfiguredCognitionFitnessResult
from grox.configured_cognition_route_admission import ConfiguredCognitionRouteAdmission
from grox.configured_cognition_route_execution import (
    ConfiguredCognitionRouteExecution,
    ConfiguredCognitionRouteExecutionError,
)
from grox.configured_cognition_route_plan import ConfiguredCognitionRoutePlan
from grox.configured_cognition_route_ranking import ConfiguredCognitionRouteRanker
from grox.configured_openai_cognition import ConfiguredOpenAICognition, ConfiguredOpenAICognitionResult
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.selected_configured_cognition import SelectedConfiguredCognitionResult
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Use exact history only inside current configured cognition gates"
MISSION_ID = "MSN-configured-cognition-route-ranking-integration"
ROSTER = [{"crew_id": "backend-engineer", "title": "Backend Engineer"}]


def interpretation() -> MissionInterpretation:
    return MissionInterpretation.from_mapping(
        {
            "commander_intent": INTENT,
            "objective": "Execute a bounded evidence-ranked configured cognition route",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": [],
            "candidate_crew_ids": ["backend-engineer"],
            "options": [{
                "name": "inspect",
                "rationale": "bounded",
                "advantages": ["bounded"],
                "risks": [],
                "crew_ids": ["backend-engineer"],
            }],
            "recommended_option": "inspect",
            "confidence": 0.9,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        },
        expected_intent=INTENT,
    )


class ConfiguredCognitionRouteRankingIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(self, model: str, alias: str) -> ConfiguredCognitionFallbackCandidate:
        cfg = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": model,
            "GROX_REASONER_ENDPOINT": ENDPOINT,
            "GROX_REASONER_CREDENTIAL_ALIAS": alias,
        }
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        order = MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"candidate {model}",
            MissionMode.inspect,
            "backend-engineer",
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": ConfiguredOpenAICognition.operation,
                "resource_id": resource["resource_id"],
                "provider_kind": "openai",
                "model": model,
                "endpoint": ENDPOINT,
                "credential_alias": alias,
                "allowed_origins": [ORIGIN],
                "secret_grants": [alias],
            },
        ).seal()
        qualification = ConfiguredOpenAICognitionResult(
            resource_id=resource["resource_id"],
            provider_kind="openai",
            model=model,
            endpoint=ENDPOINT,
            credential_alias=alias,
            mission_id=order.mission_id,
            order_id=order.order_id,
            response_id=f"resp-{model}",
            response_model=model,
            _interpretation=interpretation(),
        )
        fitness = ConfiguredCognitionFitnessResult(
            status="PASS",
            resource_id=qualification.resource_id,
            provider_kind="openai",
            model=model,
            endpoint=ENDPOINT,
            credential_alias=alias,
            mission_id=order.mission_id,
            order_id=order.order_id,
            placement="mission_interpretation",
            checks=MappingProxyType({"qualified": True}),
        )
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
            secret_broker=SecretBroker({alias: f"SECRET-{alias}"}),
        )
        return ConfiguredCognitionFallbackCandidate(
            config=cfg,
            gateway=gateway,
            qualification=qualification,
            fitness=fitness,
            order=order,
        )

    @staticmethod
    def _probe(candidate: ConfiguredCognitionFallbackCandidate, observed: float) -> dict[str, object]:
        q = candidate.qualification
        return {
            "schema": "grox-openai-authenticated-model-probe-v1",
            "origin": ORIGIN,
            "status": 200,
            "classification": "authenticated_model_visible",
            "requested_model": q.model,
            "model_identity": q.model,
            "metadata_valid": True,
            "credential_alias": q.credential_alias,
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
            "resource_id": q.resource_id,
            "provider_kind": "openai",
            "endpoint": ENDPOINT,
            "credential_use_authorized": True,
            "observed_monotonic_seconds": observed,
            "observation_clock": "process_monotonic",
            "persistable_readiness_evidence": False,
            "mission_created": False,
            "observed": False,
            "auto_selection": False,
        }

    @staticmethod
    def _performance(candidate, number: int, outcome: str) -> ConfiguredCognitionAttemptPerformance:
        return ConfiguredCognitionAttemptPerformance(
            resource_id=candidate.resource_id,
            provider_kind=candidate.qualification.provider_kind,
            model=candidate.qualification.model,
            endpoint=candidate.qualification.endpoint,
            credential_alias=candidate.qualification.credential_alias,
            mission_id=f"MSN-prior-{candidate.qualification.model}-{number}",
            order_id=f"ORD-prior-{candidate.qualification.model}-{number}",
            selection_id=f"SEL-prior-{candidate.qualification.model}-{number}",
            placement=candidate.fitness.placement,
            outcome=outcome,
            observation_id=(
                f"OBS-prior-{candidate.qualification.model}-{number}"
                if outcome == "success"
                else None
            ),
        )

    @staticmethod
    def _success(candidate) -> SelectedConfiguredCognitionResult:
        return SelectedConfiguredCognitionResult(
            observation_id=f"OBS-live-{candidate.qualification.model}",
            selection_id=f"SEL-live-{candidate.qualification.model}",
            resource_id=candidate.resource_id,
            provider_kind=candidate.qualification.provider_kind,
            model=candidate.qualification.model,
            endpoint=candidate.qualification.endpoint,
            mission_id=candidate.order.mission_id,
            order_id=candidate.order.order_id,
            placement=candidate.fitness.placement,
            response_id=f"resp-live-{candidate.qualification.model}",
            response_model=candidate.qualification.model,
            _interpretation=interpretation(),
        )

    def _planned_and_ranked(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        candidates = (first, second)
        admission = ConfiguredCognitionRouteAdmission(
            candidates,
            ConfiguredCognitionFallbackPolicy(tuple(candidate.resource_id for candidate in candidates)),
        ).plan()
        probes = {
            first.resource_id: self._probe(first, 150.0),
            second.resource_id: self._probe(second, 100.0),
        }
        route = ConfiguredCognitionRoutePlan(
            admission,
            probes,
            clock=lambda: 155.0,
            max_age_seconds=60.0,
        ).plan()
        history = [
            self._performance(first, 1, "provider_timeout"),
            self._performance(first, 2, "provider_timeout"),
            self._performance(second, 1, "success"),
            self._performance(second, 2, "success"),
        ]
        ranked = ConfiguredCognitionRouteRanker(route, history).rank()
        return first, second, probes, ranked

    def test_ranked_ready_order_executes_through_existing_attempt_seam(self):
        first, second, probes, ranked = self._planned_and_ranked()
        calls: list[str] = []

        def invoke_selected(attempt, selection, *, roster):
            calls.append(attempt.resource_id)
            return self._success(second)

        with patch.object(ConfiguredCognitionAttempt, "invoke_selected", new=invoke_selected):
            result = ConfiguredCognitionRouteExecution(
                ranked,
                probes,
                clock=lambda: 159.0,
                max_age_seconds=60.0,
            ).invoke(roster=ROSTER)

        self.assertEqual(ranked.baseline_ready_resource_ids, (first.resource_id, second.resource_id))
        self.assertEqual(ranked.ready_resource_ids, (second.resource_id, first.resource_id))
        self.assertEqual(calls, [second.resource_id])
        self.assertEqual(result.executed.resource_id, second.resource_id)
        self.assertTrue(result.ranking_evaluated)
        self.assertTrue(result.ranking_applied)
        self.assertEqual(
            result.baseline_ready_resource_ids,
            (first.resource_id, second.resource_id),
        )
        evidence = result.evidence()
        self.assertTrue(evidence["ranking_enabled"])
        self.assertTrue(evidence["ranking_applied"])
        self.assertTrue(evidence["adaptive_routing_enabled"])
        self.assertFalse(evidence["learning_enabled"])
        self.assertFalse(evidence["candidate_expansion"])
        self.assertFalse(evidence["authority_changed"])

    def test_ranked_primary_expiry_still_hard_stops_before_selection(self):
        first, second, probes, ranked = self._planned_and_ranked()
        self.assertEqual(ranked.primary_resource_id, second.resource_id)

        with patch.object(
            ConfiguredCognitionAttempt,
            "select",
            side_effect=AssertionError("stale ranked primary must fail before selection"),
        ):
            with self.assertRaises(ConfiguredCognitionRouteExecutionError) as caught:
                ConfiguredCognitionRouteExecution(
                    ranked,
                    probes,
                    clock=lambda: 161.0,
                    max_age_seconds=60.0,
                ).invoke(roster=ROSTER)

        self.assertEqual(caught.exception.resource_id, second.resource_id)
        self.assertEqual(caught.exception.reason, "stale_authenticated_model_visibility")
        self.assertEqual(caught.exception.observation_age_seconds, 61.0)
        self.assertEqual(ranked.fallback_resource_ids, (first.resource_id,))


if __name__ == "__main__":
    unittest.main()
