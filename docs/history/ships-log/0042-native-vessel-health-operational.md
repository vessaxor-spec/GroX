# Ship's Log 0042 — Native Vessel Health Operational

**Date:** 2026-08-16

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 2 — Native Vessel health surface

**Issue:** #26

## Commander intent

The Commander approved adapting the useful unified-health pattern identified in the ClaudX comparative review, but only as a GroX-native diagnostic surface over authoritative existing services. Health inspection was not permitted to become a repair engine, command layer, or duplicate state system.

## Implementation

GroX now exposes:

```text
grox health
grox health --json
```

`src/grox/health.py` collects isolated findings for command integrity, operational state, persistence readiness, authority integrity, memory integrity, source/version state, verification readiness, isolation readiness, and recovery readiness.

The health layer uses explicit `PASS`, `WARN`, `FAIL`, and `UNKNOWN` statuses. Unknown evidence is not treated as a pass. A broken detector becomes its own finding and does not suppress remaining checks.

## Read-only boundary

Health inspection does not construct `PilotGorXu` and does not initialize `StateStore`.

That distinction is material because normal state-store initialization performs crash-recovery transitions. Health instead uses SQLite read-only URI mode for private operational state and does not create a database when none exists.

Regression evidence proves an existing SQLite database has the same SHA-256 before and after health collection. The CLI path also proves that a source-only `grox health --json` invocation does not create runtime state.

Health cannot issue Orders, route or wake Crew, create/restore snapshots, mutate source, change Tool Gateway policy, activate an A6 proposal, or perform repair. Recommendations remain non-authorizing observations.

## Preserved red evidence

Initial PR #35 CI run:

`31950827151`

Result:

- pytest: **1 failed, 140 passed, 2 skipped, 19 subtests passed**;
- the failing source-version health test attempted to mutate a package-version string that did not match canonical whitespace, so the fixture did not change and the detector correctly returned PASS.

The test was repaired by targeting the exact source string and asserting that the fixture mutation actually changes the file before evaluating the detector. No health implementation was weakened to clear the run.

## Green qualification evidence

PR #35 run:

`31951084789`

Python 3.12 result:

- pytest: **143 passed, 2 skipped, 19 subtests passed**;
- unittest: **145 OK, 2 skipped**;
- Stage 1 critical invariant mutations: **12/12 KILLED**;
- Stage 2 health mutations: **7/7 KILLED**;
- mutation survivors: **0**;
- mutation source restoration: **clean**;
- all five canonical CI jobs: **PASS**.

The health mutation proof covers detector isolation, interrupted operational state, runtime state without snapshot coverage, non-Repair authority widening, invalid active-memory provenance, source/version drift, and fail-closed recovery readiness.

The Python 3.12 protected gate also runs the health CLI against the real source checkout, requires overall `HEALTHY`, 82 Standing Crew, `recovery_readiness=PASS`, and verifies that no operational database is created.

Detailed architecture and mutation evidence are recorded in:

- `docs/architecture/VESSEL_HEALTH.md`
- `docs/verification/VESSEL_HEALTH_MUTATION_MATRIX.md`

## Authority result

Commander sovereignty, GorXu sole-orchestrator authority, Crew membership and routing, Tool Gateway grants, persistence schema, Mission Graph semantics, A6 non-self-activation, and package version remain unchanged.

## Program transition

Stage 2 exit gate is satisfied.

The next authorized workstream is **Stage 3 / issue #27: tiered fast, targeted, and full reconstitution without weakening recovery gates**.
