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
Return only the JSON object required by the supplied schema; do not emit chain-of-thought.
"""


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

    def usage_snapshot(self) -> CognitiveUsage | None:
        return self._last_usage

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        self._last_usage = None
        if not isinstance(directive, str) or not directive:
            raise ReasoningError("Commander directive must be a non-empty string")
        if not isinstance(roster, list):
            raise ReasoningError("Standing Crew Directory must be a list")

        directory_json = json.dumps(roster, ensure_ascii=False, separators=(",", ":"))
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
