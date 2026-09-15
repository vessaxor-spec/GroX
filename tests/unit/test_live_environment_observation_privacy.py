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

    def test_configured_remote_observation_has_separate_strict_allowlist(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "grox.sqlite3")
            identity = {
                "observation_id": "OBS-remote",
                "selection_id": "SEL-remote",
                "resource_id": "cognition:configured:openai:abc123",
                "resource_kind": "configured_remote_cognition",
                "provider_kind": "openai",
                "model": "remote-model",
                "endpoint": "https://api.openai.com/v1/responses",
                "mission_id": "MSN-remote",
                "order_id": "ORD-remote",
                "placement": "mission_interpretation",
                "response_id": "resp-remote",
                "response_model": "remote-model",
                "authority_changed": False,
            }
            try:
                row_id = store.record_resource_observation(
                    resource_id=identity["resource_id"],
                    resource_kind="configured_remote_cognition",
                    placement="mission_interpretation",
                    identity=identity,
                )
                self.assertGreater(row_id, 0)
                history = store.resource_observations(identity["resource_id"])
                self.assertEqual(history[0]["identity"], identity)

                with self.assertRaisesRegex(
                    ValueError, "unsupported configured remote identity field"
                ):
                    store.record_resource_observation(
                        resource_id=identity["resource_id"],
                        resource_kind="configured_remote_cognition",
                        placement="mission_interpretation",
                        identity={
                            **identity,
                            "credential_alias": "must-not-enter-observation-ledger",
                        },
                    )
                self.assertEqual(len(store.resource_observations(identity["resource_id"])), 1)
            finally:
                store.close()

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
            finally:
                store.close()

    def test_nested_hardware_observation_requires_complete_identity_shape(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "grox.sqlite3")
            try:
                hardware = dict(self._identity()["hardware"])
                hardware.pop("python_version")
                with self.assertRaisesRegex(ValueError, "missing hardware identity field"):
                    store.record_resource_observation(
                        resource_id="observed-model",
                        resource_kind="local_cognition_model",
                        placement="gorxu",
                        identity={**self._identity(), "hardware": hardware},
                    )
                self.assertEqual(store.resource_observations(), [])
            finally:
                store.close()

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
