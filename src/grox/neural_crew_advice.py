"""Strict, advisory-only NCI-4A Neural Crew decision contract.

This module is intentionally disconnected from Crew execution, Mission Orders,
Tool Gateway, routing, provider registration, and model activation. Its output
may be evaluated, but cannot authorize or perform a tool action.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping


SCHEMA = "grox-neural-crew-advice-v1"
FIELDS = frozenset({
    "schema", "recommended_action", "evidence_sufficient",
    "test_interpretation", "continue_or_stop", "failure_classification",
    "confidence", "requested_evidence",
})
ACTIONS = frozenset({
    "suggest_fs_list", "suggest_fs_read", "suggest_test_run",
    "suggest_finish", "request_evidence", "stop",
})
TEST_INTERPRETATIONS = frozenset({"not_run", "pass", "fail", "inconclusive"})
FAILURE_CLASSES = frozenset({
    "none", "insufficient_evidence", "test_failure", "tool_failure",
    "policy_denied", "unknown",
})
DECISIONS = frozenset({"continue", "stop"})
MAX_EVIDENCE_REQUESTS = 8
MAX_EVIDENCE_LABEL_CHARS = 128


class NeuralCrewAdviceError(ValueError):
    """Malformed, ambiguous, or authority-bearing advisory output."""


@dataclass(frozen=True, slots=True)
class NeuralCrewAdvice:
    """Validated observation/recommendation, never an executable order."""

    recommended_action: str
    evidence_sufficient: bool
    test_interpretation: str
    continue_or_stop: str
    failure_classification: str
    confidence: float
    requested_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.recommended_action) is not str or self.recommended_action not in ACTIONS:
            raise NeuralCrewAdviceError("unsupported advisory action")
        if type(self.evidence_sufficient) is not bool:
            raise NeuralCrewAdviceError("evidence_sufficient must be boolean")
        if type(self.test_interpretation) is not str or self.test_interpretation not in TEST_INTERPRETATIONS:
            raise NeuralCrewAdviceError("unsupported test interpretation")
        if type(self.continue_or_stop) is not str or self.continue_or_stop not in DECISIONS:
            raise NeuralCrewAdviceError("unsupported continue_or_stop decision")
        if type(self.failure_classification) is not str or self.failure_classification not in FAILURE_CLASSES:
            raise NeuralCrewAdviceError("unsupported failure classification")
        if (
            type(self.confidence) not in (int, float)
            or not 0 <= self.confidence <= 1
            or not math.isfinite(self.confidence)
        ):
            raise NeuralCrewAdviceError("confidence must be a finite number in [0, 1]")
        if (
            type(self.requested_evidence) is not tuple
            or len(self.requested_evidence) > MAX_EVIDENCE_REQUESTS
        ):
            raise NeuralCrewAdviceError("requested_evidence must be a bounded tuple")
        for label in self.requested_evidence:
            if (
                not isinstance(label, str)
                or not label.strip()
                or label != label.strip()
                or len(label) > MAX_EVIDENCE_LABEL_CHARS
                or any(ord(char) < 32 for char in label)
            ):
                raise NeuralCrewAdviceError("invalid requested evidence label")
        if len(set(self.requested_evidence)) != len(self.requested_evidence):
            raise NeuralCrewAdviceError("duplicate requested evidence label")
        if self.recommended_action in {"stop", "suggest_finish"} and self.continue_or_stop != "stop":
            raise NeuralCrewAdviceError("stop/finish advice must stop")
        if self.recommended_action == "suggest_finish" and not self.evidence_sufficient:
            raise NeuralCrewAdviceError("finish advice requires sufficient evidence")
        if self.recommended_action == "request_evidence":
            if self.evidence_sufficient or not self.requested_evidence:
                raise NeuralCrewAdviceError("request_evidence needs missing evidence")
            if self.continue_or_stop != "continue":
                raise NeuralCrewAdviceError("request_evidence must continue")
        elif self.requested_evidence:
            raise NeuralCrewAdviceError("only request_evidence may carry requested_evidence")
        if self.failure_classification == "policy_denied" and self.continue_or_stop != "stop":
            raise NeuralCrewAdviceError("policy denial must stop")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "NeuralCrewAdvice":
        """Accept only the exact versioned schema; reject all authority fields."""
        if not isinstance(raw, Mapping):
            raise NeuralCrewAdviceError("Neural Crew advice must be a mapping")
        if raw.keys() != FIELDS:
            missing = sorted(FIELDS - raw.keys())
            extra = sorted(set(raw.keys()) - FIELDS, key=str)
            raise NeuralCrewAdviceError(f"advice fields mismatch (missing={missing}, extra={extra})")
        if raw["schema"] != SCHEMA:
            raise NeuralCrewAdviceError("unsupported Neural Crew advice schema")
        requests = raw["requested_evidence"]
        if type(requests) is not list:
            raise NeuralCrewAdviceError("requested_evidence must be a list")
        return cls(
            recommended_action=raw["recommended_action"],
            evidence_sufficient=raw["evidence_sufficient"],
            test_interpretation=raw["test_interpretation"],
            continue_or_stop=raw["continue_or_stop"],
            failure_classification=raw["failure_classification"],
            confidence=raw["confidence"],
            requested_evidence=tuple(requests),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "recommended_action": self.recommended_action,
            "evidence_sufficient": self.evidence_sufficient,
            "test_interpretation": self.test_interpretation,
            "continue_or_stop": self.continue_or_stop,
            "failure_classification": self.failure_classification,
            "confidence": float(self.confidence),
            "requested_evidence": list(self.requested_evidence),
        }
