# GorXu Cognitive Provider Configuration

GroX does not store provider credentials in the Vessel.

Current adapter:

- `openai` through the Responses API

Environment variables:

```text
GROX_REASONER_PROVIDER=openai
GROX_REASONER_MODEL=<model-id>
OPENAI_API_KEY=<secret supplied by host secret mechanism>
```

Optional endpoint override:

```text
GROX_REASONER_ENDPOINT=https://api.openai.com/v1/responses
```

If no provider is configured, `grox status` reports `Cognitive Pilot: deterministic-only`.

Provider configuration must never alter GroX authority policy. A model is reasoning capability, not permission.
