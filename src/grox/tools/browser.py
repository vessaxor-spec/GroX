from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile

from .policy import GatewayPolicy
from .workspace import docker_backend_available, namespace_backend_available


class BrowserUnavailable(PermissionError):
    pass


class BrowserRuntime:
    """Run offline Chromium rendering inside one qualified isolation boundary."""

    def __init__(self, vessel_root: Path, policy: GatewayPolicy):
        self.root = vessel_root.resolve()
        self.policy = policy

    def capture(self, html: str, mission_id: str, order_id: str) -> dict:
        capture_dir = self.root / "configs/state/browser" / mission_id / order_id
        capture_dir.mkdir(parents=True, exist_ok=True)
        screenshot = capture_dir / "capture.png"
        with tempfile.TemporaryDirectory(prefix="grox-browser-") as td:
            scratch = Path(td)
            worker_shot = scratch / "capture.png"
            request = {
                "html": html,
                "timeout_ms": self.policy.browser_timeout_seconds * 1000,
                "screenshot": str(worker_shot),
            }
            argv, env, backend, worker_identity, isolation, image_id = self._command(scratch, request)
            proc = subprocess.Popen(
                argv,
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=scratch,
                env=env,
                start_new_session=True,
            )
            try:
                stdout, stderr = proc.communicate(
                    json.dumps(request), timeout=self.policy.browser_timeout_seconds + 10
                )
            except subprocess.TimeoutExpired as exc:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
                raise TimeoutError(
                    f"browser capture exceeded {self.policy.browser_timeout_seconds}s"
                ) from exc
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if proc.returncode != 0:
                raise BrowserUnavailable(f"browser worker failed: {stderr[-2000:]}")
            if not worker_shot.exists():
                raise BrowserUnavailable("browser worker returned without screenshot evidence")
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise BrowserUnavailable("browser worker returned invalid evidence") from exc
            shot = worker_shot.read_bytes()
        screenshot.write_bytes(shot)
        result.update({
            "screenshot": str(screenshot.relative_to(self.root)),
            "screenshot_sha256": hashlib.sha256(shot).hexdigest(),
            "screenshot_bytes": len(shot),
            "worker_identity": worker_identity,
            "browser_backend": backend,
            "browser_image_id": image_id,
            "browser_isolation": isolation,
            "browser_network": "disabled_after_gateway_fetch",
        })
        return result

    def _command(self, scratch: Path, request: dict) -> tuple[list[str], dict[str, str] | None, str, str, list[str], str | None]:
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
        if unshare and namespace_backend_available():
            request["outer_namespace"] = True
            return (
                [
                    unshare, "--user", "--map-root-user", "--pid", "--fork", "--net",
                    sys.executable, "-m", "grox.tools.browser_worker",
                ],
                env,
                "namespace",
                "user_namespace_root",
                [
                    "user_namespace", "pid_namespace", "network_namespace",
                    "playwright_request_abort", "offline_gateway_content",
                ],
                None,
            )

        docker = shutil.which("docker")
        image = self.policy.browser_docker_image
        if not (docker and image and docker_backend_available(image)):
            raise BrowserUnavailable(
                "browser capture requires either usable user/PID/network namespaces or a pre-provisioned governed Docker browser image"
            )
        if os.getuid() == 0:
            raise BrowserUnavailable(
                "Docker browser fallback requires a non-root host user so ephemeral scratch ownership remains host-recoverable"
            )
        inspect = subprocess.run(
            [docker, "image", "inspect", "--format", "{{.Id}}", image],
            text=True,
            capture_output=True,
            timeout=5,
        )
        if inspect.returncode != 0 or not inspect.stdout.strip():
            raise BrowserUnavailable("configured browser Docker image is not pre-provisioned")
        request["outer_namespace"] = False
        request["outer_container"] = True
        request["screenshot"] = "/work/capture.png"
        return (
            [
                docker, "run", "--rm", "-i", "--init", "--pull", "never",
                "--network", "none",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "--security-opt", "seccomp=builtin",
                "--user", f"{os.getuid()}:{os.getgid()}",
                "--read-only",
                "--pids-limit", "256",
                "--memory", "1073741824",
                "--memory-swap", "1073741824",
                "--cpus", "1.0",
                "--ulimit", "nofile=1024:1024",
                "--shm-size", "268435456",
                "--tmpfs", "/tmp:rw,nosuid,nodev,size=134217728",
                "--mount", f"type=bind,src={scratch},dst=/work,bind-propagation=rprivate",
                "--workdir", "/work",
                "--env", "HOME=/work",
                "--env", "TMPDIR=/tmp",
                "--env", "LANG=C.UTF-8",
                "--env", "LC_ALL=C.UTF-8",
                image,
            ],
            None,
            "docker",
            f"docker_host_user:{os.getuid()}:{os.getgid()}",
            [
                "docker_container", "docker_network_none", "capabilities_dropped",
                "no_new_privileges", "read_only_root", "docker_builtin_seccomp",
                "outer_container_sandbox", "playwright_request_abort",
                "offline_gateway_content", "host_resolver_block", "dead_proxy",
            ],
            inspect.stdout.strip(),
        )
