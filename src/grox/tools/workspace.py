from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess


class WorkspaceUnavailable(RuntimeError):
    pass


def namespace_backend_available() -> bool:
    """Return True only when the host can create the full A5 namespace set."""
    unshare = shutil.which("unshare")
    if not unshare:
        return False
    try:
        cp = subprocess.run(
            [unshare, "--user", "--map-root-user", "--pid", "--fork", "--net", "/bin/sh", "-c", "true"],
            text=True,
            capture_output=True,
            timeout=3,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return cp.returncode == 0


def docker_backend_available(image: str | None = None) -> bool:
    """Return True only for a usable daemon and, when supplied, a pre-provisioned image."""
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        cp = subprocess.run(
            [docker, "info", "--format", "{{.ServerVersion}}"],
            text=True,
            capture_output=True,
            timeout=5,
        )
        if cp.returncode != 0 or not cp.stdout.strip():
            return False
        if image:
            cp = subprocess.run(
                [docker, "image", "inspect", image],
                text=True,
                capture_output=True,
                timeout=5,
            )
            if cp.returncode != 0:
                return False
    except (OSError, subprocess.TimeoutExpired):
        return False
    return True


class IsolatedWorkspace:
    """Host-selected A5 shell isolation with fail-closed backend selection.

    Namespace isolation is preferred when the host permits user/PID/network
    namespaces. A pre-provisioned Docker image is the governed fallback. The
    Docker path never pulls images implicitly.
    """

    def __init__(
        self,
        base: Path,
        *,
        timeout_seconds: int,
        memory_bytes: int,
        file_bytes: int,
        docker_image: str | None = None,
    ):
        self.base = base.resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.memory_bytes = memory_bytes
        self.file_bytes = file_bytes
        self.docker_image = docker_image
        self.unshare = shutil.which("unshare")
        self.chroot = shutil.which("chroot")
        self.prlimit = shutil.which("prlimit")
        self.shell = shutil.which("dash") or shutil.which("sh")
        self.docker = shutil.which("docker")

        if self.unshare and self.chroot and self.prlimit and self.shell and namespace_backend_available():
            self.backend = "namespace"
        elif docker_image and docker_backend_available(docker_image):
            self.backend = "docker"
        else:
            raise WorkspaceUnavailable(
                "no qualified A5 workspace isolation backend: usable user/PID/network namespaces "
                "or a usable Docker daemon with the host-policy image pre-provisioned is required"
            )

    @staticmethod
    def _stdin_script(script: str, env: dict[str, str] | None) -> str:
        lines = ["set -eu"]
        for name, value in sorted((env or {}).items()):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise ValueError(f"invalid workspace environment variable: {name}")
            # Secret-bearing values travel over stdin, not Docker Config.Env or
            # the host process environment/argv.
            lines.append(f"export {name}={shlex.quote(value)}")
        lines.append(script)
        return "\n".join(lines) + "\n"

    def _copy_binary_and_libs(self, binary: Path, rootfs: Path, target: str) -> None:
        dest = rootfs / target.lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(binary, dest)
        cp = subprocess.run(["ldd", str(binary)], text=True, capture_output=True, timeout=5)
        if cp.returncode != 0:
            raise WorkspaceUnavailable(f"cannot resolve sandbox shell dependencies: {cp.stderr.strip()}")
        libs: set[Path] = set()
        for line in cp.stdout.splitlines():
            match = re.search(r"=>\s+(/\S+)", line)
            if match:
                libs.add(Path(match.group(1)))
                continue
            match = re.match(r"\s*(/\S+)\s+\(", line)
            if match:
                libs.add(Path(match.group(1)))
        for lib in libs:
            if not lib.exists():
                continue
            lib_dest = rootfs / str(lib).lstrip("/")
            lib_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lib, lib_dest)

    def _namespace_run(self, workspace: Path, script: str, env: dict[str, str] | None) -> subprocess.CompletedProcess[str]:
        rootfs = workspace / "rootfs"
        (rootfs / "work").mkdir(parents=True, exist_ok=True)
        self._copy_binary_and_libs(Path(self.shell), rootfs, "/bin/sh")
        run_env = {"PATH": "/bin", "HOME": "/work", "TMPDIR": "/work", "LANG": "C", "LC_ALL": "C"}
        argv = [
            self.prlimit,
            f"--cpu={self.timeout_seconds + 1}:{self.timeout_seconds + 1}",
            f"--as={self.memory_bytes}:{self.memory_bytes}",
            f"--fsize={self.file_bytes}:{self.file_bytes}",
            "--nofile=64:64",
            "--",
            self.unshare, "--user", "--map-root-user", "--pid", "--fork", "--net",
            self.chroot, str(rootfs), "/bin/sh", "-s",
        ]
        return subprocess.run(
            argv,
            input=self._stdin_script(script, env),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            env=run_env,
        )

    def _docker_run(self, workspace: Path, script: str, env: dict[str, str] | None) -> subprocess.CompletedProcess[str]:
        if not self.docker or not self.docker_image:
            raise WorkspaceUnavailable("Docker workspace backend is not configured")
        work = workspace / "work"
        work.mkdir(parents=True, exist_ok=True)
        # No implicit image pull: backend selection already required image inspect.
        # Only the A5-private ephemeral work directory is writable from the container.
        argv = [
            self.docker, "run", "--rm", "-i",
            "--pull", "never",
            "--network", "none",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--read-only",
            "--pids-limit", "64",
            "--memory", str(self.memory_bytes),
            "--memory-swap", str(self.memory_bytes),
            "--cpus", "1.0",
            "--ulimit", f"fsize={self.file_bytes}:{self.file_bytes}",
            "--ulimit", "nofile=64:64",
            "--mount", f"type=bind,src={work},dst=/work,bind-propagation=rprivate",
            "--workdir", "/work",
            "--env", "HOME=/work",
            "--env", "TMPDIR=/work",
            "--env", "LANG=C",
            "--env", "LC_ALL=C",
            self.docker_image,
            "/bin/sh", "-s",
        ]
        cp = subprocess.run(
            argv,
            input=self._stdin_script(script, env),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds + 5,
        )
        if cp.returncode == 125:
            raise WorkspaceUnavailable(f"Docker workspace launch failed: {cp.stderr[-2000:]}")
        return cp

    def run(self, mission_id: str, order_id: str, script: str, *, env: dict[str, str] | None = None) -> dict:
        if not isinstance(script, str) or not script.strip():
            raise ValueError("workspace shell script is required")
        if len(script.encode("utf-8")) > 16_384:
            raise ValueError("workspace shell script exceeds 16 KiB")
        workspace = self.base / mission_id / order_id
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        try:
            try:
                cp = (
                    self._namespace_run(workspace, script, env)
                    if self.backend == "namespace"
                    else self._docker_run(workspace, script, env)
                )
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError(f"isolated workspace exceeded {self.timeout_seconds}s") from exc

            work = workspace / ("rootfs/work" if self.backend == "namespace" else "work")
            files: list[dict] = []
            total_bytes = 0
            for path in sorted(work.rglob("*")):
                if not path.is_file():
                    continue
                raw = path.read_bytes()
                total_bytes += len(raw)
                if total_bytes > self.file_bytes:
                    raise WorkspaceUnavailable("workspace output exceeds host-policy file budget")
                files.append({
                    "path": str(path.relative_to(work)),
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })
                if len(files) >= 100:
                    break
            isolation = (
                ["user_namespace", "pid_namespace", "network_namespace", "chroot", "resource_limits"]
                if self.backend == "namespace"
                else [
                    "docker_container", "docker_network_none", "capabilities_dropped",
                    "no_new_privileges", "read_only_root", "resource_limits",
                ]
            )
            return {
                "workspace": str(workspace.relative_to(self.base)),
                "returncode": cp.returncode,
                "stdout": cp.stdout[-65_536:],
                "stderr": cp.stderr[-65_536:],
                "files": files,
                "isolation_backend": self.backend,
                "isolation": isolation,
                "workspace_retained": False,
            }
        finally:
            # Workspaces are execution sandboxes, not a memory plane.
            shutil.rmtree(workspace, ignore_errors=True)
