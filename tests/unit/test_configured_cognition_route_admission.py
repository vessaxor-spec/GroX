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
from grox.configured_cognition_route_admission import (
    ConfiguredCognitionRouteAdmission,
    ConfiguredCognitionRouteAdmissionError,
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
INTENT = "Route configured cognition only through current admitted gates"
MISSION_ID = "MSN-configured-cognition-route-admission"


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
            "objective": "Route configured cognition safely",
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


class ConfiguredCognitionRouteAdmissionTests(unittest.TestCase):
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
        network_enabled: bool = True,
        allowed_origins: frozenset[str] = frozenset({ORIGIN}),
        secret_grant: str | None = None,
        order_origins: list[str] | None = None,
        cfg: dict[str, str] | None = None,
    ) -> ConfiguredCognitionFallbackCandidate:
        cfg = dict(cfg or config(model, alias))
        resource = ConfiguredCognitionDiscovery(config(model, alias)).inventory()["resources"][0]
        order = MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"route admission candidate {model}",
            MissionMode.inspect,
            "backend-engineer",
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": ConfiguredOpenAICognition.operation,
                "resource_id": resource["resource_id"],
                "provider_kind": resource["provider_kind"],
                "model": resource["model"],
                "endpoint": resource["endpoint"],
                "credential_alias": alias,
                "allowed_origins": list(order_origins if order_origins is not None else [ORIGIN]),
                "secret_grants": [secret_grant if secret_grant is not None else alias],
            },
        ).seal()
        result = ConfiguredOpenAICognitionResult(
            resource_id=resource["resource_id"],
            provider_kind="openai",
            model=model,
            endpoint=ENDPOINT,
            credential_alias=alias,
            mission_id=order.mission_id,
            order_id=order.order_id,
            response_id=f"resp-{model}-historical",
            response_model=model,
            _interpretation=interpretation(),
        )
        fitness = ConfiguredCognitionFitnessResult(
            status="PASS",
            resource_id=result.resource_id,
            provider_kind=result.provider_kind,
            model=result.model,
            endpoint=result.endpoint,
            credential_alias=result.credential_alias,
            mission_id=result.mission_id,
            order_id=result.order_id,
            placement="mission_interpretation",
            checks=MappingProxyType({"qualified": True}),
        )
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(
                network_enabled=network_enabled,
                allowed_origins=allowed_origins,
            ),
            secret_broker=SecretBroker({alias: f"SECRET-{alias}"} if alias_available else {}),
        )
        return ConfiguredCognitionFallbackCandidate(
            config=cfg,
            gateway=gateway,
            qualification=result,
            fitness=fitness,
            order=order,
        )

    @staticmethod
    def _policy(*candidates: ConfiguredCognitionFallbackCandidate) -> ConfiguredCognitionFallbackPolicy:
        return ConfiguredCognitionFallbackPolicy(tuple(candidate.resource_id for candidate in candidates))

    def test_current_gates_admit_exact_candidates_without_runtime_side_effects(self):
        first = self._candidate("model-a", "alias-a")
        second = self._candidate("model-b", "alias-b")
        planner = ConfiguredCognitionRouteAdmission([first, second], self._policy(first, second))

        with patch.object(SecretBroker, "materialize_env", side_effect=AssertionError("secret must not materialize")), patch.object(
            LayoutToolGateway,
            "openai_responses_cognition",
            side_effect=AssertionError("cognition must not run"),
        ):
            result = planner.plan()

        self.assertEqual(result.admitted_resource_ids, (first.resource_id, second.resource_id))
        self.assertEqual(result.admitted_candidates, (first, second))
        self.assertEqual(dict(result.rejected_reasons), {})
        evidence = result.evidence()
        self.assertTrue(evidence["current_control_plane_revalidated"])
        self.assertFalse(evidence["provider_readiness_claim"])
        self.assertFalse(evidence["historical_success_used_as_current_readiness"])
        self.assertFalse(evidence["ready"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["network_invoked"])
        self.assertFalse(evidence["secret_materialized"])
        self.assertFalse(evidence["ranking_enabled"])
        self.assertFalse(evidence["adaptive_scoring_enabled"])
        self.assertFalse(evidence["authority_changed"])

    def test_missing_current_credential_alias_is_excluded_before_routing(self):
        unavailable = self._candidate("model-a", "alias-a", alias_available=False)
        admitted = self._candidate("model-b", "alias-b")
        result = ConfiguredCognitionRouteAdmission(
            [unavailable, admitted],
            self._policy(unavailable, admitted),
        ).plan()
        self.assertEqual(result.admitted_resource_ids, (admitted.resource_id,))
        self.assertEqual(
            result.rejected_reasons[unavailable.resource_id],
            "credential_alias_unavailable",
        )

    def test_secret_grant_mismatch_is_excluded_without_secret_materialization(self):
        denied = self._candidate("model-a", "alias-a", secret_grant="other-alias")
        admitted = self._candidate("model-b", "alias-b")
        with patch.object(SecretBroker, "materialize_env", side_effect=AssertionError("secret must not materialize")):
            result = ConfiguredCognitionRouteAdmission(
                [denied, admitted],
                self._policy(denied, admitted),
            ).plan()
        self.assertEqual(result.admitted_resource_ids, (admitted.resource_id,))
        self.assertEqual(result.rejected_reasons[denied.resource_id], "credential_use_not_authorized")

    def test_current_config_rebind_is_excluded(self):
        rebound = self._candidate(
            "model-a",
            "alias-a",
            cfg=config("model-rebound", "alias-a"),
        )
        admitted = self._candidate("model-b", "alias-b")
        result = ConfiguredCognitionRouteAdmission(
            [rebound, admitted],
            self._policy(rebound, admitted),
        ).plan()
        self.assertEqual(result.admitted_resource_ids, (admitted.resource_id,))
        self.assertIn(
            result.rejected_reasons[rebound.resource_id],
            {"current_config_binding_unavailable", "current_config_identity_changed"},
        )

    def test_host_network_or_endpoint_scope_denial_excludes_candidate(self):
        host_denied = self._candidate("model-a", "alias-a", network_enabled=False)
        scope_denied = self._candidate(
            "model-b",
            "alias-b",
            order_origins=["https://example.invalid"],
        )
        admitted = self._candidate("model-c", "alias-c")
        result = ConfiguredCognitionRouteAdmission(
            [host_denied, scope_denied, admitted],
            self._policy(host_denied, scope_denied, admitted),
        ).plan()
        self.assertEqual(result.admitted_resource_ids, (admitted.resource_id,))
        self.assertEqual(
            result.rejected_reasons[host_denied.resource_id],
            "network_disabled_by_host_policy",
        )
        self.assertEqual(
            result.rejected_reasons[scope_denied.resource_id],
            "endpoint_scope_not_authorized",
        )

    def test_all_candidates_rejected_fails_closed_with_bounded_reasons(self):
        first = self._candidate("model-a", "alias-a", alias_available=False)
        second = self._candidate("model-b", "alias-b", alias_available=False)
        with self.assertRaisesRegex(ConfiguredCognitionRouteAdmissionError, "no explicit") as caught:
            ConfiguredCognitionRouteAdmission([first, second], self._policy(first, second)).plan()
        self.assertEqual(
            dict(caught.exception.rejections),
            {
                first.resource_id: "credential_alias_unavailable",
                second.resource_id: "credential_alias_unavailable",
            },
        )


if __name__ == "__main__":
    unittest.main()
