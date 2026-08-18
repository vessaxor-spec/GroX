# GroX Living Company Intelligence

**Qualification status:** **A3 QUALIFIED** in GroX `v0.8.0`. Memory and experience remain advisory to GorXu and can never grant eligibility, authority, Repair permission, or verifier independence.

A3 established the Standing Crew as an experienced organization without changing GroX command authority.

## Authority boundary

Living Company Intelligence is a native advisory service under Pilot GorXu.

**Commander → Pilot GorXu → Divisions → Standing Crew**

The intelligence service may rank eligible Crew and retrieve relevant memory. It may not:

- create a new command layer;
- grant capabilities or mutation authority;
- lower Mission Control risk;
- bypass verifier independence;
- alter Commander intent;
- make memory authoritative merely because it was previously stored.

Crew competence and Mission authority remain hard eligibility gates. Experience affects ranking only after those gates pass.

## Memory planes

A3 retains existing episodic Crew notes and adds durable records for:

- **semantic memory**: evidence-backed facts and relationships;
- **procedural memory**: versionable ways of working;
- **Vessel memory**: organizational knowledge shared across Crew.

Every durable memory record carries explicit non-empty provenance, confidence, scope, task class when known, timestamps, and an active/superseded state. Unattributed durable memory is rejected. Vessel-memory records may only use Vessel scope. Reusing a memory key supersedes the previous active record rather than silently rewriting history. Records may be explicitly forgotten by deactivation.

Memory is retrieved by relevance. A tour receives only a bounded slice selected for its Crew, objective, and task class. Unrelated memory is not injected and the complete historical memory store is never copied into a tour context.

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

## Context-isolated tours

Every Mission Order remains a fresh bounded tour. Living Company Intelligence adds only:

- a stable task-class label;
- a capped relevant-memory context;
- routing-decision evidence.

The memory context is bounded by item count and character budget. This preserves continuity without accumulating prior working context indefinitely.

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

**Current status:** QUALIFIED. Autonomous memory consolidation remains outside the released Apex baseline until separately evidenced and governed.
