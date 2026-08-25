from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

from .cognition_discovery import ConfiguredCognitionDiscovery


_CREDENTIAL_ALIAS_KEY = "GROX_REASONER_CREDENTIAL_ALIAS"
_ALIAS_RE = re.compile(r"^[A-Za-z0-9_.:@-]{1,128}$")


class ConfiguredCredentialBinding:
    """Read-only non-secret binding between configured remote cognition and a secret alias.

    The alias is configuration identity only. This surface never consults a
    SecretBroker, never inspects or materializes secret values, and never
    promotes configuration binding into authorization, readiness, fitness,
    selection, observation, provider binding, or execution.
    """

    schema = "grox-configured-credential-binding-v1"

    def __init__(self, config: Mapping[str, Any]):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        self._config = dict(config)

    def _base(self, *, status: str, resources: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "status": status,
            "resources": resources,
            "secret_broker_consulted": False,
            "secret_alias_availability_checked": False,
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
        discovered = ConfiguredCognitionDiscovery(self._config).inventory()
        resources = discovered.get("resources") or []
        if len(resources) != 1:
            return self._base(status="unbound", resources=[])

        resource = resources[0]
        if resource.get("provider_kind") != "openai":
            return self._base(status="not_applicable", resources=[])

        raw_alias = self._config.get(_CREDENTIAL_ALIAS_KEY)
        if raw_alias is None or raw_alias == "":
            return self._base(status="unbound", resources=[])
        if not isinstance(raw_alias, str) or not _ALIAS_RE.fullmatch(raw_alias):
            return self._base(status="invalid_binding", resources=[])

        item = {
            "resource_id": resource["resource_id"],
            "resource_type": "configured_cognition_credential_binding",
            "provider_kind": resource["provider_kind"],
            "model": resource["model"],
            "endpoint": resource["endpoint"],
            "credential_alias": raw_alias,
            "credential_binding_configured": True,
            "discovered": True,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "secret_broker_consulted": False,
            "secret_alias_availability_checked": False,
            "credential_inspected": False,
            "credential_validated": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }
        return self._base(status="ok", resources=[item])
