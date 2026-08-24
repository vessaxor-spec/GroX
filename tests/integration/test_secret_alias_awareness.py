from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from grox.pilot import PilotGorXu
from grox.secret_awareness import SecretAliasAwareness
from grox.tools.secrets import SecretBroker


class SecretAliasAwarenessIntegrationTests(unittest.TestCase):
    def test_pilot_injected_broker_supports_secret_blind_awareness(self):
        secret = "GROX-INTEGRATION-SECRET-SENTINEL"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs/crew/dossiers").mkdir(parents=True)
            (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
            (root / "configs/crew/company-manifest.json").write_text('{"crew": []}', encoding="utf-8")

            pilot = PilotGorXu(root, reasoner=None, secret_broker=SecretBroker({"openai-api-key": secret}))
            before = pilot.store.recent_missions(1000)

            result = SecretAliasAwareness(pilot.gateway.secret_broker).inspect("openai-api-key")

            self.assertTrue(result["available"])
            self.assertFalse(result["authorized"])
            self.assertFalse(result["ready"])
            self.assertFalse(result["credential_validated"])
            self.assertFalse(result["secret_materialized"])
            self.assertNotIn(secret, repr(result))
            self.assertEqual(pilot.store.recent_missions(1000), before)
            self.assertIsNone(pilot.reasoner)

    def test_default_empty_pilot_broker_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs/crew/dossiers").mkdir(parents=True)
            (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
            (root / "configs/crew/company-manifest.json").write_text('{"crew": []}', encoding="utf-8")

            pilot = PilotGorXu(root, reasoner=None)
            result = SecretAliasAwareness(pilot.gateway.secret_broker).inspect("openai-api-key")

            self.assertFalse(result["available"])
            self.assertFalse(result["ready"])
            self.assertFalse(result["credential_validated"])


if __name__ == "__main__":
    unittest.main()
