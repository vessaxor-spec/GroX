from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


HOT = "hot"
WARM = "warm"
COLD = "cold"

# These meanings remain current even when their source record is old. Age alone
# can never cool them below HOT while they are active/currently binding.
_ALWAYS_HOT_KINDS = {
    "commander_intent",
    "commander_constraint",
    "authority",
    "active_mission_state",
    "active_graph_state",
    "unresolved_exception",
    "unresolved_contradiction",
    "critical_evidence",
    "safety_boundary",
    "next_action",
}

_WARM_KINDS = {
    "decision",
    "crew_finding",
    "memory",
    "completed_node_summary",
    "relevant_history",
    "verification_summary",
}


@dataclass(frozen=True, slots=True)
class ContextItem:
    item_id: str
    kind: str
    content: str
    provenance: str
    summary: str | None = None
    active: bool = False
    relevant: bool = False
    critical: bool = False
    required_facts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("context item_id is required")
        if not self.kind.strip():
            raise ValueError("context kind is required")
        if not self.content.strip():
            raise ValueError("context content is required")
        if not self.provenance.strip():
            raise ValueError("context provenance is required")


@dataclass(frozen=True, slots=True)
class PackedContextItem:
    item_id: str
    kind: str
    heat: str
    text: str
    provenance: str
    compressed: bool
    required_facts: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ContextPack:
    items: tuple[PackedContextItem, ...]
    omitted_ids: tuple[str, ...]
    original_chars: int
    packed_chars: int

    @property
    def char_reduction(self) -> int:
        return max(0, self.original_chars - self.packed_chars)

    @property
    def reduction_ratio(self) -> float:
        if self.original_chars <= 0:
            return 0.0
        return round(self.char_reduction / self.original_chars, 4)

    @property
    def retained_ids(self) -> tuple[str, ...]:
        return tuple(item.item_id for item in self.items)

    def to_dict(self) -> dict:
        return {
            "items": [item.to_dict() for item in self.items],
            "omitted_ids": list(self.omitted_ids),
            "original_chars": self.original_chars,
            "packed_chars": self.packed_chars,
            "char_reduction": self.char_reduction,
            "reduction_ratio": self.reduction_ratio,
            "retained_ids": list(self.retained_ids),
        }


@dataclass(frozen=True, slots=True)
class PreservationResult:
    passed: bool
    missing_required_facts: tuple[str, ...]
    missing_provenance: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


class ContextHeatPolicy:
    """Deterministic experimental heat classification and bounded packing.

    This policy is deliberately not wired into Pilot runtime. It is a pure
    evidence experiment for Stage 4. HOT material is retained verbatim. WARM
    material may use a caller-provided attributable summary. COLD material is
    omitted. Critical/active binding material can never become COLD merely
    because it is old.
    """

    def classify(self, item: ContextItem) -> str:
        if item.critical or (item.active and item.kind in _ALWAYS_HOT_KINDS):
            return HOT
        if item.kind in _ALWAYS_HOT_KINDS and (item.active or item.relevant):
            return HOT
        if item.kind in _WARM_KINDS and item.relevant:
            return WARM
        return COLD

    def pack(self, items: Iterable[ContextItem]) -> ContextPack:
        source = tuple(items)
        packed: list[PackedContextItem] = []
        omitted: list[str] = []
        for item in source:
            heat = self.classify(item)
            if heat == COLD:
                omitted.append(item.item_id)
                continue
            if heat == HOT:
                text = item.content
                compressed = False
            else:
                # Only an attributable summary supplied with the source item may
                # replace WARM raw text. Absence of a summary keeps raw text.
                text = item.summary.strip() if item.summary and item.summary.strip() else item.content
                compressed = text != item.content
            packed.append(
                PackedContextItem(
                    item_id=item.item_id,
                    kind=item.kind,
                    heat=heat,
                    text=text,
                    provenance=item.provenance,
                    compressed=compressed,
                    required_facts=item.required_facts,
                )
            )
        return ContextPack(
            items=tuple(packed),
            omitted_ids=tuple(omitted),
            original_chars=sum(len(item.content) for item in source),
            packed_chars=sum(len(item.text) for item in packed),
        )

    @staticmethod
    def audit_preservation(pack: ContextPack, required_facts: Iterable[str]) -> PreservationResult:
        text = "\n".join(item.text for item in pack.items)
        required = tuple(dict.fromkeys(str(fact) for fact in required_facts if str(fact)))
        missing = tuple(fact for fact in required if fact not in text)
        missing_provenance = tuple(item.item_id for item in pack.items if not item.provenance.strip())
        return PreservationResult(not missing and not missing_provenance, missing, missing_provenance)
