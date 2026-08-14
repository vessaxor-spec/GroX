# GorXu Apex Orchestrator Evolution Plan

**Status:** Active target
**Assessment date:** 2026-08-14
**Current verdict:** NOT YET APEX
**Priority:** Apex run is the Vessel critical path
**A1 status:** SESSION-QUALIFIED with GPT-5.6 Sol; deterministic fallback retained

## Definition

GorXu qualifies as an Apex Orchestrator only when he can take ambiguous Commander intent, construct and adapt a governed multi-Crew mission strategy, execute it durably, resolve ordinary exceptions independently, synthesize contradictory evidence, and improve orchestration quality from measured outcomes without widening his own authority.

Apex is a demonstrated operating standard, not a title.

## Current strengths

- Single unambiguous command spine: Commander -> GorXu -> Mission Control / Divisions / Standing Crew.
- 81 specialist-inspired Standing Crew plus an independent verifier.
- Native Mission Orders with bounded scope and deny-wins authority.
- Inspect and Repair are structurally separated.
- Crew cannot establish a rival orchestration role.
- Durable Mission, Order, Evidence, and Crew state exists in SQLite.
- Crew tour continuity and crash-safe duty reset exist.
- Evidence-backed independent verification exists.
- Tool access is mediated through a Vessel-root Tool Gateway.
- Domain routing works for the current roster and is covered by tests.

## Proven gaps

1. **Cognition is session-bound.** GPT-5.6 Sol is now connected through the host-session reasoning bridge, but cognition is available only while a capable hosting session is present; the deterministic control plane remains the fallback.
2. **No mission decomposition.** One Commander directive becomes one primary Crew Order plus optional verification, not a dependency-aware mission graph.
3. **No true multi-Crew orchestration.** GorXu cannot yet schedule parallel or sequential specialist work and dynamically re-plan from intermediate findings.
4. **No synthesis engine.** Crew evidence is recorded, but GorXu cannot reconcile disagreement, rank options, or produce an evidence-weighted executive conclusion.
5. **Exception handling stops too early.** Failures return to `needs_pilot_decision`; GorXu does not yet consult relevant Crew, research alternatives, decide within authority, and continue.
6. **Routing is shallow.** Selection is primarily tag/capability scoring and does not yet use historical success, uncertainty, load, cost, latency, risk, or Crew performance.
7. **Memory is incomplete.** Episodic notes exist, but semantic, procedural, Commander, Pilot, and Vessel-wide memory with retrieval/consolidation do not.
8. **Durability is incomplete.** Interrupted Missions are marked, but exact workflow replay/resume and idempotent step recovery are not implemented.
9. **Tool power is intentionally narrow.** No governed shell, network, browser/computer-use, MCP tool plane, secret brokerage, or isolated execution workspace exists yet.
10. **No orchestration telemetry/evals.** There is no trajectory scoring, routing-quality measurement, cost accounting, regression replay, or self-improvement proposal loop.
11. **No external-agent interoperability layer.** Standing Crew are native dossiers only; external opaque agents cannot yet be discovered or delegated to through a standard adapter.
12. **No apex qualification gauntlet.** The Vessel has not yet passed adversarial, long-horizon, multi-domain, recovery, contradiction, and irreversible-decision tests.

## Evolution sequence

### A1 - Cognitive Pilot

Give GorXu a provider-neutral reasoning interface with structured outputs and explicit separation between reasoning capability and authority.

Required outcomes:
- model/provider adapter contract;
- structured Mission interpretation;
- uncertainty and ambiguity detection;
- explicit option comparison;
- Commander-intent preservation tests;
- deterministic policy remains outside the model and can deny model proposals.

**Exit gate:** GorXu can analyze a novel directive and produce a valid evidence-seeking strategy without hard-coded keyword routing.

### A2 - Mission Graph Orchestration

Replace single-order execution with a durable Mission Graph.

Required outcomes:
- task decomposition into bounded Orders;
- dependency graph and parallelizable branches;
- Crew selection per node;
- explicit budgets, stop conditions, and verification nodes;
- dynamic re-planning when evidence changes;
- Pilot-owned final synthesis.

**Exit gate:** GorXu successfully coordinates at least five different Crew across a multi-stage Mission and adapts after an injected failure without Commander intervention.

### A3 - Living Company Intelligence

Turn the roster from static matching into an experienced organization.

