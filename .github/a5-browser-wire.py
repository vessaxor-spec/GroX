from pathlib import Path

# Tool Gateway: route browser execution through the dedicated governed runtime.
p = Path('src/grox/tools/gateway.py')
s = p.read_text()
if 'from .browser import BrowserRuntime, BrowserUnavailable\n' not in s:
    s = s.replace(
        'from .mcp import MCPAdapterSpec, MCPError, StdioMCPClient\n',
        'from .browser import BrowserRuntime, BrowserUnavailable\nfrom .mcp import MCPAdapterSpec, MCPError, StdioMCPClient\n',
    )
s = s.replace(
    'from .workspace import IsolatedWorkspace, WorkspaceUnavailable, namespace_backend_available, docker_backend_available\n',
    'from .workspace import IsolatedWorkspace, WorkspaceUnavailable\n',
).replace(
    'from .workspace import IsolatedWorkspace, WorkspaceUnavailable, namespace_backend_available\n',
    'from .workspace import IsolatedWorkspace, WorkspaceUnavailable\n',
)
if '        self._browser = BrowserRuntime(self.root, self.policy)\n' not in s:
    s = s.replace(
        '        self._workspace: IsolatedWorkspace | None = None\n',
        '        self._workspace: IsolatedWorkspace | None = None\n        self._browser = BrowserRuntime(self.root, self.policy)\n',
    )
start = s.index('    def browser_capture(self, order: MissionOrder, url: str) -> dict:\n')
end = s.index('\n    def mcp_call(', start)
new_browser = '''    def browser_capture(self, order: MissionOrder, url: str) -> dict:\n        self._allowed(order, "browser_capture")\n        if not self.policy.browser_enabled:\n            raise ToolDenied("browser capability disabled by host policy")\n        meta, raw = self._fetch_response(order, url)\n        content_type = meta["content_type"].lower()\n        if "html" not in content_type and "xhtml" not in content_type:\n            raise ToolDenied("browser capture requires an HTML response")\n        try:\n            result = self._browser.capture(\n                raw.decode("utf-8", errors="replace"), order.mission_id, order.order_id\n            )\n        except BrowserUnavailable as exc:\n            raise ToolDenied(str(exc)) from exc\n        result.update({\n            "source_url": meta["url"],\n            "origin": meta["origin"],\n            "source_status": meta["status"],\n            "source_sha256": meta["sha256"],\n            "source_bytes": meta["bytes"],\n        })\n        return result\n'''
s = s[:start] + new_browser + s[end:]
p.write_text(s)

# Unit tests: backend-neutral workspace assertion + host-injected Docker browser policy.
p = Path('tests/unit/test_tool_gateway_v2.py')
s = p.read_text()
if 'import os\n' not in s:
    s = s.replace('import importlib.util\n', 'import importlib.util\nimport os\n')
needle = 'DOCKER_IMAGE = "alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc"\n'
if 'BROWSER_DOCKER_IMAGE = ' not in s:
    s = s.replace(needle, needle + 'BROWSER_DOCKER_IMAGE = os.environ.get("A5_BROWSER_DOCKER_IMAGE")\nBROWSER_SECCOMP_PROFILE = os.environ.get("A5_BROWSER_SECCOMP_PROFILE")\n')
s = s.replace('test ! -e /etc/passwd;', 'test ! -e /host;')
fs = s.index('    def test_browser_renders_gateway_fetched_html_offline_and_captures_evidence(self):')
fe = s.index('\n    def test_mcp_adapter_is_pre_registered_and_tool_granted', fs)
seg = s[fs:fe]
seg = seg.replace(
    '            gateway = ToolGateway(self.root, extra_allowed_origins=[origin])\n',
    '            gateway = ToolGateway(\n                self.root,\n                policy=GatewayPolicy(\n                    allowed_origins=frozenset({origin}),\n                    browser_docker_image=BROWSER_DOCKER_IMAGE,\n                    browser_docker_seccomp_profile=BROWSER_SECCOMP_PROFILE,\n                ),\n            )\n',
)
a0 = seg.index('            self.assertTrue(\n', seg.index('self.assertEqual(result["browser_network"]'))
a1 = seg.index('            self.assertIn("http://example.invalid"', a0)
seg = seg[:a0] + '''            self.assertIn(result["browser_backend"], {"namespace", "docker"})\n            self.assertTrue(\n                "network_namespace" in result["browser_isolation"]\n                or "docker_network_none" in result["browser_isolation"]\n            )\n            if result["browser_backend"] == "docker":\n                self.assertIn("chromium_native_sandbox", result["browser_isolation"])\n                self.assertIn("playwright_seccomp", result["browser_isolation"])\n                self.assertTrue(result["browser_image_id"])\n''' + seg[a1:]
s = s[:fs] + seg + s[fe:]
p.write_text(s)

