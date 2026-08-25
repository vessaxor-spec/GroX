from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .credential_binding import ConfiguredCredentialBinding
from .secret_awareness import SecretAliasAwareness
from .tools.secrets import SecretBroker


class ConfiguredCredentialAliasAvailability:
    """Compose configured remote credential binding with exact alias availability.

    This surface is intentionally secret-blind. It reuses the already-qualified
    configured credential binding and exact-alias awareness seams, preserving
    the configured cognition resource identity while checking only whether the
    bound alias is represented in the already-injected memory-only broker.

    Alias membership is not credential validity, readiness, fitness, selection,
    observation, provider binding, or successful cognition. No secret value is
    inspected or materialized and no network, provider, cognition, or Mission
    activity occurs.
    """

    schema = "grox-configured-credential-alias-availability-v1"

    def __init__(self, config: Mapping[str, Any], broker: SecretBroker):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(broker, SecretBroker):
            raise TypeError("broker must be a SecretBroker")
        self._config = dict(config)
        self._alias_awareness = SecretAliasAwareness(broker)

    def _base(
        self,
        *,
        status: str,
        resources: list[dict[str, Any]],
        broker_consulted: bool = False,
        alias_checked: bool = False,
    ) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "status": status,
            "resources": resources,
            "secret_broker_consulted": bool(broker_consulted),
            "secret_alias_availability_checked": bool(alias_checked),
            "secret_materialized": False,
            "credential_inspected": False,
            "credential_validated": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }

    def inventory(self) -> dict[str, Any]:
        binding = ConfiguredCredentialBinding(self._config).inventory()
        resources = binding.get("resources") or []
        if binding.get("status") != "ok" or len(resources) != 1:
            return self._base(status=str(binding.get("status") or "unbound"), resources=[])

        bound = resources[0]
        alias = bound.get("credential_alias")
        if not isinstance(alias, str) or not alias:
            return self._base(status="invalid_binding", resources=[])

        availability = self._alias_awareness.inspect(alias)
        alias_available = availability.get("available") is True

        item = {
            "resource_id": bound["resource_id"],
            "resource_type": "configured_cognition_credential_alias_availability",
            "provider_kind": bound["provider_kind"],
            "model": bound["model"],
            "endpoint": bound["endpoint"],
            "credential_alias": alias,
            "credential_binding_configured": True,
            "credential_alias_available": alias_available,
            "discovered": True,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "secret_broker_consulted": True,
            "secret_alias_availability_checked": True,
            "secret_materialized": False,
            "credential_inspected": False,
            "credential_validated": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }
        return self._base(
            status="ok",
            resources=[item],
            broker_consulted=True,
            alias_checked=True,
        )
