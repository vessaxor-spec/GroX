from __future__ import annotations

import unittest

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_credential_availability import ConfiguredCredentialAliasAvailability
from grox.credential_binding import ConfiguredCredentialBinding
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
        raise AssertionError("credential availability awareness must never materialize a secret")


class ConfiguredCredentialAliasAvailabilityTests(unittest.TestCase):
    def test_exact_configured_alias_availability_preserves_resource_identity_without_secret_access(self):
        exact_secret = "EXACT-CREDENTIAL-SECRET-SENTINEL"
        unrelated_secret = "UNRELATED-CREDENTIAL-SECRET-SENTINEL"
        broker = TrackingSecretBroker(
            {
                "openai-primary": exact_secret,
                "unrelated-alias": unrelated_secret,
            }
        )
        discovered = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]
        bound = ConfiguredCredentialBinding(OPENAI_CONFIG).inventory()["resources"][0]

        result = ConfiguredCredentialAliasAvailability(OPENAI_CONFIG, broker).inventory()
        item = result["resources"][0]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(item["resource_id"], discovered["resource_id"])
        self.assertEqual(item["resource_id"], bound["resource_id"])
        self.assertEqual(item["provider_kind"], "openai")
        self.assertEqual(item["model"], "remote-model-sentinel")
        self.assertEqual(item["endpoint"], "https://api.openai.com/v1/responses")
        self.assertEqual(item["credential_alias"], "openai-primary")
        self.assertTrue(item["credential_binding_configured"])
        self.assertTrue(item["credential_alias_available"])
        self.assertTrue(item["secret_broker_consulted"])
        self.assertTrue(item["secret_alias_availability_checked"])
        self.assertFalse(item["secret_materialized"])
        self.assertFalse(item["credential_inspected"])
        self.assertFalse(item["credential_validated"])
        self.assertFalse(item["authorized"])
        self.assertFalse(item["ready"])
        self.assertFalse(item["qualified_fit"])
        self.assertFalse(item["selected"])
        self.assertFalse(item["observed"])
        self.assertFalse(item["network_invoked"])
        self.assertFalse(item["provider_constructed"])
        self.assertFalse(item["cognition_invoked"])
        self.assertFalse(item["mission_created"])
        self.assertFalse(item["authority_changed"])
        self.assertFalse(item["auto_selection"])
        self.assertEqual(broker.alias_checks, ["openai-primary"])
        self.assertNotIn(exact_secret, repr(result))
        self.assertNotIn(unrelated_secret, repr(result))

    def test_other_broker_alias_never_satisfies_missing_exact_configured_alias(self):
        broker = TrackingSecretBroker({"fallback-alias": "FALLBACK-SECRET-SENTINEL"})

        result = ConfiguredCredentialAliasAvailability(OPENAI_CONFIG, broker).inventory()
        item = result["resources"][0]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(item["credential_alias"], "openai-primary")
        self.assertFalse(item["credential_alias_available"])
        self.assertEqual(broker.alias_checks, ["openai-primary"])
        self.assertFalse(item["ready"])
        self.assertFalse(item["credential_validated"])
        self.assertNotIn("FALLBACK-SECRET-SENTINEL", repr(result))

    def test_unbound_invalid_and_local_bindings_do_not_consult_broker(self):
        cases = []

        unbound = dict(OPENAI_CONFIG)
        unbound.pop("GROX_REASONER_CREDENTIAL_ALIAS")
        cases.append((unbound, "unbound"))

        invalid = dict(OPENAI_CONFIG)
        invalid["GROX_REASONER_CREDENTIAL_ALIAS"] = " invalid alias "
        cases.append((invalid, "invalid_binding"))

        local = {
            "GROX_REASONER_PROVIDER": "local-llama-cpp",
            "GROX_REASONER_MODEL": "local-model",
            "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
        }
        cases.append((local, "not_applicable"))

        for config, expected_status in cases:
            with self.subTest(expected_status=expected_status):
                broker = TrackingSecretBroker({"openai-primary": "SECRET-SENTINEL"})
                result = ConfiguredCredentialAliasAvailability(config, broker).inventory()
                self.assertEqual(result["status"], expected_status)
                self.assertEqual(result["resources"], [])
                self.assertEqual(broker.alias_checks, [])
                self.assertFalse(result["secret_broker_consulted"])
                self.assertFalse(result["secret_alias_availability_checked"])
                self.assertFalse(result["credential_validated"])
                self.assertFalse(result["network_invoked"])


if __name__ == "__main__":
    unittest.main()
