# GroX Roadmap

## Current position

GroX now has a runnable native Vessel, a full standing company, project/session-bound GorXu cognition, private operational-state recovery, durable source synchronization to GitHub, and qualified A1/A2/A3 Apex stages.

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
- A2 Mission Graph Orchestration qualified with durable graph state, parallel-ready scheduling, bounded replanning, independent verification, and Pilot-owned synthesis
- A3 Living Company Intelligence qualified with attributable memory, per-task performance history, experienced routing, and bounded selective memory injection

## Apex critical path

The Apex run is the Vessel's primary trajectory. Detailed gates are maintained in `APEX_ORCHESTRATOR_PLAN.md`.

### Current stage: A4 — Executive Exception Loop and Durable Operations

A4 must make GorXu a durable second-in-command during long-running Missions rather than only within a continuously running process.

Required outcomes:

- consult -> investigate -> compare -> decide -> continue handling for ordinary blockers;
- automatic consultation of relevant Crew for non-critical exceptions;
- escalation only for critical, irreversible, or material intent-changing decisions;
- checkpointed and idempotent Mission steps;
- safe crash recovery and exact resume from committed state;
- bounded timeout, retry, cancellation, compensation, and rollback semantics.

A4 is complete only when a long-running Mission survives process interruption plus multiple injected exceptions, resumes safely, and reaches independently verified closure without unnecessary Commander escalation.

## Qualified Apex stages

- **A1 Cognitive Pilot:** SESSION-QUALIFIED
- **A2 Mission Graph Orchestration:** QUALIFIED
- **A3 Living Company Intelligence:** QUALIFIED

A3 qualification is backed by a 46-test suite, repeated-Mission routing adaptation, bounded memory-context tests, and live private-Vessel Mission `MSN-6627085e3cea` with independent verification PASS.

## Later Apex stages

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
