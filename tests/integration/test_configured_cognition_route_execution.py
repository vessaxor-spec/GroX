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
from grox.configured_cognition_route_plan import ConfiguredCognitionRoutePlan
from grox.configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.selected_configured_cognition import SelectedConfiguredCognitionError
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Revalidate each planned cognition route attempt before execution"
MISSION_ID = "MSN-configured-cognition-route-execution-integration"
ROSTER = [{"crew_id": "backend-engineer", "title": "Backend Engineer"}]


def interpretation() -> MissionInterpretation:
    return MissionInterpretation.from_mapping(
        {
            "commander_intent": INTENT,
            "objective": "Exercise attempt-time route freshness",
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


class ConfiguredCognitionRouteExecutionIntegrationTests(unittest.TestCase):
    def test_primary_timeout_cannot_reach_fallback_after_fallback_readiness_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            def candidate(model: str, alias: str) -> ConfiguredCognitionFallbackCandidate:
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
                    VesselLayout.legacy(Path(tmp)),
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

            primary = candidate("model-primary", "alias-primary")
            fallback = candidate("model-fallback", "alias-fallback")
            candidates = (primary, fallback)
            policy = ConfiguredCognitionFallbackPolicy(tuple(item.resource_id for item in candidates))
            admission = ConfiguredCognitionRouteAdmission(candidates, policy).plan()

            def probe(item: ConfiguredCognitionFallbackCandidate, observed: float):
                q = item.qualification
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

            probes = {
                primary.resource_id: probe(primary, 195.0),
                fallback.resource_id: probe(fallback, 195.0),
            }
            route = ConfiguredCognitionRoutePlan(
                admission,
                probes,
                clock=lambda: 200.0,
                max_age_seconds=60.0,
            ).plan()
            execution_times = iter((205.0, 260.0))
            provider_calls: list[str] = []

            def invoke_selected(attempt, selection, *, roster):
                provider_calls.append(attempt.resource_id)
                if attempt.resource_id != primary.resource_id:
                    raise AssertionError("expired fallback must not reach selected invocation")
                try:
                    raise TimeoutError("primary provider timed out")
                except TimeoutError as timeout:
                    try:
                        raise ConfiguredOpenAICognitionError("configured invocation timed out") from timeout
                    except ConfiguredOpenAICognitionError as cognition:
                        raise SelectedConfiguredCognitionError("selected invocation failed") from cognition

            with patch.object(
                ConfiguredCognitionAttempt,
                "invoke_selected",
                new=invoke_selected,
            ), patch.object(
                SecretBroker,
                "materialize_env",
                side_effect=AssertionError("freshness revalidation must not rematerialize a secret"),
            ):
                with self.assertRaises(ConfiguredCognitionRouteExecutionError) as caught:
                    ConfiguredCognitionRouteExecution(
                        route,
                        probes,
                        clock=lambda: next(execution_times),
                        max_age_seconds=60.0,
                    ).invoke(roster=ROSTER)

            self.assertEqual(provider_calls, [primary.resource_id])
            self.assertEqual(caught.exception.resource_id, fallback.resource_id)
            self.assertEqual(caught.exception.reason, "stale_authenticated_model_visibility")
            self.assertEqual(caught.exception.observation_age_seconds, 65.0)
            self.assertEqual(route.ready_resource_ids, (primary.resource_id, fallback.resource_id))
            self.assertFalse(route.evidence()["selected"])


if __name__ == "__main__":
    unittest.main()
