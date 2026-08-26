from __future__ import annotations

import http.client
import json
import ssl
from urllib.parse import quote

from ..contracts import MissionOrder
from ..runtime_layout import VesselLayout
from .browser import BrowserRuntime
from .gateway import ToolDenied, ToolGateway
from .policy import GatewayPolicy
from .secrets import SecretBroker, SecretDenied
from .workspace import IsolatedWorkspace, WorkspaceUnavailable


_OFFICIAL_OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
_OFFICIAL_OPENAI_ORIGIN = "https://api.openai.com"
_OPENAI_PROBE_OPERATION = "configured_openai_authenticated_model_probe"
_OPENAI_PROBE_SECRET_ENV = "GROX_OPENAI_PROBE_CREDENTIAL"


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

    def openai_model_probe(
        self,
        order: MissionOrder,
        *,
        resource_id: str,
        responses_endpoint: str,
        model: str,
        credential_alias: str,
    ) -> dict:
        """Perform one credential-bearing official OpenAI model metadata GET.

        This is intentionally not a generic authenticated HTTP surface. The
        credential may leave the Vessel only for the exact official OpenAI API
        endpoint and only under an already-sealed Order that binds the exact
        configured resource/model/endpoint/alias plus both network and secret
        authority. Response body text and credential material are never returned.
        """
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not order.sealed:
            raise ToolDenied("authenticated OpenAI probe requires an already sealed Mission Order")
        self._allowed(order, "net_fetch")
        self._allowed(order, "secret_use")
        if not self.policy.network_enabled:
            raise ToolDenied("network access disabled by host policy")
        if responses_endpoint != _OFFICIAL_OPENAI_RESPONSES_ENDPOINT:
            raise ToolDenied("authenticated OpenAI probe requires the exact official Responses endpoint")
        if not isinstance(model, str) or not model or len(model) > 160:
            raise ToolDenied("authenticated OpenAI probe requires a bounded model identity")
        if not isinstance(credential_alias, str) or not credential_alias:
            raise ToolDenied("authenticated OpenAI probe requires an exact credential alias")

        parameters = order.parameters
        exact = (
            parameters.get("operation") == _OPENAI_PROBE_OPERATION
            and parameters.get("resource_id") == resource_id
            and parameters.get("provider_kind") == "openai"
            and parameters.get("model") == model
            and parameters.get("endpoint") == responses_endpoint
            and parameters.get("credential_alias") == credential_alias
        )
        if not exact:
            raise ToolDenied("authenticated OpenAI probe Mission identity mismatch")

        model_url = f"{_OFFICIAL_OPENAI_ORIGIN}/v1/models/{quote(model, safe='')}"
        origin, _ = self._assert_url(order, model_url)
        if origin != _OFFICIAL_OPENAI_ORIGIN:
            raise ToolDenied("authenticated OpenAI probe origin mismatch")

        try:
            secret_values, aliases = self.secret_broker.materialize_env(
                order,
                {_OPENAI_PROBE_SECRET_ENV: credential_alias},
            )
        except SecretDenied as exc:
            raise ToolDenied("authenticated OpenAI probe credential materialization denied") from exc
        if aliases != [credential_alias]:
            secret_values.clear()
            raise ToolDenied("authenticated OpenAI probe credential identity mismatch")
        api_key = secret_values.pop(_OPENAI_PROBE_SECRET_ENV, None)
        secret_values.clear()
        if not isinstance(api_key, str) or not api_key:
            raise ToolDenied("authenticated OpenAI probe credential materialization produced no usable value")

        conn = http.client.HTTPSConnection(
            "api.openai.com",
            443,
            timeout=self.policy.network_timeout_seconds,
            context=ssl.create_default_context(),
        )
        try:
            conn.request(
                "GET",
                f"/v1/models/{quote(model, safe='')}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "GroX/1.0",
                    "Accept": "application/json",
                },
            )
            response = conn.getresponse()
            raw = response.read(self.policy.max_response_bytes + 1)
            if len(raw) > self.policy.max_response_bytes:
                raise ToolDenied(
                    f"network response exceeds {self.policy.max_response_bytes} bytes"
                )
            status = int(response.status)
            model_identity = None
            metadata_valid = False
            if status == 200:
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    payload = None
                if isinstance(payload, dict):
                    candidate = payload.get("id")
                    metadata_valid = candidate == model and payload.get("object") == "model"
                    if metadata_valid:
                        model_identity = candidate

            if status == 200 and metadata_valid:
                classification = "authenticated_model_visible"
            elif status == 401:
                classification = "credential_rejected"
            else:
                classification = "indeterminate"

            return {
                "schema": "grox-openai-authenticated-model-probe-v1",
                "origin": _OFFICIAL_OPENAI_ORIGIN,
                "status": status,
                "classification": classification,
                "requested_model": model,
                "model_identity": model_identity,
                "metadata_valid": metadata_valid,
                "credential_alias": credential_alias,
                "credential_accepted_for_model_visibility": classification == "authenticated_model_visible",
                "credential_rejected": classification == "credential_rejected",
                "secret_materialized": True,
                "network_invoked": True,
                "response_body_returned": False,
                "cognition_invoked": False,
                "ready": False,
                "qualified_fit": False,
                "selected": False,
                "authority_changed": False,
            }
        except TimeoutError:
            raise
        except OSError as exc:
            raise ToolDenied(
                "authenticated OpenAI probe network request failed within exact official origin"
            ) from exc
        finally:
            api_key = None
            conn.close()
