# Tiered Reconstitution Mutation Matrix

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 3 — Tiered reconstitution

**Issue:** #27

## Purpose

This matrix proves that GroX's reconstitution planner escalates uncertainty and unsafe state rather than accidentally optimizing through it.

Mutations exist only in the CI checkout. Each proof weakens one production decision seam, requires the named production-path regression to fail, restores exact source bytes, reruns the same regression green, and requires `src/grox/reconstitution.py` to be Git-clean afterward.

## Preserved red evidence — redundant protection discovered

PR #36 CI run `31951963722` reached the Stage 3 mutation proof after both full regression runners and the Stage 1/2 mutation suites had passed.

Result:

- 7 of the initial 8 Stage 3 mutations were KILLED;
- 1 mutation SURVIVED: disabling the final `source_repository is None or status != PASS` safeguard did not make the `UNKNOWN` source test select FAST;
- the reason was independent earlier protection: the generic noncritical `WARN/UNKNOWN` path had already selected TARGETED for `source_repository=UNKNOWN`.

The survivor therefore identified **redundant protection**, not an unsafe path. The test was not weakened and the redundant protection was not removed merely to make mutation score green.

The final matrix was refined to challenge unique safety seams:

- the final source safeguard is now tested with **missing source-repository evidence**, where it is the unique boundary preventing FAST;
- a separate mutation was added for non-PASS `recovery_readiness`, an explicit Stage 3 FULL requirement.

## Final matrix

| # | Reconstitution invariant | Mutation | Target regression | Expected |
|---|---|---|---|---|
| 1 | Fresh host forces FULL | disable fresh-host FULL reason | `test_fresh_host_forces_full_even_when_health_is_clean` | KILLED |
| 2 | Source change forces FULL | disable source-change FULL reason | `test_source_change_forces_full` | KILLED |
| 3 | Critical health failure forces FULL | disable critical-failure FULL reason | `test_critical_health_failure_forces_full` | KILLED |
| 4 | Recovery readiness must be PASS | disable non-PASS recovery FULL reason | `test_recovery_warning_forces_full` | KILLED |
| 5 | Active/interrupted/unresolved state forces FULL | disable in-flight-state FULL reason | `test_interrupted_or_running_state_forces_full` | KILLED |
| 6 | Dirty/degraded source forces FULL | disable dirty-source FULL reason | `test_dirty_source_forces_full` | KILLED |
| 7 | Persistence WARN/FAIL forces FULL | disable persistence FULL reason | `test_persistence_warning_forces_full` | KILLED |
| 8 | Missing/non-PASS mandatory evidence forces FULL | disable mandatory-evidence FULL reason | `test_missing_mandatory_evidence_defaults_full` | KILLED |
| 9 | Missing source-repository evidence must not select FAST | disable final missing-source safeguard | `test_missing_source_repository_selects_targeted_not_fast` | KILLED |

`source_repository=UNKNOWN` remains separately covered by ordinary regression and by the generic TARGETED `WARN/UNKNOWN` path; the final matrix does not pretend the later redundant safeguard is uniquely responsible for that outcome.

## Source smoke

Canonical Python 3.12 CI additionally runs both planner modes against the clean source candidate before tests:

- normal clean health → FAST, 4/10 surfaces, structural reduction 0.6;
- `--fresh-host` → FULL, 10/10 surfaces, reduction 0.0;
- neither command may create operational state.

This is structural evidence-loading reduction, not a token-savings claim.

## Exit gate

Stage 3 closes only when all nine final mutations are killed, both earlier mutation suites remain green, both complete regression runners pass, the source planner smoke passes, wheel bootstrap portability passes, and no restore/authority behavior changes.
