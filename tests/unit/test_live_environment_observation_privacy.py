from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from grox.state import StateStore


class LiveEnvironmentObservationPrivacyTests(unittest.TestCase):
    def _identity(self) -> dict:
        return {
            "model_id": "observed-model",
            "model_kind": "test-policy",
            "backend": "echo-v1",
            "placement": "gorxu",
            "artifact_sha256": "a" * 64,
            "authority_changed": False,
            "hardware": {
                "system": "linux",
                "machine": "x86_64",
                "cpu_count": 4,
                "total_memory_bytes": 8 * 1024 * 1024,
                "accelerators": [],
                "python_implementation": "cpython",
                "python_version": "3.12.0",
            },
        }

    def test_nested_hardware_observation_is_field_allowlisted(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "grox.sqlite3")
            try:
                with self.assertRaisesRegex(ValueError, "unsupported hardware identity field"):
                    store.record_resource_observation(
                        resource_id="observed-model",
                        resource_kind="local_cognition_model",
                        placement="gorxu",
                        identity={
                            **self._identity(),
                            "hardware": {
                                **self._identity()["hardware"],
                                "commander_secret": "must-never-be-persisted",
                            },
                        },
                    )
                self.assertEqual(store.resource_observations(), [])

    def test_expected_hardware_identity_shape_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "grox.sqlite3")
            try:
                row_id = store.record_resource_observation(
                    resource_id="observed-model",
                    resource_kind="local_cognition_model",
                    placement="gorxu",
                    identity=self._identity(),
                )
                self.assertGreater(row_id, 0)
                history = store.resource_observations("observed-model")
                self.assertEqual(len(history), 1)
                self.assertEqual(history[0]["identity"], self._identity())
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
