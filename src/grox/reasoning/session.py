from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .base import ReasoningError
from .contracts import MissionInterpretation
from ..graph import MissionGraphPlan


SessionResponder = Callable[[str, list[dict[str, Any]]], dict[str, Any]]
GraphSessionResponder = Callable[[str, list[dict[str, Any]]], dict[str, Any]]


class SessionReasoningProvider:
    """Bind GorXu cognition to the currently hosting reasoning session.

    The host may supply separate callbacks for A1 interpretation and A2 Mission
    Graph planning. GroX validates both outputs and retains deterministic
    authority, risk, tool, verification, and graph-budget controls.

    Recoverable provider failures must be raised by callbacks as ReasoningError.
    Unexpected callback defects are deliberately allowed to reach GorXu's outer
    containment boundary so they retain traceback and defect classification.
    """

    def __init__(
        self,
        responder: SessionResponder,
        *,
        graph_responder: GraphSessionResponder | None = None,
        name: str = "gpt-5.6-sol-session-high",
    ):
        if not callable(responder):
            raise TypeError("responder must be callable")
        if graph_responder is not None and not callable(graph_responder):
            raise TypeError("graph_responder must be callable")
        self._responder = responder
        self._graph_responder = graph_responder
        self.name = name

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        raw = self._responder(directive, roster)
        try:
            return MissionInterpretation.from_mapping(raw, expected_intent=directive)
        except (TypeError, ValueError) as exc:
            raise ReasoningError(f"invalid session reasoning output: {exc}") from exc

    def plan_graph(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionGraphPlan:
        if self._graph_responder is None:
            raise ReasoningError("session reasoner has no Mission Graph responder")
        raw = self._graph_responder(directive, roster)
        try:
            return MissionGraphPlan.from_mapping(raw, expected_intent=directive)
        except (TypeError, ValueError) as exc:
            raise ReasoningError(f"invalid session Mission Graph output: {exc}") from exc