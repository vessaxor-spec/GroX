from __future__ import annotations

from .tools.secrets import SecretBroker


class SecretAliasAwareness:
    """Read-only awareness of one exact governed secret alias.

    This surface is intentionally secret-blind. It reports only whether the
    exact alias is represented by the already-injected memory-only broker.
    It never materializes, validates, hashes, persists, logs, or transforms a
    secret value and never promotes availability into authority or readiness.
    """

    schema = "grox-secret-alias-awareness-v1"

    def __init__(self, broker: SecretBroker):
        self._broker = broker

    def inspect(self, alias: str) -> dict[str, object]:
        if not isinstance(alias, str) or not alias or alias != alias.strip():
            raise ValueError("secret alias must be an exact non-empty string")

        available = self._broker.has_alias(alias)
        return {
            "schema": self.schema,
            "alias": alias,
            "available": available,
            "status": "available" if available else "unavailable",
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "secret_materialized": False,
            "credential_validated": False,
            "environment_scanned": False,
            "filesystem_scanned": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }
