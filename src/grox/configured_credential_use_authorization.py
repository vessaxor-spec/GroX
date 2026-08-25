from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .configured_credential_availability import ConfiguredCredentialAliasAvailability
from .contracts import MissionOrder
from .tools.gateway import ToolDenied, ToolGateway


class ConfiguredCredentialUseAuthorizationError(PermissionError):
    """Credential-use awareness received unsafe Mission authority context."""


class ConfiguredCredentialUseAuthorization:
    """Authorize use of one exact configured credential alias without using it.

    This surface composes the already-qualified configured credential binding /
    alias-availability seams with an already-sealed Mission Order and the
    existing Tool Gateway action gate. It never materializes, inspects, validates,
    hashes, persists, or exposes a secret value and performs no network, provider,
    cognition, selection, fallback, or routing activity.

    ``credential_use_authorized`` means only that the exact alias may be consumed
    under the exact sealed Order. It is not credential validity or authenticated
    provider/service readiness.
    """

    schema = "grox-configured-credential-use-authorization-v1"
    operation = "configured_cognition_credential_use_authorization"

    def __init__(self, config: Mapping[str, Any], gateway: ToolGateway):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, ToolGateway):
            raise TypeError("gateway must be a ToolGateway")
        self._config = dict(config)
        self.gateway = gateway

    @classmethod
    def _base(
        cls,
        *,
        status: str,
        authorization_status: str,
        resources: list[dict[str, Any]],
        mission_context_present: bool,
    ) -> dict[str, Any]:
        return {
            "schema": cls.schema,
            "status": status,
            "authorization_status": authorization_status,
            "resources": resources,
            "mission_context_present": bool(mission_context_present),
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
    def _parameter_identity_matches(
        parameters: Mapping[str, Any],
        item: Mapping[str, Any],
    ) -> tuple[bool, str]:
        checks = (
            ("operation", ConfiguredCredentialUseAuthorization.operation, "operation_mismatch"),
            ("resource_id", item["resource_id"], "resource_mismatch"),
            ("provider_kind", item["provider_kind"], "provider_mismatch"),
            ("model", item["model"], "model_mismatch"),
            ("endpoint", item["endpoint"], "endpoint_mismatch"),
            ("credential_alias", item["credential_alias"], "credential_alias_mismatch"),
        )
        for key, expected, status in checks:
            if parameters.get(key) != expected:
                return False, status
        return True, "exact_identity_bound"

    @staticmethod
    def _secret_grants(parameters: Mapping[str, Any]) -> tuple[str, ...] | None:
        grants = parameters.get("secret_grants")
        if not isinstance(grants, (list, tuple)):
            return None
        if not all(isinstance(alias, str) and bool(alias) for alias in grants):
            return None
        return tuple(grants)

    def inventory(
        self,
        *,
        order: MissionOrder | None = None,
    ) -> dict[str, Any]:
        if order is not None and not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder or null")
        if order is not None and not order.sealed:
            raise ConfiguredCredentialUseAuthorizationError(
                "credential-use awareness requires an already sealed Mission Order"
            )

        availability = ConfiguredCredentialAliasAvailability(
            self._config, self.gateway.secret_broker
        ).inventory()
        resources = availability.get("resources") or []
        if availability.get("status") != "ok" or len(resources) != 1:
            return self._base(
                status=str(availability.get("status") or "unbound"),
                authorization_status="not_applicable",
                resources=[],
                mission_context_present=order is not None,
            )

        available = resources[0]
        alias = available.get("credential_alias")
        if not isinstance(alias, str) or not alias:
            return self._base(
                status="invalid_binding",
                authorization_status="not_applicable",
                resources=[],
                mission_context_present=order is not None,
            )

        item = {
            "resource_id": available["resource_id"],
            "resource_type": "configured_cognition_credential_use_authorization",
            "provider_kind": available["provider_kind"],
            "model": available["model"],
            "endpoint": available["endpoint"],
            "credential_alias": alias,
            "credential_binding_configured": True,
            "credential_alias_available": available.get("credential_alias_available") is True,
            "credential_use_authorized": False,
            "authorized": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
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

        authorization_status = "no_mission_context"
        if order is not None:
            identity_matches, authorization_status = self._parameter_identity_matches(
                order.parameters, item
            )
            if identity_matches:
                if not item["credential_alias_available"]:
                    authorization_status = "credential_alias_unavailable"
                else:
                    grants = self._secret_grants(order.parameters)
                    if grants is None:
                        authorization_status = "invalid_secret_grants"
                    elif alias not in grants:
                        authorization_status = "credential_alias_not_granted"
                    else:
                        try:
                            self.gateway._allowed(order, "secret_use")
                        except (ToolDenied, ValueError, TypeError):
                            authorization_status = "denied_by_gateway_contract"
                        else:
                            item["credential_use_authorized"] = True
                            authorization_status = "sealed_mission_order_authorized"

        item["authorization_status"] = authorization_status
        return self._base(
            status="ok",
            authorization_status=authorization_status,
            resources=[item],
            mission_context_present=order is not None,
        )
