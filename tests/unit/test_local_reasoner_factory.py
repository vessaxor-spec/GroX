from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from grox.reasoning import ReasoningError
from grox.reasoning.factory import build_reasoner_from_env


class LocalReasonerFactoryTests(unittest.TestCase):
    def test_default_factory_behavior_remains_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(build_reasoner_from_env())

    def test_local_provider_requires_commissioned_installed_layout(self) -> None:
        env = {
            "GROX_REASONER_PROVIDER": "local-llama-cpp",
            "GROX_REASONER_MODEL": "qwen",
            "GROX_LLAMA_CPP_EXECUTABLE": "/tmp/llama-cli",
            "GROX_LOCAL_MODEL_LOAD": "explicit",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ReasoningError):
                build_reasoner_from_env()

    def test_local_provider_requires_explicit_model_load_request(self) -> None:
        env = {
            "GROX_REASONER_PROVIDER": "local-llama-cpp",
            "GROX_REASONER_MODEL": "qwen",
            "GROX_LLAMA_CPP_EXECUTABLE": "/tmp/llama-cli",
        }
        layout = SimpleNamespace(legacy_single_root=False)
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(ReasoningError, "GROX_LOCAL_MODEL_LOAD=explicit"):
                build_reasoner_from_env(layout=layout)


if __name__ == "__main__":
    unittest.main()
