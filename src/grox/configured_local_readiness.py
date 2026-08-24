from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .llama_cpp_backend import LlamaCppCLIBackend
from .native_model_runtime import (
    LocalModelRuntime,
    ModelReadiness,
    ModelRegistrationError,
    ModelRegistry,
    ModelRuntimeError,
)
from .runtime_layout import VesselLayout


class ConfiguredLocalCognitionReadiness:
    """Explicit non-activating readiness awareness for configured local llama.cpp cognition.

    This surface is intentionally narrower than provider construction or model
    activation. It may read the existing GroX model registry/artifact, inspect
    host constraints, and run the pinned local llama.cpp ``--version`` probe
    already used by the runtime readiness contract. Filesystem reads remain
    confined to the commissioned runtime/model-store roots. It never loads a
    model, invokes cognition, touches credentials or network, selects a
    provider, or grants Mission authority.
    """

    schema = "grox-configured-local-cognition-readiness-v1"

    def __init__(self, layout: VesselLayout):
        if not isinstance(layout, VesselLayout):
            raise TypeError("layout must be a VesselLayout")
        self.layout = layout

    @classmethod
    def _base(cls, *, status: str, resources: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": cls.schema,
            "status": status,
            "resources": resources,
            "network_invoked": False,
            "credential_inspected": False,
            "provider_constructed": False,
            "model_loaded": False,
            "cognition_invoked": False,
            "authority_changed": False,
            "auto_activation": False,
            "auto_selection": False,
        }

    @staticmethod
    def _resource(resource: Mapping[str, Any], *, ready: bool, readiness_status: str, reason: str) -> dict[str, Any]:
        return {
            "resource_id": resource.get("resource_id"),
            "resource_type": resource.get("resource_type"),
            "provider_kind": resource.get("provider_kind"),
            "model": resource.get("model"),
            "endpoint": resource.get("endpoint"),
            "discovered": bool(resource.get("discovered")),
            "authorized": False,
            "ready": bool(ready),
            "qualified_fit": False,
            "selected": False,
            "observed": False,
            "readiness_status": readiness_status,
            "readiness_reason": reason,
            "authority_changed": False,
            "auto_activation": False,
            "auto_selection": False,
        }

    @staticmethod
    def _valid_local_resource(resource: Mapping[str, Any]) -> bool:
        resource_id = resource.get("resource_id")
        model = resource.get("model")
        return (
            resource.get("resource_type") == "configured_cognition"
            and resource.get("provider_kind") == "local-llama-cpp"
            and resource.get("endpoint") is None
            and resource.get("discovered") is True
            and isinstance(resource_id, str)
            and resource_id.startswith("cognition:configured:local-llama-cpp:")
            and isinstance(model, str)
            and bool(model.strip())
        )

    def inventory(self, *, resource: Mapping[str, Any], executable: str) -> dict[str, Any]:
        if not isinstance(resource, Mapping) or not self._valid_local_resource(resource):
            return self._base(status="not_applicable", resources=[])

        placeholder = self._resource(
            resource,
            ready=False,
            readiness_status="unproven",
            reason="configured local cognition readiness has not been established",
        )

        if self.layout.legacy_single_root:
            placeholder["readiness_reason"] = "configured local cognition readiness requires a commissioned separated Vessel layout"
            return self._base(status="unavailable", resources=[placeholder])

        if not isinstance(executable, str) or not executable.strip():
            placeholder["readiness_reason"] = "configured local llama.cpp executable is missing"
            return self._base(status="incomplete", resources=[placeholder])
        executable_path = Path(executable.strip()).expanduser()
        if not executable_path.is_absolute():
            placeholder["readiness_reason"] = "configured local llama.cpp executable path must be explicit and absolute"
            return self._base(status="incomplete", resources=[placeholder])

        model_store_root = (Path(self.layout.work_root).resolve().parent / "models").resolve()
        if not model_store_root.is_dir():
            placeholder["readiness_reason"] = f"commissioned GroX model store is unavailable: {model_store_root}"
            return self._base(status="unavailable", resources=[placeholder])

        model_id = str(resource["model"])
        try:
            registry = ModelRegistry.from_asset_root(
                self.layout.asset_root,
                model_store_root=model_store_root,
            )
            backend = LlamaCppCLIBackend(executable_path)
            runtime = LocalModelRuntime(registry, [backend])
            report = runtime.readiness(model_id)
        except (ModelRegistrationError, ModelRuntimeError, OSError, ValueError) as exc:
            placeholder["readiness_reason"] = f"configured local cognition readiness failed: {type(exc).__name__}: {exc}"
            return self._base(status="unavailable", resources=[placeholder])

        ready = report.status is ModelReadiness.AVAILABLE and not report.active
        item = self._resource(
            resource,
            ready=ready,
            readiness_status=report.status.value.lower(),
            reason=report.reason,
        )
        if report.backend is not None:
            item["backend"] = report.backend
        if report.artifact_sha256 is not None:
            item["artifact_sha256"] = report.artifact_sha256

        status = "ok" if ready else report.status.value.lower()
        return self._base(status=status, resources=[item])
