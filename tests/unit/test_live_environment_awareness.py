from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any

from grox.live_environment import (
    LiveEnvironmentAwareness,
    ResourcePolicy,
    ResourceSelectionError,
)
from grox.native_model_runtime import (
    HardwareRuntimeProfile,
    LocalModelRuntime,
    ModelInvocationError,
    ModelRegistry,
)


class _EchoBackend:
    name = "echo-v1"

    def supports(self, manifest, hardware):
        return True, "echo backend available"

    def load(self, manifest, artifact_path):
        return {"model_id": manifest.model_id, "path": str(artifact_path)}

    def invoke(self, handle, payload):
        return {"echo": dict(payload)}

    def unload(self, handle):
        return None


def _profile() -> HardwareRuntimeProfile:
    return HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=4,
        total_memory_bytes=8 * 1024 * 1024,
        accelerators=(),
        python_implementation="cpython",
        python_version="3.12.0",
    )


def _model(root: Path, model_id: str, *, payload: bytes = b"model") -> dict[str, Any]:
    path = root / "configs" / "models" / f"{model_id}.bin"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return {
        "model_id": model_id,
        "model_kind": "test-policy",
        "format": "test-v1",
        "backend": "echo-v1",
        "artifact": {
            "path": f"configs/models/{model_id}.bin",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        },
        "lineage": {"generation": 1, "parent_model_id": None},
        "placements": ["gorxu"],
        "parameter_count": 1,
        "resources": {"min_ram_bytes": 0, "required_accelerator": None},
        "provenance": {"source": "unit-test"},
        "claims": {"language_capable": False},
    }


def _runtime(root: Path, model_ids: tuple[str, ...]) -> LocalModelRuntime:
    models = [_model(root, model_id) for model_id in model_ids]
    registry = ModelRegistry.from_mapping(
        asset_root=root,
        raw={"schema": "grox-model-registry-v1", "models": models},
    )
    return LocalModelRuntime(registry, [_EchoBackend()], hardware=_profile())


class LiveEnvironmentAwarenessTests(unittest.TestCase):
    def test_inventory_separates_representation_discovery_authority_readiness_and_fitness(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root, ("ready-model", "missing-model"))
            (root / "configs" / "models" / "missing-model.bin").unlink()
            awareness = LiveEnvironmentAwareness(runtime)
            policy = ResourcePolicy(
                authorized_ids=frozenset({"ready-model"}),
                qualified_ids=frozenset(),
                candidate_order=("ready-model",),
            )

            inventory = awareness.inventory(policy, placement="gorxu")
            by_id = {item.resource_id: item for item in inventory.resources}

            ready = by_id["ready-model"]
            self.assertTrue(ready.discovered)
            self.assertTrue(ready.authorized)
            self.assertTrue(ready.ready)
            self.assertFalse(ready.qualified_fit)
            self.assertFalse(ready.selected)
            self.assertFalse(ready.observed)

            missing = by_id["missing-model"]
            self.assertFalse(missing.discovered)
            self.assertFalse(missing.authorized)
            self.assertFalse(missing.ready)
            self.assertFalse(missing.qualified_fit)
            self.assertEqual(runtime.active_models(), ())
            self.assertFalse(inventory.authority_changed)
            self.assertFalse(inventory.auto_activation)

    def test_selection_uses_only_policy_order_and_requires_every_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root, ("first", "second", "ambient"))
            awareness = LiveEnvironmentAwareness(runtime)
            policy = ResourcePolicy(
                authorized_ids=frozenset({"first", "second"}),
                qualified_ids=frozenset({"second", "ambient"}),
                candidate_order=("first", "second"),
            )

            selection = awareness.select(policy, placement="gorxu")
            self.assertEqual(selection.resource_id, "second")
            self.assertTrue(selection.selected)
            self.assertTrue(selection.discovered)
            self.assertTrue(selection.authorized)
            self.assertTrue(selection.ready)
            self.assertTrue(selection.qualified_fit)
            self.assertEqual(runtime.active_models(), ())
            self.assertNotEqual(selection.resource_id, "ambient")

            denied = ResourcePolicy(
                authorized_ids=frozenset({"first"}),
                qualified_ids=frozenset({"second"}),
                candidate_order=("second",),
            )
            with self.assertRaisesRegex(ResourceSelectionError, "no policy-eligible live resource"):
                awareness.select(denied, placement="gorxu")

    def test_selected_execution_requires_explicit_load_and_records_actual_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root, ("selected-model",))
            awareness = LiveEnvironmentAwareness(runtime)
            policy = ResourcePolicy(
                authorized_ids=frozenset({"selected-model"}),
                qualified_ids=frozenset({"selected-model"}),
                candidate_order=("selected-model",),
            )
            selection = awareness.select(policy, placement="gorxu")

            with self.assertRaises(ModelInvocationError):
                awareness.invoke_selected(selection, policy, payload={"objective": "inspect"})

            runtime.load("selected-model", placement="gorxu")
            result = awareness.invoke_selected(selection, policy, payload={"objective": "inspect"})
            identity = result["execution_identity"]
            self.assertEqual(identity["model_id"], "selected-model")
            self.assertEqual(identity["backend"], "echo-v1")
            self.assertEqual(identity["placement"], "gorxu")
            self.assertEqual(identity["artifact_sha256"], hashlib.sha256(b"model").hexdigest())
            self.assertFalse(identity["authority_changed"])

            observed = awareness.inventory(policy, placement="gorxu").get("selected-model")
            self.assertTrue(observed.selected)
            self.assertTrue(observed.observed)
            self.assertEqual(observed.observed_identity, identity)

    def test_reconstitution_clears_volatile_selection_and_observation_then_rediscovers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root, ("selected-model",))
            awareness = LiveEnvironmentAwareness(runtime)
            policy = ResourcePolicy(
                authorized_ids=frozenset({"selected-model"}),
                qualified_ids=frozenset({"selected-model"}),
                candidate_order=("selected-model",),
            )
            selection = awareness.select(policy, placement="gorxu")
            runtime.load("selected-model", placement="gorxu")
            awareness.invoke_selected(selection, policy, payload={"objective": "inspect"})
            (root / "configs" / "models" / "selected-model.bin").unlink()

            report = awareness.reconstitute(policy, placement="gorxu")
            self.assertEqual(report["runtime"]["active_after"], [])
            self.assertFalse(report["auto_activation"])
            self.assertFalse(report["authority_changed"])

            refreshed = report["inventory"].get("selected-model")
            self.assertFalse(refreshed.discovered)
            self.assertFalse(refreshed.ready)
            self.assertFalse(refreshed.selected)
            self.assertFalse(refreshed.observed)
            self.assertIsNone(refreshed.observed_identity)


if __name__ == "__main__":
    unittest.main()
