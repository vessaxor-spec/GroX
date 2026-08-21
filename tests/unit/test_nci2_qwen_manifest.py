from __future__ import annotations

import unittest
from pathlib import Path

from grox.native_model_runtime import LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPPythonBackend


QWEN_MODEL_ID = "qwen3-4b-q4-k-m-seed-v1"
QWEN_SHA256 = "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5"
QWEN_BYTES = 2_497_280_256
QWEN_REVISION = "a9a60d009fa7ff9606305047c2bf77ac25dbec49"


class NCI2QwenManifestTests(unittest.TestCase):
    def test_canonical_registry_carries_exact_seed_identity_without_activation(self) -> None:
        root = Path(__file__).resolve().parents[2]
        registry = ModelRegistry.from_asset_root(root)

        self.assertIn(TINY_MODEL_ID, registry.ids())
        self.assertIn(QWEN_MODEL_ID, registry.ids())

        manifest = registry.get(QWEN_MODEL_ID)
        self.assertEqual(manifest.model_kind, "language-seed-candidate")
        self.assertEqual(manifest.model_format, "gguf")
        self.assertEqual(manifest.backend, "llama.cpp-cli-b10218")
        self.assertEqual(manifest.placements, ("gorxu",))
        self.assertIsNone(manifest.parameter_count)
        self.assertEqual(manifest.artifact.location, "persistent_model_store")
        self.assertEqual(manifest.artifact.path, "Qwen3-4B-Q4_K_M.gguf")
        self.assertEqual(manifest.artifact.sha256, QWEN_SHA256)
        self.assertEqual(manifest.artifact.byte_size, QWEN_BYTES)
        self.assertEqual(manifest.provenance.get("source_revision"), QWEN_REVISION)
        self.assertEqual(manifest.provenance.get("license"), "Apache-2.0")
        self.assertEqual(manifest.provenance.get("quantization"), "Q4_K_M")
        self.assertTrue(bool(manifest.claims.get("language_capable")))
        self.assertFalse(bool(manifest.claims.get("nci2_qualified")))
        self.assertFalse(bool(manifest.claims.get("general_purpose_grox_qualification")))

        runtime = LocalModelRuntime(registry, [TinyMLPPythonBackend()])
        seed = runtime.readiness(QWEN_MODEL_ID)
        self.assertEqual(seed.status, ModelReadiness.UNAVAILABLE)
        self.assertFalse(seed.active)
        self.assertIn("model-store root", seed.reason)
        self.assertEqual(runtime.active_models(), ())

        tiny = runtime.readiness(TINY_MODEL_ID)
        self.assertEqual(tiny.status, ModelReadiness.AVAILABLE)
        self.assertFalse(tiny.active)


if __name__ == "__main__":
    unittest.main()
