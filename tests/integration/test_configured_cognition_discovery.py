from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu


class PilotConfiguredCognitionDiscoveryTests(unittest.TestCase):
    def test_pilot_inventory_is_read_only_and_does_not_change_bound_reasoner(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reasoner = object()
            pilot = PilotGorXu(root, reasoner=reasoner)
            before_reasoner = pilot.reasoner
            with patch.dict(
                "os.environ",
                {
                    "GROX_REASONER_PROVIDER": "openai",
                    "GROX_REASONER_MODEL": "gpt-test-model",
                    "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
                    "OPENAI_API_KEY": "SUPER-SECRET-SENTINEL",
                },
                clear=False,
            ):
                inventory = pilot.live_configured_cognition_inventory()
            self.assertIs(pilot.reasoner, before_reasoner)
            self.assertEqual(inventory["status"], "ok")
            self.assertEqual(len(inventory["resources"]), 1)
            item = inventory["resources"][0]
            self.assertTrue(item["discovered"])
            self.assertFalse(item["authorized"])
            self.assertFalse(item["ready"])
            self.assertFalse(item["qualified_fit"])
            self.assertFalse(item["selected"])
            self.assertFalse(item["observed"])
            self.assertNotIn("SUPER-SECRET-SENTINEL", repr(inventory))
            self.assertEqual(pilot.store.recent_missions(), [])


if __name__ == "__main__":
    unittest.main()
