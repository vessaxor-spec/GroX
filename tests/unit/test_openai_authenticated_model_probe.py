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


OFFICIAL_ENDPOINT = "https://api.openai.com/v1/responses"
OFFICIAL_ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": OFFICIAL_ENDPOINT,
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

    def request(self, method, path, headers=None):
        self.request_call = (method, path, dict(headers or {}))

    def getresponse(self):
        return self.__class__.response

    def close(self):
        self.closed = True


class OpenAIAuthenticatedModelProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        FakeHTTPSConnection.instances = []

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _resource(config=CONFIG) -> dict:
        return ConfiguredCognitionDiscovery(config).inventory()["resources"][0]

    def _gateway(self, *, secrets=None, allowed_origins=(OFFICIAL_ORIGIN,)):
        broker = TrackingSecretBroker(secrets)
        policy = GatewayPolicy(
            network_enabled=True,
            allowed_origins=frozenset(allowed_origins),
            max_response_bytes=4096,
        )
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=policy,
            secret_broker=broker,
        )
        return gateway, broker

    def _order(
        self,
        *,
        seal=True,
        endpoint=OFFICIAL_ENDPOINT,
        resource_id=None,
        provider_kind="openai",
        model=MODEL,
        credential_alias=ALIAS,
        allowed_actions=("net_fetch", "secret_use"),
        allowed_origins=(OFFICIAL_ORIGIN,),
        secret_grants=(ALIAS,),
        operation="configured_openai_authenticated_model_probe",
    ) -> MissionOrder:
        resource = self._resource(
            {
                **CONFIG,
                "GROX_REASONER_ENDPOINT": endpoint,
                "GROX_REASONER_MODEL": model,
            }
        )
        order = MissionOrder.new(
            "MSN-openai-model-probe",
            "probe configured OpenAI model visibility",
            "probe configured OpenAI model visibility",
            MissionMode.inspect,
            "application-security-engineer",
            allowed_actions=allowed_actions,
            parameters={
                "operation": operation,
                "resource_id": resource["resource_id"] if resource_id is None else resource_id,
                "provider_kind": provider_kind,
                "model": model,
                "endpoint": endpoint,
                "credential_alias": credential_alias,
                "allowed_origins": list(allowed_origins),
                "secret_grants": list(secret_grants),
            },
        )
        return order.seal() if seal else order

    def _probe(self, gateway, order, *, endpoint=OFFICIAL_ENDPOINT, model=MODEL, alias=ALIAS):
        return gateway.openai_model_probe(
            order,
            resource_id=order.parameters["resource_id"],
            responses_endpoint=endpoint,
            model=model,
            credential_alias=alias,
        )

    def test_exact_official_200_proves_authenticated_model_visibility_without_secret_or_body_exposure(self):
        secret = "OPENAI-PROBE-SECRET-SENTINEL"
        FakeHTTPSConnection.response = FakeResponse(
            200,
            json.dumps({"id": MODEL, "object": "model", "owned_by": "openai"}).encode(),
        )
        gateway, broker = self._gateway(secrets={ALIAS: secret})
        order = self._order()

        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            result = self._probe(gateway, order)

        self.assertEqual(result["classification"], "authenticated_model_visible")
        self.assertTrue(result["credential_accepted_for_model_visibility"])
        self.assertFalse(result["credential_rejected"])
        self.assertEqual(result["model_identity"], MODEL)
        self.assertTrue(result["metadata_valid"])
        self.assertTrue(result["secret_materialized"])
        self.assertTrue(result["network_invoked"])
        self.assertFalse(result["response_body_returned"])
        self.assertFalse(result["cognition_invoked"])
        self.assertFalse(result["ready"])
        self.assertFalse(result["qualified_fit"])
        self.assertFalse(result["selected"])
        self.assertFalse(result["authority_changed"])
        self.assertNotIn(secret, repr(result))
        self.assertNotIn("owned_by", repr(result))
        self.assertEqual(
            broker.materialize_calls,
            [{"GROX_OPENAI_PROBE_CREDENTIAL": ALIAS}],
        )
        self.assertEqual(len(FakeHTTPSConnection.instances), 1)
        conn = FakeHTTPSConnection.instances[0]
        self.assertEqual((conn.host, conn.port), ("api.openai.com", 443))
        method, path, headers = conn.request_call
        self.assertEqual(method, "GET")
        self.assertEqual(path, f"/v1/models/{MODEL}")
        self.assertEqual(headers["Authorization"], f"Bearer {secret}")
        self.assertTrue(conn.closed)

    def test_401_records_rejection_without_manufacturing_visibility_or_readiness(self):
        FakeHTTPSConnection.response = FakeResponse(401, b'{"error":{"message":"invalid"}}')
        gateway, _ = self._gateway(secrets={ALIAS: "REJECTED-SENTINEL"})
        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            result = self._probe(gateway, self._order())
        self.assertEqual(result["classification"], "credential_rejected")
        self.assertTrue(result["credential_rejected"])
        self.assertFalse(result["credential_accepted_for_model_visibility"])
        self.assertIsNone(result["model_identity"])
        self.assertFalse(result["ready"])

    def test_200_with_wrong_model_identity_is_indeterminate(self):
        FakeHTTPSConnection.response = FakeResponse(
            200,
            json.dumps({"id": "different-model", "object": "model"}).encode(),
        )
        gateway, _ = self._gateway(secrets={ALIAS: "SECRET-SENTINEL"})
        with patch("grox.tools.layout_gateway.http.client.HTTPSConnection", FakeHTTPSConnection):
            result = self._probe(gateway, self._order())
        self.assertEqual(result["classification"], "indeterminate")
        self.assertFalse(result["metadata_valid"])
        self.assertFalse(result["credential_accepted_for_model_visibility"])
        self.assertIsNone(result["model_identity"])

    def test_non_official_configured_endpoint_never_receives_credential(self):
        endpoint = "https://compatible.example/v1/responses"
        gateway, broker = self._gateway(
            secrets={ALIAS: "DO-NOT-EXFILTRATE-SENTINEL"},
            allowed_origins=(OFFICIAL_ORIGIN, "https://compatible.example"),
        )
        order = self._order(
            endpoint=endpoint,
            allowed_origins=("https://compatible.example",),
        )
        with patch(
            "grox.tools.layout_gateway.http.client.HTTPSConnection",
            side_effect=AssertionError("non-official endpoint must fail before network"),
        ) as connection_mock:
            with self.assertRaisesRegex(ToolDenied, "exact official Responses endpoint"):
                self._probe(gateway, order, endpoint=endpoint)
        self.assertEqual(broker.materialize_calls, [])
        connection_mock.assert_not_called()

    def test_unsealed_order_fails_without_becoming_sealed_or_touching_secret_or_network(self):
        gateway, broker = self._gateway(secrets={ALIAS: "SECRET-SENTINEL"})
        order = self._order(seal=False)
        with patch(
            "grox.tools.layout_gateway.http.client.HTTPSConnection",
            side_effect=AssertionError("unsealed Order must fail before network"),
        ) as connection_mock:
            with self.assertRaisesRegex(ToolDenied, "already sealed"):
                self._probe(gateway, order)
        self.assertFalse(order.sealed)
        self.assertEqual(broker.materialize_calls, [])
        connection_mock.assert_not_called()

    def test_exact_identity_actions_origin_and_alias_grant_are_required(self):
        cases = (
            {"order_kwargs": {"operation": "other-operation"}, "message": "identity mismatch"},
            {"order_kwargs": {"resource_id": "cognition:configured:openai:wrong"}, "message": "identity mismatch"},
            {"order_kwargs": {"provider_kind": "other"}, "message": "identity mismatch"},
            {"order_kwargs": {"credential_alias": "other-alias"}, "message": "identity mismatch"},
            {"order_kwargs": {"allowed_actions": ("secret_use",)}, "message": "net_fetch"},
            {"order_kwargs": {"allowed_actions": ("net_fetch",)}, "message": "secret_use"},
            {"order_kwargs": {"allowed_origins": ()}, "message": "origin not granted"},
        )
        for case in cases:
            with self.subTest(case=case):
                gateway, broker = self._gateway(
                    secrets={ALIAS: "SECRET-SENTINEL", "other-alias": "OTHER-SENTINEL"}
                )
                order = self._order(**case["order_kwargs"])
                with patch(
                    "grox.tools.layout_gateway.http.client.HTTPSConnection",
                    side_effect=AssertionError("failed authority must not invoke network"),
                ):
                    with self.assertRaisesRegex(ToolDenied, case["message"]):
                        self._probe(gateway, order)
                self.assertEqual(broker.materialize_calls, [])

        gateway, broker = self._gateway(secrets={ALIAS: "SECRET-SENTINEL"})
        order = self._order(secret_grants=("other-alias",))
        with patch(
            "grox.tools.layout_gateway.http.client.HTTPSConnection",
            side_effect=AssertionError("denied alias grant must not invoke network"),
        ):
            with self.assertRaisesRegex(ToolDenied, "credential materialization denied"):
                self._probe(gateway, order)
        self.assertEqual(
            broker.materialize_calls,
            [{"GROX_OPENAI_PROBE_CREDENTIAL": ALIAS}],
        )


if __name__ == "__main__":
    unittest.main()
