from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .configured_cognition_fitness import ConfiguredCognitionMissionFitness
from .configured_cognition_selection import (
    ConfiguredCognitionSelection,
    ConfiguredCognitionSelectionError,
    ConfiguredCognitionSelectionResult,
)
from .configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionError,
    ConfiguredOpenAICognitionResult,
)
from .contracts import MissionOrder
from .credential_binding import ConfiguredCredentialBinding
from .reasoning.contracts import MissionInterpretation
from .tools.layout_gateway import LayoutToolGateway


class SelectedConfiguredCognitionError(RuntimeError):
    """Selected configured cognition could not be invoked or observed safely."""


@dataclass(frozen=True, slots=True)
class SelectedConfiguredCognitionResult:
    """One exact selected invocation with privacy-minimized observation evidence."""

    observation_id: str
    selection_id: str
    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    mission_id: str
    order_id: str
    placement: str
    response_id: str | None
    response_model: str | None
    _interpretation: MissionInterpretation = field(repr=False, compare=False)

    @property
    def interpretation(self) -> MissionInterpretation:
        return self._interpretation

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-selected-configured-cognition-v1",
            "observation_id": self.observation_id,
            "selection_id": self.selection_id,
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "mission_id": self.mission_id,
            "order_id": self.order_id,
            "placement": self.placement,
            "response_id": self.response_id,
            "response_model": self.response_model,
            "discovered": True,
            "authorized": True,
            "ready": True,
            "qualified_fit": True,
            "selected": True,
            "observed": True,
            "secret_materialized": True,
            "network_invoked": True,
            "cognition_invoked": True,
            "cognition_succeeded": True,
            "raw_response_returned": False,
            "fallback_enabled": False,
            "switching_enabled": False,
            "adaptive_routing_enabled": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }


