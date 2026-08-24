from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contracts import MissionOrder
from .tools.gateway import ToolDenied, ToolGateway
from .tools.policy import PolicyError, normalize_origin


class ConfiguredConnectionAuthorizationError(PermissionError):
    """Configured connection awareness received unsafe authority context."""


class ConfiguredConnectionPolicyAwareness:
    """Read-only policy awareness for one configured remote cognition connection.

    This surface never performs network I/O, reads credentials, constructs or
    binds a provider, loads a model, invokes cognition, selects a resource, or
    changes authority. Host-policy permission and already-sealed Mission
    authorization are intentionally reported as separate states.
    """

    schema = "grox-configured-connection-policy-awareness-v1"
    operation = "configured_cognition_connection_authorization"

    def __init__(self, gateway: ToolGateway):
        if not isinstance(gateway, ToolGateway):
            raise TypeError("gateway must be a ToolGateway")
        self.gateway = gateway

    @staticmethod
    def _base(
        *,
        status: str,
        resource_id: str | None,
        endpoint: str | None,
        origin: str | None,
        discovered: bool,
        host_policy_permitted: bool,
        authorized: bool,
        authorization_status: str,
    ) -> dict[str, Any]:
        return {
            "schema": ConfiguredConnectionPolicyAwareness.schema,
            "status": status,
            "resource_id": resource_id,
            "resource_kind": "configured_remote_cognition_connection",
            "endpoint": endpoint,
            "origin": origin,
            "discovered": bool(discovered),
            "host_policy_permitted": bool(host_policy_permitted),
            "authorized": bool(authorized),
            "authorization_status": authorization_status,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "network_invoked": False,
            "credential_inspected": False,
            "provider_constructed": False,
            "authority_changed": False,
            "auto_invocation": False,
            "auto_selection": False,
        }

    @staticmethod
    def _remote_identity(resource: Mapping[str, Any]) -> tuple[str, str, str] | None:
        if resource.get("resource_type") != "configured_cognition":
            return None
        if resource.get("provider_kind") != "openai" or resource.get("discovered") is not True:
            return None
        resource_id = resource.get("resource_id")
        endpoint = resource.get("endpoint")
        if not isinstance(resource_id, str) or not resource_id.strip():
            return None
        if not isinstance(endpoint, str) or not endpoint.strip():
            return None
        try:
            origin = normalize_origin(endpoint.strip())
        except (PolicyError, ValueError):
            return None
        return resource_id.strip(), endpoint.strip(), origin

    def inventory(
        self,
        *,
        resource: Mapping[str, Any],
        order: MissionOrder | None = None,
    ) -> dict[str, Any]:
        if not isinstance(resource, Mapping):
            raise TypeError("resource must be a mapping")
        if order is not None and not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder or null")
        if order is not None and not order.sealed:
            raise ConfiguredConnectionAuthorizationError(
                "configured connection awareness requires an already sealed Mission Order"
            )

        identity = self._remote_identity(resource)
        if identity is None:
            return self._base(
                status="not_applicable",
                resource_id=None,
                endpoint=None,
                origin=None,
                discovered=False,
                host_policy_permitted=False,
                authorized=False,
                authorization_status="not_applicable",
            )

        resource_id, endpoint, origin = identity
        host_policy_permitted = bool(
            self.gateway.policy.network_enabled and origin in self.gateway.policy.allowed_origins
        )
        if order is None:
            return self._base(
                status="ok",
                resource_id=resource_id,
                endpoint=endpoint,
                origin=origin,
                discovered=True,
                host_policy_permitted=host_policy_permitted,
                authorized=False,
                authorization_status="no_mission_context",
            )

        parameters = order.parameters
        if parameters.get("operation") != self.operation:
            authorization_status = "operation_mismatch"
            authorized = False
        elif parameters.get("resource_id") != resource_id:
            authorization_status = "resource_mismatch"
            authorized = False
        elif parameters.get("endpoint") != endpoint:
            authorization_status = "endpoint_mismatch"
            authorized = False
        elif not host_policy_permitted:
            authorization_status = "host_policy_denied"
            authorized = False
        else:
            try:
                self.gateway._allowed(order, "net_fetch")
                granted_origin, _ = self.gateway._assert_url(order, endpoint)
                authorized = granted_origin == origin
                authorization_status = (
                    "sealed_mission_order_authorized" if authorized else "origin_mismatch"
                )
            except (ToolDenied, ValueError, TypeError):
                authorized = False
                authorization_status = "denied_by_gateway_contract"

        return self._base(
            status="ok",
            resource_id=resource_id,
            endpoint=endpoint,
            origin=origin,
            discovered=True,
            host_policy_permitted=host_policy_permitted,
            authorized=authorized,
            authorization_status=authorization_status,
        )
