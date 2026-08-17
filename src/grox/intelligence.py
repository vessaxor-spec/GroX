from __future__ import annotations

import re
from types import MappingProxyType
from dataclasses import dataclass
from typing import Any, Iterable

from .contracts import MissionOrder, RiskClass, TourResult
from .crew.roster import CrewDossier, CrewRoster
from .state import StateStore

_GENERIC_TAGS = {
    "analysis", "code", "engineer", "engineering", "evidence", "inspect",
    "repair", "review", "service", "verify", "write",
}
_RISK_RANK = {RiskClass.low: 0, RiskClass.medium: 1, RiskClass.high: 2, RiskClass.critical: 3}

_ROUTING_COMPONENT_KEYS = ("competence", "reliability", "evidence_quality", "load", "cost", "latency", "risk", "experience", "preference")
DEFAULT_ROUTING_WEIGHTS = MappingProxyType({key: 1.0 for key in _ROUTING_COMPONENT_KEYS})

def weighted_routing_score(components: dict[str, float], weights: dict[str, float] | None = None) -> float:
    effective = {**DEFAULT_ROUTING_WEIGHTS, **(weights or {})}
    unknown = set(effective) - set(_ROUTING_COMPONENT_KEYS)
    if unknown:
        raise ValueError(f"unknown routing weight(s): {sorted(unknown)}")
    for key, value in effective.items():
        value = float(value)
        if not 0.0 <= value <= 10.0:
            raise ValueError(f"routing weight {key} must be between 0 and 10")
        effective[key] = value
    return sum(float(components.get(key, 0.0)) * effective[key] for key in _ROUTING_COMPONENT_KEYS)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_-]+", text.lower())


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    crew: CrewDossier
    task_class: str
    score: float
    components: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "crew_id": self.crew.crew_id,
            "task_class": self.task_class,
            "score": round(self.score, 6),
            "components": {k: round(v, 6) for k, v in self.components.items()},
        }


