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
    ConfiguredCognitionFallbackError,
    ConfiguredCognitionFallbackPolicy,
    ConfiguredCognitionFallbackPolicyError,
)
from grox.configured_cognition_fitness import ConfiguredCognitionFitnessResult
from grox.configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.selected_configured_cognition import (
    SelectedConfiguredCognition,
    SelectedConfiguredCognitionError,
    SelectedConfiguredCognitionResult,
)
from grox.tools.gateway import ToolDenied
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
INTENT = "Inspect configured cognition with bounded fallback"
MISSION_ID = "MSN-configured-cognition-fallback"
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


class ConfiguredCognitionFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
            secret_broker=SecretBroker({"alias-a": "SECRET-A", "alias-b": "SECRET-B", "alias-c": "SECRET-C"}),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _candidate(
        self,
        model: str,
        alias: str,
        *,
        mission_id: str = MISSION_ID,
        commander_intent: str = INTENT,
        mode: MissionMode = MissionMode.inspect,
    ) -> ConfiguredCognitionFallbackCandidate:
        cfg = config(model, alias)
        resource = ConfiguredCognitionDiscovery(cfg).inventory()["resources"][0]
        order = MissionOrder.new(
            mission_id,
            commander_intent,
            f"fallback candidate {model}",
            mode,
            "backend-engineer",
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
        result = ConfiguredOpenAICognitionResult(
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
        return ConfiguredCognitionFallbackCandidate(
            config=cfg,
            gateway=self.gateway,
            qualification=result,
            fitness=fitness,
            order=order,
        )

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

    @staticmethod
    def _raise_policy_failure() -> None:
        try:
            raise ToolDenied("network denied")
        except ToolDenied as denied:
            try:
                raise ConfiguredOpenAICognitionError("configured invocation denied") from denied
            except ConfiguredOpenAICognitionError as cognition:
                raise SelectedConfiguredCognitionError("selected invocation failed") from cognition

    @staticmethod
    def _raise_observation_timeout() -> None:
        try:
            raise TimeoutError("observation recorder timed out")
        except TimeoutError as timeout:
            raise SelectedConfiguredCognitionError("observation persistence failed") from timeout

    def test_primary_success_does_not_touch_fallback_candidate(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        fallback = ConfiguredCognitionFallback(
            [primary, secondary],
            ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
        )
        calls = []

        def invoke(_runner, selection, *, order, roster):
            calls.append(selection.resource_id)
            if selection.resource_id != primary.resource_id:
                raise AssertionError("fallback candidate must not run after primary success")
            return self._success(primary)

        with patch.object(SelectedConfiguredCognition, "invoke", new=invoke):
            report = fallback.invoke(roster=ROSTER)
        self.assertEqual(calls, [primary.resource_id])
        self.assertFalse(report.switched)
        self.assertEqual(report.attempted_resource_ids, (primary.resource_id,))
        self.assertEqual(report.timed_out_resource_ids, ())
        self.assertEqual(report.executed.resource_id, primary.resource_id)

    def test_provider_timeout_advances_once_to_next_explicit_candidate(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        fallback = ConfiguredCognitionFallback(
            [primary, secondary],
            ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
        )
        calls = []

        def invoke(_runner, selection, *, order, roster):
            calls.append(selection.resource_id)
            if selection.resource_id == primary.resource_id:
                self._raise_provider_timeout()
            if selection.resource_id == secondary.resource_id:
                return self._success(secondary)
            raise AssertionError("resource outside explicit envelope was invoked")

        with patch.object(SelectedConfiguredCognition, "invoke", new=invoke):
            report = fallback.invoke(roster=ROSTER)
        self.assertEqual(calls, [primary.resource_id, secondary.resource_id])
        self.assertTrue(report.switched)
        self.assertEqual(report.attempted_resource_ids, (primary.resource_id, secondary.resource_id))
        self.assertEqual(report.timed_out_resource_ids, (primary.resource_id,))
        self.assertEqual(report.executed.resource_id, secondary.resource_id)
        evidence = report.evidence()
        self.assertEqual(evidence["fallback_reason"], "provider_timeout")
        self.assertTrue(evidence["timeout_only_fallback"])
        self.assertFalse(evidence["candidate_expansion"])
        self.assertFalse(evidence["adaptive_routing_enabled"])
        self.assertFalse(evidence["authority_changed"])

    def test_non_timeout_provider_failure_never_falls_through(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        fallback = ConfiguredCognitionFallback(
            [primary, secondary],
            ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
        )
        calls = []

        def invoke(_runner, selection, *, order, roster):
            calls.append(selection.resource_id)
            if selection.resource_id == primary.resource_id:
                self._raise_policy_failure()
            raise AssertionError("non-timeout failure must never reach fallback candidate")

        with patch.object(SelectedConfiguredCognition, "invoke", new=invoke):
            with self.assertRaisesRegex(ConfiguredCognitionFallbackError, "non-recoverable"):
                fallback.invoke(roster=ROSTER)
        self.assertEqual(calls, [primary.resource_id])

    def test_observation_timeout_never_replays_provider_on_fallback(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        fallback = ConfiguredCognitionFallback(
            [primary, secondary],
            ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
        )
        calls = []

        def invoke(_runner, selection, *, order, roster):
            calls.append(selection.resource_id)
            if selection.resource_id == primary.resource_id:
                self._raise_observation_timeout()
            raise AssertionError("post-execution observation timeout must not duplicate cognition")

        with patch.object(SelectedConfiguredCognition, "invoke", new=invoke):
            with self.assertRaisesRegex(ConfiguredCognitionFallbackError, "non-recoverable"):
                fallback.invoke(roster=ROSTER)
        self.assertEqual(calls, [primary.resource_id])

    def test_explicit_envelope_rejects_duplicates_hidden_candidates_and_cross_mission_state(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        third = self._candidate("model-c", "alias-c")
        with self.assertRaises(ConfiguredCognitionFallbackPolicyError):
            ConfiguredCognitionFallbackPolicy((primary.resource_id, primary.resource_id))
        with self.assertRaisesRegex(ConfiguredCognitionFallbackPolicyError, "exactly match"):
            ConfiguredCognitionFallback(
                [primary, secondary, third],
                ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
            )
        foreign = self._candidate("model-b", "alias-b", mission_id="MSN-foreign")
        with self.assertRaisesRegex(ConfiguredCognitionFallbackPolicyError, "preserve one Mission"):
            ConfiguredCognitionFallback(
                [primary, foreign],
                ConfiguredCognitionFallbackPolicy((primary.resource_id, foreign.resource_id)),
            )

    def test_exhaustion_never_expands_beyond_policy_order(self):
        primary = self._candidate("model-a", "alias-a")
        secondary = self._candidate("model-b", "alias-b")
        fallback = ConfiguredCognitionFallback(
            [primary, secondary],
            ConfiguredCognitionFallbackPolicy((primary.resource_id, secondary.resource_id)),
        )
        calls = []

        def invoke(_runner, selection, *, order, roster):
            calls.append(selection.resource_id)
            self._raise_provider_timeout()

        with patch.object(SelectedConfiguredCognition, "invoke", new=invoke):
            with self.assertRaisesRegex(ConfiguredCognitionFallbackError, "envelope exhausted"):
                fallback.invoke(roster=ROSTER)
        self.assertEqual(calls, [primary.resource_id, secondary.resource_id])


if __name__ == "__main__":
    unittest.main()
