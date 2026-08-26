from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .configured_credential_use_authorization import (
    ConfiguredCredentialUseAuthorization,
    ConfiguredCredentialUseAuthorizationError,
)
from .contracts import MissionOrder
from .reasoning.openai_responses import OpenAIResponsesProvider
from .tools.gateway import ToolGateway
from .tools.secrets import SecretDenied


class ConfiguredRemoteReasonerActivationError(PermissionError):
    """Configured remote reasoner activation failed closed."""


@dataclass(frozen=True)
class ConfiguredRemoteReasonerHandle:
    """Non-secret activation result retaining the provider as internal capability."""

    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    _provider: OpenAIResponsesProvider = field(repr=False, compare=False)

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-remote-reasoner-activation-v1",
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "credential_use_authorized": True,
            "secret_materialized": True,
            "provider_constructed": True,
            "credential_validated": False,
            "network_invoked": False,
            "cognition_invoked": False,
            "ready": False,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }


class ConfiguredRemoteReasonerActivation:
    """Construct one exact configured remote reasoner under sealed Mission authority.

    The activation seam is deliberately narrower than authenticated readiness or
    cognition. It consumes only the exact configured credential alias after the
    existing credential-use authorization contract passes for this operation,
    constructs the configured provider, and performs no network request or
    cognition invocation. The resulting provider remains an internal capability
    of the handle rather than a public invocation surface.
    """

    operation = "configured_cognition_remote_reasoner_activation"
    _SECRET_ENV_NAME = "GROX_CONFIGURED_COGNITION_CREDENTIAL"

    def __init__(self, config: Mapping[str, Any], gateway: ToolGateway):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, ToolGateway):
            raise TypeError("gateway must be a ToolGateway")
        self._config = dict(config)
        self._gateway = gateway
        self._authorization = ConfiguredCredentialUseAuthorization(self._config, gateway)

    def activate(self, *, order: MissionOrder) -> ConfiguredRemoteReasonerHandle:
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")

        try:
            authorization = self._authorization.inventory(
                order=order,
                expected_operation=self.operation,
            )
        except ConfiguredCredentialUseAuthorizationError as exc:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner activation requires an already sealed Mission Order"
            ) from exc

        resources = authorization.get("resources") or []
        if authorization.get("status") != "ok" or len(resources) != 1:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner activation is not applicable"
            )
        item = resources[0]
        if item.get("credential_use_authorized") is not True:
            status = str(authorization.get("authorization_status") or "denied")
            raise ConfiguredRemoteReasonerActivationError(
                f"configured remote reasoner activation denied: {status}"
            )

        alias = item.get("credential_alias")
        if not isinstance(alias, str) or not alias:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner activation has no exact credential alias"
            )

        try:
            materialized, used_aliases = self._gateway.secret_broker.materialize_env(
                order,
                {self._SECRET_ENV_NAME: alias},
            )
        except (SecretDenied, TypeError, ValueError) as exc:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner credential materialization denied"
            ) from exc

        if used_aliases != [alias]:
            materialized.clear()
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner credential materialization identity mismatch"
            )

        secret = materialized.pop(self._SECRET_ENV_NAME, None)
        materialized.clear()
        if not isinstance(secret, str) or not secret:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner credential materialization produced no usable value"
            )

        try:
            provider = OpenAIResponsesProvider(
                api_key=secret,
                model=str(item["model"]),
                endpoint=str(item["endpoint"]),
            )
        except (TypeError, ValueError) as exc:
            raise ConfiguredRemoteReasonerActivationError(
                "configured remote reasoner provider construction failed"
            ) from exc
        finally:
            secret = None

        return ConfiguredRemoteReasonerHandle(
            resource_id=str(item["resource_id"]),
            provider_kind=str(item["provider_kind"]),
            model=str(item["model"]),
            endpoint=str(item["endpoint"]),
            credential_alias=alias,
            _provider=provider,
        )
