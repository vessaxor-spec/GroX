from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from urllib.parse import urlsplit


class PolicyError(PermissionError):
    pass


def normalize_origin(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise PolicyError(f"unsupported or incomplete origin: {value}")
    if parsed.username or parsed.password:
        raise PolicyError("credentials in URL authority are forbidden")
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower()
    port = parsed.port
    default = 80 if scheme == "http" else 443
    if port is None or port == default:
        return f"{scheme}://{host}"
    return f"{scheme}://{host}:{port}"


@dataclass(frozen=True, slots=True)
class GatewayPolicy:
    workspace_enabled: bool = True
    network_enabled: bool = True
    browser_enabled: bool = True
    mcp_enabled: bool = True
    allowed_origins: frozenset[str] = field(default_factory=frozenset)
    max_response_bytes: int = 262_144
    network_timeout_seconds: int = 10
    browser_timeout_seconds: int = 20
    workspace_timeout_seconds: int = 15
    workspace_memory_bytes: int = 268_435_456
    workspace_file_bytes: int = 16_777_216
    workspace_docker_image: str | None = None
    browser_docker_image: str | None = None
    browser_docker_seccomp_profile: str | None = None

    @classmethod
    def from_file(cls, path: Path, *, extra_allowed_origins: tuple[str, ...] | list[str] = ()) -> "GatewayPolicy":
        raw: dict = {}
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
        network = raw.get("network") or {}
        browser = raw.get("browser") or {}
        workspace = raw.get("workspace") or {}
        mcp = raw.get("mcp") or {}
        origins = set()
        for origin in list(network.get("allowed_origins") or []) + list(extra_allowed_origins):
            origins.add(normalize_origin(origin))
        return cls(
            workspace_enabled=bool(workspace.get("enabled", True)),
            network_enabled=bool(network.get("enabled", True)),
            browser_enabled=bool(browser.get("enabled", True)),
            mcp_enabled=bool(mcp.get("enabled", True)),
            allowed_origins=frozenset(origins),
            max_response_bytes=max(1, min(int(network.get("max_response_bytes", 262_144)), 2_000_000)),
            network_timeout_seconds=max(1, min(int(network.get("timeout_seconds", 10)), 60)),
            browser_timeout_seconds=max(1, min(int(browser.get("timeout_seconds", 20)), 60)),
            workspace_timeout_seconds=max(1, min(int(workspace.get("timeout_seconds", 15)), 60)),
            workspace_memory_bytes=max(64 * 1024 * 1024, min(int(workspace.get("memory_bytes", 268_435_456)), 2 * 1024 * 1024 * 1024)),
            workspace_file_bytes=max(1 * 1024 * 1024, min(int(workspace.get("file_bytes", 16_777_216)), 256 * 1024 * 1024)),
            workspace_docker_image=(str(workspace.get("docker_image") or "").strip() or None),
            browser_docker_image=(str(browser.get("docker_image") or "").strip() or None),
            browser_docker_seccomp_profile=(str(browser.get("docker_seccomp_profile") or "").strip() or None),
        )
