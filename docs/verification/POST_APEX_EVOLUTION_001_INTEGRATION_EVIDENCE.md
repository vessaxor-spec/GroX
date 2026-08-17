# Post-Apex Operational Evolution Program 001 — Integration Evidence

**Evidence status:** PASS — independently verified candidate

**Independent exact-head verification:** PASS on PR #53 candidate head `5c58392a0b9f8fb80f085128588167712003f283`; final status-only head requires bounded re-verification before merge

## Scope

This record captures the integrated evidence produced for issue #48. It is an evidence matrix, not an authority record and not a self-approval.

The qualification experiment composes existing GroX production surfaces; it does not add a runtime control layer, activate context compression, grant source authority, create a second telemetry store, or create A8. Temporary Mission/provenance state exists only in ephemeral test storage.

## Preserved red evidence

Run `32008781935` failed at the new integration harness before any integrated semantic assertion executed:

- all pre-existing protected gates preceding the new step remained green;
- direct execution could not import `tests.experiments.operational_drift_experiment`;
- the harness was corrected to load the existing experiment by exact file path;
- no GroX runtime semantics or authority boundary was weakened to obtain green.

## Green integrated evidence

Corrected run `32009009881` passed all five canonical jobs. Python 3.12 recorded:

- Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest: **202 passed, 2 skipped, 354 subtests**;
- unittest: **204 OK, 2 skipped**;
- critical invariant mutations: **12/12 KILLED**;
- Vessel Health mutations: **7/7 KILLED**;
- reconstitution mutations: **9/9 KILLED**;
- operational drift mutations: **4/4 KILLED**;
- source provenance mutations: **6/6 KILLED**;
- integrated Post-Apex experiment: **PASS**.

## Integrated assertions

| Surface | Required behavior | Evidence result |
|---|---|---|
| Vessel Health | Truthful clean state; detect injected authority fault; observation remains read-only | PASS |
| Reconstitution | FAST for clean evidence; FULL for fresh host and degraded authority state | PASS |
| Context heat | Preserve Commander intent, authority, critical evidence, unresolved state, next action, and provenance | PASS |
| Context activation | Experiment must not silently activate Pilot runtime compression | PASS — remains disabled |
| A6 drift | Detect real injected operational degradation | PASS — `REGRESSION` |
| A6 baseline | Observation must not rewrite accepted baseline | PASS — unchanged |
| A6 activation | Proposal must not self-activate | PASS — `proposed`, activation blocked |
| External intake | Reject circular GroX re-import and duplicate decision truth | PASS — both `REJECT` |
| Provenance privacy | Public commitment must not expose private Mission/Order/nonce/Crew/directive values | PASS |
| Provenance verification | Exact private witness validates source binding | PASS |
| Missing witness | Absence of private authority truth may not become PASS | PASS — `UNKNOWN` |
| Downgrade/replay | Class downgrade and consumed-receipt replay must fail | PASS — both `FAIL` |
| Inspect boundary | Inspect authority cannot mint source authorization | PASS |
| Command architecture | Commander, GorXu, Crew, Tool Gateway, verifier, persistence, and A6 activation authority unchanged | PASS |

## Deliberate non-claims

The experiment output sets:

- `qualification_claim=false`;
- `release_decision=false`;
- `new_apex_stage=false`.

These are required boundaries. The experiment supplies evidence; independent exact-head verification decides whether that evidence is sufficient for protected merge. A release remains a separate Commander decision after program closure.

Independent review recorded PASS on candidate head `5c58392a0b9f8fb80f085128588167712003f283` with exact-head CI run `32009679294`. The resulting status-only closeout changes intentionally restart exact-head CI and bounded independent review before protected merge. This record does not authorize a release.
