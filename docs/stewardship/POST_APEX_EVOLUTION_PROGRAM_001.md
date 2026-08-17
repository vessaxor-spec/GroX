# Post-Apex Operational Evolution Program 001

**Status:** IN EXECUTION — STAGES 0-6 + PROVENANCE IMPLEMENTATION COMPLETE; INTEGRATION GATE NEXT

**Planning baseline:** `main@c93015278daf022b1c3d85fc8fb90a6fa52d8160`

**External review source:** `vessaxor-spec/ClaudX@c82162b525ee183757e76300cc4a53f5643884f1`

## Purpose

This program converts the approved ClaudX review findings into a bounded GroX-native evolution path. It does not create an A8, import ClaudX as a dependency, or treat ClaudX-derived GroX concepts as external inventions.

The objective is to improve how the qualified Vessel determines its own condition, proves the truthfulness of its detectors, reconstitutes efficiently, manages cognitive context, detects long-horizon operational drift, evaluates external capability ideas, and links authorized Missions to source changes without weakening privacy or authority boundaries.

## Non-negotiable boundaries

- Commander authority and GorXu's role as sole operational orchestrator remain unchanged.
- Mission Control remains a GroX-native subsystem under GorXu, not a parallel command path.
- Standing Crew remain source-defined operational identities; non-standing identities are not retained as sleeping operational identities.
- Inspection, evaluation, health checking, telemetry, planning, experimentation, and research do not grant mutation authority.
- A6 findings and drift signals remain advisory and may not self-activate changes.
- Private SQLite, `.groxstate`, raw Commander directives, private Mission content, credentials, and sensitive evidence remain outside public Git.
- Existing A1-A7 qualification invariants are regression boundaries, not inherited assumptions.
- Changes use protected `main`, pull requests, all canonical CI gates, and independent verification where policy requires it.
- New layers, Crew, state stores, or abstractions are added only when the existing architecture cannot satisfy the demonstrated need cleanly.

## Source-review classification

The approved ClaudX review produced the following GroX decisions. Research and testing are next actions, not additional intake postures.

| Candidate | Posture | GroX action |
|---|---|---|
| Unified Vessel health surface | ADAPT | Build a GroX-native diagnostic surface from authoritative existing services. |
| Health/governance detector mutation proving | HARVEST | Apply the testing discipline to GroX's critical invariants. |
| Tiered fast/targeted/full reconstitution | ADAPT | Optimize evidence loading without weakening existing recovery gates. |
| Long-horizon operational drift detection | ADAPT | Extend A6 using real Mission trajectories and protected baselines. |
| Adopt/adapt/harvest/reject intake discipline | HARVEST | Formalize a lightweight external-capability review convention. |
| Hot/warm/cold context management | HARVEST | Run GroX-native controlled experiments before runtime adoption. |
| Mission-to-source provenance | HARVEST | Retain the traceability question; research and threat-model it before deciding whether to implement. |
| GroX-derived ClaudX command spine, Crew, memory, durable ops, Mission Graph, A6 concepts | REJECT | Already native GroX capability; do not re-import or duplicate. |
| Separate decisions ledger | REJECT | Avoid duplicate source of truth. |
| Host-specific launchd heartbeat architecture | REJECT | Preserve host portability; only the abstract unattended-health idea may inform design. |
| Sleeping non-standing Crew identities | REJECT | Preserve GroX purge rule. |
| ClaudX synthetic 57.4% token-savings claim as GroX proof | REJECT | Establish GroX evidence independently. |
| Removing `orchestration-evaluation-analyst` because ClaudX removed a similar role | REJECT | GroX role decisions require GroX authority/capability evidence. |

## Execution sequence

The work is deliberately staged so later capabilities depend on trustworthy evidence rather than being built simultaneously.

### Stage 0 — External capability intake convention — COMPLETE

**Issue:** #29

`docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md` defines the lightweight `ADOPT | ADAPT | HARVEST | REJECT` convention. It distinguishes source facts, external evidence, GroX inference, and GroX-native evidence; checks existing coverage and circular novelty; and preserves the normal Commander → GorXu → Mission/Order → verification → protected source path.

The convention is exercised against the pinned ClaudX review without creating a command layer, external dependency, or duplicate decisions ledger.

**Exit condition:** PASSED.

