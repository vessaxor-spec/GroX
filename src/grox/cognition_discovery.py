from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import os
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit


_LEGACY_NONSECRET_ENV_KEYS = (
    "GROX_REASONER_PROVIDER",
    "GROX_REASONER_MODEL",
    "GROX_REASONER_ENDPOINT",
    "GROX_REASONER_CREDENTIAL_ALIAS",
)
_CATALOG_ENV_KEY = "GROX_REASONER_CATALOG_JSON"
_NONSECRET_ENV_KEYS = (*_LEGACY_NONSECRET_ENV_KEYS, _CATALOG_ENV_KEY)
_CATALOG_ALLOWED_FIELDS = frozenset({"provider_kind", "model", "endpoint", "credential_alias"})
_MAX_CATALOG_ENTRIES = 8
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


def _safe_credential_alias(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.:@-]{1,128}", value):
        return None
    return value


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

    @staticmethod
    def _catalog_entry_config(entry: Any) -> dict[str, str] | None:
        if not isinstance(entry, Mapping):
            return None
        if set(entry) - _CATALOG_ALLOWED_FIELDS:
            return None

        provider_raw = entry.get("provider_kind")
        if not isinstance(provider_raw, str):
            return None
        provider_kind = provider_raw.strip().lower()
        if provider_kind not in _SUPPORTED_PROVIDER_KINDS:
            return None

        model = _safe_identity(entry.get("model"))
        if model is None:
            return None

        config = {
            "GROX_REASONER_PROVIDER": provider_kind,
            "GROX_REASONER_MODEL": model,
        }
        alias_raw = entry.get("credential_alias")
        alias = _safe_credential_alias(alias_raw)
        if alias_raw is not None and alias is None:
            return None

        if provider_kind == "openai":
            endpoint = _safe_endpoint(entry.get("endpoint"))
            if endpoint is None:
                return None
            config["GROX_REASONER_ENDPOINT"] = endpoint
            if alias is not None:
                config["GROX_REASONER_CREDENTIAL_ALIAS"] = alias
        else:
            if entry.get("endpoint") is not None or alias_raw is not None:
                return None

        return config

    def _catalog_configs(self) -> tuple[str, tuple[dict[str, str], ...]]:
        raw = self._config.get(_CATALOG_ENV_KEY)
        if not isinstance(raw, str) or not raw:
            return "unconfigured", ()

        if any(self._config.get(key) for key in _LEGACY_NONSECRET_ENV_KEYS):
            return "ambiguous", ()
        if len(raw) > 32_768:
            return "invalid_catalog", ()

        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError, ValueError):
            return "invalid_catalog", ()
        if (
            not isinstance(payload, list)
            or isinstance(payload, (str, bytes))
            or not 1 <= len(payload) <= _MAX_CATALOG_ENTRIES
        ):
            return "invalid_catalog", ()

        normalized: list[dict[str, str]] = []
        resource_ids: set[str] = set()
        for entry in payload:
            config = self._catalog_entry_config(entry)
            if config is None:
                return "invalid_catalog", ()
            provider_kind = config["GROX_REASONER_PROVIDER"]
            model = config["GROX_REASONER_MODEL"]
            endpoint = config.get("GROX_REASONER_ENDPOINT")
            resource_id = _resource_id(
                provider_kind=provider_kind,
                model=model,
                endpoint=endpoint,
            )
            if resource_id in resource_ids:
                return "invalid_catalog", ()
            resource_ids.add(resource_id)
            normalized.append(config)
        return "ok", tuple(normalized)

    def declared_configs(self) -> tuple[dict[str, str], ...]:
        """Return normalized non-secret declarations for internal bounded composition.

        Credential aliases may be present because alias names are non-secret
        identity metadata. Secret values are never read or returned here.
        """
        if self._config.get(_CATALOG_ENV_KEY):
            status, configs = self._catalog_configs()
            return tuple(dict(item) for item in configs) if status == "ok" else ()

        raw_provider = self._config.get("GROX_REASONER_PROVIDER", "")
        provider_kind = raw_provider.strip().lower()
        if not provider_kind or provider_kind in {"none", "off", "disabled"}:
            return ()
        if provider_kind not in _SUPPORTED_PROVIDER_KINDS:
            return ()

        model = _safe_identity(self._config.get("GROX_REASONER_MODEL"))
        if model is None:
            return ()

        config = {
            "GROX_REASONER_PROVIDER": provider_kind,
            "GROX_REASONER_MODEL": model,
        }
        if provider_kind == "openai":
            endpoint = _safe_endpoint(
                self._config.get("GROX_REASONER_ENDPOINT", _DEFAULT_OPENAI_ENDPOINT)
            )
            if endpoint is None:
                return ()
            config["GROX_REASONER_ENDPOINT"] = endpoint
            alias_raw = self._config.get("GROX_REASONER_CREDENTIAL_ALIAS")
            if alias_raw:
                alias = _safe_credential_alias(alias_raw)
                if alias is None:
                    return ()
                config["GROX_REASONER_CREDENTIAL_ALIAS"] = alias
        return (config,)

    def inventory(self) -> dict[str, Any]:
        if self._config.get(_CATALOG_ENV_KEY):
            status, configs = self._catalog_configs()
            if status != "ok":
                return self._base_inventory(status=status, resources=[])
            resources = [
                self._resource(
                    provider_kind=config["GROX_REASONER_PROVIDER"],
                    model=config["GROX_REASONER_MODEL"],
                    endpoint=config.get("GROX_REASONER_ENDPOINT"),
                )
                for config in configs
            ]
            result = self._base_inventory(status="ok", resources=resources)
            result["configuration_source"] = "explicit_catalog"
            result["catalog_entry_count"] = len(resources)
            return result

        raw_provider = self._config.get("GROX_REASONER_PROVIDER", "")
        provider_kind = raw_provider.strip().lower()
        if not provider_kind or provider_kind in {"none", "off", "disabled"}:
            return self._base_inventory(status="unconfigured", resources=[])
        if provider_kind not in _SUPPORTED_PROVIDER_KINDS:
            return self._base_inventory(status="unsupported", resources=[])

        configs = self.declared_configs()
        if len(configs) != 1:
            return self._base_inventory(status="incomplete", resources=[])
        config = configs[0]
        resource = self._resource(
            provider_kind=config["GROX_REASONER_PROVIDER"],
            model=config["GROX_REASONER_MODEL"],
            endpoint=config.get("GROX_REASONER_ENDPOINT"),
        )
        result = self._base_inventory(status="ok", resources=[resource])
        result["configuration_source"] = "legacy_single"
        result["catalog_entry_count"] = 1
        return result
