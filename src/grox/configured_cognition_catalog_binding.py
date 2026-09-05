from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .cognition_discovery import ConfiguredCognitionDiscovery
from .credential_binding import ConfiguredCredentialBinding


class ConfiguredCognitionCatalogBindingError(RuntimeError):
    """Catalog binding composition detected an internal identity inconsistency."""


class ConfiguredCognitionCatalogBinding:
    """Compose configured cognition discovery with per-resource credential binding.

    This surface is non-secret and read-only. It never consults a SecretBroker,
    checks alias availability, materializes credentials, constructs providers,
    touches the network, invokes cognition, or changes selection/authority state.
    """

    schema = "grox-configured-cognition-catalog-binding-v1"

    def __init__(self, config: Mapping[str, Any]):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        self._config = dict(config)

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
            "secret_broker_consulted": False,
            "secret_alias_availability_checked": False,
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
    def _base_item(resource: Mapping[str, Any], *, binding_status: str) -> dict[str, Any]:
        return {
            "resource_id": resource["resource_id"],
            "resource_type": "configured_cognition_catalog_credential_binding",
            "provider_kind": resource["provider_kind"],
            "model": resource["model"],
            "endpoint": resource["endpoint"],
            "credential_binding_status": binding_status,
            "credential_binding_configured": False,
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

    @staticmethod
    def _binding_matches_resource(
        binding: Mapping[str, Any],
        resource: Mapping[str, Any],
    ) -> bool:
        return (
            binding.get("resource_id") == resource.get("resource_id")
            and binding.get("provider_kind") == resource.get("provider_kind")
            and binding.get("model") == resource.get("model")
            and binding.get("endpoint") == resource.get("endpoint")
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
            raise ConfiguredCognitionCatalogBindingError(
                "configured cognition catalog declaration/resource cardinality mismatch"
            )

        composed: list[dict[str, Any]] = []
        remote_incomplete = False
        for resource, declaration in zip(resources, declarations, strict=True):
            provider_kind = resource.get("provider_kind")
            if provider_kind != "openai":
                composed.append(self._base_item(resource, binding_status="not_applicable"))
                continue

            binding_inventory = ConfiguredCredentialBinding(declaration).inventory()
            bound_resources = binding_inventory.get("resources") or []
            if binding_inventory.get("status") != "ok" or len(bound_resources) != 1:
                remote_incomplete = True
                composed.append(self._base_item(resource, binding_status="unbound"))
                continue

            bound = bound_resources[0]
            if not self._binding_matches_resource(bound, resource):
                raise ConfiguredCognitionCatalogBindingError(
                    "configured credential binding identity differs from catalog resource"
                )
            alias = bound.get("credential_alias")
            if not isinstance(alias, str) or not alias:
                raise ConfiguredCognitionCatalogBindingError(
                    "configured credential binding lacks an exact alias"
                )

            item = self._base_item(resource, binding_status="ok")
            item["credential_alias"] = alias
            item["credential_binding_configured"] = True
            composed.append(item)

        remote_count = sum(item.get("provider_kind") == "openai" for item in composed)
        if remote_count == 0:
            status = "not_applicable"
        elif remote_incomplete:
            status = "incomplete_binding"
        else:
            status = "ok"
        return self._base(
            status=status,
            resources=composed,
            configuration_source=discovered.get("configuration_source"),
        )
