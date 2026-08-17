# Cognitive Pilot Contract

**Qualification status:** **A1 SESSION-QUALIFIED** in GroX `v0.7.1`. Project-hosted cognition may occupy the Pilot reasoning seat; deterministic authority remains authoritative and safe fallback remains mandatory.

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

## Standing Crew cognitive directory

GorXu's cognitive provider receives a compact discovery directory derived from the canonical active Crew dossiers. The directory keeps every Standing Crew identity cognitively visible while limiting repeated model context to descriptive fields:

- Crew ID;
- Division;
- title;
- descriptive domains;
- verification eligibility.

The directory deliberately omits capability grants and expanded routing tags. Capabilities, eligibility, experienced routing, Mission authority, risk floors, Repair permission, and verifier independence remain local deterministic GroX controls. A cognitive Crew recommendation is advisory; an invalid or ineligible recommendation cannot make a Crew member eligible and falls back through the qualified deterministic routing path.

Deep specialist craft cards are not part of this directory and are not injected merely because a Crew member is selected. `craft_card()` remains an explicit read-only craft lookup. Future model-backed Crew cognition, if separately authorized, should activate bounded Mission-relevant craft rather than require complete-card reinjection per tour.

## Cognitive usage evidence

Provider adapters may expose normalized observational usage for a cognitive invocation, including input, cached input, output, reasoning, total tokens, provider, and model when the provider supplies those fields. GorXu may persist that observation as `cognitive_usage` Mission evidence.

Usage telemetry is not an authority surface. Missing, malformed, or unavailable usage data must not block or widen execution, alter eligibility, lower risk, grant Repair permission, or affect verifier independence.

Provider-specific prompt caching is likewise an efficiency optimization only. Stable Standing Crew context may be framed before Mission-specific input and associated with a deterministic provider cache identity, but cache hit, miss, expiry, or provider removal cannot change GroX behavior or authority.

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
