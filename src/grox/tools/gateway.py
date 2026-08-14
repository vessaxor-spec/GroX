from __future__ import annotations

from pathlib import Path
import hashlib
import http.client
import json
import os
import signal
import shutil
import ssl
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

from ..contracts import MissionOrder, MissionMode
from .mcp import MCPAdapterSpec, MCPError, StdioMCPClient
from .policy import GatewayPolicy, PolicyError, normalize_origin
from .secrets import SecretBroker, SecretDenied
from .workspace import IsolatedWorkspace, WorkspaceUnavailable, namespace_backend_available


class ToolDenied(PermissionError):
    pass


class ToolGateway:
    """Deny-wins Tool Gateway v2.

    Mission Orders grant actions. Host policy may only narrow those grants. Crew
    never supply raw host process argv, browser executables, secret values, or
    MCP adapter process definitions.
    """

    def __init__(
        self,
        vessel_root: Path,
        *,
        policy: GatewayPolicy | None = None,
        extra_allowed_origins: tuple[str, ...] | list[str] = (),
        secret_broker: SecretBroker | None = None,
        mcp_registry: dict[str, MCPAdapterSpec] | None = None,
    ):
        self.root = vessel_root.resolve()
        self.policy = policy or GatewayPolicy.from_file(
            self.root / "configs/tool-policy.json", extra_allowed_origins=extra_allowed_origins
        )
        self.secret_broker = secret_broker or SecretBroker()
        self.mcp = StdioMCPClient(mcp_registry)
        self._workspace: IsolatedWorkspace | None = None

    def _resolve(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        try:
            p.relative_to(self.root)
        except ValueError:
            raise ToolDenied(f"path escapes Vessel root: {rel}")
        return p

    def _allowed(self, order: MissionOrder, action: str) -> None:
        if action in order.forbidden_actions:
            raise ToolDenied(f"action explicitly forbidden: {action}")
        if action not in order.allowed_actions:
            raise ToolDenied(f"action not granted by Mission Order: {action}")
        if order.mode in {MissionMode.inspect, MissionMode.verify} and action in {"fs_write", "mcp_mutate"}:
            raise ToolDenied(f"{order.mode.value} mode cannot mutate")

    def _origin_grants(self, order: MissionOrder) -> frozenset[str]:
        raw = order.parameters.get("allowed_origins") or []
        if not isinstance(raw, list) or not all(isinstance(x, str) and x for x in raw):
            raise ToolDenied("allowed_origins must be a list of non-empty strings")
        try:
            requested = frozenset(normalize_origin(x) for x in raw)
        except PolicyError as exc:
            raise ToolDenied(str(exc)) from exc
        if not requested.issubset(self.policy.allowed_origins):
            denied = sorted(requested - self.policy.allowed_origins)
            raise ToolDenied(f"origin outside host policy: {denied}")
        return requested

    def _assert_url(self, order: MissionOrder, url: str) -> tuple[str, object]:
        try:
            origin = normalize_origin(url)
        except PolicyError as exc:
            raise ToolDenied(str(exc)) from exc
        if origin not in self._origin_grants(order):
            raise ToolDenied(f"origin not granted by Mission Order: {origin}")
        parsed = urlsplit(url)
        if parsed.fragment:
            # Fragments never affect the network request and are removed from evidence.
            url = url.split("#", 1)[0]
            parsed = urlsplit(url)
        return origin, parsed

    def list_path(self, order: MissionOrder, rel: str = "."):
        self._allowed(order, "fs_list")
        p = self._resolve(rel)
        if p.is_file():
            return [str(p.relative_to(self.root))]
        out = []
        for x in sorted(p.rglob("*")):
            if ".git" in x.parts or "__pycache__" in x.parts or x.name.endswith(".sqlite3"):
                continue
            if x.is_file():
                out.append(str(x.relative_to(self.root)))
            if len(out) >= 500:
                break
        return out

    def read_text(self, order: MissionOrder, rel: str, limit: int = 200000):
        self._allowed(order, "fs_read")
        p = self._resolve(rel)
        text = p.read_text(encoding="utf-8", errors="replace")
        return text[:limit]

    def capture_text(self, order: MissionOrder, rel: str, limit: int = 262144):
        self._allowed(order, "fs_read")
        p = self._resolve(rel)
        if not p.exists():
            return {"exists": False, "content": None, "sha256": None}
        if p.is_dir():
            raise IsADirectoryError(rel)
        raw = p.read_bytes()
        if len(raw) > limit:
            raise ToolDenied(f"rollback capture exceeds {limit} bytes: {rel}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ToolDenied(f"rollback capture requires UTF-8 text: {rel}") from exc
        return {"exists": True, "content": text, "sha256": hashlib.sha256(raw).hexdigest()}

    def hash_file(self, order: MissionOrder, rel: str):
        self._allowed(order, "fs_read")
        p = self._resolve(rel)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def current_hash(self, rel: str):
        p = self._resolve(rel)
        if not p.exists():
            return None
        if p.is_dir():
            raise IsADirectoryError(rel)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def _assert_write_scope(self, order: MissionOrder, p: Path, rel: str):
        scopes = [self._resolve(s) for s in order.scope]
        if not any(p == s or (s.is_dir() and p.is_relative_to(s)) for s in scopes):
            raise ToolDenied(f"write target outside Mission scope: {rel}")

    def write_text(self, order: MissionOrder, rel: str, content: str):
        self._allowed(order, "fs_write")
        p = self._resolve(rel)
        self._assert_write_scope(order, p, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{p.name}.grox-", dir=p.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, p)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return {
            "path": str(p.relative_to(self.root)),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }

    def rollback_text(
        self,
        order: MissionOrder,
        rel: str,
        *,
        existed: bool,
        content: str | None,
        expected_current_sha256: str | None,
    ):
        self._allowed(order, "fs_write")
        p = self._resolve(rel)
        self._assert_write_scope(order, p, rel)
        current = self.current_hash(rel)
        if current != expected_current_sha256:
            raise ToolDenied(f"rollback target diverged from journaled mutation: {rel}")
        if not existed:
            if p.exists():
                p.unlink()
            return {"path": rel, "restored": "absent", "sha256": None}
        if content is None:
            raise ToolDenied(f"rollback content missing: {rel}")
        result = self.write_text(order, rel, content)
        return {"path": rel, "restored": "content", "sha256": result["sha256"]}

    def run_tests(self, order: MissionOrder):
        self._allowed(order, "test_run")
        timeout = max(1, min(90, int(order.parameters.get("_graph_max_seconds", 90))))
        try:
            cp = subprocess.run(
                ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"test run exceeded {timeout}s") from exc
        return {"returncode": cp.returncode, "stdout": cp.stdout[-16000:], "stderr": cp.stderr[-16000:]}

    # --- A5 governed capabilities -------------------------------------------------

    def workspace_shell(self, order: MissionOrder, script: str, *, secret_env: dict[str, str] | None = None) -> dict:
        self._allowed(order, "workspace_exec")
        if not self.policy.workspace_enabled:
            raise ToolDenied("isolated workspace disabled by host policy")
        secret_values: dict[str, str] = {}
        aliases: list[str] = []
        if secret_env:
            self._allowed(order, "secret_use")
            try:
                secret_values, aliases = self.secret_broker.materialize_env(order, secret_env)
            except SecretDenied as exc:
                raise ToolDenied(str(exc)) from exc
        if self._workspace is None:
            try:
                self._workspace = IsolatedWorkspace(
                    self.root / "configs/state/workspaces",
                    timeout_seconds=self.policy.workspace_timeout_seconds,
                    memory_bytes=self.policy.workspace_memory_bytes,
                    file_bytes=self.policy.workspace_file_bytes,
                    docker_image=self.policy.workspace_docker_image,
                )
            except WorkspaceUnavailable as exc:
                raise ToolDenied(str(exc)) from exc
        result = self._workspace.run(order.mission_id, order.order_id, script, env=secret_values)
        result["stdout"] = self.secret_broker.redact(result["stdout"], secret_values)
        result["stderr"] = self.secret_broker.redact(result["stderr"], secret_values)
        result["secret_aliases"] = aliases
        return result

    def _fetch_response(self, order: MissionOrder, url: str) -> tuple[dict, bytes]:
        self._allowed(order, "net_fetch")
        if not self.policy.network_enabled:
            raise ToolDenied("network access disabled by host policy")
        origin, parsed = self._assert_url(order, url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        kwargs = {"timeout": self.policy.network_timeout_seconds}
        if parsed.scheme == "https":
            kwargs["context"] = ssl.create_default_context()
        conn = conn_cls(host, port, **kwargs)
        try:
            conn.request("GET", path, headers={"User-Agent": "GroX-A5/1.0", "Accept": "*/*"})
            response = conn.getresponse()
            raw = response.read(self.policy.max_response_bytes + 1)
            meta = {
                "url": f"{origin}{parsed.path or '/'}" + (f"?{parsed.query}" if parsed.query else ""),
                "origin": origin,
                "status": response.status,
                "content_type": (response.getheader("Content-Type") or "")[:200],
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "redirect_followed": False,
            }
        except TimeoutError:
            raise
        except OSError as exc:
            raise ToolDenied(f"network request failed within granted origin: {origin}: {exc}") from exc
        finally:
            conn.close()
        if len(raw) > self.policy.max_response_bytes:
            raise ToolDenied(f"network response exceeds {self.policy.max_response_bytes} bytes")
        return meta, raw

    def fetch_url(self, order: MissionOrder, url: str) -> dict:
        meta, raw = self._fetch_response(order, url)
        return {**meta, "preview": raw[:4096].decode("utf-8", errors="replace")}

    def browser_capture(self, order: MissionOrder, url: str) -> dict:
        self._allowed(order, "browser_capture")
        if not self.policy.browser_enabled:
            raise ToolDenied("browser capability disabled by host policy")
        meta, raw = self._fetch_response(order, url)
        content_type = meta["content_type"].lower()
        if "html" not in content_type and "xhtml" not in content_type:
            raise ToolDenied("browser capture requires an HTML response")
        html = raw.decode("utf-8", errors="replace")
        capture_dir = self.root / "configs/state/browser" / order.mission_id / order.order_id
        capture_dir.mkdir(parents=True, exist_ok=True)
        screenshot = capture_dir / "capture.png"
        with tempfile.TemporaryDirectory(prefix="grox-browser-") as td:
            scratch = Path(td)
            os.chmod(scratch, 0o777)
            worker_shot = scratch / "capture.png"
            request = {
                "html": html,
                "timeout_ms": self.policy.browser_timeout_seconds * 1000,
                "screenshot": str(worker_shot),
            }
            source_root = Path(__file__).resolve().parents[2]
            env = {
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONPATH": str(source_root),
                "HOME": str(scratch),
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
                "TERM": "dumb",
            }
            unshare = shutil.which("unshare")
            namespace_backend = bool(unshare and namespace_backend_available())
            request["outer_namespace"] = namespace_backend
            if namespace_backend:
                argv = [unshare, "--user", "--map-root-user", "--pid", "--fork", "--net", sys.executable, "-m", "grox.tools.browser_worker"]
                worker_identity = "user_namespace_root"
                browser_isolation = [
                    "user_namespace", "pid_namespace", "network_namespace",
                    "playwright_request_abort", "offline_gateway_content",
                ]
            else:
                if os.geteuid() == 0:
                    raise ToolDenied(
                        "browser capture requires either usable user/PID/network namespaces or a non-root host for the native Chromium sandbox"
                    )
                argv = [sys.executable, "-m", "grox.tools.browser_worker"]
                worker_identity = f"host_uid:{os.geteuid()}"
                browser_isolation = [
                    "chromium_native_sandbox", "playwright_request_abort",
                    "offline_gateway_content", "host_resolver_block", "dead_proxy",
                ]
            proc = subprocess.Popen(
                argv, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=scratch, env=env, start_new_session=True,
            )
            try:
                stdout, stderr = proc.communicate(json.dumps(request), timeout=self.policy.browser_timeout_seconds + 10)
            except subprocess.TimeoutExpired as exc:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait()
                raise TimeoutError(f"browser capture exceeded {self.policy.browser_timeout_seconds}s") from exc
            finally:
                # Chromium may leave helper descendants after the worker exits. The
                # dedicated process group is A5-private and is always reaped here.
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
            if proc.returncode != 0:
                raise ToolDenied(f"browser worker failed: {stderr[-2000:]}")
            if not worker_shot.exists():
                raise ToolDenied("browser worker returned without screenshot evidence")
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise ToolDenied("browser worker returned invalid evidence") from exc
            shot = worker_shot.read_bytes()
        screenshot.write_bytes(shot)
        result.update({
            "source_url": meta["url"],
            "origin": meta["origin"],
            "source_status": meta["status"],
            "source_sha256": meta["sha256"],
            "source_bytes": meta["bytes"],
            "screenshot": str(screenshot.relative_to(self.root)),
            "screenshot_sha256": hashlib.sha256(shot).hexdigest(),
            "screenshot_bytes": len(shot),
            "worker_identity": worker_identity,
            "browser_isolation": browser_isolation,
            "browser_network": "disabled_after_gateway_fetch",
        })
        return result

    def mcp_call(self, order: MissionOrder, adapter: str, tool: str, arguments: dict) -> dict:
        self._allowed(order, "mcp_call")
        if not self.policy.mcp_enabled:
            raise ToolDenied("MCP adapters disabled by host policy")
        grants = order.parameters.get("mcp_grants") or {}
        if not isinstance(grants, dict):
            raise ToolDenied("mcp_grants must be an object")
        tools = grants.get(adapter) or []
        if not isinstance(tools, list) or tool not in tools:
            raise ToolDenied(f"MCP tool not granted by Mission Order: {adapter}/{tool}")
        spec = self.mcp.registry.get(adapter)
        if spec is None:
            raise ToolDenied(f"MCP adapter is not pre-registered by host policy: {adapter}")
        if tool in spec.mutating_tools:
            self._allowed(order, "mcp_mutate")
            if order.mode not in {MissionMode.execute, MissionMode.repair}:
                raise ToolDenied(f"{order.mode.value} mode cannot invoke mutating MCP tool")
        try:
            return self.mcp.call(
                adapter, tool, arguments,
                allow_mutation=("mcp_mutate" in order.allowed_actions),
                timeout=max(1, min(30, int(order.parameters.get("mcp_timeout_seconds", 10)))),
            )
        except (MCPError, TimeoutError) as exc:
            if isinstance(exc, TimeoutError):
                raise
            raise ToolDenied(str(exc)) from exc
