from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_remote_reasoner import (
    ConfiguredRemoteReasonerActivation,
    ConfiguredRemoteReasonerActivationError,
)
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.gateway import ToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


OPENAI_CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": "remote-model-sentinel",
    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
    "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
}


class TrackingSecretBroker(SecretBroker):
    def __init__(self, secrets=None):
        super().__init__(secrets)
        self.materialize_calls: list[dict[str, str]] = []

    def materialize_env(self, order, requested):
        self.materialize_calls.append(dict(requested or {}))
        return super().materialize_env(order, requested)


class ConfiguredRemoteReasonerActivationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _gateway(self, secrets=None) -> tuple[ToolGateway, TrackingSecretBroker]:
        broker = TrackingSecretBroker(secrets)
        gateway = ToolGateway(
            Path(self.tempdir.name),
            policy=GatewayPolicy(),
            secret_broker=broker,
        )
        return gateway, broker

    @staticmethod
    def _resource() -> dict:
        return ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]

    def _order(
        self,
        *,
        seal: bool = True,
        operation: str = "configured_cognition_remote_reasoner_activation",
        resource_id: str | None = None,
        provider_kind: str = "openai",
        model: str = "remote-model-sentinel",
        endpoint: str = "https://api.openai.com/v1/responses",
        credential_alias: str = "openai-primary",
        allowed_actions=("secret_use",),
        secret_grants=("openai-primary",),
    ) -> MissionOrder:
        resource = self._resource()
        order = MissionOrder.new(
            "MSN-configured-remote-reasoner",
            "activate configured remote reasoner",
            "activate configured remote reasoner",
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
                "secret_grants": list(secret_grants) if secret_grants is not None else None,
            },
        )
        return order.seal() if seal else order

    def test_exact_authorized_activation_constructs_provider_without_network_or_secret_exposure(self):
        secret = "EXACT-CONFIGURED-CREDENTIAL-SENTINEL"
        gateway, broker = self._gateway({"openai-primary": secret})
        activation = ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway)

        with patch(
            "grox.reasoning.openai_responses.urlopen",
            side_effect=AssertionError("activation must not invoke network"),
        ) as urlopen_mock:
            handle = activation.activate(order=self._order())

        evidence = handle.evidence()
        self.assertEqual(handle.resource_id, self._resource()["resource_id"])
        self.assertEqual(handle.provider_kind, "openai")
        self.assertEqual(handle.model, "remote-model-sentinel")
        self.assertEqual(handle.endpoint, "https://api.openai.com/v1/responses")
        self.assertEqual(handle.credential_alias, "openai-primary")
        self.assertFalse(hasattr(handle, "provider"))
        self.assertTrue(evidence["credential_use_authorized"])
        self.assertTrue(evidence["secret_materialized"])
        self.assertTrue(evidence["provider_constructed"])
        self.assertFalse(evidence["credential_validated"])
        self.assertFalse(evidence["network_invoked"])
        self.assertFalse(evidence["cognition_invoked"])
        self.assertFalse(evidence["ready"])
        self.assertFalse(evidence["qualified_fit"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["mission_created"])
        self.assertFalse(evidence["authority_changed"])
        self.assertFalse(evidence["auto_selection"])
        self.assertEqual(
            broker.materialize_calls,
            [{"GROX_CONFIGURED_COGNITION_CREDENTIAL": "openai-primary"}],
        )
        self.assertNotIn(secret, repr(handle))
        self.assertNotIn(secret, repr(evidence))
        urlopen_mock.assert_not_called()

    def test_openai_provider_does_not_expose_public_api_key_attribute(self):
        provider = OpenAIResponsesProvider(
            api_key="PRIVATE-PROVIDER-CREDENTIAL-SENTINEL",
            model="remote-model-sentinel",
            endpoint="https://api.openai.com/v1/responses",
        )
        self.assertFalse(hasattr(provider, "api_key"))
        self.assertNotIn("PRIVATE-PROVIDER-CREDENTIAL-SENTINEL", repr(provider))

    def test_authorization_awareness_operation_cannot_materialize_or_construct_provider(self):
        gateway, broker = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        activation = ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway)
        with self.assertRaisesRegex(ConfiguredRemoteReasonerActivationError, "operation_mismatch"):
            activation.activate(
                order=self._order(operation="configured_cognition_credential_use_authorization")
            )
        self.assertEqual(broker.materialize_calls, [])

    def test_unsealed_order_fails_before_materialization(self):
        gateway, broker = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        order = self._order(seal=False)
        with self.assertRaises(ConfiguredRemoteReasonerActivationError):
            ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(order=order)
        self.assertFalse(order.sealed)
        self.assertEqual(broker.materialize_calls, [])

    def test_exact_resource_provider_model_endpoint_and_alias_binding_fail_before_materialization(self):
        cases = (
            {"resource_id": "cognition:configured:openai:wrong"},
            {"provider_kind": "other"},
            {"model": "other-model"},
            {"endpoint": "https://api.openai.com/v1/other"},
            {"credential_alias": "fallback-alias"},
        )
        for override in cases:
            with self.subTest(override=override):
                gateway, broker = self._gateway(
                    {"openai-primary": "SECRET-SENTINEL", "fallback-alias": "OTHER-SENTINEL"}
                )
                with self.assertRaises(ConfiguredRemoteReasonerActivationError):
                    ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(
                        order=self._order(**override)
                    )
                self.assertEqual(broker.materialize_calls, [])

    def test_secret_use_action_and_exact_alias_grant_are_required_before_materialization(self):
        cases = (
            {"allowed_actions": (), "secret_grants": ("openai-primary",)},
            {"allowed_actions": ("secret_use",), "secret_grants": ("fallback-alias",)},
            {"allowed_actions": ("secret_use",), "secret_grants": None},
        )
        for override in cases:
            with self.subTest(override=override):
                gateway, broker = self._gateway(
                    {"openai-primary": "SECRET-SENTINEL", "fallback-alias": "OTHER-SENTINEL"}
                )
                with self.assertRaises(ConfiguredRemoteReasonerActivationError):
                    ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(
                        order=self._order(**override)
                    )
                self.assertEqual(broker.materialize_calls, [])

    def test_unavailable_alias_fails_before_materialization(self):
        gateway, broker = self._gateway({"fallback-alias": "OTHER-SENTINEL"})
        with self.assertRaises(ConfiguredRemoteReasonerActivationError):
            ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(order=self._order())
        self.assertEqual(broker.materialize_calls, [])

    def test_empty_materialized_value_fails_closed_without_readiness_claim(self):
        gateway, broker = self._gateway({"openai-primary": ""})
        with self.assertRaisesRegex(ConfiguredRemoteReasonerActivationError, "no usable value"):
            ConfiguredRemoteReasonerActivation(OPENAI_CONFIG, gateway).activate(order=self._order())
        self.assertEqual(len(broker.materialize_calls), 1)


if __name__ == "__main__":
    unittest.main()
