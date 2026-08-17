# Source Provenance Mutation Matrix

## Purpose

The source-authorization provenance capability sits between private Commander-authorized Mission/Order evidence and public source-control evidence. Its most consequential detectors must therefore be proven capable of failing when weakened rather than merely covered by green tests.

The mutation harness changes only the CI checkout, runs the exact targeted regression, restores the production source byte-for-byte, and then proves the same regression returns green.

## Preserved red evidence

GroX CI run `32007023966` exposed two **surviving** mutations in the first source-provenance mutation matrix. Four of six mutations were killed, but two targeted seams were redundantly protected by independent checks:

- the initial Repair-order mutation targeted a test that also failed because the injected non-Repair Order lacked a mutating grant;
- the initial consumed-receipt replay mutation was still rejected by a later exact binding/replay defense.

The red result was treated as evidence that the mutation targets were not isolating the intended detectors. The production defenses were not weakened to make the harness pass.

The matrix was corrected by:

- adding a dedicated regression that injects a persisted mutation grant into a non-Repair Order so the Repair-mode gate is isolated;
- targeting the exact PR head/tree binding detector rather than a replay seam that was intentionally defended twice.

## Green exact-head evidence

GroX CI run `32007232455` passed all five protected jobs on PR #46 head `27134cdb1c595afb8d6460e8983674c73f0c9a4e`.

The Python 3.12 lane recorded:

- pytest: **200 passed, 2 skipped, 354 subtests passed**;
- unittest: **202 tests, 2 skipped, PASS**;
- Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN** with 82 Standing Crew;
- controlled context heat experiment: **PASS**;
- operational drift Mission experiment: **PASS**;
- critical invariant mutations: **12/12 KILLED**;
- Vessel Health mutations: **7/7 KILLED**;
- tiered reconstitution mutations: **9/9 KILLED**;
- operational drift mutations: **4/4 KILLED**;
- source provenance mutations: **6/6 KILLED**, zero survivors, exact source restoration.

## Source-provenance mutations

| Detector | Required failure behavior | Result |
|---|---|---|
| Repair-order authority | A persisted non-Repair Order cannot become receipt authority even if a mutation grant is injected. | KILLED |
| Commitment integrity | A forged public commitment cannot match the private witness. | KILLED |
| Scope containment | Changed paths outside every independently valid private receipt scope fail verification. | KILLED |
| Change-class floor | Public metadata cannot downgrade a stricter private change class. | KILLED |
| Missing witness | Unavailable private authorization evidence becomes `UNKNOWN`, never PASS. | KILLED |
| Exact-head binding | A receipt verified for one PR head/tree cannot be consumed against another head/tree. | KILLED |

## Authority boundary

Mutation proof does not create or expand authority. The provenance capability remains evidence-only:

- Mission Orders remain the mutation authority source;
- provenance cannot issue Orders, wake or route Crew, change capabilities, alter Tool Gateway policy, or write repository files;
- public CI does not receive private Commander/Mission state or a secret authority-verification key;
- receipt verification and consumption cannot turn an unauthorized source change into an authorized one.
