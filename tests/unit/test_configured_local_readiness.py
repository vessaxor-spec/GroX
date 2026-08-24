from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from grox.cognition_discovery import ConfiguredCognitionDiscovery
from grox.configured_local_readiness import ConfiguredLocalCognitionReadiness
from grox.native_model_runtime import ModelReadiness
from grox.runtime_layout import VesselLayout


_REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfiguredLocalCognitionReadinessTests(unittest.TestCase):
    def _layout(self, root: Path) -> VesselLayout:
        state = root / "state"
        work = root / "work"
        state.mkdir()
        work.mkdir()
        (root / "models").mkdir()
        return VesselLayout.separated(asset_root=_REPO_ROOT, state_root=state, work_root=work)

    @staticmethod
    def _resource(model: str = "qwen-seed") -> dict[str, object]:
        inventory = ConfiguredCognitionDiscovery(
            {
                "GROX_REASONER_PROVIDER": "local-llama-cpp",
                "GROX_REASONER_MODEL": model,
            }
        ).inventory()
        return inventory["resources"][0]

    def test_available_exact_resource_is_ready_but_never_authorized_or_activated(self):
        with tempfile.TemporaryDirectory() as td:
            layout = self._layout(Path(td))
            runtime = MagicMock()
            runtime.readiness.return_value = SimpleNamespace(
                status=ModelReadiness.AVAILABLE,
                reason="pinned local runtime is ready",
                backend="llama.cpp-cli-b10218",
                artifact_sha256="a" * 64,
                active=False,
            )
            with (
                patch("grox.configured_local_readiness.ModelRegistry.from_asset_root", return_value=object()),
                patch("grox.configured_local_readiness.LlamaCppCLIBackend", return_value=object()),
                patch("grox.configured_local_readiness.LocalModelRuntime", return_value=runtime),
            ):
                inventory = ConfiguredLocalCognitionReadiness(layout).inventory(
                    resource=self._resource(), executable="/opt/grox/llama-cli"
                )

            self.assertEqual(inventory["status"], "ok")
            item = inventory["resources"][0]
            self.assertTrue(item["discovered"])
            self.assertTrue(item["ready"])
            for field in ("authorized", "qualified_fit", "selected", "observed"):
                self.assertFalse(item[field], field)
            self.assertFalse(inventory["network_invoked"])
            self.assertFalse(inventory["credential_inspected"])
            self.assertFalse(inventory["provider_constructed"])
            self.assertFalse(inventory["model_loaded"])
            self.assertFalse(inventory["cognition_invoked"])
            self.assertFalse(inventory["authority_changed"])
            runtime.readiness.assert_called_once_with("qwen-seed")
            runtime.load.assert_not_called()
            runtime.invoke.assert_not_called()

    def test_ready_state_never_implies_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            layout = self._layout(Path(td))
            runtime = MagicMock()
            runtime.readiness.return_value = SimpleNamespace(
                status=ModelReadiness.AVAILABLE,
                reason="ready",
                backend="llama.cpp-cli-b10218",
                artifact_sha256="b" * 64,
                active=False,
            )
            with (
                patch("grox.configured_local_readiness.ModelRegistry.from_asset_root", return_value=object()),
                patch("grox.configured_local_readiness.LlamaCppCLIBackend", return_value=object()),
                patch("grox.configured_local_readiness.LocalModelRuntime", return_value=runtime),
            ):
                item = ConfiguredLocalCognitionReadiness(layout).inventory(
                    resource=self._resource(), executable="/opt/grox/llama-cli"
                )["resources"][0]
            self.assertTrue(item["ready"])
            self.assertFalse(item["authorized"])

    def test_remote_resource_and_legacy_layout_fail_closed_without_runtime_probe(self):
        remote = ConfiguredCognitionDiscovery(
            {
                "GROX_REASONER_PROVIDER": "openai",
                "GROX_REASONER_MODEL": "gpt-test-model",
                "GROX_REASONER_ENDPOINT": "https://api.openai.com/v1/responses",
            }
        ).inventory()["resources"][0]
        with tempfile.TemporaryDirectory() as td:
            legacy = VesselLayout.legacy(Path(td))
            with patch("grox.configured_local_readiness.LocalModelRuntime") as runtime_cls:
                remote_inventory = ConfiguredLocalCognitionReadiness(legacy).inventory(
                    resource=remote, executable="/opt/grox/llama-cli"
                )
                local_inventory = ConfiguredLocalCognitionReadiness(legacy).inventory(
                    resource=self._resource(), executable="/opt/grox/llama-cli"
                )
            self.assertEqual(remote_inventory["status"], "not_applicable")
            self.assertEqual(local_inventory["status"], "unavailable")
            self.assertFalse(local_inventory["resources"][0]["ready"])
            runtime_cls.assert_not_called()

    def test_missing_executable_fails_closed_without_model_activation(self):
        with tempfile.TemporaryDirectory() as td:
            layout = self._layout(Path(td))
            with patch("grox.configured_local_readiness.LocalModelRuntime") as runtime_cls:
                inventory = ConfiguredLocalCognitionReadiness(layout).inventory(
                    resource=self._resource(), executable=""
                )
            self.assertEqual(inventory["status"], "incomplete")
            self.assertFalse(inventory["resources"][0]["ready"])
            self.assertFalse(inventory["model_loaded"])
            runtime_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
