from __future__ import annotations

from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fallback import (
    ConfiguredCognitionFallback,
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
)
from grox.configured_cognition_fitness import ConfiguredCognitionFitnessResult
from grox.configured_cognition_route_admission import ConfiguredCognitionRouteAdmission
from grox.configured_cognition_route_plan import ConfiguredCognitionRoutePlan
from grox.configured_openai_cognition import ConfiguredOpenAICognition, ConfiguredOpenAICognitionResult
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Compose current cognition admission and readiness into a deterministic route"
MISSION_ID = "MSN-configured-cognition-route-plan-integration"


def _config(model: str, alias: str) -> dict[str, str]:
    return {
        "GROX_REASONER_PROVIDER": "openai",
        "GROX_REASONER_MODEL": model,
        "GROX_REASONER_ENDPOINT": ENDPOINT,
        "GROX_REASONER_CREDENTIAL_ALIAS": alias,
    }


def _interpretation() -> MissionInterpretation:
    return MissionInterpretation.from_mapping(
        {
            "commander_intent": INTENT,
            "objective": "Compose bounded cognition route evidence",
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


class ConfiguredCognitionRoutePlanIntegrationTests(unittest.TestCase):
    def test_admission_then_freshness_pruning_composes_exact_existing_fallback_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            def candidate(model: str, alias: str, *, available: bool = True):
                cfg = _config(model, alias)
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
                    _interpretation=_interpretation(),
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
                    secret_broker=SecretBroker({alias: f"SECRET-{alias}"} if available else {}),
                )
                return ConfiguredCognitionFallbackCandidate(
                    config=cfg,
                    gateway=gateway,
                    qualification=qualification,
                    fitness=fitness,
                    order=order,
                )

            denied = candidate("model-denied", "alias-denied", available=False)
            stale = candidate("model-stale", "alias-stale")
            primary = candidate("model-primary", "alias-primary")
            fallback = candidate("model-fallback", "alias-fallback")
            candidates = (denied, stale, primary, fallback)
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
                denied.resource_id: probe(denied, 195.0),
                stale.resource_id: probe(stale, 100.0),
                primary.resource_id: probe(primary, 190.0),
                fallback.resource_id: probe(fallback, 195.0),
            }
            with patch.object(SecretBroker, "materialize_env", side_effect=AssertionError("no secret reuse")), patch.object(
                LayoutToolGateway,
                "openai_model_probe",
                side_effect=AssertionError("no readiness network reuse"),
            ), patch.object(
                LayoutToolGateway,
                "openai_responses_cognition",
                side_effect=AssertionError("no cognition during route planning"),
            ):
                route = ConfiguredCognitionRoutePlan(
                    admission,
                    probes,
                    clock=lambda: 200.0,
                    max_age_seconds=60.0,
                ).plan()
                fallback_runtime = ConfiguredCognitionFallback(
                    route.ready_candidates,
                    route.fallback_policy,
                )

            self.assertEqual(admission.admitted_resource_ids, (stale.resource_id, primary.resource_id, fallback.resource_id))
            self.assertEqual(route.ready_resource_ids, (primary.resource_id, fallback.resource_id))
            self.assertEqual(route.primary_resource_id, primary.resource_id)
            self.assertEqual(route.fallback_resource_ids, (fallback.resource_id,))
            self.assertEqual(route.not_ready_reasons[stale.resource_id], "stale_authenticated_model_visibility")
            self.assertEqual(fallback_runtime._policy.candidate_order, (primary.resource_id, fallback.resource_id))
            self.assertFalse(route.evidence()["selected"])
            self.assertFalse(route.evidence()["fallback_invoked"])
            self.assertFalse(route.evidence()["adaptive_scoring_enabled"])


if __name__ == "__main__":
    unittest.main()
