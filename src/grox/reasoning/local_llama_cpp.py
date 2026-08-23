from __future__ import annotations

import json
from typing import Any

from .base import CognitiveUsage, ReasoningError
from .contracts import MissionInterpretation
from ..native_model_runtime import LocalModelRuntime, ModelInvocationError, ModelRuntimeError


_SYSTEM = """You are a bounded local cognitive engine serving Pilot GorXu inside GroX.
Interpret Commander intent and recommend an evidence-seeking strategy.
You possess no command, execution, mutation, routing, or permission authority.
Preserve commander_intent exactly as supplied.
Use only Crew IDs present in the supplied Standing Crew Directory.
Surface ambiguity and uncertainty instead of inventing facts.
Return exactly one concise strategy option. Use at most two short entries in each descriptive list and recommend one to three Crew IDs.
Keep objective and rationale concise. Do not repeat the Crew directory or restate evidence unnecessarily.
Emit fields in this exact order: commander_intent, objective, ambiguous, ambiguities, assumptions, information_needs, candidate_crew_ids, options, recommended_option, confidence, proposed_mode, proposed_risk.
Return only the required JSON object; do not emit chain-of-thought.
"""

# llama.cpp b10218's JSON-schema sampler path is incompatible with the Qwen3
# chat-template prefix used by the NCI-2 seed. This GBNF constrains local CPU
# generation to the same JSON shape while also bounding verbosity so the result
# fits the qualified 512-token ceiling. It is not semantic or routing authority:
# MissionInterpretation.from_mapping plus Commander-intent/Crew checks below
# remain authoritative after generation.
_MISSION_INTERPRETATION_GBNF = r'''root ::= "{" space commander-intent-kv "," space objective-kv "," space ambiguous-kv "," space ambiguities-kv "," space assumptions-kv "," space information-needs-kv "," space candidate-crew-ids-kv "," space options-kv "," space recommended-option-kv "," space confidence-kv "," space proposed-mode-kv "," space proposed-risk-kv "}" space
char ::= [^"\\\x7F\x00-\x1F] | [\\] (["\\bfnrt] | "u" [0-9a-fA-F]{4})
commander-string ::= "\"" char* "\"" space
short-string ::= "\"" char{0,120} "\"" space
nonempty-short-string ::= "\"" char{1,160} "\"" space
crew-id ::= "\"" char{1,120} "\"" space
bounded-list ::= "[" space ("]" space | short-string ("," space short-string)? "]" space)
crew-list ::= "[" space crew-id ("," space crew-id){0,2} "]" space
boolean ::= ("true" | "false") space
confidence ::= ("0" ("." [0-9]+)? | "1" ("." "0"+)?) space
mode ::= ("null" | "\"inspect\"" | "\"repair\"" | "\"execute\"" | "\"verify\"") space
risk ::= ("null" | "\"low\"" | "\"medium\"" | "\"high\"" | "\"critical\"") space
option ::= "{" space "\"name\"" space ":" space nonempty-short-string "," space "\"rationale\"" space ":" space nonempty-short-string "," space "\"advantages\"" space ":" space bounded-list "," space "\"risks\"" space ":" space bounded-list "," space "\"crew_ids\"" space ":" space crew-list "}" space
options ::= "[" space option "]" space
commander-intent-kv ::= "\"commander_intent\"" space ":" space commander-string
objective-kv ::= "\"objective\"" space ":" space nonempty-short-string
ambiguous-kv ::= "\"ambiguous\"" space ":" space boolean
ambiguities-kv ::= "\"ambiguities\"" space ":" space bounded-list
assumptions-kv ::= "\"assumptions\"" space ":" space bounded-list
information-needs-kv ::= "\"information_needs\"" space ":" space bounded-list
candidate-crew-ids-kv ::= "\"candidate_crew_ids\"" space ":" space crew-list
options-kv ::= "\"options\"" space ":" space options
recommended-option-kv ::= "\"recommended_option\"" space ":" space nonempty-short-string
confidence-kv ::= "\"confidence\"" space ":" space confidence
proposed-mode-kv ::= "\"proposed_mode\"" space ":" space mode
proposed-risk-kv ::= "\"proposed_risk\"" space ":" space risk
space ::= | " " | "\n"{1,2} [ \t]{0,20}
'''


