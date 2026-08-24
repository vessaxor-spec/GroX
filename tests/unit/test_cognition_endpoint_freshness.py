from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_awareness import CognitionProviderAwareness
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.gateway import ToolGateway
from grox.tools.policy import GatewayPolicy


ORIGIN = "https://api.openai.com"
ENDPOINT = ORIGIN + "/v1/responses"


class CognitionEndpointFreshnessRedBaselineTests(unittest.TestCase):
    def test_exact_bound_endpoint_surface_requires_a_distinct_refresh_seam(self):
        with tempfile.TemporaryDirectory() as td:
            gateway = ToolGateway(
                Path(td),
                policy=GatewayPolicy(
                    network_enabled=True,
                    allowed_origins=frozenset({ORIGIN}),
                    network_timeout_seconds=3,
                    max_response_bytes=4096,
                ),
            )
            provider = OpenAIResponsesProvider(
                api_key="REMOTE-SECRET-SENTINEL",
                model="remote-model-sentinel",
                endpoint=ENDPOINT,
            )
            awareness = CognitionProviderAwareness(reasoner=provider, gateway=gateway)
            resource_id = awareness.inventory()["resources"][0]["resource_id"]
            order = MissionOrder.new(
                "MSN-endpoint-red",
                "Refresh exact bound endpoint evidence",
                "Observe only the exact configured remote cognition endpoint path",
                MissionMode.inspect,
                "researcher",
                allowed_actions=("net_fetch",),
                parameters={
                    "operation": "cognition_endpoint_probe",
                    "resource_id": resource_id,
                    "endpoint": ENDPOINT,
                    "allowed_origins": [ORIGIN],
                },
            ).seal()

            with patch.object(
                gateway,
                "fetch_url",
                return_value={"url": ENDPOINT, "origin": ORIGIN, "status": 405, "preview": "ignored"},
            ) as fetch:
                refreshed = awareness.refresh_endpoint_surface(resource_id=resource_id, order=order)

            fetch.assert_called_once_with(order, ENDPOINT)
            self.assertTrue(refreshed["endpoint_surface_fresh"])
            self.assertEqual(refreshed["endpoint_surface_status"], "responding")
            self.assertEqual(refreshed["endpoint_http_status"], 405)
            self.assertFalse(refreshed["ready"])
            self.assertFalse(refreshed["authorized"])
            self.assertFalse(refreshed["qualified_fit"])


if __name__ == "__main__":
    unittest.main()
