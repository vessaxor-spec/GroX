from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu
from grox.tools.secrets import SecretBroker


ENDPOINT = "https://api.openai.com/v1/responses"


class PilotConfiguredCognitionCatalogBindingTests(unittest.TestCase):
    def test_pilot_catalog_binding_inventory_is_read_only_and_secret_blind(self):
        with tempfile.TemporaryDirectory() as td:
            pilot = PilotGorXu(Path(td), reasoner=object())
            raw = json.dumps([
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
                },
            ])

            with patch.dict(
                "os.environ",
                {"GROX_REASONER_CATALOG_JSON": raw},
                clear=True,
            ), patch.object(
                SecretBroker,
                "materialize_env",
                side_effect=AssertionError("catalog binding must never materialize a secret"),
            ):
                result = pilot.live_configured_cognition_catalog_binding_inventory()

            self.assertEqual(result["status"], "incomplete_binding")
            self.assertEqual(
                [item["model"] for item in result["resources"]],
                ["model-a", "local-b", "model-c"],
            )
            self.assertEqual(result["remote_resource_count"], 2)
            self.assertEqual(result["bound_remote_resource_count"], 1)
            self.assertEqual(result["resources"][0]["credential_alias"], "alias-a")
            self.assertEqual(result["resources"][1]["credential_binding_status"], "not_applicable")
            self.assertEqual(result["resources"][2]["credential_binding_status"], "unbound")
            self.assertFalse(result["secret_broker_consulted"])
            self.assertFalse(result["secret_alias_availability_checked"])
            self.assertFalse(result["credential_inspected"])
            self.assertFalse(result["network_invoked"])
            self.assertFalse(result["provider_constructed"])
            self.assertFalse(result["cognition_invoked"])
            self.assertFalse(result["ready"])
            self.assertFalse(result["selected"])
            self.assertFalse(result["routing_enabled"])
            self.assertFalse(result["authority_changed"])
            self.assertEqual(pilot.store.recent_missions(), [])


if __name__ == "__main__":
    unittest.main()
