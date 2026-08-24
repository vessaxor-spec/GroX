from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
