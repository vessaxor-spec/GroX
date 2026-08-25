from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu
from grox.tools.secrets import SecretBroker


OPENAI_CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": "remote-model-sentinel",
    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
    "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
}


class MaterializationTrapBroker(SecretBroker):
    def materialize_env(self, order, requested):
        raise AssertionError("Pilot awareness must never materialize credential values")


class PilotConfiguredCredentialAliasAvailabilityTests(unittest.TestCase):
    def test_pilot_composes_exact_alias_availability_without_mission_secret_or_network_activity(self):
        secret = "PILOT-CREDENTIAL-SECRET-SENTINEL"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs/crew/dossiers").mkdir(parents=True)
            (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
            (root / "configs/crew/company-manifest.json").write_text('{"crew": []}', encoding="utf-8")

            broker = MaterializationTrapBroker({"openai-primary": secret})
            pilot = PilotGorXu(root, reasoner=None, secret_broker=broker)
            before = pilot.store.recent_missions(1000)

            with patch("grox.pilot.nonsecret_reasoner_config_from_env", return_value=OPENAI_CONFIG):
                result = pilot.live_configured_credential_alias_availability_inventory()

            self.assertEqual(result["status"], "ok")
            item = result["resources"][0]
            self.assertTrue(item["credential_alias_available"])
            self.assertEqual(item["credential_alias"], "openai-primary")
            self.assertTrue(item["secret_broker_consulted"])
            self.assertTrue(item["secret_alias_availability_checked"])
            self.assertFalse(item["secret_materialized"])
            self.assertFalse(item["credential_inspected"])
            self.assertFalse(item["credential_validated"])
            self.assertFalse(item["network_invoked"])
            self.assertFalse(item["provider_constructed"])
            self.assertFalse(item["cognition_invoked"])
            self.assertFalse(item["mission_created"])
            self.assertFalse(item["authorized"])
            self.assertFalse(item["ready"])
            self.assertFalse(item["qualified_fit"])
            self.assertFalse(item["selected"])
            self.assertFalse(item["observed"])
            self.assertNotIn(secret, repr(result))
            self.assertEqual(pilot.store.recent_missions(1000), before)
            self.assertIsNone(pilot.reasoner)


if __name__ == "__main__":
    unittest.main()
