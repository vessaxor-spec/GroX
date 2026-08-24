from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_awareness import (
    CognitionProviderAwareness,
    CognitionTransportAuthorizationError,
)
from grox.contracts import MissionMode, MissionOrder
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.tools.gateway import ToolDenied, ToolGateway
from grox.tools.policy import GatewayPolicy


ORIGIN = "https://api.openai.com"


class CognitionTransportFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        self.gateway = ToolGateway(
            self.root,
            policy=GatewayPolicy(
                network_enabled=True,
                allowed_origins=frozenset({ORIGIN}),
                network_timeout_seconds=3,
                max_response_bytes=4096,
            ),
        )
        self.provider = OpenAIResponsesProvider(
            api_key="REMOTE-SECRET-SENTINEL",
            model="remote-model-sentinel",
        )
        self.observations: dict[str, object] = {}
        self.now = 1000.0
        self.awareness = CognitionProviderAwareness(
            reasoner=self.provider,
            gateway=self.gateway,
            transport_observations=self.observations,
            clock=lambda: self.now,
            transport_freshness_seconds=60,
        )
        self.resource_id = self.awareness.inventory()["resources"][0]["resource_id"]

    def tearDown(self):
        self.td.cleanup()

    def order(
        self,
        *,
        allowed_actions=("net_fetch",),
        allowed_origins=(ORIGIN,),
        resource_id: str | None = None,
        operation: str = "cognition_transport_probe",
        seal: bool = True,
    ) -> MissionOrder:
        order = MissionOrder.new(
            "MSN-transport-test",
            "Refresh remote cognition transport evidence",
            "Refresh only the exact bound remote cognition origin",
            MissionMode.inspect,
            "researcher",
            allowed_actions=allowed_actions,
            parameters={
                "operation": operation,
                "resource_id": resource_id or self.resource_id,
                "allowed_origins": list(allowed_origins),
            },
        )
        return order.seal() if seal else order

    def test_passive_inventory_performs_zero_network_io(self):
        with patch.object(self.gateway, "fetch_url") as fetch:
            inventory = self.awareness.inventory()
        fetch.assert_not_called()
        item = inventory["resources"][0]
        self.assertFalse(item["ready"])
        self.assertFalse(item["transport_reachable"])
        self.assertFalse(item["transport_fresh"])
        self.assertEqual(item["transport_status"], "unproven")

    def test_unsealed_order_is_rejected_without_becoming_sealed(self):
        order = self.order(seal=False)
        with patch.object(self.gateway, "fetch_url") as fetch:
            with self.assertRaises(CognitionTransportAuthorizationError):
                self.awareness.refresh_transport(resource_id=self.resource_id, order=order)
        fetch.assert_not_called()
        self.assertFalse(order.sealed)

    def test_exact_net_fetch_operation_resource_and_origin_grants_are_required(self):
        cases = [
            self.order(allowed_actions=()),
            self.order(allowed_origins=("https://example.invalid",)),
            self.order(resource_id="cognition:gorxu_reasoner:other:000000000000"),
            self.order(operation="http_fetch"),
        ]
        for order in cases:
            with self.subTest(parameters=dict(order.parameters)):
                with patch.object(self.gateway, "fetch_url") as fetch:
                    with self.assertRaises(CognitionTransportAuthorizationError):
                        self.awareness.refresh_transport(resource_id=self.resource_id, order=order)
                fetch.assert_not_called()

    def test_positive_http_observation_is_privacy_minimized_and_never_implies_ready(self):
        response = {
            "url": ORIGIN + "/",
            "origin": ORIGIN,
            "status": 401,
            "content_type": "application/json",
            "bytes": 321,
            "sha256": "a" * 64,
            "redirect_followed": False,
            "preview": "RESPONSE-BODY-SENTINEL",
        }
        with patch.object(self.gateway, "fetch_url", return_value=response) as fetch:
            refreshed = self.awareness.refresh_transport(
                resource_id=self.resource_id,
                order=self.order(),
            )
        fetch.assert_called_once()
        _, url = fetch.call_args.args
        self.assertEqual(url, ORIGIN + "/")
        encoded_call = repr(fetch.call_args)
        self.assertNotIn("REMOTE-SECRET-SENTINEL", encoded_call)
        self.assertNotIn("remote-model-sentinel", encoded_call)

        self.assertTrue(refreshed["transport_reachable"])
        self.assertTrue(refreshed["transport_fresh"])
        self.assertEqual(refreshed["transport_status"], "reachable")
        self.assertEqual(refreshed["transport_http_status"], 401)
        self.assertFalse(refreshed["ready"])
        self.assertFalse(refreshed["authorized"])
        self.assertFalse(refreshed["qualified_fit"])

        encoded = json.dumps(refreshed, sort_keys=True)
        self.assertNotIn("RESPONSE-BODY-SENTINEL", encoded)
        self.assertNotIn("REMOTE-SECRET-SENTINEL", encoded)

    def test_transport_observation_expires_without_becoming_remote_readiness(self):
        with patch.object(
            self.gateway,
            "fetch_url",
            return_value={"origin": ORIGIN, "status": 404, "preview": "ignored"},
        ):
            self.awareness.refresh_transport(resource_id=self.resource_id, order=self.order())
        self.now += 61
        item = self.awareness.inventory()["resources"][0]
        self.assertFalse(item["transport_reachable"])
        self.assertFalse(item["transport_fresh"])
        self.assertEqual(item["transport_status"], "stale")
        self.assertFalse(item["ready"])

    def test_network_failure_replaces_prior_positive_current_claim(self):
        with patch.object(
            self.gateway,
            "fetch_url",
            return_value={"origin": ORIGIN, "status": 200, "preview": "ignored"},
        ):
            first = self.awareness.refresh_transport(resource_id=self.resource_id, order=self.order())
        self.assertTrue(first["transport_reachable"])

        self.now += 1
        with patch.object(self.gateway, "fetch_url", side_effect=ToolDenied("network request failed")):
            second = self.awareness.refresh_transport(resource_id=self.resource_id, order=self.order())
        self.assertFalse(second["transport_reachable"])
        self.assertTrue(second["transport_fresh"])
        self.assertEqual(second["transport_status"], "unreachable")
        self.assertIsNone(second["transport_http_status"])
        self.assertFalse(second["ready"])

    def test_rebinding_ignores_prior_resource_transport_observation(self):
        with patch.object(
            self.gateway,
            "fetch_url",
            return_value={"origin": ORIGIN, "status": 200, "preview": "ignored"},
        ):
            self.awareness.refresh_transport(resource_id=self.resource_id, order=self.order())

        rebound = OpenAIResponsesProvider(api_key="different-secret", model="different-model")
        rebound_awareness = CognitionProviderAwareness(
            reasoner=rebound,
            gateway=self.gateway,
            transport_observations=self.observations,
            clock=lambda: self.now,
            transport_freshness_seconds=60,
        )
        item = rebound_awareness.inventory()["resources"][0]
        self.assertNotEqual(item["resource_id"], self.resource_id)
        self.assertFalse(item["transport_reachable"])
        self.assertFalse(item["transport_fresh"])
        self.assertEqual(item["transport_status"], "unproven")

    def test_same_resource_identity_endpoint_rebind_invalidates_prior_origin_evidence(self):
        with patch.object(
            self.gateway,
            "fetch_url",
            return_value={"origin": ORIGIN, "status": 200, "preview": "ignored"},
        ):
            first = self.awareness.refresh_transport(resource_id=self.resource_id, order=self.order())
        self.assertTrue(first["transport_reachable"])

        rebound = OpenAIResponsesProvider(
            api_key="different-secret",
            model="remote-model-sentinel",
            endpoint="https://example.invalid/v1/responses",
        )
        rebound_awareness = CognitionProviderAwareness(
            reasoner=rebound,
            gateway=self.gateway,
            transport_observations=self.observations,
            clock=lambda: self.now,
            transport_freshness_seconds=60,
        )
        item = rebound_awareness.inventory()["resources"][0]
        self.assertEqual(item["resource_id"], self.resource_id)
        self.assertFalse(item["transport_reachable"])
        self.assertFalse(item["transport_fresh"])
        self.assertEqual(item["transport_status"], "unproven")

    def test_missing_or_malformed_observation_origin_fails_closed(self):
        for observed_origin in (None, "not-an-http-origin"):
            with self.subTest(observed_origin=observed_origin):
                self.observations[self.resource_id] = {
                    "observed_at": self.now,
                    "origin": observed_origin,
                    "reachable": True,
                    "http_status": 200,
                }
                item = self.awareness.inventory()["resources"][0]
                self.assertFalse(item["transport_reachable"])
                self.assertFalse(item["transport_fresh"])
                self.assertEqual(item["transport_status"], "unproven")
                self.assertIsNone(item["transport_http_status"])

    def test_non_remote_bound_resource_cannot_be_transport_probed(self):
        from grox.reasoning.session import SessionReasoningProvider

        session_awareness = CognitionProviderAwareness(
            reasoner=SessionReasoningProvider(lambda directive, roster: {}, name="session-only"),
            gateway=self.gateway,
            transport_observations=self.observations,
            clock=lambda: self.now,
        )
        resource_id = session_awareness.inventory()["resources"][0]["resource_id"]
        order = self.order(resource_id=resource_id)
        with patch.object(self.gateway, "fetch_url") as fetch:
            with self.assertRaises(CognitionTransportAuthorizationError):
                session_awareness.refresh_transport(resource_id=resource_id, order=order)
        fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
