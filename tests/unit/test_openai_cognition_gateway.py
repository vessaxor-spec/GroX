from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.contracts import MissionMode, MissionOrder
from grox.runtime_layout import VesselLayout
from grox.tools.gateway import ToolDenied
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


class TrackingSecretBroker(SecretBroker):
    def __init__(self, secrets=None):
        super().__init__(secrets)
        self.materialize_calls: list[dict[str, str]] = []

    def materialize_env(self, order, requested):
        self.materialize_calls.append(dict(requested or {}))
        return super().materialize_env(order, requested)


class FakeResponse:
    def __init__(self, status: int, payload: bytes):
        self.status = status
        self._payload = payload

    def read(self, limit: int) -> bytes:
        return self._payload


class FakeHTTPSConnection:
    response = FakeResponse(500, b"{}")
    instances: list["FakeHTTPSConnection"] = []

    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.request_call = None
        self.closed = False
        self.__class__.instances.append(self)

    def request(self, method, path, body=None, headers=None):
        self.request_call = (method, path, body, dict(headers or {}))

    def getresponse(self):
        return self.__class__.response

    def close(self):
        self.closed = True


class OpenAICognitionGatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        FakeHTTPSConnection.instances = []

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource() -> dict:
        return ConfiguredCognitionDiscovery(CONFIG).inventory()["resources"][0]

    def _gateway(self, secrets=None):
        broker = TrackingSecretBroker(secrets)
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({ORIGIN}),
                max_response_bytes=65536,
            ),
            secret_broker=broker,
        )
        return gateway, broker

    def _order(
        self,
        *,
        allowed_actions=("cognition_invoke", "net_fetch", "secret_use"),
        endpoint=ENDPOINT,
        secret_grants=(ALIAS,),
        seal=True,
    ) -> MissionOrder:
        resource = self._resource()
        order = MissionOrder.new(
            "MSN-openai-cognition",
            INTENT,
            "interpret configured cognition",
            MissionMode.inspect,
            "application-security-engineer",
            allowed_actions=allowed_actions,
            parameters={
                "operation": "configured_openai_cognition_invoke",
                "resource_id": resource["resource_id"],
                "provider_kind": "openai",
                "model": MODEL,
                "endpoint": endpoint,
                "credential_alias": ALIAS,
                "allowed_origins": [ORIGIN],
                "secret_grants": list(secret_grants),
            },
        )
        return order.seal() if seal else order

    @staticmethod
    def _valid_payload() -> bytes:
        interpretation = {
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
        }
        return json.dumps({
            "id": "resp_test",
            "model": MODEL,
            "provider_extra": "RAW-PROVIDER-SENTINEL",
            "output_text": json.dumps(interpretation),
        }).encode()

    def _invoke(self, gateway, order, **overrides):
        return gateway.openai_responses_cognition(
            order,
            resource_id=overrides.get("resource_id", self._resource()["resource_id"]),
            responses_endpoint=overrides.get("responses_endpoint", ENDPOINT),
            model=overrides.get("model", MODEL),
            credential_alias=overrides.get("credential_alias", ALIAS),
            directive=overrides.get("directive", INTENT),
            roster=overrides.get("roster", ROSTER),
        )

    def test_exact_sealed_cognition_posts_only_to_official_responses_and_hides_secret(self):
        secret = "OPENAI-COGNITION-SECRET-SENTINEL"
        FakeHTTPSConnection.response = FakeResponse(200, self._valid_payload())
        gateway, broker = self._gateway({ALIAS: secret})

        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            result = self._invoke(gateway, self._order())

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["response_id"], "resp_test")
        self.assertEqual(result["response_model"], MODEL)
        self.assertEqual(result["interpretation"].commander_intent, INTENT)
        self.assertTrue(result["cognition_invoked"])
        self.assertFalse(result["raw_response_returned"])
        self.assertNotIn("_payload", result)
        self.assertNotIn("RAW-PROVIDER-SENTINEL", repr(result))
        self.assertNotIn(secret, repr(result))
        self.assertEqual(
            broker.materialize_calls,
            [{"GROX_OPENAI_COGNITION_CREDENTIAL": ALIAS}],
        )
        self.assertEqual(len(FakeHTTPSConnection.instances), 1)
        conn = FakeHTTPSConnection.instances[0]
        method, path, body, headers = conn.request_call
        self.assertEqual((conn.host, conn.port), ("api.openai.com", 443))
        self.assertEqual(method, "POST")
        self.assertEqual(path, "/v1/responses")
        self.assertEqual(headers["Authorization"], f"Bearer {secret}")
        request_body = json.loads(body.decode("utf-8"))
        self.assertEqual(request_body["model"], MODEL)
        self.assertFalse(request_body["store"])
        self.assertNotIn("tools", request_body)
        self.assertIn(INTENT, request_body["input"])
        self.assertTrue(conn.closed)

    def test_missing_cognition_invoke_grant_fails_before_secret_or_network(self):
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        order = self._order(allowed_actions=("net_fetch", "secret_use"))
        with patch(
            "grox.tools.layout_gateway.http.client.HTTPSConnection",
            side_effect=AssertionError("missing cognition grant must fail before network"),
        ) as connection_mock:
            with self.assertRaisesRegex(ToolDenied, "cognition_invoke"):
                self._invoke(gateway, order)
        self.assertEqual(broker.materialize_calls, [])
        connection_mock.assert_not_called()

    def test_unsealed_order_fails_without_becoming_sealed(self):
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        order = self._order(seal=False)
        with self.assertRaisesRegex(ToolDenied, "already sealed"):
            self._invoke(gateway, order)
        self.assertFalse(order.sealed)
        self.assertEqual(broker.materialize_calls, [])

    def test_directive_mismatch_and_nonofficial_endpoint_fail_before_materialization(self):
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        with self.assertRaisesRegex(ToolDenied, "Commander intent mismatch"):
            self._invoke(gateway, self._order(), directive="different")
        self.assertEqual(broker.materialize_calls, [])

        with self.assertRaisesRegex(ToolDenied, "official Responses endpoint"):
            self._invoke(
                gateway,
                self._order(endpoint="https://compatible.example/v1/responses"),
                responses_endpoint="https://compatible.example/v1/responses",
            )
        self.assertEqual(broker.materialize_calls, [])

    def test_non_200_invalid_json_and_invalid_structure_are_sanitized_failures(self):
        gateway, _ = self._gateway({ALIAS: "SECRET-SENTINEL"})
        FakeHTTPSConnection.response = FakeResponse(
            429,
            b'{"error":{"message":"provider-secret-detail"}}',
        )
        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            with self.assertRaises(ToolDenied) as caught:
                self._invoke(gateway, self._order())
        self.assertIn("HTTP 429", str(caught.exception))
        self.assertNotIn("provider-secret-detail", str(caught.exception))

        FakeHTTPSConnection.response = FakeResponse(200, b"{not-json")
        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            with self.assertRaisesRegex(ToolDenied, "invalid JSON"):
                self._invoke(gateway, self._order())

        FakeHTTPSConnection.response = FakeResponse(
            200,
            json.dumps({"output_text": "{not-valid-structured-output"}).encode(),
        )
        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            with self.assertRaisesRegex(ToolDenied, "invalid structured interpretation"):
                self._invoke(gateway, self._order())


if __name__ == "__main__":
    unittest.main()
