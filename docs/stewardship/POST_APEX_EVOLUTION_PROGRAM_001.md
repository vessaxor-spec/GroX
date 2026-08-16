# Post-Apex Operational Evolution Program 001

**Status:** IN EXECUTION — STAGES 0-4 COMPLETE; STAGE 5 NEXT

**Planning baseline:** `main@c93015278daf022b1c3d85fc8fb90a6fa52d8160`

**External review source:** `vessaxor-spec/ClaudX@c82162b525ee183757e76300cc4a53f5643884f1`

## Purpose

This program converts the approved ClaudX review findings into a bounded GroX-native evolution path. It does not create an A8, import ClaudX as a dependency, or treat ClaudX-derived GroX concepts as external inventions.

The objective is to improve how the qualified Vessel determines its own condition, proves the truthfulness of its detectors, reconstitutes efficiently, manages cognitive context, detects long-horizon operational drift, evaluates external capability ideas, and links authorized Missions to source changes without weakening privacy or authority boundaries.

## Non-negotiable boundaries

- Commander authority and GorXu's role as sole operational orchestrator remain unchanged.
- Mission Control remains a GroX-native subsystem under GorXu, not a parallel command path.
- Standing Crew remain source-defined operational identities; retired or archived Crew are not retained as sleeping operational identities.
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
| Sleeping retired Crew identities | REJECT | Preserve GroX purge rule. |
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

### Stage 5 — A6 longitudinal operational drift analysis — NEXT

**Issue:** #28

Extend A6 trajectory evaluation to compare attributable operational evidence across time without a self-normalizing baseline or self-activation path.

Required design constraints:

- baseline identity/content must be frozen or cryptographically bound rather than overwritten by the act of checking;
- real operational history remains distinguishable from controlled/synthetic qualification cases;
- missing/stale evidence is UNKNOWN, not PASS;
- invariant failures remain first-class and cannot be hidden inside a composite score;
- drift creates an investigation/advisory finding or proposal only;
- A6 proposal activation remains denied.

Candidate signals include Mission disposition, evidence quality/trace completeness, verifier failures, authority/capability violations, exception/replan and recovery rates, cost, latency, tool failures, Crew utilization/routing concentration, and Commander escalation rate.

**Exit condition:** replayable evidence detects real/injected degradation against a protected baseline without self-normalization or self-activation and all affected A6/A7 invariants remain green.

### Stage 6 — Mission-to-source provenance research

**Issue:** #31

Research a privacy-safe link:

**Commander directive → GorXu decision → Mission / Mission Order → bounded implementation evidence → PR → CI / verification → merge → resulting source**

Research covers opaque identifiers/digests/attestations, squash-merge survival, multi-Mission changes, documentation-only work, verification rather than assertion, and leakage threats. CI must not need raw private operational state merely to prove provenance.

**Exit condition:** a source-backed `ADOPT | ADAPT | HARVEST | REJECT` decision with threat model, privacy boundary, verification mechanism, failure modes, and minimal implementation proposal only if warranted.

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
