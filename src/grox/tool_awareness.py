from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
import shutil
from typing import Any

from .contracts import MissionMode, MissionOrder
from .tools.gateway import ToolDenied, ToolGateway
from .tools.workspace import docker_backend_available, namespace_backend_available


class ToolCapabilityAuthorizationError(RuntimeError):
    """A Tool Gateway awareness request supplied unsafe authority context."""


def _workspace_readiness(gateway: ToolGateway) -> tuple[bool, str | None]:
    """Fresh local workspace preflight without executing Commander work."""
    policy = gateway.policy
    if not policy.workspace_enabled:
        return False, None
    namespace_tools = (
        shutil.which("unshare"),
        shutil.which("chroot"),
        shutil.which("prlimit"),
        shutil.which("dash") or shutil.which("sh"),
    )
    if all(namespace_tools) and namespace_backend_available():
        return True, "namespace"
    image = policy.workspace_docker_image
    if image and docker_backend_available(image):
        return True, "docker"
    return False, None


def _browser_readiness(gateway: ToolGateway) -> tuple[bool, str | None]:
    """Fresh local browser-isolation preflight without fetching or rendering."""
    policy = gateway.policy
    if not policy.browser_enabled or not policy.network_enabled or not policy.allowed_origins:
        return False, None
    if shutil.which("unshare") and namespace_backend_available():
        return True, "namespace"
    image = policy.browser_docker_image
    getuid = getattr(os, "getuid", None)
    host_uid = getuid() if callable(getuid) else 0
    if image and host_uid != 0 and docker_backend_available(image):
        return True, "docker"
    return False, None


def _mcp_adapter_launchable(spec: Any) -> bool:
    argv = getattr(spec, "argv", None)
    if not isinstance(argv, tuple) or not argv or not isinstance(argv[0], str) or not argv[0].strip():
        return False
    executable = argv[0].strip()
    path = Path(executable)
    if path.is_absolute():
        executable_ok = path.is_file() and os.access(path, os.X_OK)
    else:
        executable_ok = shutil.which(executable) is not None
    if not executable_ok:
        return False
    cwd = getattr(spec, "cwd", None)
    if cwd is not None and (not isinstance(cwd, str) or not cwd.strip() or not Path(cwd).is_dir()):
        return False
    return True


def _mcp_readiness(gateway: ToolGateway) -> tuple[bool, int]:
    """Count locally launchable pre-registered adapters without spawning them."""
    if not gateway.policy.mcp_enabled:
        return False, 0
    launchable = sum(1 for spec in gateway.mcp.registry.values() if _mcp_adapter_launchable(spec))
    return launchable > 0, launchable