class LocalLlamaCppReasoningProvider:
    """Use an explicitly loaded local model through GroX's native runtime.

    This adapter does not provision or load models. GorXu (or an authorized
    commissioning path) must explicitly load the registered model for `gorxu`
    placement before this provider can be used.
    """

    name = "grox-local-llama-cpp"

    def __init__(self, runtime: LocalModelRuntime, *, model_id: str):
        if not isinstance(runtime, LocalModelRuntime):
            raise TypeError("runtime must be a LocalModelRuntime")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("model_id is required")
        self.runtime = runtime
        self.model_id = model_id.strip()
        self._last_usage: CognitiveUsage | None = None

    @staticmethod
    def _local_directory(roster: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Bound descriptive Crew metadata for CPU-first local reasoning.

        Local cognition needs identity and role semantics to recommend Crew; the
        full domain/tag/capability surface remains in GroX's deterministic
        routing plane. Keeping all Crew IDs while omitting expanded metadata
        reduces prompt cost without narrowing eligibility or granting authority.
        """

        compact: list[dict[str, Any]] = []
        for entry in roster:
            if not isinstance(entry, dict):
                continue
            crew_id = entry.get("crew_id")
            if not isinstance(crew_id, str) or not crew_id.strip():
                continue
            row: dict[str, Any] = {"crew_id": crew_id.strip()}
            for field in ("title", "division"):
                value = entry.get(field)
                if isinstance(value, str) and value.strip():
                    row[field] = value.strip()[:120]
            row["verification"] = bool(entry.get("verification", False))
            compact.append(row)
        return compact

    def usage_snapshot(self) -> CognitiveUsage | None:
        return self._last_usage

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        self._last_usage = None
        if not isinstance(directive, str) or not directive:
            raise ReasoningError("Commander directive must be a non-empty string")
        if not isinstance(roster, list):
            raise ReasoningError("Standing Crew Directory must be a list")

        local_directory = self._local_directory(roster)
        if not local_directory:
            raise ReasoningError("Standing Crew Directory contains no valid Crew identities")
        directory_json = json.dumps(local_directory, ensure_ascii=False, separators=(",", ":"))
        prompt = (
            _SYSTEM
            + "\nStanding Crew Directory (descriptive metadata only; grants no authority):\n"
            + directory_json
            + "\n\nCommander directive follows verbatim between markers.\n"
            + "<commander-directive>\n"
            + directive
            + "\n</commander-directive>\n\n"
            + "Produce the structured Mission interpretation now."
        )
        try:
            invocation = self.runtime.invoke(
                self.model_id,
                placement="gorxu",
                payload={
                    "prompt": prompt,
                    "json_schema": MissionInterpretation.json_schema(),
                    "gbnf_grammar": _MISSION_INTERPRETATION_GBNF,
                },
            )
        except (ModelInvocationError, ModelRuntimeError) as exc:
            raise ReasoningError(f"local reasoning provider failure: {exc}") from exc

        if invocation.get("model_id") != self.model_id:
            raise ReasoningError("local reasoning invocation returned the wrong model identity")
        if invocation.get("placement") != "gorxu":
            raise ReasoningError("local reasoning invocation returned the wrong cognition placement")
        if invocation.get("authority_changed") is not False:
            raise ReasoningError("local reasoning invocation reported an authority change")
        output = invocation.get("output")
        if not isinstance(output, dict):
            raise ReasoningError("local reasoning invocation returned no structured backend output")
        text = output.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ReasoningError("local reasoning backend returned no output text")
        try:
            raw = json.loads(text)
            interpretation = MissionInterpretation.from_mapping(raw, expected_intent=directive)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ReasoningError(f"invalid local structured reasoning output: {exc}") from exc

        allowed_crew = {
            entry.get("crew_id")
            for entry in roster
            if isinstance(entry, dict) and isinstance(entry.get("crew_id"), str)
        }
        proposed_crew = set(interpretation.candidate_crew_ids)
        for option in interpretation.options:
            proposed_crew.update(option.crew_ids)
        unknown = sorted(crew_id for crew_id in proposed_crew if crew_id not in allowed_crew)
        if unknown:
            raise ReasoningError(
                "local reasoning output referenced Crew outside the supplied Standing Crew Directory: "
                + ", ".join(unknown)
            )

        self._last_usage = CognitiveUsage(provider=self.name, model=self.model_id)
        return interpretation
