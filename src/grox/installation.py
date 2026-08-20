from __future__ import annotations

import json
import os
import platform
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


CONFIG_SCHEMA_VERSION = 1
WORKSPACE_SCHEMA_VERSION = 1
WORKSPACE_KIND = "grox-vessel-workspace"
BINDING_KIND = "grox-workspace-binding"
WORKSPACE_MARKER = Path(".grox/workspace.json")
WORKSPACE_DIRECTORIES = (
    "state",
    "memory",
    "models",
    "missions",
    "evidence",
    "workspace",
    "snapshots",
    "logs",
    "exports",
)


class InstallationError(RuntimeError):
    """Raised when installed-host workspace state is unsafe or malformed."""


@dataclass(frozen=True)
class CommissioningResult:
    status: str
    workspace: Path
    config_file: Path
    marker_file: Path
    created_directories: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "workspace": str(self.workspace),
            "config_file": str(self.config_file),
            "marker_file": str(self.marker_file),
            "created_directories": list(self.created_directories),
            "schema_version": WORKSPACE_SCHEMA_VERSION,
        }


def _home_path(home: Path | str | None = None) -> Path:
    if home is None:
        return Path.home().expanduser().resolve()
    return Path(home).expanduser().resolve()


def default_workspace(*, home: Path | str | None = None) -> Path:
    """Return the cross-platform user-visible default GroX workspace."""

    return (_home_path(home) / "GroX").resolve()


