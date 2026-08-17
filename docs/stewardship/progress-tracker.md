# GroX Progress Tracker

**Status date:** 2026-08-17
**Canonical release:** `v0.7.1`
**Release candidate:** `v0.8.0` — PREPARATION AUTHORIZED; TAG/PUBLICATION PENDING
**Canonical source branch:** `main`
**Current source package:** `0.8.0`
**Current released source:** `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`
**First Apex-qualified release:** `v0.7.0@71ffd60769d81b5b249dac4eca56333ff27e26d0`
**Apex qualification merge:** `419cc73950f573c3e201106f7949c6bf7829f2af`
**Current operating verdict:** **APEX QUALIFIED — OPERATIONAL AUDIT 001 CLOSED**
**Standing Crew:** **82**
**Current verified regression:** pytest **202 passed, 2 skipped, 354 subtests**; unittest **204 OK, 2 skipped**

## Verified Vessel baseline

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified by source, qualification evidence, and automated testing:

- GroX-native command architecture implemented
- Commander Seat CLI and interactive bridge live
- Pilot GorXu is the sole operational orchestrator
- Mission Control operates as a native advisory/policy subsystem under GorXu
- 81 specialist-inspired Standing Crew recruited as native GroX identities
- 1 native independent verifier retained, for 82 total standing dossiers
- active Standing Crew membership is canonical, source-defined, and free of stale roster overlap
- non-standing or otherwise stale Crew operational state is purged during roster reconstitution
- orchestration-role recruitment blocked; orchestration remains Pilot authority
- fresh Crew tours with persistent tour/episodic state
- SQLite Mission, Order, Evidence, and Crew state persistence
- Tool Gateway v2 with deny-wins Mission Order, Crew capability, and host-policy enforcement
- governed isolated workspace execution, memory-only secret brokerage, exact-origin network access, offline browser evidence capture, and pre-registered stdio MCP adapters
- Inspect vs Repair mutation separation enforced
- Mission Orders enforce competence/authority intersection
- source-defined Crew are canonical over stale private operational state during reconstitution
- Crew-scoped stale operational state is purged when its identity is not present in current source-defined Standing Crew
- package/source version metadata is aligned to the `0.8.0` release candidate and remains guarded by both pytest and unittest
- current published release `v0.7.1` remains pinned to `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2` until the verified `v0.8.0` candidate is explicitly published

## Current regression baseline

Canonical post-Program 001 source is independently verified and post-merge green:

- pytest: **202 passed, 2 skipped, 354 subtests**
- unittest: **204 OK, 2 skipped**
- Python 3.11, 3.12, 3.13, and 3.14 CI lanes: PASS
- Wheel bootstrap portability: PASS
- Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**
- critical invariant mutations: **12/12 KILLED**
- Vessel Health mutations: **7/7 KILLED**
- tiered reconstitution mutations: **9/9 KILLED**
- operational drift mutations: **4/4 KILLED**
- source provenance mutations: **6/6 KILLED**
- integrated Post-Apex operational qualification: PASS

Canonical evidence:

- PR #53 final exact-head CI `32009983924`: PASS all five jobs
- PR #53 merge: `4122845858fae6abdf52af7a3a1ce56256e0c5cf`
- PR #53 post-merge CI `32010172588`: PASS all five jobs
- PR #54 merge: `14262546967d7aed54cf07f94759cf6e77414f24`
- PR #54 post-merge CI `32010554121`: PASS all five jobs

## Current source-defined Standing Crew

**Standing Crew: 82**

- 81 specialist-inspired GroX Crew
- 1 native independent verifier
- source dossiers are the current roster truth
- non-standing and stale private Crew operational state is removed during reconstitution
- GorXu remains the sole operational orchestrator

The roster and command model remain governed by `AI_INSTRUCTIONS.md`, `configs/crew/company-manifest.json`, and `docs/stewardship/CREW_ROSTER.md`.

## Operational Audit 001

**Status: CLOSED**

Operational Audit 001 verified finalization → authority → recovery after the Apex baseline and repaired weaknesses actually proved by evidence. It established the post-Apex hardening baseline released as `v0.7.1`.

Evidence and history remain in:

- `docs/stewardship/OPERATIONAL_AUDIT_001.md`
- `docs/history/ships-log/0038-operational-audit-001-governance-closed.md`
- release `v0.7.1`

## Post-Apex Operational Evolution Program 001

**Status: COMPLETE — CANONICAL POST-MERGE VERIFIED**

Program 001 converted approved external-review findings into a staged GroX-native evolution path without creating A8, a second command layer, or duplicate authority/state truth.

Canonical plan: `docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md`.

### Stage 0 — External capability intake convention

