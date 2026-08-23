from __future__ import annotations

import json
import unittest

from grox.native_model_runtime import LocalModelRuntime
from grox.reasoning import ReasoningError
from grox.reasoning.local_llama_cpp import LocalLlamaCppReasoningProvider, _ASSISTANT_RESPONSE_GBNF, _ASSISTANT_SYSTEM


class FakeRuntime(LocalModelRuntime):
    def __init__(self, text: str):
        self.text = text
        self.payload = None

    def invoke(self, model_id, *, placement, payload):
        self.payload = dict(payload)
        return {"model_id": model_id, "placement": placement, "authority_changed": False, "output": {"text": self.text}}


class LocalLlamaConversationTests(unittest.TestCase):
    def test_direct_response_uses_bounded_gbnf_and_exact_input(self) -> None:
        message = "Why verify restores?"
        runtime = FakeRuntime(json.dumps({"commander_input": message, "response": "Restore verification proves a backup can actually be recovered."}))
        provider = LocalLlamaCppReasoningProvider(runtime, model_id="qwen-test")
        turn = provider.respond(message)
        self.assertEqual(turn.commander_input, message)
        self.assertIn("restore", turn.response.lower())
        self.assertEqual(runtime.payload["gbnf_grammar"], _ASSISTANT_RESPONSE_GBNF)
        self.assertEqual(runtime.payload["json_schema"]["required"], ["commander_input", "response"])
        self.assertIn(message, runtime.payload["prompt"])

    def test_direct_response_fails_closed_on_input_drift(self) -> None:
        runtime = FakeRuntime(json.dumps({"commander_input": "changed", "response": "answer"}))
        provider = LocalLlamaCppReasoningProvider(runtime, model_id="qwen-test")
        with self.assertRaises(ReasoningError):
            provider.respond("original")

    def test_direct_generation_contract_is_bounded(self) -> None:
        self.assertIn('response-string ::= "\"" char{1,1200}', _ASSISTANT_RESPONSE_GBNF)
        self.assertIn('commander-string ::= "\"" char*', _ASSISTANT_RESPONSE_GBNF)
        self.assertIn("at most three concise sentences", _ASSISTANT_SYSTEM)
        self.assertIn("no command", _ASSISTANT_SYSTEM.lower())


if __name__ == "__main__":
    unittest.main()
