from __future__ import annotations

from collections.abc import Callable, Mapping
import math
import time
from typing import Any

from .configured_credential_use_authorization import (
    ConfiguredCredentialUseAuthorization,
    ConfiguredCredentialUseAuthorizationError,
)
from .contracts import MissionOrder
from .tools.layout_gateway import LayoutToolGateway


class ConfiguredOpenAIAuthenticatedModelProbeError(PermissionError):
    """Configured authenticated OpenAI model probe failed closed."""


class ConfiguredOpenAIAuthenticatedModelProbe:
    """Probe exact configured official OpenAI model visibility under Mission authority.

    Configuration identity is resolved here before the Tool Gateway is allowed to
    materialize or transmit a credential. The gateway remains the final secret and
    network boundary. No cognition request, readiness promotion, fitness decision,
    provider selection, fallback, observation promotion, or authority widening occurs.

    Completed probe evidence carries a process-local monotonic observation stamp so
    a separate pure evaluator can bound freshness. The stamp is deliberately not a
    wall-clock timestamp and is not portable across process reconstitution.
    """

    operation = "configured_openai_authenticated_model_probe"
    official_responses_endpoint = "https://api.openai.com/v1/responses"

    def __init__(
        self,
        config: Mapping[str, Any],
        gateway: LayoutToolGateway,
        *,
        clock: Callable[[], float] | None = None,
    ):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, LayoutToolGateway):
            raise TypeError("gateway must be a LayoutToolGateway")
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable or null")
        self._config = dict(config)
        self._gateway = gateway
        self._clock = clock or time.monotonic
        self._authorization = ConfiguredCredentialUseAuthorization(self._config, gateway)

    def probe(self, *, order: MissionOrder) -> dict[str, Any]:
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        try:
            authorization = self._authorization.inventory(
                order=order,
                expected_operation=self.operation,
            )
        except ConfiguredCredentialUseAuthorizationError as exc:
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe requires an already sealed Mission Order"
            ) from exc

        resources = authorization.get("resources") or []
        if authorization.get("status") != "ok" or len(resources) != 1:
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe is not applicable to current configured cognition"
            )
        item = resources[0]
        if item.get("provider_kind") != "openai":
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe requires configured provider kind openai"
            )
        if item.get("endpoint") != self.official_responses_endpoint:
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe requires the exact official Responses endpoint"
            )
        if item.get("credential_use_authorized") is not True:
            status = str(authorization.get("authorization_status") or "denied")
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                f"authenticated OpenAI model probe denied: {status}"
            )

        alias = item.get("credential_alias")
        if not isinstance(alias, str) or not alias:
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe has no exact credential alias"
            )

        try:
            result = self._gateway.openai_model_probe(
                order,
                resource_id=str(item["resource_id"]),
                responses_endpoint=str(item["endpoint"]),
                model=str(item["model"]),
                credential_alias=alias,
            )
        except (PermissionError, TypeError, ValueError, TimeoutError) as exc:
            if isinstance(exc, TimeoutError):
                raise
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                f"authenticated OpenAI model probe denied: {exc}"
            ) from exc

        observed = self._clock()
        if (
            isinstance(observed, bool)
            or not isinstance(observed, (int, float))
            or not math.isfinite(float(observed))
            or float(observed) < 0.0
        ):
            raise ConfiguredOpenAIAuthenticatedModelProbeError(
                "authenticated OpenAI model probe produced an invalid monotonic observation stamp"
            )

        return {
            **result,
            "resource_id": str(item["resource_id"]),
            "provider_kind": "openai",
            "endpoint": self.official_responses_endpoint,
            "credential_use_authorized": True,
            "observed_monotonic_seconds": float(observed),
            "observation_clock": "process_monotonic",
            "persistable_readiness_evidence": False,
            "mission_created": False,
            "observed": False,
            "auto_selection": False,
        }
