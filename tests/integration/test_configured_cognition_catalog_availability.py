from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu
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
            "Pilot catalog availability must never materialize credential values"
        )


class PilotConfiguredCognitionCatalogCredentialAvailabilityTests(unittest.TestCase):
    def test_pilot_catalog_availability_is_read_only_exact_alias_and_mission_free(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs/crew/dossiers").mkdir(parents=True)
            (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
            (root / "configs/crew/company-manifest.json").write_text(
                '{"crew": []}', encoding="utf-8"
            )

            broker = TrackingSecretBroker(
                {
                    "alias-a": "PILOT-SECRET-A-SENTINEL",
                    "other": "PILOT-OTHER-SECRET-SENTINEL",
                }
            )
            pilot = PilotGorXu(root, reasoner=None, secret_broker=broker)
            before = pilot.store.recent_missions(1000)
            raw = json.dumps(
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
                ]
            )

            with patch.dict(
                "os.environ",
                {"GROX_REASONER_CATALOG_JSON": raw},
                clear=True,
            ):
                result = (
                    pilot.live_configured_cognition_catalog_credential_availability_inventory()
                )

            self.assertEqual(result["status"], "ok")
            self.assertEqual(
                [item["model"] for item in result["resources"]],
                ["model-a", "local-b", "model-c"],
            )
            self.assertTrue(result["resources"][0]["credential_alias_available"])
            self.assertIsNone(result["resources"][1]["credential_alias_available"])
            self.assertFalse(result["resources"][2]["credential_alias_available"])
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
            self.assertEqual(pilot.store.recent_missions(1000), before)
            self.assertIsNone(pilot.reasoner)
            self.assertNotIn("PILOT-SECRET-A-SENTINEL", repr(result))
            self.assertNotIn("PILOT-OTHER-SECRET-SENTINEL", repr(result))


if __name__ == "__main__":
    unittest.main()
