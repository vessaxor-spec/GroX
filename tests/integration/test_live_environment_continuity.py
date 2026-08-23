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
        return {"echo": dict(payload), "raw_text": "private-output"}

    def unload(self, handle):
        return None


class _BoundReasoner:
    name = "test-bound-local-runtime"

    def __init__(self, runtime: LocalModelRuntime):
        self.runtime = runtime


def _runtime(root: Path) -> LocalModelRuntime:
    model_id = "pilot-observed-model"
    payload = b"pilot-model"
    artifact = root / "configs" / "models" / f"{model_id}.bin"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(payload)
    registry = ModelRegistry.from_mapping(
        asset_root=root,
        raw={
            "schema": "grox-model-registry-v1",
            "models": [
                {
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
                    "provenance": {"source": "integration-test"},
                    "claims": {"language_capable": False},
                }
            ],
        },
    )
    hardware = HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=4,
        total_memory_bytes=8 * 1024 * 1024,
        accelerators=(),
        python_implementation="cpython",
        python_version="3.12.0",
    )
    return LocalModelRuntime(registry, [_EchoBackend()], hardware=hardware)


class LiveEnvironmentPilotContinuityTests(unittest.TestCase):
    def test_pilot_history_survives_reconstitution_and_restart_without_fake_mission(self):
        td, root, bootstrap = temp_vessel()
        try:
            bootstrap.store.close()
            runtime = _runtime(root)
            pilot = PilotGorXu(root, reasoner=_BoundReasoner(runtime))
            policy = ResourcePolicy(
                authorized_ids=frozenset({"pilot-observed-model"}),
                qualified_ids=frozenset({"pilot-observed-model"}),
                candidate_order=("pilot-observed-model",),
            )
            selection = pilot.select_live_resource(policy)
            runtime.load("pilot-observed-model", placement="gorxu")
            execution = pilot._live_environment.invoke_selected(
                selection,
                policy,
                payload={"commander_content": "must not be persisted"},
            )

            history = pilot.live_resource_history("pilot-observed-model")
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["identity"], execution["execution_identity"])
            self.assertTrue(history[0]["historical"])
            self.assertFalse(history[0]["current_readiness_claim"])
            self.assertNotIn("commander_content", str(history[0]["identity"]))
            self.assertNotIn("private-output", str(history[0]["identity"]))
            self.assertEqual(pilot.store.recent_missions(), [])

            report = pilot._live_environment.reconstitute(policy, placement="gorxu")
            current = report["inventory"].get("pilot-observed-model")
            self.assertFalse(current.selected)
            self.assertFalse(current.observed)
            self.assertEqual(len(pilot.live_resource_history("pilot-observed-model")), 1)
            self.assertEqual(pilot.store.recent_missions(), [])
            pilot.store.close()

            restarted = PilotGorXu(root, reasoner=None)
            try:
                restarted_history = restarted.live_resource_history("pilot-observed-model")
                self.assertEqual(len(restarted_history), 1)
                self.assertEqual(restarted_history[0]["identity"], execution["execution_identity"])
                self.assertTrue(restarted_history[0]["historical"])
                self.assertFalse(restarted_history[0]["current_readiness_claim"])
                self.assertEqual(restarted.store.recent_missions(), [])
                unavailable = restarted.live_resource_inventory(policy)
                self.assertEqual(unavailable["status"], "unavailable")
                self.assertEqual(unavailable["resources"], [])
            finally:
                restarted.store.close()
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
