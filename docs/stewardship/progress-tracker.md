# GroX Progress Tracker

**Status date:** 2026-08-14

## Verified Vessel baseline

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified by source, qualification evidence, and automated testing:

- GroX-native command architecture implemented
- Commander Seat CLI and interactive bridge live
- Pilot GorXu is the sole operational orchestrator
- Mission Control operates as a native advisory/policy subsystem under GorXu
- 81 specialist-inspired Standing Crew recruited as native GroX identities
- 1 native independent verifier retained, for 82 total standing dossiers
- former bootstrap `systems-architect` overlap replaced by the canonical `architect` Crew
- orchestration-role recruitment blocked; orchestration remains Pilot authority
- fresh Crew tours with persistent tour/episodic state
- SQLite Mission, Order, Evidence, and Crew state persistence
- bounded Tool Gateway with Vessel-root confinement
- Inspect vs Repair mutation separation enforced
- Mission Orders enforce competence/authority intersection
- independent verifier must differ from executor
- interrupted Crew duty state recovers safely on restart
- domain-routing contracts added for the expanded company
- 40 automated contract/unit/integration tests passing
- live Inspect Mission completed successfully
- live medium-risk Repair Mission completed with independent verification

## Company state

- Total standing dossiers: **82**
- Specialist-inspired Crew: **81**
- Native support Crew: **1 independent verifier**
- Verification-capable Crew: **16**
- Duplicate Crew IDs: **0**
- Recruited command/orchestrator roles: **0**

### Division attendance

- Strategy: 17
- Engineering: 14
- Intelligence: 13
- Assurance: 12
- Platform: 10
- Physical Systems: 7
- Operations: 5
- Verification: 3
- Systems: 1

## Evidence boundary

The complete Git-tracked live Vessel source is synchronized to `vessaxor-spec/GroX` on `main`. Private SQLite and `.groxstate` operational state remain outside public Git by design. Historical private state may contain retired Crew identities that are not part of the active source-defined company.

## Known deliberate limits

- GorXu cognition is project-hosted through GPT-5.6 Sol when a capable Space Exploration session is active; deterministic control remains the safe fallback when cognition is unavailable.
- Tool Gateway exposes safe filesystem/list/test operations only; arbitrary shell, network, browser, and credential actuation remain disabled.
- Episodic Crew continuity is live; semantic, procedural, and Vessel-wide memory planes are not yet implemented.
- Durable Mission Graph nodes/events and crash-safe state exist, but exact idempotent mid-step workflow replay/resume is not yet implemented.

## Apex Orchestrator readiness

**Current status: NOT YET APEX**

