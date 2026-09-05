from __future__ import annotations

from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_attempt_performance import ConfiguredCognitionAttemptPerformance
from grox.configured_cognition_fallback import ConfiguredCognitionFallbackCandidate
from grox.configured_cognition_fitness import ConfiguredCognitionFitnessResult
from grox.configured_cognition_route_plan import ConfiguredCognitionRoutePlanResult
from grox.configured_cognition_route_ranking import (
    ConfiguredCognitionRouteRanker,
    ConfiguredCognitionRouteRankingError,
)
from grox.configured_openai_cognition import ConfiguredOpenAICognition, ConfiguredOpenAICognitionResult
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Rank only current ready configured cognition candidates"
MISSION_ID = "MSN-configured-cognition-route-ranking"


def interpretation() -> MissionInterpretation:
    return MissionInterpretation.from_mapping(
        {
            "commander_intent": INTENT,
            "objective": "Rank a bounded current configured cognition route",
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


class ConfiguredCognitionRouteRankingTests(unittest.TestCase):
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
            f"rank candidate {model}",
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
    def _route(*candidates: ConfiguredCognitionFallbackCandidate) -> ConfiguredCognitionRoutePlanResult:
        ids = tuple(candidate.resource_id for candidate in candidates)
        return ConfiguredCognitionRoutePlanResult(
            candidate_order=ids,
            admitted_resource_ids=ids,
            ready_resource_ids=ids,
            primary_resource_id=ids[0],
            fallback_resource_ids=ids[1:],
            not_ready_reasons=MappingProxyType({}),
            mission_id=MISSION_ID,
            placement="mission_interpretation",
            _ready_candidates=tuple(candidates),
        )

    @staticmethod
    def _performance(
        candidate: ConfiguredCognitionFallbackCandidate,
        *,
        number: int,
        outcome: str,
        alias: str | None = None,
        mission_prefix: str = "MSN-history",
    ) -> ConfiguredCognitionAttemptPerformance:
        return ConfiguredCognitionAttemptPerformance(
            resource_id=candidate.resource_id,
            provider_kind=candidate.qualification.provider_kind,
            model=candidate.qualification.model,
            endpoint=candidate.qualification.endpoint,
            credential_alias=alias or candidate.qualification.credential_alias,
            mission_id=f"{mission_prefix}-{number}",
            order_id=f"ORD-history-{candidate.qualification.model}-{number}",
            selection_id=f"SEL-history-{candidate.qualification.model}-{number}",
            placement=candidate.fitness.placement,
            outcome=outcome,
            observation_id=(
                f"OBS-history-{candidate.qualification.model}-{number}"
                if outcome == "success"
                else None
            ),
        )

    def test_exact_timeout_reliability_reorders_only_current_ready_candidates(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        unrelated = self._candidate("model-c", "alias-c")
        route = self._route(first, second)
        history = [
            self._performance(first, number=1, outcome="provider_timeout"),
            self._performance(first, number=2, outcome="provider_timeout"),
            self._performance(second, number=1, outcome="success"),
            self._performance(second, number=2, outcome="success"),
            self._performance(unrelated, number=1, outcome="success"),
            self._performance(unrelated, number=2, outcome="success"),
        ]

        ranked = ConfiguredCognitionRouteRanker(route, history).rank()

        self.assertEqual(ranked.baseline_ready_resource_ids, (first.resource_id, second.resource_id))
        self.assertEqual(ranked.ready_resource_ids, (second.resource_id, first.resource_id))
        self.assertEqual(ranked.primary_resource_id, second.resource_id)
        self.assertEqual(ranked.fallback_resource_ids, (first.resource_id,))
        self.assertEqual(set(ranked.ready_resource_ids), {first.resource_id, second.resource_id})
        self.assertNotIn(unrelated.resource_id, ranked.ready_resource_ids)
        self.assertTrue(ranked.ranking_evaluated)
        self.assertTrue(ranked.ranking_applied)
        self.assertEqual(ranked.ranking_reason, "exact_timeout_reliability")
        self.assertEqual(ranked.ranking_sample_counts[first.resource_id], 2)
        self.assertEqual(ranked.ranking_sample_counts[second.resource_id], 2)
        self.assertEqual(ranked.ranking_scores[first.resource_id], 0.25)
        self.assertEqual(ranked.ranking_scores[second.resource_id], 0.75)
        self.assertEqual(ranked.fallback_policy.candidate_order, ranked.ready_resource_ids)
        evidence = ranked.evidence()
        self.assertTrue(evidence["ranking_enabled"])
        self.assertTrue(evidence["adaptive_scoring_enabled"])
        self.assertFalse(evidence["learning_enabled"])
        self.assertFalse(evidence["candidate_expansion"])
        self.assertFalse(evidence["authority_changed"])

    def test_credential_alias_rebind_history_is_not_attributed_to_current_identity(self):
        first = self._candidate("model-a", "alias-current-a")
        second = self._candidate("model-b", "alias-current-b")
        route = self._route(first, second)
        history = [
            self._performance(first, number=1, outcome="provider_timeout"),
            self._performance(first, number=2, outcome="provider_timeout"),
            self._performance(second, number=1, outcome="success", alias="alias-old-b"),
            self._performance(second, number=2, outcome="success", alias="alias-old-b"),
        ]

        ranked = ConfiguredCognitionRouteRanker(route, history).rank()

        self.assertFalse(ranked.ranking_applied)
        self.assertTrue(ranked.ranking_evaluated)
        self.assertEqual(ranked.ranking_reason, "insufficient_exact_history")
        self.assertEqual(ranked.ready_resource_ids, route.ready_resource_ids)
        self.assertEqual(ranked.ranking_sample_counts[first.resource_id], 2)
        self.assertEqual(ranked.ranking_sample_counts[second.resource_id], 0)
        self.assertEqual(dict(ranked.ranking_scores), {})

    def test_tied_exact_history_preserves_existing_current_ready_order(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        route = self._route(first, second)
        history = [
            self._performance(first, number=1, outcome="success"),
            self._performance(first, number=2, outcome="provider_timeout"),
            self._performance(second, number=1, outcome="provider_timeout"),
            self._performance(second, number=2, outcome="success"),
        ]

        ranked = ConfiguredCognitionRouteRanker(route, history).rank()

        self.assertTrue(ranked.ranking_applied)
        self.assertEqual(ranked.ranking_scores[first.resource_id], 0.5)
        self.assertEqual(ranked.ranking_scores[second.resource_id], 0.5)
        self.assertEqual(ranked.ready_resource_ids, route.ready_resource_ids)

    def test_current_mission_and_duplicate_attempt_identity_fail_closed(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        route = self._route(first, second)
        current = self._performance(
            first,
            number=1,
            outcome="success",
            mission_prefix=MISSION_ID.rsplit("-", 1)[0],
        )
        # Make the constructed Mission ID exactly equal the current route Mission.
        current = ConfiguredCognitionAttemptPerformance(
            resource_id=current.resource_id,
            provider_kind=current.provider_kind,
            model=current.model,
            endpoint=current.endpoint,
            credential_alias=current.credential_alias,
            mission_id=MISSION_ID,
            order_id=current.order_id,
            selection_id=current.selection_id,
            placement=current.placement,
            outcome=current.outcome,
            observation_id=current.observation_id,
        )
        with self.assertRaisesRegex(ConfiguredCognitionRouteRankingError, "current-Mission"):
            ConfiguredCognitionRouteRanker(route, [current])

        duplicate = self._performance(first, number=7, outcome="success")
        with self.assertRaisesRegex(ConfiguredCognitionRouteRankingError, "duplicate"):
            ConfiguredCognitionRouteRanker(route, [duplicate, duplicate])

    def test_insufficient_exact_history_preserves_policy_order_for_every_candidate(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        route = self._route(first, second)
        history = [
            self._performance(first, number=1, outcome="provider_timeout"),
            self._performance(first, number=2, outcome="provider_timeout"),
            self._performance(second, number=1, outcome="success"),
        ]

        ranked = ConfiguredCognitionRouteRanker(route, history).rank()

        self.assertEqual(ranked.ready_resource_ids, route.ready_resource_ids)
        self.assertFalse(ranked.ranking_applied)
        self.assertEqual(ranked.ranking_reason, "insufficient_exact_history")
        self.assertFalse(ranked.evidence()["adaptive_scoring_enabled"])


if __name__ == "__main__":
    unittest.main()