**Status: COMPLETE**

- `ADOPT | ADAPT | HARVEST | REJECT` convention is canonical;
- distinguishes source facts, external evidence, GroX inference, and GroX-native evidence;
- circular GroX re-import and duplicate decisions truth are explicitly rejected;
- external intelligence never inherits GroX authority.

### Stage 1 — Critical detector mutation proving

**Status: COMPLETE**

- 12/12 high-consequence mutations killed;
- ambiguous mutation targeting fails closed;
- source restored exactly after every mutation;
- continuous proof is part of protected Python 3.12 CI.

Evidence: `docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md`.

### Stage 2 — Native Vessel health

**Status: COMPLETE**

- read-only `grox health` and JSON surface;
- checks command, operational state, persistence, authority, memory, source, verification, environment, and recovery readiness;
- one detector failure cannot blind the report;
- inspection does not create or mutate operational state;
- 7/7 Vessel Health mutations killed.

Architecture: `docs/architecture/VESSEL_HEALTH.md`.
Evidence: `docs/verification/VESSEL_HEALTH_MUTATION_MATRIX.md`.

### Stage 3 — Tiered reconstitution

**Status: COMPLETE**

- FAST / TARGETED / FULL planning consumes Vessel Health rather than duplicating truth;
- FAST requires positive mandatory evidence and clean source;
- FULL is mandatory for fresh hosts, critical failures, unsafe in-flight state, dirty source, persistence problems, or missing/non-PASS mandatory evidence;
- planner performs no restore or mutation;
- 9/9 reconstitution mutations killed.

Architecture: `docs/architecture/TIERED_RECONSTITUTION.md`.
Evidence: `docs/verification/RECONSTITUTION_MUTATION_MATRIX.md`.

### Stage 4 — Context heat and bounded compression experiment

**Status: COMPLETE — CONTROLLED; RUNTIME ACTIVATION UNCLAIMED**

- HOT/WARM/COLD policy preserves active Commander intent, authority, critical evidence, unresolved state, safety boundaries, and next action;
- WARM compression requires caller-supplied attributable summaries;
- retained material preserves provenance;
- controlled corpus preserved 100% of declared critical facts and retained provenance while reducing 20,464 characters to 1,336 characters (93.47%);
- result is a controlled character-count result, not a production token/latency claim;
- automatic Pilot context compression remains deliberately inactive.

Research: `docs/research/CONTEXT_HEAT_EXPERIMENT.md`.

### Stage 5 — A6 longitudinal operational drift

**Status: COMPLETE**

- digest-bound operational windows and explicit `STABLE | WATCH | REGRESSION | UNKNOWN` findings;
- missing, tampered, stale, incompatible, or non-operational evidence becomes UNKNOWN;
- critical authority/capability/verifier/escalation/evidence-trace failures cannot be hidden by averages;
- real operational degradation experiment detected REGRESSION without changing the accepted baseline;
- proposal remained `proposed`; activation remained blocked;
- 4/4 operational-drift mutations killed.

Architecture: `docs/architecture/OPERATIONAL_DRIFT.md`.
Evidence: `docs/verification/OPERATIONAL_DRIFT_MUTATION_MATRIX.md`.

### Stage 6 — Mission-to-source provenance

**Status: COMPLETE — RESEARCH + BOUNDED IMPLEMENTATION**

- private nonce-bound authorization receipts reuse the existing StateStore plane;
- public commitments expose only opaque receipt ID, commitment, and coarse change class;
- issuance requires existing bounded Repair/mutation authority;
- exact scope/head/tree verification is enforced;
- missing private witness becomes UNKNOWN;
- downgrade, forgery, out-of-scope change, and replay fail;
- Inspect authority cannot mint source authorization;
- provenance never grants mutation authority;
- 6/6 source-provenance mutations killed.

Architecture: `docs/architecture/SOURCE_PROVENANCE.md`.
Research: `docs/research/MISSION_SOURCE_PROVENANCE.md`.
Evidence: `docs/verification/SOURCE_PROVENANCE_MUTATION_MATRIX.md`.

## Post-Apex Evolution Program 001 — Integrated qualification

**Status: COMPLETE — CANONICAL POST-MERGE PASS**

