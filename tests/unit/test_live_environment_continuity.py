from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any

from grox.live_environment import (
    LiveEnvironmentAwareness,
    ResourceObservationError,
    ResourcePolicy,
)
from grox.native_model_runtime import HardwareRuntimeProfile, LocalModelRuntime, ModelRegistry
from grox.state import StateStore


class _EchoBackend:
    name = "echo-v1"

    def supports(self, manifest, hardware):
        return True, "echo backend available"

    def load(self, manifest, artifact_path):
        return {"model_id": manifest.model_id, "path": str(artifact_path)}

    def invoke(self, handle, payload):
        return {"echo": dict(payload), "raw_text": "must-not-enter-history"}

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


def _runtime(root: Path, model_id: str = "observed-model") -> LocalModelRuntime:
    payload = b"model"
    path = root / "configs" / "models" / f"{model_id}.bin"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
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
                    "provenance": {"source": "unit-test"},
                    "claims": {"language_capable": False},
                }
            ],
        },
    )
    return LocalModelRuntime(registry, [_EchoBackend()], hardware=_profile())


def _policy(model_id: str = "observed-model") -> ResourcePolicy:
    return ResourcePolicy(
        authorized_ids=frozenset({model_id}),
        qualified_ids=frozenset({model_id}),
        candidate_order=(model_id,),
    )


class LiveEnvironmentContinuityTests(unittest.TestCase):
    def test_observed_execution_persists_identity_only_and_survives_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root)
            db_path = root / "state" / "grox.sqlite3"
            store = StateStore(db_path)
            awareness = LiveEnvironmentAwareness(
                runtime,
                observation_recorder=store.record_resource_observation,
            )
            policy = _policy()
            selection = awareness.select(policy, placement="gorxu")
            runtime.load("observed-model", placement="gorxu")
            execution = awareness.invoke_selected(
                selection,
                policy,
                payload={"secret_prompt": "do not persist this"},
            )

            history = store.resource_observations(resource_id="observed-model")
            self.assertEqual(len(history), 1)
            row = history[0]
            self.assertEqual(row["resource_id"], "observed-model")
            self.assertEqual(row["resource_kind"], "local_cognition_model")
            self.assertEqual(row["placement"], "gorxu")
            self.assertEqual(row["identity"], execution["execution_identity"])
            self.assertNotIn("output", row["identity"])
            self.assertNotIn("echo", row["identity"])
            self.assertNotIn("raw_text", row["identity"])
            self.assertNotIn("secret_prompt", str(row["identity"]))

            report = awareness.reconstitute(policy, placement="gorxu")
            refreshed = report["inventory"].get("observed-model")
            self.assertFalse(refreshed.selected)
            self.assertFalse(refreshed.observed)
            self.assertIsNone(refreshed.observed_identity)
            self.assertEqual(len(store.resource_observations(resource_id="observed-model")), 1)
            store.close()

            reopened = StateStore(db_path)
            try:
                persisted = reopened.resource_observations(resource_id="observed-model")
                self.assertEqual(len(persisted), 1)
                self.assertEqual(persisted[0]["identity"], execution["execution_identity"])
                self.assertTrue(persisted[0]["historical"])
                self.assertFalse(persisted[0]["current_readiness_claim"])
            finally:
                reopened.close()

    def test_observation_store_rejects_raw_output_authority_change_and_identity_drift(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "grox.sqlite3")
            base: dict[str, Any] = {
                "model_id": "observed-model",
                "model_kind": "test-policy",
                "backend": "echo-v1",
                "placement": "gorxu",
                "artifact_sha256": "a" * 64,
                "authority_changed": False,
                "hardware": _profile().to_dict(),
            }
            try:
                with self.assertRaisesRegex(ValueError, "unsupported execution identity field"):
                    store.record_resource_observation(
                        resource_id="observed-model",
                        resource_kind="local_cognition_model",
                        placement="gorxu",
                        identity={**base, "output": {"raw": "forbidden"}},
                    )
                with self.assertRaisesRegex(ValueError, "authority change"):
                    store.record_resource_observation(
                        resource_id="observed-model",
                        resource_kind="local_cognition_model",
                        placement="gorxu",
                        identity={**base, "authority_changed": True},
                    )
                with self.assertRaisesRegex(ValueError, "model identity mismatch"):
                    store.record_resource_observation(
                        resource_id="observed-model",
                        resource_kind="local_cognition_model",
                        placement="gorxu",
                        identity={**base, "model_id": "other-model"},
                    )
            finally:
                store.close()

    def test_observation_recorder_failure_is_explicit_and_not_marked_observed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime = _runtime(root)

            def fail_record(**kwargs):
                raise OSError("disk unavailable")

            awareness = LiveEnvironmentAwareness(runtime, observation_recorder=fail_record)
            policy = _policy()
            selection = awareness.select(policy, placement="gorxu")
            runtime.load("observed-model", placement="gorxu")
            with self.assertRaisesRegex(ResourceObservationError, "observation persistence failed"):
                awareness.invoke_selected(selection, policy, payload={"objective": "inspect"})
            current = awareness.inventory(policy, placement="gorxu").get("observed-model")
            self.assertTrue(current.selected)
            self.assertFalse(current.observed)
            self.assertIsNone(current.observed_identity)


if __name__ == "__main__":
    unittest.main()
