from __future__ import annotations

from ..runtime_layout import VesselLayout
from .browser import BrowserRuntime
from .gateway import ToolDenied, ToolGateway
from .policy import GatewayPolicy
from .secrets import SecretDenied
from .workspace import IsolatedWorkspace, WorkspaceUnavailable


class LayoutToolGateway(ToolGateway):
    """Tool Gateway bound to explicit GroX filesystem roles.

    Ordinary filesystem authority remains rooted at the Commander work root.
    Host policy and other immutable runtime assets are read from asset_root.
    Browser evidence and isolated-workspace scratch are kept under private
    state_root. Mission Order action and scope semantics remain those of the
    base Tool Gateway.
    """

    def __init__(
        self,
        layout: VesselLayout,
        *,
        policy: GatewayPolicy | None = None,
        extra_allowed_origins=(),
        secret_broker=None,
        mcp_registry=None,
    ):
        effective_policy = policy or GatewayPolicy.from_file(
            layout.asset_path("configs/tool-policy.json"),
            extra_allowed_origins=extra_allowed_origins,
        )
        super().__init__(
            layout.work_root,
            policy=effective_policy,
            secret_broker=secret_broker,
            mcp_registry=mcp_registry,
        )
        self.layout = layout
        self.asset_root = layout.asset_root
        self.state_root = layout.state_root
        self.state_storage_root = layout.state_storage_root
        # BrowserRuntime uses its root only for mutable capture evidence. Its
        # executable/module discovery remains independent of this path.
        self._browser = BrowserRuntime(self.state_storage_root, self.policy)

    def workspace_shell(self, order, script: str, *, secret_env: dict[str, str] | None = None) -> dict:
        self._allowed(order, "workspace_exec")
        if not self.policy.workspace_enabled:
            raise ToolDenied("isolated workspace disabled by host policy")
        secret_values: dict[str, str] = {}
        aliases: list[str] = []
        if secret_env:
            self._allowed(order, "secret_use")
            try:
                secret_values, aliases = self.secret_broker.materialize_env(order, secret_env)
            except SecretDenied as exc:
                raise ToolDenied(str(exc)) from exc
        if self._workspace is None:
            try:
                self._workspace = IsolatedWorkspace(
                    self.state_storage_root / "workspaces",
                    timeout_seconds=self.policy.workspace_timeout_seconds,
                    memory_bytes=self.policy.workspace_memory_bytes,
                    file_bytes=self.policy.workspace_file_bytes,
                    docker_image=self.policy.workspace_docker_image,
                )
            except WorkspaceUnavailable as exc:
                raise ToolDenied(str(exc)) from exc
        result = self._workspace.run(order.mission_id, order.order_id, script, env=secret_values)
        result["stdout"] = self.secret_broker.redact(result["stdout"], secret_values)
        result["stderr"] = self.secret_broker.redact(result["stderr"], secret_values)
        result["secret_aliases"] = aliases
        return result