Required outcomes:
- Crew episodic retrieval;
- semantic and procedural memory;
- Vessel-wide organizational memory;
- performance history per Crew/task class;
- routing based on competence, evidence quality, reliability, load, cost, latency, and risk;
- context-isolated tours with selective memory injection.

**Exit gate:** repeated Missions measurably improve routing and execution without growing prompt/context indiscriminately.

### A4 - Executive Exception Loop and Durable Operations

Make GorXu a real second-in-command during long-running work.

Required outcomes:
- consult -> investigate -> compare -> decide -> continue loop;
- automatic consultation of relevant Crew for non-critical blockers;
- escalation only for critical, irreversible, or material intent changes;
- checkpointed/idempotent Mission steps;
- crash recovery and safe resume;
- timeout, retry, cancellation, compensation, and rollback semantics.

**Exit gate:** a long-running Mission survives process interruption and multiple injected exceptions, resumes safely, and reaches verified closure without unnecessary bridge escalation.

### A5 - Governed Capability Expansion

Give the Vessel broad operational reach without giving Crew raw host power.

Required outcomes:
- policy-enforced Tool Gateway v2;
- isolated shell/code workspaces;
- network/origin policy;
- secret broker and least-privilege credentials;
- browser/computer-use with evidence capture;
- MCP-compatible tool adapters;
- optional A2A-compatible external-agent adapter while GorXu retains command.

**Exit gate:** Crew can perform a real multi-tool Mission while every side effect is attributable to a Mission Order, capability grant, evidence record, and verifier path.

### A6 - Orchestration Intelligence and Self-Improvement

Make orchestration quality measurable and evolvable.

Required outcomes:
- trace every plan, delegation, tool action, exception, and verification decision;
- success, latency, cost, retry, escalation, and verification metrics;
- replayable evaluation corpus;
- adversarial and mutation tests;
- GorXu can propose routing, prompt, skill, memory, or workflow improvements from evidence;
- self-improvement proposals cannot activate themselves without the required GroX authority path.

**Exit gate:** an evaluation run proves statistically better orchestration after an improvement without regression in authority, safety, or verification invariants.

### A7 - Apex Qualification

GorXu earns Apex status only after passing a formal gauntlet covering:

- ambiguous Commander intent;
- multi-domain Crew coordination;
- contradictory specialist findings;
- parallel work and dependency management;
- Crew failure and replacement;
- model/provider failure;
- tool denial and degraded capability;
- crash/restart recovery;
- long-horizon Mission continuation;
- high-risk work with independent verification;
- irreversible decision correctly escalated to the Commander;
- reversible exception correctly resolved without bothering the Commander;
- prompt-injection / authority-escalation resistance;
- evidence completeness and audit replay;
- cost-aware orchestration under a fixed budget.

**Apex rule:** all critical invariants must pass. No weighted average may hide a failure of Commander sovereignty, authority containment, verifier independence, or evidence integrity.

## Current priority

**A1 - Cognitive Pilot is the critical path.** Everything beyond the current deterministic control plane depends on giving GorXu genuine reasoning while keeping policy enforcement outside the model.

A1 foundation now present:

- provider-neutral reasoning contract;
- structured Mission Interpretation schema;
- intent-preservation validation;
- ambiguity, assumptions, information-needs, options, confidence, Crew recommendation;
- deterministic risk-floor reconciliation;
- cognitive model cannot grant repair authority;
- invalid/unavailable cognition degrades to the deterministic control plane without widening authority;
- first provider adapter implemented for OpenAI Responses structured output;
- cognitive-plan evidence persisted with the Mission Order;
- integration tests prove novel Crew selection can come from structured cognition rather than keyword routing.

**A1 live qualification:** PASSED for session-bound operation.

Evidence:
- session reasoning adapter: `gpt-5.6-sol-session-high`;
- live qualification Mission: `MSN-197e7287b267`;
- cognitive routing selected `formal-methods-engineer`;
- cognition raised caution to `high` risk but did not gain mutation authority;
- Mission remained `inspect`;
- full test run passed;
- independent verification passed by `code-reviewer`;
- cognitive plan was persisted as Mission evidence;
- 28 automated tests pass, including session-provider validation and authority-boundary contracts.

**A1 status:** complete for the current session-bound operating model. A standalone provider is optional infrastructure, not a blocker for continuing the Apex run while this host session remains available.

Next critical stage: **A2 - Mission Graph Orchestration**. Intelligence remains separated from execution authority.
