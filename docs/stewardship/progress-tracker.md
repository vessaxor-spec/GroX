# GroX Progress Tracker

**Status date:** 2026-08-14

## Local sandbox Vessel

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified in the current sandbox:

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

The live Vessel source has now been synchronized to `vessaxor-spec/GroX` on `main`. Private SQLite and `.groxstate` operational state remain outside public Git by design. The previous external sandbox implementation remains unrecovered and is not treated as current source truth.

## Known deliberate limits

- GorXu cognition is session-qualified through the project/host GPT-5.6 Sol reasoning bridge; deterministic control remains the safe fallback when cognition is unavailable.
- Tool Gateway exposes safe filesystem/list/test operations only; arbitrary shell, network, browser, and credential actuation remain disabled.
- Episodic Crew continuity is live; semantic, procedural, and Vessel-wide memory planes are not yet implemented.
- Crash-safe durable state exists, but automatic mid-step workflow replay/resume is not yet implemented.

## Apex Orchestrator readiness

**Current status: NOT YET APEX**

Evidence from live self-assessment Mission `MSN-354de0550dd5`: GorXu correctly delegated the inspection to `orchestration-evaluation-analyst` and required independent verification, but the current deterministic runtime could only inventory the implementation and execute tests. It could not itself reason over findings, decompose a mission graph, synthesize competing Crew judgments, or adaptively resolve exceptions.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`.

A1 has since passed session qualification; the current critical path is A2.

## Apex critical-path update - A1 Cognitive Pilot

**Status:** SESSION-QUALIFIED

Verified in the live sandbox Vessel:

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
- 28 automated tests pass.

**A1 status: SESSION-QUALIFIED.** The current ChatGPT GPT-5.6 Sol session acts as GorXu's cognitive provider. No API key, OAuth flow, or vendor CLI is required for this operating mode. If the hosting session is unavailable, GorXu degrades to the deterministic control plane rather than widening authority.

Current critical path: **A2 - Mission Graph Orchestration**.

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

The sandbox is now explicitly classified as a replaceable flight computer rather than the Vessel's permanent home. A2 Mission Graph Orchestration remains the Apex critical path.

## Durable source synchronization

**Status: COMPLETE**

- complete Git-tracked live Vessel source synchronized to GitHub;
- 82 standing Crew dossiers present in durable source;
- runtime, cognition boundary, persistence subsystem, tests, Apex plan, and Ship's Log synchronized;
- private operational SQLite and `.groxstate` snapshots excluded from public Git;
- post-sync documentation reconciliation preserved richer approved canonical doctrine rather than allowing bootstrap summaries to overwrite it;
- local automated suite remains **31 tests passing**.

A2 Mission Graph Orchestration remains the current Apex stage.
