from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import math
import time
from typing import Any

from .credential_binding import ConfiguredCredentialBinding
from .configured_openai_probe import ConfiguredOpenAIAuthenticatedModelProbe


class ConfiguredCognitionReadinessError(RuntimeError):
    """Configured cognition readiness could not be evaluated safely."""


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionReadinessResult:
    """Volatile readiness evidence for one exact configured cognition resource."""

    status: str
    reason: str | None
    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    observation_age_seconds: float | None
    max_age_seconds: float

    @property
    def ready(self) -> bool:
        return self.status == "READY"

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-readiness-v1",
            "status": self.status,
            "reason": self.reason,
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "observation_age_seconds": self.observation_age_seconds,
            "max_age_seconds": self.max_age_seconds,
            "ready": self.ready,
            "readiness_scope": "authenticated_model_visibility",
            "freshness_clock": "process_monotonic",
            "volatile_process_local": True,
            "persistable_readiness_evidence": False,
            "qualified_fit": False,
            "routing_fit_claim": False,
            "selected": False,
            "observed": False,
            "cognition_invoked": False,
            "secret_materialized_by_evaluator": False,
            "network_invoked_by_evaluator": False,
            "provider_constructed": False,
            "fallback_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "ranking_enabled": False,
            "learning_enabled": False,
            "adaptive_scoring_enabled": False,
        }


class ConfiguredCognitionReadiness:
    """Evaluate fresh authenticated visibility for the exact current resource.

    This evaluator is deliberately pure. It consumes already-returned authenticated
    model-probe evidence, resolves current non-secret configured binding, and checks
    exact identity plus a process-local monotonic freshness window. It performs no
    secret access, network I/O, provider construction, cognition, selection, or
    fallback. READY is scoped only to recent authenticated model visibility.
    """

    default_max_age_seconds = 60.0
    maximum_max_age_seconds = 300.0

    def __init__(
        self,
        config: Mapping[str, Any],
        *,
        clock: Callable[[], float] | None = None,
        max_age_seconds: float = default_max_age_seconds,
    ):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable or null")
        if (
            isinstance(max_age_seconds, bool)
            or not isinstance(max_age_seconds, (int, float))
            or not math.isfinite(float(max_age_seconds))
            or not 0.0 < float(max_age_seconds) <= self.maximum_max_age_seconds
        ):
            raise ValueError(
                f"max_age_seconds must be greater than 0 and at most {self.maximum_max_age_seconds}"
            )
        self._config = dict(config)
        self._clock = clock or time.monotonic
        self._max_age_seconds = float(max_age_seconds)

    @staticmethod
    def _valid_number(value: Any) -> bool:
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(float(value))
            and float(value) >= 0.0
        )

    def _current_binding(self) -> Mapping[str, Any]:
        binding = ConfiguredCredentialBinding(self._config).inventory()
        resources = binding.get("resources") or []
        if binding.get("status") != "ok" or len(resources) != 1:
            raise ConfiguredCognitionReadinessError(
                "current configured cognition credential binding is unavailable"
            )
        item = resources[0]
        if item.get("provider_kind") != "openai":
            raise ConfiguredCognitionReadinessError(
                "configured cognition readiness currently requires provider kind openai"
            )
        if item.get("endpoint") != ConfiguredOpenAIAuthenticatedModelProbe.official_responses_endpoint:
            raise ConfiguredCognitionReadinessError(
                "configured cognition readiness requires the exact official Responses endpoint"
            )
        return item

    def _result(
        self,
        current: Mapping[str, Any],
        *,
        status: str,
        reason: str | None,
        age: float | None,
    ) -> ConfiguredCognitionReadinessResult:
        return ConfiguredCognitionReadinessResult(
            status=status,
            reason=reason,
            resource_id=str(current["resource_id"]),
            provider_kind=str(current["provider_kind"]),
            model=str(current["model"]),
            endpoint=str(current["endpoint"]),
            credential_alias=str(current["credential_alias"]),
            observation_age_seconds=age,
            max_age_seconds=self._max_age_seconds,
        )

    def evaluate(self, probe_evidence: Mapping[str, Any]) -> ConfiguredCognitionReadinessResult:
        if not isinstance(probe_evidence, Mapping):
            raise TypeError("probe_evidence must be a mapping")
        current = self._current_binding()

        if probe_evidence.get("schema") != "grox-openai-authenticated-model-probe-v1":
            return self._result(current, status="NOT_READY", reason="invalid_probe_schema", age=None)

        exact_identity = (
            probe_evidence.get("resource_id") == current.get("resource_id")
            and probe_evidence.get("provider_kind") == current.get("provider_kind") == "openai"
            and probe_evidence.get("endpoint") == current.get("endpoint")
            and probe_evidence.get("requested_model") == current.get("model")
            and probe_evidence.get("model_identity") == current.get("model")
            and probe_evidence.get("credential_alias") == current.get("credential_alias")
        )
        if not exact_identity:
            return self._result(
                current,
                status="NOT_READY",
                reason="current_config_identity_changed",
                age=None,
            )

        authenticated_visibility = (
            probe_evidence.get("status") == 200
            and probe_evidence.get("classification") == "authenticated_model_visible"
            and probe_evidence.get("metadata_valid") is True
            and probe_evidence.get("credential_accepted_for_model_visibility") is True
            and probe_evidence.get("credential_rejected") is False
            and probe_evidence.get("credential_use_authorized") is True
            and probe_evidence.get("secret_materialized") is True
            and probe_evidence.get("network_invoked") is True
            and probe_evidence.get("response_body_returned") is False
            and probe_evidence.get("cognition_invoked") is False
        )
        if not authenticated_visibility:
            return self._result(
                current,
                status="NOT_READY",
                reason="authenticated_model_visibility_unproven",
                age=None,
            )

        source_state_separated = (
            probe_evidence.get("ready") is False
            and probe_evidence.get("qualified_fit") is False
            and probe_evidence.get("selected") is False
            and probe_evidence.get("observed") is False
            and probe_evidence.get("authority_changed") is False
            and probe_evidence.get("persistable_readiness_evidence") is False
            and probe_evidence.get("observation_clock") == "process_monotonic"
        )
        if not source_state_separated:
            return self._result(
                current,
                status="NOT_READY",
                reason="probe_state_separation_invalid",
                age=None,
            )

        observed = probe_evidence.get("observed_monotonic_seconds")
        now = self._clock()
        if not self._valid_number(observed) or not self._valid_number(now):
            return self._result(
                current,
                status="NOT_READY",
                reason="invalid_monotonic_observation",
                age=None,
            )
        age = float(now) - float(observed)
        if age < 0.0:
            return self._result(
                current,
                status="NOT_READY",
                reason="future_monotonic_observation",
                age=age,
            )
        if age > self._max_age_seconds:
            return self._result(
                current,
                status="NOT_READY",
                reason="stale_authenticated_model_visibility",
                age=age,
            )
        return self._result(current, status="READY", reason=None, age=age)
