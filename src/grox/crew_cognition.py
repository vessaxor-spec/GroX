from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


READ_ONLY_COGNITIVE_ACTIONS = frozenset({"fs_list", "fs_read", "test_run"})


class CrewCognitionError(RuntimeError):
    """Recoverable provider/contract failure that may degrade to deterministic execution."""


class CrewCognitionDenied(PermissionError):
    """A cognitive request attempted to exceed the bounded read-only seam."""


@dataclass(frozen=True, slots=True)
class CrewCognitionStep:
    action: str
    path: str | None = None
    work_product: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CrewCognitionStep":
        if not isinstance(raw, Mapping):
            raise CrewCognitionError("Crew cognition output must be a mapping")
        action = raw.get("action")
        if not isinstance(action, str) or not action.strip():
            raise CrewCognitionError("Crew cognition action must be a non-empty string")
        action = action.strip()
        if action == "finish":
            work_product = raw.get("work_product")
            if not isinstance(work_product, str) or not work_product.strip():
                raise CrewCognitionError("Crew cognition finish requires a non-empty work_product")
            return cls(action="finish", work_product=work_product.strip())
        if action not in READ_ONLY_COGNITIVE_ACTIONS:
            raise CrewCognitionDenied(f"Crew cognition action is outside the read-only seam: {action}")
        if action in {"fs_list", "fs_read"}:
            path = raw.get("path")
            if not isinstance(path, str) or not path.strip():
                raise CrewCognitionError(f"Crew cognition {action} requires a non-empty path")
            return cls(action=action, path=path.strip())
        return cls(action=action)


class CrewCognitionProvider(Protocol):
    name: str

    def next_step(
        self,
        *,
        order: dict[str, Any],
        craft_context: list[dict[str, Any]],
        memory_context: list[dict[str, Any]],
        observations: list[dict[str, Any]],
    ) -> Mapping[str, Any]: ...
