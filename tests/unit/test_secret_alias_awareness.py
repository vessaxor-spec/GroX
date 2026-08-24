from __future__ import annotations

import unittest

from grox.secret_awareness import SecretAliasAwareness
from grox.tools.secrets import SecretBroker


class MaterializationTrapBroker(SecretBroker):
    def materialize_env(self, *args, **kwargs):
        raise AssertionError("secret materialization must not occur during awareness")


class SecretAliasAwarenessTests(unittest.TestCase):
    def test_exact_alias_availability_never_exposes_secret_value(self):
        secret = "GROX-SECRET-SENTINEL-DO-NOT-EXPOSE"
        awareness = SecretAliasAwareness(SecretBroker({"openai-api-key": secret}))

        result = awareness.inspect("openai-api-key")

        self.assertTrue(result["available"])
        self.assertEqual(result["alias"], "openai-api-key")
        self.assertFalse(result["authorized"])
        self.assertFalse(result["ready"])
        self.assertFalse(result["qualified_fit"])
        self.assertFalse(result["selected"])
        self.assertFalse(result["observed"])
        self.assertFalse(result["secret_materialized"])
        self.assertFalse(result["credential_validated"])
        self.assertNotIn(secret, repr(result))

    def test_awareness_never_materializes_secret(self):
        awareness = SecretAliasAwareness(
            MaterializationTrapBroker({"openai-api-key": "GROX-MATERIALIZATION-TRAP"})
        )

        result = awareness.inspect("openai-api-key")

        self.assertTrue(result["available"])
        self.assertFalse(result["secret_materialized"])

    def test_absent_alias_fails_closed_without_enumerating_other_aliases(self):
        awareness = SecretAliasAwareness(SecretBroker({"other-alias": "value"}))

        result = awareness.inspect("openai-api-key")

        self.assertFalse(result["available"])
        self.assertEqual(result["alias"], "openai-api-key")
        self.assertNotIn("other-alias", repr(result))
        self.assertFalse(result["secret_materialized"])

    def test_alias_must_be_exact_nonempty_string(self):
        awareness = SecretAliasAwareness(SecretBroker({"openai-api-key": "value"}))
        for alias in ("", " openai-api-key", "openai-api-key "):
            with self.subTest(alias=alias):
                with self.assertRaises(ValueError):
                    awareness.inspect(alias)


if __name__ == "__main__":
    unittest.main()