def platform_config_dir(
    *,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> Path:
    """Return the per-user GroX host-configuration directory.

    Linux follows XDG_CONFIG_HOME when explicitly set; otherwise it uses the
    conventional ~/.config/grox location. macOS uses the user's Application
    Support directory. Unsupported platforms fail closed rather than guessing.
    """

    os_name = (system or platform.system()).strip()
    env = os.environ if environ is None else environ
    user_home = _home_path(home)

    if os_name == "Linux":
        configured = str(env.get("XDG_CONFIG_HOME", "")).strip()
        if configured:
            base = Path(configured).expanduser()
            if not base.is_absolute():
                raise InstallationError(
                    "XDG_CONFIG_HOME must be absolute for GroX host configuration"
                )
            return (base / "grox").resolve()
        return (user_home / ".config" / "grox").resolve()

    if os_name == "Darwin":
        return (user_home / "Library" / "Application Support" / "GroX").resolve()

    raise InstallationError(
        f"GroX local commissioning is not yet supported on host platform: {os_name or '<unknown>'}"
    )


def workspace_binding_file(
    *,
    config_dir: Path | str | None = None,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> Path:
    root = (
        Path(config_dir).expanduser().resolve()
        if config_dir is not None
        else platform_config_dir(system=system, environ=environ, home=home)
    )
    return root / "workspace.json"


def workspace_marker_file(workspace: Path | str) -> Path:
    return Path(workspace).expanduser().resolve() / WORKSPACE_MARKER


def _read_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationError(f"Malformed {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InstallationError(f"Malformed {label}: expected JSON object at {path}")
    return payload


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        finally:
            raise


def _validate_workspace_marker(path: Path, workspace: Path) -> None:
    payload = _read_json_object(path, label="GroX workspace marker")
    if payload.get("kind") != WORKSPACE_KIND:
        raise InstallationError(f"Invalid GroX workspace marker kind: {path}")
    if payload.get("schema_version") != WORKSPACE_SCHEMA_VERSION:
        raise InstallationError(f"Unsupported GroX workspace marker schema: {path}")
    recorded = payload.get("workspace")
    if not isinstance(recorded, str) or Path(recorded).expanduser().resolve() != workspace:
        raise InstallationError(f"GroX workspace marker path mismatch: {path}")


def _validate_binding_payload(payload: Mapping[str, object], path: Path) -> Path:
    if payload.get("kind") != BINDING_KIND:
        raise InstallationError(f"Invalid GroX workspace binding kind: {path}")
    if payload.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise InstallationError(f"Unsupported GroX workspace binding schema: {path}")
    raw_workspace = payload.get("workspace")
    if not isinstance(raw_workspace, str) or not raw_workspace.strip():
        raise InstallationError(f"Malformed GroX workspace binding path: {path}")
    workspace = Path(raw_workspace).expanduser()
    if not workspace.is_absolute():
        raise InstallationError(f"GroX workspace binding must be absolute: {path}")
    return workspace.resolve()


def load_workspace_binding(
    *,
    config_dir: Path | str | None = None,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
    require_marker: bool = True,
) -> Path | None:
    """Return the configured workspace or None when no binding exists.

    Existing malformed or stale bindings fail closed. A configured path is not
    silently accepted as a GroX workspace merely because the directory exists.
    """

    binding = workspace_binding_file(
        config_dir=config_dir,
        system=system,
        environ=environ,
        home=home,
    )
    if not binding.exists():
        return None
    payload = _read_json_object(binding, label="GroX workspace binding")
    workspace = _validate_binding_payload(payload, binding)
    if require_marker:
        marker = workspace_marker_file(workspace)
        if not marker.is_file():
            raise InstallationError(
                f"Configured GroX workspace is missing its marker: {marker}"
            )
        _validate_workspace_marker(marker, workspace)
    return workspace


def workspace_status(
    *,
    config_dir: Path | str | None = None,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> dict[str, object]:
    binding = workspace_binding_file(
        config_dir=config_dir,
        system=system,
        environ=environ,
        home=home,
    )
    configured = load_workspace_binding(
        config_dir=config_dir,
        system=system,
        environ=environ,
        home=home,
        require_marker=True,
    )
    if configured is None:
        target = default_workspace(home=home)
        return {
            "configured": False,
            "commissioned": False,
            "workspace": str(target),
            "default_workspace": str(target),
            "config_file": str(binding),
            "marker_file": str(workspace_marker_file(target)),
        }
    return {
        "configured": True,
        "commissioned": True,
        "workspace": str(configured),
        "default_workspace": str(default_workspace(home=home)),
        "config_file": str(binding),
        "marker_file": str(workspace_marker_file(configured)),
    }


def commission_workspace(
    workspace: Path | str | None = None,
    *,
    config_dir: Path | str | None = None,
    system: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> CommissioningResult:
    """Create or re-open a bounded GroX workspace and persist its host binding.

    This is an installed-host foundation only. It does not turn the workspace
    into the canonical operational source root and does not activate Pilot or
    model authority.
    """

    target = (
        Path(workspace).expanduser().resolve()
        if workspace is not None
        else default_workspace(home=home)
    )
    binding = workspace_binding_file(
        config_dir=config_dir,
        system=system,
        environ=environ,
        home=home,
    )
    marker = workspace_marker_file(target)

    existing_binding = load_workspace_binding(
        config_dir=config_dir,
        system=system,
        environ=environ,
        home=home,
        require_marker=True,
    )
    if existing_binding is not None and existing_binding != target:
        raise InstallationError(
            "GroX is already bound to a different commissioned workspace: "
            f"{existing_binding}. Refusing implicit rebind to {target}."
        )

    if target.exists() and not target.is_dir():
        raise InstallationError(f"GroX workspace path is not a directory: {target}")

    marker_exists = marker.is_file()
    if target.exists() and not marker_exists:
        entries = list(target.iterdir())
        if entries:
            raise InstallationError(
                "Refusing to claim a non-empty directory without a GroX workspace marker: "
                f"{target}"
            )

    if marker_exists:
        _validate_workspace_marker(marker, target)

    target.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for name in WORKSPACE_DIRECTORIES:
        child = target / name
        if child.exists() and not child.is_dir():
            raise InstallationError(
                f"GroX workspace layout collision: expected directory at {child}"
            )
        if not child.exists():
            child.mkdir(parents=False)
            created.append(name)

    if not marker_exists:
        _atomic_write_json(
            marker,
            {
                "kind": WORKSPACE_KIND,
                "schema_version": WORKSPACE_SCHEMA_VERSION,
                "workspace": str(target),
            },
        )

    _atomic_write_json(
        binding,
        {
            "kind": BINDING_KIND,
            "schema_version": CONFIG_SCHEMA_VERSION,
            "workspace": str(target),
        },
    )

    return CommissioningResult(
        status="existing" if marker_exists else "created",
        workspace=target,
        config_file=binding,
        marker_file=marker,
        created_directories=tuple(created),
    )
