from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_openai_probe import (
    ConfiguredOpenAIAuthenticatedModelProbe,
    ConfiguredOpenAIAuthenticatedModelProbeError,
)
from grox.contracts import MissionMode, MissionOrder
from grox.runtime_layout import VesselLayout
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


class ConfiguredOpenAIAuthenticatedModelProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _gateway(self, secrets=None):
        broker = TrackingSecretBroker(secrets)
        gateway = LayoutToolGateway(
            VesselLayout.legacy(Path(self.tempdir.name)),
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({OFFICIAL_ORIGIN}),
            ),
            secret_broker=broker,
        )
        return gateway, broker

    @staticmethod
    def _resource(config=CONFIG):
        return ConfiguredCognitionDiscovery(config).inventory()["resources"][0]

    def _order(
        self,
        *,
        config=CONFIG,
        seal=True,
        resource_id=None,
        provider_kind="openai",
        model=MODEL,
        endpoint=OFFICIAL_ENDPOINT,
        credential_alias=ALIAS,
        operation="configured_openai_authenticated_model_probe",
        allowed_actions=("net_fetch", "secret_use"),
        allowed_origins=(OFFICIAL_ORIGIN,),
        secret_grants=(ALIAS,),
    ):
        resource = self._resource(config)
        order = MissionOrder.new(
            "MSN-configured-openai-probe",
            "probe exact configured OpenAI model visibility",
            "probe exact configured OpenAI model visibility",
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

    def test_exact_configured_identity_is_forwarded_to_gateway_and_later_states_remain_false(self):
        gateway, _ = self._gateway({ALIAS: "SECRET-SENTINEL"})
        service = ConfiguredOpenAIAuthenticatedModelProbe(CONFIG, gateway)
        expected = {
            "schema": "grox-openai-authenticated-model-probe-v1",
            "origin": OFFICIAL_ORIGIN,
            "status": 200,
            "classification": "authenticated_model_visible",
            "requested_model": MODEL,
            "model_identity": MODEL,
            "metadata_valid": True,
            "credential_alias": ALIAS,
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
        }
        order = self._order()
        with patch.object(gateway, "openai_model_probe", return_value=expected) as probe_mock:
            result = service.probe(order=order)

        resource = self._resource()
        probe_mock.assert_called_once_with(
            order,
            resource_id=resource["resource_id"],
            responses_endpoint=OFFICIAL_ENDPOINT,
            model=MODEL,
            credential_alias=ALIAS,
        )
        self.assertEqual(result["resource_id"], resource["resource_id"])
        self.assertTrue(result["credential_use_authorized"])
        self.assertFalse(result["ready"])
        self.assertFalse(result["qualified_fit"])
        self.assertFalse(result["selected"])
        self.assertFalse(result["observed"])
        self.assertFalse(result["mission_created"])
        self.assertFalse(result["auto_selection"])

    def test_wrong_resource_or_operation_fails_before_gateway_or_materialization(self):
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        service = ConfiguredOpenAIAuthenticatedModelProbe(CONFIG, gateway)
        cases = (
            self._order(resource_id="cognition:configured:openai:wrong"),
            self._order(operation="configured_cognition_remote_reasoner_activation"),
        )
        for order in cases:
            with self.subTest(parameters=order.parameters):
                with patch.object(
                    gateway,
                    "openai_model_probe",
                    side_effect=AssertionError("identity mismatch must fail before gateway probe"),
                ) as probe_mock:
                    with self.assertRaises(ConfiguredOpenAIAuthenticatedModelProbeError):
                        service.probe(order=order)
                probe_mock.assert_not_called()
        self.assertEqual(broker.materialize_calls, [])

    def test_non_official_configured_endpoint_fails_before_gateway_or_materialization(self):
        config = {
            **CONFIG,
            "GROX_REASONER_ENDPOINT": "https://compatible.example/v1/responses",
        }
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        service = ConfiguredOpenAIAuthenticatedModelProbe(config, gateway)
        order = self._order(
            config=config,
            endpoint="https://compatible.example/v1/responses",
            allowed_origins=("https://compatible.example",),
        )
        with patch.object(
            gateway,
            "openai_model_probe",
            side_effect=AssertionError("compatible endpoint must not reach credential-bearing gateway"),
        ) as probe_mock:
            with self.assertRaisesRegex(
                ConfiguredOpenAIAuthenticatedModelProbeError,
                "exact official Responses endpoint",
            ):
                service.probe(order=order)
        probe_mock.assert_not_called()
        self.assertEqual(broker.materialize_calls, [])

    def test_unsealed_order_fails_without_becoming_sealed(self):
        gateway, broker = self._gateway({ALIAS: "SECRET-SENTINEL"})
        service = ConfiguredOpenAIAuthenticatedModelProbe(CONFIG, gateway)
        order = self._order(seal=False)
        with patch.object(gateway, "openai_model_probe") as probe_mock:
            with self.assertRaisesRegex(
                ConfiguredOpenAIAuthenticatedModelProbeError,
                "already sealed",
            ):
                service.probe(order=order)
        self.assertFalse(order.sealed)
        self.assertEqual(broker.materialize_calls, [])
        probe_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
