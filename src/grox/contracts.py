from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
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

@dataclass(slots=True)
class MissionOrder:
    mission_id: str
    order_id: str
    commander_intent: str
    objective: str
    mode: MissionMode
    assigned_crew: str
    required_capabilities: list[str] = field(default_factory=list)
    allowed_actions: tuple[str, ...] = field(default_factory=tuple)
    forbidden_actions: list[str] = field(default_factory=list)
    scope: list[str] = field(default_factory=lambda:["."])
    risk_class: RiskClass = RiskClass.low
    evidence_requirements: list[str] = field(default_factory=lambda:["action_log","result"])
    verification_requirements: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    exception_channel: str = "GorXu"
    parent_order_id: str | None = None
    status: str = "issued"
    parameters: dict[str, Any] = field(default_factory=dict)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "allowed_actions":
            try:
                object.__getattribute__(self, name)
            except AttributeError:
                object.__setattr__(self, name, tuple(value))
                return
            raise AttributeError("allowed_actions is immutable after MissionOrder construction")
        object.__setattr__(self, name, value)

    def __post_init__(self) -> None:
        mutation_grants = sorted(set(self.allowed_actions) & _MUTATING_ACTIONS)
        if self.mode is not MissionMode.repair and mutation_grants:
            raise ValueError(
                f"mutation actions require explicit Repair authority: {mutation_grants}"
            )

    @classmethod
    def new(cls, mission_id: str, commander_intent: str, objective: str, mode: MissionMode,
            assigned_crew: str, **kwargs: Any) -> "MissionOrder":
        return cls(mission_id=mission_id, order_id=f"ORD-{uuid.uuid4().hex[:12]}",
                   commander_intent=commander_intent, objective=objective, mode=mode,
                   assigned_crew=assigned_crew, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value
        d["risk_class"] = self.risk_class.value
        d["allowed_actions"] = list(self.allowed_actions)
        return d

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
