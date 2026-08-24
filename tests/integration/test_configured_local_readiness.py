from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from grox.pilot import PilotGorXu
from grox.runtime_layout import VesselLayout


_REPO_ROOT = Path(__file__).resolve().parents[2]


class PilotConfiguredLocalCognitionReadinessTests(unittest.TestCase):
    def test_pilot_readiness_inventory_is_explicit_read_only_and_does_not_change_reasoner(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "state"
            work = root / "work"
            state.mkdir()
            work.mkdir()
            layout = VesselLayout.separated(asset_root=_REPO_ROOT, state_root=state, work_root=work)
            reasoner = object()
            pilot = PilotGorXu(layout, reasoner=reasoner)
            before_reasoner = pilot.reasoner
            expected = {
                "schema": "grox-configured-local-cognition-readiness-v1",
                "status": "unavailable",
                "resources": [],
                "network_invoked": False,
                "credential_inspected": False,
                "provider_constructed": False,
                "model_loaded": False,
                "cognition_invoked": False,
                "authority_changed": False,
                "auto_activation": False,
                "auto_selection": False,
            }
            with (
                patch.dict(
                    os.environ,
                    {
                        "GROX_REASONER_PROVIDER": "local-llama-cpp",
                        "GROX_REASONER_MODEL": "qwen-seed",
                        "GROX_LLAMA_CPP_EXECUTABLE": "/opt/grox/llama-cli",
                        "OPENAI_API_KEY": "SUPER-SECRET-SENTINEL",
                    },
                    clear=False,
                ),
                patch("grox.pilot.ConfiguredLocalCognitionReadiness.inventory", return_value=expected) as awareness,
            ):
                inventory = pilot.live_configured_local_cognition_readiness_inventory()

            self.assertEqual(inventory, expected)
            self.assertIs(pilot.reasoner, before_reasoner)
            self.assertEqual(pilot.store.recent_missions(), [])
            self.assertNotIn("SUPER-SECRET-SENTINEL", repr(inventory))
            awareness.assert_called_once()
            kwargs = awareness.call_args.kwargs
            self.assertEqual(kwargs["executable"], "/opt/grox/llama-cli")
            self.assertEqual(kwargs["resource"]["provider_kind"], "local-llama-cpp")
            self.assertEqual(kwargs["resource"]["model"], "qwen-seed")
            self.assertFalse(kwargs["resource"]["ready"])


if __name__ == "__main__":
    unittest.main()
