from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from grox.crew_provider import bind_crew_cognition_provider, qualify_bound_crew_cognition_provider
from grox.native_model_runtime import HardwareRuntimeProfile, LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPCrewCognitionProvider, TinyMLPPythonBackend
from tests._support import temp_vessel


def _profile() -> HardwareRuntimeProfile:
    return HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=4,
        total_memory_bytes=32 * 1024 * 1024,
        accelerators=(),
        python_implementation="cpython",
        python_version="3.12.0",
    )


class NativeModelRuntimeIntegrationTests(unittest.TestCase):
    def test_registered_tiny_policy_runs_through_existing_gorxu_owned_crew_seam(self):
        source_root = Path(__file__).resolve().parents[2]
        td, root, pilot = temp_vessel()
        try:
            shutil.copytree(source_root / "configs" / "models", root / "configs" / "models")
            registry = ModelRegistry.from_asset_root(root)
            runtime = LocalModelRuntime(registry, [TinyMLPPythonBackend()], hardware=_profile())

            readiness = runtime.readiness(TINY_MODEL_ID)
            self.assertEqual(readiness.status, ModelReadiness.AVAILABLE)
            self.assertFalse(readiness.active)
            self.assertEqual(runtime.active_models(), ())

            load_evidence = runtime.load(TINY_MODEL_ID, placement="crew")
            self.assertFalse(load_evidence["authority_changed"])
            self.assertFalse(load_evidence["pilot_binding_changed"])

            pilot.intelligence.remember(
                kind="semantic",
                memory_key="nci-1d-native-model-runtime",
                content="README bounded provider qualification uses governed Inspect evidence.",
                scope="crew",
                crew_id="backend-engineer",
                task_class="general",
                provenance={"source": "nci-1d-native-model-runtime"},
            )
            provider = TinyMLPCrewCognitionProvider(runtime)
            self.assertEqual(bind_crew_cognition_provider(pilot, provider), provider.name)

            report = qualify_bound_crew_cognition_provider(
                pilot,
                directive="Inspect README evidence for bounded provider qualification",
                crew_id="backend-engineer",
            )
            self.assertEqual(report["status"], "PASS")
            self.assertTrue(all(report["checks"].values()))
            self.assertFalse(report["live_provider_claim"])
            self.assertEqual(report["provider"], "local-neural-session-crew-v1")
            self.assertEqual(report["provider_observability"].get("model"), TINY_MODEL_ID)
            self.assertGreaterEqual(len(provider.inference_trace), 2)
            self.assertEqual(provider.inference_trace[0]["action"], "fs_read")
            self.assertEqual(provider.inference_trace[-1]["action"], "finish")
            self.assertTrue(provider.inference_trace[0]["craft_present"])
            self.assertTrue(provider.inference_trace[0]["memory_present"])
            self.assertTrue(all(not row["authority_changed"] for row in provider.inference_trace))

            mission = pilot.store.mission(report["mission_id"])
            evidence = list((mission or {}).get("evidence") or [])
            kinds = {row.get("kind") for row in evidence}
            self.assertIn("crew_cognition", kinds)
            self.assertNotIn("mutation", kinds)
            self.assertNotIn("mutation_rollback", kinds)

            reconstituted = runtime.reconstitute()
            self.assertEqual(reconstituted["active_after"], [])
            self.assertFalse(reconstituted["auto_activation"])
            self.assertFalse(reconstituted["authority_changed"])
            models_by_id = {item["model_id"]: item for item in reconstituted["models"]}
            self.assertEqual(models_by_id[TINY_MODEL_ID]["status"], ModelReadiness.AVAILABLE.value)
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
