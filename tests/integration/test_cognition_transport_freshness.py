from __future__ import annotations

import unittest
from unittest.mock import patch

from grox.contracts import MissionMode, MissionOrder
from grox.pilot import PilotGorXu
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.policy import GatewayPolicy
from tests._support import temp_vessel


ORIGIN = "https://api.openai.com"


class PilotCognitionTransportFreshnessTests(unittest.TestCase):
    def test_pilot_refresh_is_explicit_non_mission_transport_observation_only(self):
        td, root, bootstrap = temp_vessel()
        try:
            bootstrap.store.close()
            provider = OpenAIResponsesProvider(api_key="pilot-secret-sentinel", model="pilot-remote-model")
            pilot = PilotGorXu(
                root,
                reasoner=provider,
                gateway_policy=GatewayPolicy(
                    network_enabled=True,
                    allowed_origins=frozenset({ORIGIN}),
                    network_timeout_seconds=3,
                    max_response_bytes=4096,
                ),
            )
            try:
                before = pilot.store.recent_missions()
                resource_id = pilot.live_cognition_provider_inventory()["resources"][0]["resource_id"]
                order = MissionOrder.new(
                    "MSN-external-probe-context",
                    "Refresh only remote transport evidence",
                    "Probe exact bound cognition origin",
                    MissionMode.inspect,
                    "researcher",
                    allowed_actions=["net_fetch"],
                    parameters={
                        "operation": "cognition_transport_probe",
                        "resource_id": resource_id,
                        "allowed_origins": [ORIGIN],
                    },
                ).seal()
                with patch.object(
                    pilot.gateway,
                    "fetch_url",
                    return_value={"origin": ORIGIN, "status": 401, "preview": "must-not-escape"},
                ) as fetch:
                    refreshed = pilot.refresh_cognition_transport(resource_id=resource_id, order=order)
                fetch.assert_called_once()
                self.assertTrue(refreshed["transport_reachable"])
                self.assertFalse(refreshed["ready"])
                self.assertFalse(refreshed["authorized"])
                self.assertEqual(pilot.store.recent_missions(), before)

                current = pilot.live_cognition_provider_inventory()["resources"][0]
                self.assertTrue(current["transport_reachable"])
                self.assertFalse(current["ready"])
                self.assertFalse(current["qualified_fit"])
                self.assertFalse(current["authority_changed"])
            finally:
                pilot.store.close()
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
