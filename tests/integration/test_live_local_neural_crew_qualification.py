from __future__ import annotations

import hashlib
import json
import math
import random
import unittest

from grox.crew_provider import bind_crew_cognition_provider, qualify_bound_crew_cognition_provider
from grox.session_crew_cognition import SessionCrewCognitionProvider
from tests._support import temp_vessel


_ACTIONS = ("fs_read", "test_run", "finish")
_SEED = 7601


class _TinyNeuralCrewPolicy:
    """Small locally trained MLP used only as live provider qualification evidence.

    This is intentionally not a GroX runtime capability or an LLM claim. It is a
    learned 5 -> 8 -> 3 neural policy whose only purpose is to prove that actual
    local model training and inference can occupy the existing bounded Crew
    cognition seam without adding authority.
    """

    architecture = "tiny-mlp-policy-5x8x3-v1"

    def __init__(self, *, seed: int = _SEED, hidden: int = 8):
        rng = random.Random(seed)
        self.w1 = [[rng.uniform(-0.35, 0.35) for _ in range(5)] for _ in range(hidden)]
        self.b1 = [0.0] * hidden
        self.w2 = [[rng.uniform(-0.35, 0.35) for _ in range(hidden)] for _ in range(3)]
        self.b2 = [0.0] * 3

    @property
    def parameter_count(self) -> int:
        return sum(len(row) for row in self.w1) + len(self.b1) + sum(len(row) for row in self.w2) + len(self.b2)

    def features(self, order, craft_context, memory_context, observations):
        directive = str(order.get("directive") or order.get("objective") or "").lower()
        return [
            1.0 if observations else 0.0,
            min(len(observations), 4) / 4.0,
            1.0 if "test" in directive else 0.0,
            1.0 if craft_context else 0.0,
            1.0 if memory_context else 0.0,
        ]

    def _forward(self, features):
        hidden = [
            math.tanh(sum(weight * value for weight, value in zip(row, features)) + bias)
            for row, bias in zip(self.w1, self.b1)
        ]
        logits = [
            sum(weight * value for weight, value in zip(row, hidden)) + bias
            for row, bias in zip(self.w2, self.b2)
        ]
        maximum = max(logits)
        exp = [math.exp(value - maximum) for value in logits]
        total = sum(exp)
        probabilities = [value / total for value in exp]
        return hidden, probabilities

    def train_one(self, features, target, *, learning_rate: float = 0.08):
        hidden, probabilities = self._forward(features)
        output_gradient = list(probabilities)
        output_gradient[target] -= 1.0
        hidden_gradient = [
            sum(self.w2[action][index] * output_gradient[action] for action in range(3))
            * (1.0 - hidden[index] * hidden[index])
            for index in range(len(hidden))
        ]
        for action in range(3):
            for index in range(len(hidden)):
                self.w2[action][index] -= learning_rate * output_gradient[action] * hidden[index]
            self.b2[action] -= learning_rate * output_gradient[action]
        for index in range(len(hidden)):
            for feature_index in range(len(features)):
                self.w1[index][feature_index] -= learning_rate * hidden_gradient[index] * features[feature_index]
            self.b1[index] -= learning_rate * hidden_gradient[index]

    def predict(self, order, craft_context, memory_context, observations):
        features = self.features(order, craft_context, memory_context, observations)
        _, probabilities = self._forward(features)
        action_index = max(range(len(probabilities)), key=lambda index: probabilities[index])
        return _ACTIONS[action_index], probabilities

    def digest(self) -> str:
        payload = json.dumps(
            {"w1": self.w1, "b1": self.b1, "w2": self.w2, "b2": self.b2},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _training_example(rng: random.Random):
    wants_test = rng.random() < 0.30
    observed = rng.random() < 0.50
    order = {"objective": "Inspect " + ("test evidence" if wants_test else "README evidence")}
    craft = [{"heading": "Safety Boundaries", "content": "read only"}] if rng.random() > 0.10 else []
    memory = [{"kind": "semantic", "content": "bounded evidence"}] if rng.random() > 0.10 else []
    observations = [{"action": "fs_read", "path": "README.md", "status": "ok"}] if observed else []
    target = 2 if observed else (1 if wants_test else 0)
    return order, craft, memory, observations, target


def _train_local_policy():
    rng = random.Random(_SEED)
    training = [_training_example(rng) for _ in range(240)]
    held_out = [_training_example(rng) for _ in range(100)]
    model = _TinyNeuralCrewPolicy()
    for _ in range(90):
        rng.shuffle(training)
        for order, craft, memory, observations, target in training:
            model.train_one(model.features(order, craft, memory, observations), target)

    correct = 0
    for order, craft, memory, observations, target in held_out:
        action, _ = model.predict(order, craft, memory, observations)
        correct += _ACTIONS.index(action) == target
    return model, correct / len(held_out), len(training), len(held_out)


class _LocalNeuralSessionProvider(SessionCrewCognitionProvider):
    model = _TinyNeuralCrewPolicy.architecture

    def __init__(self, policy: _TinyNeuralCrewPolicy):
        self.policy = policy
        self.inference_trace = []
        super().__init__(self._respond, name="local-neural-session-crew-v1")

    def _respond(self, order, craft_context, memory_context, observations):
        action, probabilities = self.policy.predict(order, craft_context, memory_context, observations)
        self.inference_trace.append(
            {
                "observation_count": len(observations),
                "craft_present": bool(craft_context),
                "memory_present": bool(memory_context),
                "action": action,
                "probabilities": {
                    name: round(probabilities[index], 6) for index, name in enumerate(_ACTIONS)
                },
            }
        )
        if action == "fs_read":
            return {"action": "fs_read", "path": "README.md"}
        if action == "test_run":
            return {"action": "test_run"}
        return {
            "action": "finish",
            "work_product": (
                "Locally trained neural Crew policy completed bounded Inspect after governed evidence observation."
            ),
        }


class LiveLocalNeuralCrewQualificationTests(unittest.TestCase):
    def test_locally_trained_neural_provider_passes_canonical_bounded_gate(self):
        policy, held_out_accuracy, training_count, held_out_count = _train_local_policy()
        self.assertGreaterEqual(held_out_accuracy, 0.95)
        self.assertGreater(policy.parameter_count, 0)

        td, root, pilot = temp_vessel()
        try:
            pilot.intelligence.remember(
                kind="semantic",
                memory_key="live-local-neural-provider-qualification",
                content="README bounded provider qualification uses governed Inspect evidence.",
                scope="crew",
                crew_id="backend-engineer",
                task_class="general",
                provenance={"source": "live-local-neural-qualification"},
            )
            provider = _LocalNeuralSessionProvider(policy)
            self.assertEqual(bind_crew_cognition_provider(pilot, provider), provider.name)
            report = qualify_bound_crew_cognition_provider(
                pilot,
                directive="Inspect README evidence for bounded provider qualification",
                crew_id="backend-engineer",
            )

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(all(report["checks"].values()))
            self.assertFalse(report["live_provider_claim"])
            self.assertEqual(report["provider"], provider.name)
            self.assertEqual(report["provider_observability"].get("model"), provider.model)
            self.assertGreaterEqual(len(provider.inference_trace), 2)
            self.assertEqual(provider.inference_trace[0]["action"], "fs_read")
            self.assertEqual(provider.inference_trace[-1]["action"], "finish")
            self.assertTrue(provider.inference_trace[0]["craft_present"])
            self.assertTrue(provider.inference_trace[0]["memory_present"])

            host_evidence = {
                "schema": "grox-live-local-neural-crew-host-evidence-v1",
                "provider": provider.name,
                "model": provider.model,
                "model_kind": "locally-trained-neural-policy",
                "general_purpose_llm_claim": False,
                "training_runtime": "current-python-process",
                "network_required": False,
                "external_disclosure": False,
                "training_examples": training_count,
                "held_out_examples": held_out_count,
                "held_out_accuracy": round(held_out_accuracy, 6),
                "learned_parameters": policy.parameter_count,
                "model_sha256": policy.digest(),
                "inference_count": len(provider.inference_trace),
                "inference_trace": provider.inference_trace,
                "canonical_qualification": report,
                "host_establishes_live_model_execution": True,
                "claim_boundary": (
                    "This proves one locally trained neural action-selection model executed through the bounded "
                    "Inspect Crew cognition seam. It is not evidence of general-purpose LLM reasoning quality."
                ),
            }
            print("LIVE_LOCAL_NEURAL_CREW_QUALIFICATION_JSON=" + json.dumps(host_evidence, sort_keys=True))
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
