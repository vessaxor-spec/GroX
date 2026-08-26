from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
)
from grox.contracts import MissionMode, MissionOrder
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"
ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
INTENT = "Inspect configured cognition safely"
ROSTER = [{"crew_id": "backend-engineer", "title": "Backend Engineer"}]
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}


class ConfiguredOpenAICognitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({ORIGIN}),
            ),
            secret_broker=SecretBroker({ALIAS: "SECRET-SENTINEL"}),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource(config=CONFIG):
        return ConfiguredCognitionDiscovery(config).inventory()["resources"][0]

    def _order(self, *, config=CONFIG, operation="configured_openai_cognition_invoke", seal=True):
        resource = self._resource(config)
        order = MissionOrder.new(
            "MSN-configured-openai-cognition",
            INTENT,
            "interpret configured cognition",
            MissionMode.inspect,
            "application-security-engineer",
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": operation,
                "resource_id": resource["resource_id"],
                "provider_kind": resource["provider_kind"],
                "model": resource["model"],
                "endpoint": resource["endpoint"],
                "credential_alias": ALIAS,
                "allowed_origins": [ORIGIN],
                "secret_grants": [ALIAS],
            },
        )
        return order.seal() if seal else order

    def test_exact_configured_identity_is_forwarded_and_later_states_remain_false(self):
        payload = {
            "id": "resp_test",
            "model": MODEL,
            "output_text": json.dumps({
                "commander_intent": INTENT,
                "objective": "Inspect configured cognition",
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
            }),
        }
        transport = {
            "schema": "grox-openai-responses-cognition-transport-v1",
            "status": 200,
            "response_id": "resp_test",
            "response_model": MODEL,
            "_payload": payload,
        }
        with patch.object(self.gateway, "openai_responses_cognition", return_value=transport) as invoke:
            result = ConfiguredOpenAICognition(CONFIG, self.gateway).invoke(
                order=self._order(),
                roster=ROSTER,
            )
        evidence = result.evidence()
        self.assertEqual(result.interpretation.commander_intent, INTENT)
        self.assertEqual(result.interpretation.recommended_option, "inspect")
        self.assertTrue(evidence["cognition_succeeded"])
        self.assertTrue(evidence["ready"])
        self.assertFalse(evidence["qualified_fit"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["authority_changed"])
        self.assertNotIn("_payload", repr(evidence))
        kwargs = invoke.call_args.kwargs
        self.assertEqual(kwargs["directive"], INTENT)
        self.assertEqual(kwargs["resource_id"], self._resource()["resource_id"])
        self.assertEqual(kwargs["credential_alias"], ALIAS)

    def test_nonofficial_configuration_fails_before_gateway(self):
        config = {
            **CONFIG,
            "GROX_REASONER_ENDPOINT": "https://compatible.example/v1/responses",
        }
        with patch.object(
            self.gateway,
            "openai_responses_cognition",
            side_effect=AssertionError("nonofficial config must fail before gateway"),
        ) as invoke:
            with self.assertRaisesRegex(ConfiguredOpenAICognitionError, "official Responses endpoint"):
                ConfiguredOpenAICognition(config, self.gateway).invoke(
                    order=self._order(config=config),
                    roster=ROSTER,
                )
        invoke.assert_not_called()

    def test_unsealed_or_wrong_operation_fails_before_gateway(self):
        cognition = ConfiguredOpenAICognition(CONFIG, self.gateway)
        with patch.object(self.gateway, "openai_responses_cognition") as invoke:
            with self.assertRaises(ConfiguredOpenAICognitionError):
                cognition.invoke(order=self._order(seal=False), roster=ROSTER)
            with self.assertRaisesRegex(ConfiguredOpenAICognitionError, "operation_mismatch"):
                cognition.invoke(
                    order=self._order(operation="configured_openai_authenticated_model_probe"),
                    roster=ROSTER,
                )
        invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
