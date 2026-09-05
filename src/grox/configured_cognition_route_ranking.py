from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from types import MappingProxyType

from .configured_cognition_attempt_performance import ConfiguredCognitionAttemptPerformance
from .configured_cognition_route_plan import ConfiguredCognitionRoutePlanResult


class ConfiguredCognitionRouteRankingError(RuntimeError):
    """Configured cognition route history cannot be ranked safely."""


class ConfiguredCognitionRouteRanker:
    """Deterministically rank only the candidates already present in a current READY route.

    History is advisory evidence, never authority. A candidate is matched only by
    exact configured identity including credential alias and placement. The ranker
    refuses current-Mission evidence and duplicate attempt identities. It changes
    order only when every current READY candidate has the configured minimum exact
    sample count; otherwise the existing policy order is preserved.
    """

    default_min_exact_samples = 2
    max_exact_samples = 2_000

    def __init__(
        self,
        route: ConfiguredCognitionRoutePlanResult,
        history: Sequence[ConfiguredCognitionAttemptPerformance],
        *,
        min_exact_samples: int = default_min_exact_samples,
    ):
        if not isinstance(route, ConfiguredCognitionRoutePlanResult):
            raise TypeError("route must be a ConfiguredCognitionRoutePlanResult")
        if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
            raise TypeError("history must be a sequence")
        if len(history) > self.max_exact_samples:
            raise ConfiguredCognitionRouteRankingError("configured cognition ranking history is unbounded")
        if not all(isinstance(item, ConfiguredCognitionAttemptPerformance) for item in history):
            raise TypeError("every history item must be ConfiguredCognitionAttemptPerformance")
        if not isinstance(min_exact_samples, int) or isinstance(min_exact_samples, bool):
            raise TypeError("min_exact_samples must be an integer")
        if min_exact_samples < 1 or min_exact_samples > 100:
            raise ValueError("min_exact_samples must be between 1 and 100")
        if route.ranking_evaluated:
            raise ConfiguredCognitionRouteRankingError("configured cognition route has already been ranked")

        self._route = route
        self._history = tuple(history)
        self._min_exact_samples = min_exact_samples
        self._validate_route_shape()
        self._validate_history_identity()

    def _validate_route_shape(self) -> None:
        candidates = self._route.ready_candidates
        ids = tuple(candidate.resource_id for candidate in candidates)
        if not candidates or ids != self._route.ready_resource_ids:
            raise ConfiguredCognitionRouteRankingError(
                "current route READY candidate identity does not match route order"
            )
        if len(set(ids)) != len(ids):
            raise ConfiguredCognitionRouteRankingError("current route contains duplicate READY resources")
        if self._route.primary_resource_id != ids[0]:
            raise ConfiguredCognitionRouteRankingError("current route primary identity drifted")
        if self._route.fallback_resource_ids != ids[1:]:
            raise ConfiguredCognitionRouteRankingError("current route fallback identity drifted")

    def _validate_history_identity(self) -> None:
        seen: set[tuple[str, str, str]] = set()
        for item in self._history:
            if item.mission_id == self._route.mission_id:
                raise ConfiguredCognitionRouteRankingError(
                    "current-Mission attempt evidence cannot influence current route ranking"
                )
            key = (item.mission_id, item.order_id, item.selection_id)
            if key in seen:
                raise ConfiguredCognitionRouteRankingError(
                    "duplicate configured cognition attempt identity cannot influence ranking"
                )
            seen.add(key)

    @staticmethod
    def _matches_current_candidate(item, candidate) -> bool:
        qualification = candidate.qualification
        return (
            item.resource_id == qualification.resource_id
            and item.provider_kind == qualification.provider_kind
            and item.model == qualification.model
            and item.endpoint == qualification.endpoint
            and item.credential_alias == qualification.credential_alias
            and item.placement == candidate.fitness.placement
        )

    @staticmethod
    def _laplace_reliability(items: tuple[ConfiguredCognitionAttemptPerformance, ...]) -> float:
        successes = sum(item.succeeded for item in items)
        return (successes + 1.0) / (len(items) + 2.0)

    def rank(self) -> ConfiguredCognitionRoutePlanResult:
        baseline = self._route.ready_resource_ids
        samples: dict[str, tuple[ConfiguredCognitionAttemptPerformance, ...]] = {}
        sample_counts: dict[str, int] = {}

        for candidate in self._route.ready_candidates:
            exact = tuple(
                item for item in self._history
                if self._matches_current_candidate(item, candidate)
            )
            samples[candidate.resource_id] = exact
            sample_counts[candidate.resource_id] = len(exact)

        if any(count < self._min_exact_samples for count in sample_counts.values()):
            return replace(
                self._route,
                baseline_ready_resource_ids=baseline,
                ranking_sample_counts=MappingProxyType(dict(sample_counts)),
                ranking_scores=MappingProxyType({}),
                ranking_evaluated=True,
                ranking_applied=False,
                ranking_reason="insufficient_exact_history",
            )

        scores = {
            resource_id: self._laplace_reliability(items)
            for resource_id, items in samples.items()
        }
        baseline_position = {resource_id: index for index, resource_id in enumerate(baseline)}
        ranked_candidates = tuple(
            sorted(
                self._route.ready_candidates,
                key=lambda candidate: (
                    -scores[candidate.resource_id],
                    baseline_position[candidate.resource_id],
                ),
            )
        )
        ranked_ids = tuple(candidate.resource_id for candidate in ranked_candidates)
        return replace(
            self._route,
            ready_resource_ids=ranked_ids,
            primary_resource_id=ranked_ids[0],
            fallback_resource_ids=ranked_ids[1:],
            _ready_candidates=ranked_candidates,
            baseline_ready_resource_ids=baseline,
            ranking_sample_counts=MappingProxyType(dict(sample_counts)),
            ranking_scores=MappingProxyType(dict(scores)),
            ranking_evaluated=True,
            ranking_applied=True,
            ranking_reason="exact_timeout_reliability",
        )
