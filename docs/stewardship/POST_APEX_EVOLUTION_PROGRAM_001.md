# Post-Apex Operational Evolution Program 001

**Status:** IN EXECUTION — STAGE 0 COMPLETE; STAGE 1 NEXT

**Planning baseline:** `main@c93015278daf022b1c3d85fc8fb90a6fa52d8160`

**External review source:** `vessaxor-spec/ClaudX@c82162b525ee183757e76300cc4a53f5643884f1`

## Purpose

This program converts the approved ClaudX review findings into a bounded GroX-native evolution path. It does not create an A8, import ClaudX as a dependency, or treat ClaudX-derived GroX concepts as external inventions.

The objective is to improve how the qualified Vessel determines its own condition, proves the truthfulness of its detectors, reconstitutes efficiently, manages cognitive context, detects long-horizon operational drift, evaluates external capability ideas, and links authorized Missions to source changes without weakening privacy or authority boundaries.

## Non-negotiable boundaries

- Commander authority and GorXu's role as sole operational orchestrator remain unchanged.
- Mission Control remains a GroX-native subsystem under GorXu, not a parallel command path.
- Standing Crew remain source-defined operational identities; retired or archived Crew are not retained as sleeping operational identities.
- Inspection, evaluation, health checking, telemetry, and research do not grant mutation authority.
- A6 findings and drift signals remain advisory and may not self-activate changes.
- Private SQLite, `.groxstate`, raw Commander directives, private Mission content, credentials, and sensitive evidence remain outside public Git.
- Existing A1-A7 qualification invariants are regression boundaries, not inherited assumptions.
- Changes use protected `main`, pull requests, all canonical CI gates, and independent verification where policy requires it.
- New layers, Crew, state stores, or abstractions are added only when the existing architecture cannot satisfy the demonstrated need cleanly.

## Source-review classification

The approved ClaudX review produced the following GroX decisions. The posture column uses only the four canonical intake postures; research and testing are next actions, not additional postures.

| Candidate | Posture | GroX action |
|---|---|---|
| Unified Vessel health surface | ADAPT | Build a GroX-native diagnostic surface from authoritative existing services. |
| Health/governance detector mutation proving | HARVEST | Apply the testing discipline to GroX's critical invariants. |
| Tiered fast/targeted/full reconstitution | ADAPT | Optimize evidence loading without weakening existing recovery gates. |
| Long-horizon operational drift detection | ADAPT | Extend A6 using real Mission trajectories and protected baselines. |
| Adopt/adapt/harvest/reject intake discipline | HARVEST | Formalize a lightweight external-capability review convention. |
| Hot/warm/cold context management | HARVEST | Run GroX-native controlled experiments before any runtime adoption. |
| Mission-to-source provenance | HARVEST | Retain the traceability question; research and threat-model it before deciding whether to implement. |
| ClaudX's GroX-derived command spine, Crew, memory, durable ops, Mission Graph, A6 concepts | REJECT | Already native GroX capability; do not re-import or duplicate. |
| Separate decisions ledger | REJECT | Avoid duplicate source of truth. |
| Host-specific launchd heartbeat architecture | REJECT | Preserve host portability; only the abstract unattended-health idea may inform design. |
| Sleeping retired Crew identities | REJECT | Preserve GroX purge rule. |
| ClaudX's synthetic 57.4% token-savings claim as GroX proof | REJECT | Establish GroX evidence independently. |
| Removing `orchestration-evaluation-analyst` because ClaudX removed a similar role | REJECT | GroX role decisions require GroX authority/capability evidence. |

## Execution sequence

The work is deliberately staged so later capabilities depend on trustworthy evidence rather than being built simultaneously.

### Stage 0 - External capability intake convention — COMPLETE

**Issue:** #29

The lightweight GroX review convention is now defined in `docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md`.

It establishes:

- per-candidate `ADOPT | ADAPT | HARVEST | REJECT` classification before material implementation from external sources;
- explicit checks for existing coverage, novelty provenance, duplication, authority/privacy/portability risk, and evidence thresholds;
- separation of external source facts, external evidence, GroX inference, and GroX-native evidence;
- a compact review record that lives in existing Mission, issue, research, architecture, or stewardship records rather than a new decisions ledger;
- explicit preservation of the normal Commander -> GorXu -> Mission/Order -> verification -> protected source path after any intake decision.

The convention is exercised against the pinned ClaudX review, including different decisions for independent seams from the same repository and explicit rejection of circular GroX-derived material.

**Exit condition:** PASSED. One canonical convention/template exists and the ClaudX review is represented through it without architectural duplication.

### Stage 1 - Prove the detectors — NEXT

**Issue:** #25

Mutation-challenge the highest-consequence existing health, authority, recovery, identity, verification, bootstrap, and cost-control invariants.

Priority order:

1. source/state restore compatibility;
2. sole-orchestrator and Crew admission invariants;
3. stale/retired Crew operational purge;
4. verifier independence and forged-verifier resistance;
5. Mission cost commitment/resume accounting;
6. Repair/authority boundaries and no authority widening;
7. fail-closed Vessel-root bootstrap;
8. critical escalation behavior;
9. protected CI/action-pin contracts where practical.

