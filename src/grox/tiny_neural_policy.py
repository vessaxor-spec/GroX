from __future__ import annotations

import hashlib
import json
import math
import random
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


@dataclass(slots=True)
class _TinyMLPHandle:
    model_id: str
    w1: list[list[float]]
    b1: list[float]
    w2: list[list[float]]
    b2: list[float]


class TinyMLPPythonBackend:
    """Dependency-free backend for the previously qualified tiny neural policy.

    The tiny artifact is a deterministic reconstruction recipe, not a claim that
    future GroX models must train at load time. This special backend replays the
    exact qualified seed/corpus procedure, verifies both the initial and trained
    weight digests, and then exposes inference through the generic runtime.
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
        if not isinstance(training, dict):
            raise ValueError("tiny model training/reconstruction evidence is malformed")
        expected = {
            "seed": 7601,
            "training_examples": 240,
            "held_out_examples": 100,
            "initial_held_out_accuracy": 0.44,
            "final_held_out_accuracy": 1.0,
            "initial_weights_sha256": "f5c197881e1fbdf90395bbc09d2c1ac7097691ac68101cf573c64a90b419b6b6",
            "trained_weights_sha256": "7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60",
        }
        if training != expected:
            raise ValueError("tiny model deterministic reconstruction recipe differs from qualified evidence")

        handle = self._initial_handle(seed=training["seed"])
        if self._digest(handle) != training["initial_weights_sha256"]:
            raise ValueError("tiny model initial-weight digest mismatch")

        rng = random.Random(training["seed"])
        examples = [self._training_example(rng) for _ in range(training["training_examples"])]
        held_out = [self._training_example(rng) for _ in range(training["held_out_examples"])]
        if round(self._accuracy(handle, held_out), 12) != training["initial_held_out_accuracy"]:
            raise ValueError("tiny model initial held-out accuracy does not reproduce")

        for _ in range(90):
            rng.shuffle(examples)
            for order, craft, memory, observations, target in examples:
                self._train_one(handle, self._features(order, craft, memory, observations), target)

        if self._digest(handle) != training["trained_weights_sha256"]:
            raise ValueError("tiny model trained-weight digest does not reproduce")
        if round(self._accuracy(handle, held_out), 12) != training["final_held_out_accuracy"]:
            raise ValueError("tiny model final held-out accuracy does not reproduce")
        return handle

    def invoke(self, handle: _TinyMLPHandle, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        order = payload.get("order")
        craft_context = payload.get("craft_context")
        memory_context = payload.get("memory_context")
        observations = payload.get("observations")
        if not isinstance(order, Mapping):
            raise ValueError("tiny Crew policy requires an order mapping")
        if not isinstance(craft_context, list) or not isinstance(memory_context, list) or not isinstance(observations, list):
            raise ValueError("tiny Crew policy context inputs must be lists")
        features = self._features(order, craft_context, memory_context, observations)
        _, probabilities = self._forward(handle, features)
        action_index = max(range(len(probabilities)), key=lambda index: probabilities[index])
        return {
            "action": TINY_ACTIONS[action_index],
            "probabilities": {action: round(probabilities[index], 6) for index, action in enumerate(TINY_ACTIONS)},
        }

    def unload(self, handle: _TinyMLPHandle) -> None:
        return None

    @staticmethod
    def _initial_handle(*, seed: int) -> _TinyMLPHandle:
        rng = random.Random(seed)
        return _TinyMLPHandle(
            model_id=TINY_MODEL_ID,
            w1=[[rng.uniform(-0.35, 0.35) for _ in range(5)] for _ in range(8)],
            b1=[0.0] * 8,
            w2=[[rng.uniform(-0.35, 0.35) for _ in range(8)] for _ in range(3)],
            b2=[0.0] * 3,
        )

    @staticmethod
    def _features(order: Mapping[str, Any], craft_context: list[Any], memory_context: list[Any], observations: list[Any]) -> list[float]:
        directive = str(order.get("directive") or order.get("objective") or "").lower()
        return [
            1.0 if observations else 0.0,
            min(len(observations), 4) / 4.0,
            1.0 if "test" in directive else 0.0,
            1.0 if craft_context else 0.0,
            1.0 if memory_context else 0.0,
        ]

    @staticmethod
    def _forward(handle: _TinyMLPHandle, features: list[float]) -> tuple[list[float], list[float]]:
        hidden = [
            math.tanh(sum(weight * value for weight, value in zip(row, features)) + bias)
            for row, bias in zip(handle.w1, handle.b1)
        ]
        logits = [
            sum(weight * value for weight, value in zip(row, hidden)) + bias
            for row, bias in zip(handle.w2, handle.b2)
        ]
        maximum = max(logits)
        exponentials = [math.exp(value - maximum) for value in logits]
        total = sum(exponentials)
        return hidden, [value / total for value in exponentials]

    @classmethod
    def _train_one(cls, handle: _TinyMLPHandle, features: list[float], target: int, *, learning_rate: float = 0.08) -> None:
        hidden, probabilities = cls._forward(handle, features)
        output_gradient = list(probabilities)
        output_gradient[target] -= 1.0
        hidden_gradient = [
            sum(handle.w2[action][index] * output_gradient[action] for action in range(3))
            * (1.0 - hidden[index] * hidden[index])
            for index in range(len(hidden))
        ]
        for action in range(3):
            for index in range(len(hidden)):
                handle.w2[action][index] -= learning_rate * output_gradient[action] * hidden[index]
            handle.b2[action] -= learning_rate * output_gradient[action]
        for index in range(len(hidden)):
            for feature_index in range(len(features)):
                handle.w1[index][feature_index] -= learning_rate * hidden_gradient[index] * features[feature_index]
            handle.b1[index] -= learning_rate * hidden_gradient[index]

    @classmethod
    def _training_example(cls, rng: random.Random):
        wants_test = rng.random() < 0.30
        observed = rng.random() < 0.50
        order = {"objective": "Inspect " + ("test evidence" if wants_test else "README evidence")}
        craft = [{"heading": "Safety Boundaries", "content": "read only"}] if rng.random() > 0.10 else []
        memory = [{"kind": "semantic", "content": "bounded evidence"}] if rng.random() > 0.10 else []
        observations = [{"action": "fs_read", "path": "README.md", "status": "ok"}] if observed else []
        target = 2 if observed else (1 if wants_test else 0)
        return order, craft, memory, observations, target

    @classmethod
    def _accuracy(cls, handle: _TinyMLPHandle, examples: list[Any]) -> float:
        correct = 0
        for order, craft, memory, observations, target in examples:
            _, probabilities = cls._forward(handle, cls._features(order, craft, memory, observations))
            action_index = max(range(len(probabilities)), key=lambda index: probabilities[index])
            correct += action_index == target
        return correct / len(examples)

    @staticmethod
    def _digest(handle: _TinyMLPHandle) -> str:
        payload = json.dumps(
            {"w1": handle.w1, "b1": handle.b1, "w2": handle.w2, "b2": handle.b2},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
