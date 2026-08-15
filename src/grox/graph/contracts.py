from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Any

from ..contracts import MissionMode, RiskClass

_MUTATING_ACTIONS = frozenset({"fs_write", "mcp_mutate"})


@dataclass(slots=True)
class NodeBudget:
    max_attempts: int = 2
    max_seconds: int = 120
    cost_units: float = 1.0

    @classmethod
    def from_mapping(cls, raw: dict[str, Any] | None) -> "NodeBudget":
        raw = raw or {}
        max_attempts = int(raw.get("max_attempts", 2))
        max_seconds = int(raw.get("max_seconds", 120))
        cost_units = float(raw.get("cost_units", 1.0))
        if not 1 <= max_attempts <= 5:
            raise ValueError("node max_attempts must be between 1 and 5")
        if not 1 <= max_seconds <= 3600:
            raise ValueError("node max_seconds must be between 1 and 3600")
        if not math.isfinite(cost_units) or not 0.0 <= cost_units <= 1_000_000.0:
            raise ValueError("node cost_units must be finite and between 0 and 1000000")
        return cls(max_attempts=max_attempts, max_seconds=max_seconds, cost_units=cost_units)


@dataclass(slots=True)
class MissionBudget:
    max_nodes: int = 20
    max_parallel: int = 4
    max_replans: int = 3
    max_cost_units: float = 100.0

    @classmethod
    def from_mapping(cls, raw: dict[str, Any] | None) -> "MissionBudget":
        raw = raw or {}
        max_nodes = int(raw.get("max_nodes", 20))
        max_parallel = int(raw.get("max_parallel", 4))
        max_replans = int(raw.get("max_replans", 3))
        max_cost_units = float(raw.get("max_cost_units", 100.0))
        if not 1 <= max_nodes <= 100:
            raise ValueError("mission max_nodes must be between 1 and 100")
        if not 1 <= max_parallel <= 16:
            raise ValueError("mission max_parallel must be between 1 and 16")
        if not 0 <= max_replans <= 20:
            raise ValueError("mission max_replans must be between 0 and 20")
        if not math.isfinite(max_cost_units) or not 0.0 <= max_cost_units <= 100_000_000.0:
            raise ValueError("mission max_cost_units must be finite and between 0 and 100000000")
        return cls(
            max_nodes=max_nodes,
            max_parallel=max_parallel,
            max_replans=max_replans,
            max_cost_units=max_cost_units,
        )


@dataclass(slots=True)
class GraphNodeSpec:
    node_id: str
    objective: str
    mode: MissionMode
    dependencies: list[str] = field(default_factory=list)
    candidate_crew_ids: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=lambda: ["repo_read"])
    allowed_actions: list[str] = field(default_factory=list)
    scope: list[str] = field(default_factory=lambda: ["."])
    risk_class: RiskClass = RiskClass.low
    stop_conditions: list[str] = field(default_factory=lambda: [
        "blocker", "better_or_safer_path", "missing_capability", "elevated_risk",
        "scope_change", "irreversible_consequence",
    ])
    parameters: dict[str, Any] = field(default_factory=dict)
    budget: NodeBudget = field(default_factory=NodeBudget)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "GraphNodeSpec":
        if not isinstance(raw, dict):
            raise ValueError("graph node must be an object")
        node_id = raw.get("node_id")
        objective = raw.get("objective")
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("graph node_id is required")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError(f"graph node {node_id}: objective is required")
        try:
            mode = MissionMode(raw.get("mode", "inspect"))
            risk = RiskClass(raw.get("risk_class", "low"))
        except ValueError as exc:
            raise ValueError(f"graph node {node_id}: invalid mode or risk") from exc
        dependencies = raw.get("dependencies") or []
        candidates = raw.get("candidate_crew_ids") or []
        required = raw.get("required_capabilities") or ["repo_read"]
        allowed = raw.get("allowed_actions") or []
        scope = raw.get("scope") or ["."]
        stop = raw.get("stop_conditions") or [
            "blocker", "better_or_safer_path", "missing_capability", "elevated_risk",
            "scope_change", "irreversible_consequence",
        ]
        for field_name, value in (
            ("dependencies", dependencies), ("candidate_crew_ids", candidates),
            ("required_capabilities", required), ("allowed_actions", allowed), ("scope", scope), ("stop_conditions", stop),
        ):
            if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
                raise ValueError(f"graph node {node_id}: {field_name} must be non-empty strings")
        mutation_grants = sorted(set(allowed) & _MUTATING_ACTIONS)
        if mode is not MissionMode.repair and mutation_grants:
            raise ValueError(
                f"graph node {node_id}: mutation actions require explicit Repair authority: {mutation_grants}"
            )
        parameters = raw.get("parameters") or {}
        if not isinstance(parameters, dict):
            raise ValueError(f"graph node {node_id}: parameters must be an object")
        return cls(
            node_id=node_id.strip(), objective=objective.strip(), mode=mode,
            dependencies=list(dependencies), candidate_crew_ids=list(candidates),
            required_capabilities=list(required), allowed_actions=list(allowed), scope=list(scope), risk_class=risk,
            stop_conditions=list(stop), parameters=dict(parameters),
            budget=NodeBudget.from_mapping(raw.get("budget")),
        )

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["mode"] = self.mode.value
        out["risk_class"] = self.risk_class.value
        return out


