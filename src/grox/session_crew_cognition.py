from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .crew_cognition import CrewCognitionError


SessionCrewResponder = Callable[
    [dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]],
    Mapping[str, Any],
]


class SessionCrewCognitionProvider:
    """Bind one Crew cognition tour to the currently hosting reasoning session.

    This adapter is deliberately separate from GorXu's reasoning provider. The
    hosting session recommends only the next bounded Crew step; Mission Order,
    Tool Gateway, scope, mode, resource limits, routing, Repair authority, and
    verification remain GroX-owned controls.

    Recoverable host/provider failures should be raised as CrewCognitionError.
    Unexpected host defects are intentionally not normalized here so GorXu's
    outer containment path can retain defect classification and traceback.
    """

    def __init__(self, responder: SessionCrewResponder, *, name: str = "project-session-crew"):
        if not callable(responder):
            raise TypeError("responder must be callable")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        self._responder = responder
        self.name = name.strip()

    def usage_snapshot(self) -> None:
        # The project/session callback contract does not expose token accounting.
        # Returning None is explicit and avoids invented provider-usage evidence.
        return None

    def next_step(
        self,
        *,
        order: dict[str, Any],
        craft_context: list[dict[str, Any]],
        memory_context: list[dict[str, Any]],
        observations: list[dict[str, Any]],
    ) -> Mapping[str, Any]:
        raw = self._responder(order, craft_context, memory_context, observations)
        if not isinstance(raw, Mapping):
            raise CrewCognitionError("session Crew cognition output must be a mapping")
        return dict(raw)
