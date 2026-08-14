from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .contracts import RiskClass, TourResult
from .state import StateStore

_RECOVERABLE = {"crew_unavailable", "transient_failure", "TimeoutError", "blocker", "better_or_safer_path", "missing_capability"}
_IRREVERSIBLE = {"irreversible_consequence", "mutation_state_diverged", "authority_violation"}


@dataclass(frozen=True, slots=True)
class ExceptionDecision:
    disposition: str
    reason: str
    requires_commander: bool = False
    consult: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExecutiveExceptionLoop:
    """Deterministic exception policy under GorXu.

    This service does not command Crew and cannot widen Mission authority. It
    classifies a returned exception into a bounded Pilot disposition. The graph
    runtime performs any approved consultation/replan as ordinary Mission Orders.
    """

    def __init__(self, store: StateStore):
        self.store = store

    def decide(self, *, risk: RiskClass, result: TourResult, mutation: bool = False) -> ExceptionDecision:
        exc_type = str((result.exception or {}).get("type") or "unknown")
        material_intent_change = bool((result.exception or {}).get("material_intent_change"))
        irreversible = exc_type in _IRREVERSIBLE or bool((result.exception or {}).get("irreversible"))
        if risk is RiskClass.critical or irreversible or material_intent_change:
            return ExceptionDecision(
                "escalate_commander",
                "critical, irreversible, or material-intent exception requires Commander decision",
                requires_commander=True,
            )
        if mutation and exc_type == "post_repair_test_failure":
            return ExceptionDecision(
                "rollback_then_halt",
                "repair verification failed; compensate the bounded mutation before Pilot review",
            )
        if exc_type in _RECOVERABLE:
            return ExceptionDecision(
                "consult_then_replan",
                "ordinary recoverable Crew/runtime exception; consult evidence before bounded replacement",
                consult=True,
            )
        return ExceptionDecision(
            "pilot_halt",
            "non-critical exception is outside the automatic recovery policy; return to GorXu without Commander escalation",
        )

    def persist(
        self,
        *,
        mission_id: str,
        node_id: str | None,
        order_id: str | None,
        exception_type: str,
        risk: RiskClass,
        decision: ExceptionDecision,
        consulted_crew: str | None = None,
        consultation_order_id: str | None = None,
    ) -> int:
        return self.store.add_exception_decision(
            mission_id=mission_id,
            node_id=node_id,
            order_id=order_id,
            exception_type=exception_type,
            risk=risk.value,
            disposition=decision.disposition,
            reason=decision.reason,
            requires_commander=decision.requires_commander,
            consulted_crew=consulted_crew,
            consultation_order_id=consultation_order_id,
        )
