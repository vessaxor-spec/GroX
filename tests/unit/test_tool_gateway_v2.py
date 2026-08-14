from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
from threading import Thread
import unittest

from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.tools.gateway import ToolDenied, ToolGateway
from grox.tools.mcp import MCPAdapterSpec
from grox.tools.secrets import SecretBroker


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "mcp_echo_server.py"
HAS_BROWSER = importlib.util.find_spec("playwright") is not None and any(shutil.which(x) for x in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"))


class QuietHandler(BaseHTTPRequestHandler):
    body = b"<html><title>A5</title><h1>qualified</h1><img src='http://example.invalid/blocked.png'><iframe src='file:///etc/passwd'></iframe></html>"
    status = 200
    def do_GET(self):
        self.send_response(self.status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)
    def log_message(self, *_):
        pass


class GatewayV2Tests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        (self.root / "configs/state").mkdir(parents=True)

    def tearDown(self):
        self.td.cleanup()

    def order(self, *, actions, parameters=None, crew="devops-engineer"):
        return MissionOrder.new(
            "MSN-A5", "intent", "objective", MissionMode.execute, crew,
            required_capabilities=["repo_read"], allowed_actions=list(actions),
            forbidden_actions=[], scope=["."], risk_class=RiskClass.high,
            parameters=parameters or {},
        )

    def test_workspace_is_chrooted_network_namespaced_and_secret_output_is_redacted(self):
        secret = "A5-DO-NOT-PERSIST"
        gateway = ToolGateway(self.root, secret_broker=SecretBroker({"token": secret}))
        order = self.order(
            actions=["workspace_exec", "secret_use"],
            parameters={"secret_grants": ["token"]},
        )
        result = gateway.workspace_shell(
            order,
            'test ! -e /etc/passwd; printf "%s" "$TOKEN"; printf qualified > /work/result.txt',
            secret_env={"TOKEN": "token"},
        )
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["stdout"], "[REDACTED]")
        self.assertNotIn(secret, result["stdout"])
        self.assertEqual(result["secret_aliases"], ["token"])
        self.assertIn("network_namespace", result["isolation"])
        self.assertIn("chroot", result["isolation"])
        self.assertFalse(result["workspace_retained"])
        self.assertFalse((self.root / "configs/state/workspaces" / result["workspace"]).exists())
        self.assertEqual(result["files"][0]["path"], "result.txt")

    def test_secret_alias_must_be_granted_by_order(self):
        gateway = ToolGateway(self.root, secret_broker=SecretBroker({"token": "value"}))
        order = self.order(actions=["workspace_exec", "secret_use"], parameters={"secret_grants": []})
        with self.assertRaises(ToolDenied):
            gateway.workspace_shell(order, 'printf ok', secret_env={"TOKEN": "token"})

    def test_network_origin_requires_both_host_policy_and_order_grant(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            gateway = ToolGateway(self.root, extra_allowed_origins=[origin])
            denied = self.order(actions=["net_fetch"], parameters={"allowed_origins": []}, crew="researcher")
            with self.assertRaises(ToolDenied):
                gateway.fetch_url(denied, origin + "/")
            allowed = self.order(actions=["net_fetch"], parameters={"allowed_origins": [origin]}, crew="researcher")
            result = gateway.fetch_url(allowed, origin + "/")
            self.assertEqual(result["status"], 200)
            self.assertEqual(result["origin"], origin)
            self.assertFalse(result["redirect_followed"])
        finally:
            server.shutdown(); server.server_close()

    def test_order_cannot_expand_host_origin_policy(self):
        gateway = ToolGateway(self.root)
        order = self.order(actions=["net_fetch"], parameters={"allowed_origins": ["https://example.com"]}, crew="researcher")
        with self.assertRaises(ToolDenied):
            gateway.fetch_url(order, "https://example.com/")

    @unittest.skipUnless(HAS_BROWSER, "Playwright plus Chromium/Chrome required")
    def test_browser_renders_gateway_fetched_html_offline_and_captures_evidence(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            gateway = ToolGateway(self.root, extra_allowed_origins=[origin])
            order = self.order(
                actions=["net_fetch", "browser_capture"],
                parameters={"allowed_origins": [origin]}, crew="researcher",
            )
            result = gateway.browser_capture(order, origin + "/")
            self.assertTrue(result["offline_render"])
            self.assertEqual(result["browser_network"], "disabled_after_gateway_fetch")
            self.assertIn("network_namespace", result["browser_isolation"])
            self.assertIn("http://example.invalid", result["blocked_origins"])
            shot = self.root / result["screenshot"]
            self.assertTrue(shot.is_file())
            self.assertGreater(result["screenshot_bytes"], 100)
        finally:
            server.shutdown(); server.server_close()

    def test_mcp_adapter_is_pre_registered_and_tool_granted(self):
        spec = MCPAdapterSpec(
            argv=(sys.executable, str(FIXTURE)),
            allowed_tools=frozenset({"echo", "mutate"}),
            mutating_tools=frozenset({"mutate"}),
        )
        gateway = ToolGateway(self.root, mcp_registry={"qualification": spec})
        order = self.order(
            actions=["mcp_call"],
            parameters={"mcp_grants": {"qualification": ["echo"]}}, crew="platform-engineer",
        )
        result = gateway.mcp_call(order, "qualification", "echo", {"text": "hello"})
        self.assertEqual(result["protocol_version"], "2025-06-18")
        self.assertEqual(result["tool"], "echo")
        self.assertFalse(result["mutating"])

    def test_mcp_mutation_requires_separate_action_grant(self):
        spec = MCPAdapterSpec(
            argv=(sys.executable, str(FIXTURE)),
            allowed_tools=frozenset({"mutate"}),
            mutating_tools=frozenset({"mutate"}),
        )
        gateway = ToolGateway(self.root, mcp_registry={"qualification": spec})
        order = self.order(
            actions=["mcp_call"],
            parameters={"mcp_grants": {"qualification": ["mutate"]}}, crew="platform-engineer",
        )
        with self.assertRaises(ToolDenied):
            gateway.mcp_call(order, "qualification", "mutate", {})

    def test_privileged_action_itself_must_be_in_mission_order(self):
        gateway = ToolGateway(self.root)
        order = self.order(actions=[])
        with self.assertRaises(ToolDenied):
            gateway.workspace_shell(order, "printf denied")


if __name__ == "__main__":
    unittest.main()
