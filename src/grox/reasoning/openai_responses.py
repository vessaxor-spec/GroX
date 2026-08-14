from __future__ import annotations
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Any
from .base import ReasoningError
from .contracts import MissionInterpretation

_SYSTEM = """You are the cognitive planning core for Pilot GorXu inside GroX.
You interpret Commander intent and recommend an evidence-seeking strategy.
You do NOT possess execution authority. You do NOT grant permissions, lower risk, or bypass policy.
Return concise decision rationale, not private chain-of-thought.
Use only Crew IDs present in the supplied roster. Preserve commander_intent verbatim.
Surface ambiguity and uncertainty instead of inventing facts.
"""

class OpenAIResponsesProvider:
    name = "openai-responses"

    def __init__(self, *, api_key: str, model: str, endpoint: str="https://api.openai.com/v1/responses", timeout: int=90):
        if not api_key: raise ValueError("api_key is required")
        if not model: raise ValueError("model is required")
        self.api_key=api_key; self.model=model; self.endpoint=endpoint; self.timeout=timeout

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        roster_json=json.dumps(roster, ensure_ascii=False, separators=(",",":"))
        user=("Commander directive:\n" + directive + "\n\nAvailable standing Crew:\n" + roster_json +
              "\n\nProduce a structured Mission interpretation with at least two strategy options when meaningful.")
        body={
            "model": self.model,
            "store": False,
            "instructions": _SYSTEM,
            "input": user,
            "text": {"format": {"type":"json_schema","name":"grox_mission_interpretation","strict":True,"schema":MissionInterpretation.json_schema()}},
        }
        req=Request(self.endpoint,data=json.dumps(body).encode("utf-8"),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        try:
            with urlopen(req,timeout=self.timeout) as r:
                payload=json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            detail=e.read().decode("utf-8",errors="replace")[:1000]
            raise ReasoningError(f"reasoning provider HTTP {e.code}: {detail}") from e
        except (URLError,TimeoutError,OSError,json.JSONDecodeError) as e:
            raise ReasoningError(f"reasoning provider failure: {e}") from e
        text=self._output_text(payload)
        try:
            raw=json.loads(text)
            return MissionInterpretation.from_mapping(raw,expected_intent=directive)
        except (json.JSONDecodeError,ValueError) as e:
            raise ReasoningError(f"invalid structured reasoning output: {e}") from e

    @staticmethod
    def _output_text(payload: dict[str, Any]) -> str:
        # REST Responses API returns output items; SDKs expose a convenience output_text.
        if isinstance(payload.get("output_text"),str):
            return payload["output_text"]
        pieces=[]
        for item in payload.get("output",[]):
            if item.get("type")!="message": continue
            for c in item.get("content",[]):
                if c.get("type") in {"output_text","text"} and isinstance(c.get("text"),str): pieces.append(c["text"])
        if not pieces: raise ReasoningError("reasoning provider returned no output text")
        return "".join(pieces)
