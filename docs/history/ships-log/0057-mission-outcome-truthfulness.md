# Mission Outcome Truthfulness

**Date:** 2026-08-18
**Status:** COMPLETE — CANONICAL SOURCE MERGED

A public-readiness probe against `main@16f541480b192ca1f2576e3ed9c3457885b58f5e` exposed an outcome-truthfulness gap in the single-Mission Pilot path. Generic Execute work could correctly complete only a bounded repository inventory while the Commander-facing result still presented plain `completed`, making successful bounded execution easy to misread as delivery of the requested objective.

Issue #70 defined the bounded repair. PR #71 implemented it without widening authority.

## Canonical behavior

- executor lifecycle state and Commander-facing Mission outcome are now separate;
- generic Execute inventory fallback is reported as `status: scan_only` while `execution_status` remains `completed`;
- the persisted `mission_outcome` evidence contract records `execution`, `effect`, `objective`, `mutation`, `next_authority`, and `verification_scope`;
- scan-only execution reports `objective: not_delivered`, `mutation: false`, and `next_authority: explicit_operation_or_repair`;
- verification PASS on an unsatisfied objective is explicitly scoped to bounded execution evidence and does not become proof of objective delivery;
- supported explicit `repair-write` retains the existing Repair authority path, independent verification, and satisfied bounded objective semantics;
- failed Repair reporting is conservative: completed rollback reports `mutation_rolled_back` with no remaining mutation, while failed rollback or divergent mutation state reports `mutation_state_unresolved`, `mutation: true`, and returns to Pilot recovery.

Mission Graph authority and synthesis semantics were not changed by this repair.

## Independent review

Independent review found one material blocker before merge: the initial exception classifier would have reported `mutation: false` for every failed Mission, including a Repair whose mutation remained unresolved after rollback failure. The candidate was corrected before merge and permanent regressions now cover both failed rollback/divergent state and successful rollback.

## Qualification evidence

Final PR head: `37392878566bbe9ad84eba3b5d723a974cca5164`.

Canonical PR CI run `32127267143` passed all five required jobs:

- Wheel bootstrap portability;
- Regression / Python 3.11;
- Regression / Python 3.12;
- Regression / Python 3.13;
- Regression / Python 3.14.

Python 3.12 qualification recorded:

- Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **218 passed, 2 skipped, 354 subtests passed**;
- unittest **220 tests OK, 2 skipped**;
- critical invariant mutations **12/12 KILLED**;
- Vessel Health mutations **7/7 KILLED**;
- reconstitution mutations **9/9 KILLED**;
- operational drift mutations **4/4 KILLED**;
- source provenance mutations **6/6 KILLED**;
- integrated Post-Apex qualification PASS with `new_apex_stage=false`, `qualification_claim=false`, and `release_decision=false`.

PR #71 merged as canonical `main@1409605a98e0fd805a55839321f28364505773f5` and closed issue #70 as completed. The merged `main` tree SHA is `fedb4d54bb2e907f6fc9ff1e0125476c6af4f587`, exactly matching the tree of the final CI-qualified PR head, providing exact source-equivalence evidence. A separate post-merge push run was not observed through the available GitHub interface and is therefore not claimed.

## Boundaries preserved

- Commander sovereignty unchanged;
- GorXu remains sole operational orchestrator;
- Execute remains non-mutating without an explicitly governed operation;
- Repair remains explicit mutation authority;
- independent verifier separation remains intact;
- Standing Crew remains **82**;
- package remains `0.8.0`;
- published release remains immutable `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`;
- no A8 or new Apex stage was created or implied.
