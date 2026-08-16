# Ship's Log 0041 — Critical Detectors Mutation-Proven

**Date:** 2026-08-16

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 1 — Prove the detectors

**Issue:** #25

## Commander intent

The Commander approved harvesting the detector-testing discipline identified during the ClaudX comparative review: a critical check is not strong evidence until GroX has deliberately weakened the production invariant and observed the intended detector turn red.

## Implementation

Stage 1 added a CI mutation proof harness at `tests/mutation/run_critical_invariants.py` and two direct regressions that closed specific coverage gaps:

- executor self-verification rejection;
- committed Mission cost reconstruction across restart.

The harness applies isolated mutations only inside the CI checkout. It requires the targeted detector to fail, restores exact source bytes, reruns the detector green, continues across all selected cases, and fails if the mutated production paths are not Git-clean afterward.

## Preserved red evidence

PR #34 head:

`16e893dd9471e01d708096ec030ee6aaa6200568`

CI run:

`31950179712`

The normal full suites passed, and 11 selected mutations were killed. The final CI-action-pin mutation did not execute because the harness found two matching mutation seams and failed closed with:

`source drift: expected exactly one mutation seam, found 2`

No mutation survived. Source restoration remained clean.

This red run is retained because it demonstrates that mutation targeting itself is bounded and will not silently edit an arbitrary matching location.

## Remediation

The CI pin mutation was narrowed to one exact regression-job workflow block. No production invariant was weakened and no detector expectation was relaxed.

## Green qualification evidence

PR #34 head:

`988c97a390a31b5a255385149088ae7e67685fa9`

CI run:

`31950265325`

Results:

- pytest: **133 passed, 2 skipped, 19 subtests passed**;
- unittest: **135 OK, 2 skipped**;
- mutations: **12/12 KILLED**;
- surviving mutations: **0**;
- other mutation-proof failures: **0**;
- source restoration: **clean**;
- all five protected GroX CI jobs: **PASS**.

The 12 proven detector classes cover source/state restore, semantic orchestrator admission, stale Crew purge, verifier independence, forged verification evidence, hard Mission cost budget, cost reconstruction on resume, graph Repair authority, Tool Gateway Repair authority, critical Commander escalation, fail-closed Vessel binding, and immutable GitHub Actions pins.

The detailed matrix is canonicalized in `docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md`.

## Authority result

No weakened production variant is committed. Stage 1 changes verification infrastructure and regression coverage only. Commander authority, GorXu orchestration authority, Standing Crew, routing, Tool Gateway grants, persistence schema, production cost semantics, and package version are unchanged.

## Program transition

Stage 1 exit gate is satisfied.

The next authorized workstream is **Stage 2 / issue #26: build the native GroX Vessel health surface**.
