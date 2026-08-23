from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Protocol, Any
from .contracts import AssistantResponse, MissionInterpretation


class ReasoningError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CognitiveUsage:
    """Provider-neutral observational usage for one cognitive invocation."""

    provider: str
    model: str | None = None
    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReasoningProvider(Protocol):
    name: str
    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation: ...
    def usage_snapshot(self) -> CognitiveUsage | None: ...


class ConversationalReasoningProvider(Protocol):
    """Optional provider-neutral direct-assistance capability.

    Implementing this protocol does not grant Mission or command authority.
    Existing interpretation-only providers remain valid for Mission cognition.
    """

    name: str
    def respond(self, message: str) -> AssistantResponse: ...
    def usage_snapshot(self) -> CognitiveUsage | None: ...