class LivingCompanyIntelligence:
    """Evidence-backed memory retrieval and experienced Crew ranking under GorXu."""

    def __init__(self, store: StateStore, roster: CrewRoster, *, memory_items: int = 6, memory_chars: int = 3000):
        self.store = store
        self.roster = roster
        self.memory_items = max(1, int(memory_items))
        self.memory_chars = max(256, int(memory_chars))
        self._known_tags = {tag for crew in roster.all() for tag in crew.tags}

    def task_class(self, objective: str) -> str:
        tokens = _words(objective)
        for token in tokens:
            if token in self._known_tags and token not in _GENERIC_TAGS:
                return token
        return "general"

    def remember(
        self,
        *,
        kind: str,
        memory_key: str,
        content: str,
        scope: str = "vessel",
        crew_id: str | None = None,
        task_class: str | None = None,
        provenance: dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> int:
        return self.store.remember(
            kind=kind,
            scope=scope,
            crew_id=crew_id,
            task_class=task_class,
            memory_key=memory_key,
            content=content,
            provenance=provenance or {},
            confidence=confidence,
        )

    def _memory_candidates(self, crew_id: str, objective: str, task_class: str) -> list[tuple[float, dict[str, Any]]]:
        objective_words = set(_words(objective))
        ranked: list[tuple[float, dict[str, Any]]] = []
        for memory in self.store.memories_for(crew_id):
            content_words = set(_words(memory["content"]))
            overlap = len(objective_words & content_words)
            class_match = bool(memory.get("task_class") and memory["task_class"] == task_class)
            if not overlap and not class_match:
                continue
            score = overlap * 2.0 + (6.0 if class_match else 0.0) + float(memory.get("confidence", 1.0))
            if memory["scope"] == "crew":
                score += 0.5
            ranked.append((score, {
                "memory_id": memory["id"],
                "kind": memory["kind"],
                "scope": memory["scope"],
                "task_class": memory.get("task_class"),
                "content": memory["content"],
                "provenance": memory["provenance"],
                "confidence": memory["confidence"],
            }))

        for note in self.store.episodic_notes(crew_id, limit=20):
            content = str(note.get("note") or "")
            overlap = len(objective_words & set(_words(content)))
            if not overlap:
                continue
            ranked.append((overlap * 1.5, {
                "memory_id": None,
                "kind": "episodic",
                "scope": "crew",
                "task_class": None,
                "content": content,
                "provenance": {"mission_id": note.get("mission_id"), "at": note.get("at")},
                "confidence": 1.0,
            }))
        ranked.sort(key=lambda item: (-item[0], -(item[1]["memory_id"] or 0), item[1]["kind"]))
        return ranked

    def memory_context(self, crew_id: str, objective: str, *, task_class: str | None = None) -> list[dict[str, Any]]:
        task_class = task_class or self.task_class(objective)
        ranked = self._memory_candidates(crew_id, objective, task_class)
        representatives: dict[str, tuple[float, dict[str, Any]]] = {}
        for score, item in ranked:
            representatives.setdefault(item["kind"], (score, item))
        diverse = sorted(representatives.values(), key=lambda entry: (-entry[0], entry[1]["kind"]))
        representative_keys = {(item["kind"], item["memory_id"], item["content"]) for _, item in diverse}
        ordered = diverse + [
            entry for entry in ranked
            if (entry[1]["kind"], entry[1]["memory_id"], entry[1]["content"]) not in representative_keys
        ]

        selected: list[dict[str, Any]] = []
        used_chars = 0
        for _, item in ordered:
            item_chars = len(item["content"])
            if selected and used_chars + item_chars > self.memory_chars:
                continue
            if not selected and item_chars > self.memory_chars:
                item = dict(item)
                item["content"] = item["content"][: self.memory_chars]
                item_chars = len(item["content"])
            selected.append(item)
            used_chars += item_chars
            if len(selected) >= self.memory_items:
                break
        return selected

    def inject_order_context(self, order: MissionOrder, objective: str) -> dict[str, Any]:
        task_class = self.task_class(objective)
        memory = self.memory_context(order.assigned_crew, objective, task_class=task_class)
        order.parameters = {
            **dict(order.parameters),
            "_task_class": task_class,
            "_memory_context": memory,
        }
        return {"task_class": task_class, "memory_count": len(memory), "memory_ids": [m["memory_id"] for m in memory if m["memory_id"] is not None]}

    def record_performance(
        self,
        *,
        crew_id: str,
        mission_id: str,
        order_id: str,
        task_class: str,
        result: TourResult,
        latency_ms: float,
        risk: RiskClass,
        verified: bool | None = None,
        cost_units: float = 0.0,
    ) -> None:
        kinds = {e.kind for e in result.evidence}
        evidence_quality = min(1.0, len(kinds) / 3.0)
        tests = [e for e in result.evidence if e.kind == "test_run"]
        if tests and all(e.content.get("returncode") == 0 for e in tests):
            evidence_quality = min(1.0, evidence_quality + 0.25)
        self.store.record_performance(
            crew_id=crew_id,
            mission_id=mission_id,
            order_id=order_id,
            task_class=task_class,
            status=result.status,
            evidence_quality=evidence_quality,
            verified=verified,
            latency_ms=latency_ms,
            cost_units=max(0.0, float(cost_units)),
            risk=risk.value,
        )

    def mark_verified(self, order_id: str, ok: bool) -> None:
        self.store.mark_performance_verified(order_id, ok)

    def _static_competence(self, crew: CrewDossier, objective: str, required: set[str]) -> float:
        words = set(_words(objective))
        return float(len(words & crew.tags) * 4 + len(required & crew.capabilities) * 3)

    def route(
        self,
        objective: str,
        required: Iterable[str] = (),
        *,
        exclude: Iterable[str] = (),
        verifier: bool = False,
        risk: RiskClass = RiskClass.low,
        preferred_ids: Iterable[str] = (),
    ) -> RoutingDecision:
        required_set = set(required)
        excluded = set(exclude)
        preferred = list(preferred_ids)
        preferred_rank = {crew_id: index for index, crew_id in enumerate(preferred)}
        task_class = self.task_class(objective)
        states = {row["crew_id"]: row for row in self.store.crew_states()}
        candidates: list[tuple[float, str, RoutingDecision]] = []
        eligible = [
            crew for crew in self.roster.all()
            if crew.crew_id not in excluded
            and (crew.verification if verifier else crew.ordinary_routing)
            and (not required_set or required_set.issubset(crew.capabilities))
        ]
        if preferred:
            preferred_eligible = [crew for crew in eligible if crew.crew_id in preferred_rank]
            if preferred_eligible:
                eligible = preferred_eligible

        for crew in eligible:
            summary = self.store.performance_summary(crew.crew_id, task_class)
            samples = summary["samples"]
            success_rate = summary["success_rate"] if samples else 0.5
            evidence_quality = summary["evidence_quality"] if samples else 0.5
            verification_rate = summary["verification_rate"] if summary["verified_samples"] else 0.5
            latency_ms = summary["latency_ms"] if samples else 0.0
            cost_units = summary["cost_units"] if samples else 0.0
            is_loaded = states.get(crew.crew_id, {}).get("status") == "on_duty"
            risk_rank = _RISK_RANK[risk]

            components = {
                "competence": self._static_competence(crew, objective, required_set),
                "reliability": (success_rate - 0.5) * 8.0 if samples else 0.0,
                "evidence_quality": (evidence_quality - 0.5) * 4.0 if samples else 0.0,
                "load": -6.0 if is_loaded else 0.0,
                "cost": -min(cost_units, 20.0) * 0.25 if samples else 0.0,
                "latency": -min(latency_ms / 1000.0, 10.0) * 0.25 if samples else 0.0,
                "risk": risk_rank * (((success_rate - 0.5) * 2.0) + ((verification_rate - 0.5) * 2.0)) if samples else 0.0,
                "experience": min(samples, 10) * 0.2,
                "preference": max(0.0, 0.75 - preferred_rank[crew.crew_id] * 0.1) if crew.crew_id in preferred_rank else 0.0,
            }
            score = weighted_routing_score(components)
            decision = RoutingDecision(crew=crew, task_class=task_class, score=score, components=components)
            candidates.append((score, crew.crew_id, decision))

        if not candidates:
            raise LookupError(f"No standing Crew covers required capabilities: {sorted(required_set)}")
        candidates.sort(key=lambda item: (-item[0], item[1]))
        return candidates[0][2]