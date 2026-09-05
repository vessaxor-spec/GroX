from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import time
from types import MappingProxyType
from typing import Any

from .configured_cognition_attempt import ConfiguredCognitionAttempt
from .configured_cognition_attempt_performance import ConfiguredCognitionAttemptPerformance
from .configured_cognition_fallback import (
    ConfiguredCognitionFallback,
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackError,
)
from .configured_cognition_fitness import ConfiguredCognitionMissionFitness
from .configured_cognition_readiness import (
    ConfiguredCognitionReadiness,
    ConfiguredCognitionReadinessError,
    ConfiguredCognitionReadinessResult,
)
from .configured_cognition_route_plan import ConfiguredCognitionRoutePlanResult
from .configured_cognition_selection import ConfiguredCognitionSelectionError
from .selected_configured_cognition import (
    SelectedConfiguredCognitionError,
    SelectedConfiguredCognitionResult,
)


class ConfiguredCognitionRouteExecutionError(RuntimeError):
    """A planned configured-cognition route could not be attempted safely."""

    def __init__(
        self,
        message: str,
        *,
        resource_id: str | None = None,
        reason: str | None = None,
        observation_age_seconds: float | None = None,
    ):
        super().__init__(message)
        self.resource_id = resource_id
        self.reason = reason
        self.observation_age_seconds = observation_age_seconds


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionRouteExecutionResult:
    """Successful execution of one exact current planned cognition route."""

    candidate_order: tuple[str, ...]
    attempted_resource_ids: tuple[str, ...]
    timed_out_resource_ids: tuple[str, ...]
    attempt_readiness_age_seconds: Mapping[str, float]
    attempt_performance: tuple[ConfiguredCognitionAttemptPerformance, ...]
    executed: SelectedConfiguredCognitionResult

    @property
    def switched(self) -> bool:
        return len(self.attempted_resource_ids) > 1

    @property
    def interpretation(self):
        return self.executed.interpretation

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-route-execution-v1",
            "candidate_order": list(self.candidate_order),
            "attempted_resource_ids": list(self.attempted_resource_ids),
            "timed_out_resource_ids": list(self.timed_out_resource_ids),
            "attempt_readiness_age_seconds": dict(self.attempt_readiness_age_seconds),
            "attempt_performance": [item.evidence() for item in self.attempt_performance],
            "executed_resource_id": self.executed.resource_id,
            "executed_observation_id": self.executed.observation_id,
            "mission_id": self.executed.mission_id,
            "order_id": self.executed.order_id,
            "placement": self.executed.placement,
            "fresh_readiness_revalidated_per_attempt": True,
            "readiness_scope": "authenticated_model_visibility",
            "freshness_clock": "process_monotonic",
            "ready_at_plan_time_not_sufficient": True,
            "selected": True,
            "observed": True,
            "switching_occurred": self.switched,
            "fallback_reason": "provider_timeout" if self.switched else None,
            "timeout_only_fallback": True,
            "candidate_expansion": False,
            "adaptive_routing_enabled": False,
            "ranking_enabled": False,
            "learning_enabled": False,
            "mission_created": False,
            "authority_changed": False,
        }


