from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_openai_cognition import ConfiguredOpenAICognition
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
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}
ROSTER = [{"crew_id": "backend-engineer", "title": "Backend Engineer"}]


class FakeResponse:
    status = 200

    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self, limit: int) -> bytes:
        return self._payload


class FakeHTTPSConnection:
    response_payload = b"{}"
    request_call = None

    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.closed = False

    def request(self, method, path, body=None, headers=None):
        self.__class__.request_call = (method, path, body, dict(headers or {}))

    def getresponse(self):
        return FakeResponse(self.__class__.response_payload)

    def close(self):
        self.closed = True


class ConfiguredOpenAICognitionIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({ORIGIN}),
                max_response_bytes=65536,
            ),
            secret_broker=SecretBroker({ALIAS: "INTEGRATION-SECRET-SENTINEL"}),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource():
        return ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]

    def _order(self) -> MissionOrder:
        resource = self._resource()
        return MissionOrder.new(
            "MSN-configured-openai-cognition-integration",
            INTENT,
            "interpret configured cognition",
            MissionMode.inspect,
            "application-security-engineer",
            allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
            parameters={
                "operation": "configured_openai_cognition_invoke",
                "resource_id": resource["resource_id"],
                "provider_kind": "openai",
                "model": MODEL,
                "endpoint": ENDPOINT,
                "credential_alias": ALIAS,
                "allowed_origins": [ORIGIN],
                "secret_grants": [ALIAS],
            },
        ).seal()

    def test_discovery_to_governed_structured_cognition_preserves_fitness_and_selection_boundaries(self):
        interpretation = {
            "commander_intent": INTENT,
            "objective": "Inspect configured cognition",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": ["current runtime evidence"],
            "candidate_crew_ids": ["backend-engineer"],
            "options": [{
                "name": "bounded-inspection",
                "rationale": "Use only the authorized read path.",
                "advantages": ["bounded"],
                "risks": [],
                "crew_ids": ["backend-engineer"],
            }],
            "recommended_option": "bounded-inspection",
            "confidence": 0.88,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        }
        FakeHTTPSConnection.response_payload = json.dumps({
            "id": "resp_integration",
            "model": MODEL,
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": json.dumps(interpretation),
                }],
            }],
        }).encode()

        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            result = ConfiguredOpenAICognition(CONFIG, self.gateway).invoke(
                order=self._order(),
                roster=ROSTER,
            )

        evidence = result.evidence()
        self.assertEqual(result.interpretation.commander_intent, INTENT)
        self.assertEqual(result.interpretation.candidate_crew_ids, ["backend-engineer"])
        self.assertTrue(evidence["credential_use_authorized"])
        self.assertTrue(evidence["secret_materialized"])
        self.assertTrue(evidence["network_invoked"])
        self.assertTrue(evidence["cognition_invoked"])
        self.assertTrue(evidence["cognition_succeeded"])
        self.assertTrue(evidence["structured_interpretation_valid"])
        self.assertTrue(evidence["ready"])
        self.assertFalse(evidence["qualified_fit"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["mission_created"])
        self.assertFalse(evidence["authority_changed"])
        self.assertFalse(evidence["auto_selection"])
        method, path, body, headers = FakeHTTPSConnection.request_call
        self.assertEqual((method, path), ("POST", "/v1/responses"))
        self.assertNotIn("INTEGRATION-SECRET-SENTINEL", body.decode("utf-8"))
        self.assertEqual(headers["Authorization"], "Bearer INTEGRATION-SECRET-SENTINEL")


if __name__ == "__main__":
    unittest.main()
