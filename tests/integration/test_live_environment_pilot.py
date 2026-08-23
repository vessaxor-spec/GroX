from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from grox.live_environment import ResourcePolicy
from grox.native_model_runtime import HardwareRuntimeProfile, LocalModelRuntime, ModelRegistry
from grox.pilot import PilotGorXu
from tests._support import temp_vessel


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


class _LocalReasoner:
    name = "test-local-reasoner"

    def __init__(self, runtime: LocalModelRuntime):
        self.runtime = runtime


def _runtime(root: Path) -> LocalModelRuntime:
    payload = b"pilot-live-model"
    artifact = root / "configs" / "models" / "pilot-live-model.bin"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(payload)
    registry = ModelRegistry.from_mapping(
        asset_root=root,
        raw={
            "schema": "grox-model-registry-v1",
            "models": [
                {
                    "model_id": "pilot-live-model",
                    "model_kind": "test-policy",
                    "format": "test-v1",
                    "backend": "echo-v1",
                    "artifact": {
                        "path": "configs/models/pilot-live-model.bin",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "bytes": len(payload),
                    },
                    "lineage": {"generation": 1, "parent_model_id": None},
                    "placements": ["gorxu"],
                    "parameter_count": 1,
                    "resources": {"min_ram_bytes": 0, "required_accelerator": None},
                    "provenance": {"source": "unit-test"},
                    "claims": {},
                }
            ],
        },
    )
    profile = HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=4,
        total_memory_bytes=8 * 1024 * 1024,
        accelerators=(),
        python_implementation="cpython",
        python_version="3.12.0",
    )
    return LocalModelRuntime(registry, [_EchoBackend()], hardware=profile)


class PilotLiveEnvironmentTests(unittest.TestCase):
    def test_pilot_can_inventory_and_select_bound_local_runtime_without_activation(self):
        td, root, _ = temp_vessel()
        try:
            runtime = _runtime(root)
            pilot = PilotGorXu(root, reasoner=_LocalReasoner(runtime))
            policy = ResourcePolicy(
                authorized_ids=frozenset({"pilot-live-model"}),
                qualified_ids=frozenset({"pilot-live-model"}),
                candidate_order=("pilot-live-model",),
            )

            inventory = pilot.live_resource_inventory(policy, placement="gorxu")
            self.assertEqual(inventory["status"], "ok")
            self.assertEqual(inventory["resources"][0]["resource_id"], "pilot-live-model")
            self.assertTrue(inventory["resources"][0]["selectable"])
            self.assertFalse(inventory["authority_changed"])
            self.assertFalse(inventory["auto_activation"])
            self.assertEqual(runtime.active_models(), ())

            selected = pilot.select_live_resource(policy, placement="gorxu")
            self.assertEqual(selected.resource_id, "pilot-live-model")
            self.assertTrue(selected.selected)
            self.assertEqual(runtime.active_models(), ())
        finally:
            td.cleanup()

    def test_pilot_without_local_runtime_reports_no_live_local_inventory(self):
        td, _, pilot = temp_vessel()
        try:
            inventory = pilot.live_resource_inventory(
                ResourcePolicy(
                    authorized_ids=frozenset({"ambient"}),
                    qualified_ids=frozenset({"ambient"}),
                    candidate_order=("ambient",),
                ),
                placement="gorxu",
            )
            self.assertEqual(inventory["status"], "unavailable")
            self.assertEqual(inventory["resources"], [])
            self.assertFalse(inventory["authority_changed"])
            self.assertFalse(inventory["auto_activation"])
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
