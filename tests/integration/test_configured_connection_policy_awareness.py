from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.contracts import MissionMode, MissionOrder
from grox.pilot import PilotGorXu
from grox.tools.policy import GatewayPolicy


class PilotConfiguredConnectionPolicyAwarenessTests(unittest.TestCase):
    def test_pilot_connection_policy_inventory_is_read_only_and_secret_blind(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reasoner = object()
            policy = GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({"https://api.openai.com"}),
            )
            pilot = PilotGorXu(root, reasoner=reasoner, gateway_policy=policy)
            before_reasoner = pilot.reasoner
            before_missions = pilot.store.recent_missions()
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
                discovered = pilot.live_configured_cognition_inventory()["resources"][0]
                order = MissionOrder.new(
                    "MSN-configured-connection-policy",
                    "inspect configured connection policy",
                    "inspect configured connection policy",
                    MissionMode.inspect,
                    "backend-engineer",
                    allowed_actions=("net_fetch",),
                    parameters={
                        "operation": "configured_cognition_connection_authorization",
                        "resource_id": discovered["resource_id"],
                        "endpoint": discovered["endpoint"],
                        "allowed_origins": ["https://api.openai.com"],
                    },
                ).seal()
                snapshot = pilot.live_configured_connection_policy_inventory(order=order)
            self.assertIs(pilot.reasoner, before_reasoner)
            self.assertEqual(pilot.store.recent_missions(), before_missions)
            self.assertTrue(snapshot["authorized"])
            self.assertFalse(snapshot["ready"])
            self.assertFalse(snapshot["network_invoked"])
            self.assertNotIn("SUPER-SECRET-SENTINEL", repr(snapshot))


if __name__ == "__main__":
    unittest.main()
