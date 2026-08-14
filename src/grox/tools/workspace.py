from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess


class WorkspaceUnavailable(RuntimeError):
    pass


class IsolatedWorkspace:
    """Chrooted user/PID/network namespace for bounded shell execution."""

    def __init__(self, base: Path, *, timeout_seconds: int, memory_bytes: int, file_bytes: int):
        self.base = base.resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.memory_bytes = memory_bytes
        self.file_bytes = file_bytes
        self.unshare = shutil.which("unshare")
        self.chroot = shutil.which("chroot")
        self.prlimit = shutil.which("prlimit")
        self.shell = shutil.which("dash") or shutil.which("sh")
        if not self.unshare or not self.chroot or not self.prlimit or not self.shell:
            raise WorkspaceUnavailable("A5 workspace requires unshare, chroot, prlimit, and dash/sh")

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

    def run(self, mission_id: str, order_id: str, script: str, *, env: dict[str, str] | None = None) -> dict:
        if not isinstance(script, str) or not script.strip():
            raise ValueError("workspace shell script is required")
        if len(script.encode("utf-8")) > 16_384:
            raise ValueError("workspace shell script exceeds 16 KiB")
        workspace = self.base / mission_id / order_id
        rootfs = workspace / "rootfs"
        if rootfs.exists():
            shutil.rmtree(rootfs)
        (rootfs / "work").mkdir(parents=True, exist_ok=True)
        self._copy_binary_and_libs(Path(self.shell), rootfs, "/bin/sh")
        run_env = {"PATH": "/bin", "HOME": "/work", "TMPDIR": "/work", "LANG": "C", "LC_ALL": "C"}
        run_env.update(env or {})
        argv = [
            self.prlimit,
            f"--cpu={self.timeout_seconds + 1}:{self.timeout_seconds + 1}",
            f"--as={self.memory_bytes}:{self.memory_bytes}",
            f"--fsize={self.file_bytes}:{self.file_bytes}",
            "--nofile=64:64",
            "--",
            self.unshare, "--user", "--map-root-user", "--pid", "--fork", "--net",
            self.chroot, str(rootfs), "/bin/sh", "-c", script,
        ]
        try:
            cp = subprocess.run(
                argv, text=True, capture_output=True, timeout=self.timeout_seconds,
                env=run_env,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"isolated workspace exceeded {self.timeout_seconds}s") from exc
        files: list[dict] = []
        work = rootfs / "work"
        for path in sorted(work.rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            files.append({
                "path": str(path.relative_to(work)),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
            if len(files) >= 100:
                break
        result = {
            "workspace": str(workspace.relative_to(self.base)),
            "returncode": cp.returncode,
            "stdout": cp.stdout[-65_536:],
            "stderr": cp.stderr[-65_536:],
            "files": files,
            "isolation": ["user_namespace", "pid_namespace", "network_namespace", "chroot", "resource_limits"],
            "workspace_retained": False,
        }
        # Workspaces are execution sandboxes, not a memory plane. Evidence retains
        # hashes/metadata while shell output and any injected secret material are
        # removed from disk after normal completion.
        shutil.rmtree(workspace, ignore_errors=True)
        return result