### Stage 1 — Prove the detectors — COMPLETE

**Issue:** #25

`docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md` records continuous mutation proof for 12 high-consequence restore, command-identity, stale-Crew, verification, cost, authority, escalation, bootstrap, and CI supply-chain invariants.

Preserved red run `31950179712` proved ambiguous mutation targeting fails closed. Green run `31950265325` recorded pytest **133 passed, 2 skipped, 19 subtests passed**, unittest **135 OK, 2 skipped**, **12/12 mutations KILLED**, zero survivors, and clean restoration. Final exact-head Stage 1 run `31950516865` passed all five canonical jobs before merge.

**Exit condition:** PASSED.

### Stage 2 — Native Vessel health surface — COMPLETE

**Issue:** #26

`src/grox/health.py` plus `grox health` / `grox health --json` provide an isolated read-only diagnostic surface across command, operational state, persistence, authority, memory, source, verification, environment, and recovery readiness.

Health does not construct Pilot, create operational state, issue Orders, route Crew, restore snapshots, or repair the Vessel. SQLite is opened read-only. `PASS`, `WARN`, `FAIL`, and `UNKNOWN` remain explicit and one failed detector cannot blind the report.

Stage 2 preserved three red evidence classes rather than weakening health: ineffective test-fixture mutation (`31950827151`), post-regression dirty-source observation (`31951286406`), and generated editable-install metadata exposing a `.gitignore` gap (`31951491116`).

Final pre-merge run `31951586094` passed the clean health smoke, pytest **143 passed, 2 skipped, 19 subtests passed**, unittest **145 OK, 2 skipped**, Stage 1 mutations **12/12 KILLED**, Stage 2 health mutations **7/7 KILLED**, and all five canonical jobs. PR #35 merged as `7209fa9cf3f5d2cf2cd9d1df840c91ea946c544c` with zero tree drift; post-merge run `31951678763` passed.

Architecture: `docs/architecture/VESSEL_HEALTH.md`  
Evidence: `docs/verification/VESSEL_HEALTH_MUTATION_MATRIX.md`

**Exit condition:** PASSED.

### Stage 3 — Tiered reconstitution — COMPLETE

**Issue:** #27

`src/grox/reconstitution.py` consumes the native Vessel Health report and selects a read-only evidence-loading plan:

- **FAST** — all mandatory evidence positively PASS, source repository PASS, no unsafe in-flight state, no fresh-host/source-change fact; loads 4/10 mandatory surfaces.
- **TARGETED** — bounded noncritical WARN/UNKNOWN surfaces only, after all FULL triggers are ruled out.
- **FULL** — fresh host, source change, critical failure, non-PASS recovery readiness, active/interrupted/unresolved Mission state, dirty source, persistence WARN/FAIL, or missing/non-PASS mandatory evidence; loads all 10 surfaces.

The planner performs no restore, Pilot construction, Crew routing, state mutation, memory mutation, or authority change. Existing persistence/Mission recovery remains authoritative.

FAST structurally avoids 6/10 defined reconstitution surfaces; this is a **structural loading metric, not a token-savings claim**.

Preserved red mutation run `31951963722` revealed redundant independent protection rather than an unsafe FAST path. Green Stage 3 run `31952132782` passed the health/reconstitution smokes, pytest **158 passed, 2 skipped, 19 subtests passed**, unittest **160 OK, 2 skipped**, Stage 1 **12/12**, Stage 2 **7/7**, and Stage 3 **9/9** mutations killed, zero survivors, clean restoration, and all five CI jobs. PR #36 then closed Stage 3 through the protected merge path.

Architecture: `docs/architecture/TIERED_RECONSTITUTION.md`  
Evidence: `docs/verification/RECONSTITUTION_MUTATION_MATRIX.md`  
History: `docs/history/ships-log/0043-tiered-reconstitution-operational.md`

**Exit condition:** PASSED.

### Stage 4 — Context heat and bounded compression experiment — COMPLETE

**Issue:** #30

Stage 4 deliberately remains an experiment rather than a Pilot runtime mutation.

`src/grox/context_heat.py` defines a deterministic HOT/WARM/COLD policy:

