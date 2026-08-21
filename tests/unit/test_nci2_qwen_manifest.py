from __future__ import annotations

import unittest
from pathlib import Path

from grox.native_model_runtime import LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPPythonBackend


QWEN_MODEL_ID = "qwen3-0.6b-q4-0-seed-v1"
QWEN_SHA256 = "da2572f16c06133561ce56accaa822216f2391ef4d37fba427801cd6736417d4"
QWEN_BYTES = 428_970_080
QWEN_REVISION = "a41486f827d17edd055fe6b3b0ba3f8d427c0519"
QWEN_XET = "8ad0a46ab1560d187c313af45b26af00f03882f1cd127766037e9aa279f4a3da"


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
        self.assertEqual(manifest.parameter_count, 600_000_000)
        self.assertEqual(manifest.artifact.location, "persistent_model_store")
        self.assertEqual(manifest.artifact.path, "Qwen3-0.6B-Q4_0.gguf")
        self.assertEqual(manifest.artifact.sha256, QWEN_SHA256)
        self.assertEqual(manifest.artifact.byte_size, QWEN_BYTES)
        self.assertEqual(manifest.provenance.get("source_revision"), QWEN_REVISION)
        self.assertEqual(manifest.provenance.get("xet_hash"), QWEN_XET)
        self.assertEqual(manifest.provenance.get("artifact_repository"), "ggml-org/Qwen3-0.6B-GGUF")
        self.assertEqual(manifest.provenance.get("source_model"), "Qwen/Qwen3-0.6B")
        self.assertEqual(manifest.provenance.get("license"), "Apache-2.0")
        self.assertEqual(manifest.provenance.get("quantization"), "Q4_0")
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
