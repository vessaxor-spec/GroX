from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from grox.installation import commission_workspace
from grox.model_store import (
    ModelArtifactState,
    ModelStoreError,
    PersistentModelStore,
    ProvisioningSpec,
)
from grox.native_model_runtime import HardwareRuntimeProfile, LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPPythonBackend


def _spec(payload: bytes = b"seed-model") -> ProvisioningSpec:
    return ProvisioningSpec(
        model_id="seed-model",
        target_filename="seed-model.gguf",
        source="https://example.invalid/models/seed-model.gguf",
        source_revision="revision-pinned-for-test",
        license_id="Apache-2.0",
        sha256=hashlib.sha256(payload).hexdigest(),
        byte_size=len(payload),
    )


class PersistentModelStoreTests(unittest.TestCase):
    def test_commissioned_workspace_resolves_persistent_model_store(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "GroX"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            store = PersistentModelStore.from_workspace(config_dir=config)
            self.assertEqual(store.root, (workspace / "models").resolve())
            self.assertNotEqual(store.root, (workspace / "workspace").resolve())
            self.assertNotEqual(store.root, (workspace / "state").resolve())

    def test_missing_workspace_or_model_store_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "config"
            with self.assertRaisesRegex(ModelStoreError, "No commissioned GroX workspace"):
                PersistentModelStore.from_workspace(config_dir=config)

            workspace = root / "GroX"
            commission_workspace(workspace, config_dir=config)
            (workspace / "models").rmdir()
            with self.assertRaisesRegex(ModelStoreError, "missing its model store"):
                PersistentModelStore.from_workspace(config_dir=config)

    def test_provisioning_metadata_is_explicit_and_path_confined(self) -> None:
        payload = b"model"
        digest = hashlib.sha256(payload).hexdigest()
        with self.assertRaisesRegex(ModelStoreError, "source_revision"):
            ProvisioningSpec(
                model_id="seed",
                target_filename="seed.gguf",
                source="https://example.invalid/seed.gguf",
                source_revision="",
                license_id="Apache-2.0",
                sha256=digest,
                byte_size=len(payload),
            )
        for unsafe in ("../seed.gguf", "/tmp/seed.gguf", "nested/seed.gguf", "."):
            with self.subTest(unsafe=unsafe), self.assertRaises(ModelStoreError):
                ProvisioningSpec(
                    model_id="seed",
                    target_filename=unsafe,
                    source="https://example.invalid/seed.gguf",
                    source_revision="rev",
                    license_id="Apache-2.0",
                    sha256=digest,
                    byte_size=len(payload),
                )

    def test_verified_local_import_is_atomic_and_offline_after_provisioning(self) -> None:
        payload = b"verified seed model bytes"
        spec = _spec(payload)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model_root = root / "models"
            model_root.mkdir()
            source = root / "downloaded.gguf"
            source.write_bytes(payload)
            store = PersistentModelStore(model_root)

            before = store.inspect(spec)
            self.assertEqual(before.state, ModelArtifactState.MISSING)
            result = store.provision_from_file(spec, source)
            self.assertEqual(result.status, "provisioned")
            self.assertFalse(result.network_used)
            self.assertFalse(result.authority_changed)
            self.assertFalse(result.auto_activation)
            self.assertEqual(Path(result.path).read_bytes(), payload)
            self.assertEqual(list(model_root.glob("*.partial")), [])

            source.unlink()
            after = store.inspect(spec)
            self.assertEqual(after.state, ModelArtifactState.AVAILABLE)
            self.assertEqual(after.observed_sha256, spec.sha256)
            self.assertEqual(after.observed_bytes, spec.byte_size)

    def test_bad_import_never_becomes_ready_and_partial_file_is_removed(self) -> None:
        expected = b"expected bytes"
        spec = _spec(expected)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model_root = root / "models"
            model_root.mkdir()
            source = root / "wrong.gguf"
            source.write_bytes(b"wrong bytes")
            store = PersistentModelStore(model_root)

            with self.assertRaisesRegex(ModelStoreError, "byte-size mismatch|digest mismatch"):
                store.provision_from_file(spec, source)
            self.assertFalse((model_root / spec.target_filename).exists())
            self.assertEqual(list(model_root.glob("*.partial")), [])
            self.assertEqual(store.inspect(spec).state, ModelArtifactState.MISSING)

    def test_corrupt_existing_target_is_not_overwritten(self) -> None:
        payload = b"expected bytes"
        spec = _spec(payload)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model_root = root / "models"
            model_root.mkdir()
            target = model_root / spec.target_filename
            target.write_bytes(b"conflicting bytes")
            source = root / "source.gguf"
            source.write_bytes(payload)
            store = PersistentModelStore(model_root)

            self.assertEqual(store.inspect(spec).state, ModelArtifactState.CORRUPT)
            with self.assertRaisesRegex(ModelStoreError, "refusing to overwrite"):
                store.provision_from_file(spec, source)
            self.assertEqual(target.read_bytes(), b"conflicting bytes")

    def test_publish_race_fails_closed_without_overwrite_or_partial(self) -> None:
        payload = b"expected bytes"
        spec = _spec(payload)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model_root = root / "models"
            model_root.mkdir()
            source = root / "source.gguf"
            source.write_bytes(payload)
            store = PersistentModelStore(model_root)

            with patch("grox.model_store.os.link", side_effect=FileExistsError("raced")):
                with self.assertRaisesRegex(ModelStoreError, "appeared during provisioning"):
                    store.provision_from_file(spec, source)
            self.assertFalse((model_root / spec.target_filename).exists())
            self.assertEqual(list(model_root.glob("*.partial")), [])

    def test_exact_existing_target_is_idempotent_without_activation(self) -> None:
        payload = b"expected bytes"
        spec = _spec(payload)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model_root = root / "models"
            model_root.mkdir()
            source = root / "source.gguf"
            source.write_bytes(payload)
            store = PersistentModelStore(model_root)
            store.provision_from_file(spec, source)
            second = store.provision_from_file(spec, source)
            self.assertEqual(second.status, "existing")
            self.assertFalse(second.network_used)
            self.assertFalse(second.authority_changed)
            self.assertFalse(second.auto_activation)

    def test_nci1_packaged_model_runtime_contract_remains_unchanged(self) -> None:
        source_root = Path(__file__).resolve().parents[2]
        registry = ModelRegistry.from_asset_root(source_root)
        self.assertEqual(registry.ids(), (TINY_MODEL_ID,))
        profile = HardwareRuntimeProfile(
            system="linux",
            machine="x86_64",
            cpu_count=4,
            total_memory_bytes=32 * 1024 * 1024,
            accelerators=(),
            python_implementation="cpython",
            python_version="3.12.0",
        )
        runtime = LocalModelRuntime(registry, [TinyMLPPythonBackend()], hardware=profile)
        readiness = runtime.readiness(TINY_MODEL_ID)
        self.assertEqual(readiness.status, ModelReadiness.AVAILABLE)
        self.assertFalse(readiness.active)
        self.assertEqual(runtime.active_models(), ())


if __name__ == "__main__":
    unittest.main()
