from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class RuntimeLayoutError(ValueError):
    """Raised when GroX runtime/state/work roots are ambiguous or unsafe."""


def _resolved(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def _overlap(left: Path, right: Path) -> bool:
    return (
        left == right
        or left.is_relative_to(right)
        or right.is_relative_to(left)
    )


@dataclass(frozen=True, slots=True)
class VesselLayout:
    """Filesystem role contract beneath GorXu.

    `legacy_single_root=True` preserves the source-checkout layout exactly:
    runtime assets, private state, and Commander work all share the historical
    Vessel root, with private state below `configs/state`.

    A separated layout requires non-overlapping runtime, state, and work roots.
    That prevents ordinary Tool Gateway filesystem paths from reaching private
    state or immutable runtime assets through a relative path.
    """

    asset_root: Path
    state_root: Path
    work_root: Path
    legacy_single_root: bool = False

    def __post_init__(self) -> None:
        assets = _resolved(self.asset_root)
        state = _resolved(self.state_root)
        work = _resolved(self.work_root)
        object.__setattr__(self, "asset_root", assets)
        object.__setattr__(self, "state_root", state)
        object.__setattr__(self, "work_root", work)

        if self.legacy_single_root:
            if not (assets == state == work):
                raise RuntimeLayoutError(
                    "legacy GroX layout requires asset, state, and work roots to be identical"
                )
            return

        pairs = (
            ("runtime assets", assets, "private state", state),
            ("runtime assets", assets, "Commander work", work),
            ("private state", state, "Commander work", work),
        )
        for left_name, left, right_name, right in pairs:
            if _overlap(left, right):
                raise RuntimeLayoutError(
                    f"separated GroX roots must not overlap: {left_name}={left} ; "
                    f"{right_name}={right}"
                )

    @classmethod
    def legacy(cls, vessel_root: Path | str) -> "VesselLayout":
        root = _resolved(vessel_root)
        return cls(root, root, root, legacy_single_root=True)

    @classmethod
    def separated(
        cls,
        *,
        asset_root: Path | str,
        state_root: Path | str,
        work_root: Path | str,
    ) -> "VesselLayout":
        return cls(
            _resolved(asset_root),
            _resolved(state_root),
            _resolved(work_root),
            legacy_single_root=False,
        )

    @property
    def state_storage_root(self) -> Path:
        if self.legacy_single_root:
            return self.state_root / "configs" / "state"
        return self.state_root

    def asset_path(self, relative: str | Path) -> Path:
        return (self.asset_root / relative).resolve()

    def state_path(self, relative: str | Path) -> Path:
        return (self.state_storage_root / relative).resolve()

    def work_path(self, relative: str | Path) -> Path:
        return (self.work_root / relative).resolve()

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_root": str(self.asset_root),
            "state_root": str(self.state_root),
            "state_storage_root": str(self.state_storage_root),
            "work_root": str(self.work_root),
            "legacy_single_root": self.legacy_single_root,
        }
