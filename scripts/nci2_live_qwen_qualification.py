from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any

import grox
from grox.contracts import MissionMode, RiskClass
from grox.installation import installed_vessel_layout
from grox.llama_cpp_backend import LlamaCppCLIBackend
from grox.model_store import ModelArtifactState, PersistentModelStore, ProvisioningSpec
from grox.native_model_runtime import LocalModelRuntime, ModelReadiness, ModelRegistry
from grox.pilot import PilotGorXu
from grox.reasoning.local_llama_cpp import LocalLlamaCppReasoningProvider
from grox.tiny_neural_policy import TinyMLPPythonBackend


MODEL_ID = "qwen3-0.6b-q4-0-seed-v1"
MODEL_FILENAME = "Qwen3-0.6B-Q4_0.gguf"
MODEL_SHA256 = "da2572f16c06133561ce56accaa822216f2391ef4d37fba427801cd6736417d4"
MODEL_BYTES = 428_970_080
MODEL_SOURCE = "https://huggingface.co/ggml-org/Qwen3-0.6B-GGUF"
MODEL_REVISION = "a41486f827d17edd055fe6b3b0ba3f8d427c0519"
MODEL_LICENSE = "Apache-2.0"
DIRECTIVE = "Inspect README.md for the most important reliability risk. Do not modify files. /no_think"


def _dump(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _assert_installed_outside_checkout(forbidden_source_root: Path | None) -> str:
    module_path = Path(grox.__file__).resolve()
    if forbidden_source_root is not None:
        root = forbidden_source_root.expanduser().resolve()
        try:
            module_path.relative_to(root)
        except ValueError:
            pass
        else:
            raise AssertionError(f"qualification imported GroX from source checkout: {module_path}")
    if "site-packages" not in module_path.parts:
        raise AssertionError(f"qualification did not import installed GroX from site-packages: {module_path}")
    return str(module_path)


def _assert_network_isolated() -> None:
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=1.0):
            pass
    except OSError:
        return
    raise AssertionError("qualification network namespace can reach an external address")


def _assert_no_vendor_credentials() -> None:
    forbidden = (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
    )
    present = [name for name in forbidden if str(os.environ.get(name, "")).strip()]
    if present:
        raise AssertionError(f"vendor credentials present during local qualification: {present}")


def _spec() -> ProvisioningSpec:
    return ProvisioningSpec(
        model_id=MODEL_ID,
        target_filename=MODEL_FILENAME,
        source=MODEL_SOURCE,
        source_revision=MODEL_REVISION,
        license_id=MODEL_LICENSE,
        sha256=MODEL_SHA256,
        byte_size=MODEL_BYTES,
    )


def provision(args: argparse.Namespace) -> None:
    installed_module = _assert_installed_outside_checkout(args.forbidden_source_root)
    store = PersistentModelStore.from_workspace(config_dir=args.config_dir)
    result = store.provision_from_file(_spec(), args.model_source)
    report = store.inspect(_spec())
    if report.state is not ModelArtifactState.AVAILABLE:
        raise AssertionError(report.to_dict())

    workspace = store.root.parent
    commander_work = workspace / "workspace"
    commander_work.mkdir(parents=True, exist_ok=True)
    (commander_work / "README.md").write_text(
        "# Commander Workspace Reliability Note\n\n"
        "The local backup job has no configured restore verification.\n"
        "A restore drill has not yet been recorded.\n",
        encoding="utf-8",
    )
    tests_dir = commander_work / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_smoke.py").write_text(
        "import unittest\n\n"
        "class CommanderWorkspaceSmoke(unittest.TestCase):\n"
        "    def test_workspace_is_testable(self):\n"
        "        self.assertTrue(True)\n",
        encoding="utf-8",
    )
    _dump(
        {
            "schema": "grox-nci2-live-provisioning-v1",
            "status": "PASS",
            "installed_module": installed_module,
            "model": report.to_dict(),
            "provisioning": result.to_dict(),
            "authority_changed": False,
            "auto_activation": False,
            "network_used_for_model_admission": False,
        }
    )


