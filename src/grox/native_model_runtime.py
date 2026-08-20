from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol


class ModelRuntimeError(RuntimeError):
    """Base failure for the GroX-owned local model runtime."""


class ModelRegistrationError(ModelRuntimeError):
    """A model registry or lineage contract is malformed or ambiguous."""


class ModelInvocationError(ModelRuntimeError):
    """An explicitly loaded local model could not be invoked safely."""


class ModelReadiness(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    CORRUPT = "CORRUPT"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class HardwareRuntimeProfile:
    system: str
    machine: str
    cpu_count: int
    total_memory_bytes: int | None
    accelerators: tuple[str, ...]
    python_implementation: str
    python_version: str

    @classmethod
    def discover(cls) -> "HardwareRuntimeProfile":
        total_memory: int | None = None
        try:
            page_size = int(os.sysconf("SC_PAGE_SIZE"))
            physical_pages = int(os.sysconf("SC_PHYS_PAGES"))
            if page_size > 0 and physical_pages > 0:
                total_memory = page_size * physical_pages
        except (AttributeError, OSError, TypeError, ValueError):
            total_memory = None
        return cls(
            system=platform.system().lower(),
            machine=platform.machine().lower(),
            cpu_count=max(1, int(os.cpu_count() or 1)),
            total_memory_bytes=total_memory,
            accelerators=(),
            python_implementation=platform.python_implementation().lower(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelArtifact:
    path: str
    sha256: str
    byte_size: int

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelArtifact":
        if not isinstance(raw, Mapping):
            raise ModelRegistrationError("model artifact must be a mapping")
        path = raw.get("path")
        digest = raw.get("sha256")
        byte_size = raw.get("bytes")
        if not isinstance(path, str) or not path.strip():
            raise ModelRegistrationError("model artifact path must be a non-empty string")
        normalized = Path(path.strip())
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ModelRegistrationError("model artifact path must remain relative to the GroX asset root")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ModelRegistrationError("model artifact sha256 must be a 64-character hexadecimal digest")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise ModelRegistrationError("model artifact sha256 must be hexadecimal") from exc
        if not isinstance(byte_size, int) or isinstance(byte_size, bool) or byte_size <= 0:
            raise ModelRegistrationError("model artifact bytes must be a positive integer")
        return cls(path=normalized.as_posix(), sha256=digest.lower(), byte_size=byte_size)

    def resolve(self, asset_root: Path | str) -> Path:
        root = Path(asset_root).expanduser().resolve()
        target = (root / self.path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ModelRegistrationError("model artifact path escapes the GroX asset root") from exc
        return target


@dataclass(frozen=True, slots=True)
class ModelLineage:
    generation: int
    parent_model_id: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelLineage":
        if not isinstance(raw, Mapping):
            raise ModelRegistrationError("model lineage must be a mapping")
        generation = raw.get("generation")
        parent = raw.get("parent_model_id")
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            raise ModelRegistrationError("model lineage generation must be a positive integer")
        if parent is not None and (not isinstance(parent, str) or not parent.strip()):
            raise ModelRegistrationError("model lineage parent_model_id must be null or a non-empty string")
        return cls(generation=generation, parent_model_id=parent.strip() if isinstance(parent, str) else None)


@dataclass(frozen=True, slots=True)
class ModelManifest:
    model_id: str
    model_kind: str
    model_format: str
    backend: str
    artifact: ModelArtifact
    lineage: ModelLineage
    placements: tuple[str, ...]
    parameter_count: int | None
    min_ram_bytes: int
    required_accelerator: str | None
    provenance: Mapping[str, Any]
    claims: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelManifest":
        if not isinstance(raw, Mapping):
            raise ModelRegistrationError("model manifest must be a mapping")
        required_strings = {}
        for key in ("model_id", "model_kind", "format", "backend"):
            value = raw.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ModelRegistrationError(f"model manifest {key} must be a non-empty string")
            required_strings[key] = value.strip()

        placements_raw = raw.get("placements")
        if not isinstance(placements_raw, list) or not placements_raw:
            raise ModelRegistrationError("model placements must be a non-empty list")
        placements: list[str] = []
        for item in placements_raw:
            if not isinstance(item, str) or not item.strip():
                raise ModelRegistrationError("model placement entries must be non-empty strings")
            value = item.strip()
            if value not in {"crew", "gorxu"}:
                raise ModelRegistrationError(f"unsupported cognition placement in manifest: {value}")
            if value in placements:
                raise ModelRegistrationError(f"duplicate cognition placement in manifest: {value}")
            placements.append(value)

        parameter_count = raw.get("parameter_count")
        if parameter_count is not None and (
            not isinstance(parameter_count, int) or isinstance(parameter_count, bool) or parameter_count <= 0
        ):
            raise ModelRegistrationError("model parameter_count must be null or a positive integer")

        resources = raw.get("resources") or {}
        if not isinstance(resources, Mapping):
            raise ModelRegistrationError("model resources must be a mapping")
        min_ram = resources.get("min_ram_bytes", 0)
        if not isinstance(min_ram, int) or isinstance(min_ram, bool) or min_ram < 0:
            raise ModelRegistrationError("model min_ram_bytes must be a non-negative integer")
        required_accelerator = resources.get("required_accelerator")
        if required_accelerator is not None and (
            not isinstance(required_accelerator, str) or not required_accelerator.strip()
        ):
            raise ModelRegistrationError("required_accelerator must be null or a non-empty string")

        provenance = raw.get("provenance") or {}
        claims = raw.get("claims") or {}
        if not isinstance(provenance, Mapping) or not isinstance(claims, Mapping):
            raise ModelRegistrationError("model provenance and claims must be mappings")

        return cls(
            model_id=required_strings["model_id"],
            model_kind=required_strings["model_kind"],
            model_format=required_strings["format"],
            backend=required_strings["backend"],
            artifact=ModelArtifact.from_mapping(raw.get("artifact") or {}),
            lineage=ModelLineage.from_mapping(raw.get("lineage") or {}),
            placements=tuple(placements),
            parameter_count=parameter_count,
            min_ram_bytes=min_ram,
            required_accelerator=required_accelerator.strip() if isinstance(required_accelerator, str) else None,
            provenance=dict(provenance),
            claims=dict(claims),
        )


@dataclass(frozen=True, slots=True)
class ModelReadinessReport:
    model_id: str
    status: ModelReadiness
    reason: str
    backend: str | None
    placement_options: tuple[str, ...]
    artifact_path: str | None
    artifact_sha256: str | None
    hardware: HardwareRuntimeProfile
    active: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "status": self.status.value,
            "reason": self.reason,
            "backend": self.backend,
            "placement_options": list(self.placement_options),
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "hardware": self.hardware.to_dict(),
            "active": self.active,
        }


class LocalInferenceBackend(Protocol):
    name: str

    def supports(
        self, manifest: ModelManifest, hardware: HardwareRuntimeProfile
    ) -> tuple[bool, str]: ...

    def load(self, manifest: ModelManifest, artifact_path: Path) -> Any: ...

    def invoke(self, handle: Any, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def unload(self, handle: Any) -> None: ...


class ModelRegistry:
    """Deterministic local model registry.

    Registration is descriptive only: reading a registry never loads, binds, or
    activates a model and never grants Mission or command authority.
    """

    schema = "grox-model-registry-v1"

    def __init__(self, *, asset_root: Path | str, manifests: list[ModelManifest]):
        self.asset_root = Path(asset_root).expanduser().resolve()
        by_id: dict[str, ModelManifest] = {}
        for manifest in manifests:
            if manifest.model_id in by_id:
                raise ModelRegistrationError(f"duplicate model_id in registry: {manifest.model_id}")
            by_id[manifest.model_id] = manifest
        self._manifests = by_id
        self._validate_lineage()

    @classmethod
    def from_mapping(
        cls, *, asset_root: Path | str, raw: Mapping[str, Any]
    ) -> "ModelRegistry":
        if not isinstance(raw, Mapping) or raw.get("schema") != cls.schema:
            raise ModelRegistrationError(f"model registry schema must be {cls.schema}")
        models = raw.get("models")
        if not isinstance(models, list):
            raise ModelRegistrationError("model registry models must be a list")
        return cls(
            asset_root=asset_root,
            manifests=[ModelManifest.from_mapping(item) for item in models],
        )

    @classmethod
    def from_asset_root(cls, asset_root: Path | str) -> "ModelRegistry":
        root = Path(asset_root).expanduser().resolve()
        path = root / "configs" / "models" / "registry.json"
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ModelRegistrationError(f"model registry is unavailable: {path}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise ModelRegistrationError(f"model registry is malformed: {path}: {exc}") from exc
        return cls.from_mapping(asset_root=root, raw=raw)

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._manifests))

    def get(self, model_id: str) -> ModelManifest:
        try:
            return self._manifests[model_id]
        except KeyError as exc:
            raise ModelRegistrationError(f"model is not registered: {model_id}") from exc

    def _validate_lineage(self) -> None:
        for manifest in self._manifests.values():
            parent_id = manifest.lineage.parent_model_id
            if parent_id is None:
                continue
            parent = self._manifests.get(parent_id)
            if parent is None:
                raise ModelRegistrationError(
                    f"model lineage references unknown parent: {manifest.model_id} -> {parent_id}"
                )
            if parent.lineage.generation >= manifest.lineage.generation:
                raise ModelRegistrationError(
                    f"model lineage generation does not advance: {manifest.model_id} -> {parent_id}"
                )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(model_id: str) -> None:
            if model_id in visited:
                return
            if model_id in visiting:
                raise ModelRegistrationError(f"model lineage cycle detected at: {model_id}")
            visiting.add(model_id)
            parent_id = self._manifests[model_id].lineage.parent_model_id
            if parent_id is not None:
                visit(parent_id)
            visiting.remove(model_id)
            visited.add(model_id)

        for model_id in self._manifests:
            visit(model_id)


@dataclass(slots=True)
class _LoadedModel:
    manifest: ModelManifest
    backend: LocalInferenceBackend
    handle: Any
    placement: str


class LocalModelRuntime:
    """GroX-owned control plane over local inference backends.

    Readiness and registration are non-activating. A caller must explicitly load
    a registered model for an allowed cognition placement, and a separate
    Pilot-owned binding step remains necessary before Crew can use that model.
    """

    schema = "grox-local-model-runtime-v1"

    def __init__(
        self,
        registry: ModelRegistry,
        backends: list[LocalInferenceBackend] | tuple[LocalInferenceBackend, ...],
        *,
        hardware: HardwareRuntimeProfile | None = None,
    ):
        self.registry = registry
        self.hardware = hardware or HardwareRuntimeProfile.discover()
        by_name: dict[str, LocalInferenceBackend] = {}
        for backend in backends:
            name = getattr(backend, "name", None)
            if not isinstance(name, str) or not name.strip():
                raise ModelRuntimeError("local inference backend must expose a non-empty name")
            if name in by_name:
                raise ModelRuntimeError(f"duplicate local inference backend: {name}")
            by_name[name] = backend
        self.backends = by_name
        self._loaded: dict[str, _LoadedModel] = {}

    def active_models(self) -> tuple[str, ...]:
        return tuple(sorted(self._loaded))

    def readiness(self, model_id: str) -> ModelReadinessReport:
        try:
            manifest = self.registry.get(model_id)
        except ModelRegistrationError as exc:
            return ModelReadinessReport(
                model_id=model_id,
                status=ModelReadiness.UNAVAILABLE,
                reason=str(exc),
                backend=None,
                placement_options=(),
                artifact_path=None,
                artifact_sha256=None,
                hardware=self.hardware,
                active=False,
            )

        artifact_path = manifest.artifact.resolve(self.registry.asset_root)
        active = model_id in self._loaded
        if not artifact_path.is_file():
            return self._report(
                manifest,
                ModelReadiness.UNAVAILABLE,
                f"model artifact is unavailable: {artifact_path}",
                artifact_path,
                active,
            )
        try:
            data = artifact_path.read_bytes()
        except OSError as exc:
            return self._report(
                manifest,
                ModelReadiness.UNAVAILABLE,
                f"model artifact cannot be read: {exc}",
                artifact_path,
                active,
            )
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != manifest.artifact.byte_size:
            return self._report(
                manifest,
                ModelReadiness.CORRUPT,
                f"model artifact byte-size mismatch: expected {manifest.artifact.byte_size}, got {len(data)}",
                artifact_path,
                active,
                digest=digest,
            )
        if digest != manifest.artifact.sha256:
            return self._report(
                manifest,
                ModelReadiness.CORRUPT,
                f"model artifact digest mismatch: expected {manifest.artifact.sha256}, got {digest}",
                artifact_path,
                active,
                digest=digest,
            )

        if (
            self.hardware.total_memory_bytes is not None
            and self.hardware.total_memory_bytes < manifest.min_ram_bytes
        ):
            return self._report(
                manifest,
                ModelReadiness.UNSUPPORTED,
                (
                    "host memory is below the registered model ceiling: "
                    f"required={manifest.min_ram_bytes}, available={self.hardware.total_memory_bytes}"
                ),
                artifact_path,
                active,
                digest=digest,
            )
        if (
            manifest.required_accelerator is not None
            and manifest.required_accelerator not in self.hardware.accelerators
        ):
            return self._report(
                manifest,
                ModelReadiness.UNSUPPORTED,
                f"required accelerator is unavailable: {manifest.required_accelerator}",
                artifact_path,
                active,
                digest=digest,
            )

        backend = self.backends.get(manifest.backend)
        if backend is None:
            return self._report(
                manifest,
                ModelReadiness.UNSUPPORTED,
                f"registered inference backend is unavailable: {manifest.backend}",
                artifact_path,
                active,
                digest=digest,
            )
        try:
            supported, reason = backend.supports(manifest, self.hardware)
        except Exception as exc:
            return self._report(
                manifest,
                ModelReadiness.UNSUPPORTED,
                f"inference backend readiness check failed: {type(exc).__name__}: {exc}",
                artifact_path,
                active,
                digest=digest,
            )
        if not supported:
            return self._report(
                manifest,
                ModelReadiness.UNSUPPORTED,
                reason or f"inference backend does not support model: {manifest.backend}",
                artifact_path,
                active,
                digest=digest,
            )
        return self._report(
            manifest,
            ModelReadiness.AVAILABLE,
            reason or "registered local model is integrity-bound and supported",
            artifact_path,
            active,
            digest=digest,
        )

    def load(self, model_id: str, *, placement: str) -> dict[str, Any]:
        if model_id in self._loaded:
            raise ModelRuntimeError(f"model is already explicitly loaded: {model_id}")
        manifest = self.registry.get(model_id)
        if placement not in manifest.placements:
            raise ModelRuntimeError(
                f"model {model_id} is not registered for cognition placement: {placement}"
            )
        report = self.readiness(model_id)
        if report.status is not ModelReadiness.AVAILABLE:
            raise ModelRuntimeError(
                f"model {model_id} is not ready: {report.status.value}: {report.reason}"
            )
        backend = self.backends[manifest.backend]
        artifact_path = manifest.artifact.resolve(self.registry.asset_root)
        try:
            handle = backend.load(manifest, artifact_path)
        except Exception as exc:
            raise ModelRuntimeError(
                f"model backend load failed for {model_id}: {type(exc).__name__}: {exc}"
            ) from exc
        self._loaded[model_id] = _LoadedModel(
            manifest=manifest,
            backend=backend,
            handle=handle,
            placement=placement,
        )
        return {
            "schema": "grox-local-model-load-v1",
            "model_id": model_id,
            "backend": manifest.backend,
            "placement": placement,
            "artifact_sha256": manifest.artifact.sha256,
            "authority_changed": False,
            "pilot_binding_changed": False,
        }

    def invoke(
        self, model_id: str, *, placement: str, payload: Mapping[str, Any]
    ) -> dict[str, Any]:
        loaded = self._loaded.get(model_id)
        if loaded is None:
            raise ModelInvocationError(f"model is not explicitly loaded: {model_id}")
        if placement != loaded.placement:
            raise ModelInvocationError(
                f"loaded model placement mismatch: expected {loaded.placement}, got {placement}"
            )
        if not isinstance(payload, Mapping):
            raise ModelInvocationError("local model invocation payload must be a mapping")
        try:
            output = loaded.backend.invoke(loaded.handle, payload)
        except Exception as exc:
            raise ModelInvocationError(
                f"model inference failed for {model_id}: {type(exc).__name__}: {exc}"
            ) from exc
        if not isinstance(output, Mapping):
            raise ModelInvocationError("local inference backend output must be a mapping")
        return {
            "schema": "grox-local-model-invocation-v1",
            "model_id": model_id,
            "model_kind": loaded.manifest.model_kind,
            "backend": loaded.manifest.backend,
            "placement": loaded.placement,
            "artifact_sha256": loaded.manifest.artifact.sha256,
            "authority_changed": False,
            "output": dict(output),
        }

    def unload(self, model_id: str) -> bool:
        loaded = self._loaded.pop(model_id, None)
        if loaded is None:
            return False
        try:
            loaded.backend.unload(loaded.handle)
        except Exception as exc:
            raise ModelRuntimeError(
                f"model backend unload failed for {model_id}: {type(exc).__name__}: {exc}"
            ) from exc
        return True

    def reconstitute(self) -> dict[str, Any]:
        active_before = self.active_models()
        unload_errors: list[str] = []
        for model_id in active_before:
            try:
                self.unload(model_id)
            except ModelRuntimeError as exc:
                unload_errors.append(str(exc))
                self._loaded.pop(model_id, None)
        reports = [self.readiness(model_id).to_dict() for model_id in self.registry.ids()]
        return {
            "schema": "grox-local-model-reconstitution-v1",
            "active_before": list(active_before),
            "active_after": list(self.active_models()),
            "models": reports,
            "unload_errors": unload_errors,
            "auto_activation": False,
            "authority_changed": False,
        }

    def _report(
        self,
        manifest: ModelManifest,
        status: ModelReadiness,
        reason: str,
        artifact_path: Path,
        active: bool,
        *,
        digest: str | None = None,
    ) -> ModelReadinessReport:
        return ModelReadinessReport(
            model_id=manifest.model_id,
            status=status,
            reason=reason,
            backend=manifest.backend,
            placement_options=manifest.placements,
            artifact_path=str(artifact_path),
            artifact_sha256=digest,
            hardware=self.hardware,
            active=active,
        )
