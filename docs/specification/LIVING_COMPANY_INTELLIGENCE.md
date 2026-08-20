# GroX Living Company Intelligence

**Qualification status:** **A3 QUALIFIED** in GroX `v0.8.0`. Memory, craft, experience, and Crew cognition remain advisory to GorXu and can never grant eligibility, authority, Repair permission, command rank, or verifier independence. Later protected-main evolution may strengthen these surfaces without creating a new Apex stage.

A3 established the Standing Crew as an experienced organization without changing GroX command authority.

## Authority boundary

Living Company Intelligence is a native advisory service under Pilot GorXu.

**Commander → Pilot GorXu → Divisions → Standing Crew**

The intelligence service may rank eligible Crew and retrieve relevant memory and, for bounded Inspect tours, selective craft context. It may not:

- create a new command layer;
- place Crew, Crew cognition, a native model, or an external provider above/parallel to GorXu;
- insert a cognition/provider layer between GorXu and Crew as command authority;
- grant capabilities or mutation authority;
- lower Mission Control risk;
- bypass verifier independence;
- alter Commander intent;
- make memory, craft prose, provider output, model confidence, or filesystem placement authoritative merely because it was supplied to a Crew tour.

Crew competence and Mission authority remain hard eligibility gates. Experience affects ranking only after those gates pass.

Native or external cognition may supply bounded cognitive capability to an already-routed Crew tour, but the provider/model does not select its own Crew assignment, issue its own Mission Order, own Tool Gateway authority, or become an organizational superior. GorXu remains the sole operational orchestrator.

## Memory planes

A3 retains existing episodic Crew notes and adds durable records for:

- **semantic memory**: evidence-backed facts and relationships;
- **procedural memory**: versionable ways of working;
- **Vessel memory**: organizational knowledge shared across Crew.

Every durable memory record carries explicit non-empty provenance, confidence, scope, task class when known, timestamps, and an active/superseded state. Unattributed durable memory is rejected. Vessel-memory records may only use Vessel scope. Reusing a memory key supersedes the previous active record rather than silently rewriting history. Records may be explicitly forgotten by deactivation.

Memory is retrieved by relevance. A tour receives only a bounded slice selected for its Crew, objective, and task class. Unrelated memory is not injected and the complete historical memory store is never copied into a tour context.

Memory is infrastructure/context. Persistence location does not create command authority.

## Performance history

Each completed or failed Crew tour records an auditable performance observation keyed by Mission Order and task class. The record includes:

- outcome status;
- evidence-quality score;
- independent-verification result when available;
- observed latency;
- attributable cost units when a runtime can report them;
- Mission risk.

The present bounded filesystem/test runtime reports zero attributable model/tool cost units. The cost dimension is retained explicitly so later runtimes can supply non-zero observations without changing routing contracts.

## Experienced routing

GorXu's Living Company routing service first applies hard constraints:

1. Crew is Standing Crew, not a command/orchestrator identity;
2. required capabilities are present;
3. verifier requirements and independence exclusions are satisfied.

Eligible Crew are then ranked with an auditable score containing these dimensions:

- competence and task/tag relevance;
- task-class reliability history;
- evidence quality;
- current load;
- attributable cost;
- observed latency;
- risk-adjusted experience and verification history;
- small advisory preference from a validated cognitive/graph candidate list.

Historical performance may change the winner among otherwise eligible Crew. It can never make an ineligible Crew member eligible. Replanned graph nodes use the effective Mission/node risk floor when experience affects replacement ranking.

Routing remains GorXu-owned. A model/provider recommendation is candidate context to GorXu's governed routing path, not a command decision that can bypass deterministic eligibility.

## Context-isolated tours

Every Mission Order remains a fresh bounded tour. Living Company Intelligence continues to add:

- a stable task-class label;
- a capped relevant-memory context;
- routing/context-selection metadata.

For **Inspect** tours only, Living Company Intelligence may also add bounded selective specialist craft before the Order is sealed. Verify, Repair, and Execute retain their existing memory/routing context without carrying unused deep craft.

### Selective specialist craft

The post-Apex selective-craft path uses deterministic section selection after Crew routing and before an Inspect Mission Order is sealed.

Default limits are:

- at most **6** selected craft sections;
- at most **4,500** selected craft characters.

