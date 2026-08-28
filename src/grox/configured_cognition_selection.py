from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .configured_cognition_fitness import (
    ConfiguredCognitionFitnessResult,
    ConfiguredCognitionMissionFitness,
)
from .configured_openai_cognition import (
    ConfiguredOpenAICognition,
    ConfiguredOpenAICognitionResult,
)
from .contracts import MissionOrder
from .credential_binding import ConfiguredCredentialBinding


class ConfiguredCognitionSelectionPolicyError(ValueError):
    """An explicit configured-cognition selection policy is malformed."""


class ConfiguredCognitionSelectionError(RuntimeError):
    """Configured cognition could not be selected under the current exact gates."""


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionSelectionPolicy:
    """Explicit policy for selecting exactly one configured cognition resource.

    This slice intentionally has no candidate list. Switching, fallback and
    adaptive routing remain separate downstream capabilities.
    """

    resource_id: str
    placement: str = ConfiguredCognitionMissionFitness.placement

    def __post_init__(self) -> None:
        if not isinstance(self.resource_id, str) or not self.resource_id.strip():
            raise ConfiguredCognitionSelectionPolicyError("resource_id must be a non-empty string")
        if not isinstance(self.placement, str) or not self.placement.strip():
            raise ConfiguredCognitionSelectionPolicyError("placement must be a non-empty string")
        object.__setattr__(self, "resource_id", self.resource_id.strip())
        object.__setattr__(self, "placement", self.placement.strip())


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionSelectionResult:
    """Volatile selection handle for one exact configured cognition resource."""

    selection_id: str
    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    mission_id: str
    order_id: str
    placement: str

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-selection-v1",
            "selection_id": self.selection_id,
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "mission_id": self.mission_id,
            "order_id": self.order_id,
            "placement": self.placement,
            "discovered": True,
            "authorized": True,
            "ready": True,
            "qualified_fit": True,
            "selected": True,
            "observed": False,
            "selection_scope": "explicit_single_resource",
            "fallback_enabled": False,
            "switching_enabled": False,
            "adaptive_routing_enabled": False,
            "network_invoked": False,
            "secret_materialized": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }


