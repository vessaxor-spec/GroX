from __future__ import annotations

import unittest
from pathlib import Path

from grox.native_model_runtime import LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPPythonBackend


QWEN_MODEL_ID = "qwen3-1.7b-q4-k-m-seed-v1"
QWEN_SHA256 = "d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5"
QWEN_BYTES = 1_282_439_264
QWEN_REVISION = "daeb8e2d528a760970442092f6bf1e55c3b659eb"
QWEN_XET = "0a8e661bad7f1ea5accdd078b6a2aca20ff0201100bbf128aa1cc22c643d7221"


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
        self.assertEqual(manifest.parameter_count, 1_700_000_000)
        self.assertEqual(manifest.artifact.location, "persistent_model_store")
        self.assertEqual(manifest.artifact.path, "Qwen3-1.7B-Q4_K_M.gguf")
        self.assertEqual(manifest.artifact.sha256, QWEN_SHA256)
        self.assertEqual(manifest.artifact.byte_size, QWEN_BYTES)
        self.assertEqual(manifest.provenance.get("source_revision"), QWEN_REVISION)
        self.assertEqual(manifest.provenance.get("xet_hash"), QWEN_XET)
        self.assertEqual(manifest.provenance.get("artifact_repository"), "ggml-org/Qwen3-1.7B-GGUF")
        self.assertEqual(manifest.provenance.get("source_model"), "Qwen/Qwen3-1.7B")
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