The initial self-assessment Mission `MSN-354de0550dd5` established the baseline gaps. Since then A1 Cognitive Pilot and A2 Mission Graph Orchestration have qualified. GorXu now has project-hosted cognition, durable dependency-aware multi-Crew graphs, parallel scheduling, bounded replanning for recoverable Crew/runtime failure, independent graph verification, and Pilot-owned structural synthesis.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`.

Current critical path: **A3 - Living Company Intelligence**. GorXu remains **NOT YET APEX** until later stages and the final gauntlet pass.

## Apex critical-path update - A1 Cognitive Pilot

**Status:** SESSION-QUALIFIED

Verified in the qualified Vessel:

- provider-neutral cognitive interface added;
- structured Mission interpretation contract added;
- Commander intent preservation is validated;
- ambiguity, option comparison, candidate Crew, confidence, and information needs are first-class fields;
- model recommendations cannot lower the Mission Control risk floor;
- model recommendations cannot self-grant Repair mode;
- Crew recommendations remain capability checked;
- cognitive plans are persisted as Mission evidence;
- provider failures degrade to deterministic control without authority widening;
- session-bound GPT-5.6 Sol reasoning provider added;
- live cognitive Mission `MSN-197e7287b267` completed;
- cognition selected `formal-methods-engineer` without relying on the deterministic keyword route;
- cognition raised risk to high while deterministic controls retained mutation authority;
- independent verification passed by `code-reviewer`;
- 28 automated tests passed at A1 qualification.

**A1 status: SESSION-QUALIFIED.** A capable ChatGPT GPT-5.6 Sol project session may act as GorXu's cognitive provider. No API key, OAuth flow, or vendor CLI is required for this operating mode. If the hosting session is unavailable, GorXu degrades to the deterministic control plane rather than widening authority.

A1 exit gate is closed; the current Apex stage is tracked below.

## Persistence foundation

**Status: LOCKED AND IMPLEMENTED**

- cognitive continuity home: ChatGPT project `Space Exploration`;
- Pilot identity: GorXu; preferred reasoning runtime: GPT-5.6 Sol / high reasoning;
- durable Vessel source home: `vessaxor-spec/GroX`;
- operational state remains private and outside public Git;
- `.groxstate` snapshot creation, SHA-256 verification, SQLite integrity checking, and confirmation-gated restore implemented;
- restore creates a pre-restore checkpoint;
- `configs/persistence/project-binding.json` records the active persistence bindings;
- automated suite: **31 tests passing** after persistence-plane implementation.

The sandbox is explicitly classified as a replaceable flight computer rather than the Vessel's permanent home. The persistence foundation is closed; the current Apex critical path is A3 Living Company Intelligence.

## Durable source synchronization

**Status: COMPLETE**

- complete Git-tracked Vessel runtime synchronized to GitHub;
- 82 Standing Crew dossiers present in durable source;
- cognition boundary, persistence system, Mission Graph runtime, tests, Apex plan, and Ship's Log are source-controlled;
- private SQLite and `.groxstate` files remain excluded from public Git;
- canonical architecture was reconciled after synchronization to avoid documentation regression.

## Apex critical-path update - A2 Mission Graph Orchestration

**Status: QUALIFIED**

Implemented and verified in the Vessel:

- durable `MissionGraphPlan` and node contracts;
- Commander-intent preservation and DAG validation;
- explicit node attempt/time budgets and Mission node/parallel/replan budgets;
- dependency-aware scheduling with true parallel-ready batches;
- Crew selection per graph node with capability enforcement;
- each node materializes as a bounded native Mission Order;
- graph node/event persistence in SQLite;
- explicit independent verification nodes;
- repair nodes denied unless GorXu receives explicit mutation authorization;
- bounded automatic replanning for recoverable Crew/runtime failures;
- downstream dependency rewiring after replacement;
- Pilot-owned persisted synthesis;
- Commander Seat `graph-mission` command with validated JSON plan input;
- session reasoning provider supports validated Mission Graph proposals;
- **40 automated tests passing**.

A2 qualification Mission: `MSN-f522e1ff611e`.

Qualification evidence:

- seven Crew identities participated;
- three root branches were scheduled as a parallel batch;
- `database-reliability-engineer` received an injected recoverable availability failure;
- GorXu replaced it with `distributed-systems-engineer` without Commander intervention;
- downstream `operations` dependency was rewired to the replacement node;
- `architect`, `formal-methods-engineer`, `application-security-engineer`, `site-reliability-engineer`, and the replacement Crew all completed bounded branches;
- `code-reviewer` independently verified five branch results and ran the full test suite;
- verification passed;
- final Pilot synthesis recorded `replans=1`, no unresolved nodes, and Mission status `completed`.

**A2 exit gate: PASSED.**

Current Apex stage: **A3 - Living Company Intelligence**.

## Fresh-session reconstitution and source-integrity recovery

**Status: QUALIFIED FOR A3 READINESS**

A fresh Space Exploration session reconstituted the Vessel against live GitHub source and the private A2 checkpoint before allowing A3 work.

Recovery evidence:

- live `main` matched the A2 handoff commit before recovery work;
- the private `GROX-A2-qualified.groxstate` checkpoint passed archive-path, schema, SHA-256, and SQLite integrity verification and was restored through GroX's controlled persistence path;
- active source-defined company remains 82 Standing Crew; a retired historical `systems-architect` row in private state does not re-enter the active company;
- two source-integrity defects were found before A3: corrupted bytes in the A2 Mission Graph regression test and one mis-indented runtime statement in bounded replanning;
- both defects were repaired on an isolated recovery branch without changing Mission Graph authority semantics;
- the lost `test_graph_repair_requires_explicit_mutation_authority` invariant was recovered from A2 qualification evidence;
- the repaired Vessel installed cleanly, compiled cleanly, and ran the complete suite on a fresh GitHub-hosted Ubuntu 24.04 / Python 3.12 checkout;
- **40/40 automated tests passed** after recovery, including injected Crew failure/replanning, downstream dependency rewiring, graph mutation-authority denial, persistence restore, cognition boundaries, Tool Gateway confinement, full-company integrity, and independent verification paths;
- the Roadmap was reconciled from stale A2 wording to the actual current stage, A3 Living Company Intelligence.

The recovery repairs restore the qualified A2 baseline; they do not implement A3.
