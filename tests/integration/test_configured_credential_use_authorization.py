from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_credential_use_authorization import ConfiguredCredentialUseAuthorization
from grox.contracts import MissionMode, MissionOrder
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
        raise AssertionError("configured credential-use awareness must never materialize credential values")


class PilotConfiguredCredentialUseAuthorizationTests(unittest.TestCase):
    def test_gorxu_gateway_authorizes_exact_alias_use_without_materialization_network_provider_or_mission_activity(self):
        secret = "PILOT-CREDENTIAL-SECRET-SENTINEL"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs/crew/dossiers").mkdir(parents=True)
            (root / "configs/tool-policy.json").write_text("{}", encoding="utf-8")
            (root / "configs/crew/company-manifest.json").write_text('{"crew": []}', encoding="utf-8")

            broker = MaterializationTrapBroker({"openai-primary": secret})
            pilot = PilotGorXu(root, reasoner=None, secret_broker=broker)
            before = pilot.store.recent_missions(1000)
            resource = ConfiguredCognitionDiscovery(OPENAI_CONFIG).inventory()["resources"][0]
            order = MissionOrder.new(
                "MSN-pilot-credential-use-awareness",
                "inspect configured credential-use authorization",
                "inspect configured credential-use authorization",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("secret_use",),
                parameters={
                    "operation": "configured_cognition_credential_use_authorization",
                    "resource_id": resource["resource_id"],
                    "provider_kind": resource["provider_kind"],
                    "model": resource["model"],
                    "endpoint": resource["endpoint"],
                    "credential_alias": "openai-primary",
                    "secret_grants": ["openai-primary"],
                },
            ).seal()

            result = ConfiguredCredentialUseAuthorization(
                OPENAI_CONFIG, pilot.gateway
            ).inventory(order=order)

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["authorization_status"], "sealed_mission_order_authorized")
            item = result["resources"][0]
            self.assertTrue(item["credential_alias_available"])
            self.assertTrue(item["credential_use_authorized"])
            self.assertEqual(item["credential_alias"], "openai-primary")
            self.assertFalse(item["authorized"])
            self.assertFalse(item["ready"])
            self.assertFalse(item["qualified_fit"])
            self.assertFalse(item["selected"])
            self.assertFalse(item["observed"])
            self.assertFalse(item["secret_materialized"])
            self.assertFalse(item["credential_inspected"])
            self.assertFalse(item["credential_validated"])
            self.assertFalse(item["network_invoked"])
            self.assertFalse(item["provider_constructed"])
            self.assertFalse(item["cognition_invoked"])
            self.assertFalse(item["mission_created"])
            self.assertFalse(item["authority_changed"])
            self.assertFalse(item["auto_selection"])
            self.assertNotIn(secret, repr(result))
            self.assertEqual(pilot.store.recent_missions(1000), before)
            self.assertIsNone(pilot.reasoner)


if __name__ == "__main__":
    unittest.main()
