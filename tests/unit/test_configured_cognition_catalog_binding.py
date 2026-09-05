from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from grox.configured_cognition_catalog_binding import (
    ConfiguredCognitionCatalogBinding,
    ConfiguredCognitionCatalogBindingError,
)
from grox.credential_binding import ConfiguredCredentialBinding


ENDPOINT = "https://api.openai.com/v1/responses"


class ConfiguredCognitionCatalogBindingTests(unittest.TestCase):
    @staticmethod
    def _catalog(entries):
        return {"GROX_REASONER_CATALOG_JSON": json.dumps(entries)}

    def test_mixed_catalog_preserves_order_and_exact_remote_alias_binding(self):
        result = ConfiguredCognitionCatalogBinding(
            self._catalog([
                {
                    "provider_kind": "openai",
                    "model": "model-a",
                    "endpoint": ENDPOINT,
                    "credential_alias": "alias-a",
                },
                {
                    "provider_kind": "local-llama-cpp",
                    "model": "local-b",
                },
                {
                    "provider_kind": "openai",
                    "model": "model-c",
                    "endpoint": ENDPOINT,
                    "credential_alias": "alias-c",
                },
            ])
        ).inventory()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["configuration_source"], "explicit_catalog")
        self.assertEqual(result["remote_resource_count"], 2)
        self.assertEqual(result["bound_remote_resource_count"], 2)
        self.assertEqual(
            [item["model"] for item in result["resources"]],
            ["model-a", "local-b", "model-c"],
        )
        self.assertEqual(result["resources"][0]["credential_alias"], "alias-a")
        self.assertEqual(result["resources"][0]["credential_binding_status"], "ok")
        self.assertTrue(result["resources"][0]["credential_binding_configured"])
        self.assertEqual(result["resources"][1]["credential_binding_status"], "not_applicable")
        self.assertNotIn("credential_alias", result["resources"][1])
        self.assertEqual(result["resources"][2]["credential_alias"], "alias-c")
        for item in result["resources"]:
            self.assertFalse(item["authorized"])
            self.assertFalse(item["ready"])
            self.assertFalse(item["qualified_fit"])
            self.assertFalse(item["selected"])
            self.assertFalse(item["observed"])
        self.assertFalse(result["secret_broker_consulted"])
        self.assertFalse(result["secret_alias_availability_checked"])
        self.assertFalse(result["network_invoked"])
        self.assertFalse(result["provider_constructed"])
        self.assertFalse(result["cognition_invoked"])
        self.assertFalse(result["routing_enabled"])
        self.assertFalse(result["authority_changed"])

    def test_missing_remote_alias_is_retained_as_unbound_instead_of_disappearing(self):
        result = ConfiguredCognitionCatalogBinding(
            self._catalog([
                {
                    "provider_kind": "openai",
                    "model": "model-a",
                    "endpoint": ENDPOINT,
                    "credential_alias": "alias-a",
                },
                {
                    "provider_kind": "openai",
                    "model": "model-b",
                    "endpoint": ENDPOINT,
                },
            ])
        ).inventory()

        self.assertEqual(result["status"], "incomplete_binding")
        self.assertEqual(result["remote_resource_count"], 2)
        self.assertEqual(result["bound_remote_resource_count"], 1)
        self.assertEqual(len(result["resources"]), 2)
        self.assertEqual(result["resources"][1]["model"], "model-b")
        self.assertEqual(result["resources"][1]["credential_binding_status"], "unbound")
        self.assertFalse(result["resources"][1]["credential_binding_configured"])
        self.assertNotIn("credential_alias", result["resources"][1])

    def test_malformed_catalog_propagates_fail_closed_without_partial_bindings(self):
        result = ConfiguredCognitionCatalogBinding(
            {"GROX_REASONER_CATALOG_JSON": "{not-json"}
        ).inventory()

        self.assertEqual(result["status"], "invalid_catalog")
        self.assertEqual(result["resources"], [])
        self.assertEqual(result["remote_resource_count"], 0)
        self.assertEqual(result["bound_remote_resource_count"], 0)

    def test_legacy_single_resource_remains_supported_without_changing_legacy_binder(self):
        config = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "legacy-model",
            "GROX_REASONER_ENDPOINT": ENDPOINT,
            "GROX_REASONER_CREDENTIAL_ALIAS": "legacy-alias",
        }

        catalog = ConfiguredCognitionCatalogBinding(config).inventory()
        legacy = ConfiguredCredentialBinding(config).inventory()

        self.assertEqual(catalog["status"], "ok")
        self.assertEqual(catalog["configuration_source"], "legacy_single")
        self.assertEqual(catalog["resources"][0]["resource_id"], legacy["resources"][0]["resource_id"])
        self.assertEqual(catalog["resources"][0]["credential_alias"], "legacy-alias")

    def test_binding_identity_mismatch_fails_closed(self):
        config = self._catalog([
            {
                "provider_kind": "openai",
                "model": "model-a",
                "endpoint": ENDPOINT,
                "credential_alias": "alias-a",
            }
        ])
        forged = {
            "status": "ok",
            "resources": [{
                "resource_id": "cognition:configured:openai:forged",
                "provider_kind": "openai",
                "model": "model-a",
                "endpoint": ENDPOINT,
                "credential_alias": "alias-a",
            }],
        }

        with patch.object(ConfiguredCredentialBinding, "inventory", return_value=forged):
            with self.assertRaisesRegex(ConfiguredCognitionCatalogBindingError, "identity differs"):
                ConfiguredCognitionCatalogBinding(config).inventory()


if __name__ == "__main__":
    unittest.main()
