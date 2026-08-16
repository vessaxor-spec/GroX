# Vessel Health Mutation Matrix

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 2 — Native Vessel health surface

**Issue:** #26

## Purpose

This matrix records the mutation proof for the critical behaviors introduced by the native Vessel health surface. It extends the Stage 1 detector discipline rather than replacing it.

Each mutation exists only in the CI checkout. The health mutation harness requires one exact production seam, observes the named production-path health regression fail, restores exact source bytes, reruns that detector green, and requires `src/grox/health.py` to be Git-clean before the proof succeeds.

## Preserved Stage 2 red evidence

Initial Stage 2 PR run `31950827151` failed with:

- pytest: **1 failed, 140 passed, 2 skipped, 19 subtests passed**;
- failing detector test: `test_source_version_detector_rejects_metadata_drift`.

The health implementation was not the cause. The test attempted to mutate `version="0.7.1"`, but canonical `pyproject.toml` uses `version = "0.7.1"`; the fixture therefore remained unchanged and the detector correctly returned PASS.

The test was corrected to mutate the exact source text and now asserts that the fixture mutation changes the file before asking the detector to evaluate it. The red run is preserved because it demonstrates a test-evidence failure: a regression test must prove that its challenge actually occurred.

## Green Stage 2 evidence

PR #35 candidate CI run `31951084789` completed all five canonical jobs successfully.

Python 3.12 recorded:

- pytest: **143 passed, 2 skipped, 19 subtests passed**;
- unittest: **145 OK, 2 skipped**;
- Stage 1 critical mutations: **12/12 KILLED**, zero survivors;
- Stage 2 health mutations: **7/7 KILLED**, zero survivors;
- both mutation harnesses restored source cleanly.

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
- health output keeps unknown source-repository evidence explicit when Git metadata is unavailable;
- the canonical CI source smoke runs `grox health --json` against the actual checkout, requires overall `HEALTHY`, requires 82 Standing Crew and `recovery_readiness=PASS`, and proves no runtime database is created.

## Exit gate

**PASSED.** Critical Stage 2 health behavior is production-wiring tested, mutation-proven, read-only, and continuously exercised by the protected Python 3.12 CI gate without granting repair authority.