def qualify(args: argparse.Namespace) -> None:
    installed_module = _assert_installed_outside_checkout(args.forbidden_source_root)
    _assert_no_vendor_credentials()
    _assert_network_isolated()

    layout = installed_vessel_layout(config_dir=args.config_dir)
    store = PersistentModelStore.from_workspace(config_dir=args.config_dir)
    artifact = store.inspect(_spec())
    if artifact.state is not ModelArtifactState.AVAILABLE:
        raise AssertionError(artifact.to_dict())

    scratch = layout.state_root / "nci2-llama-scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    registry = ModelRegistry.from_asset_root(
        layout.asset_root,
        model_store_root=store.root,
    )
    if MODEL_ID not in registry.ids():
        raise AssertionError(f"installed registry is missing {MODEL_ID}: {registry.ids()}")

    backend = LlamaCppCLIBackend(
        args.llama_cli,
        context_tokens=4096,
        max_output_tokens=256,
        max_threads=4,
        timeout_seconds=600,
        scratch_root=scratch,
    )
    runtime = LocalModelRuntime(
        registry,
        [TinyMLPPythonBackend(), backend],
    )

    before = runtime.readiness(MODEL_ID)
    if before.status is not ModelReadiness.AVAILABLE or before.active:
        raise AssertionError(before.to_dict())
    if runtime.active_models():
        raise AssertionError(f"model registry/readiness auto-activated models: {runtime.active_models()}")

    load = runtime.load(MODEL_ID, placement="gorxu")
    if load.get("authority_changed") is not False or load.get("pilot_binding_changed") is not False:
        raise AssertionError(load)

    provider = LocalLlamaCppReasoningProvider(runtime, model_id=MODEL_ID)
    pilot = PilotGorXu(layout, reasoner=provider)
    result = pilot.command(
        DIRECTIVE,
        mode=MissionMode.inspect,
        risk=RiskClass.high,
        scope="README.md",
    )

    cognition = result.get("cognition")
    if result.get("execution_status") != "completed":
        raise AssertionError(result)
    if result.get("cognition_error") is not None or not isinstance(cognition, dict):
        raise AssertionError(result)
    if cognition.get("commander_intent") != DIRECTIVE:
        raise AssertionError(cognition)
    candidate_crew = cognition.get("candidate_crew_ids")
    if not isinstance(candidate_crew, list) or not candidate_crew:
        raise AssertionError(f"local cognition did not recommend Standing Crew: {cognition}")
    if result.get("crew") not in candidate_crew:
        raise AssertionError(
            f"deterministic routing did not select a locally recommended eligible Crew: "
            f"selected={result.get('crew')} candidates={candidate_crew}"
        )
    if result.get("outcome", {}).get("mutation") is not False:
        raise AssertionError(result)
    verification = result.get("verification")
    if not isinstance(verification, dict) or verification.get("ok") is not True:
        raise AssertionError(result)
    if verification.get("verifier") == result.get("crew"):
        raise AssertionError(result)

    mission = pilot.store.mission(result["mission_id"])
    if not isinstance(mission, dict):
        raise AssertionError("qualified Mission was not persisted")
    evidence = mission.get("evidence") or []
    kinds = [row.get("kind") for row in evidence]
    if "cognitive_plan" not in kinds:
        raise AssertionError(f"qualified Mission lacks cognitive_plan evidence: {kinds}")
    if "cognition_degraded" in kinds:
        raise AssertionError(f"qualified Mission used deterministic cognition fallback: {kinds}")
    if "mission_outcome" not in kinds:
        raise AssertionError(f"qualified Mission lacks mission_outcome evidence: {kinds}")

    reconstituted = runtime.reconstitute()
    if reconstituted.get("active_after") != []:
        raise AssertionError(reconstituted)
    if reconstituted.get("auto_activation") is not False:
        raise AssertionError(reconstituted)
    if reconstituted.get("authority_changed") is not False:
        raise AssertionError(reconstituted)

    _assert_network_isolated()
    _dump(
        {
            "schema": "grox-nci2-live-qwen-qualification-v1",
            "status": "PASS",
            "installed_module": installed_module,
            "model_id": MODEL_ID,
            "model_sha256": MODEL_SHA256,
            "model_bytes": MODEL_BYTES,
            "backend": backend.name,
            "backend_version": backend.expected_version,
            "backend_commit_prefix": backend.expected_commit_prefix,
            "network_isolated": True,
            "vendor_credentials_present": False,
            "readiness_before_load": before.to_dict(),
            "load": load,
            "mission": {
                "mission_id": result["mission_id"],
                "directive": DIRECTIVE,
                "crew": result.get("crew"),
                "candidate_crew_ids": candidate_crew,
                "recommended_option": cognition.get("recommended_option"),
                "confidence": cognition.get("confidence"),
                "execution_status": result.get("execution_status"),
                "mission_status": result.get("mission_status"),
                "outcome": result.get("outcome"),
                "verification": verification,
                "evidence_kinds": kinds,
            },
            "reconstitution": reconstituted,
            "authority_changed": False,
            "auto_activation": False,
        }
    )


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=("provision", "qualify"))
    ap.add_argument("--config-dir", type=Path, required=True)
    ap.add_argument("--forbidden-source-root", type=Path)
    ap.add_argument("--model-source", type=Path)
    ap.add_argument("--llama-cli", type=Path)
    return ap


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    if args.phase == "provision":
        if args.model_source is None:
            raise SystemExit("--model-source is required for provision")
        provision(args)
        return
    if args.llama_cli is None:
        raise SystemExit("--llama-cli is required for qualify")
    qualify(args)


if __name__ == "__main__":
    main(sys.argv[1:])
