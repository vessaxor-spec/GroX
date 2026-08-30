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
from grox.configured_openai_cognition import ConfiguredOpenAICognition, ConfiguredOpenAICognitionResult
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Compose current route admission with bounded fallback"
MISSION_ID = "MSN-route-admission-integration"


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
            "objective": "Compose admitted candidates",
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


class ConfiguredCognitionRouteAdmissionIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(self, model: str, alias: str, *, available: bool) -> ConfiguredCognitionFallbackCandidate:
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
            provider_kind=qualification.provider_kind,
            model=qualification.model,
            endpoint=qualification.endpoint,
            credential_alias=qualification.credential_alias,
            mission_id=qualification.mission_id,
            order_id=qualification.order_id,
            placement="mission_interpretation",
            checks=MappingProxyType({"qualified": True}),
        )
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
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

    def test_current_admission_prunes_ineligible_candidate_and_composes_exact_remaining_fallback(self):
        stale = self._candidate("model-a", "alias-a", available=False)
        primary = self._candidate("model-b", "alias-b", available=True)
        fallback = self._candidate("model-c", "alias-c", available=True)
        envelope = ConfiguredCognitionFallbackPolicy(
            (stale.resource_id, primary.resource_id, fallback.resource_id)
        )

        with patch.object(SecretBroker, "materialize_env", side_effect=AssertionError("preflight must stay secret-blind")), patch.object(
            LayoutToolGateway,
            "openai_responses_cognition",
            side_effect=AssertionError("preflight must not invoke cognition"),
        ):
            plan = ConfiguredCognitionRouteAdmission(
                [stale, primary, fallback],
                envelope,
            ).plan()

        self.assertEqual(plan.admitted_resource_ids, (primary.resource_id, fallback.resource_id))
        self.assertEqual(plan.rejected_reasons[stale.resource_id], "credential_alias_unavailable")
        admitted_policy = ConfiguredCognitionFallbackPolicy(plan.admitted_resource_ids)
        composed = ConfiguredCognitionFallback(plan.admitted_candidates, admitted_policy)
        self.assertIsInstance(composed, ConfiguredCognitionFallback)
        evidence = plan.evidence()
        self.assertFalse(evidence["ready"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["fallback_invoked"])
        self.assertFalse(evidence["authority_changed"])


if __name__ == "__main__":
    unittest.main()
