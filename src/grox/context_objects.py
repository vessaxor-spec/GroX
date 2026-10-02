from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


class ContextBudgetExceeded(RuntimeError):
    """A bounded context read would exceed its shared allowance."""


@dataclass(frozen=True, slots=True)
class ContextObjectReference:
    """Metadata-only reference to one immutable content-addressed context object."""

    label: str
    sha256: str
    chars: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "grox-context-object-reference-v1",
            "label": self.label,
            "sha256": self.sha256,
            "chars": self.chars,
        }


@dataclass(frozen=True, slots=True)
class ContextView:
    """One exact read-only view over a content-addressed context object."""

    label: str
    source_sha256: str
    start: int
    end: int
    content: str
    view_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "grox-context-view-v1",
            "label": self.label,
            "source_sha256": self.source_sha256,
            "start": self.start,
            "end": self.end,
            "chars": self.end - self.start,
            "content": self.content,
            "view_sha256": self.view_sha256,
        }


@dataclass(slots=True)
class ContextReadBudget:
    """Shared fail-closed allowance for bounded context reads.

    The budget accounts only for views returned to the caller. It grants no
    Mission, tool, provider, filesystem, or execution authority.
    """

    max_operations: int
    max_chars: int
    operations_used: int = 0
    chars_used: int = 0

    def __post_init__(self) -> None:
        for label, value in (
            ("max_operations", self.max_operations),
            ("max_chars", self.max_chars),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{label} must be a positive integer")

    @property
    def remaining_operations(self) -> int:
        return self.max_operations - self.operations_used

    @property
    def remaining_chars(self) -> int:
        return self.max_chars - self.chars_used

    def reserve(self, *, operations: int = 1, chars: int) -> None:
        if not isinstance(operations, int) or isinstance(operations, bool) or operations < 1:
            raise ValueError("operations must be a positive integer")
        if not isinstance(chars, int) or isinstance(chars, bool) or chars < 0:
            raise ValueError("chars must be a non-negative integer")
        next_operations = self.operations_used + operations
        next_chars = self.chars_used + chars
        if next_operations > self.max_operations or next_chars > self.max_chars:
            raise ContextBudgetExceeded(
                "bounded context read exceeds the shared operation/character budget"
            )
        self.operations_used = next_operations
        self.chars_used = next_chars

    def snapshot(self) -> dict[str, int]:
        return {
            "max_operations": self.max_operations,
            "max_chars": self.max_chars,
            "operations_used": self.operations_used,
            "chars_used": self.chars_used,
            "remaining_operations": self.remaining_operations,
            "remaining_chars": self.remaining_chars,
        }


@dataclass(frozen=True, slots=True)
class ContentAddressedContextObject:
    """Immutable in-memory context object with deterministic SHA-256 identity."""

    label: str
    _content: str = field(repr=False)
    sha256: str = field(init=False)
    chars: int = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("context object label must be a non-empty string")
        if not isinstance(self._content, str) or not self._content:
            raise ValueError("context object content must be a non-empty string")
        digest = hashlib.sha256(self._content.encode("utf-8")).hexdigest()
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(self, "chars", len(self._content))

    def reference(self) -> ContextObjectReference:
        """Return metadata only; raw context never escapes through references."""
        return ContextObjectReference(
            label=self.label,
            sha256=self.sha256,
            chars=self.chars,
        )

    def reader(self, budget: ContextReadBudget) -> "BoundedContextReader":
        if not isinstance(budget, ContextReadBudget):
            raise TypeError("budget must be a ContextReadBudget")
        return BoundedContextReader(self, budget)


class BoundedContextReader:
    """Expose exact slice/search views under one shared fail-closed budget."""

    max_pattern_chars = 256
    max_matches_limit = 32
    max_window_chars = 4096

    def __init__(
        self,
        context: ContentAddressedContextObject,
        budget: ContextReadBudget,
    ):
        if not isinstance(context, ContentAddressedContextObject):
            raise TypeError("context must be a ContentAddressedContextObject")
        if not isinstance(budget, ContextReadBudget):
            raise TypeError("budget must be a ContextReadBudget")
        self._context = context
        self._budget = budget

    @staticmethod
    def _view(
        context: ContentAddressedContextObject,
        start: int,
        end: int,
    ) -> ContextView:
        content = context._content[start:end]
        material = f"{context.sha256}:{start}:{end}:".encode("utf-8") + content.encode("utf-8")
        return ContextView(
            label=context.label,
            source_sha256=context.sha256,
            start=start,
            end=end,
            content=content,
            view_sha256=hashlib.sha256(material).hexdigest(),
        )

    def slice(self, start: int, end: int) -> ContextView:
        for label, value in (("start", start), ("end", end)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{label} must be an integer")
        if start < 0 or end <= start or end > self._context.chars:
            raise ValueError(
                "context slice must satisfy 0 <= start < end <= context length"
            )
        view = self._view(self._context, start, end)
        self._budget.reserve(chars=len(view.content))
        return view

    def search(
        self,
        pattern: str,
        *,
        max_matches: int = 8,
        window: int = 160,
    ) -> tuple[ContextView, ...]:
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("search pattern must be a non-empty string")
        if len(pattern) > self.max_pattern_chars:
            raise ValueError(
                f"search pattern exceeds {self.max_pattern_chars} characters"
            )
        if (
            not isinstance(max_matches, int)
            or isinstance(max_matches, bool)
            or not 1 <= max_matches <= self.max_matches_limit
        ):
            raise ValueError(
                f"max_matches must be between 1 and {self.max_matches_limit}"
            )
        if (
            not isinstance(window, int)
            or isinstance(window, bool)
            or not 0 <= window <= self.max_window_chars
        ):
            raise ValueError(
                f"window must be between 0 and {self.max_window_chars}"
            )

        content = self._context._content
        spans: list[tuple[int, int]] = []
        offset = 0
        while len(spans) < max_matches:
            index = content.find(pattern, offset)
            if index < 0:
                break
            start = max(0, index - window)
            end = min(self._context.chars, index + len(pattern) + window)
            span = (start, end)
            if not spans or spans[-1] != span:
                spans.append(span)
            offset = index + max(1, len(pattern))

        views = tuple(self._view(self._context, start, end) for start, end in spans)
        self._budget.reserve(chars=sum(len(view.content) for view in views))
        return views
