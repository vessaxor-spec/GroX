# GroX Roadmap

## Current position

GroX now has a runnable native Vessel, a full standing company, project/session-bound GorXu cognition, private operational-state recovery, and durable source synchronization to GitHub.

The command architecture is native to the Vessel:

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

## Completed foundation

- Native command hierarchy defined and implemented
- GorXu established as sole primary orchestrator
- Mission Control defined as a GroX-native subsystem under GorXu
- GroX Mission Order defined as the operational authority contract
- 81 specialist-inspired Standing Crew plus native independent verifier
- Inspect/Repair separation enforced
- Crew exception handling routed through GorXu
- Commander escalation threshold narrowed to critical, irreversible, or material intent-changing decisions
- Verification and evidence path implemented
- Bounded filesystem/test Tool Gateway implemented
- SQLite Mission/Order/Evidence/Crew persistence implemented
- Three-plane persistence architecture implemented
- A1 Cognitive Pilot session-qualified with GPT-5.6 Sol

## Apex critical path

The Apex run is the Vessel's primary trajectory. Detailed gates are maintained in `APEX_ORCHESTRATOR_PLAN.md`.

### Current stage: A2 — Mission Graph Orchestration

A2 must add:

- durable task decomposition into bounded Mission Orders;
- dependency graph and parallelizable branches;
- Crew selection per node;
- explicit budgets and stop conditions;
- dynamic re-planning from intermediate evidence;
- Pilot-owned synthesis;
- injected-failure recovery without unnecessary Commander intervention.

A2 is complete only when GorXu coordinates at least five different Crew across a multi-stage Mission and adapts after an injected failure while preserving all authority invariants.

## Later Apex stages

- A3 Living Company Intelligence
- A4 Executive Exception Loop and Durable Operations
- A5 Governed Capability Expansion
- A6 Orchestration Intelligence and Self-Improvement
- A7 Apex Qualification Gauntlet

## Persistence foundation

The three-plane persistence architecture is foundational infrastructure for every Apex stage:

- Project-bound GorXu cognitive continuity;
- GitHub-bound Vessel source;
- private, integrity-checked operational-state snapshots;
- replaceable sandbox/host compute;
- gated reconstitution before Mission resume.

## Recovery rule

A future host may resume GroX only after source materialization, private-state verification/restoration when needed, test/integrity gates, and Pilot reconstitution. Failure at a recovery gate leaves the Vessel paused rather than reconstructed from memory.