- preserved red run `32008781935` isolated a direct-script import-path defect in the new integration harness after every pre-existing protected gate remained green; the harness loader was corrected rather than bypassed;
- corrected exact-head run `32009009881` passed Python 3.11, 3.12, 3.13, 3.14 and Wheel bootstrap portability;
- Python 3.12 recorded pytest **202 passed, 2 skipped, 354 subtests** and unittest **204 OK, 2 skipped**;
- Vessel Health remained **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN** on the clean source and detected the injected non-Repair `fs_write` authority violation as `UNHEALTHY` without changing the private SQLite bytes;
- clean state selected FAST reconstitution; fresh-host and degraded authority state selected FULL;
- HOT/WARM/COLD packing preserved Commander intent, authority, critical evidence, unresolved critical state, next action, and retained provenance; automatic Pilot runtime activation remained disabled;
- A6 operational degradation remained `REGRESSION`, baseline content remained unchanged, the proposal remained `proposed`, and activation remained blocked;
- external intake continued to reject circular GroX re-import and duplicate decision truth;
- private source provenance verified an exact source binding while public metadata remained privacy-minimized; missing private witness returned `UNKNOWN`, downgrade/replay returned `FAIL`, and Inspect authority could not issue source authorization;
- mutation proof remained fully green: critical **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6** killed.

The experiment deliberately emits `qualification_claim=false`, `release_decision=false`, and `new_apex_stage=false`; the experiment did not self-certify. PR #53 received bounded PASS reviews on candidate head `5c58392a0b9f8fb80f085128588167712003f283` and final closeout head `3a58a8e9df85087cbbe382085e1b1d9ea1ae6fcd`; final PR CI run `32009983924` passed, the PR merged as `4122845858fae6abdf52af7a3a1ce56256e0c5cf`, and canonical post-merge run `32010172588` passed all five jobs. Any later release remains a Commander decision.

Evidence: `docs/verification/POST_APEX_EVOLUTION_001_INTEGRATION_EVIDENCE.md`.

## v0.8.0 release candidate

**Status: PREPARATION AUTHORIZED — TAG/PUBLICATION PENDING**

- Commander authorization opened issue #55 for a bounded `v0.8.0` candidate;
- candidate source begins from canonical post-merge verified `main@14262546967d7aed54cf07f94759cf6e77414f24`;
- package/source metadata is aligned to `0.8.0`;
- public README and current stewardship are being reconciled to the completed Program 001 state;
- preserved release-canary run `32014163449` failed because `test_source_version_detector_rejects_metadata_drift` hard-coded the prior `0.7.1` package string, so the test challenge no longer mutated metadata after the intentional `0.8.0` bump; Vessel Health itself remained healthy and reported source/package version aligned at `0.8.0`;
- the canary was repaired by deriving the current package version from `pyproject.toml` before injecting `9.9.9`, preserving the detector requirement while removing release-number coupling;
- the complete protected CI matrix plus independent exact-head verification are required before publication can be considered;
- no tag or GitHub release is created by preparation; publication remains a separate Commander-controlled action;
- no Commander, GorXu, Crew, Tool Gateway, verifier, persistence, A6 activation, or other authority boundary is widened; no A8 is created or implied.

## Known deliberate limits

- GorXu cognition is project-hosted through GPT-5.6 Sol when a capable Space Exploration session is active; deterministic control remains the safe fallback when cognition is unavailable.
- A3 episodic retrieval plus attributable semantic, procedural, and Vessel-wide memory are live with bounded selective retrieval; autonomous consolidation remains future evolution.
- A4 durable Mission Graph resume, checkpointing, bounded cancellation/retry, and text-Repair compensation are live; generic compensation for arbitrary external systems remains intentionally unclaimed.
- A5 qualifies bounded workspace shell/code execution, memory-only secret aliases, exact-origin read-only HTTP(S), offline browser evidence capture, and pre-registered stdio MCP. Unrestricted interactive desktop control, arbitrary/networked MCP processes, runtime image pulls/builds, and optional A2A delegation remain outside the qualified boundary.
- A5 isolation fails closed when neither the preferred namespace backend nor the host-commissioned Docker fallback is available.

## Apex Orchestrator readiness

**Current status: APEX QUALIFIED**

The initial self-assessment Mission `MSN-354de0550dd5` established the baseline gaps. Since then A1 Cognitive Pilot, A2 Mission Graph Orchestration, A3 Living Company Intelligence, A4 Executive Exception Loop and Durable Operations, A5 Governed Capability Expansion, and A6 Orchestration Intelligence and Self-Improvement have qualified. GorXu now has project-hosted cognition, durable dependency-aware multi-Crew graphs, attributable organizational memory, experienced routing, bounded selective memory, same-Mission crash recovery, checkpointed execution, bounded executive consultation/replanning, cancellation, journaled text-Repair compensation, governed multi-tool execution through Tool Gateway v2, and replayable evidence-backed orchestration evaluation whose proposals cannot self-activate.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`.

Apex critical path: **COMPLETE**. A1 through A7 are qualified; future changes must preserve the qualification invariants rather than inherit Apex automatically.

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
