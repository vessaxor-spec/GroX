from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping


class VesselRootError(RuntimeError):
    """Raised when GroX cannot bind an installed runtime to a Vessel source root."""


_REQUIRED_MARKERS = (
    Path("pyproject.toml"),
    Path("configs/crew/dossiers"),
    Path("configs/tool-policy.json"),
)


def _is_vessel_root(path: Path) -> bool:
    root = path.resolve()
    return all((root / marker).exists() for marker in _REQUIRED_MARKERS)


def _search_up(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if _is_vessel_root(candidate):
            return candidate
    return None


def resolve_vessel_root(
    *,
    cwd: Path | None = None,
    module_file: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Resolve the active GroX Vessel root without fabricating an empty Vessel.

    Resolution order is explicit host binding, current checkout ancestry, then
    source-module ancestry. Installed runtimes outside a Vessel checkout fail
    closed unless ``GROX_VESSEL_ROOT`` binds them to a valid source root.
    """

    env = os.environ if environ is None else environ
    configured = str(env.get("GROX_VESSEL_ROOT", "")).strip()
    if configured:
        root = Path(configured).expanduser().resolve()
        if not _is_vessel_root(root):
            raise VesselRootError(
                f"GROX_VESSEL_ROOT does not point to a valid GroX Vessel root: {root}"
            )
        return root

    starts = [cwd or Path.cwd()]
    starts.append(Path(module_file).resolve() if module_file is not None else Path(__file__).resolve())
    for start in starts:
        found = _search_up(start)
        if found is not None:
            return found

    raise VesselRootError(
        "No GroX Vessel root found. Run from a GroX source checkout or set "
        "GROX_VESSEL_ROOT to the checkout root. Refusing to start an empty Vessel."
    )
