from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import ReasoningError
from .local_llama_cpp import LocalLlamaCppReasoningProvider
from .openai_responses import OpenAIResponsesProvider
from ..llama_cpp_backend import LlamaCppCLIBackend
from ..native_model_runtime import LocalModelRuntime, ModelReadiness, ModelRegistry, ModelRuntimeError


def _build_local_llama_reasoner(layout: Any) -> LocalLlamaCppReasoningProvider:
    if layout is None or bool(getattr(layout, "legacy_single_root", True)):
        raise ReasoningError("local llama.cpp cognition requires a commissioned installed Vessel layout")
    if os.getenv("GROX_LOCAL_MODEL_LOAD", "").strip().lower() != "explicit":
        raise ReasoningError(
            "local model loading requires GROX_LOCAL_MODEL_LOAD=explicit; registration/readiness never auto-activate a model"
        )
    model_id = os.getenv("GROX_REASONER_MODEL", "").strip()
    executable = os.getenv("GROX_LLAMA_CPP_EXECUTABLE", "").strip()
    if not model_id or not executable:
        raise ReasoningError(
            "GROX_REASONER_PROVIDER=local-llama-cpp requires GROX_REASONER_MODEL and GROX_LLAMA_CPP_EXECUTABLE"
        )
    model_store_root = (Path(layout.work_root).resolve().parent / "models").resolve()
    if not model_store_root.is_dir():
        raise ReasoningError(f"commissioned GroX model store is unavailable: {model_store_root}")
    scratch = Path(layout.state_root).resolve() / "local-llama-scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        registry = ModelRegistry.from_asset_root(layout.asset_root, model_store_root=model_store_root)
        backend = LlamaCppCLIBackend(
            executable,
            context_tokens=8192,
            max_output_tokens=512,
            max_threads=4,
            timeout_seconds=600,
            scratch_root=scratch,
        )
        runtime = LocalModelRuntime(registry, [backend])
        readiness = runtime.readiness(model_id)
        if readiness.status is not ModelReadiness.AVAILABLE or readiness.active:
            raise ReasoningError(f"local model is not explicitly loadable: {readiness.to_dict()}")
        load = runtime.load(model_id, placement="gorxu")
    except ReasoningError:
        raise
    except (ModelRuntimeError, OSError, ValueError) as exc:
        raise ReasoningError(f"local llama.cpp cognition startup failed: {exc}") from exc
    if load.get("authority_changed") is not False or load.get("pilot_binding_changed") is not False:
        raise ReasoningError("local model load reported an authority or Pilot-binding change")
    return LocalLlamaCppReasoningProvider(runtime, model_id=model_id)


def build_reasoner_from_env(*, layout: Any = None):
    provider = os.getenv("GROX_REASONER_PROVIDER", "").strip().lower()
    if not provider or provider in {"none", "off", "disabled"}:
        return None
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("GROX_REASONER_MODEL", "")
        endpoint = os.getenv("GROX_REASONER_ENDPOINT", "https://api.openai.com/v1/responses")
        if not key or not model:
            raise ReasoningError("GROX_REASONER_PROVIDER=openai requires OPENAI_API_KEY and GROX_REASONER_MODEL")
        return OpenAIResponsesProvider(api_key=key, model=model, endpoint=endpoint)
    if provider == "local-llama-cpp":
        return _build_local_llama_reasoner(layout)
    raise ReasoningError(f"unsupported GROX_REASONER_PROVIDER: {provider}")
