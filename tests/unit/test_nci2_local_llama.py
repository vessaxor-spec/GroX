from __future__ import annotations

import hashlib
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from grox.llama_cpp_backend import LlamaCppCLIBackend
from grox.native_model_runtime import (
    HardwareRuntimeProfile,
    LocalModelRuntime,
    ModelArtifact,
    ModelReadiness,
    ModelRegistrationError,
    ModelRegistry,
)
from grox.reasoning.base import ReasoningError
from grox.reasoning.local_llama_cpp import LocalLlamaCppReasoningProvider
from grox.tiny_neural_policy import TINY_MODEL_ID, TinyMLPPythonBackend


_DIRECTIVE = "Inspect the repository and identify the highest-risk reliability gap."
_ROSTER = [
    {"crew_id": "architect", "division": "Engineering", "title": "Architect", "domains": ["architecture"], "verification": False},
    {"crew_id": "code-reviewer", "division": "Assurance", "title": "Code Reviewer", "domains": ["code review"], "verification": True},
]


def _hardware() -> HardwareRuntimeProfile:
    return HardwareRuntimeProfile(
        system="linux",
        machine="x86_64",
        cpu_count=8,
        total_memory_bytes=16 * 1024 * 1024 * 1024,
        accelerators=(),
        python_implementation="cpython",
        python_version="3.12.0",
    )


def _write_fake_cli(root: Path, *, mode: str = "valid", version: str = "version: 10218 (de699957b)") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"llama-cli-{mode}"
    script = f'''#!/usr/bin/env python3
import json
import pathlib
import sys
import time

if "--version" in sys.argv:
    print({version!r})
    raise SystemExit(0)

mode = {mode!r}
if mode == "timeout":
    time.sleep(2)
    raise SystemExit(0)
if mode == "nonzero":
    print("simulated backend failure", file=sys.stderr)
    raise SystemExit(7)

args = sys.argv[1:]
prompt_path = pathlib.Path(args[args.index("-f") + 1])
prompt = prompt_path.read_text(encoding="utf-8")
if "--grammar-file" in args:
    grammar_path = pathlib.Path(args[args.index("--grammar-file") + 1])
    if not grammar_path.is_file() or not grammar_path.read_text(encoding="utf-8").strip():
        print("missing grammar", file=sys.stderr)
        raise SystemExit(8)
start = prompt.index("<commander-directive>\\n") + len("<commander-directive>\\n")
end = prompt.index("\\n</commander-directive>")
directive = prompt[start:end]

if mode == "drift":
    directive = "changed intent"
if mode == "unknown-crew":
    crew = ["ghost-crew"]
else:
    crew = ["architect"]

payload = {{
    "commander_intent": directive,
    "objective": "Identify the highest-risk reliability gap.",
    "ambiguous": False,
    "ambiguities": [],
    "assumptions": [],
    "information_needs": ["repository evidence"],
    "candidate_crew_ids": crew,
    "options": [
        {{
            "name": "inspect",
            "rationale": "Gather bounded evidence before proposing change.",
            "advantages": ["evidence first"],
            "risks": ["inspection may be incomplete"],
            "crew_ids": crew,
        }}
    ],
    "recommended_option": "inspect",
    "confidence": 0.8,
    "proposed_mode": "inspect",
    "proposed_risk": "medium",
}}
response = "not-json" if mode == "malformed" else json.dumps(payload, separators=(",", ":"))

if "--output-file" in args:
    output_path = pathlib.Path(args[args.index("--output-file") + 1])
    transcript_prompt = "tampered prompt" if mode == "transcript-tamper" else prompt
    output_path.write_text(
        "User:\\n" + transcript_prompt + "\\n\\nAssistant:\\n" + response + "\\n",
        encoding="utf-8",
    )
else:
    print(response)
'''
    path.write_text(textwrap.dedent(script), encoding="utf-8")
    path.chmod(0o755)
    return path