class ConfiguredCognitionSelection:
    """Select one exact configured cognition resource after all prior gates pass.

    Selection is volatile process-local state. It performs only fresh non-secret
    configured binding discovery and deterministic evidence checks. It never
    invokes cognition, materializes a secret, creates a Mission, marks execution
    observed, scans alternatives, or widens authority.
    """

    def __init__(self, config: Mapping[str, Any]):
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping")
        self._binding = ConfiguredCredentialBinding(config)
        self._active: dict[tuple[str, str, str], tuple[str, str]] = {}

    @staticmethod
    def _order_identity_matches(order: MissionOrder, result: ConfiguredOpenAICognitionResult) -> bool:
        parameters = order.parameters
        return (
            result.mission_id == order.mission_id
            and result.order_id == order.order_id
            and parameters.get("operation") == ConfiguredOpenAICognition.operation
            and parameters.get("resource_id") == result.resource_id
            and parameters.get("provider_kind") == result.provider_kind
            and parameters.get("model") == result.model
            and parameters.get("endpoint") == result.endpoint
            and parameters.get("credential_alias") == result.credential_alias
            and {"cognition_invoke", "net_fetch", "secret_use"}.issubset(set(order.allowed_actions))
        )

    @staticmethod
    def _fitness_identity_matches(
        fitness: ConfiguredCognitionFitnessResult,
        result: ConfiguredOpenAICognitionResult,
    ) -> bool:
        return (
            fitness.resource_id == result.resource_id
            and fitness.provider_kind == result.provider_kind
            and fitness.model == result.model
            and fitness.endpoint == result.endpoint
            and fitness.credential_alias == result.credential_alias
            and fitness.mission_id == result.mission_id
            and fitness.order_id == result.order_id
            and fitness.placement == ConfiguredCognitionMissionFitness.placement
        )

    def select(
        self,
        result: ConfiguredOpenAICognitionResult,
        fitness: ConfiguredCognitionFitnessResult,
        *,
        order: MissionOrder,
        policy: ConfiguredCognitionSelectionPolicy,
    ) -> ConfiguredCognitionSelectionResult:
        if not isinstance(result, ConfiguredOpenAICognitionResult):
            raise TypeError("result must be a ConfiguredOpenAICognitionResult")
        if not isinstance(fitness, ConfiguredCognitionFitnessResult):
            raise TypeError("fitness must be a ConfiguredCognitionFitnessResult")
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not isinstance(policy, ConfiguredCognitionSelectionPolicy):
            raise TypeError("policy must be a ConfiguredCognitionSelectionPolicy")
        if not order.sealed:
            raise ConfiguredCognitionSelectionError(
                "configured cognition selection requires the already sealed source Mission Order"
            )
        if policy.placement != ConfiguredCognitionMissionFitness.placement:
            raise ConfiguredCognitionSelectionError(
                "configured cognition selection is qualified only for mission_interpretation"
            )
        if policy.resource_id != result.resource_id:
            raise ConfiguredCognitionSelectionError("selection policy does not name the exact cognition resource")
        if not self._order_identity_matches(order, result):
            raise ConfiguredCognitionSelectionError("successful cognition evidence does not match the exact source Order")
        if not self._fitness_identity_matches(fitness, result):
            raise ConfiguredCognitionSelectionError("fitness evidence identity does not match successful cognition")
        if not fitness.qualified_fit:
            raise ConfiguredCognitionSelectionError("configured cognition is not qualified fit for selection")

        source = result.evidence()
        fit = fitness.evidence()
        if not (
            source.get("credential_use_authorized") is True
            and source.get("cognition_succeeded") is True
            and source.get("ready") is True
            and source.get("qualified_fit") is False
            and source.get("selected") is False
            and source.get("observed") is False
            and source.get("authority_changed") is False
        ):
            raise ConfiguredCognitionSelectionError("successful cognition evidence does not preserve prior state gates")
        if not (
            fit.get("status") == "PASS"
            and fit.get("qualified_fit") is True
            and fit.get("selected") is False
            and fit.get("observed") is False
            and fit.get("authority_changed") is False
            and fit.get("network_invoked") is False
            and fit.get("secret_materialized") is False
            and fit.get("cognition_invoked") is False
        ):
            raise ConfiguredCognitionSelectionError("fitness evidence is not a pure PASS qualification")

        current = self._binding.inventory()
        resources = current.get("resources") or []
        if current.get("status") != "ok" or len(resources) != 1:
            raise ConfiguredCognitionSelectionError("configured cognition is no longer exactly bound")
        bound = resources[0]
        if not (
            bound.get("discovered") is True
            and bound.get("resource_id") == result.resource_id
            and bound.get("provider_kind") == result.provider_kind
            and bound.get("model") == result.model
            and bound.get("endpoint") == result.endpoint
            and bound.get("credential_alias") == result.credential_alias
        ):
            raise ConfiguredCognitionSelectionError("current configured cognition binding differs from qualified evidence")

        selection_id = "SEL-" + uuid4().hex[:20]
        key = (order.mission_id, order.order_id, policy.placement)
        self._active[key] = (selection_id, result.resource_id)
        return ConfiguredCognitionSelectionResult(
            selection_id=selection_id,
            resource_id=result.resource_id,
            provider_kind=result.provider_kind,
            model=result.model,
            endpoint=result.endpoint,
            credential_alias=result.credential_alias,
            mission_id=result.mission_id,
            order_id=result.order_id,
            placement=policy.placement,
        )

    def validate_active(
        self,
        selection: ConfiguredCognitionSelectionResult,
        *,
        order: MissionOrder,
    ) -> None:
        """Fail closed unless a selection handle is still active in this process."""
        if not isinstance(selection, ConfiguredCognitionSelectionResult):
            raise TypeError("selection must be a ConfiguredCognitionSelectionResult")
        if not isinstance(order, MissionOrder):
            raise TypeError("order must be a MissionOrder")
        if not order.sealed:
            raise ConfiguredCognitionSelectionError("active selection validation requires a sealed Mission Order")
        key = (order.mission_id, order.order_id, selection.placement)
        active = self._active.get(key)
        if (
            active != (selection.selection_id, selection.resource_id)
            or selection.mission_id != order.mission_id
            or selection.order_id != order.order_id
        ):
            raise ConfiguredCognitionSelectionError("configured cognition selection is no longer active")

    def reconstitute(self) -> dict[str, Any]:
        """Clear all volatile selections; no selection survives reconstitution."""
        cleared = len(self._active)
        self._active.clear()
        return {
            "schema": "grox-configured-cognition-selection-reconstitution-v1",
            "cleared_selection_count": cleared,
            "selected": False,
            "observed": False,
            "network_invoked": False,
            "secret_materialized": False,
            "cognition_invoked": False,
            "mission_created": False,
            "authority_changed": False,
            "auto_selection": False,
        }
