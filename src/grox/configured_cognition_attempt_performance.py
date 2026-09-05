from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ConfiguredCognitionAttemptPerformanceError(ValueError):
    """Attempt-performance evidence is malformed or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class ConfiguredCognitionAttemptPerformance:
    """Privacy-minimized exact identity and outcome for one actual provider attempt."""

    resource_id: str
    provider_kind: str
    model: str
    endpoint: str
    credential_alias: str
    mission_id: str
    order_id: str
    selection_id: str
    placement: str
    outcome: str
    observation_id: str | None = None

    _OUTCOMES = frozenset({"success", "provider_timeout"})

    def __post_init__(self) -> None:
        for name in (
            "resource_id",
            "provider_kind",
            "model",
            "endpoint",
            "credential_alias",
            "mission_id",
            "order_id",
            "selection_id",
            "placement",
            "outcome",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ConfiguredCognitionAttemptPerformanceError(f"{name} must be a non-empty string")
            object.__setattr__(self, name, value.strip())
        if self.outcome not in self._OUTCOMES:
            raise ConfiguredCognitionAttemptPerformanceError(
                f"unsupported configured cognition attempt outcome: {self.outcome}"
            )
        if self.outcome == "success":
            if not isinstance(self.observation_id, str) or not self.observation_id.strip():
                raise ConfiguredCognitionAttemptPerformanceError(
                    "successful attempt performance requires an observation_id"
                )
            object.__setattr__(self, "observation_id", self.observation_id.strip())
        elif self.observation_id is not None:
            raise ConfiguredCognitionAttemptPerformanceError(
                "provider timeout performance must not carry an observation_id"
            )

    @property
    def succeeded(self) -> bool:
        return self.outcome == "success"

    @property
    def timed_out(self) -> bool:
        return self.outcome == "provider_timeout"

    def evidence(self) -> dict[str, Any]:
        return {
            "schema": "grox-configured-cognition-attempt-performance-v1",
            "resource_id": self.resource_id,
            "provider_kind": self.provider_kind,
            "model": self.model,
            "endpoint": self.endpoint,
            "credential_alias": self.credential_alias,
            "mission_id": self.mission_id,
            "order_id": self.order_id,
            "selection_id": self.selection_id,
            "placement": self.placement,
            "outcome": self.outcome,
            "observation_id": self.observation_id,
            "actual_provider_attempt": True,
            "provider_succeeded": self.succeeded,
            "provider_timed_out": self.timed_out,
            "raw_response_returned": False,
            "credential_material_returned": False,
            "secret_value_returned": False,
            "ranking_applied": False,
            "learning_applied": False,
            "candidate_expansion": False,
            "authority_changed": False,
        }
