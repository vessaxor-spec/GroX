from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .native_model_runtime import HardwareRuntimeProfile, ModelManifest, ModelRuntimeError


_VERSION_RE = re.compile(r"version:\s*(?P<version>\d+)\s*\([`']?(?P<commit>[0-9a-fA-F]+)[`']?\)")


@dataclass(frozen=True, slots=True)
class LlamaCppHandle:
    model_id: str
    artifact_path: Path


class LlamaCppCLIBackend:
    """Pinned local llama.cpp process backend.

    The backend never downloads models or executables, never searches PATH, and
    never starts a network server. An explicit local executable and an already
    verified local GGUF artifact are required before invocation.
    """

    name = "llama.cpp-cli-b10218"

    def __init__(
        self,
        executable: Path | str,
        *,
        expected_version: int = 10218,
        expected_commit_prefix: str = "de69995",
        context_tokens: int = 4096,
        max_output_tokens: int = 512,
        max_threads: int = 4,
        timeout_seconds: int = 120,
        max_output_chars: int = 65536,
        scratch_root: Path | str | None = None,
    ):
        path = Path(executable).expanduser()
        if not path.is_absolute():
            raise ValueError("llama.cpp executable path must be explicit and absolute")
        self.executable = path.resolve()
        if not isinstance(expected_version, int) or isinstance(expected_version, bool) or expected_version <= 0:
            raise ValueError("expected_version must be a positive integer")
        commit = expected_commit_prefix.strip().lower()
        if not commit or not re.fullmatch(r"[0-9a-f]+", commit):
            raise ValueError("expected_commit_prefix must be hexadecimal")
        if context_tokens < 512 or context_tokens > 32768:
            raise ValueError("context_tokens must be between 512 and 32768")
        if max_output_tokens < 1 or max_output_tokens > 2048:
            raise ValueError("max_output_tokens must be between 1 and 2048")
        if max_threads < 1 or max_threads > 64:
            raise ValueError("max_threads must be between 1 and 64")
        if timeout_seconds < 1 or timeout_seconds > 900:
            raise ValueError("timeout_seconds must be between 1 and 900")
        if max_output_chars < 1024 or max_output_chars > 1024 * 1024:
            raise ValueError("max_output_chars must be between 1024 and 1048576")
        self.expected_version = expected_version
        self.expected_commit_prefix = commit
        self.context_tokens = context_tokens
        self.max_output_tokens = max_output_tokens
        self.max_threads = max_threads
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars
        self.scratch_root = Path(scratch_root).expanduser().resolve() if scratch_root is not None else None
        self._version_cache: tuple[bool, str] | None = None
        self.last_command: tuple[str, ...] | None = None

    @staticmethod
    def _sanitized_environment() -> dict[str, str]:
        denied_exact = {
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
            "http_proxy", "https_proxy", "all_proxy", "no_proxy",
        }
        environment: dict[str, str] = {}
        for key, value in os.environ.items():
            upper = key.upper()
            if key in denied_exact or upper.startswith("LLAMA_") or upper.startswith("HF_") or upper.startswith("HUGGING_FACE_"):
                continue
            environment[key] = value
        environment["NO_COLOR"] = "1"
        environment["TERM"] = "dumb"
        return environment

    def _probe_version(self) -> tuple[bool, str]:
        if self._version_cache is not None:
            return self._version_cache
        if not self.executable.is_file():
            self._version_cache = (False, f"llama.cpp executable is unavailable: {self.executable}")
            return self._version_cache
        if not os.access(self.executable, os.X_OK):
            self._version_cache = (False, f"llama.cpp executable is not executable: {self.executable}")
            return self._version_cache
        try:
            completed = subprocess.run(
                [str(self.executable), "--version"],
                capture_output=True,
                text=True,
                timeout=min(10, self.timeout_seconds),
                check=False,
                env=self._sanitized_environment(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._version_cache = (False, f"llama.cpp version probe failed: {type(exc).__name__}: {exc}")
            return self._version_cache
        version_text = (completed.stdout + "\n" + completed.stderr).strip()
        if completed.returncode != 0:
            self._version_cache = (False, f"llama.cpp version probe returned {completed.returncode}")
            return self._version_cache
        match = _VERSION_RE.search(version_text)
        if match is None:
            self._version_cache = (False, "llama.cpp version output did not match the pinned contract")
            return self._version_cache
        version = int(match.group("version"))
        commit = match.group("commit").lower()
        if version != self.expected_version or not commit.startswith(self.expected_commit_prefix):
            self._version_cache = (
                False,
                "llama.cpp build mismatch: "
                f"expected={self.expected_version}/{self.expected_commit_prefix}, observed={version}/{commit}",
            )
            return self._version_cache
        self._version_cache = (True, f"pinned llama.cpp build verified: {version}/{commit}")
        return self._version_cache

    def supports(
        self, manifest: ModelManifest, hardware: HardwareRuntimeProfile
    ) -> tuple[bool, str]:
        del hardware
        if manifest.backend != self.name:
            return False, f"manifest backend does not match pinned llama.cpp backend: {manifest.backend}"
        if manifest.model_format.lower() != "gguf":
            return False, f"llama.cpp backend requires GGUF, got: {manifest.model_format}"
        if "gorxu" not in manifest.placements:
            return False, "local reasoning seed is not registered for GorXu cognition placement"
        return self._probe_version()

    def load(self, manifest: ModelManifest, artifact_path: Path) -> LlamaCppHandle:
        supported, reason = self.supports(manifest, HardwareRuntimeProfile.discover())
        if not supported:
            raise ModelRuntimeError(reason)
        path = artifact_path.expanduser().resolve()
        if not path.is_file():
            raise ModelRuntimeError(f"GGUF artifact is unavailable: {path}")
        return LlamaCppHandle(model_id=manifest.model_id, artifact_path=path)

    def invoke(self, handle: LlamaCppHandle, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(handle, LlamaCppHandle):
            raise ModelRuntimeError("llama.cpp handle is invalid")
        prompt = payload.get("prompt")
        json_schema = payload.get("json_schema")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ModelRuntimeError("llama.cpp invocation requires a non-empty prompt")
        if not isinstance(json_schema, Mapping):
            raise ModelRuntimeError("llama.cpp invocation requires a JSON-schema mapping")
        if len(prompt) > 131072:
            raise ModelRuntimeError("llama.cpp prompt exceeds the bounded character ceiling")

        schema_text = json.dumps(dict(json_schema), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        threads = min(self.max_threads, max(1, int(os.cpu_count() or 1)))
        temp_dir = str(self.scratch_root) if self.scratch_root is not None else None
        prompt_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix="grox-llama-prompt-",
                suffix=".txt",
                dir=temp_dir,
                delete=False,
            ) as prompt_file:
                prompt_file.write(prompt)
                prompt_file.flush()
                os.fsync(prompt_file.fileno())
                prompt_path = Path(prompt_file.name)
            os.chmod(prompt_path, 0o600)

            command = [
                str(self.executable),
                "-m", str(handle.artifact_path),
                "-f", str(prompt_path),
                "-j", schema_text,
                "--single-turn",
                "--no-display-prompt",
                "--no-warmup",
                "--temp", "0",
                "--seed", "1",
                "--ctx-size", str(self.context_tokens),
                "-n", str(self.max_output_tokens),
                "-t", str(threads),
                "--fit", "off",
                "-ngl", "0",
            ]
            self.last_command = tuple(command)
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                    env=self._sanitized_environment(),
                )
            except subprocess.TimeoutExpired as exc:
                raise ModelRuntimeError(f"llama.cpp inference timed out after {self.timeout_seconds}s") from exc
            except OSError as exc:
                raise ModelRuntimeError(f"llama.cpp inference process failed to start: {exc}") from exc
            if completed.returncode != 0:
                detail = completed.stderr.strip()[:2000]
                raise ModelRuntimeError(
                    f"llama.cpp inference returned {completed.returncode}: {detail}"
                )
            text = completed.stdout.strip()
            if not text:
                raise ModelRuntimeError("llama.cpp inference returned no stdout")
            if len(text) > self.max_output_chars:
                raise ModelRuntimeError("llama.cpp inference output exceeded the bounded character ceiling")
            return {
                "text": text,
                "backend_version": self.expected_version,
                "backend_commit_prefix": self.expected_commit_prefix,
                "network_used": False,
                "authority_changed": False,
                "cpu_only": True,
            }
        finally:
            if prompt_path is not None:
                prompt_path.unlink(missing_ok=True)

    def unload(self, handle: LlamaCppHandle) -> None:
        if not isinstance(handle, LlamaCppHandle):
            raise ModelRuntimeError("llama.cpp handle is invalid")
