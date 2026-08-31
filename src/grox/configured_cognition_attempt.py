from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .configured_cognition_fitness import ConfiguredCognitionFitnessResult
from .configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionPolicy,
    ConfiguredCognitionSelectionResult,
)
from .configured_openai_cognition import ConfiguredOpenAICognitionResult
from .contracts import MissionOrder
from .selected_configured_cognition import (
    SelectedConfiguredCognition,
    SelectedConfiguredCognitionResult,
)
from .tools.layout_gateway import LayoutToolGateway


class ConfiguredCognitionAttempt:
    """Shared exact selection-and-invocation seam for one configured candidate.

    This class deliberately adds no routing, readiness, fallback, or authority.
    Callers remain responsible for proving any additional pre-attempt gates before
    invoking this seam. It exists so direct route execution and timeout fallback
    use the same exact selection and selected-provider implementation.
    """

    def __init__(
        self,
        config: Mapping[str, Any],
        gateway: LayoutToolGateway,
        qualification: ConfiguredOpenAICognitionResult,
        fitness: ConfiguredCognitionFitnessResult,
        order: MissionOrder,
        *,
        observation_recorder: Callable[..., Any] | None = None,
    ):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, LayoutToolGateway):
            raise TypeError("gateway must be a LayoutToolGateway")
        if not isinstance(qualification, ConfiguredOpenAICognitionResult):
            raise TypeError("qualification must be a ConfiguredOpenAICognitionResult")
        if not isinstance(fitness, ConfiguredCognitionFitnessResult):
            raise TypeError("fitness must be a ConfiguredCognitionFitnessResult")
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if observation_recorder is not None and not callable(observation_recorder):
            raise TypeError("observation_recorder must be callable or null")

        self._qualification = qualification
        self._fitness = fitness
        self._order = order
        self._selector = ConfiguredCognitionSelection(config)
        self._runner = SelectedConfiguredCognition(
            config,
            gateway,
            self._selector,
            observation_recorder=observation_recorder,
        )

    @property
    def resource_id(self) -> str:
        return self._qualification.resource_id

    def select(self) -> ConfiguredCognitionSelectionResult:
        """Create one volatile exact selection under the existing selection gates."""
        return self._selector.select(
            self._qualification,
            self._fitness,
            order=self._order,
            policy=ConfiguredCognitionSelectionPolicy(resource_id=self.resource_id),
        )

    def invoke_selected(
        self,
        selection: ConfiguredCognitionSelectionResult,
        *,
        roster: list[dict[str, Any]],
    ) -> SelectedConfiguredCognitionResult:
        """Invoke only the supplied still-active selection through the existing seam."""
        return self._runner.invoke(
            selection,
            order=self._order,
            roster=roster,
        )

    def invoke(self, *, roster: list[dict[str, Any]]) -> SelectedConfiguredCognitionResult:
        """Select then invoke one exact candidate; no routing or fallback is performed."""
        return self.invoke_selected(self.select(), roster=roster)