class SelectedConfiguredCognition:
    """Invoke only the exact still-active selected configured cognition resource.

    This seam composes the existing volatile selection and governed configured
    OpenAI cognition path. It does not duplicate authorization, secret handling,
    transport, fallback, switching, or routing. Observation is recorded only
    after the actual invocation returns the exact selected execution identity.
    """

    resource_kind = "configured_remote_cognition"

    def __init__(
        self,
        config: Mapping[str, Any],
        gateway: LayoutToolGateway,
        selection_state: ConfiguredCognitionSelection,
        *,
        observation_recorder: Callable[..., Any] | None = None,
    ):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        if not isinstance(gateway, LayoutToolGateway):
            raise TypeError("gateway must be a LayoutToolGateway")
        if not isinstance(selection_state, ConfiguredCognitionSelection):
            raise TypeError("selection_state must be a ConfiguredCognitionSelection")
        if observation_recorder is not None and not callable(observation_recorder):
            raise TypeError("observation_recorder must be callable or null")
        self._binding = ConfiguredCredentialBinding(config)
        self._cognition = ConfiguredOpenAICognition(config, gateway)
        self._selection_state = selection_state
        self._observation_recorder = observation_recorder
        self._observed: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _current_binding_matches(
        binding: Mapping[str, Any],
        selection: ConfiguredCognitionSelectionResult,
    ) -> bool:
        return (
            binding.get("discovered") is True
            and binding.get("resource_id") == selection.resource_id
            and binding.get("provider_kind") == selection.provider_kind
            and binding.get("model") == selection.model
            and binding.get("endpoint") == selection.endpoint
            and binding.get("credential_alias") == selection.credential_alias
        )

    @staticmethod
    def _result_identity_matches(
        result: ConfiguredOpenAICognitionResult,
        selection: ConfiguredCognitionSelectionResult,
        order: MissionOrder,
    ) -> bool:
        return (
            result.resource_id == selection.resource_id
            and result.provider_kind == selection.provider_kind
            and result.model == selection.model
            and result.endpoint == selection.endpoint
            and result.credential_alias == selection.credential_alias
            and result.mission_id == selection.mission_id == order.mission_id
            and result.order_id == selection.order_id == order.order_id
            and selection.placement == ConfiguredCognitionMissionFitness.placement
            and (result.response_model is None or result.response_model == selection.model)
        )

    def invoke(
        self,
        selection: ConfiguredCognitionSelectionResult,
        *,
        order: MissionOrder,
        roster: list[dict[str, Any]],
    ) -> SelectedConfiguredCognitionResult:
        if not isinstance(selection, ConfiguredCognitionSelectionResult):
            raise TypeError("selection must be a ConfiguredCognitionSelectionResult")
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not isinstance(roster, list) or not all(isinstance(item, dict) for item in roster):
            raise TypeError("roster must be a list of mappings")

        # This must remain the first operational gate. A stale/reconstituted or
        # foreign handle must fail before current binding discovery and, most
        # importantly, before any governed secret/network/provider activity.
        try:
            self._selection_state.validate_active(selection, order=order)
        except ConfiguredCognitionSelectionError as exc:
            raise SelectedConfiguredCognitionError(
                "selected configured cognition requires an active exact selection"
            ) from exc

        current = self._binding.inventory()
        resources = current.get("resources") or []
        if current.get("status") != "ok" or len(resources) != 1:
            raise SelectedConfiguredCognitionError(
                "selected configured cognition is no longer exactly bound"
            )
        if not self._current_binding_matches(resources[0], selection):
            raise SelectedConfiguredCognitionError(
                "current configured cognition binding differs from selected identity"
            )

        parameters = order.parameters
        if not (
            order.sealed
            and parameters.get("operation") == ConfiguredOpenAICognition.operation
            and parameters.get("resource_id") == selection.resource_id
            and parameters.get("provider_kind") == selection.provider_kind
            and parameters.get("model") == selection.model
            and parameters.get("endpoint") == selection.endpoint
            and parameters.get("credential_alias") == selection.credential_alias
        ):
            raise SelectedConfiguredCognitionError(
                "sealed Mission Order no longer binds the selected configured cognition identity"
            )

        try:
            result = self._cognition.invoke(order=order, roster=roster)
        except ConfiguredOpenAICognitionError as exc:
            raise SelectedConfiguredCognitionError(
                "selected configured cognition invocation failed closed"
            ) from exc

        if not self._result_identity_matches(result, selection, order):
            raise SelectedConfiguredCognitionError(
                "actual configured cognition invocation identity differs from selection"
            )

        observation_id = "OBS-" + uuid4().hex[:20]
        identity = {
            "observation_id": observation_id,
            "selection_id": selection.selection_id,
            "resource_id": result.resource_id,
            "resource_kind": self.resource_kind,
            "provider_kind": result.provider_kind,
            "model": result.model,
            "endpoint": result.endpoint,
            "mission_id": result.mission_id,
            "order_id": result.order_id,
            "placement": selection.placement,
            "response_id": result.response_id,
            "response_model": result.response_model,
            "authority_changed": False,
        }
        if self._observation_recorder is not None:
            try:
                self._observation_recorder(
                    resource_id=result.resource_id,
                    resource_kind=self.resource_kind,
                    placement=selection.placement,
                    identity=dict(identity),
                )
            except Exception as exc:
                raise SelectedConfiguredCognitionError(
                    f"selected cognition observation persistence failed: {type(exc).__name__}: {exc}"
                ) from exc
        self._observed[observation_id] = dict(identity)

        return SelectedConfiguredCognitionResult(
            observation_id=observation_id,
            selection_id=selection.selection_id,
            resource_id=result.resource_id,
            provider_kind=result.provider_kind,
            model=result.model,
            endpoint=result.endpoint,
            mission_id=result.mission_id,
            order_id=result.order_id,
            placement=selection.placement,
            response_id=result.response_id,
            response_model=result.response_model,
            _interpretation=result.interpretation,
        )

    def observation(self, observation_id: str) -> dict[str, Any]:
        """Return one process-local privacy-minimized observed identity."""
        if not isinstance(observation_id, str) or not observation_id:
            raise ValueError("observation_id must be a non-empty string")
        try:
            return dict(self._observed[observation_id])
        except KeyError as exc:
            raise SelectedConfiguredCognitionError("configured cognition observation is unknown") from exc
