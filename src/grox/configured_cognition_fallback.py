from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .configured_cognition_fitness import (
    ConfiguredCognitionFitnessResult,
    ConfiguredCognitionMissionFitness,
)
from .configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionError,
    ConfiguredCognitionSelectionPolicy,
)
from .configured_openai_cognition import (
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from .contracts import MissionOrder
from .selected_configured_cognition import (
    SelectedConfiguredCognition,
    SelectedConfiguredCognitionError,
    SelectedConfiguredCognitionResult,
)
from .tools.layout_gateway import LayoutToolGateway


class ConfiguredCognitionFallbackPolicyError(ValueError):
    """An explicit configured-cognition fallback envelope is malformed."""


class ConfiguredCognitionFallbackError(RuntimeError):
    """Configured cognition fallback stopped or exhausted without safe success."""


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionFallbackPolicy:
    """Finite explicit candidate order for timeout-only fallback.

    The order is the entire fallback envelope. This policy cannot discover,
    authorize, qualify, rank, learn, or append candidates.
    """

    candidate_order: tuple[str, ...]

    max_candidates = 8

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_order, tuple):
            raise ConfiguredCognitionFallbackPolicyError("candidate_order must be a tuple")
        if not 2 <= len(self.candidate_order) <= self.max_candidates:
            raise ConfiguredCognitionFallbackPolicyError(
                f"candidate_order must contain between 2 and {self.max_candidates} resources"
            )
        normalized: list[str] = []
        seen: set[str] = set()
        for resource_id in self.candidate_order:
            if not isinstance(resource_id, str) or not resource_id.strip():
                raise ConfiguredCognitionFallbackPolicyError(
                    "candidate_order entries must be non-empty resource IDs"
                )
            resource_id = resource_id.strip()
            if resource_id in seen:
                raise ConfiguredCognitionFallbackPolicyError(
                    f"candidate_order contains duplicate resource: {resource_id}"
                )
            seen.add(resource_id)
            normalized.append(resource_id)
        object.__setattr__(self, "candidate_order", tuple(normalized))


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionFallbackCandidate:
    """One independently gated candidate inside an explicit fallback envelope."""

    config: Mapping[str, Any]
    gateway: LayoutToolGateway
    qualification: ConfiguredOpenAICognitionResult
    fitness: ConfiguredCognitionFitnessResult
    order: MissionOrder

    def __post_init__(self) -> None:
        if not isinstance(self.config, Mapping):
            raise TypeError("candidate config must be a mapping")
        if not isinstance(self.gateway, LayoutToolGateway):
            raise TypeError("candidate gateway must be a LayoutToolGateway")
        if not isinstance(self.qualification, ConfiguredOpenAICognitionResult):
            raise TypeError("candidate qualification must be a ConfiguredOpenAICognitionResult")
        if not isinstance(self.fitness, ConfiguredCognitionFitnessResult):
            raise TypeError("candidate fitness must be a ConfiguredCognitionFitnessResult")
        if not isinstance(self.order, MissionOrder):
            raise TypeError("candidate order must be a MissionOrder")
        object.__setattr__(self, "config", MappingProxyType(dict(self.config)))

    @property
    def resource_id(self) -> str:
        return self.qualification.resource_id


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionFallbackResult:
    """Successful execution result from one explicit bounded fallback envelope."""

    candidate_order: tuple[str, ...]
    attempted_resource_ids: tuple[str, ...]
    timed_out_resource_ids: tuple[str, ...]
    executed: SelectedConfiguredCognitionResult

    @property
    def switched(self) -> bool:
        return len(self.attempted_resource_ids) > 1

    @property
    def interpretation(self):
        return self.executed.interpretation

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-fallback-v1",
            "candidate_order": list(self.candidate_order),
            "attempted_resource_ids": list(self.attempted_resource_ids),
            "timed_out_resource_ids": list(self.timed_out_resource_ids),
            "executed_resource_id": self.executed.resource_id,
            "executed_observation_id": self.executed.observation_id,
            "mission_id": self.executed.mission_id,
            "order_id": self.executed.order_id,
            "placement": self.executed.placement,
            "selected": True,
            "observed": True,
            "fallback_enabled": True,
            "switching_occurred": self.switched,
            "fallback_reason": "provider_timeout" if self.switched else None,
            "timeout_only_fallback": True,
            "candidate_expansion": False,
            "adaptive_routing_enabled": False,
            "ranking_enabled": False,
            "learning_enabled": False,
            "raw_response_returned": False,
            "credential_material_returned": False,
            "mission_created": False,
            "authority_changed": False,
        }


