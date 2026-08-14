from __future__ import annotations
import os
from .base import ReasoningError
from .openai_responses import OpenAIResponsesProvider

def build_reasoner_from_env():
    provider=os.getenv("GROX_REASONER_PROVIDER","").strip().lower()
    if not provider or provider in {"none","off","disabled"}: return None
    if provider=="openai":
        key=os.getenv("OPENAI_API_KEY","")
        model=os.getenv("GROX_REASONER_MODEL","")
        endpoint=os.getenv("GROX_REASONER_ENDPOINT","https://api.openai.com/v1/responses")
        if not key or not model:
            raise ReasoningError("GROX_REASONER_PROVIDER=openai requires OPENAI_API_KEY and GROX_REASONER_MODEL")
        return OpenAIResponsesProvider(api_key=key,model=model,endpoint=endpoint)
    raise ReasoningError(f"unsupported GROX_REASONER_PROVIDER: {provider}")
