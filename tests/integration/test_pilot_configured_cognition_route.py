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
from grox.configured_cognition_route_admission import ConfiguredCognitionRouteAdmissionError
from grox.configured_cognition_route_execution import ConfiguredCognitionRouteExecutionError
from grox.configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from grox.contracts import MissionMode, MissionOrder
from grox.pilot import PilotGorXu
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Use Pilot GorXu to control a bounded configured cognition route"
MISSION_ID = "MSN-pilot-configured-cognition-route"


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
            "objective": "Use only the bounded configured cognition route",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": [],
            "candidate_crew_ids": [],
            "options": [
                {
                    "name": "bounded-route",
                    "rationale": "Preserve exact governed route state.",
                    "advantages": ["bounded"],
                    "risks": [],
                    "crew_ids": [],
                }
            ],
            "recommended_option": "bounded-route",
            "confidence": 0.9,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        },
        expected_intent=INTENT,
    )


class PilotConfiguredCognitionRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name) / "pilot"
        (root / "configs/crew/dossiers").mkdir(parents=True)
        (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
        (root / "configs/crew/company-manifest.json").write_text(
            '{"crew": []}', encoding="utf-8"
        )
        self.pilot = PilotGorXu(root, reasoner=None)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(
        self,
        model: str,
        alias: str,
        *,
        secret_available: bool = True,
    ) -> ConfiguredCognitionFallbackCandidate:
        cfg = config(model, alias)
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        order = MissionOrder.new(
            MISSION_ID,
            INTENT,
            f"configured route candidate {model}",
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
        broker = SecretBroker({alias: f"SECRET-{alias}"} if secret_available else {})
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name) / f"candidate-{model}"),
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({ORIGIN}),
            ),
            secret_broker=broker,
        )
        return ConfiguredCognitionFallbackCandidate(
            config=cfg,
            gateway=gateway,
            qualification=qualification,
            fitness=fitness,
            order=order,
        )

    @staticmethod
    def _probe(
        candidate: ConfiguredCognitionFallbackCandidate,
        observed: float,
    ) -> dict[str, object]:
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
    def _success_for_order(order: MissionOrder) -> ConfiguredOpenAICognitionResult:
        return ConfiguredOpenAICognitionResult(
            resource_id=str(order.parameters["resource_id"]),
            provider_kind="openai",
            model=str(order.parameters["model"]),
            endpoint=str(order.parameters["endpoint"]),
            credential_alias=str(order.parameters["credential_alias"]),
            mission_id=order.mission_id,
            order_id=order.order_id,
            response_id=f"resp-{order.parameters['model']}-pilot",
            response_model=str(order.parameters["model"]),
            _interpretation=interpretation(),
        )

    @staticmethod
    def _raise_timeout() -> None:
        try:
            raise TimeoutError("provider timed out")
        except TimeoutError as timeout:
            raise ConfiguredOpenAICognitionError(
                "configured invocation timed out"
            ) from timeout

    def test_gorxu_plans_and_executes_existing_route_with_exact_observation(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        candidates = (primary, fallback)
        policy = ConfiguredCognitionFallbackPolicy(
            tuple(candidate.resource_id for candidate in candidates)
        )
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }

        route = self.pilot.plan_configured_cognition_route(
            candidates,
            policy,
            probes,
            clock=lambda: 110.0,
            max_age_seconds=60.0,
        )
        self.assertEqual(route.primary_resource_id, primary.resource_id)
        self.assertEqual(route.fallback_resource_ids, (fallback.resource_id,))

        def invoke(cognition, *, order, roster):
            return self._success_for_order(order)

        with patch.object(ConfiguredOpenAICognition, "invoke", new=invoke):
            result = self.pilot.execute_configured_cognition_route(
                route,
                probes,
                clock=lambda: 120.0,
                max_age_seconds=60.0,
            )

        self.assertEqual(result.executed.resource_id, primary.resource_id)
        self.assertEqual(result.attempted_resource_ids, (primary.resource_id,))
        self.assertEqual(result.timed_out_resource_ids, ())
        self.assertTrue(result.evidence()["selected"])
        self.assertTrue(result.evidence()["observed"])
        self.assertFalse(result.evidence()["authority_changed"])
        history = self.pilot.store.resource_observations(
            resource_id=primary.resource_id,
            limit=10,
        )
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["identity"]["resource_id"], primary.resource_id)
        self.assertEqual(history[0]["identity"]["model"], "model-primary")

    def test_gorxu_route_planning_rejects_candidates_without_current_alias_availability(self):
        primary = self._candidate(
            "model-primary",
            "alias-primary",
            secret_available=False,
        )
        fallback = self._candidate(
            "model-fallback",
            "alias-fallback",
            secret_available=False,
        )
        candidates = (primary, fallback)
        policy = ConfiguredCognitionFallbackPolicy(
            tuple(candidate.resource_id for candidate in candidates)
        )
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }

        with self.assertRaises(ConfiguredCognitionRouteAdmissionError):
            self.pilot.plan_configured_cognition_route(
                candidates,
                policy,
                probes,
                clock=lambda: 110.0,
                max_age_seconds=60.0,
            )

    def test_gorxu_execution_revalidates_freshness_before_selection(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        candidates = (primary, fallback)
        policy = ConfiguredCognitionFallbackPolicy(
            tuple(candidate.resource_id for candidate in candidates)
        )
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }
        route = self.pilot.plan_configured_cognition_route(
            candidates,
            policy,
            probes,
            clock=lambda: 110.0,
            max_age_seconds=60.0,
        )

        with patch.object(
            ConfiguredOpenAICognition,
            "invoke",
            side_effect=AssertionError("stale route must fail before provider invocation"),
        ):
            with self.assertRaises(ConfiguredCognitionRouteExecutionError) as caught:
                self.pilot.execute_configured_cognition_route(
                    route,
                    probes,
                    clock=lambda: 170.0,
                    max_age_seconds=60.0,
                )

        self.assertEqual(caught.exception.resource_id, primary.resource_id)
        self.assertEqual(caught.exception.reason, "stale_authenticated_model_visibility")
        self.assertEqual(self.pilot.store.resource_observations(limit=10), [])

    def test_gorxu_preserves_timeout_only_fallback_and_exact_executed_identity(self):
        primary = self._candidate("model-primary", "alias-primary")
        fallback = self._candidate("model-fallback", "alias-fallback")
        candidates = (primary, fallback)
        policy = ConfiguredCognitionFallbackPolicy(
            tuple(candidate.resource_id for candidate in candidates)
        )
        probes = {
            primary.resource_id: self._probe(primary, 100.0),
            fallback.resource_id: self._probe(fallback, 100.0),
        }
        route = self.pilot.plan_configured_cognition_route(
            candidates,
            policy,
            probes,
            clock=lambda: 110.0,
            max_age_seconds=60.0,
        )
        times = iter((120.0, 130.0))
        calls: list[str] = []

        def invoke(cognition, *, order, roster):
            resource_id = str(order.parameters["resource_id"])
            calls.append(resource_id)
            if resource_id == primary.resource_id:
                self._raise_timeout()
            return self._success_for_order(order)

        with patch.object(ConfiguredOpenAICognition, "invoke", new=invoke):
            result = self.pilot.execute_configured_cognition_route(
                route,
                probes,
                clock=lambda: next(times),
                max_age_seconds=60.0,
            )

        self.assertEqual(calls, [primary.resource_id, fallback.resource_id])
        self.assertEqual(
            result.attempted_resource_ids,
            (primary.resource_id, fallback.resource_id),
        )
        self.assertEqual(result.timed_out_resource_ids, (primary.resource_id,))
        self.assertEqual(result.executed.resource_id, fallback.resource_id)
        self.assertEqual(result.evidence()["fallback_reason"], "provider_timeout")
        self.assertTrue(result.evidence()["timeout_only_fallback"])
        self.assertFalse(result.evidence()["candidate_expansion"])
        self.assertFalse(result.evidence()["authority_changed"])


if __name__ == "__main__":
    unittest.main()
