from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery, nonsecret_reasoner_config_from_env


class ConfiguredCognitionDiscoveryTests(unittest.TestCase):
    def test_supported_openai_configuration_is_discovered_only(self):
        config = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "gpt-test-model",
            "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
        }
        inventory = ConfiguredCognitionDiscovery(config).inventory()
        repeated = ConfiguredCognitionDiscovery(config).inventory()
        self.assertEqual(inventory["status"], "ok")
        self.assertEqual(len(inventory["resources"]), 1)
        item = inventory["resources"][0]
        self.assertEqual(item["provider_kind"], "openai")
        self.assertEqual(item["model"], "gpt-test-model")
        self.assertEqual(item["endpoint"], "https://api.openai.com/v1/responses")
        self.assertTrue(item["resource_id"].startswith("cognition:configured:openai:"))
        self.assertEqual(item["resource_id"], repeated["resources"][0]["resource_id"])
        self.assertTrue(item["discovered"])
        for field in ("authorized", "ready", "qualified_fit", "selected", "observed"):
            self.assertFalse(item[field], field)
        self.assertFalse(inventory["authority_changed"])
        self.assertFalse(inventory["auto_activation"])
        self.assertFalse(inventory["auto_selection"])
        self.assertFalse(inventory["network_invoked"])
        self.assertFalse(inventory["credential_inspected"])

    def test_local_llama_configuration_does_not_probe_executable_or_model_store(self):
        inventory = ConfiguredCognitionDiscovery(
            {
                "GROX_REASONER_PROVIDER": "local-llama-cpp",
                "GROX_REASONER_MODEL": "qwen-seed",
            }
        ).inventory()
        item = inventory["resources"][0]
        self.assertEqual(item["provider_kind"], "local-llama-cpp")
        self.assertEqual(item["model"], "qwen-seed")
        self.assertIsNone(item["endpoint"])
        self.assertTrue(item["discovered"])
        self.assertFalse(item["ready"])

    def test_missing_incomplete_malformed_and_unsupported_configuration_fail_closed(self):
        cases = [
            ({}, "unconfigured"),
            ({"GROX_REASONER_PROVIDER": "openai"}, "incomplete"),
            ({"GROX_REASONER_PROVIDER": "openai", "GROX_REASONER_MODEL": "m", "GROX_REASONER_ENDPOINT": "not-a-url"}, "incomplete"),
            ({"GROX_REASONER_PROVIDER": "unknown-provider", "GROX_REASONER_MODEL": "m"}, "unsupported"),
        ]
        for config, status in cases:
            with self.subTest(config=config):
                inventory = ConfiguredCognitionDiscovery(config).inventory()
                self.assertEqual(inventory["status"], status)
                if inventory["resources"]:
                    item = inventory["resources"][0]
                    self.assertFalse(item["ready"])
                    self.assertFalse(item["authorized"])
                    self.assertFalse(item["qualified_fit"])
                    self.assertFalse(item["selected"])
                    self.assertFalse(item["observed"])

    def test_environment_snapshot_never_reads_secret_key(self):
        values = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "gpt-test-model",
            "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
        }
        touched = []

        def fake_getenv(name, default=""):
            touched.append(name)
            if name == "OPENAI_API_KEY":
                raise AssertionError("secret key must not be inspected")
            return values.get(name, default)

        with patch("grox.cognition_discovery.os.getenv", side_effect=fake_getenv):
            snapshot = nonsecret_reasoner_config_from_env()
        self.assertNotIn("OPENAI_API_KEY", touched)
        self.assertEqual(snapshot, values)

    def test_output_never_contains_unrelated_or_secret_configuration(self):
        secret = "SUPER-SECRET-SENTINEL"
        inventory = ConfiguredCognitionDiscovery(
            {
                "GROX_REASONER_PROVIDER": "openai",
                "GROX_REASONER_MODEL": "gpt-test-model",
                "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
                "OPENAI_API_KEY": secret,
                "UNRELATED_PRIVATE_VALUE": "PRIVATE-SENTINEL",
            }
        ).inventory()
        encoded = repr(inventory)
        self.assertNotIn(secret, encoded)
        self.assertNotIn("PRIVATE-SENTINEL", encoded)
        self.assertNotIn("OPENAI_API_KEY", encoded)

    def test_malformed_legacy_alias_does_not_change_base_discovery_contract(self):
        config = {
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "legacy-model",
            "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
            "GROX_REASONER_CREDENTIAL_ALIAS": "not valid alias",
        }

        inventory = ConfiguredCognitionDiscovery(config).inventory()

        self.assertEqual(inventory["status"], "ok")
        self.assertEqual(inventory["configuration_source"], "legacy_single")
        self.assertEqual(inventory["resources"][0]["model"], "legacy-model")
        self.assertNotIn("credential_alias", inventory["resources"][0])

    def test_explicit_catalog_discovers_multiple_resources_in_declared_order_without_alias_exposure(self):
        catalog = [
            {
                "provider_kind": "openai",
                "model": "remote-model-a",
                "endpoint": "https://api.openai.com/v1/responses",
                "credential_alias": "openai-a",
            },
            {
                "provider_kind": "local-llama-cpp",
                "model": "local-model-b",
            },
            {
                "provider_kind": "openai",
                "model": "remote-model-c",
                "endpoint": "https://api.openai.com/v1/responses",
                "credential_alias": "openai-c",
            },
        ]
        config = {"GROX_REASONER_CATALOG_JSON": json.dumps(catalog)}

        discovery = ConfiguredCognitionDiscovery(config)
        inventory = discovery.inventory()
        declared = discovery.declared_configs()

        self.assertEqual(inventory["status"], "ok")
        self.assertEqual(inventory["configuration_source"], "explicit_catalog")
        self.assertEqual(inventory["catalog_entry_count"], 3)
        self.assertEqual(
            [item["model"] for item in inventory["resources"]],
            ["remote-model-a", "local-model-b", "remote-model-c"],
        )
        self.assertEqual(
            [item["provider_kind"] for item in inventory["resources"]],
            ["openai", "local-llama-cpp", "openai"],
        )
        self.assertEqual(declared[0]["GROX_REASONER_CREDENTIAL_ALIAS"], "openai-a")
        self.assertEqual(declared[2]["GROX_REASONER_CREDENTIAL_ALIAS"], "openai-c")
        self.assertNotIn("credential_alias", repr(inventory))
        self.assertNotIn("openai-a", repr(inventory))
        self.assertNotIn("openai-c", repr(inventory))
        self.assertEqual(len({item["resource_id"] for item in inventory["resources"]}), 3)
        for item in inventory["resources"]:
            self.assertTrue(item["discovered"])
            self.assertFalse(item["authorized"])
            self.assertFalse(item["ready"])
            self.assertFalse(item["qualified_fit"])
            self.assertFalse(item["selected"])
            self.assertFalse(item["observed"])

    def test_catalog_and_legacy_single_configuration_are_mutually_exclusive(self):
        config = {
            "GROX_REASONER_CATALOG_JSON": json.dumps(
                [{
                    "provider_kind": "openai",
                    "model": "catalog-model",
                    "endpoint": "https://api.openai.com/v1/responses",
                }]
            ),
            "GROX_REASONER_PROVIDER": "openai",
            "GROX_REASONER_MODEL": "legacy-model",
        }

        discovery = ConfiguredCognitionDiscovery(config)
        inventory = discovery.inventory()

        self.assertEqual(inventory["status"], "ambiguous")
        self.assertEqual(inventory["resources"], [])
        self.assertEqual(discovery.declared_configs(), ())

    def test_catalog_malformed_unsupported_duplicate_and_over_limit_fail_closed_without_partial_inventory(self):
        valid = {
            "provider_kind": "openai",
            "model": "remote-model",
            "endpoint": "https://api.openai.com/v1/responses",
        }
        cases = {
            "malformed_json": "{not-json",
            "wrong_shape": json.dumps({"provider_kind": "openai"}),
            "unknown_field": json.dumps([{**valid, "priority": 1}]),
            "unsupported": json.dumps([{
                "provider_kind": "unknown-provider",
                "model": "remote-model",
                "endpoint": "https://example.invalid/v1/responses",
            }]),
            "incomplete_remote": json.dumps([{
                "provider_kind": "openai",
                "model": "remote-model",
            }]),
            "local_remote_metadata": json.dumps([{
                "provider_kind": "local-llama-cpp",
                "model": "local-model",
                "endpoint": "http://127.0.0.1:8080/v1/responses",
            }]),
            "duplicate_resource": json.dumps([
                {**valid, "credential_alias": "alias-a"},
                {**valid, "credential_alias": "alias-b"},
            ]),
            "over_limit": json.dumps([
                {
                    "provider_kind": "openai",
                    "model": f"model-{index}",
                    "endpoint": "https://api.openai.com/v1/responses",
                }
                for index in range(9)
            ]),
        }
        for name, raw in cases.items():
            with self.subTest(name=name):
                discovery = ConfiguredCognitionDiscovery({"GROX_REASONER_CATALOG_JSON": raw})
                inventory = discovery.inventory()
                self.assertEqual(inventory["status"], "invalid_catalog")
                self.assertEqual(inventory["resources"], [])
                self.assertEqual(discovery.declared_configs(), ())

    def test_catalog_environment_snapshot_is_nonsecret_and_does_not_read_provider_keys(self):
        raw_catalog = json.dumps([
            {
                "provider_kind": "openai",
                "model": "remote-model-a",
                "endpoint": "https://api.openai.com/v1/responses",
                "credential_alias": "openai-a",
            }
        ])
        touched = []

        def fake_getenv(name, default=""):
            touched.append(name)
            if name == "OPENAI_API_KEY":
                raise AssertionError("secret key must not be inspected")
            return raw_catalog if name == "GROX_REASONER_CATALOG_JSON" else default

        with patch("grox.cognition_discovery.os.getenv", side_effect=fake_getenv):
            snapshot = nonsecret_reasoner_config_from_env()

        self.assertEqual(snapshot, {"GROX_REASONER_CATALOG_JSON": raw_catalog})
        self.assertIn("GROX_REASONER_CATALOG_JSON", touched)
        self.assertNotIn("OPENAI_API_KEY", touched)


if __name__ == "__main__":
    unittest.main()
