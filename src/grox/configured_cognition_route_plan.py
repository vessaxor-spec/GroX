from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import time
from types import MappingProxyType
from typing import Any

from .configured_cognition_fallback import (
    ConfiguredCognitionFallbackCandidate,
    ConfiguredCognitionFallbackPolicy,
)
from .configured_cognition_readiness import (
    ConfiguredCognitionReadiness,
    ConfiguredCognitionReadinessError,
    ConfiguredCognitionReadinessResult,
)
from .configured_cognition_route_admission import ConfiguredCognitionRouteAdmissionResult


class ConfiguredCognitionRoutePlanError(RuntimeError):
    """No safe deterministic route can be planned from current admitted evidence."""

    def __init__(self, message: str, *, rejections: Mapping[str, str] | None = None):
        super().__init__(message)
        self.rejections = MappingProxyType(dict(rejections or {}))


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionRoutePlanResult:
    """Volatile deterministic route plan; never an active selection."""

    candidate_order: tuple[str, ...]
    admitted_resource_ids: tuple[str, ...]
    ready_resource_ids: tuple[str, ...]
    primary_resource_id: str
    fallback_resource_ids: tuple[str, ...]
    not_ready_reasons: Mapping[str, str]
    mission_id: str
    placement: str
    _ready_candidates: tuple[ConfiguredCognitionFallbackCandidate, ...] = field(
        repr=False,
        compare=False,
    )

    @property
    def ready_candidates(self) -> tuple[ConfiguredCognitionFallbackCandidate, ...]:
        return self._ready_candidates

    @property
    def fallback_policy(self) -> ConfiguredCognitionFallbackPolicy | None:
        """Return an exact timeout-fallback envelope only when at least two are ready."""
        if len(self.ready_resource_ids) < 2:
            return None
        return ConfiguredCognitionFallbackPolicy(self.ready_resource_ids)

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-route-plan-v1",
            "candidate_order": list(self.candidate_order),
            "admitted_resource_ids": list(self.admitted_resource_ids),
            "ready_resource_ids": list(self.ready_resource_ids),
            "primary_resource_id": self.primary_resource_id,
            "fallback_resource_ids": list(self.fallback_resource_ids),
            "not_ready_reasons": dict(self.not_ready_reasons),
            "mission_id": self.mission_id,
            "placement": self.placement,
            "route_planned": True,
            "current_admission_required": True,
            "fresh_readiness_revalidated_at_plan_time": True,
            "readiness_scope": "authenticated_model_visibility",
            "freshness_clock": "process_monotonic",
            "deterministic_policy_order": True,
            "active_selection_created": False,
            "selected": False,
            "observed": False,
            "candidate_expansion": False,
            "secret_materialized": False,
            "network_invoked": False,
            "provider_constructed": False,
            "cognition_invoked": False,
            "fallback_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "historical_scoring_used": False,
            "ranking_enabled": False,
            "learning_enabled": False,
            "adaptive_scoring_enabled": False,
        }


class ConfiguredCognitionRoutePlan:
    """Plan primary/fallback order from admitted candidates and current readiness.

    The planner re-evaluates supplied authenticated probe evidence at one captured
    monotonic planning instant. It never trusts a cached READY object and never
    performs provider activity. The first freshly ready candidate in the already
    admitted policy order is the planned primary; later ready candidates retain
    their existing order as planned timeout fallbacks.
    """

    def __init__(
        self,
        admission: ConfiguredCognitionRouteAdmissionResult,
        probe_evidence: Mapping[str, Mapping[str, Any]],
        *,
        clock: Callable[[], float] | None = None,
        max_age_seconds: float = ConfiguredCognitionReadiness.default_max_age_seconds,
    ):
        if not isinstance(admission, ConfiguredCognitionRouteAdmissionResult):
            raise TypeError("admission must be a ConfiguredCognitionRouteAdmissionResult")
        if not isinstance(probe_evidence, Mapping):
            raise TypeError("probe_evidence must be a mapping keyed by resource ID")
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable or null")
        self._admission = admission
        self._probe_evidence = MappingProxyType(dict(probe_evidence))
        self._clock = clock or time.monotonic
        self._max_age_seconds = max_age_seconds
        self._validate_admission_shape()

    def _validate_admission_shape(self) -> None:
        admitted = self._admission.admitted_candidates
        admitted_ids = tuple(candidate.resource_id for candidate in admitted)
        if not admitted or admitted_ids != self._admission.admitted_resource_ids:
            raise ConfiguredCognitionRoutePlanError(
                "route admission candidate identity does not match admitted resource IDs"
            )
        if len(set(admitted_ids)) != len(admitted_ids):
            raise ConfiguredCognitionRoutePlanError("route admission contains duplicate resources")
        policy_positions = {resource_id: index for index, resource_id in enumerate(self._admission.candidate_order)}
        try:
            positions = [policy_positions[resource_id] for resource_id in admitted_ids]
        except KeyError as exc:
            raise ConfiguredCognitionRoutePlanError(
                "admitted resource is absent from original candidate order"
            ) from exc
        if positions != sorted(positions):
            raise ConfiguredCognitionRoutePlanError(
                "admitted resources do not preserve original candidate order"
            )
        for candidate in admitted:
            if (
                candidate.order.mission_id != self._admission.mission_id
                or candidate.fitness.mission_id != self._admission.mission_id
                or candidate.qualification.mission_id != self._admission.mission_id
                or candidate.fitness.placement != self._admission.placement
            ):
                raise ConfiguredCognitionRoutePlanError(
                    "admitted candidate Mission or placement identity drifted"
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

    def plan(self) -> ConfiguredCognitionRoutePlanResult:
        # Capture one planning instant so every candidate is evaluated against the
        # same volatile freshness boundary and candidate iteration cannot age one
        # resource relative to another.
        planning_now = self._clock()
        ready: list[ConfiguredCognitionFallbackCandidate] = []
        rejected: dict[str, str] = {}

        for candidate in self._admission.admitted_candidates:
            resource_id = candidate.resource_id
            probe = self._probe_evidence.get(resource_id)
            if not isinstance(probe, Mapping):
                rejected[resource_id] = "readiness_evidence_missing_or_invalid"
                continue
            try:
                readiness = ConfiguredCognitionReadiness(
                    candidate.config,
                    clock=lambda now=planning_now: now,
                    max_age_seconds=self._max_age_seconds,
                ).evaluate(probe)
            except (ConfiguredCognitionReadinessError, TypeError, ValueError):
                rejected[resource_id] = "readiness_evaluation_failed"
                continue
            if not self._readiness_identity_exact(candidate, readiness):
                rejected[resource_id] = "readiness_identity_mismatch"
                continue
            if not readiness.ready:
                rejected[resource_id] = readiness.reason or "provider_not_ready"
                continue
            ready.append(candidate)

        if not ready:
            raise ConfiguredCognitionRoutePlanError(
                "no admitted configured cognition candidate is freshly ready at route-planning time",
                rejections=rejected,
            )

        ready_ids = tuple(candidate.resource_id for candidate in ready)
        return ConfiguredCognitionRoutePlanResult(
            candidate_order=self._admission.candidate_order,
            admitted_resource_ids=self._admission.admitted_resource_ids,
            ready_resource_ids=ready_ids,
            primary_resource_id=ready_ids[0],
            fallback_resource_ids=ready_ids[1:],
            not_ready_reasons=MappingProxyType(dict(rejected)),
            mission_id=self._admission.mission_id,
            placement=self._admission.placement,
            _ready_candidates=tuple(ready),
        )
