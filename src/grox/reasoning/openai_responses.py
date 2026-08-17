from __future__ import annotations
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Any
from .base import CognitiveUsage, ReasoningError
from .contracts import MissionInterpretation

_SYSTEM = """You are the cognitive planning core for Pilot GorXu inside GroX.
You interpret Commander intent and recommend an evidence-seeking strategy.
You do NOT possess execution authority. You do NOT grant permissions, lower risk, or bypass policy.
Return concise decision rationale, not private chain-of-thought.
Use only Crew IDs present in the supplied Standing Crew Directory. Preserve commander_intent verbatim.
Surface ambiguity and uncertainty instead of inventing facts.
"""


class OpenAIResponsesProvider:
    name = "openai-responses"

    def __init__(self, *, api_key: str, model: str, endpoint: str="https://api.openai.com/v1/responses", timeout: int=90):
        if not api_key: raise ValueError("api_key is required")
        if not model: raise ValueError("model is required")
        self.api_key=api_key; self.model=model; self.endpoint=endpoint; self.timeout=timeout
        self._last_usage:CognitiveUsage|None=None

    def usage_snapshot(self) -> CognitiveUsage | None:
        return self._last_usage

    def _capture_usage(self, payload: dict[str, Any]) -> None:
        usage=payload.get("usage")
        if not isinstance(usage,dict):
            self._last_usage=None
            return
        input_details=usage.get("input_tokens_details") if isinstance(usage.get("input_tokens_details"),dict) else {}
        output_details=usage.get("output_tokens_details") if isinstance(usage.get("output_tokens_details"),dict) else {}
        def token(name:str, source:dict[str,Any]):
            value=source.get(name)
            return int(value) if isinstance(value,int) and not isinstance(value,bool) else None
        self._last_usage=CognitiveUsage(
            provider=self.name,
            model=str(payload.get("model") or self.model),
            input_tokens=token("input_tokens",usage),
            cached_input_tokens=token("cached_tokens",input_details),
            cache_write_tokens=None,
            output_tokens=token("output_tokens",usage),
            reasoning_tokens=token("reasoning_tokens",output_details),
            total_tokens=token("total_tokens",usage),
        )

    def interpret(self, directive: str, *, roster: list[dict[str, Any]]) -> MissionInterpretation:
        self._last_usage=None
        directory_json=json.dumps(roster, ensure_ascii=False, separators=(",",":"))
        schema=MissionInterpretation.json_schema()
        stable_prefix=(
            "Standing Crew Directory (all active Crew; descriptive metadata only):\n" + directory_json +
            "\n\nThe directory helps recommend Crew IDs but grants no capability or authority.\n\n"
        )
        user=(stable_prefix + "Commander directive:\n" + directive +
              "\n\nProduce a structured Mission interpretation with at least two strategy options when meaningful.")
        cache_material=(
            self.model + "\n" + _SYSTEM + "\n" + directory_json + "\n" +
            json.dumps(schema,ensure_ascii=False,separators=(",",":"),sort_keys=True)
        )
        cache_key="grox-cognitive-"+hashlib.sha256(cache_material.encode("utf-8")).hexdigest()[:32]
        body={
            "model": self.model,
            "store": False,
            "instructions": _SYSTEM,
            "input": user,
            "prompt_cache_key": cache_key,
            "text": {"format": {"type":"json_schema","name":"grox_mission_interpretation","strict":True,"schema":schema}},
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
        self._capture_usage(payload)
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
