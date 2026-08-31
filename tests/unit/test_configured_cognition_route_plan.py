from __future__ import annotations

from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fallback import (
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
)
from grox.configured_cognition_fitness import ConfiguredCognitionFitnessResult
from grox.configured_cognition_route_admission import ConfiguredCognitionRouteAdmission
from grox.configured_cognition_route_plan import (
    ConfiguredCognitionRoutePlan,
    ConfiguredCognitionRoutePlanError,
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
INTENT = "Plan configured cognition route only from current fresh evidence"
MISSION_ID = "MSN-configured-cognition-route-plan"


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
            "objective": "Plan one bounded configured cognition route",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": [],
            "candidate_crew_ids": ["backend-engineer"],
            "options": [{
                "name": "inspect",
                "rationale": "Use bounded inspection.",
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


class ConfiguredCognitionRoutePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(
        self,
        model: str,
        alias: str,
        *,
        alias_available: bool = True,
    ) -> ConfiguredCognitionFallbackCandidate:
        cfg = config(model, alias)
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        order = MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"route plan candidate {model}",
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
            secret_broker=SecretBroker({alias: f"SECRET-{alias}"} if alias_available else {}),
        )
        return ConfiguredCognitionFallbackCandidate(
            config=cfg,
            gateway=gateway,
            qualification=qualification,
            fitness=fitness,
            order=order,
        )

    @staticmethod
    def _policy(*candidates: ConfiguredCognitionFallbackCandidate) -> ConfiguredCognitionFallbackPolicy:
        return ConfiguredCognitionFallbackPolicy(tuple(candidate.resource_id for candidate in candidates))

    @staticmethod
    def _probe(candidate: ConfiguredCognitionFallbackCandidate, *, observed: float) -> dict[str, object]:
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

    def _admit(self, *candidates: ConfiguredCognitionFallbackCandidate):
        return ConfiguredCognitionRouteAdmission(candidates, self._policy(*candidates)).plan()

    def test_stale_first_candidate_is_pruned_and_ready_policy_order_is_preserved(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        third = self._candidate("model-c", "alias-c")
        admission = self._admit(first, second, third)
        probes = {
            first.resource_id: self._probe(first, observed=100.0),
            second.resource_id: self._probe(second, observed=170.0),
            third.resource_id: self._probe(third, observed=180.0),
        }

        result = ConfiguredCognitionRoutePlan(
            admission,
            probes,
            clock=lambda: 200.0,
            max_age_seconds=60.0,
        ).plan()

        self.assertEqual(result.ready_resource_ids, (second.resource_id, third.resource_id))
        self.assertEqual(result.primary_resource_id, second.resource_id)
        self.assertEqual(result.fallback_resource_ids, (third.resource_id,))
        self.assertEqual(result.not_ready_reasons[first.resource_id], "stale_authenticated_model_visibility")
        self.assertEqual(result.ready_candidates, (second, third))
        self.assertIsNotNone(result.fallback_policy)
        self.assertEqual(result.fallback_policy.candidate_order, (second.resource_id, third.resource_id))
        evidence = result.evidence()
        self.assertTrue(evidence["fresh_readiness_revalidated_at_plan_time"])
        self.assertTrue(evidence["deterministic_policy_order"])
        self.assertFalse(evidence["active_selection_created"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["ranking_enabled"])
        self.assertFalse(evidence["historical_scoring_used"])
        self.assertFalse(evidence["adaptive_scoring_enabled"])

    def test_unadmitted_candidate_cannot_enter_route_even_with_fresh_probe(self):
        denied = self._candidate("model-a", "alias-a", alias_available=False)
        first = self._candidate("model-b", "alias-b")
        second = self._candidate("model-c", "alias-c")
        admission = self._admit(denied, first, second)
        result = ConfiguredCognitionRoutePlan(
            admission,
            {
                denied.resource_id: self._probe(denied, observed=100.0),
                first.resource_id: self._probe(first, observed=100.0),
                second.resource_id: self._probe(second, observed=100.0),
            },
            clock=lambda: 110.0,
        ).plan()

        self.assertNotIn(denied.resource_id, result.ready_resource_ids)
        self.assertEqual(result.ready_resource_ids, (first.resource_id, second.resource_id))
        self.assertEqual(result.primary_resource_id, first.resource_id)

    def test_one_planning_instant_is_used_for_every_candidate(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        admission = self._admit(first, second)
        calls = []

        def clock():
            calls.append(True)
            return 160.0

        result = ConfiguredCognitionRoutePlan(
            admission,
            {
                first.resource_id: self._probe(first, observed=100.0),
                second.resource_id: self._probe(second, observed=100.0),
            },
            clock=clock,
            max_age_seconds=60.0,
        ).plan()

        self.assertEqual(len(calls), 1)
        self.assertEqual(result.ready_resource_ids, (first.resource_id, second.resource_id))

    def test_missing_invalid_and_stale_probe_evidence_fail_closed_when_no_candidate_remains(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        admission = self._admit(first, second)
        with self.assertRaisesRegex(ConfiguredCognitionRoutePlanError, "no admitted") as caught:
            ConfiguredCognitionRoutePlan(
                admission,
                {
                    first.resource_id: self._probe(first, observed=0.0),
                    second.resource_id: "not-a-probe",
                },
                clock=lambda: 100.0,
                max_age_seconds=60.0,
            ).plan()
        self.assertEqual(
            dict(caught.exception.rejections),
            {
                first.resource_id: "stale_authenticated_model_visibility",
                second.resource_id: "readiness_evidence_missing_or_invalid",
            },
        )

    def test_route_planning_never_reuses_secret_network_or_provider_execution(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        admission = self._admit(first, second)
        probes = {
            first.resource_id: self._probe(first, observed=100.0),
            second.resource_id: self._probe(second, observed=100.0),
        }
        with patch.object(SecretBroker, "materialize_env", side_effect=AssertionError("secret reuse")), patch.object(
            LayoutToolGateway,
            "openai_model_probe",
            side_effect=AssertionError("network reuse"),
        ), patch.object(
            LayoutToolGateway,
            "openai_responses_cognition",
            side_effect=AssertionError("cognition reuse"),
        ):
            result = ConfiguredCognitionRoutePlan(admission, probes, clock=lambda: 101.0).plan()
        self.assertEqual(result.primary_resource_id, first.resource_id)
        self.assertFalse(result.evidence()["network_invoked"])
        self.assertFalse(result.evidence()["secret_materialized"])


if __name__ == "__main__":
    unittest.main()
