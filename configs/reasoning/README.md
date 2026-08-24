# GorXu Cognitive Provider Configuration

GroX does not store provider credentials in the Vessel. Provider configuration supplies cognition; it never grants authority.

Current source adapters:

- `openai` through the Responses API;
- `local-llama-cpp` through the GroX-owned local model runtime and an explicitly supplied `llama.cpp` executable.

## Hosted OpenAI configuration

```text
GROX_REASONER_PROVIDER=openai
GROX_REASONER_MODEL=<model-id>
OPENAI_API_KEY=<secret supplied by host secret mechanism>
```

Optional endpoint override:

```text
GROX_REASONER_ENDPOINT=https://api.openai.com/v1/responses
```

## Local llama.cpp configuration

The local path requires a commissioned **separated installed Vessel layout** and explicit model activation. Registration, discovery, readiness, or reconstitution never auto-loads a model.

```text
GROX_REASONER_PROVIDER=local-llama-cpp
GROX_REASONER_MODEL=<registered model id>
GROX_LLAMA_CPP_EXECUTABLE=<path to qualified llama.cpp executable>
GROX_LOCAL_MODEL_LOAD=explicit
```

The model must already exist in the commissioned persistent model store and pass the GroX registry/readiness gates. NCI-2/NCI-3 qualification used the exact `qwen3-4b-q4-k-m-seed-v1` artifact and pinned `llama.cpp` b10218 path under the recorded Linux x86_64 CPU-first constraints. That evidence does not qualify arbitrary models, binaries, platforms, or self-activation.

If no provider is configured, `grox status` reports `Cognitive Pilot: deterministic-only`.

## Live awareness boundary

Passive cognition inventory performs no provider invocation or network I/O. For an already-bound remote cognition resource, current origin transport freshness may be refreshed only through the existing governed Tool Gateway under an already sealed exact Mission Order. Transport reachability does not establish credential validity, provider/service readiness, authorization, qualification/fit, provider switching, or routing authority.

Provider configuration, connection, model power, or historical success must never alter GroX authority policy. A model is reasoning capability, not permission.
