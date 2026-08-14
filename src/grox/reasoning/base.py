from __future__ import annotations
from typing import Protocol, Any
from .contracts import MissionInterpretation

class ReasoningError(RuntimeError):
    pass

class ReasoningProvider(Protocol):
    name: str
    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation: ...
