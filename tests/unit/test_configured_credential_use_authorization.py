from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_credential_use_authorization import (
    ConfiguredCredentialUseAuthorization,
    ConfiguredCredentialUseAuthorizationError,
)
from grox.contracts import MissionMode, MissionOrder
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
        self.alias_checks: list[str] = []

    def has_alias(self, alias: str) -> bool:
        self.alias_checks.append(alias)
        return super().has_alias(alias)

    def materialize_env(self, order, requested):
        raise AssertionError("credential-use awareness must never materialize a secret")


class ConfiguredCredentialUseAuthorizationTests(unittest.TestCase):
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
        result = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()
        return result["resources"][0]

    def _order(
        self,
        *,
        seal: bool = True,
        allowed_actions=("secret_use",),
        operation="configured_cognition_credential_use_authorization",
        resource_id=None,
        provider_kind="openai",
        model="remote-model-sentinel",
        endpoint="https://api.openai.com/v1/responses",
        credential_alias="openai-primary",
        secret_grants=("openai-primary",),
    ) -> MissionOrder:
        resource = self._resource()
        order = MissionOrder.new(
            "MSN-credential-use-awareness",
            "inspect configured credential-use authorization",
            "inspect configured credential-use authorization",
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

    def test_exact_presealed_order_authorizes_only_credential_use_without_secret_or_later_state(self):
        exact_secret = "EXACT-CREDENTIAL-SECRET-SENTINEL"
        gateway, broker = self._gateway(
            {"openai-primary": exact_secret, "fallback-alias": "FALLBACK-SECRET-SENTINEL"}
        )
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
            order=self._order()
        )
        item = snapshot["resources"][0]

        self.assertEqual(snapshot["status"], "ok")
        self.assertEqual(snapshot["authorization_status"], "sealed_mission_order_authorized")
        self.assertTrue(snapshot["mission_context_present"])
        self.assertEqual(item["resource_id"], self._resource()["resource_id"])
        self.assertEqual(item["provider_kind"], "openai")
        self.assertEqual(item["model"], "remote-model-sentinel")
        self.assertEqual(item["endpoint"], "https://api.openai.com/v1/responses")
        self.assertEqual(item["credential_alias"], "openai-primary")
        self.assertTrue(item["credential_binding_configured"])
        self.assertTrue(item["credential_alias_available"])
        self.assertTrue(item["credential_use_authorized"])
        self.assertFalse(item["authorized"])
        self.assertFalse(item["ready"])
        self.assertFalse(item["qualified_fit"])
        self.assertFalse(item["selected"])
        self.assertFalse(item["observed"])
        self.assertFalse(item["secret_materialized"])
        self.assertFalse(item["credential_inspected"])
        self.assertFalse(item["credential_validated"])
        self.assertFalse(item["network_invoked"])
        self.assertFalse(item["provider_constructed"])
        self.assertFalse(item["cognition_invoked"])
        self.assertFalse(item["mission_created"])
        self.assertFalse(item["authority_changed"])
        self.assertFalse(item["auto_selection"])
        self.assertEqual(broker.alias_checks, ["openai-primary"])
        self.assertNotIn(exact_secret, repr(snapshot))
        self.assertNotIn("FALLBACK-SECRET-SENTINEL", repr(snapshot))

    def test_no_mission_context_never_authorizes_credential_use(self):
        gateway, _ = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory()
        item = snapshot["resources"][0]
        self.assertFalse(snapshot["mission_context_present"])
        self.assertEqual(snapshot["authorization_status"], "no_mission_context")
        self.assertFalse(item["credential_use_authorized"])
        self.assertFalse(item["authorized"])
        self.assertFalse(item["ready"])

    def test_unsealed_order_is_rejected_without_becoming_sealed(self):
        gateway, _ = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        order = self._order(seal=False)
        with self.assertRaises(ConfiguredCredentialUseAuthorizationError):
            ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(order=order)
        self.assertFalse(order.sealed)

    def test_exact_resource_provider_model_endpoint_alias_and_operation_binding_fail_closed(self):
        resource = self._resource()
        cases = (
            ("operation", {"operation": "wrong_operation"}, "operation_mismatch"),
            ("resource", {"resource_id": "cognition:configured:openai:wrong"}, "resource_mismatch"),
            ("provider", {"provider_kind": "other"}, "provider_mismatch"),
            ("model", {"model": "other-model"}, "model_mismatch"),
            ("endpoint", {"endpoint": "https://api.openai.com/v1/other"}, "endpoint_mismatch"),
            ("alias", {"credential_alias": "fallback-alias"}, "credential_alias_mismatch"),
        )
        for name, override, expected in cases:
            with self.subTest(name=name):
                gateway, _ = self._gateway(
                    {"openai-primary": "SECRET-SENTINEL", "fallback-alias": "OTHER-SENTINEL"}
                )
                kwargs = {
                    "resource_id": resource["resource_id"],
                    "provider_kind": "openai",
                    "model": "remote-model-sentinel",
                    "endpoint": "https://api.openai.com/v1/responses",
                    "credential_alias": "openai-primary",
                    "operation": "configured_cognition_credential_use_authorization",
                }
                kwargs.update(override)
                snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
                    order=self._order(**kwargs)
                )
                item = snapshot["resources"][0]
                self.assertEqual(snapshot["authorization_status"], expected)
                self.assertFalse(item["credential_use_authorized"])
                self.assertFalse(item["authorized"])
                self.assertFalse(item["ready"])

    def test_other_granted_alias_never_authorizes_exact_configured_alias(self):
        gateway, _ = self._gateway(
            {"openai-primary": "EXACT-SECRET-SENTINEL", "fallback-alias": "FALLBACK-SECRET-SENTINEL"}
        )
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
            order=self._order(secret_grants=("fallback-alias",))
        )
        item = snapshot["resources"][0]
        self.assertEqual(snapshot["authorization_status"], "credential_alias_not_granted")
        self.assertTrue(item["credential_alias_available"])
        self.assertFalse(item["credential_use_authorized"])

    def test_secret_use_action_is_required_even_when_exact_alias_is_granted(self):
        gateway, _ = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
            order=self._order(allowed_actions=(), secret_grants=("openai-primary",))
        )
        self.assertEqual(snapshot["authorization_status"], "denied_by_gateway_contract")
        self.assertFalse(snapshot["resources"][0]["credential_use_authorized"])

    def test_unavailable_exact_alias_never_authorizes_even_with_exact_order(self):
        gateway, broker = self._gateway({"fallback-alias": "FALLBACK-SECRET-SENTINEL"})
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(
            order=self._order(secret_grants=("openai-primary",))
        )
        item = snapshot["resources"][0]
        self.assertEqual(snapshot["authorization_status"], "credential_alias_unavailable")
        self.assertFalse(item["credential_alias_available"])
        self.assertFalse(item["credential_use_authorized"])
        self.assertEqual(broker.alias_checks, ["openai-primary"])

    def test_invalid_secret_grants_fail_closed(self):
        gateway, _ = self._gateway({"openai-primary": "SECRET-SENTINEL"})
        order = self._order(secret_grants=None)
        snapshot = ConfiguredCredentialUseAuthorization(OPENAI_CONFIG, gateway).inventory(order=order)
        self.assertEqual(snapshot["authorization_status"], "invalid_secret_grants")
        self.assertFalse(snapshot["resources"][0]["credential_use_authorized"])

    def test_unbound_invalid_and_local_bindings_are_not_promoted(self):
        cases = []
        unbound = dict(OPENAI_CONFIG)
        unbound.pop("GROX_REASONER_CREDENTIAL_ALIAS")
        cases.append(unbound)

        invalid = dict(OPENAI_CONFIG)
        invalid["GROX_REASONER_CREDENTIAL_ALIAS"] = " invalid alias "
        cases.append(invalid)

        local = {
            "GROX_REASONER_PROVIDER": "local-llama-cpp",
            "GROX_REASONER_MODEL": "local-model",
            "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
        }
        cases.append(local)

        for config in cases:
            with self.subTest(config=config):
                gateway, broker = self._gateway({"openai-primary": "SECRET-SENTINEL"})
                snapshot = ConfiguredCredentialUseAuthorization(config, gateway).inventory(
                    order=self._order()
                )
                self.assertEqual(snapshot["resources"], [])
                self.assertEqual(snapshot["authorization_status"], "not_applicable")
                self.assertEqual(broker.alias_checks, [])
                self.assertFalse(snapshot["credential_validated"])
                self.assertFalse(snapshot["network_invoked"])


if __name__ == "__main__":
    unittest.main()