def _runtime(root: Path, executable: Path) -> tuple[LocalModelRuntime, LlamaCppCLIBackend, str]:
    root.mkdir(parents=True, exist_ok=True)
    asset_root = root / "assets"
    model_root = root / "models"
    asset_root.mkdir()
    model_root.mkdir()
    artifact = b"fake-gguf-model"
    (model_root / "seed.gguf").write_bytes(artifact)
    model_id = "nci2-seed-test"
    backend = LlamaCppCLIBackend(
        executable,
        timeout_seconds=1,
        scratch_root=root / "scratch",
    )
    (root / "scratch").mkdir()
    raw = {
        "schema": "grox-model-registry-v1",
        "models": [
            {
                "model_id": model_id,
                "model_kind": "language-seed-candidate",
                "format": "gguf",
                "backend": backend.name,
                "artifact": {
                    "location": "persistent_model_store",
                    "path": "seed.gguf",
                    "sha256": hashlib.sha256(artifact).hexdigest(),
                    "bytes": len(artifact),
                },
                "lineage": {"generation": 1, "parent_model_id": None},
                "placements": ["gorxu"],
                "parameter_count": 4_000_000_000,
                "resources": {"min_ram_bytes": 0, "required_accelerator": None},
                "provenance": {"source": "unit-test", "license": "Apache-2.0"},
                "claims": {"qualified": False},
            }
        ],
    }
    registry = ModelRegistry.from_mapping(
        asset_root=asset_root,
        model_store_root=model_root,
        raw=raw,
    )
    return LocalModelRuntime(registry, [backend], hardware=_hardware()), backend, model_id


class NCI2ArtifactLocationTests(unittest.TestCase):
    def test_legacy_artifact_location_defaults_to_runtime_assets(self) -> None:
        artifact = ModelArtifact.from_mapping(
            {"path": "configs/models/model.json", "sha256": "0" * 64, "bytes": 1}
        )
        self.assertEqual(artifact.location, "runtime_assets")

    def test_invalid_artifact_location_type_fails_as_registration_error(self) -> None:
        with self.assertRaisesRegex(ModelRegistrationError, "artifact location"):
            ModelArtifact.from_mapping(
                {"location": ["persistent_model_store"], "path": "model.gguf", "sha256": "0" * 64, "bytes": 1}
            )

    def test_existing_nci1_registry_and_tiny_backend_remain_unchanged(self) -> None:
        source_root = Path(__file__).resolve().parents[2]
        registry = ModelRegistry.from_asset_root(source_root)
        self.assertIn(TINY_MODEL_ID, registry.ids())
        self.assertEqual(registry.get(TINY_MODEL_ID).artifact.location, "runtime_assets")
        runtime = LocalModelRuntime(registry, [TinyMLPPythonBackend()], hardware=_hardware())
        self.assertEqual(runtime.readiness(TINY_MODEL_ID).status, ModelReadiness.AVAILABLE)
        self.assertEqual(runtime.active_models(), ())

    def test_persistent_artifact_requires_explicit_store_root(self) -> None:
        raw = {
            "schema": "grox-model-registry-v1",
            "models": [{
                "model_id": "seed",
                "model_kind": "candidate",
                "format": "gguf",
                "backend": "missing-backend",
                "artifact": {"location": "persistent_model_store", "path": "seed.gguf", "sha256": "0" * 64, "bytes": 1},
                "lineage": {"generation": 1, "parent_model_id": None},
                "placements": ["gorxu"],
                "parameter_count": None,
                "resources": {"min_ram_bytes": 0, "required_accelerator": None},
                "provenance": {},
                "claims": {},
            }],
        }
        with tempfile.TemporaryDirectory() as td:
            registry = ModelRegistry.from_mapping(asset_root=td, raw=raw)
            runtime = LocalModelRuntime(registry, [], hardware=_hardware())
            report = runtime.readiness("seed")
            self.assertEqual(report.status, ModelReadiness.UNAVAILABLE)
            self.assertIn("model-store root", report.reason)

    def test_large_artifact_integrity_is_streamed_not_read_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cli = _write_fake_cli(root)
            runtime, _, model_id = _runtime(root, cli)
            with patch.object(Path, "read_bytes", side_effect=AssertionError("read_bytes must not be used")):
                self.assertEqual(runtime.readiness(model_id).status, ModelReadiness.AVAILABLE)


