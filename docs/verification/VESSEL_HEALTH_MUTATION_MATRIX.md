# Vessel Health Mutation Matrix

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 2 — Native Vessel health surface

**Issue:** #26

## Purpose

This matrix records the mutation proof for the critical behaviors introduced by the native Vessel health surface. It extends the Stage 1 detector discipline rather than replacing it.

Each mutation exists only in the CI checkout. The health mutation harness requires one exact production seam, observes the named production-path health regression fail, restores exact source bytes, reruns that detector green, and requires `src/grox/health.py` to be Git-clean before the proof succeeds.

## Preserved Stage 2 red evidence

### Red 1 — ineffective test challenge

Initial Stage 2 PR run `31950827151` failed with:

- pytest: **1 failed, 140 passed, 2 skipped, 19 subtests passed**;
- failing detector test: `test_source_version_detector_rejects_metadata_drift`.

The health implementation was not the cause. The test attempted to mutate `version="0.7.1"`, but canonical `pyproject.toml` uses `version = "0.7.1"`; the fixture therefore remained unchanged and the detector correctly returned PASS.

The test was corrected to mutate the exact source text and now asserts that the fixture mutation changes the file before asking the detector to evaluate it. The red run is preserved because it demonstrates a test-evidence failure: a regression test must prove that its challenge actually occurred.

### Red 2 — smoke executed after a dirtying test suite

Later exact-head run `31951286406` completed the full pytest and unittest suites successfully but failed the Python 3.12 `Vessel health source smoke`.

The health report was correctly `DEGRADED`, not `HEALTHY`, because `source_repository` observed one non-ignored working-tree change after the regression suites had already executed. All other checks passed, including 82 Standing Crew and `recovery_readiness=PASS`.

This was not resolved by weakening source health or treating dirty source as healthy. The smoke's purpose is to prove health on the clean source candidate, so it was moved before pytest/unittest and now explicitly requires `git status --porcelain=v1` to be empty before invoking `grox health --json`. Test-created workspace changes are later regression artifacts, not the clean candidate being measured.

The red run is preserved because it proves the health surface truthfully reports dirty source rather than conforming to an expected green disposition.

## Green Stage 2 mutation evidence

PR #35 candidate CI run `31951084789` completed all five canonical jobs successfully before final stewardship closure.

Python 3.12 recorded:

- pytest: **143 passed, 2 skipped, 19 subtests passed**;
- unittest: **145 OK, 2 skipped**;
- Stage 1 critical mutations: **12/12 KILLED**, zero survivors;
- Stage 2 health mutations: **7/7 KILLED**, zero survivors;
- both mutation harnesses restored source cleanly.

Final exact-head qualification additionally requires the clean pre-regression source smoke, complete suites, both mutation harnesses, and all five protected CI jobs to pass on the same candidate.

## Health mutation matrix

| # | Health invariant | Production mutation | Target detector | Result |
|---|---|---|---|---|
| 1 | One broken detector cannot blind the rest of the health report | change `_safe` from catching `Exception` to catching nothing | `test_one_detector_exception_does_not_blind_other_results` | KILLED |
| 2 | Interrupted Mission/graph state must surface for recovery | disable interrupted-state branch | `test_operational_state_warns_on_interrupted_mission` | KILLED |
| 3 | Persisted runtime history without a snapshot is not recovery-ready | disable runtime-without-snapshot warning | `test_persistence_warns_when_runtime_history_has_no_snapshot` | KILLED |
| 4 | Persisted non-Repair mutation grants are authority failure | disable non-Repair mutation-grant finding | `test_authority_detector_rejects_non_repair_mutation_grant_in_persisted_order` | KILLED |
| 5 | Active memory requires valid provenance | disable invalid-provenance finding | `test_memory_detector_rejects_invalid_active_provenance` | KILLED |
| 6 | Source/package version drift is critical | disable version-disagreement failure | `test_source_version_detector_rejects_metadata_drift` | KILLED |
| 7 | Critical health failure keeps reconstitution paused | disable recovery blocker branch | `test_recovery_readiness_fails_closed_on_critical_health_failure` | KILLED |

## Additional non-mutation evidence

The ordinary regression suite also proves:

- a source-only `grox health` inspection reconstructs the 82-Crew roster without creating runtime state;
- health collection does not change the SHA-256 of an existing SQLite operational database;
- `grox health --json` executes before Pilot construction and does not create a database;
- health output keeps unknown source-repository evidence explicit when Git metadata is unavailable.

The canonical CI source smoke is intentionally positioned against the clean source candidate, before tests can change the workspace. It:

- explicitly proves the working tree is clean;
- proves no operational database exists before health inspection;
- runs `grox health --json` against the actual PR/main checkout;
- requires overall `HEALTHY` and `source_repository=PASS`;
- requires 82 Standing Crew and `recovery_readiness=PASS`;
- proves no operational database is created.

## Exit gate

Stage 2 may close only after the final exact-head candidate passes the clean source smoke, both complete regression runners, both mutation harnesses, wheel bootstrap portability, and the remaining protected CI jobs without granting repair authority.
