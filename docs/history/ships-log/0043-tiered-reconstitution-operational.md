# Ship's Log 0043 — Tiered Reconstitution Operational

**Date:** 2026-08-16

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 3 — Tiered reconstitution

**Issue:** #27

## Commander intent

The Commander approved adapting tiered fast/targeted/full reconstitution from the ClaudX comparative review only if GroX's existing recovery gates remained authoritative. Efficiency was permitted only as reduced evidence/context loading after current health had positively established the conditions for a shortcut.

## Implementation

GroX now exposes a read-only planning surface:

```text
grox reconstitution-plan
grox reconstitution-plan --json
grox reconstitution-plan --fresh-host
grox reconstitution-plan --source-changed
```

`src/grox/reconstitution.py` consumes the native Vessel Health report and chooses one of three modes:

- **FAST** — all mandatory evidence is positively PASS, source repository evidence is PASS, no unsafe in-flight state exists, and no fresh-host/source-change fact was declared;
- **TARGETED** — only bounded noncritical WARN/UNKNOWN surfaces need refresh after all FULL triggers are ruled out;
- **FULL** — fresh host, source change, critical health failure, non-PASS recovery readiness, active/interrupted/unresolved Mission state, dirty source, persistence warning/failure, or missing/non-PASS mandatory evidence.

The planner reports exact reasons and the evidence/context surfaces to load. It performs no restore, Pilot construction, Crew routing, state mutation, or authority change.

## Structural efficiency

The full reconstitution model contains ten evidence/context surfaces. FAST preserves four mandatory surfaces — command doctrine, source integrity, authority policy, and cognitive context — and therefore structurally avoids six of ten surfaces when the Vessel is already positively healthy.

This 60% figure is **not** a token-savings claim. It is only a count of defined reconstitution surfaces. Stage 4 independently evaluates context compression and quality preservation.

## Preserved red evidence

Initial Stage 3 mutation run:

`31951963722`

The normal health smoke, reconstitution smoke, pytest, unittest, Stage 1 mutations, and Stage 2 health mutations passed. The Stage 3 mutation harness then reported:

- 7 mutations KILLED;
- 1 mutation SURVIVED;
- source restoration clean.

The surviving mutation disabled the final `source_repository != PASS` safeguard while testing `source_repository=UNKNOWN`. It survived because an earlier independent generic WARN/UNKNOWN branch had already selected TARGETED. The survivor therefore revealed redundant protection rather than an unsafe FAST path.

GroX did not remove the earlier protection or weaken the test merely to improve the mutation score. The final matrix instead challenges unique safety seams: missing source-repository evidence now tests the final safeguard, and non-PASS recovery readiness has its own explicit mutation.

## Green qualification evidence

PR #36 run:

`31952132782`

Python 3.12 result:

- clean Vessel health source smoke: PASS;
- tiered reconstitution source smoke: PASS;
- pytest: **158 passed, 2 skipped, 19 subtests passed**;
- unittest: **160 OK, 2 skipped**;
- Stage 1 critical mutations: **12/12 KILLED**;
- Stage 2 health mutations: **7/7 KILLED**;
- Stage 3 reconstitution mutations: **9/9 KILLED**;
- mutation survivors: **0**;
- all mutation source restoration: **clean**;
- all five canonical CI jobs: **PASS**.

The clean-source smoke proves normal current-state planning selects FAST with 4/10 surfaces and structural reduction 0.6, while `--fresh-host` selects FULL with 10/10 surfaces and reduction 0.0. Neither path creates operational state.

Detailed architecture and mutation evidence are recorded in:

- `docs/architecture/TIERED_RECONSTITUTION.md`
- `docs/verification/RECONSTITUTION_MUTATION_MATRIX.md`

## Authority result

The planner is advisory only. Existing persistence restore, Mission resume, Commander escalation, Mission Order, Tool Gateway, and verification controls remain the authority-bearing paths. FAST and TARGETED never weaken those controls.

## Program transition

Stage 3 exit gate is satisfied.

The next authorized workstream is **Stage 4 / issue #30: test a GroX-native context heat model and bounded compression**.