class ToolCapabilityAwareness:
    """Fresh read-only awareness over GroX's existing governed A5 tool surface.

    This class does not select or invoke tools and does not create an authority
    model. Host readiness and sealed Mission Order authorization remain separate.
    Existing ToolGateway deny-wins checks are reused for authorization preflight.
    """

    schema = "grox-live-tool-capability-inventory-v1"
    resource_kind = "governed_tool_capability"

    def __init__(self, gateway: ToolGateway):
        if not isinstance(gateway, ToolGateway):
            raise TypeError("gateway must be a ToolGateway")
        self.gateway = gateway

    @staticmethod
    def _require_safe_order(order: MissionOrder | None) -> MissionOrder | None:
        if order is None:
            return None
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder or null")
        if not order.sealed:
            raise ToolCapabilityAuthorizationError(
                "Tool capability authorization awareness requires an already sealed Mission Order"
            )
        return order

    @staticmethod
    def _operation(order: MissionOrder | None) -> str | None:
        if order is None:
            return None
        value = order.parameters.get("operation")
        return value.strip() if isinstance(value, str) and value.strip() else None

    def _authorize_workspace(self, order: MissionOrder) -> tuple[bool, str]:
        if not self.gateway.policy.workspace_enabled:
            return False, "host_policy_disabled"
        try:
            self.gateway._allowed(order, "workspace_exec")
            secret_env = order.parameters.get("secret_env") or {}
            if secret_env:
                if not isinstance(secret_env, Mapping):
                    return False, "denied_by_gateway_contract"
                self.gateway._allowed(order, "secret_use")
        except (ToolDenied, ValueError, TypeError):
            return False, "denied_by_gateway_contract"
        return True, "sealed_mission_order_authorized"

    def _authorize_network(self, order: MissionOrder) -> tuple[bool, str]:
        if not self.gateway.policy.network_enabled:
            return False, "host_policy_disabled"
        try:
            self.gateway._allowed(order, "net_fetch")
            url = order.parameters.get("url")
            if not isinstance(url, str) or not url.strip():
                return False, "denied_by_gateway_contract"
            self.gateway._assert_url(order, url.strip())
        except (ToolDenied, ValueError, TypeError):
            return False, "denied_by_gateway_contract"
        return True, "sealed_mission_order_authorized"

    def _authorize_browser(self, order: MissionOrder) -> tuple[bool, str]:
        if not self.gateway.policy.browser_enabled or not self.gateway.policy.network_enabled:
            return False, "host_policy_disabled"
        try:
            self.gateway._allowed(order, "browser_capture")
            self.gateway._allowed(order, "net_fetch")
            url = order.parameters.get("url")
            if not isinstance(url, str) or not url.strip():
                return False, "denied_by_gateway_contract"
            self.gateway._assert_url(order, url.strip())
        except (ToolDenied, ValueError, TypeError):
            return False, "denied_by_gateway_contract"
        return True, "sealed_mission_order_authorized"

    def _authorize_mcp(self, order: MissionOrder) -> tuple[bool, str]:
        if not self.gateway.policy.mcp_enabled:
            return False, "host_policy_disabled"
        try:
            self.gateway._allowed(order, "mcp_call")
            adapter = order.parameters.get("adapter")
            tool = order.parameters.get("tool")
            if not isinstance(adapter, str) or not adapter.strip() or not isinstance(tool, str) or not tool.strip():
                return False, "denied_by_gateway_contract"
            adapter = adapter.strip()
            tool = tool.strip()
            grants = order.parameters.get("mcp_grants") or {}
            if not isinstance(grants, Mapping):
                return False, "denied_by_gateway_contract"
            tools = grants.get(adapter) or ()
            if not isinstance(tools, (list, tuple)) or tool not in tools:
                return False, "denied_by_gateway_contract"
            spec = self.gateway.mcp.registry.get(adapter)
            if spec is None or tool not in spec.allowed_tools:
                return False, "denied_by_gateway_contract"
            if tool in spec.mutating_tools:
                self.gateway._allowed(order, "mcp_mutate")
                if order.mode is not MissionMode.repair:
                    return False, "denied_by_gateway_contract"
        except (ToolDenied, ValueError, TypeError):
            return False, "denied_by_gateway_contract"
        return True, "sealed_mission_order_authorized"

    @staticmethod
    def _snapshot(
        *,
        resource_id: str,
        operation: str,
        host_enabled: bool,
        ready: bool,
        readiness_status: str,
        readiness_reason: str,
        requested: bool,
        authorized: bool,
        authorization_status: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "resource_id": resource_id,
            "resource_kind": ToolCapabilityAwareness.resource_kind,
            "operation": operation,
            "discovered": True,
            "host_enabled": bool(host_enabled),
            "ready": bool(ready),
            "readiness_status": readiness_status,
            "readiness_reason": readiness_reason,
            "requested": bool(requested),
            "authorized": bool(authorized),
            "authorization_status": authorization_status,
            "selected": False,
            "observed": False,
            "details": dict(details),
            "authority_changed": False,
            "auto_invocation": False,
        }

    def inventory(self, *, order: MissionOrder | None = None) -> dict[str, Any]:
        """Rediscover current governed tool state without invoking any capability."""
        order = self._require_safe_order(order)
        requested_operation = self._operation(order)
        policy = self.gateway.policy

        workspace_ready, workspace_backend = _workspace_readiness(self.gateway)
        browser_ready, browser_backend = _browser_readiness(self.gateway)
        mcp_ready, mcp_launchable = _mcp_readiness(self.gateway)
        network_ready = bool(policy.network_enabled and policy.allowed_origins)

        def authorization(
            operation: str,
            authorize,
        ) -> tuple[bool, bool, str]:
            requested = requested_operation == operation
            if order is None:
                return requested, False, "no_mission_context"
            if not requested:
                return False, False, "operation_not_requested"
            allowed, status = authorize(order)
            return True, allowed, status

        workspace_requested, workspace_authorized, workspace_auth_status = authorization(
            "workspace_shell", self._authorize_workspace
        )
        network_requested, network_authorized, network_auth_status = authorization(
            "http_fetch", self._authorize_network
        )
        browser_requested, browser_authorized, browser_auth_status = authorization(
            "browser_capture", self._authorize_browser
        )
        mcp_requested, mcp_authorized, mcp_auth_status = authorization(
            "mcp_call", self._authorize_mcp
        )

        resources = [
            self._snapshot(
                resource_id="tool:workspace",
                operation="workspace_shell",
                host_enabled=policy.workspace_enabled,
                ready=workspace_ready,
                readiness_status="ready" if workspace_ready else "unavailable",
                readiness_reason=(
                    f"qualified local isolation backend: {workspace_backend}"
                    if workspace_ready
                    else "no currently qualified local workspace isolation backend"
                ),
                requested=workspace_requested,
                authorized=workspace_authorized,
                authorization_status=workspace_auth_status,
                details={"backend": workspace_backend},
            ),
            self._snapshot(
                resource_id="tool:network",
                operation="http_fetch",
                host_enabled=policy.network_enabled,
                ready=network_ready,
                readiness_status="ready" if network_ready else "unavailable",
                readiness_reason=(
                    "host network policy has at least one represented allowed origin"
                    if network_ready
                    else "network disabled or host policy represents no allowed origin"
                ),
                requested=network_requested,
                authorized=network_authorized,
                authorization_status=network_auth_status,
                details={"allowed_origin_count": len(policy.allowed_origins)},
            ),
            self._snapshot(
                resource_id="tool:browser",
                operation="browser_capture",
                host_enabled=policy.browser_enabled,
                ready=browser_ready,
                readiness_status="ready" if browser_ready else "unavailable",
                readiness_reason=(
                    f"browser isolation preflight available: {browser_backend}"
                    if browser_ready
                    else "browser/network policy or local isolation preflight is unavailable"
                ),
                requested=browser_requested,
                authorized=browser_authorized,
                authorization_status=browser_auth_status,
                details={"backend": browser_backend},
            ),
            self._snapshot(
                resource_id="tool:mcp",
                operation="mcp_call",
                host_enabled=policy.mcp_enabled,
                ready=mcp_ready,
                readiness_status="ready" if mcp_ready else "unavailable",
                readiness_reason=(
                    "at least one pre-registered MCP adapter is locally launchable"
                    if mcp_ready
                    else "MCP disabled or no pre-registered adapter is locally launchable"
                ),
                requested=mcp_requested,
                authorized=mcp_authorized,
                authorization_status=mcp_auth_status,
                details={
                    "registered_adapter_count": len(self.gateway.mcp.registry),
                    "launchable_adapter_count": mcp_launchable,
                },
            ),
        ]
        return {
            "schema": self.schema,
            "mission_order_id": order.order_id if order is not None else None,
            "resources": resources,
            "authority_changed": False,
            "auto_invocation": False,
        }
