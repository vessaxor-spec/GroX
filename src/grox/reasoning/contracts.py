from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

_VALID_MODES = {"inspect", "repair", "execute", "verify"}
_VALID_RISKS = {"low", "medium", "high", "critical"}


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return value


@dataclass(slots=True)
class StrategyOption:
    name: str
    rationale: str
    advantages: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    crew_ids: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "StrategyOption":
        if not isinstance(raw, dict):
            raise ValueError("strategy option must be an object")
        name = raw.get("name")
        rationale = raw.get("rationale")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("strategy option name is required")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("strategy option rationale is required")
        return cls(
            name=name.strip(),
            rationale=rationale.strip(),
            advantages=_string_list(raw.get("advantages"), "advantages"),
            risks=_string_list(raw.get("risks"), "risks"),
            crew_ids=_string_list(raw.get("crew_ids"), "crew_ids"),
        )


@dataclass(slots=True)
class MissionInterpretation:
    commander_intent: str
    objective: str
    ambiguous: bool
    ambiguities: list[str]
    assumptions: list[str]
    information_needs: list[str]
    candidate_crew_ids: list[str]
    options: list[StrategyOption]
    recommended_option: str
    confidence: float
    proposed_mode: str | None = None
    proposed_risk: str | None = None

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], *, expected_intent: str) -> "MissionInterpretation":
        if not isinstance(raw, dict):
            raise ValueError("mission interpretation must be an object")
        commander_intent = raw.get("commander_intent")
        if commander_intent != expected_intent:
            raise ValueError("reasoner must preserve Commander intent verbatim")
        objective = raw.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError("objective is required")
        ambiguous = raw.get("ambiguous")
        if not isinstance(ambiguous, bool):
            raise ValueError("ambiguous must be boolean")
        confidence = raw.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            raise ValueError("confidence must be numeric")
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        proposed_mode = raw.get("proposed_mode")
        if proposed_mode is not None and proposed_mode not in _VALID_MODES:
            raise ValueError("invalid proposed_mode")
        proposed_risk = raw.get("proposed_risk")
        if proposed_risk is not None and proposed_risk not in _VALID_RISKS:
            raise ValueError("invalid proposed_risk")
        options_raw = raw.get("options") or []
        if not isinstance(options_raw, list):
            raise ValueError("options must be a list")
        options = [StrategyOption.from_mapping(x) for x in options_raw]
        recommended = raw.get("recommended_option")
        if not isinstance(recommended, str):
            raise ValueError("recommended_option must be a string")
        if options and recommended not in {x.name for x in options}:
            raise ValueError("recommended_option must name one of the options")
        return cls(
            commander_intent=commander_intent,
            objective=objective.strip(),
            ambiguous=ambiguous,
            ambiguities=_string_list(raw.get("ambiguities"), "ambiguities"),
            assumptions=_string_list(raw.get("assumptions"), "assumptions"),
            information_needs=_string_list(raw.get("information_needs"), "information_needs"),
            candidate_crew_ids=_string_list(raw.get("candidate_crew_ids"), "candidate_crew_ids"),
            options=options,
            recommended_option=recommended,
            confidence=confidence,
            proposed_mode=proposed_mode,
            proposed_risk=proposed_risk,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def json_schema() -> dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "commander_intent": {"type": "string", "description": "Repeat the Commander directive exactly, byte for byte."},
                "objective": {"type": "string", "description": "Concise operational interpretation of the requested outcome."},
                "ambiguous": {"type": "boolean"},
                "ambiguities": {"type": "array", "items": {"type": "string"}},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "information_needs": {"type": "array", "items": {"type": "string"}},
                "candidate_crew_ids": {"type": "array", "items": {"type": "string"}, "description": "Ordered Crew IDs from the supplied roster only."},
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "rationale": {"type": "string", "description": "Decision rationale only; do not expose private chain-of-thought."},
                            "advantages": {"type": "array", "items": {"type": "string"}},
                            "risks": {"type": "array", "items": {"type": "string"}},
                            "crew_ids": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "rationale", "advantages", "risks", "crew_ids"],
                    },
                },
                "recommended_option": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "proposed_mode": {"type": ["string", "null"], "enum": ["inspect", "repair", "execute", "verify", None]},
                "proposed_risk": {"type": ["string", "null"], "enum": ["low", "medium", "high", "critical", None]},
            },
            "required": [
                "commander_intent", "objective", "ambiguous", "ambiguities", "assumptions",
                "information_needs", "candidate_crew_ids", "options", "recommended_option",
                "confidence", "proposed_mode", "proposed_risk"
            ],
        }
