from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu
from tests._support import temp_vessel


CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": "remote-model-sentinel",
    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
    "GROX_REASONER_CREDENTIAL_ALIAS": "openai-primary",
    "OPENAI_API_KEY": "SECRET-VALUE-SENTINEL",
}


class PilotConfiguredCredentialBindingTests(unittest.TestCase):
    def test_pilot_exposes_nonsecret_binding_without_mission_or_secret_access(self):
        td, root, bootstrap = temp_vessel()
        try:
            bootstrap.store.close()
            with patch.dict(os.environ, CONFIG, clear=False):
                pilot = PilotGorXu(root, reasoner=None)
                try:
                    before = pilot.store.recent_missions()
                    discovered = pilot.live_configured_cognition_inventory()["resources"][0]
                    result = pilot.live_configured_credential_binding_inventory()
                    item = result["resources"][0]

                    self.assertEqual(result["status"], "ok")
                    self.assertEqual(item["resource_id"], discovered["resource_id"])
                    self.assertEqual(item["credential_alias"], "openai-primary")
                    self.assertTrue(item["credential_binding_configured"])
                    self.assertFalse(result["secret_broker_consulted"])
                    self.assertFalse(result["secret_alias_availability_checked"])
                    self.assertFalse(result["credential_inspected"])
                    self.assertFalse(result["credential_validated"])
                    self.assertFalse(result["network_invoked"])
                    self.assertFalse(result["provider_constructed"])
                    self.assertFalse(result["cognition_invoked"])
                    self.assertFalse(result["mission_created"])
                    self.assertFalse(result["authority_changed"])
                    self.assertEqual(pilot.store.recent_missions(), before)
                    encoded = repr(result)
                    self.assertNotIn("SECRET-VALUE-SENTINEL", encoded)
                    self.assertNotIn("OPENAI_API_KEY", encoded)
                finally:
                    pilot.store.close()
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
