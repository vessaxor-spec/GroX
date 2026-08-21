from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping

from .installation import InstallationError, load_workspace_binding


class ModelStoreError(RuntimeError):
    """A persistent local-model store operation is unsafe or invalid."""


class ModelArtifactState(str, Enum):
    MISSING = "MISSING"
    AVAILABLE = "AVAILABLE"
    CORRUPT = "CORRUPT"


@dataclass(frozen=True, slots=True)
class ProvisioningSpec:
    """Attributable identity required before a model artifact may be admitted.

    This contract is intentionally transport-neutral. It contains no downloader
    and cannot cause network access merely by being constructed or inspected.
    """

    model_id: str
    target_filename: str
    source: str
    source_revision: str
    license_id: str
    sha256: str
    byte_size: int

    def __post_init__(self) -> None:
        for field_name in ("model_id", "source", "source_revision", "license_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ModelStoreError(f"{field_name} must be a non-empty string")
            object.__setattr__(self, field_name, value.strip())

        target = self.target_filename
        if not isinstance(target, str) or not target.strip():
            raise ModelStoreError("target_filename must be a non-empty string")
        target_path = Path(target.strip())
        if target_path.is_absolute() or len(target_path.parts) != 1 or target_path.name in {".", ".."}:
            raise ModelStoreError("target_filename must be one safe filename inside the GroX model store")
        object.__setattr__(self, "target_filename", target_path.name)

        digest = self.sha256
        if not isinstance(digest, str) or len(digest) != 64:
            raise ModelStoreError("sha256 must be a 64-character hexadecimal digest")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise ModelStoreError("sha256 must be hexadecimal") from exc
        object.__setattr__(self, "sha256", digest.lower())

        if not isinstance(self.byte_size, int) or isinstance(self.byte_size, bool) or self.byte_size <= 0:
            raise ModelStoreError("byte_size must be a positive integer")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> "ProvisioningSpec":
        if not isinstance(raw, Mapping):
            raise ModelStoreError("model provisioning metadata must be a mapping")
        return cls(
            model_id=raw.get("model_id"),  # type: ignore[arg-type]
            target_filename=raw.get("target_filename"),  # type: ignore[arg-type]
            source=raw.get("source"),  # type: ignore[arg-type]
            source_revision=raw.get("source_revision"),  # type: ignore[arg-type]
            license_id=raw.get("license_id"),  # type: ignore[arg-type]
            sha256=raw.get("sha256"),  # type: ignore[arg-type]
            byte_size=raw.get("byte_size"),  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelArtifactReport:
    model_id: str
    state: ModelArtifactState
    path: str
    expected_sha256: str
    observed_sha256: str | None
    expected_bytes: int
    observed_bytes: int | None
    reason: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["state"] = self.state.value
        return payload


@dataclass(frozen=True, slots=True)
class ProvisioningResult:
    model_id: str
    status: str
    path: str
    sha256: str
    byte_size: int
    source: str
    source_revision: str
    license_id: str
    network_used: bool = False
    authority_changed: bool = False
    auto_activation: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class PersistentModelStore:
    """Persistent, non-command model-byte store for a commissioned Vessel.

    The store is deliberately separate from immutable runtime assets and from
    Commander work. It verifies bytes but does not register, load, activate,
    route, or grant authority to a model.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root).expanduser().resolve()
        if not self.root.is_dir():
            raise ModelStoreError(f"GroX model store is unavailable: {self.root}")

    @classmethod
    def from_workspace(
        cls,
        *,
        config_dir: Path | str | None = None,
        system: str | None = None,
        environ: Mapping[str, str] | None = None,
        home: Path | str | None = None,
    ) -> "PersistentModelStore":
        try:
            workspace = load_workspace_binding(
                config_dir=config_dir,
                system=system,
                environ=environ,
                home=home,
                require_marker=True,
            )
        except InstallationError as exc:
            raise ModelStoreError(str(exc)) from exc
        if workspace is None:
            raise ModelStoreError("No commissioned GroX workspace found for persistent model storage")
        model_root = (workspace / "models").resolve()
        try:
            model_root.relative_to(workspace)
        except ValueError as exc:
            raise ModelStoreError("GroX model store escapes the commissioned workspace") from exc
        if not model_root.is_dir():
            raise ModelStoreError(f"Commissioned GroX workspace is missing its model store: {model_root}")
        return cls(model_root)

    def target(self, spec: ProvisioningSpec) -> Path:
        target = (self.root / spec.target_filename).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ModelStoreError("model artifact target escapes the GroX model store") from exc
        return target

    @staticmethod
    def _digest_file(path: Path) -> tuple[str, int]:
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
        return digest.hexdigest(), size

    def inspect(self, spec: ProvisioningSpec) -> ModelArtifactReport:
        path = self.target(spec)
        if not path.is_file():
            return ModelArtifactReport(
                model_id=spec.model_id,
                state=ModelArtifactState.MISSING,
                path=str(path),
                expected_sha256=spec.sha256,
                observed_sha256=None,
                expected_bytes=spec.byte_size,
                observed_bytes=None,
                reason="verified local model artifact is not present",
            )
        try:
            digest, size = self._digest_file(path)
        except OSError as exc:
            return ModelArtifactReport(
                model_id=spec.model_id,
                state=ModelArtifactState.MISSING,
                path=str(path),
                expected_sha256=spec.sha256,
                observed_sha256=None,
                expected_bytes=spec.byte_size,
                observed_bytes=None,
                reason=f"local model artifact cannot be read: {exc}",
            )
        if size != spec.byte_size or digest != spec.sha256:
            return ModelArtifactReport(
                model_id=spec.model_id,
                state=ModelArtifactState.CORRUPT,
                path=str(path),
                expected_sha256=spec.sha256,
                observed_sha256=digest,
                expected_bytes=spec.byte_size,
                observed_bytes=size,
                reason="local model artifact does not match its admitted identity",
            )
        return ModelArtifactReport(
            model_id=spec.model_id,
            state=ModelArtifactState.AVAILABLE,
            path=str(path),
            expected_sha256=spec.sha256,
            observed_sha256=digest,
            expected_bytes=spec.byte_size,
            observed_bytes=size,
            reason="local model artifact is integrity-bound and available",
        )

    def provision_from_file(self, spec: ProvisioningSpec, source_path: Path | str) -> ProvisioningResult:
        """Explicitly admit verified local bytes into the persistent model store.

        The caller is responsible for acquiring `source_path`. This method does
        not perform network access. Bytes are copied to a private temporary file
        in the model store, verified there, fsynced, and atomically published.
        """

        source = Path(source_path).expanduser().resolve()
        if not source.is_file():
            raise ModelStoreError(f"model provisioning source is not a file: {source}")

        target = self.target(spec)
        if target.exists():
            report = self.inspect(spec)
            if report.state is ModelArtifactState.AVAILABLE:
                return ProvisioningResult(
                    model_id=spec.model_id,
                    status="existing",
                    path=str(target),
                    sha256=spec.sha256,
                    byte_size=spec.byte_size,
                    source=spec.source,
                    source_revision=spec.source_revision,
                    license_id=spec.license_id,
                )
            raise ModelStoreError(f"refusing to overwrite conflicting model artifact: {target}")

        fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".partial", dir=str(self.root))
        temp_path = Path(temp_name)
        digest = hashlib.sha256()
        size = 0
        try:
            with source.open("rb") as source_handle, os.fdopen(fd, "wb") as target_handle:
                while True:
                    chunk = source_handle.read(1024 * 1024)
                    if not chunk:
                        break
                    target_handle.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                target_handle.flush()
                os.fsync(target_handle.fileno())

            observed = digest.hexdigest()
            if size != spec.byte_size:
                raise ModelStoreError(
                    f"model artifact byte-size mismatch: expected {spec.byte_size}, got {size}"
                )
            if observed != spec.sha256:
                raise ModelStoreError(
                    f"model artifact digest mismatch: expected {spec.sha256}, got {observed}"
                )
            try:
                os.link(temp_path, target)
            except FileExistsError as exc:
                raise ModelStoreError(
                    f"model artifact target appeared during provisioning: {target}"
                ) from exc
            except OSError as exc:
                raise ModelStoreError(
                    f"model artifact could not be atomically published: {target}: {exc}"
                ) from exc
            temp_path.unlink()
            return ProvisioningResult(
                model_id=spec.model_id,
                status="provisioned",
                path=str(target),
                sha256=observed,
                byte_size=size,
                source=spec.source,
                source_revision=spec.source_revision,
                license_id=spec.license_id,
            )
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
