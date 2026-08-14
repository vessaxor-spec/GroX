from __future__ import annotations

import re
from typing import Mapping
from ..contracts import MissionOrder


class SecretDenied(PermissionError):
    pass


_ENV_RE = re.compile(r"^[A-Z_][A-Z0-9_]{0,63}$")


class SecretBroker:
    """Memory-only secret broker. Secret values are never persisted by this class."""

    def __init__(self, secrets: Mapping[str, str] | None = None):
        self._secrets = {str(k): str(v) for k, v in (secrets or {}).items()}

    def materialize_env(self, order: MissionOrder, requested: Mapping[str, str] | None) -> tuple[dict[str, str], list[str]]:
        requested = requested or {}
        grants = set(order.parameters.get("secret_grants") or [])
        env: dict[str, str] = {}
        used: list[str] = []
        for env_name, alias in requested.items():
            env_name = str(env_name)
            alias = str(alias)
            if not _ENV_RE.fullmatch(env_name):
                raise SecretDenied(f"invalid secret environment name: {env_name}")
            if alias not in grants:
                raise SecretDenied(f"secret alias not granted by Mission Order: {alias}")
            if alias not in self._secrets:
                raise SecretDenied(f"secret alias unavailable from broker: {alias}")
            env[env_name] = self._secrets[alias]
            used.append(alias)
        return env, sorted(set(used))

    def redact(self, text: str, values: Mapping[str, str] | list[str] | tuple[str, ...]) -> str:
        secrets = list(values.values()) if isinstance(values, Mapping) else list(values)
        out = text
        for value in sorted((x for x in secrets if x), key=len, reverse=True):
            out = out.replace(value, "[REDACTED]")
        return out