class LlamaCppBackendTests(unittest.TestCase):
    def test_pinned_cli_load_and_invoke_uses_private_gbnf_transcript_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cli = _write_fake_cli(root)
            runtime, backend, model_id = _runtime(root, cli)
            self.assertEqual(runtime.active_models(), ())
            self.assertEqual(runtime.readiness(model_id).status, ModelReadiness.AVAILABLE)
            load = runtime.load(model_id, placement="gorxu")
            self.assertFalse(load["authority_changed"])
            self.assertEqual(runtime.active_models(), (model_id,))

            provider = LocalLlamaCppReasoningProvider(runtime, model_id=model_id)
            result = provider.interpret(_DIRECTIVE, roster=_ROSTER)
            self.assertEqual(result.commander_intent, _DIRECTIVE)
            self.assertEqual(result.candidate_crew_ids, ["architect"])
            self.assertIsNotNone(provider.usage_snapshot())
            self.assertEqual(provider.usage_snapshot().model, model_id)

            command = list(backend.last_command or ())
            joined = " ".join(command)
            self.assertNotIn("-hf", command)
            self.assertNotIn("http://", joined)
            self.assertNotIn("https://", joined)
            self.assertNotIn(_DIRECTIVE, joined)
            self.assertIn("--grammar-file", command)
            self.assertNotIn("-j", command)
            self.assertIn("--output-file", command)
            self.assertIn("--fit", command)
            self.assertEqual(command[command.index("--fit") + 1], "off")
            self.assertIn("-dev", command)
            self.assertEqual(command[command.index("-dev") + 1], "none")
            self.assertIn("--no-op-offload", command)
            self.assertIn("-ngl", command)
            self.assertEqual(command[command.index("-ngl") + 1], "0")
            self.assertIn("--simple-io", command)
            self.assertIn("--reasoning", command)
            self.assertEqual(command[command.index("--reasoning") + 1], "off")
            self.assertIn("--skip-chat-parsing", command)

            for flag in ("-f", "--grammar-file", "--output-file"):
                temporary_path = Path(command[command.index(flag) + 1])
                self.assertFalse(temporary_path.exists(), flag)

            reconstituted = runtime.reconstitute()
            self.assertEqual(reconstituted["active_after"], [])
            self.assertFalse(reconstituted["auto_activation"])
            self.assertFalse(reconstituted["authority_changed"])

    def test_transcript_prompt_tampering_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime, backend, model_id = _runtime(root, _write_fake_cli(root, mode="transcript-tamper"))
            runtime.load(model_id, placement="gorxu")
            provider = LocalLlamaCppReasoningProvider(runtime, model_id=model_id)
            with self.assertRaisesRegex(ReasoningError, "exact prompt boundary"):
                provider.interpret(_DIRECTIVE, roster=_ROSTER)
            self.assertIsNone(provider.usage_snapshot())
            command = list(backend.last_command or ())
            for flag in ("-f", "--grammar-file", "--output-file"):
                self.assertFalse(Path(command[command.index(flag) + 1]).exists())

    def test_wrong_pinned_version_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cli = _write_fake_cli(root, version="version: 10217 (aaaaaaaa)")
            runtime, _, model_id = _runtime(root, cli)
            report = runtime.readiness(model_id)
            self.assertEqual(report.status, ModelReadiness.UNSUPPORTED)
            self.assertIn("build mismatch", report.reason)

    def test_missing_or_non_executable_cli_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            missing = (root / "missing-llama-cli").resolve()
            runtime, _, model_id = _runtime(root, missing)
            self.assertEqual(runtime.readiness(model_id).status, ModelReadiness.UNSUPPORTED)

            cli = _write_fake_cli(root)
            cli.chmod(0o644)
            runtime2, _, model_id2 = _runtime(root / "second", cli)
            self.assertEqual(runtime2.readiness(model_id2).status, ModelReadiness.UNSUPPORTED)

    def test_timeout_and_nonzero_exit_are_contained(self) -> None:
        for mode, expected in (("timeout", "timed out"), ("nonzero", "returned 7")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                cli = _write_fake_cli(root, mode=mode)
                runtime, _, model_id = _runtime(root, cli)
                runtime.load(model_id, placement="gorxu")
                provider = LocalLlamaCppReasoningProvider(runtime, model_id=model_id)
                with self.assertRaisesRegex(ReasoningError, expected):
                    provider.interpret(_DIRECTIVE, roster=_ROSTER)


class LocalLlamaReasoningProviderTests(unittest.TestCase):
    def test_provider_requires_explicit_model_load(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runtime, _, model_id = _runtime(root, _write_fake_cli(root))
            provider = LocalLlamaCppReasoningProvider(runtime, model_id=model_id)
            with self.assertRaisesRegex(ReasoningError, "not explicitly loaded"):
                provider.interpret(_DIRECTIVE, roster=_ROSTER)
            self.assertEqual(runtime.active_models(), ())

    def test_malformed_output_intent_drift_and_unknown_crew_fail_closed(self) -> None:
        cases = (
            ("malformed", "invalid local structured reasoning output"),
            ("drift", "preserve Commander intent verbatim"),
            ("unknown-crew", "outside the supplied Standing Crew Directory"),
        )
        for mode, expected in cases:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                runtime, _, model_id = _runtime(root, _write_fake_cli(root, mode=mode))
                runtime.load(model_id, placement="gorxu")
                provider = LocalLlamaCppReasoningProvider(runtime, model_id=model_id)
                with self.assertRaisesRegex(ReasoningError, expected):
                    provider.interpret(_DIRECTIVE, roster=_ROSTER)
                self.assertIsNone(provider.usage_snapshot())


if __name__ == "__main__":
    unittest.main()