# Integration qualification: same injected Docker browser policy and backend-neutral checks.
p = Path('tests/integration/test_governed_capabilities.py')
s = p.read_text()
if 'import os\n' not in s:
    s = s.replace('from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\n', 'from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\nimport os\n')
if 'BROWSER_DOCKER_IMAGE = ' not in s:
    s = s.replace(needle, needle + 'BROWSER_DOCKER_IMAGE = os.environ.get("A5_BROWSER_DOCKER_IMAGE")\nBROWSER_SECCOMP_PROFILE = os.environ.get("A5_BROWSER_SECCOMP_PROFILE")\n')
s = s.replace('test ! -e /etc/passwd;', 'test ! -e /host;')
s = s.replace(
    'gateway_policy=GatewayPolicy(allowed_origins=frozenset({origin}), workspace_docker_image=DOCKER_IMAGE),',
    'gateway_policy=GatewayPolicy(\n                    allowed_origins=frozenset({origin}),\n                    workspace_docker_image=DOCKER_IMAGE,\n                    browser_docker_image=BROWSER_DOCKER_IMAGE,\n                    browser_docker_seccomp_profile=BROWSER_SECCOMP_PROFILE,\n                ),',
)
old = '''            self.assertTrue(\n                'network_namespace' in browser['browser_isolation']\n                or 'chromium_native_sandbox' in browser['browser_isolation']\n            )\n'''
if old in s:
    s = s.replace(old, '''            self.assertIn(browser['browser_backend'], {'namespace', 'docker'})\n            self.assertTrue(\n                'network_namespace' in browser['browser_isolation']\n                or 'docker_network_none' in browser['browser_isolation']\n            )\n            if browser['browser_backend'] == 'docker':\n                self.assertIn('chromium_native_sandbox', browser['browser_isolation'])\n                self.assertIn('playwright_seccomp', browser['browser_isolation'])\n                self.assertTrue(browser['browser_image_id'])\n''')
p.write_text(s)

# Specification: browser fallback is pre-provisioned Docker, never unsandboxed host Chromium.
p = Path('docs/specification/GOVERNED_CAPABILITIES.md')
s = p.read_text()
old = '''Where the host supports the full A5 namespace set, the browser worker also runs inside user, PID, and network namespaces. Where user namespaces are blocked but the process is non-root, GroX instead requires Chromium's native sandbox and adds deny-at-resolution and dead-proxy controls. A root host without the outer namespace boundary is denied. This keeps network authority in the Gateway rather than silently falling back to an unsandboxed root browser.\n'''
new = '''Where the host supports the full A5 namespace set, the browser worker runs inside user, PID, and network namespaces. Where that namespace set is blocked, GroX requires a separately commissioned Docker browser image. That image is built from the Playwright v1.62.0 Noble base pinned by registry digest, installs the matching Python Playwright package, and runs the worker as a dedicated non-root `groxbrowser` user with Chromium's native sandbox enabled. The Docker path uses the Playwright seccomp profile pinned to the v1.62.0 source commit, `network=none`, dropped Linux capabilities, `no-new-privileges`, a read-only root, bounded resources, private tmpfs/shared memory, and only an ephemeral screenshot scratch directory mounted writable. Runtime uses `--pull never` and never builds or downloads the image or seccomp profile.\n\nIf neither the outer namespace path nor the pre-provisioned Docker browser boundary is available, browser capture is denied. This keeps network authority in the Gateway rather than silently falling back to an unsandboxed host browser.\n'''
if old in s:
    s = s.replace(old, new)
s = s.replace('- selected browser isolation controls and Chromium sandbox mode;\n', '- selected browser backend, isolation controls, Chromium sandbox mode, and container image ID when Docker is used;\n')
s = s.replace(
    'Browser evidence lives under the private `configs/state/browser/` path and is excluded from source control.\n',
    'Browser evidence lives under the private `configs/state/browser/` path and is excluded from source control. Host commissioning for the Docker fallback is explicit through `scripts/commission-a5-browser.sh`; the resulting image and seccomp profile are host/private operational assets rather than command authority or Vessel memory.\n',
)
p.write_text(s)
