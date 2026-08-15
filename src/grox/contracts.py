from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any
import copy
import json
import uuid


class RiskClass(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class MissionMode(str, Enum):
    inspect = "inspect"
    repair = "repair"
    execute = "execute"
    verify = "verify"


_MUTATING_ACTIONS = frozenset({"fs_write", "mcp_mutate"})
_IMMUTABLE_ORDER_FIELDS = frozenset({
    "mission_id", "order_id", "commander_intent", "objective", "mode", "assigned_crew",
    "required_capabilities", "allowed_actions", "forbidden_actions", "scope", "risk_class",
    "evidence_requirements", "verification_requirements", "stop_conditions", "exception_channel",
    "parent_order_id", "status",
})


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return sorted((_thaw(item) for item in value), key=repr)
    return value


@dataclass(slots=True)
class MissionOrder:
    """Bounded authority contract that seals before persistence or tool use.

    Authority-bearing fields are immutable immediately after construction.
    Parameters may receive bounded pre-issuance context, then are deep-frozen
    when the Order is persisted or first presented to the Tool Gateway.
    """

    mission_id: str
    order_id: str
    commander_intent: str
    objective: str
    mode: MissionMode
    assigned_crew: str
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    allowed_actions: tuple[str, ...] = field(default_factory=tuple)
    forbidden_actions: tuple[str, ...] = field(default_factory=tuple)
    scope: tuple[str, ...] = field(default_factory=lambda: (".",))
    risk_class: RiskClass = RiskClass.low
    evidence_requirements: tuple[str, ...] = field(default_factory=lambda: ("action_log", "result"))
    verification_requirements: tuple[str, ...] = field(default_factory=tuple)
    stop_conditions: tuple[str, ...] = field(default_factory=tuple)
    exception_channel: str = "GorXu"
    parent_order_id: str | None = None
    status: str = "issued"
    parameters: Mapping[str, Any] = field(default_factory=dict)
    _constructed: bool = field(default=False, init=False, repr=False, compare=False)
    _sealed: bool = field(default=False, init=False, repr=False, compare=False)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        try:
            constructed = object.__getattribute__(self, "_constructed")
        except AttributeError:
            constructed = False
        if constructed and name in _IMMUTABLE_ORDER_FIELDS:
            raise AttributeError(f"MissionOrder field is immutable after construction: {name}")
        if constructed and name == "parameters":
            if object.__getattribute__(self, "_sealed"):
                raise AttributeError("MissionOrder parameters are immutable after issuance")
            object.__setattr__(self, name, copy.deepcopy(dict(value)))
            return
        object.__setattr__(self, name, value)

    def __post_init__(self) -> None:
        for name in (
            "required_capabilities", "allowed_actions", "forbidden_actions", "scope",
            "evidence_requirements", "verification_requirements", "stop_conditions",
        ):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, "parameters", copy.deepcopy(dict(self.parameters)))

        mutation_grants = sorted(set(self.allowed_actions) & _MUTATING_ACTIONS)
        if self.mode is not MissionMode.repair and mutation_grants:
            raise ValueError(
                f"mutation actions require explicit Repair authority: {mutation_grants}"
            )
        object.__setattr__(self, "_constructed", True)

    @property
    def sealed(self) -> bool:
        return self._sealed

    def seal(self) -> "MissionOrder":
        if not self._sealed:
            object.__setattr__(self, "parameters", _freeze(dict(self.parameters)))
            object.__setattr__(self, "_sealed", True)
        return self

    @classmethod
    def new(
        cls,
        mission_id: str,
        commander_intent: str,
        objective: str,
        mode: MissionMode,
        assigned_crew: str,
        **kwargs: Any,
    ) -> "MissionOrder":
        return cls(
            mission_id=mission_id,
            order_id=f"ORD-{uuid.uuid4().hex[:12]}",
            commander_intent=commander_intent,
            objective=objective,
            mode=mode,
            assigned_crew=assigned_crew,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "order_id": self.order_id,
            "commander_intent": self.commander_intent,
            "objective": self.objective,
            "mode": self.mode.value,
            "assigned_crew": self.assigned_crew,
            "required_capabilities": list(self.required_capabilities),
            "allowed_actions": list(self.allowed_actions),
            "forbidden_actions": list(self.forbidden_actions),
            "scope": list(self.scope),
            "risk_class": self.risk_class.value,
            "evidence_requirements": list(self.evidence_requirements),
            "verification_requirements": list(self.verification_requirements),
            "stop_conditions": list(self.stop_conditions),
            "exception_channel": self.exception_channel,
            "parent_order_id": self.parent_order_id,
            "status": self.status,
            "parameters": _thaw(self.parameters),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass(slots=True)
class Evidence:
    kind: str
    content: dict[str, Any]


@dataclass(slots=True)
class TourResult:
    order_id: str
    crew_id: str
    status: str
    summary: str
    evidence: list[Evidence] = field(default_factory=list)
    exception: dict[str, Any] | None = None
