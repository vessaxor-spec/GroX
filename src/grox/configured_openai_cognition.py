from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .configured_credential_use_authorization import (
    ConfiguredCredentialUseAuthorization,
    ConfiguredCredentialUseAuthorizationError,
)
from .contracts import MissionOrder
from .reasoning.contracts import MissionInterpretation
from .tools.gateway import ToolDenied
from .tools.layout_gateway import LayoutToolGateway


class ConfiguredOpenAICognitionError(RuntimeError):
    """Configured governed OpenAI cognition failed closed."""


@dataclass(frozen=True)
class ConfiguredOpenAICognitionResult:
    """Successful exact configured cognition result plus privacy-minimized evidence."""

    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    response_id: str | None
    response_model: str | None
    _interpretation: MissionInterpretation = field(repr=False, compare=False)

    @property
    def interpretation(self) -> MissionInterpretation:
        return self._interpretation

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-openai-cognition-v1",
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "response_id": self.response_id,
            "response_model": self.response_model,
            "credential_use_authorized": True,
            "secret_materialized": True,
            "network_invoked": True,
            "cognition_invoked": True,
            "cognition_succeeded": True,
            "structured_interpretation_valid": True,
            "ready": True,
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
            "raw_response_returned": False,
        }


class ConfiguredOpenAICognition:
    """Invoke one exact configured official OpenAI reasoner through the Tool Gateway."""

    operation = "configured_openai_cognition_invoke"
    official_responses_endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, config: Mapping[str, Any], gateway: LayoutToolGateway):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, LayoutToolGateway):
            raise TypeError("gateway must be a LayoutToolGateway")
        self._config = dict(config)
        self._gateway = gateway
        self._authorization = ConfiguredCredentialUseAuthorization(self._config, gateway)

    def invoke(
        self,
        *,
        order: MissionOrder,
        roster: list[dict[str, Any]],
    ) -> ConfiguredOpenAICognitionResult:
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not isinstance(roster, list) or not all(isinstance(item, dict) for item in roster):
            raise TypeError("roster must be a list of mappings")

        try:
            authorization = self._authorization.inventory(
                order=order,
                expected_operation=self.operation,
            )
        except ConfiguredCredentialUseAuthorizationError as exc:
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition requires an already sealed Mission Order"
            ) from exc

        resources = authorization.get("resources") or []
        if authorization.get("status") != "ok" or len(resources) != 1:
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition is not applicable to current configured cognition"
            )
        item = resources[0]
        if item.get("provider_kind") != "openai":
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition requires provider kind openai"
            )
        if item.get("endpoint") != self.official_responses_endpoint:
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition requires the exact official Responses endpoint"
            )
        if item.get("credential_use_authorized") is not True:
            status = str(authorization.get("authorization_status") or "denied")
            raise ConfiguredOpenAICognitionError(
                f"configured OpenAI cognition denied: {status}"
            )

        alias = item.get("credential_alias")
        if not isinstance(alias, str) or not alias:
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition has no exact credential alias"
            )
        if not order.commander_intent or len(order.commander_intent) > 20_000:
            raise ConfiguredOpenAICognitionError(
                "configured OpenAI cognition requires bounded Commander intent"
            )

        try:
            response = self._gateway.openai_responses_cognition(
                order,
                resource_id=str(item["resource_id"]),
                responses_endpoint=str(item["endpoint"]),
                model=str(item["model"]),
                credential_alias=alias,
                directive=order.commander_intent,
                roster=roster,
            )
            interpretation = response["interpretation"]
            if not isinstance(interpretation, MissionInterpretation):
                raise TypeError("gateway returned invalid structured interpretation")
            if interpretation.commander_intent != order.commander_intent:
                raise ValueError("gateway interpretation Commander intent mismatch")
        except (ToolDenied, KeyError, TypeError, ValueError, TimeoutError) as exc:
            raise ConfiguredOpenAICognitionError(
                f"configured OpenAI cognition failed closed: {exc}"
            ) from exc

        return ConfiguredOpenAICognitionResult(
            resource_id=str(item["resource_id"]),
            provider_kind="openai",
            model=str(item["model"]),
            endpoint=self.official_responses_endpoint,
            credential_alias=alias,
            response_id=response.get("response_id"),
            response_model=response.get("response_model"),
            _interpretation=interpretation,
        )
