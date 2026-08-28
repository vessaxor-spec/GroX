from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_cognition_fitness import ConfiguredCognitionMissionFitness
from grox.configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionPolicy,
)
from grox.configured_openai_cognition import ConfiguredOpenAICognition
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.contracts import MissionInterpretation
from grox.runtime_layout import VesselLayout
from grox.selected_configured_cognition import (
    SelectedConfiguredCognition,
    SelectedConfiguredCognitionError,
)
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
INTENT = "Inspect configured cognition safely"
ROSTER = [
    {"crew_id": "backend-engineer", "title": "Backend Engineer"},
    {"crew_id": "application-security-engineer", "title": "Application Security Engineer"},
]
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}


class SelectedConfiguredCognitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(network_enabled=True, allowed_origins=frozenset({ORIGIN})),
            secret_broker=SecretBroker({ALIAS: "SECRET-SENTINEL"}),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource(config=CONFIG):
        return ConfiguredCognitionDiscovery(config).inventory()["resources"][0]

    def _order(self):
        resource = self._resource()
        return MissionOrder.new(
            "MSN-selected-configured-cognition",
            INTENT,
            "invoke selected configured cognition",
            MissionMode.inspect,
            "application-security-engineer",
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": ConfiguredOpenAICognition.operation,
                "resource_id": resource["resource_id"],
                "provider_kind": resource["provider_kind"],
                "model": resource["model"],
                "endpoint": resource["endpoint"],
                "credential_alias": ALIAS,
                "allowed_origins": [ORIGIN],
                "secret_grants": [ALIAS],
            },
        ).seal()

    @staticmethod
    def _interpretation():
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

    def _selected(self, order):
        transport = {
            "schema": "grox-openai-responses-cognition-transport-v1",
            "status": 200,
            "response_id": "resp_qualification",
            "response_model": MODEL,
            "interpretation": self._interpretation(),
            "raw_response_returned": False,
        }
        with patch.object(self.gateway, "openai_responses_cognition", return_value=transport):
            result = ConfiguredOpenAICognition(CONFIG, self.gateway).invoke(order=order, roster=ROSTER)
        fitness = ConfiguredCognitionMissionFitness.evaluate(result, order=order, roster=ROSTER)
        self.assertTrue(fitness.qualified_fit)
        selector = ConfiguredCognitionSelection(CONFIG)
        selection = selector.select(
            result,
            fitness,
            order=order,
            policy=ConfiguredCognitionSelectionPolicy(resource_id=result.resource_id),
        )
        return selector, selection, result

    def test_active_exact_selection_invokes_and_promotes_only_observed_execution(self):
        order = self._order()
        selector, selection, result = self._selected(order)
        observed_calls = []
        runner = SelectedConfiguredCognition(
            CONFIG,
            self.gateway,
            selector,
            observation_recorder=lambda **kwargs: observed_calls.append(kwargs),
        )
        actual = replace(result, response_id="resp_selected")
        with patch.object(runner._cognition, "invoke", return_value=actual) as invoke:
            report = runner.invoke(selection, order=order, roster=ROSTER)
        invoke.assert_called_once_with(order=order, roster=ROSTER)
        evidence = report.evidence()
        self.assertTrue(evidence["selected"])
        self.assertTrue(evidence["observed"])
        self.assertTrue(evidence["network_invoked"])
        self.assertTrue(evidence["secret_materialized"])
        self.assertTrue(evidence["cognition_invoked"])
        self.assertTrue(evidence["cognition_succeeded"])
        self.assertFalse(evidence["fallback_enabled"])
        self.assertFalse(evidence["switching_enabled"])
        self.assertFalse(evidence["adaptive_routing_enabled"])
        self.assertFalse(evidence["authority_changed"])
        self.assertFalse(evidence["raw_response_returned"])
        self.assertEqual(report.interpretation.commander_intent, INTENT)
        self.assertEqual(len(observed_calls), 1)
        stored = runner.observation(report.observation_id)
        self.assertEqual(stored["selection_id"], selection.selection_id)
        self.assertNotIn("credential_alias", stored)
        self.assertNotIn("interpretation", stored)

    def test_reconstituted_selection_fails_before_binding_or_provider_activity(self):
        order = self._order()
        selector, selection, _ = self._selected(order)
        selector.reconstitute()
        runner = SelectedConfiguredCognition(CONFIG, self.gateway, selector)
        with patch.object(
            runner._binding,
            "inventory",
            side_effect=AssertionError("stale selection must fail before binding discovery"),
        ) as binding, patch.object(
            runner._cognition,
            "invoke",
            side_effect=AssertionError("stale selection must fail before provider activity"),
        ) as invoke:
            with self.assertRaisesRegex(SelectedConfiguredCognitionError, "active exact selection"):
                runner.invoke(selection, order=order, roster=ROSTER)
        binding.assert_not_called()
        invoke.assert_not_called()

    def test_current_binding_rebind_fails_before_provider_activity(self):
        order = self._order()
        selector, selection, _ = self._selected(order)
        rebound = dict(CONFIG)
        rebound["GROX_REASONER_CREDENTIAL_ALIAS"] = "rotated-alias"
        runner = SelectedConfiguredCognition(rebound, self.gateway, selector)
        with patch.object(
            runner._cognition,
            "invoke",
            side_effect=AssertionError("rebound selection must fail before provider activity"),
        ) as invoke:
            with self.assertRaisesRegex(SelectedConfiguredCognitionError, "binding differs"):
                runner.invoke(selection, order=order, roster=ROSTER)
        invoke.assert_not_called()

    def test_actual_identity_mismatch_never_becomes_observed(self):
        order = self._order()
        selector, selection, result = self._selected(order)
        runner = SelectedConfiguredCognition(CONFIG, self.gateway, selector)
        mismatched = replace(result, model="different-model", response_model="different-model")
        with patch.object(runner._cognition, "invoke", return_value=mismatched):
            with self.assertRaisesRegex(SelectedConfiguredCognitionError, "differs from selection"):
                runner.invoke(selection, order=order, roster=ROSTER)
        self.assertEqual(runner._observed, {})

    def test_observation_recorder_failure_never_marks_execution_observed(self):
        order = self._order()
        selector, selection, result = self._selected(order)
        runner = SelectedConfiguredCognition(
            CONFIG,
            self.gateway,
            selector,
            observation_recorder=lambda **_: (_ for _ in ()).throw(RuntimeError("recorder down")),
        )
        with patch.object(runner._cognition, "invoke", return_value=result):
            with self.assertRaisesRegex(SelectedConfiguredCognitionError, "persistence failed"):
                runner.invoke(selection, order=order, roster=ROSTER)
        self.assertEqual(runner._observed, {})


if __name__ == "__main__":
    unittest.main()