Every selected detector must be observed failing against a deliberate isolated mutation for the intended reason before it is treated as proven.

**Exit condition:** a critical-invariant mutation matrix records mutation, expected red signal, observed red signal, restored green result, and any strengthened tests.

### Stage 2 - Native Vessel health surface

**Issue:** #26

Design and implement a unified diagnostic surface, provisionally `grox health`, from services GroX already owns.

Required domains:

- command integrity;
- operational-state integrity;
- persistence/source-state compatibility;
- authority/Tool Gateway condition;
- memory integrity/provenance condition;
- source/version binding where available;
- verification/regression condition;
- isolation/environment readiness;
- recovery readiness.

Health aggregation must preserve individual findings. One malformed checker may fail its own result but may not erase the rest of the health surface. Unknown or stale evidence is not healthy evidence. Health inspection is non-mutating by default and recommendations do not authorize repair.

**Exit condition:** production-wiring tests, mutation-proven critical detectors, independent verification, canonical CI, and no authority widening.

### Stage 3 - Tiered reconstitution

**Issue:** #27

Add fast, targeted, and full reconstitution selection on top of the existing three-plane persistence and recovery architecture.

- **Fast:** evidence proves current source/state binding, no unsafe in-flight state, and required health signals are fresh.
- **Targeted:** named surfaces need refresh or verification while the rest remain proven current.
- **Full:** fresh host, active/interrupted Mission recovery, source/state uncertainty, failed critical health evidence, or any unbounded condition.

Mode selection must state its reasons and escalate on uncertainty. Fast/targeted modes reduce context/evidence loading only; they do not weaken restore, integrity, authority, or Mission-resume rules.

**Exit condition:** deterministic mode-selection and escalation tests plus measurable reconstitution-efficiency evidence with unchanged recovery correctness.

### Stage 4 - Context heat and bounded compression experiment

**Issue:** #30

Test a GroX-native hot/warm/cold context model on representative long-horizon Mission and reconstitution traces.

- **Hot:** active intent, Commander constraints, authority, current graph/Mission state, unresolved exceptions/contradictions, latest critical evidence, next action.
- **Warm:** recent relevant decisions, Crew findings, retrieved memory, completed-node summaries, currently relevant history.
- **Cold:** old raw tool output, superseded discussion, dormant history, and re-derivable source material that is not currently authoritative.

The experiment must measure context size/cost/latency where available and separately measure preservation of intent, hard constraints, authority, unresolved conflict, provenance, and final task quality. Adversarial cases must include old information that remains safety- or authority-critical.

**Exit condition:** GroX evidence supports adoption, partial adoption, or rejection. No external synthetic savings percentage is used as the target.

### Stage 5 - A6 longitudinal operational drift analysis

**Issue:** #28

Extend existing A6 trajectory evaluation to compare real operational evidence across time without a self-normalizing baseline or self-activation path.

Candidate signals include:

- Mission disposition;
- evidence quality and trace completeness;
- verifier failures;
- authority/capability violations;
- exception/replan and recovery rates;
- cost and latency;
- tool failures;
- Crew utilization/routing concentration;
- Commander escalation rate.

Invariant failures remain first-class and may not be hidden inside a composite score. Controlled qualification corpora and real operational history remain separately attributable. Missing/stale data is unknown rather than pass. Drift produces an investigation or proposal only.

**Exit condition:** replayable evidence demonstrates detection of a real or injected degradation against a protected baseline, no self-normalization, no self-activation, and all affected A6/A7 invariants remain green.

### Stage 6 - Mission-to-source provenance research

**Issue:** #31

Research a privacy-safe link between authorized private Missions and public source mutations.

Desired trace:

**Commander directive -> GorXu decision -> Mission / Mission Order -> bounded implementation evidence -> PR -> CI / verification -> merge -> resulting source**

Research must cover public identifiers/digests/attestations, squash-merge survival, multi-Mission changes, documentation-only changes, verification rather than assertion, and leakage threats. CI must not require access to raw private operational state merely to prove provenance.

**Exit condition:** a source-backed adopt/adapt/harvest/reject decision with threat model, privacy boundary, verification mechanism, failure modes, and minimal implementation proposal only if warranted.

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

After the implementation/research stages complete, run an integrated post-evolution operational Mission that exercises the changed surfaces together. The final review must answer:

- Did health reporting stay truthful under injected faults?
- Did tiered reconstitution choose the correct mode under clean and degraded state?
- Did context optimization preserve intent, authority, and unresolved critical evidence?
- Did A6 detect degradation without changing its own baseline or activating a fix?
- Did external-intake classification prevent duplicate or circular architecture?
- If provenance is implemented, can the source/Mission link be verified without exposing private state?
- Did any change widen Commander, GorXu, Crew, Tool Gateway, verifier, or persistence authority?

Only evidence from that integrated Mission should determine whether this set of changes warrants a subsequent release. No version bump, release tag, new Apex stage, or A8 is implied by this plan.
