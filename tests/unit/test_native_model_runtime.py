from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any

from grox.crew_provider import bound_crew_cognition_provider
from grox.native_model_runtime import (
    HardwareRuntimeProfile,
    LocalModelRuntime,
    ModelReadiness,
    ModelRegistrationError,
    ModelRegistry,
    ModelRuntimeError,
)
from grox.tiny_neural_policy import TINY_BACKEND_NAME, TINY_MODEL_FORMAT, TINY_MODEL_ID, TinyMLPPythonBackend
from tests._support import temp_vessel


class _EchoBackend:
    name = "echo-v1"

    def __init__(self, *, supported: bool = True, fail_load: bool = False, fail_invoke: bool = False):
        self.supported = supported
        self.fail_load = fail_load
        self.fail_invoke = fail_invoke

    def supports(self, manifest, hardware):
        return self.supported, "echo backend available" if self.supported else "echo backend unsupported"

    def load(self, manifest, artifact_path):
        if self.fail_load:
            raise RuntimeError("load boom")
        return {"model_id": manifest.model_id, "path": str(artifact_path)}

    def invoke(self, handle, payload):
        if self.fail_invoke:
            raise RuntimeError("invoke boom")
        return {"echo": dict(payload)}

    def unload(self, handle):
        return None


def _profile(*, memory: int | None = 8 * 1024 * 1024, accelerators: tuple[str, ...] = ()):
    return HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=4,
        total_memory_bytes=memory,
        accelerators=accelerators,
        python_implementation="cpython",
        python_version="3.12.0",
    )


def _write_registry(root: Path, *, models: list[dict[str, Any]]) -> ModelRegistry:
    return ModelRegistry.from_mapping(
        asset_root=root,
        raw={"schema": "grox-model-registry-v1", "models": models},
    )


def _model(
    root: Path,
    *,
    model_id: str = "test-model",
    parent: str | None = None,
    generation: int = 1,
    backend: str = "echo-v1",
    placements: list[str] | None = None,
    min_ram_bytes: int = 0,
    required_accelerator: str | None = None,
    payload: bytes = b"model",
) -> dict[str, Any]:
    path = root / "configs" / "models" / f"{model_id}.bin"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return {
        "model_id": model_id,
        "model_kind": "test-policy",
        "format": "test-v1",
        "backend": backend,
        "artifact": {
            "path": f"configs/models/{model_id}.bin",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        },
        "lineage": {"generation": generation, "parent_model_id": parent},
        "placements": placements or ["crew"],
        "parameter_count": 1,
        "resources": {"min_ram_bytes": min_ram_bytes, "required_accelerator": required_accelerator},
        "provenance": {"source": "unit-test"},
        "claims": {"language_capable": False},
    }