@dataclass(slots=True)
class MissionGraphPlan:
    commander_intent: str
    objective: str
    nodes: list[GraphNodeSpec]
    budget: MissionBudget = field(default_factory=MissionBudget)
    rationale: str = ""

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], *, expected_intent: str) -> "MissionGraphPlan":
        if not isinstance(raw, dict):
            raise ValueError("mission graph plan must be an object")
        if raw.get("commander_intent") != expected_intent:
            raise ValueError("graph planner must preserve Commander intent verbatim")
        objective = raw.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError("mission graph objective is required")
        nodes_raw = raw.get("nodes")
        if not isinstance(nodes_raw, list) or not nodes_raw:
            raise ValueError("mission graph requires at least one node")
        nodes = [GraphNodeSpec.from_mapping(x) for x in nodes_raw]
        plan = cls(
            commander_intent=expected_intent,
            objective=objective.strip(),
            nodes=nodes,
            budget=MissionBudget.from_mapping(raw.get("budget")),
            rationale=str(raw.get("rationale") or "").strip(),
        )
        plan.validate()
        return plan

    def validate(self) -> None:
        if len(self.nodes) > self.budget.max_nodes:
            raise ValueError("mission graph exceeds node budget")
        ids = [n.node_id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("mission graph node IDs must be unique")
        known = set(ids)
        for node in self.nodes:
            mutation_grants = sorted(set(node.allowed_actions) & _MUTATING_ACTIONS)
            if node.mode is not MissionMode.repair and mutation_grants:
                raise ValueError(
                    f"graph node {node.node_id}: mutation actions require explicit Repair authority: {mutation_grants}"
                )
            unknown = set(node.dependencies) - known
            if unknown:
                raise ValueError(f"graph node {node.node_id} has unknown dependencies: {sorted(unknown)}")
            if node.node_id in node.dependencies:
                raise ValueError(f"graph node {node.node_id} cannot depend on itself")

        visiting: set[str] = set()
        visited: set[str] = set()
        deps = {n.node_id: n.dependencies for n in self.nodes}

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            if node_id in visiting:
                raise ValueError("mission graph must be acyclic")
            visiting.add(node_id)
            for dep in deps[node_id]:
                visit(dep)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in ids:
            visit(node_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "commander_intent": self.commander_intent,
            "objective": self.objective,
            "rationale": self.rationale,
            "budget": asdict(self.budget),
            "nodes": [n.to_dict() for n in self.nodes],
        }


@dataclass(slots=True)
class GraphNodeOutcome:
    node_id: str
    order_id: str
    crew_id: str
    status: str
    summary: str
    evidence_kinds: list[str]
    exception: dict[str, Any] | None = None
    attempt: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PilotSynthesis:
    outcome: str
    executive_summary: str
    completed_nodes: list[str]
    unresolved_nodes: list[str]
    crew_used: list[str]
    replans: int
    verification_passed: bool
    evidence_kinds: list[str]
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    cost_units: float = 0.0
    cost_budget: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
