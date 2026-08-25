from __future__ import annotations

from collections.abc import Mapping
import hashlib
import os
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit


_NONSECRET_ENV_KEYS = (
    "GROX_REASONER_PROVIDER",
    "GROX_REASONER_MODEL",
    "GROX_REASONER_ENDPOINT",
    "GROX_REASONER_CREDENTIAL_ALIAS",
)
_SUPPORTED_PROVIDER_KINDS = frozenset({"openai", "local-llama-cpp"})
_DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1/responses"


def nonsecret_reasoner_config_from_env() -> dict[str, str]:
    """Return only explicit non-secret reasoning identity configuration.

    Secret values and credential presence remain outside this allowlist. A
    credential *alias name* may be returned as non-secret binding metadata, but
    it does not imply that the alias exists in a broker, contains usable
    material, is valid, or grants any authority/readiness.
    """
    snapshot: dict[str, str] = {}
    for key in _NONSECRET_ENV_KEYS:
        value = os.getenv(key, "")
        if isinstance(value, str) and value.strip():
            snapshot[key] = value.strip()
    return snapshot


def _safe_identity(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > 160:
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.:/ +@-]+", value):
        return None
    return value


def _safe_endpoint(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = urlsplit(value.strip())
        port = parsed.port
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    default_port = 80 if parsed.scheme.lower() == "http" else 443
    netloc = host if port in {None, default_port} else f"{host}:{port}"
    path = parsed.path or "/"
    normalized = urlunsplit((parsed.scheme.lower(), netloc, path, "", ""))
    return normalized if normalized == value.strip() else None


def _resource_id(*, provider_kind: str, model: str, endpoint: str | None) -> str:
    basis = f"{provider_kind}|{model}|{endpoint or ''}"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]
    return f"cognition:configured:{provider_kind}:{digest}"


class ConfiguredCognitionDiscovery:
    """Passive privacy-minimized discovery of supported cognition configuration.

    Discovery reads only an explicit non-secret configuration allowlist. It does
    not construct providers, inspect credentials, touch the network/filesystem,
    load models, invoke cognition, bind resources, select providers, or route.
    Credential-alias metadata is intentionally not exposed on the base resource;
    that binding is handled by a separate awareness surface.
    """

    def __init__(self, config: Mapping[str, Any]):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        self._config = {
            key: value.strip()
            for key in _NONSECRET_ENV_KEYS
            if isinstance((value := config.get(key)), str) and value.strip()
        }

    @staticmethod
    def _base_inventory(*, status: str, resources: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-discovery-v1",
            "status": status,
            "resources": resources,
            "authority_changed": False,
            "auto_activation": False,
            "auto_selection": False,
            "network_invoked": False,
            "credential_inspected": False,
        }

    @staticmethod
    def _resource(*, provider_kind: str, model: str, endpoint: str | None) -> dict[str, Any]:
        return {
            "resource_id": _resource_id(provider_kind=provider_kind, model=model, endpoint=endpoint),
            "resource_type": "configured_cognition",
            "provider_kind": provider_kind,
            "model": model,
            "endpoint": endpoint,
            "discovered": True,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "authority_changed": False,
            "auto_activation": False,
            "auto_selection": False,
        }

    def inventory(self) -> dict[str, Any]:
        raw_provider = self._config.get("GROX_REASONER_PROVIDER", "")
        provider_kind = raw_provider.strip().lower()
        if not provider_kind or provider_kind in {"none", "off", "disabled"}:
            return self._base_inventory(status="unconfigured", resources=[])
        if provider_kind not in _SUPPORTED_PROVIDER_KINDS:
            return self._base_inventory(status="unsupported", resources=[])

        model = _safe_identity(self._config.get("GROX_REASONER_MODEL"))
        if model is None:
            return self._base_inventory(status="incomplete", resources=[])

        endpoint: str | None = None
        if provider_kind == "openai":
            raw_endpoint = self._config.get("GROX_REASONER_ENDPOINT", _DEFAULT_OPENAI_ENDPOINT)
            endpoint = _safe_endpoint(raw_endpoint)
            if endpoint is None:
                return self._base_inventory(status="incomplete", resources=[])

        resource = self._resource(provider_kind=provider_kind, model=model, endpoint=endpoint)
        return self._base_inventory(status="ok", resources=[resource])
