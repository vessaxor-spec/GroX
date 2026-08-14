from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SNAPSHOT_SCHEMA = "groxstate-v1"
STATE_MEMBER = "state/grox.sqlite3"
MANIFEST_MEMBER = "manifest.json"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_member(name: str) -> bool:
    p = PurePosixPath(name)
    return not p.is_absolute() and ".." not in p.parts


@dataclass(frozen=True)
class SnapshotReport:
    path: str
    valid: bool
    manifest: dict[str, Any]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "valid": self.valid, "manifest": self.manifest, "errors": self.errors}


class PersistenceManager:
    """Creates and restores private operational-state checkpoints.

    Source code belongs in Git. Runtime mission/memory state does not. This
    manager snapshots only the SQLite operational state and a non-secret
    manifest. Snapshot archives are ignored by Git by default.
    """

    def __init__(self, vessel_root: Path):
        self.root = vessel_root.resolve()
        self.state_db = self.root / "configs/state/grox.sqlite3"
        self.snapshot_dir = self.root / "configs/state/snapshots"
        self.binding_path = self.root / "configs/persistence/project-binding.json"

    def _binding(self) -> dict[str, Any]:
        if not self.binding_path.exists():
            return {}
        return json.loads(self.binding_path.read_text(encoding="utf-8"))

    def _git_commit(self) -> str | None:
        try:
            out = subprocess.check_output(
                ["git", "-C", str(self.root), "rev-parse", "HEAD"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5,
            ).strip()
            return out or None
        except Exception:
            return None

    def _sqlite_backup(self, destination: Path) -> None:
        if not self.state_db.exists():
            raise FileNotFoundError(f"Operational state database not found: {self.state_db}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(self.state_db)
        target = sqlite3.connect(destination)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    def create_snapshot(self, *, label: str | None = None, output: Path | None = None) -> SnapshotReport:
        safe_label = "".join(c for c in (label or "") if c.isalnum() or c in "-_" ).strip("-_")
        suffix = f"-{safe_label}" if safe_label else ""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        target = output.resolve() if output else (self.snapshot_dir / f"GROX-{_utc_stamp()}{suffix}.groxstate")
        target.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="grox-snapshot-") as td:
            td_path = Path(td)
            db_copy = td_path / "grox.sqlite3"
            self._sqlite_backup(db_copy)
            state_hash = _sha256(db_copy)
            binding = self._binding()
            manifest = {
                "schema": SNAPSHOT_SCHEMA,
                "created_at": _iso_now(),
                "sensitivity": "private_runtime_state",
                "vessel_git_commit": self._git_commit(),
                "state_member": STATE_MEMBER,
                "state_sha256": state_hash,
                "project_binding": binding.get("cognitive_home", {}),
                "source_binding": binding.get("vessel_source", {}),
                "notes": "Contains mission, order, evidence and Crew operational state. Do not commit to a public repository.",
            }
            manifest_path = td_path / MANIFEST_MEMBER
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(manifest_path, MANIFEST_MEMBER)
                zf.write(db_copy, STATE_MEMBER)

        return self.verify_snapshot(target)

    def verify_snapshot(self, snapshot: Path) -> SnapshotReport:
        snapshot = snapshot.resolve()
        errors: list[str] = []
        manifest: dict[str, Any] = {}
        if not snapshot.exists():
            return SnapshotReport(str(snapshot), False, {}, ["snapshot does not exist"])
        try:
            with zipfile.ZipFile(snapshot, "r") as zf:
                names = zf.namelist()
                if any(not _safe_member(n) for n in names):
                    errors.append("unsafe archive member path")
                if MANIFEST_MEMBER not in names:
                    errors.append("manifest missing")
                if STATE_MEMBER not in names:
                    errors.append("state database missing")
                if errors:
                    return SnapshotReport(str(snapshot), False, {}, errors)
                manifest = json.loads(zf.read(MANIFEST_MEMBER).decode("utf-8"))
                if manifest.get("schema") != SNAPSHOT_SCHEMA:
                    errors.append(f"unsupported schema: {manifest.get('schema')}")
                with tempfile.TemporaryDirectory(prefix="grox-verify-") as td:
                    db_path = Path(td) / "grox.sqlite3"
                    with db_path.open("wb") as fh:
                        fh.write(zf.read(STATE_MEMBER))
                    actual = _sha256(db_path)
                    if actual != manifest.get("state_sha256"):
                        errors.append("state SHA-256 mismatch")
                    try:
                        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                        row = db.execute("PRAGMA integrity_check").fetchone()
                        db.close()
                        if not row or row[0] != "ok":
                            errors.append("SQLite integrity_check failed")
                    except sqlite3.DatabaseError as exc:
                        errors.append(f"invalid SQLite state: {exc}")
        except (zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"invalid snapshot: {exc}")
        return SnapshotReport(str(snapshot), not errors, manifest, errors)

    def restore_snapshot(self, snapshot: Path, *, confirm: bool = False) -> dict[str, Any]:
        if not confirm:
            raise PermissionError("restore requires explicit confirm=True")
        report = self.verify_snapshot(snapshot)
        if not report.valid:
            raise ValueError(f"snapshot verification failed: {report.errors}")

        pre_restore: SnapshotReport | None = None
        if self.state_db.exists():
            pre_restore = self.create_snapshot(label="pre-restore")

        with zipfile.ZipFile(Path(snapshot).resolve(), "r") as zf, tempfile.TemporaryDirectory(prefix="grox-restore-") as td:
            staged = Path(td) / "grox.sqlite3"
            with staged.open("wb") as fh:
                fh.write(zf.read(STATE_MEMBER))
            self.state_db.parent.mkdir(parents=True, exist_ok=True)
            replace = self.state_db.with_suffix(".sqlite3.restore")
            shutil.copy2(staged, replace)
            replace.replace(self.state_db)

        return {
            "restored": True,
            "snapshot": str(Path(snapshot).resolve()),
            "state_db": str(self.state_db),
            "pre_restore_snapshot": pre_restore.path if pre_restore else None,
            "manifest": report.manifest,
        }
