# Cognitive Pilot Contract

**Qualification status:** **A1 SESSION-QUALIFIED** in GroX `v0.7.0`. Project-hosted cognition may occupy the Pilot reasoning seat; deterministic authority remains authoritative and safe fallback remains mandatory.

## Purpose

The Cognitive Pilot layer gives Pilot GorXu model-backed interpretation and strategy formation without transferring command authority to the model.

The reasoning model is an advisor inside GorXu, not GorXu's constitution and not Mission Control.

## Required structured output

For each Commander directive, the cognitive provider returns a validated Mission Interpretation containing:

- the Commander directive preserved verbatim;
- the operational objective;
- ambiguity state and explicit ambiguities;
- assumptions and information needs;
- candidate Standing Crew IDs;
- strategy options with concise decision rationale, advantages, and risks;
- one recommended option;
- confidence;
- proposed Mission mode and risk for advisory use.

Private chain-of-thought is neither requested nor stored. GroX records concise decision rationale and evidence-seeking strategy only.

## Authority boundary

Cognition may:

- interpret novel wording;
- detect ambiguity;
- identify information gaps;
- compare strategies;
- recommend Crew;
- recommend higher caution.

Cognition may not:

- grant repair or mutation authority;
- lower the deterministic risk floor;
- widen capabilities;
- bypass Mission Control;
- bypass independent verification;
- change Commander intent;
- create a parallel orchestrator.

Mission Control and the Tool Gateway remain deterministic enforcement layers and may deny cognitive proposals.

## Degraded mode

If the configured cognitive provider is unavailable or returns invalid structured output, GorXu records `cognition_degraded` evidence and falls back to the existing deterministic control plane. Degraded mode does not widen authority.

As GroX gains more powerful tools, policy may require cognitive availability for specific Mission classes rather than allowing degraded execution.

## Provider boundary

The runtime exposes a provider-neutral `ReasoningProvider` contract. Provider adapters are implementation details and may be replaced without changing the command architecture.

The first implemented adapter uses the OpenAI Responses API with structured JSON output and disables response storage at the request level. No provider key is stored in the Vessel repository.

## Qualified A1 boundary

A1 qualification was established with a real configured reasoning model, not a test double, demonstrating all of the following against novel Commander directives:

1. exact intent preservation;
2. useful ambiguity detection;
3. at least two meaningful strategy options where appropriate;
4. valid Crew recommendation without hard-coded keyword routing;
5. risk cannot be lowered below Mission Control policy;
6. mutation authority cannot be self-granted;
7. structured reasoning evidence is persisted and independently inspectable.

**Current status:** SESSION-QUALIFIED. Loss of the project/session cognitive provider degrades to deterministic control and never widens authority.
