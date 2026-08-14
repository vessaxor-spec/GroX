from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .base import ReasoningError
from .contracts import MissionInterpretation


SessionResponder = Callable[[str, list[dict[str, Any]]], dict[str, Any]]


class SessionReasoningProvider:
    """Bind GorXu cognition to the currently hosting reasoning session.

    This adapter does not authenticate to an external model service. The host
    supplies a responder callback for each live reasoning turn. GroX still
    validates the returned structure and retains deterministic authority,
    risk, tool, and verification controls.
    """

    def __init__(self, responder: SessionResponder, *, name: str = "gpt-5.6-sol-session-high"):
        if not callable(responder):
            raise TypeError("responder must be callable")
        self._responder = responder
        self.name = name

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        try:
            raw = self._responder(directive, roster)
        except Exception as exc:  # host boundary: normalize provider failures
            raise ReasoningError(f"session reasoner failed: {exc}") from exc
        try:
            return MissionInterpretation.from_mapping(raw, expected_intent=directive)
        except (TypeError, ValueError) as exc:
            raise ReasoningError(f"invalid session reasoning output: {exc}") from exc
