from __future__ import annotations
import unittest
from unittest.mock import patch
from grox.contracts import MissionMode, MissionOrder
from grox.pilot import PilotGorXu
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.policy import GatewayPolicy
from tests._support import temp_vessel
ORIGIN="https://api.openai.com"; ENDPOINT=ORIGIN+"/v1/responses"
class PilotCognitionEndpointFreshnessTests(unittest.TestCase):
    def test_pilot_refresh_is_explicit_non_mission_endpoint_observation_only(self):
        td,root,bootstrap=temp_vessel()
        try:
            bootstrap.store.close(); provider=OpenAIResponsesProvider(api_key="pilot-secret",model="pilot-remote-model",endpoint=ENDPOINT); pilot=PilotGorXu(root,reasoner=provider,gateway_policy=GatewayPolicy(network_enabled=True,allowed_origins=frozenset({ORIGIN}),network_timeout_seconds=3,max_response_bytes=4096))
            try:
                before=pilot.store.recent_missions(); rid=pilot.live_cognition_provider_inventory()["resources"][0]["resource_id"]; order=MissionOrder.new("MSN-endpoint-context","Refresh exact endpoint evidence","Probe exact bound cognition endpoint",MissionMode.inspect,"researcher",allowed_actions=["net_fetch"],parameters={"operation":"cognition_endpoint_probe","resource_id":rid,"endpoint":ENDPOINT,"allowed_origins":[ORIGIN]}).seal()
                with patch.object(pilot.gateway,"fetch_url",return_value={"url":ENDPOINT,"origin":ORIGIN,"status":405,"preview":"discard"}) as fetch: item=pilot.refresh_cognition_endpoint_surface(resource_id=rid,order=order)
                fetch.assert_called_once_with(order,ENDPOINT); self.assertTrue(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"responding"); self.assertFalse(item["ready"]); self.assertFalse(item["authorized"]); self.assertEqual(pilot.store.recent_missions(),before); current=pilot.live_cognition_provider_inventory()["resources"][0]; self.assertTrue(current["endpoint_surface_fresh"]); self.assertFalse(current["qualified_fit"]); self.assertFalse(current["authority_changed"])
            finally: pilot.store.close()
        finally: td.cleanup()
if __name__=="__main__": unittest.main()