When present, `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` must fit **in full** before optional task-relevant craft is selected. If the complete mandatory set cannot fit within the configured budget, selection fails closed rather than truncating safety/operational binding. Remaining sections are selected by bounded lexical relevance with stable fallback fundamentals.

The selected context carries the full-card SHA-256 plus source revision and freshness-policy metadata. Inspect execution emits explicit `craft_selection` evidence so selection remains attributable even when no cognition provider is configured.

The complete craft card is never injected by default. Craft context is competence context only: a craft card cannot add a capability, widen scope, lower risk, authorize Repair, override a forbidden action, self-route Crew, or satisfy verifier independence.

Under NCI-1B separated operation, canonical Crew dossiers/craft may be read from the runtime/assets root while Commander work and private state occupy different filesystem roots. This storage topology does not alter the `Commander → Pilot GorXu → Divisions → Standing Crew` hierarchy.

## Bounded read-only Crew cognition

GroX exposes a provider-neutral Crew cognition seam for **Inspect** tours when a Crew cognition provider is separately supplied. The seam consumes:

- a sanitized copy of the sealed Mission Order envelope;
- the bounded selected specialist craft;
- the existing bounded relevant Crew memory;
- observations returned only by governed read/test actions already allowed by that Order.

The first bounded seam deliberately excludes Verify, Repair, and Execute. Those modes retain their existing deterministic execution paths and do not receive selective deep craft through this seam.

Within an Inspect tour, a cognitive Crew provider may request only:

- `fs_list`;
- `fs_read`;
- `test_run`.

Every request is still checked against the issued Mission Order, forbidden actions, Mission scope, Commander-work/Vessel-root confinement appropriate to the active layout, Crew capability, Tool Gateway policy, and host restrictions. The provider does not receive an alternate tool path. Requests for mutation or scope escape fail closed rather than falling back to broader execution.

Default resource limits are:

- at most **4** cognitive steps per tour;
- at most **1** cognitive `test_run` per tour;
- at most **8,000** characters of a bounded observation supplied back to cognition;
- at most **4,000** characters in the final cognitive work product.

Provider-facing Order, craft, memory, and observation structures are copied for each call. Provider-local mutation cannot alter executor-owned context, Mission authority, or prior observation history.

Governed cognitive observations are persisted as attributable evidence even if the provider later fails or degrades. Raw file-read content is not copied into persistent cognitive-observation evidence; bounded metadata and hashes are retained. A successful cognitive work product records provider identity, selected craft attribution, selected headings, selected size, relevant memory IDs, observation count, and cognitive test-run count.

Known recoverable provider/contract failures degrade to the existing deterministic Crew executor without widening authority. A policy or authority denial does not silently fall back. Unexpected programming defects remain defects rather than being normalized as ordinary provider failure.

Controlled fake-provider CI can qualify this provider-neutral seam and its boundaries. **That evidence does not by itself establish live model-backed Crew operation.** Any project/session, local, or external model provider requires separate operational qualification before GroX may claim the corresponding live model-backed Crew cognition capability.

The current protected source separately qualifies one exact live locally trained neural action-selection provider through this Inspect seam. That provider is a bounded cognitive resource inside an issued Crew tour; it is not a Crew commander, general-purpose LLM, or alternate Pilot.

## Qualified A3 gate

A3 qualification was established by demonstrating all of the following:

1. episodic, semantic, procedural, and Vessel memory survive StateStore reopen;
2. memory correction preserves provenance and supersession history;
3. unrelated memory is excluded and injected context remains bounded after the memory store grows;
4. Crew performance is persisted per task class with reliability, evidence, verification, latency, cost, and risk observations;
5. repeated equivalent Missions change routing toward the better-evidenced eligible Crew member;
6. capability, authority, risk-floor, and verifier-independence invariants remain unchanged;
7. both single-order Missions and Mission Graph nodes use the same experienced routing and selective-memory service;
8. the complete Vessel suite passes after an injected Crew failure and routing adaptation.

**Exit gate:** repeated Missions measurably improve routing and execution without indiscriminate context growth.

**Current A3 status:** QUALIFIED. Later selective-craft, controlled Crew-cognition hardening, live local neural Crew cognition, and NCI filesystem/install foundations are post-Apex extensions and do not redefine the historical A3 gate. Autonomous memory consolidation remains outside the released Apex baseline until separately evidenced and governed.