class ConfiguredCognitionFallback:
    """Execute an explicit finite configured-cognition timeout fallback envelope.

    Every candidate already carries its own successful qualification, PASS
    fitness evidence, exact sealed Mission Order, configured identity, and Tool
    Gateway. This class adds no authority. It selects and invokes candidates only
    in the policy order and advances only after a provider invocation TimeoutError.
    """

    def __init__(
        self,
        candidates: Sequence[ConfiguredCognitionFallbackCandidate],
        policy: ConfiguredCognitionFallbackPolicy,
        *,
        observation_recorder: Callable[..., Any] | None = None,
    ):
        if not isinstance(policy, ConfiguredCognitionFallbackPolicy):
            raise TypeError("policy must be a ConfiguredCognitionFallbackPolicy")
        if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
            raise TypeError("candidates must be a sequence")
        if observation_recorder is not None and not callable(observation_recorder):
            raise TypeError("observation_recorder must be callable or null")
        frozen = tuple(candidates)
        if len(frozen) != len(policy.candidate_order):
            raise ConfiguredCognitionFallbackPolicyError(
                "candidate set must exactly match the explicit fallback envelope"
            )
        if not all(isinstance(candidate, ConfiguredCognitionFallbackCandidate) for candidate in frozen):
            raise TypeError("every candidate must be a ConfiguredCognitionFallbackCandidate")

        by_id: dict[str, ConfiguredCognitionFallbackCandidate] = {}
        mission_id: str | None = None
        commander_intent: str | None = None
        mission_mode = None
        order_ids: set[str] = set()
        for candidate in frozen:
            if candidate.resource_id in by_id:
                raise ConfiguredCognitionFallbackPolicyError(
                    f"duplicate fallback candidate resource: {candidate.resource_id}"
                )
            by_id[candidate.resource_id] = candidate
            order = candidate.order
            qualification = candidate.qualification
            fitness = candidate.fitness
            if not order.sealed:
                raise ConfiguredCognitionFallbackPolicyError(
                    f"fallback candidate Order is not sealed: {candidate.resource_id}"
                )
            if order.order_id in order_ids:
                raise ConfiguredCognitionFallbackPolicyError(
                    "fallback candidates require distinct independently bound Order IDs"
                )
            order_ids.add(order.order_id)
            if mission_id is None:
                mission_id = order.mission_id
                commander_intent = order.commander_intent
                mission_mode = order.mode
            elif (
                order.mission_id != mission_id
                or order.commander_intent != commander_intent
                or order.mode is not mission_mode
            ):
                raise ConfiguredCognitionFallbackPolicyError(
                    "all fallback candidates must preserve one Mission, exact Commander intent and Mission mode"
                )
            if not (
                qualification.mission_id == order.mission_id
                and qualification.order_id == order.order_id
                and fitness.mission_id == order.mission_id
                and fitness.order_id == order.order_id
                and fitness.resource_id == qualification.resource_id
                and fitness.provider_kind == qualification.provider_kind
                and fitness.model == qualification.model
                and fitness.endpoint == qualification.endpoint
                and fitness.credential_alias == qualification.credential_alias
                and fitness.placement == ConfiguredCognitionMissionFitness.placement
                and fitness.qualified_fit
            ):
                raise ConfiguredCognitionFallbackPolicyError(
                    f"fallback candidate lacks exact successful PASS fitness evidence: {candidate.resource_id}"
                )

        if tuple(by_id) != tuple(candidate.resource_id for candidate in frozen):
            raise AssertionError("candidate identity normalization drift")
        if set(by_id) != set(policy.candidate_order):
            raise ConfiguredCognitionFallbackPolicyError(
                "explicit fallback policy and supplied candidate resources differ"
            )

        self._candidates = MappingProxyType(by_id)
        self._policy = policy
        self._observation_recorder = observation_recorder

    @staticmethod
    def _is_recoverable_provider_timeout(exc: SelectedConfiguredCognitionError) -> bool:
        """Allow fallback only for the exact selected-provider timeout cause chain."""
        cognition_error = exc.__cause__
        return (
            isinstance(cognition_error, ConfiguredOpenAICognitionError)
            and isinstance(cognition_error.__cause__, TimeoutError)
        )

    def invoke(self, *, roster: list[dict[str, Any]]) -> ConfiguredCognitionFallbackResult:
        if not isinstance(roster, list) or not all(isinstance(item, dict) for item in roster):
            raise TypeError("roster must be a list of mappings")

        attempted: list[str] = []
        timed_out: list[str] = []
        for index, resource_id in enumerate(self._policy.candidate_order):
            candidate = self._candidates[resource_id]
            selector = ConfiguredCognitionSelection(candidate.config)
            try:
                selection = selector.select(
                    candidate.qualification,
                    candidate.fitness,
                    order=candidate.order,
                    policy=ConfiguredCognitionSelectionPolicy(resource_id=resource_id),
                )
            except ConfiguredCognitionSelectionError as exc:
                raise ConfiguredCognitionFallbackError(
                    f"fallback candidate failed exact selection before invocation: {resource_id}"
                ) from exc

            runner = SelectedConfiguredCognition(
                candidate.config,
                candidate.gateway,
                selector,
                observation_recorder=self._observation_recorder,
            )
            attempted.append(resource_id)
            try:
                executed = runner.invoke(
                    selection,
                    order=candidate.order,
                    roster=roster,
                )
            except SelectedConfiguredCognitionError as exc:
                if not self._is_recoverable_provider_timeout(exc):
                    raise ConfiguredCognitionFallbackError(
                        f"fallback stopped on non-recoverable candidate failure: {resource_id}"
                    ) from exc
                timed_out.append(resource_id)
                if index + 1 >= len(self._policy.candidate_order):
                    raise ConfiguredCognitionFallbackError(
                        "explicit configured cognition fallback envelope exhausted on provider timeouts"
                    ) from exc
                continue

            return ConfiguredCognitionFallbackResult(
                candidate_order=self._policy.candidate_order,
                attempted_resource_ids=tuple(attempted),
                timed_out_resource_ids=tuple(timed_out),
                executed=executed,
            )

        raise ConfiguredCognitionFallbackError(
            "explicit configured cognition fallback envelope produced no execution"
        )
