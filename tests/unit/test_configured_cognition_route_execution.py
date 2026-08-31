from __future__ import annotations

from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_attempt import ConfiguredCognitionAttempt
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
from grox.configured_cognition_route_plan import (
    ConfiguredCognitionRoutePlan,
    ConfiguredCognitionRoutePlanResult,
)
from grox.configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.selected_configured_cognition import (
    SelectedConfiguredCognitionError,
    SelectedConfiguredCognitionResult,
)
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Execute only a currently fresh configured cognition route"
MISSION_ID = "MSN-configured-cognition-route-execution"
ROSTER = [{"crew_id": "backend-engineer", "title": "Backend Engineer"}]


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
            "objective": "Execute one bounded configured cognition route",
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


class ConfiguredCognitionRouteExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(self, model: str, alias: str) -> ConfiguredCognitionFallbackCandidate:
        cfg = config(model, alias)
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        order = MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"route candidate {model}",
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
            response_id=f"resp-{model}-qualification",
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

    def _route(
        self,
        candidates: tuple[ConfiguredCognitionFallbackCandidate, ...],
        probes: dict[str, dict[str, object]],
        *,
        now: float,
    ) -> ConfiguredCognitionRoutePlanResult:
        policy = ConfiguredCognitionFallbackPolicy(tuple(candidate.resource_id for candidate in candidates))
        admission = ConfiguredCognitionRouteAdmission(candidates, policy).plan()
        return ConfiguredCognitionRoutePlan(
            admission,
            probes,
            clock=lambda: now,
            max_age_seconds=60.0,
        ).plan()

    @staticmethod
    def _success(candidate: ConfiguredCognitionFallbackCandidate) -> SelectedConfiguredCognitionResult:
        return SelectedConfiguredCognitionResult(
            observation_id=f"OBS-{candidate.resource_id[-8:]}",
            selection_id=f"SEL-{candidate.resource_id[-8:]}",
            resource_id=candidate.resource_id,
            provider_kind=candidate.qualification.provider_kind,
            model=candidate.qualification.model,
            endpoint=candidate.qualification.endpoint,
            mission_id=candidate.order.mission_id,
            order_id=candidate.order.order_id,
            placement="mission_interpretation",
            response_id=f"resp-{candidate.qualification.model}-execution",
            response_model=candidate.qualification.model,
            _interpretation=interpretation(),
        )

    @staticmethod
    def _raise_provider_timeout() -> None:
        try:
            raise TimeoutError("provider timed out")
        except TimeoutError as timeout:
            try:
                raise ConfiguredOpenAICognitionError("configured invocation timed out") from timeout
            except ConfiguredOpenAICognitionError as cognition:
                raise SelectedConfiguredCognitionError("selected invocation failed") from cognition

    def test_primary_expiry_after_planning_fails_before_selection_or_provider_activity(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        probes = {
            primary.resource_id: self._probe(primary, 50.0),
            fallback.resource_id: self._probe(fallback, 50.0),
        }
        route = self._route((primary, fallback), probes, now=100.0)

        with patch.object(
            ConfiguredCognitionAttempt,
            "select",
            side_effect=AssertionError("stale route must fail before selection"),
        ), patch.object(
            ConfiguredCognitionAttempt,
            "invoke_selected",
            side_effect=AssertionError("stale route must fail before provider invocation"),
        ):
            with self.assertRaises(ConfiguredCognitionRouteExecutionError) as caught:
                ConfiguredCognitionRouteExecution(
                    route,
                    probes,
                    clock=lambda: 111.0,
                    max_age_seconds=60.0,
                ).invoke(roster=ROSTER)
        self.assertEqual(caught.exception.resource_id, primary.resource_id)
        self.assertEqual(caught.exception.reason, "stale_authenticated_model_visibility")
        self.assertEqual(caught.exception.observation_age_seconds, 61.0)

    def test_fallback_is_revalidated_after_primary_timeout_and_stale_fallback_stops(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }
        route = self._route((primary, fallback), probes, now=110.0)
        times = iter((120.0, 170.0))
        provider_calls: list[str] = []

        def invoke_selected(attempt, selection, *, roster):
            provider_calls.append(attempt.resource_id)
            if attempt.resource_id == primary.resource_id:
                self._raise_provider_timeout()
            raise AssertionError("stale fallback must never reach provider invocation")

        with patch.object(ConfiguredCognitionAttempt, "invoke_selected", new=invoke_selected):
            with self.assertRaises(ConfiguredCognitionRouteExecutionError) as caught:
                ConfiguredCognitionRouteExecution(
                    route,
                    probes,
                    clock=lambda: next(times),
                    max_age_seconds=60.0,
                ).invoke(roster=ROSTER)
        self.assertEqual(provider_calls, [primary.resource_id])
        self.assertEqual(caught.exception.resource_id, fallback.resource_id)
        self.assertEqual(caught.exception.reason, "stale_authenticated_model_visibility")
        self.assertEqual(caught.exception.observation_age_seconds, 70.0)

    def test_timeout_advances_only_to_fallback_that_is_fresh_at_its_own_attempt(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }
        route = self._route((primary, fallback), probes, now=110.0)
        times = iter((120.0, 130.0))
        provider_calls: list[str] = []

        def invoke_selected(attempt, selection, *, roster):
            provider_calls.append(attempt.resource_id)
            if attempt.resource_id == primary.resource_id:
                self._raise_provider_timeout()
            if attempt.resource_id == fallback.resource_id:
                return self._success(fallback)
            raise AssertionError("candidate expansion occurred")

        with patch.object(ConfiguredCognitionAttempt, "invoke_selected", new=invoke_selected):
            result = ConfiguredCognitionRouteExecution(
                route,
                probes,
                clock=lambda: next(times),
                max_age_seconds=60.0,
            ).invoke(roster=ROSTER)

        self.assertEqual(provider_calls, [primary.resource_id, fallback.resource_id])
        self.assertEqual(result.attempted_resource_ids, (primary.resource_id, fallback.resource_id))
        self.assertEqual(result.timed_out_resource_ids, (primary.resource_id,))
        self.assertEqual(result.executed.resource_id, fallback.resource_id)
        self.assertEqual(result.attempt_readiness_age_seconds[primary.resource_id], 20.0)
        self.assertEqual(result.attempt_readiness_age_seconds[fallback.resource_id], 30.0)
        evidence = result.evidence()
        self.assertTrue(evidence["fresh_readiness_revalidated_per_attempt"])
        self.assertTrue(evidence["ready_at_plan_time_not_sufficient"])
        self.assertEqual(evidence["fallback_reason"], "provider_timeout")
        self.assertFalse(evidence["candidate_expansion"])
        self.assertFalse(evidence["adaptive_routing_enabled"])
        self.assertFalse(evidence["authority_changed"])

    def test_single_candidate_route_uses_same_shared_attempt_seam(self):
        primary = self._candidate("model-primary", "alias-primary")
        probe = self._probe(primary, 100.0)
        route = ConfiguredCognitionRoutePlanResult(
            candidate_order=(primary.resource_id,),
            admitted_resource_ids=(primary.resource_id,),
            ready_resource_ids=(primary.resource_id,),
            primary_resource_id=primary.resource_id,
            fallback_resource_ids=(),
            not_ready_reasons=MappingProxyType({}),
            mission_id=primary.order.mission_id,
            placement="mission_interpretation",
            _ready_candidates=(primary,),
        )
        provider_calls: list[str] = []

        def invoke_selected(attempt, selection, *, roster):
            provider_calls.append(attempt.resource_id)
            return self._success(primary)

        with patch.object(ConfiguredCognitionAttempt, "invoke_selected", new=invoke_selected):
            result = ConfiguredCognitionRouteExecution(
                route,
                {primary.resource_id: probe},
                clock=lambda: 120.0,
                max_age_seconds=60.0,
            ).invoke(roster=ROSTER)

        self.assertEqual(provider_calls, [primary.resource_id])
        self.assertEqual(result.candidate_order, (primary.resource_id,))
        self.assertEqual(result.attempted_resource_ids, (primary.resource_id,))
        self.assertEqual(result.timed_out_resource_ids, ())
        self.assertFalse(result.switched)


if __name__ == "__main__":
    unittest.main()
