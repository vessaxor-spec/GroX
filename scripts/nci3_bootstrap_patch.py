from __future__ import annotations

from pathlib import Path


def replace_exact(path: Path, old: str, new: str, expected: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} occurrences, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    contracts = Path("src/grox/reasoning/contracts.py")
    marker = "@dataclass(slots=True)\nclass MissionInterpretation:"
    assistant_contract = '''@dataclass(slots=True)
class AssistantResponse:
    """One bounded direct Commander-facing response from GorXu cognition.

    This is conversational content only. It carries no Mission, tool, routing,
    mutation, or permission authority.
    """

    commander_input: str
    response: str

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], *, expected_input: str) -> "AssistantResponse":
        if not isinstance(raw, dict):
            raise ValueError("assistant response must be an object")
        expected_fields = {"commander_input", "response"}
        if set(raw) != expected_fields:
            raise ValueError("assistant response must contain only commander_input and response")
        commander_input = raw.get("commander_input")
        if commander_input != expected_input:
            raise ValueError("assistant response must preserve Commander input verbatim")
        response = raw.get("response")
        if not isinstance(response, str) or not response.strip():
            raise ValueError("assistant response text is required")
        response = response.strip()
        if len(response) > 1200:
            raise ValueError("assistant response exceeds the bounded 1200-character ceiling")
        return cls(commander_input=commander_input, response=response)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def json_schema() -> dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "commander_input": {
                    "type": "string",
                    "description": "Repeat the Commander input exactly, byte for byte.",
                },
                "response": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 1200,
                    "description": "Concise direct answer for the Commander; no private chain-of-thought.",
                },
            },
            "required": ["commander_input", "response"],
        }


@dataclass(slots=True)
class MissionInterpretation:'''
    replace_exact(contracts, marker, assistant_contract)

    base = Path("src/grox/reasoning/base.py")
    replace_exact(base, "from .contracts import MissionInterpretation", "from .contracts import AssistantResponse, MissionInterpretation")
    replace_exact(
        base,
        "class ReasoningProvider(Protocol):\n    name: str\n    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation: ...\n    def usage_snapshot(self) -> CognitiveUsage | None: ...\n",
        '''class ReasoningProvider(Protocol):
    name: str
    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation: ...
    def usage_snapshot(self) -> CognitiveUsage | None: ...


class ConversationalReasoningProvider(Protocol):
    """Optional provider-neutral direct-assistance capability.

    Implementing this protocol does not grant Mission or command authority.
    Existing interpretation-only providers remain valid for Mission cognition.
    """

    name: str
    def respond(self, message: str) -> AssistantResponse: ...
    def usage_snapshot(self) -> CognitiveUsage | None: ...
''',
    )

    init = Path("src/grox/reasoning/__init__.py")
    replace_exact(init, "from .base import CognitiveUsage, ReasoningProvider, ReasoningError", "from .base import CognitiveUsage, ConversationalReasoningProvider, ReasoningProvider, ReasoningError")
    replace_exact(init, "from .contracts import MissionInterpretation, StrategyOption", "from .contracts import AssistantResponse, MissionInterpretation, StrategyOption")
    replace_exact(init, '    "CognitiveUsage",\n', '    "CognitiveUsage",\n    "ConversationalReasoningProvider",\n    "AssistantResponse",\n')

    local = Path("src/grox/reasoning/local_llama_cpp.py")
    replace_exact(local, "from .contracts import MissionInterpretation", "from .contracts import AssistantResponse, MissionInterpretation")
    class_marker = "\n\nclass LocalLlamaCppReasoningProvider:"
    assistant_prompt = r'''

_ASSISTANT_SYSTEM = """You are bounded local cognition serving Pilot GorXu, the Commander's personal AI assistant inside GroX.
Answer the Commander's question directly, concisely, and usefully.
You possess no command, routing, execution, mutation, tool, permission, or model-activation authority.
Do not claim that you used tools, inspected files, accessed the network, or observed external state unless that information is supplied in the Commander input.
Preserve commander_input exactly as supplied.
Return at most three concise sentences in response.
Return only the required JSON object; do not emit private chain-of-thought.
"""

_ASSISTANT_RESPONSE_GBNF = r"""root ::= "{" space commander-input-kv "," space response-kv "}" space
char ::= [^"\\\x7F\x00-\x1F] | [\\] (["\\bfnrt] | "u" [0-9a-fA-F]{4})
commander-string ::= "\"" char* "\"" space
response-string ::= "\"" char{1,1200} "\"" space
commander-input-kv ::= "\"commander_input\"" space ":" space commander-string
response-kv ::= "\"response\"" space ":" space response-string
space ::= | " " | "\n"{1,2} [ \t]{0,20}
"""
'''
    replace_exact(local, class_marker, assistant_prompt + class_marker)
    method_marker = "    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:\n"
    respond_method = '''    def respond(self, message: str) -> AssistantResponse:
        self._last_usage = None
        if not isinstance(message, str) or not message.strip():
            raise ReasoningError("Commander input must be a non-empty string")
        if len(message) > 32768:
            raise ReasoningError("Commander input exceeds the bounded direct-assistance ceiling")
        prompt = (
            _ASSISTANT_SYSTEM
            + "\nCommander input follows verbatim between markers.\n"
            + "<commander-input>\n"
            + message
            + "\n</commander-input>\n\n"
            + "Produce the direct Commander-facing response now."
        )
        try:
            invocation = self.runtime.invoke(
                self.model_id,
                placement="gorxu",
                payload={
                    "prompt": prompt,
                    "json_schema": AssistantResponse.json_schema(),
                    "gbnf_grammar": _ASSISTANT_RESPONSE_GBNF,
                },
            )
        except (ModelInvocationError, ModelRuntimeError) as exc:
            raise ReasoningError(f"local direct-assistance provider failure: {exc}") from exc

        if invocation.get("model_id") != self.model_id:
            raise ReasoningError("local direct-assistance invocation returned the wrong model identity")
        if invocation.get("placement") != "gorxu":
            raise ReasoningError("local direct-assistance invocation returned the wrong cognition placement")
        if invocation.get("authority_changed") is not False:
            raise ReasoningError("local direct-assistance invocation reported an authority change")
        output = invocation.get("output")
        if not isinstance(output, dict):
            raise ReasoningError("local direct-assistance invocation returned no structured backend output")
        text = output.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ReasoningError("local direct-assistance backend returned no output text")
        try:
            raw = json.loads(text)
            response = AssistantResponse.from_mapping(raw, expected_input=message)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ReasoningError(f"invalid local direct-assistance output: {exc}") from exc

        self._last_usage = CognitiveUsage(provider=self.name, model=self.model_id)
        return response

'''
    replace_exact(local, method_marker, respond_method + method_marker)

    factory = Path("src/grox/reasoning/factory.py")
    factory.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

    pilot = Path("src/grox/pilot.py")
    replace_exact(pilot, "from .reasoning import ReasoningError, build_reasoner_from_env", "from .reasoning import AssistantResponse, ReasoningError, build_reasoner_from_env")
    replace_exact(pilot, "self.reasoner=build_reasoner_from_env() if reasoner is _AUTO else reasoner", "self.reasoner=build_reasoner_from_env(layout=layout) if reasoner is _AUTO else reasoner")
    ask_marker = "    def _reconcile_mode(self,directive:str,explicit:MissionMode|None,brief)->MissionMode:\n"
    ask_method = '''    def ask(self, message: str) -> dict[str, Any]:
        """Return one direct GorXu assistant response without creating a Mission.

        Direct cognition is advisory text only. It cannot route Crew, issue a
        Mission Order, mutate the Vessel, or widen authority.
        """
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Commander input must be a non-empty string")
        if len(message) > 32768:
            raise ValueError("Commander input exceeds the bounded direct-assistance ceiling")
        provider = self.cognitive_status
        if not self.reasoner:
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": "no cognitive provider is configured",
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        responder = getattr(self.reasoner, "respond", None)
        if not callable(responder):
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": "configured cognitive provider has no direct-assistance capability",
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        try:
            turn = responder(message)
            if not isinstance(turn, AssistantResponse):
                raise ReasoningError("direct-assistance provider returned the wrong contract type")
        except (ReasoningError, ValueError, TypeError) as exc:
            return {
                "status": "cognition_unavailable", "commander_input": message, "response": None,
                "provider": provider, "error": str(exc),
                "mission_created": False, "crew_delegated": False, "authority_changed": False,
            }
        return {
            "status": "answered", "commander_input": turn.commander_input, "response": turn.response,
            "provider": provider, "usage": self._reasoner_usage(),
            "mission_created": False, "crew_delegated": False, "authority_changed": False,
        }

'''
    replace_exact(pilot, ask_marker, ask_method + ask_marker)

    cli = Path("src/grox/cli.py")
    replace_exact(cli, "from .persistence import PersistenceManager", "from .persistence import PersistenceManager\nfrom .reasoning import ReasoningError")
    replace_exact(
        cli,
        "if line=='/help': print(\"/status /roster /missions /show <id> /exit | plain text = Mission directive\"); continue",
        "if line=='/help': print(\"/status /roster /missions /show <id> /ask <question> /exit | plain text = Mission directive\"); continue",
    )
    replace_exact(
        cli,
        "        if line.startswith('/show '): dump(p.store.mission(line.split(maxsplit=1)[1])); continue\n        dump(p.command(line))",
        "        if line.startswith('/show '): dump(p.store.mission(line.split(maxsplit=1)[1])); continue\n        if line.startswith('/ask '):\n            result=p.ask(line.split(maxsplit=1)[1])\n            if result.get('status')=='answered': print(f\"GorXu> {result['response']}\")\n            else: dump(result)\n            continue\n        dump(p.command(line))",
    )
    replace_exact(
        cli,
        "    sp.add_parser('status'); sp.add_parser('roster'); sp.add_parser('missions'); sp.add_parser('bridge')\n",
        "    sp.add_parser('status'); sp.add_parser('roster'); sp.add_parser('missions'); sp.add_parser('bridge')\n    ask=sp.add_parser('ask'); ask.add_argument('message')\n",
    )
    replace_exact(cli, "        if ns.cmd=='status': status(p); return\n", "        if ns.cmd=='status': status(p); return\n        if ns.cmd=='ask': dump(p.ask(ns.message)); return\n")
    replace_exact(cli, "    except InstallationError as exc:", "    except (InstallationError, ReasoningError) as exc:")

    Path("tests/unit/test_assistant_response.py").write_text('''from __future__ import annotations

import unittest

from grox.reasoning.contracts import AssistantResponse


class AssistantResponseTests(unittest.TestCase):
    def test_direct_response_preserves_commander_input_and_is_bounded(self) -> None:
        turn = AssistantResponse.from_mapping(
            {"commander_input": "Why verify restores?", "response": "A restore test proves the backup is usable."},
            expected_input="Why verify restores?",
        )
        self.assertEqual(turn.commander_input, "Why verify restores?")
        self.assertIn("restore", turn.response.lower())

    def test_direct_response_rejects_commander_input_drift(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping(
                {"commander_input": "changed", "response": "answer"}, expected_input="original"
            )

    def test_direct_response_rejects_authority_shaped_extra_fields(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping(
                {"commander_input": "x", "response": "answer", "allowed_actions": ["fs_write"]},
                expected_input="x",
            )

    def test_direct_response_rejects_empty_or_oversized_text(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping({"commander_input": "x", "response": "  "}, expected_input="x")
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping({"commander_input": "x", "response": "y" * 1201}, expected_input="x")


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    Path("tests/unit/test_local_llama_conversation.py").write_text('''from __future__ import annotations

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
        self.assertIn('response-string ::= "\\\"" char{1,1200}', _ASSISTANT_RESPONSE_GBNF)
        self.assertIn('commander-string ::= "\\\"" char*', _ASSISTANT_RESPONSE_GBNF)
        self.assertIn("at most three concise sentences", _ASSISTANT_SYSTEM)
        self.assertIn("no command", _ASSISTANT_SYSTEM.lower())


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    Path("tests/unit/test_local_reasoner_factory.py").write_text('''from __future__ import annotations

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
''', encoding="utf-8")

    Path("tests/integration/test_gorxu_direct_assistance.py").write_text('''from __future__ import annotations

import unittest

from grox.contracts import MissionMode
from grox.pilot import PilotGorXu
from grox.reasoning import AssistantResponse
from grox.reasoning.contracts import MissionInterpretation
from tests._support import temp_vessel


class ConversationalReasoner:
    name = "fake-conversational-core"

    def respond(self, message):
        return AssistantResponse.from_mapping(
            {"commander_input": message, "response": "Restore verification proves a backup can be recovered."},
            expected_input=message,
        )

    def interpret(self, directive, *, roster):
        candidate = "test-architecture-specialist"
        raw = {
            "commander_intent": directive,
            "objective": "Inspect architecture without mutation",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": [],
            "candidate_crew_ids": [candidate],
            "options": [{"name": "inspect", "rationale": "Use governed inspection", "advantages": [], "risks": [], "crew_ids": [candidate]}],
            "recommended_option": "inspect",
            "confidence": 0.8,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        }
        return MissionInterpretation.from_mapping(raw, expected_intent=directive)

    def usage_snapshot(self):
        return None


class InterpretationOnlyReasoner(ConversationalReasoner):
    respond = None


class BrokenConversationalReasoner(ConversationalReasoner):
    def respond(self, message):
        raise ValueError("bad direct output")


class GorXuDirectAssistanceTests(unittest.TestCase):
    def test_direct_assistance_answers_without_creating_mission_or_delegating_crew(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=ConversationalReasoner())
            before_missions = pilot.store.recent_missions(1000)
            before_states = pilot.store.crew_states()
            result = pilot.ask("Why verify restores?")
            self.assertEqual(result["status"], "answered")
            self.assertIn("restore", result["response"].lower())
            self.assertFalse(result["mission_created"])
            self.assertFalse(result["crew_delegated"])
            self.assertFalse(result["authority_changed"])
            self.assertEqual(pilot.store.recent_missions(1000), before_missions)
            self.assertEqual(pilot.store.crew_states(), before_states)
        finally:
            td.cleanup()

    def test_interpretation_only_provider_remains_usable_for_existing_missions(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=InterpretationOnlyReasoner())
            direct = pilot.ask("hello")
            self.assertEqual(direct["status"], "cognition_unavailable")
            mission = pilot.command("Inspect architecture", mode=MissionMode.inspect)
            self.assertEqual(mission["status"], "completed")
        finally:
            td.cleanup()

    def test_direct_assistance_failure_is_explicit_and_creates_no_mission(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=BrokenConversationalReasoner())
            result = pilot.ask("hello")
            self.assertEqual(result["status"], "cognition_unavailable")
            self.assertIsNone(result["response"])
            self.assertFalse(result["mission_created"])
            self.assertEqual(pilot.store.recent_missions(1000), [])
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    for temp in (
        Path(".github/workflows/nci3-implementation-bootstrap.yml"),
        Path(".github/workflows/nci3-bootstrap-v2.yml"),
        Path(".nci3-bootstrap-trigger"),
        Path("scripts/nci3_bootstrap_patch.py"),
    ):
        temp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
