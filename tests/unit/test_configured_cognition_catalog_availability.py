from __future__ import annotations

import json
import unittest

from grox.configured_cognition_catalog_availability import (
    ConfiguredCognitionCatalogCredentialAvailability,
)
from grox.configured_cognition_catalog_binding import ConfiguredCognitionCatalogBinding
from grox.configured_credential_availability import ConfiguredCredentialAliasAvailability
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"


class TrackingSecretBroker(SecretBroker):
    def __init__(self, secrets=None):
        super().__init__(secrets)
        self.alias_checks: list[str] = []

    def has_alias(self, alias: str) -> bool:
        self.alias_checks.append(alias)
        return super().has_alias(alias)

    def materialize_env(self, order, requested):
        raise AssertionError(
            "catalog credential availability must never materialize a secret"
        )


class ConfiguredCognitionCatalogCredentialAvailabilityTests(unittest.TestCase):
    @staticmethod
    def _catalog(entries):
        return {"GROX_REASONER_CATALOG_JSON": json.dumps(entries)}

    def test_mixed_catalog_preserves_exact_identity_order_and_alias_membership(self):
        broker = TrackingSecretBroker(
            {
                "alias-a": "SECRET-A-SENTINEL",
                "unrelated": "UNRELATED-SECRET-SENTINEL",
            }
        )
        config = self._catalog(
            [
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
                {
                    "provider_kind": "openai",
                    "model": "model-d",
                    "endpoint": ENDPOINT,
                },
            ]
        )

        binding = ConfiguredCognitionCatalogBinding(config).inventory()
        result = ConfiguredCognitionCatalogCredentialAvailability(config, broker).inventory()

        self.assertEqual(result["status"], "incomplete_binding")
        self.assertEqual(result["configuration_source"], "explicit_catalog")
        self.assertEqual(result["remote_resource_count"], 3)
        self.assertEqual(result["bound_remote_resource_count"], 2)
        self.assertEqual(result["available_remote_resource_count"], 1)
        self.assertEqual(
            [item["model"] for item in result["resources"]],
            ["model-a", "local-b", "model-c", "model-d"],
        )
        self.assertEqual(
            [item["resource_id"] for item in result["resources"]],
            [item["resource_id"] for item in binding["resources"]],
        )

        first, local, third, unbound = result["resources"]
        self.assertEqual(first["credential_alias"], "alias-a")
        self.assertTrue(first["credential_alias_available"])
        self.assertEqual(first["credential_alias_availability_status"], "available")

        self.assertEqual(local["credential_binding_status"], "not_applicable")
        self.assertEqual(local["credential_alias_availability_status"], "not_applicable")
        self.assertIsNone(local["credential_alias_available"])
        self.assertNotIn("credential_alias", local)

        self.assertEqual(third["credential_alias"], "alias-c")
        self.assertFalse(third["credential_alias_available"])
        self.assertEqual(third["credential_alias_availability_status"], "unavailable")

        self.assertEqual(unbound["credential_binding_status"], "unbound")
        self.assertEqual(unbound["credential_alias_availability_status"], "unbound")
        self.assertFalse(unbound["credential_alias_available"])
        self.assertNotIn("credential_alias", unbound)

        self.assertEqual(broker.alias_checks, ["alias-a", "alias-c"])
        self.assertTrue(result["secret_broker_consulted"])
        self.assertTrue(result["secret_alias_availability_checked"])
        self.assertFalse(result["secret_materialized"])
        self.assertFalse(result["credential_inspected"])
        self.assertFalse(result["credential_validated"])
        self.assertFalse(result["network_invoked"])
        self.assertFalse(result["provider_constructed"])
        self.assertFalse(result["cognition_invoked"])
        self.assertFalse(result["ready"])
        self.assertFalse(result["qualified_fit"])
        self.assertFalse(result["selected"])
        self.assertFalse(result["observed"])
        self.assertFalse(result["routing_enabled"])
        self.assertFalse(result["mission_created"])
        self.assertFalse(result["authority_changed"])
        self.assertFalse(result["auto_selection"])
        self.assertNotIn("SECRET-A-SENTINEL", repr(result))
        self.assertNotIn("UNRELATED-SECRET-SENTINEL", repr(result))

    def test_malformed_or_ambiguous_catalog_fails_closed_without_broker_consultation(self):
        cases = [
            (
                {"GROX_REASONER_CATALOG_JSON": "{not-json"},
                "invalid_catalog",
            ),
            (
                {
                    "GROX_REASONER_CATALOG_JSON": json.dumps(
                        [
                            {
                                "provider_kind": "openai",
                                "model": "model-a",
                                "endpoint": ENDPOINT,
                                "credential_alias": "alias-a",
                            }
                        ]
                    ),
                    "GROX_REASONER_PROVIDER": "openai",
                },
                "ambiguous",
            ),
        ]

        for config, expected_status in cases:
            with self.subTest(expected_status=expected_status):
                broker = TrackingSecretBroker({"alias-a": "SECRET-SENTINEL"})
                result = ConfiguredCognitionCatalogCredentialAvailability(
                    config,
                    broker,
                ).inventory()

                self.assertEqual(result["status"], expected_status)
                self.assertEqual(result["resources"], [])
                self.assertEqual(result["remote_resource_count"], 0)
                self.assertEqual(result["bound_remote_resource_count"], 0)
                self.assertEqual(result["available_remote_resource_count"], 0)
                self.assertEqual(broker.alias_checks, [])
                self.assertFalse(result["secret_broker_consulted"])
                self.assertFalse(result["secret_alias_availability_checked"])

    def test_legacy_single_resource_availability_remains_compatible(self):
        config = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "legacy-model",
            "GROX_REASONER_ENDPOINT": ENDPOINT,
            "GROX_REASONER_CREDENTIAL_ALIAS": "legacy-alias",
        }
        broker = TrackingSecretBroker({"legacy-alias": "LEGACY-SECRET-SENTINEL"})

        legacy = ConfiguredCredentialAliasAvailability(config, broker).inventory()
        catalog = ConfiguredCognitionCatalogCredentialAvailability(config, broker).inventory()

        self.assertEqual(catalog["status"], "ok")
        self.assertEqual(catalog["configuration_source"], "legacy_single")
        self.assertEqual(
            catalog["resources"][0]["resource_id"],
            legacy["resources"][0]["resource_id"],
        )
        self.assertEqual(catalog["resources"][0]["credential_alias"], "legacy-alias")
        self.assertTrue(catalog["resources"][0]["credential_alias_available"])
        self.assertEqual(broker.alias_checks, ["legacy-alias", "legacy-alias"])


if __name__ == "__main__":
    unittest.main()
