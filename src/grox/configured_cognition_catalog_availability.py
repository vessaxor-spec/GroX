from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .configured_cognition_catalog_binding import ConfiguredCognitionCatalogBinding
from .secret_awareness import SecretAliasAwareness
from .tools.secrets import SecretBroker


class ConfiguredCognitionCatalogCredentialAvailabilityError(RuntimeError):
    """Catalog availability composition detected an internal identity inconsistency."""


class ConfiguredCognitionCatalogCredentialAvailability:
    """Compose catalog credential bindings with exact governed alias availability.

    This surface is secret-blind and read-only. It preserves configured catalog
    declaration order and exact resource identity while consulting only exact
    alias membership in the already-injected memory-only SecretBroker.

    Alias membership is not credential validity, Mission authorization,
    readiness, qualification/fit, selection, routing, observation, provider
    construction, or successful cognition.
    """

    schema = "grox-configured-cognition-catalog-credential-availability-v1"

    def __init__(self, config: Mapping[str, Any], broker: SecretBroker):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(broker, SecretBroker):
            raise TypeError("broker must be a SecretBroker")
        self._config = dict(config)
        self._alias_awareness = SecretAliasAwareness(broker)

    @classmethod
    def _base(
        cls,
        *,
        status: str,
        resources: list[dict[str, Any]],
        configuration_source: str | None = None,
    ) -> dict[str, Any]:
        remote = [item for item in resources if item.get("provider_kind") == "openai"]
        return {
            "schema": cls.schema,
            "status": status,
            "configuration_source": configuration_source,
            "resources": resources,
            "remote_resource_count": len(remote),
            "bound_remote_resource_count": sum(
                item.get("credential_binding_configured") is True for item in remote
            ),
            "available_remote_resource_count": sum(
                item.get("credential_alias_available") is True for item in remote
            ),
            "secret_broker_consulted": any(
                item.get("secret_broker_consulted") is True for item in resources
            ),
            "secret_alias_availability_checked": any(
                item.get("secret_alias_availability_checked") is True
                for item in resources
            ),
            "secret_materialized": False,
            "credential_inspected": False,
            "credential_validated": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "routing_enabled": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }

    @staticmethod
    def _base_item(
        resource: Mapping[str, Any],
        *,
        availability_status: str,
        alias_available: bool | None,
        broker_consulted: bool = False,
        alias_checked: bool = False,
    ) -> dict[str, Any]:
        return {
            "resource_id": resource["resource_id"],
            "resource_type": "configured_cognition_catalog_credential_alias_availability",
            "provider_kind": resource["provider_kind"],
            "model": resource["model"],
            "endpoint": resource["endpoint"],
            "credential_binding_status": resource.get("credential_binding_status"),
            "credential_binding_configured": (
                resource.get("credential_binding_configured") is True
            ),
            "credential_alias_availability_status": availability_status,
            "credential_alias_available": alias_available,
            "discovered": True,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
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
        binding = ConfiguredCognitionCatalogBinding(self._config).inventory()
        resources = binding.get("resources") or []
        status = str(binding.get("status") or "unconfigured")
        configuration_source = binding.get("configuration_source")

        if status not in {"ok", "incomplete_binding", "not_applicable"}:
            return self._base(
                status=status,
                resources=[],
                configuration_source=configuration_source,
            )

        composed: list[dict[str, Any]] = []
        for resource in resources:
            if resource.get("provider_kind") != "openai":
                composed.append(
                    self._base_item(
                        resource,
                        availability_status="not_applicable",
                        alias_available=None,
                    )
                )
                continue

            if resource.get("credential_binding_configured") is not True:
                composed.append(
                    self._base_item(
                        resource,
                        availability_status="unbound",
                        alias_available=False,
                    )
                )
                continue

            alias = resource.get("credential_alias")
            if not isinstance(alias, str) or not alias:
                raise ConfiguredCognitionCatalogCredentialAvailabilityError(
                    "catalog credential binding lacks an exact alias"
                )

            availability = self._alias_awareness.inspect(alias)
            if availability.get("alias") != alias:
                raise ConfiguredCognitionCatalogCredentialAvailabilityError(
                    "secret alias availability identity differs from catalog binding"
                )

            item = self._base_item(
                resource,
                availability_status=(
                    "available" if availability.get("available") is True else "unavailable"
                ),
                alias_available=availability.get("available") is True,
                broker_consulted=True,
                alias_checked=True,
            )
            item["credential_alias"] = alias
            composed.append(item)

        return self._base(
            status=status,
            resources=composed,
            configuration_source=configuration_source,
        )
