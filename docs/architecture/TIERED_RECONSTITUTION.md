# GroX Tiered Reconstitution Architecture

## Purpose

Tiered reconstitution reduces unnecessary evidence/context loading when the Vessel is already demonstrably current. It does **not** create weaker restore rules.

The planner is an advisory read-only layer over `VesselHealth`. It selects how much evidence/context must be loaded before GorXu resumes operation; it does not itself restore snapshots, open a Mission, wake Crew, alter authority, or mutate state.

The surface is:

```text
grox reconstitution-plan
grox reconstitution-plan --json
grox reconstitution-plan --fresh-host
grox reconstitution-plan --source-changed
```

## Modes

### FAST

FAST is allowed only when required health evidence is positively PASS, the local source repository is positively clean/current, no unsafe in-flight state is present, persistence/recovery conditions are safe, and the caller has not declared a fresh host or source change.

FAST loads the minimum four mandatory surfaces:

1. `command_doctrine`
2. `source_integrity`
3. `authority_policy`
4. `cognitive_context`

This is a context/evidence-loading optimization only. It does not skip source integrity or authority context.

### TARGETED

TARGETED is used only for bounded noncritical WARN/UNKNOWN conditions after every FULL trigger has been ruled out.

It loads the four mandatory surfaces plus the named domain surface that needs refresh. Examples include:

- source repository evidence unavailable in a materialization where source integrity can be refreshed;
- noncritical environment/isolation readiness warning where the Mission does not yet require workspace execution.

TARGETED is not permitted to absorb a critical failure, unsafe Mission state, dirty source, persistence warning/failure, or non-PASS recovery readiness.

### FULL

FULL is the fail-closed mode and loads all ten reconstitution surfaces:

1. `command_doctrine`
2. `source_integrity`
3. `operational_state`
4. `persistence_binding`
5. `authority_policy`
6. `memory_state`
7. `verification_boundary`
8. `environment_capabilities`
9. `mission_recovery`
10. `cognitive_context`

FULL is selected when any of the following is true:

- fresh host;
- source changed since the prior operating context;
- any critical health check is FAIL;
- recovery readiness is absent or anything other than PASS;
- running/interrupted/needs-pilot-decision Mission state or running/interrupted graph state exists;
- source repository is dirty/degraded;
- persistence readiness is WARN or FAIL;
- mandatory health evidence is missing or anything other than PASS.

Failure or ambiguity therefore increases the amount of reconstitution; it never reduces it.

## Health dependency

The planner consumes a single `HealthReport` from the Stage 2 Vessel Health surface rather than reimplementing health detectors.

This avoids a second source of truth for:

- command integrity;
- operational state;
- persistence readiness;
- authority condition;
- memory integrity;
- source/version state;
- verification readiness;
- environment readiness;
- recovery readiness.

The planner may interpret those statuses for loading scope, but it does not redefine what PASS/WARN/FAIL/UNKNOWN mean.

## Explicit host/source facts

Two conditions are not reliably inferable from a local health report and are therefore explicit planner inputs:

- `fresh_host`
- `source_changed`

The CLI exposes them as flags. Declaring either forces FULL. Omitting them does not override health evidence; it only states that the caller has no separate knowledge of those conditions.

## In-flight state

Operational health evidence is inspected for:

- Mission `running`;
- Mission `interrupted`;
- Mission `needs_pilot_decision`;
- graph node `running`;
- graph node `interrupted`.

Any such state forces FULL because resuming a live/interrupted trajectory requires the complete recovery surface.

## Structural efficiency evidence

A `ReconstitutionPlan` reports:

- full surface count;
- planned surface count;
- avoided surface count;
- structural reduction ratio.

The metric is deliberately **not a token-savings claim**. It measures only how many defined reconstitution surfaces need loading under the selected mode.

With the current ten-surface baseline:

- FAST loads 4/10 surfaces, structurally avoiding 6/10;
- TARGETED typically loads 5/10 or the minimum additional bounded surfaces required;
- FULL loads 10/10.

Stage 4 separately determines whether context compression or heat classification yields real token/cost/latency benefit without information loss.

## Non-mutation boundary

`ReconstitutionPlanner` and `grox reconstitution-plan` do not:

- construct `PilotGorXu`;
- restore/create snapshots;
- create a private operational database;
- alter Mission or graph state;
- change Crew status;
- mutate memory;
- alter Tool Gateway policy;
- authorize Repair;
- activate A6 proposals;
- change repository source.

A FULL recommendation is not itself a restore action. Existing persistence and Mission-resume code remains the authority-bearing recovery implementation.

## Verification discipline

Stage 3 uses deterministic mode-selection tests plus a mutation harness in the required Python 3.12 CI gate.

The initial mutation run exposed redundant protection: disabling the final `source_repository != PASS` safeguard did not make UNKNOWN source evidence select FAST because the earlier generic TARGETED WARN/UNKNOWN path still protected it. This was not treated as a detector failure. The matrix was refined to challenge the unique missing-source safeguard and separately added a recovery-readiness mutation.

The final mutation set proves the unique FULL/TARGETED safety gates rather than requiring a redundant branch to be individually necessary.