class NativeModelRuntimeTests(unittest.TestCase):
    def test_canonical_registry_is_available_but_not_auto_activated(self):
        root = Path(__file__).resolve().parents[2]
        registry = ModelRegistry.from_asset_root(root)
        self.assertIn(TINY_MODEL_ID, registry.ids())
        runtime = LocalModelRuntime(registry, [TinyMLPPythonBackend()], hardware=_profile(memory=32 * 1024 * 1024))
        readiness = runtime.readiness(TINY_MODEL_ID)
        self.assertEqual(readiness.status, ModelReadiness.AVAILABLE)
        self.assertFalse(readiness.active)
        self.assertEqual(runtime.active_models(), ())
        manifest = registry.get(TINY_MODEL_ID)
        self.assertEqual(manifest.model_format, TINY_MODEL_FORMAT)
        self.assertEqual(manifest.backend, TINY_BACKEND_NAME)
        self.assertEqual(manifest.placements, ("crew",))
        self.assertEqual(manifest.parameter_count, 75)
        self.assertFalse(bool(manifest.claims.get("language_capable")))
        self.assertFalse(bool(manifest.claims.get("general_purpose_llm")))

    def test_explicit_load_and_invoke_emit_model_identity_without_authority(self):
        root = Path(__file__).resolve().parents[2]
        runtime = LocalModelRuntime(
            ModelRegistry.from_asset_root(root),
            [TinyMLPPythonBackend()],
            hardware=_profile(memory=32 * 1024 * 1024),
        )
        with self.assertRaisesRegex(Exception, "not explicitly loaded"):
            runtime.invoke(TINY_MODEL_ID, placement="crew", payload={})
        load = runtime.load(TINY_MODEL_ID, placement="crew")
        self.assertFalse(load["authority_changed"])
        self.assertFalse(load["pilot_binding_changed"])
        result = runtime.invoke(
            TINY_MODEL_ID,
            placement="crew",
            payload={
                "order": {"objective": "Inspect README evidence"},
                "craft_context": [{"heading": "Safety Boundaries"}],
                "memory_context": [{"kind": "semantic"}],
                "observations": [],
                "requested_mode": "repair",
                "requested_verifier_authority": True,
            },
        )
        self.assertEqual(result["model_id"], TINY_MODEL_ID)
        self.assertEqual(result["placement"], "crew")
        self.assertFalse(result["authority_changed"])
        self.assertIn(result["output"]["action"], {"fs_read", "test_run", "finish"})
        runtime.unload(TINY_MODEL_ID)
        with self.assertRaisesRegex(ModelRuntimeError, "not registered for cognition placement"):
            runtime.load(TINY_MODEL_ID, placement="gorxu")

    def test_missing_artifact_is_unavailable_and_digest_mismatch_is_corrupt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = _model(root)
            runtime = LocalModelRuntime(_write_registry(root, models=[raw]), [_EchoBackend()], hardware=_profile())
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.AVAILABLE)
            artifact = root / raw["artifact"]["path"]
            artifact.unlink()
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.UNAVAILABLE)
            artifact.write_bytes(b"other")
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.CORRUPT)

    def test_duplicate_unknown_parent_and_cycle_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = _model(root, model_id="first")
            with self.assertRaisesRegex(ModelRegistrationError, "duplicate model_id"):
                _write_registry(root, models=[first, dict(first)])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            orphan = _model(root, model_id="orphan", parent="missing", generation=2)
            with self.assertRaisesRegex(ModelRegistrationError, "unknown parent"):
                _write_registry(root, models=[orphan])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = _model(root, model_id="first", parent="second", generation=2)
            second = _model(root, model_id="second", parent="first", generation=1)
            with self.assertRaises(ModelRegistrationError):
                _write_registry(root, models=[first, second])

    def test_hardware_or_backend_constraints_report_unsupported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = _write_registry(root, models=[_model(root, min_ram_bytes=4096)])
            runtime = LocalModelRuntime(registry, [_EchoBackend()], hardware=_profile(memory=1024))
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.UNSUPPORTED)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = _write_registry(root, models=[_model(root, required_accelerator="gpu")])
            runtime = LocalModelRuntime(registry, [_EchoBackend()], hardware=_profile(accelerators=()))
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.UNSUPPORTED)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = _write_registry(root, models=[_model(root, backend="missing-backend")])
            runtime = LocalModelRuntime(registry, [], hardware=_profile())
            self.assertEqual(runtime.readiness("test-model").status, ModelReadiness.UNSUPPORTED)

    def test_backend_load_and_inference_failures_are_contained(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = _write_registry(root, models=[_model(root)])
            runtime = LocalModelRuntime(registry, [_EchoBackend(fail_load=True)], hardware=_profile())
            with self.assertRaisesRegex(ModelRuntimeError, "backend load failed"):
                runtime.load("test-model", placement="crew")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = _write_registry(root, models=[_model(root)])
            runtime = LocalModelRuntime(registry, [_EchoBackend(fail_invoke=True)], hardware=_profile())
            runtime.load("test-model", placement="crew")
            with self.assertRaisesRegex(Exception, "model inference failed"):
                runtime.invoke("test-model", placement="crew", payload={"x": 1})

    def test_registration_and_readiness_do_not_bind_pilot_or_widen_mission_authority(self):
        root = Path(__file__).resolve().parents[2]
        runtime = LocalModelRuntime(
            ModelRegistry.from_asset_root(root),
            [TinyMLPPythonBackend()],
            hardware=_profile(memory=32 * 1024 * 1024),
        )
        td, _, pilot = temp_vessel()
        try:
            self.assertIsNone(bound_crew_cognition_provider(pilot))
            self.assertEqual(runtime.readiness(TINY_MODEL_ID).status, ModelReadiness.AVAILABLE)
            self.assertEqual(runtime.active_models(), ())
            self.assertIsNone(bound_crew_cognition_provider(pilot))
            runtime.load(TINY_MODEL_ID, placement="crew")
            self.assertIsNone(bound_crew_cognition_provider(pilot))
            self.assertFalse(hasattr(runtime, "command"))
            self.assertFalse(hasattr(runtime, "verify"))
        finally:
            td.cleanup()

    def test_reconstitution_never_auto_activates_and_surfaces_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = _model(root)
            runtime = LocalModelRuntime(_write_registry(root, models=[raw]), [_EchoBackend()], hardware=_profile())
            runtime.load("test-model", placement="crew")
            report = runtime.reconstitute()
            self.assertEqual(report["active_before"], ["test-model"])
            self.assertEqual(report["active_after"], [])
            self.assertFalse(report["auto_activation"])
            self.assertFalse(report["authority_changed"])
            self.assertEqual(report["models"][0]["status"], ModelReadiness.AVAILABLE.value)
            (root / raw["artifact"]["path"]).write_bytes(b"corrupt")
            degraded = runtime.reconstitute()
            self.assertEqual(degraded["active_after"], [])
            self.assertEqual(degraded["models"][0]["status"], ModelReadiness.CORRUPT.value)


if __name__ == "__main__":
    unittest.main()
