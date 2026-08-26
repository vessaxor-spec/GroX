from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.cognition_discovery import (
    ConfiguredCognitionDiscovery,
    nonsecret_reasoner_config_from_env,
)
from grox.configured_openai_probe import ConfiguredOpenAIAuthenticatedModelProbe
from grox.contracts import MissionMode, MissionOrder
from grox.runtime_layout import VesselLayout
from grox.tools.layout_gateway import LayoutToolGateway
from grox.tools.policy import GatewayPolicy
from grox.tools.secrets import SecretBroker


OFFICIAL_ENDPOINT = "https://api.openai.com/v1/responses"
OFFICIAL_ORIGIN = "https://api.openai.com"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
SECRET = "INTEGRATION-OPENAI-PROBE-SECRET"


class FakeResponse:
    status = 200

    def read(self, limit: int) -> bytes:
        return json.dumps({"id": MODEL, "object": "model", "owned_by": "openai"}).encode()


class FakeHTTPSConnection:
    requests: list[tuple[str, str, dict[str, str]]] = []

    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.closed = False

    def request(self, method, path, headers=None):
        self.__class__.requests.append((method, path, dict(headers or {})))

    def getresponse(self):
        return FakeResponse()

    def close(self):
        self.closed = True


class ConfiguredOpenAIAuthenticatedModelProbeIntegrationTests(unittest.TestCase):
    def test_environment_discovery_to_exact_authenticated_visibility_preserves_later_state_boundaries(self):
        FakeHTTPSConnection.requests = []
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            assets = root / "assets"
            state = root / "state"
            work = root / "work"
            for path in (assets, state, work):
                path.mkdir()
            layout = VesselLayout.separated(
                asset_root=assets,
                state_root=state,
                work_root=work,
            )
            gateway = LayoutToolGateway(
                layout,
                policy=GatewayPolicy(
                    network_enabled=True,
                    allowed_origins=frozenset({OFFICIAL_ORIGIN}),
                    max_response_bytes=4096,
                ),
                secret_broker=SecretBroker({ALIAS: SECRET}),
            )
            env = {
                "GROX_REASONER_PROVIDER": "openai",
                "GROX_REASONER_MODEL": MODEL,
                "GROX_REASONER_ENDPOINT": OFFICIAL_ENDPOINT,
                "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
            }
            with patch.dict(os.environ, env, clear=False):
                config = nonsecret_reasoner_config_from_env()
            resource = ConfiguredCognitionDiscovery(config).inventory()["resources"][0]
            order = MissionOrder.new(
                "MSN-openai-probe-integration",
                "verify configured OpenAI model visibility",
                "verify configured OpenAI model visibility",
                MissionMode.inspect,
                "application-security-engineer",
                allowed_actions=("net_fetch", "secret_use"),
                parameters={
                    "operation": "configured_openai_authenticated_model_probe",
                    "resource_id": resource["resource_id"],
                    "provider_kind": "openai",
                    "model": MODEL,
                    "endpoint": OFFICIAL_ENDPOINT,
                    "credential_alias": ALIAS,
                    "allowed_origins": [OFFICIAL_ORIGIN],
                    "secret_grants": [ALIAS],
                },
            ).seal()

            with patch(
                "grox.tools.layout_gateway.http.client.HTTPSConnection",
                FakeHTTPSConnection,
            ):
                result = ConfiguredOpenAIAuthenticatedModelProbe(config, gateway).probe(
                    order=order
                )

        self.assertEqual(result["resource_id"], resource["resource_id"])
        self.assertEqual(result["classification"], "authenticated_model_visible")
        self.assertTrue(result["credential_use_authorized"])
        self.assertTrue(result["credential_accepted_for_model_visibility"])
        self.assertTrue(result["secret_materialized"])
        self.assertTrue(result["network_invoked"])
        self.assertFalse(result["response_body_returned"])
        self.assertFalse(result["cognition_invoked"])
        self.assertFalse(result["ready"])
        self.assertFalse(result["qualified_fit"])
        self.assertFalse(result["selected"])
        self.assertFalse(result["observed"])
        self.assertFalse(result["mission_created"])
        self.assertFalse(result["authority_changed"])
        self.assertNotIn(SECRET, repr(result))
        self.assertEqual(len(FakeHTTPSConnection.requests), 1)
        method, path, headers = FakeHTTPSConnection.requests[0]
        self.assertEqual(method, "GET")
        self.assertEqual(path, f"/v1/models/{MODEL}")
        self.assertEqual(headers["Authorization"], f"Bearer {SECRET}")


if __name__ == "__main__":
    unittest.main()
