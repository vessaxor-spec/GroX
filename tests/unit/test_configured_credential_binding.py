from __future__ import annotations

import unittest

from grox.credential_binding import ConfiguredCredentialBinding
from grox.cognition_discovery import ConfiguredCognitionDiscovery


OPENAI_CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": "remote-model-sentinel",
    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
    "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
}


class ConfiguredCredentialBindingTests(unittest.TestCase):
    def test_valid_remote_binding_preserves_exact_resource_identity(self):
        discovered = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]

        item = ConfiguredCredentialBinding(OPENAI_CONFIG).inventory()["resources"][0]

        self.assertEqual(item["resource_id"], discovered["resource_id"])
        self.assertEqual(item["provider_kind"], "openai")
        self.assertEqual(item["model"], "remote-model-sentinel")
        self.assertEqual(item["endpoint"], "https://api.openai.com/v1/responses")
        self.assertEqual(item["credential_alias"], "openai-primary")
        self.assertTrue(item["credential_binding_configured"])
        self.assertFalse(item["secret_alias_availability_checked"])
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
        self.assertFalse(item["authority_changed"])

    def test_absent_alias_fails_closed_without_guessing_default(self):
        config = dict(OPENAI_CONFIG)
        config.pop("GROX_REASONER_CREDENTIAL_ALIAS")

        result = ConfiguredCredentialBinding(config).inventory()

        self.assertEqual(result["status"], "unbound")
        self.assertEqual(result["resources"], [])
        self.assertNotIn("openai-api-key", repr(result))

    def test_malformed_alias_fails_closed(self):
        for alias in (" openai-primary", "openai primary", "openai-primary ", "x" * 129):
            with self.subTest(alias=alias):
                config = dict(OPENAI_CONFIG)
                config["GROX_REASONER_CREDENTIAL_ALIAS"] = alias
                result = ConfiguredCredentialBinding(config).inventory()
                self.assertEqual(result["status"], "invalid_binding")
                self.assertEqual(result["resources"], [])

    def test_local_resource_is_never_promoted_to_credential_bound_remote(self):
        config = {
            "GROX_REASONER_PROVIDER": "local-llama-cpp",
            "GROX_REASONER_MODEL": "local-model",
            "GROX_REASONER_CREDENTIAL_ALIAS": "should-not-bind",
        }
        result = ConfiguredCredentialBinding(config).inventory()
        self.assertEqual(result["status"], "not_applicable")
        self.assertEqual(result["resources"], [])

    def test_base_discovery_does_not_expose_credential_alias(self):
        item = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]
        self.assertNotIn("credential_alias", item)
        self.assertFalse(item["ready"])


if __name__ == "__main__":
    unittest.main()
