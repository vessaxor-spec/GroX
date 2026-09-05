from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .cognition_discovery import ConfiguredCognitionDiscovery
from .configured_credential_availability import ConfiguredCredentialAliasAvailability
from .tools.secrets import SecretBroker


class ConfiguredCognitionCatalogAvailabilityError(RuntimeError):
    """Catalog availability composition detected an internal identity inconsistency."""


class ConfiguredCognitionCatalogAvailability:
    """Report exact configured credential-alias availability across a cognition catalog.

    This surface may ask the injected SecretBroker only whether one exact alias
    exists. It never materializes or inspects secret values and never performs
    network/provider/cognition activity or changes authority/readiness/selection.
    """

    schema = "grox-configured-cognition-catalog-availability-v1"

    def __init__(self, config: Mapping[str, Any], broker: SecretBroker):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(broker, SecretBroker):
            raise TypeError("broker must be a SecretBroker")
        self._config = dict(config)
        self._broker = broker

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
                item.get("secret_broker_consulted") is True for item in remote
            ),
            "secret_alias_availability_checked": any(
                item.get("secret_alias_availability_checked") is True for item in remote
            ),
            "secret_materialized": False,
            "credential_inspected": False,
            "credential_validated": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "ready": False,
            "qualified_fit": False,
            "authorized": False,
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
        binding_status: str,
        availability_status: str,
    ) -> dict[str, Any]:
        return {
            "resource_id": resource["resource_id"],
            "resource_type": "configured_cognition_catalog_credential_availability",
            "provider_kind": resource["provider_kind"],
            "model": resource["model"],
            "endpoint": resource["endpoint"],
            "credential_binding_status": binding_status,
            "credential_binding_configured": False,
            "credential_alias_availability_status": availability_status,
            "credential_alias_available": False,
            "discovered": True,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "secret_broker_consulted": False,
            "secret_alias_availability_checked": False,
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

    @staticmethod
    def _availability_matches_resource(
        availability: Mapping[str, Any],
        resource: Mapping[str, Any],
    ) -> bool:
        return (
            availability.get("resource_id") == resource.get("resource_id")
            and availability.get("provider_kind") == resource.get("provider_kind")
            and availability.get("model") == resource.get("model")
            and availability.get("endpoint") == resource.get("endpoint")
        )

    def inventory(self) -> dict[str, Any]:
        discovery = ConfiguredCognitionDiscovery(self._config)
        discovered = discovery.inventory()
        resources = discovered.get("resources") or []
        if discovered.get("status") != "ok":
            return self._base(
                status=str(discovered.get("status") or "unconfigured"),
                resources=[],
                configuration_source=discovered.get("configuration_source"),
            )

        declarations = discovery.declared_configs()
        if len(declarations) != len(resources):
            raise ConfiguredCognitionCatalogAvailabilityError(
                "configured cognition catalog declaration/resource cardinality mismatch"
            )

        composed: list[dict[str, Any]] = []
        remote_incomplete = False
        for resource, declaration in zip(resources, declarations, strict=True):
            if resource.get("provider_kind") != "openai":
                composed.append(
                    self._base_item(
                        resource,
                        binding_status="not_applicable",
                        availability_status="not_applicable",
                    )
                )
                continue

            availability_inventory = ConfiguredCredentialAliasAvailability(
                declaration,
                self._broker,
            ).inventory()
            available_resources = availability_inventory.get("resources") or []
            if availability_inventory.get("status") != "ok" or len(available_resources) != 1:
                remote_incomplete = True
                composed.append(
                    self._base_item(
                        resource,
                        binding_status="unbound",
                        availability_status="not_checked",
                    )
                )
                continue

            available = available_resources[0]
            if not self._availability_matches_resource(available, resource):
                raise ConfiguredCognitionCatalogAvailabilityError(
                    "configured credential availability identity differs from catalog resource"
                )
            alias = available.get("credential_alias")
            if not isinstance(alias, str) or not alias:
                raise ConfiguredCognitionCatalogAvailabilityError(
                    "configured credential availability lacks an exact alias"
                )

            alias_available = available.get("credential_alias_available") is True
            if not alias_available:
                remote_incomplete = True
            item = self._base_item(
                resource,
                binding_status="ok",
                availability_status="available" if alias_available else "unavailable",
            )
            item["credential_alias"] = alias
            item["credential_binding_configured"] = True
            item["credential_alias_available"] = alias_available
            item["secret_broker_consulted"] = True
            item["secret_alias_availability_checked"] = True
            composed.append(item)

        remote_count = sum(item.get("provider_kind") == "openai" for item in composed)
        if remote_count == 0:
            status = "not_applicable"
        elif remote_incomplete:
            status = "incomplete_availability"
        else:
            status = "ok"
        return self._base(
            status=status,
            resources=composed,
            configuration_source=discovered.get("configuration_source"),
        )
