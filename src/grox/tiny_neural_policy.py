from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .crew_cognition import CrewCognitionError
from .native_model_runtime import HardwareRuntimeProfile, LocalModelRuntime, ModelManifest


TINY_MODEL_ID = "tiny-mlp-policy-5x8x3-v1"
TINY_BACKEND_NAME = "tiny-mlp-python-v1"
TINY_MODEL_FORMAT = "grox-json-tiny-mlp-v1"
TINY_PROVIDER_NAME = "local-neural-session-crew-v1"
TINY_ACTIONS = ("fs_read", "test_run", "finish")


@dataclass(frozen=True, slots=True)
class _TinyMLPHandle:
    model_id: str
    w1: tuple[tuple[float, ...], ...]
    b1: tuple[float, ...]
    w2: tuple[tuple[float, ...], ...]
    b2: tuple[float, ...]


class TinyMLPPythonBackend:
    """Dependency-free inference backend for the previously qualified tiny policy.

    Training remains provenance. Runtime loading consumes the exact qualified
    trained weights, so model identity does not depend on floating-point training
    reproduction across Python versions.
    """

    name = TINY_BACKEND_NAME

    def supports(self, manifest: ModelManifest, hardware: HardwareRuntimeProfile) -> tuple[bool, str]:
        if manifest.model_format != TINY_MODEL_FORMAT:
            return False, f"unsupported tiny-model format: {manifest.model_format}"
        if manifest.parameter_count != 75:
            return False, f"unexpected tiny-model parameter count: {manifest.parameter_count}"
        if manifest.placements != ("crew",):
            return False, "qualified tiny model is restricted to Crew cognition placement"
        return True, "dependency-free Python tiny-MLP backend is available"

    def load(self, manifest: ModelManifest, artifact_path: Path) -> _TinyMLPHandle:
        raw = json.loads(artifact_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("schema") != "grox-local-model-artifact-v1":
            raise ValueError("tiny model artifact schema is invalid")
        if raw.get("model_id") != manifest.model_id:
            raise ValueError("tiny model artifact identity does not match registry manifest")
        if raw.get("model_kind") != manifest.model_kind:
            raise ValueError("tiny model artifact kind does not match registry manifest")
        if raw.get("actions") != list(TINY_ACTIONS):
            raise ValueError("tiny model action vocabulary differs from the qualified boundary")
        if raw.get("parameter_count") != 75:
            raise ValueError("tiny model artifact parameter count is not 75")

        training = raw.get("training")
        weights = raw.get("weights")
        if not isinstance(training, dict) or not isinstance(weights, dict):
            raise ValueError("tiny model artifact training/weights evidence is malformed")
        expected_digest = training.get("trained_weights_sha256")
        if expected_digest != manifest.provenance.get("trained_weights_sha256"):
            raise ValueError("tiny model trained-weight identity differs from registry provenance")
        weights_digest = hashlib.sha256(
            json.dumps(weights, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if weights_digest != expected_digest:
            raise ValueError("tiny model internal trained-weight digest mismatch")

        w1 = self._matrix(weights.get("w1"), rows=8, cols=5, label="w1")
        b1 = self._vector(weights.get("b1"), length=8, label="b1")
        w2 = self._matrix(weights.get("w2"), rows=3, cols=8, label="w2")
        b2 = self._vector(weights.get("b2"), length=3, label="b2")
        parameter_count = sum(len(row) for row in w1) + len(b1) + sum(len(row) for row in w2) + len(b2)
        if parameter_count != 75:
            raise ValueError(f"tiny model loaded parameter count is not 75: {parameter_count}")
        return _TinyMLPHandle(model_id=manifest.model_id, w1=w1, b1=b1, w2=w2, b2=b2)

    def invoke(self, handle: _TinyMLPHandle, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        order = payload.get("order")
        craft_context = payload.get("craft_context")
        memory_context = payload.get("memory_context")
        observations = payload.get("observations")
        if not isinstance(order, Mapping):
            raise ValueError("tiny Crew policy requires an order mapping")
        if not isinstance(craft_context, list) or not isinstance(memory_context, list) or not isinstance(observations, list):
            raise ValueError("tiny Crew policy context inputs must be lists")

        directive = str(order.get("directive") or order.get("objective") or "").lower()
        features = (
            1.0 if observations else 0.0,
            min(len(observations), 4) / 4.0,
            1.0 if "test" in directive else 0.0,
            1.0 if craft_context else 0.0,
            1.0 if memory_context else 0.0,
        )
        hidden = tuple(
            math.tanh(sum(weight * value for weight, value in zip(row, features)) + bias)
            for row, bias in zip(handle.w1, handle.b1)
        )
        logits = tuple(
            sum(weight * value for weight, value in zip(row, hidden)) + bias
            for row, bias in zip(handle.w2, handle.b2)
        )
        maximum = max(logits)
        exponentials = tuple(math.exp(value - maximum) for value in logits)
        total = sum(exponentials)
        probabilities = tuple(value / total for value in exponentials)
        action_index = max(range(len(probabilities)), key=lambda index: probabilities[index])
        return {
            "action": TINY_ACTIONS[action_index],
            "probabilities": {action: round(probabilities[index], 6) for index, action in enumerate(TINY_ACTIONS)},
        }

    def unload(self, handle: _TinyMLPHandle) -> None:
        return None

    @staticmethod
    def _vector(raw: Any, *, length: int, label: str) -> tuple[float, ...]:
        if not isinstance(raw, list) or len(raw) != length:
            raise ValueError(f"tiny model {label} shape is invalid")
        values = tuple(float(value) for value in raw)
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"tiny model {label} contains non-finite values")
        return values

    @classmethod
    def _matrix(cls, raw: Any, *, rows: int, cols: int, label: str) -> tuple[tuple[float, ...], ...]:
        if not isinstance(raw, list) or len(raw) != rows:
            raise ValueError(f"tiny model {label} shape is invalid")
        return tuple(cls._vector(row, length=cols, label=label) for row in raw)


class TinyMLPCrewCognitionProvider:
    """Expose one explicitly loaded tiny model through the existing Crew seam.

    Construction does not load or bind the model. `LocalModelRuntime.load(...)`
    and the existing Pilot-owned `bind_crew_cognition_provider(...)` remain
    separate explicit steps.
    """

    name = TINY_PROVIDER_NAME
    model = TINY_MODEL_ID

    def __init__(self, runtime: LocalModelRuntime):
        self.runtime = runtime
        self.inference_trace: list[dict[str, Any]] = []

    def usage_snapshot(self) -> None:
        return None

    def next_step(self, *, order: dict[str, Any], craft_context: list[dict[str, Any]], memory_context: list[dict[str, Any]], observations: list[dict[str, Any]]) -> Mapping[str, Any]:
        try:
            result = self.runtime.invoke(
                self.model,
                placement="crew",
                payload={
                    "order": order,
                    "craft_context": craft_context,
                    "memory_context": memory_context,
                    "observations": observations,
                },
            )
        except Exception as exc:
            raise CrewCognitionError(f"local tiny neural Crew inference unavailable: {exc}") from exc
        output = result["output"]
        action = output.get("action")
        self.inference_trace.append(
            {
                "model_id": result["model_id"],
                "backend": result["backend"],
                "artifact_sha256": result["artifact_sha256"],
                "observation_count": len(observations),
                "craft_present": bool(craft_context),
                "memory_present": bool(memory_context),
                "action": action,
                "probabilities": dict(output.get("probabilities") or {}),
                "authority_changed": result["authority_changed"],
            }
        )
        if action == "fs_read":
            return {"action": "fs_read", "path": "README.md"}
        if action == "test_run":
            return {"action": "test_run"}
        if action == "finish":
            return {
                "action": "finish",
                "work_product": "Locally trained neural Crew policy completed bounded Inspect after governed evidence observation.",
            }
        raise CrewCognitionError(f"local tiny neural Crew model returned unsupported action: {action}")
