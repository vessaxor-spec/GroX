from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_awareness import CognitionEndpointAuthorizationError, CognitionProviderAwareness
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.gateway import ToolDenied, ToolGateway
from grox.tools.policy import GatewayPolicy

ORIGIN="https://api.openai.com"
ENDPOINT=ORIGIN+"/v1/responses"

class CognitionEndpointFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name)
        self.gateway=ToolGateway(self.root,policy=GatewayPolicy(network_enabled=True,allowed_origins=frozenset({ORIGIN}),network_timeout_seconds=3,max_response_bytes=4096))
        self.provider=OpenAIResponsesProvider(api_key="REMOTE-SECRET-SENTINEL",model="remote-model-sentinel",endpoint=ENDPOINT)
        self.observations={}; self.now=1000.0
        self.awareness=CognitionProviderAwareness(reasoner=self.provider,gateway=self.gateway,endpoint_observations=self.observations,clock=lambda:self.now,transport_freshness_seconds=60)
        self.resource_id=self.awareness.inventory()["resources"][0]["resource_id"]
    def tearDown(self): self.td.cleanup()
    def order(self, *, endpoint=ENDPOINT, operation="cognition_endpoint_probe", resource_id=None, allowed_actions=("net_fetch",), allowed_origins=(ORIGIN,), seal=True):
        o=MissionOrder.new("MSN-endpoint-test","Refresh exact bound endpoint evidence","Observe only exact configured endpoint path",MissionMode.inspect,"researcher",allowed_actions=allowed_actions,parameters={"operation":operation,"resource_id":resource_id or self.resource_id,"endpoint":endpoint,"allowed_origins":list(allowed_origins)})
        return o.seal() if seal else o
    def test_passive_inventory_performs_zero_network_io(self):
        with patch.object(self.gateway,"fetch_url") as fetch: item=self.awareness.inventory()["resources"][0]
        fetch.assert_not_called(); self.assertFalse(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"unproven"); self.assertFalse(item["ready"])
    def test_unsealed_order_is_rejected_without_becoming_sealed(self):
        order=self.order(seal=False)
        with patch.object(self.gateway,"fetch_url") as fetch:
            with self.assertRaises(CognitionEndpointAuthorizationError): self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=order)
        fetch.assert_not_called(); self.assertFalse(order.sealed)
    def test_exact_endpoint_authority_is_required(self):
        cases=[self.order(endpoint=ORIGIN+"/v1/other"),self.order(operation="cognition_transport_probe"),self.order(resource_id="cognition:other"),self.order(allowed_actions=()),self.order(allowed_origins=("https://example.invalid",))]
        for order in cases:
            with self.subTest(params=dict(order.parameters)):
                with patch.object(self.gateway,"fetch_url") as fetch:
                    with self.assertRaises(CognitionEndpointAuthorizationError): self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=order)
                fetch.assert_not_called()
    def test_http_response_is_privacy_minimized_and_never_implies_ready(self):
        response={"url":ENDPOINT,"origin":ORIGIN,"status":405,"preview":"RESPONSE-BODY-SENTINEL"}
        with patch.object(self.gateway,"fetch_url",return_value=response) as fetch: item=self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=self.order())
        fetch.assert_called_once(); self.assertEqual(fetch.call_args.args[1],ENDPOINT); self.assertTrue(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"responding"); self.assertEqual(item["endpoint_http_status"],405); self.assertFalse(item["ready"]); self.assertFalse(item["authorized"]); self.assertFalse(item["qualified_fit"]); encoded=json.dumps(item,sort_keys=True); self.assertNotIn("RESPONSE-BODY-SENTINEL",encoded); self.assertNotIn("REMOTE-SECRET-SENTINEL",repr(fetch.call_args)); self.assertNotIn("remote-model-sentinel",repr(fetch.call_args))
    def test_response_classification_preserves_evidence_without_readiness_claim(self):
        for status,label in ((404,"not_found"),(503,"server_degraded"),(401,"responding")):
            with self.subTest(status=status):
                with patch.object(self.gateway,"fetch_url",return_value={"url":ENDPOINT,"origin":ORIGIN,"status":status,"preview":"ignored"}): item=self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=self.order())
                self.assertEqual(item["endpoint_surface_status"],label); self.assertTrue(item["endpoint_surface_fresh"]); self.assertFalse(item["ready"])
    def test_network_failure_replaces_prior_positive_and_observation_expires(self):
        with patch.object(self.gateway,"fetch_url",return_value={"url":ENDPOINT,"origin":ORIGIN,"status":405,"preview":"ignored"}): self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=self.order())
        self.now+=1
        with patch.object(self.gateway,"fetch_url",side_effect=ToolDenied("network failed")): item=self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=self.order())
        self.assertTrue(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"unreachable"); self.assertFalse(item["ready"]); self.now+=61; item=self.awareness.inventory()["resources"][0]; self.assertFalse(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"stale")
    def test_same_resource_endpoint_rebind_invalidates_prior_evidence(self):
        with patch.object(self.gateway,"fetch_url",return_value={"url":ENDPOINT,"origin":ORIGIN,"status":405,"preview":"ignored"}): self.awareness.refresh_endpoint_surface(resource_id=self.resource_id,order=self.order())
        rebound=OpenAIResponsesProvider(api_key="different",model="remote-model-sentinel",endpoint=ORIGIN+"/v1/other")
        other=CognitionProviderAwareness(reasoner=rebound,gateway=self.gateway,endpoint_observations=self.observations,clock=lambda:self.now)
        item=other.inventory()["resources"][0]; self.assertEqual(item["resource_id"],self.resource_id); self.assertFalse(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"unproven")
    def test_missing_or_malformed_endpoint_evidence_fails_closed(self):
        for endpoint,origin in ((None,ORIGIN),("not-a-url",ORIGIN),(ENDPOINT,None),(ENDPOINT,"not-an-origin")):
            self.observations[self.resource_id]={"observed_at":self.now,"endpoint":endpoint,"origin":origin,"responded":True,"http_status":200}
            item=self.awareness.inventory()["resources"][0]; self.assertFalse(item["endpoint_surface_fresh"]); self.assertEqual(item["endpoint_surface_status"],"unproven")

if __name__=="__main__": unittest.main()