- active Commander intent, constraints, authority, Mission/graph state, unresolved exceptions/contradictions, critical evidence, safety boundaries, and next action are HOT and retained verbatim;
- critical material remains HOT regardless of age;
- relevant WARM decisions/findings/memory/history may use only caller-supplied attributable summaries; without a safe summary, raw text remains;
- COLD re-derivable or superseded material may be omitted;
- every retained item preserves provenance.

`tests/experiments/context_heat_experiment.py` evaluates four controlled GroX scenarios: long Mission, reconstitution, adversarial old safety fact, and WARM material without a safe summary.

The deterministic corpus contains **20,464 source characters** and packs to **1,336 characters**, a controlled character reduction of **93.47%**, while preserving **100% of declared required critical facts** and **100% retained-item provenance**. Scenario reduction ranges from **70.82% to 97.90%**.

This is **not a production token-savings or latency claim**. Processing-time telemetry is recorded only diagnostically because the corpus is too small to support a meaningful latency conclusion. ClaudX's synthetic 57.4% result was not used as a target or baseline.

Decision: **HARVEST** the bounded HOT/WARM/COLD policy as an evidence-supported GroX design technique, but **defer Pilot runtime activation** until the integrated post-evolution Mission tests the technique against real program evidence.

Research: `docs/research/CONTEXT_HEAT_EXPERIMENT.md`  
History: `docs/history/ships-log/0044-context-heat-experiment-passed.md`

**Exit condition:** PASSED for controlled experiment; runtime activation remains deliberately unclaimed.

### Stage 5 — A6 longitudinal operational drift analysis — COMPLETE

**Issue:** #28

`src/grox/operational_drift.py` extends the existing A6 evaluation plane with digest-bound operational windows and explicit `STABLE | WATCH | REGRESSION | UNKNOWN` findings. No second telemetry store or autonomous optimization loop was introduced.

Operational windows accept only attributable `canonical_private_mission_state` trajectory cases. Each window binds case IDs, case digests, trajectory digests, a window digest, metric schema, and the ordinary A6 run digest. Comparisons reopen and verify those bindings; missing, tampered, stale, incompatible, or non-operational evidence becomes `UNKNOWN` rather than PASS. A proposed baseline containing a critical invariant failure or incomplete trace is also `UNKNOWN`, preventing degradation from self-normalizing into the accepted baseline.

Critical authority, capability, verifier-independence, escalation, and evidence-trace failures remain first-class and cannot be hidden by averages. Longitudinal signals include success, evidence quality, verification failures, cost, budget pressure when available, latency, retries, exceptions, replans, resumes, tool failures, Commander escalation, and Crew routing concentration/utilization. Findings remain advisory; A6 proposal activation is still denied.

Preserved red run `32004304942` exposed a direct-script import-path defect in the operational experiment after all unit/regression tests had passed. The experiment bootstrap was corrected rather than bypassed. Green exact-head implementation run `32004673068` then passed all five canonical jobs with pytest **185 passed, 2 skipped, 351 subtests**, unittest **187 OK, 2 skipped**, Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, prior mutation suites **12/12**, **7/7**, and **9/9** killed, plus Stage 5 operational-drift mutations **4/4 KILLED**.

The production-path experiment ran four real GorXu Inspect Missions in an isolated temporary Vessel: two healthy baseline Missions followed by two injected test-failure Missions. A6 detected `REGRESSION` with success rate **1.0 → 0.0**, tool failure rate **0.0 → 0.5**, evidence quality **0.916667 → 0.666667**, and no baseline digest/metric mutation. The generated proposal remained `proposed` and activation remained blocked.

Architecture: `docs/architecture/OPERATIONAL_DRIFT.md`
Evidence: `docs/verification/OPERATIONAL_DRIFT_MUTATION_MATRIX.md`
History: `docs/history/ships-log/0047-a6-operational-drift-complete.md`

**Exit condition:** PASSED.

### Stage 6 — Mission-to-source provenance research — COMPLETE

**Issue:** #31

Research decision: **ADAPT**.

`docs/research/MISSION_SOURCE_PROVENANCE.md` defines a privacy-safe bridge between private Commander-authorized Mission/Order evidence and public PR/CI/merge history without creating a second Mission ledger or exposing private operational state.

The recommended minimal design is a private nonce-bound authorization receipt stored in the existing operational evidence plane, a public opaque receipt ID + SHA-256 commitment + coarse change class, structural-only public CI, and independent private verification of commitment/scope/replay state. Final source revisions map back to the merged PR through the source-control platform's commit-to-PR association rather than depending on feature-branch commit survival.