class ConfiguredCognitionRouteExecution:
    """Execute a planned route only while every attempted candidate is freshly READY.

    A route plan is a volatile policy-order snapshot, not an execution permit. This
    seam re-evaluates the authenticated model-visibility evidence immediately before
    each actual candidate attempt. A failed freshness gate stops the route before
    selection and therefore before governed secret/network/provider activity. Only
    an actual selected-provider TimeoutError may advance to the next planned
    candidate, which is then re-evaluated at its own later attempt instant.
    """

    def __init__(
        self,
        route: ConfiguredCognitionRoutePlanResult,
        probe_evidence: Mapping[str, Mapping[str, Any]],
        *,
        clock: Callable[[], float] | None = None,
        max_age_seconds: float = ConfiguredCognitionReadiness.default_max_age_seconds,
        observation_recorder: Callable[..., Any] | None = None,
    ):
        if not isinstance(route, ConfiguredCognitionRoutePlanResult):
            raise TypeError("route must be a ConfiguredCognitionRoutePlanResult")
        if not isinstance(probe_evidence, Mapping):
            raise TypeError("probe_evidence must be a mapping keyed by resource ID")
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable or null")
        if observation_recorder is not None and not callable(observation_recorder):
            raise TypeError("observation_recorder must be callable or null")

        self._route = route
        self._probe_evidence = MappingProxyType(dict(probe_evidence))
        self._clock = clock or time.monotonic
        self._max_age_seconds = max_age_seconds
        self._observation_recorder = observation_recorder
        self._attempt_ages: dict[str, float] = {}
        self._validate_route_shape()

    def _validate_route_shape(self) -> None:
        candidates = self._route.ready_candidates
        candidate_ids = tuple(candidate.resource_id for candidate in candidates)
        if not candidates or candidate_ids != self._route.ready_resource_ids:
            raise ConfiguredCognitionRouteExecutionError(
                "route ready-candidate identity does not match planned resource order"
            )
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ConfiguredCognitionRouteExecutionError("planned route contains duplicate resources")
        if self._route.primary_resource_id != candidate_ids[0]:
            raise ConfiguredCognitionRouteExecutionError("planned primary identity drifted")
        if self._route.fallback_resource_ids != candidate_ids[1:]:
            raise ConfiguredCognitionRouteExecutionError("planned fallback identity drifted")
        if self._route.placement != ConfiguredCognitionMissionFitness.placement:
            raise ConfiguredCognitionRouteExecutionError(
                "configured cognition route execution is qualified only for mission_interpretation"
            )
        for candidate in candidates:
            if (
                candidate.order.mission_id != self._route.mission_id
                or candidate.qualification.mission_id != self._route.mission_id
                or candidate.fitness.mission_id != self._route.mission_id
                or candidate.fitness.placement != self._route.placement
            ):
                raise ConfiguredCognitionRouteExecutionError(
                    "planned candidate Mission or placement identity drifted",
                    resource_id=candidate.resource_id,
                    reason="planned_identity_drift",
                )
        if len(candidate_ids) >= 2:
            policy = self._route.fallback_policy
            if policy is None or policy.candidate_order != candidate_ids:
                raise ConfiguredCognitionRouteExecutionError(
                    "planned fallback policy does not exactly match ready candidate order"
                )
        elif self._route.fallback_policy is not None:
            raise ConfiguredCognitionRouteExecutionError(
                "single-candidate route must not carry a fallback policy"
            )

    @staticmethod
    def _readiness_identity_exact(
        candidate: ConfiguredCognitionFallbackCandidate,
        readiness: ConfiguredCognitionReadinessResult,
    ) -> bool:
        qualification = candidate.qualification
        return (
            readiness.resource_id == qualification.resource_id
            and readiness.provider_kind == qualification.provider_kind == "openai"
            and readiness.model == qualification.model
            and readiness.endpoint == qualification.endpoint
            and readiness.credential_alias == qualification.credential_alias
        )

    def _require_fresh_attempt(self, candidate: ConfiguredCognitionFallbackCandidate) -> None:
        probe = self._probe_evidence.get(candidate.resource_id)
        if not isinstance(probe, Mapping):
            raise ConfiguredCognitionRouteExecutionError(
                "planned candidate lacks valid authenticated readiness evidence at attempt time",
                resource_id=candidate.resource_id,
                reason="readiness_evidence_missing_or_invalid",
            )
        try:
            readiness = ConfiguredCognitionReadiness(
                candidate.config,
                clock=self._clock,
                max_age_seconds=self._max_age_seconds,
            ).evaluate(probe)
        except (ConfiguredCognitionReadinessError, TypeError, ValueError) as exc:
            raise ConfiguredCognitionRouteExecutionError(
                "planned candidate readiness could not be re-evaluated at attempt time",
                resource_id=candidate.resource_id,
                reason="readiness_evaluation_failed",
            ) from exc
        if not self._readiness_identity_exact(candidate, readiness):
            raise ConfiguredCognitionRouteExecutionError(
                "planned candidate readiness identity changed before attempt",
                resource_id=candidate.resource_id,
                reason="readiness_identity_mismatch",
                observation_age_seconds=readiness.observation_age_seconds,
            )
        if not readiness.ready:
            raise ConfiguredCognitionRouteExecutionError(
                "planned candidate is no longer freshly ready at attempt time",
                resource_id=candidate.resource_id,
                reason=readiness.reason or "provider_not_ready",
                observation_age_seconds=readiness.observation_age_seconds,
            )
        if readiness.observation_age_seconds is None:
            raise ConfiguredCognitionRouteExecutionError(
                "fresh readiness lacks an observation age",
                resource_id=candidate.resource_id,
                reason="readiness_age_missing",
            )
        self._attempt_ages[candidate.resource_id] = readiness.observation_age_seconds

    def _single_candidate(
        self,
        candidate: ConfiguredCognitionFallbackCandidate,
        *,
        roster: list[dict[str, Any]],
    ) -> ConfiguredCognitionRouteExecutionResult:
        self._require_fresh_attempt(candidate)
        attempt = ConfiguredCognitionAttempt(
            candidate.config,
            candidate.gateway,
            candidate.qualification,
            candidate.fitness,
            candidate.order,
            observation_recorder=self._observation_recorder,
        )
        try:
            selection = attempt.select()
        except ConfiguredCognitionSelectionError as exc:
            raise ConfiguredCognitionRouteExecutionError(
                "planned primary failed exact selection before invocation",
                resource_id=candidate.resource_id,
                reason="selection_failed",
            ) from exc
        try:
            executed = attempt.invoke_selected(selection, roster=roster)
        except SelectedConfiguredCognitionError as exc:
            raise ConfiguredCognitionRouteExecutionError(
                "planned primary invocation failed closed",
                resource_id=candidate.resource_id,
                reason="selected_invocation_failed",
            ) from exc
        performance = ConfiguredCognitionAttemptPerformance(
            resource_id=candidate.qualification.resource_id,
            provider_kind=candidate.qualification.provider_kind,
            model=candidate.qualification.model,
            endpoint=candidate.qualification.endpoint,
            credential_alias=candidate.qualification.credential_alias,
            mission_id=candidate.order.mission_id,
            order_id=candidate.order.order_id,
            selection_id=selection.selection_id,
            placement=candidate.fitness.placement,
            outcome="success",
            observation_id=executed.observation_id,
        )
        return ConfiguredCognitionRouteExecutionResult(
            candidate_order=(candidate.resource_id,),
            attempted_resource_ids=(candidate.resource_id,),
            timed_out_resource_ids=(),
            attempt_readiness_age_seconds=MappingProxyType(dict(self._attempt_ages)),
            attempt_performance=(performance,),
            executed=executed,
        )

    def invoke(self, *, roster: list[dict[str, Any]]) -> ConfiguredCognitionRouteExecutionResult:
        if not isinstance(roster, list) or not all(isinstance(item, dict) for item in roster):
            raise TypeError("roster must be a list of mappings")

        candidates = self._route.ready_candidates
        if len(candidates) == 1:
            return self._single_candidate(candidates[0], roster=roster)

        policy = self._route.fallback_policy
        if policy is None:
            raise ConfiguredCognitionRouteExecutionError("multi-candidate route lacks exact fallback policy")
        fallback = ConfiguredCognitionFallback(
            candidates,
            policy,
            observation_recorder=self._observation_recorder,
            pre_attempt_gate=self._require_fresh_attempt,
        )
        try:
            result = fallback.invoke(roster=roster)
        except ConfiguredCognitionFallbackError as exc:
            if isinstance(exc.__cause__, ConfiguredCognitionRouteExecutionError):
                gate_error = exc.__cause__
                raise ConfiguredCognitionRouteExecutionError(
                    str(gate_error),
                    resource_id=gate_error.resource_id,
                    reason=gate_error.reason,
                    observation_age_seconds=gate_error.observation_age_seconds,
                ) from exc
            raise ConfiguredCognitionRouteExecutionError(
                "planned configured cognition route stopped without safe success",
                reason="fallback_execution_failed",
            ) from exc

        return ConfiguredCognitionRouteExecutionResult(
            candidate_order=result.candidate_order,
            attempted_resource_ids=result.attempted_resource_ids,
            timed_out_resource_ids=result.timed_out_resource_ids,
            attempt_readiness_age_seconds=MappingProxyType(dict(self._attempt_ages)),
            attempt_performance=result.attempt_performance,
            executed=result.executed,
        )