Raw Mission/Order identifiers, Commander directives, private nonce, Crew notes, SQLite, `.groxstate`, credentials, and sensitive evidence remain private. Provenance proves a prior authorization relationship; it never grants authority.

GitHub/Sigstore custom attestations are retained only as optional future public cryptographic hardening if an external consumer appears. They are not the private authority witness and are not required for the minimal design.

Research: `docs/research/MISSION_SOURCE_PROVENANCE.md`
History: `docs/history/ships-log/0048-mission-source-provenance-researched.md`

**Exit condition:** PASSED. Separate bounded implementation is warranted and must prove forged/replayed/out-of-scope/downgraded receipts fail, missing private evidence is UNKNOWN, squash linkage survives, and public CI never receives private raw operational state.

### Provenance implementation — COMPLETE

**Issue:** #45

`src/grox/source_provenance.py` implements the Stage 6 ADAPT decision as a private authorization-evidence capability over the existing `StateStore` SQLite plane. It introduces no second state database or public Mission ledger.

Receipt issuance requires an existing explicit Repair Order carrying a mutating action and source scope that covers the requested receipt paths. Each receipt uses a random opaque public ID and 256-bit private nonce. Public metadata exposes only the v1 schema, opaque ID, domain-separated SHA-256 commitment, and coarse change class.

Private verification reopens the originating Mission and Orders, verifies current Repair/mutation authority, recomputes the commitment, rejects class downgrade, enforces normalized path coverage, prevents incompatible replay, and binds PASS to the exact PR head/tree. Missing private authority evidence is `UNKNOWN`, never PASS. Consumption requires that exact verified binding and records the canonical source revision.

Repository-wide mandatory provenance enforcement remains deliberately inactive until integrated qualification and a durable private Vessel can issue/verify the corresponding private receipts operationally. Public CI remains structural-only and receives no raw private authority state.

Preserved red evidence includes temporary harness run `32006665435`, which exposed a missing test-runtime installation, and source-provenance CI run `32007023966`, which killed 4/6 mutations while exposing two non-isolating mutation targets protected by redundant defenses. Neither result was bypassed. The harness and detector targets were corrected without weakening production behavior.

Exact-head green run `32007232455` then passed all five protected jobs with pytest **200 passed, 2 skipped, 354 subtests**, unittest **202 tests, 2 skipped**, all prior Post-Apex experiments/mutation suites green, and source-provenance mutation proof **6/6 KILLED**, zero survivors, exact source restoration.

Architecture: `docs/architecture/SOURCE_PROVENANCE.md`
Evidence: `docs/verification/SOURCE_PROVENANCE_MUTATION_MATRIX.md`
History: `docs/history/ships-log/0049-source-provenance-receipts-operational.md`

**Exit condition:** PASSED. Integrated Post-Apex Evolution Program 001 qualification is next.

## Cross-workstream verification rules

Each implementation workstream must:

1. recalibrate against current `main` and current operational evidence before mutation;
2. identify affected Apex invariants before changing source;
3. keep the change isolated from unrelated work;
4. add production-path tests rather than helper-only confidence where practical;
5. run the complete canonical CI matrix;
6. use independent verification where required by GroX policy;
7. preserve red canary evidence instead of bypassing it;
8. update Roadmap, Progress Tracker, architecture/specification docs, and Ship's Log only when state actually changes;
9. avoid claiming qualification from implementation alone;
10. stop only for a critical blocker, irreversible Commander decision, or evidence that the approved design is materially unsafe or incompatible.

## Integration gate

After implementation/research stages complete, run an integrated post-evolution operational Mission that verifies:

- health remains truthful under injected faults;
- tiered reconstitution selects correct modes under clean and degraded state;
- context optimization preserves intent, authority, provenance, and unresolved critical evidence;
- A6 detects degradation without changing its own baseline or activating a fix;
- external-intake classification prevents duplicate/circular architecture;
- provenance, if implemented, is verifiable without exposing private state;
- no change widens Commander, GorXu, Crew, Tool Gateway, verifier, or persistence authority.

Only that integrated evidence should determine whether the program warrants a subsequent release. No version bump, release tag, new Apex stage, or A8 is implied by this plan.
