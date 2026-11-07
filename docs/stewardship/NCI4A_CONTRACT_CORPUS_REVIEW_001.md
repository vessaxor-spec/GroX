# NCI-4A Contract + Corpus Review Evidence 001

**Date:** 2026-11-07  
**Tracking issue:** [#209](https://github.com/vessaxor-spec/GroX/issues/209)  
**Review candidate:** [PR #217](https://github.com/vessaxor-spec/GroX/pull/217)  
**Disposition:** **REVIEW REQUESTED FOR CONTRACT/CORPUS SLICE; NCI-4A NOT QUALIFIED**  
**Canonical release:** unchanged `v0.8.0`  
**Canonical main:** unchanged until separately reviewed and merged.

## Scope

The proposal introduces an advisory-only Neural Crew output contract,
a narrow synthetic-only admission path, and an exact-content-committed,
write-once experimental generation manifest in the **existing private
GroX SQLite persistence plane**. It does not modify Pilot GorXu,
the 82-Crew roster, Mission Orders, the Tool Gateway, A6 evaluation,
model/provider registration, any live cognitive path, or model training.

## Reproducible corpus

- Seed: `tests/fixtures/nci4a_synthetic_seed.py`
- Generation identity: `nci4a-synthetic-g1`
- Cases: **12 invented policy vectors**, **6 train / 6 gold**
- Independent source-controlled digest pin:
  `tests/fixtures/nci4a_synthetic_seed.sha256`
- Expected pinned generation SHA-256:
  `4888ea9aa30af61937f528cda134adb9d469b2676b1edc6bd83c071ccb6b72a5`
- Source provenance: the exact `.py` test source bytes verified at admission,
  GroX-owned/synthetic declaration, no Commander or Mission transcript inputs.
- Corpus seal: explicit only; one `generation_id` cannot be resealed with
  different content or split assignments.
- Trainer-facing view returns only six `train` cases. Evaluator gold view is
  separate and requires the same externally pinned generation digest.
- Source-checkout revision and pinned manifest hash must be recorded together
  by anyone later using these cases for evaluation.

**Limits:** The label choices are synthetic reference expectations, not
independently established real-world ground truth. Six gold cases are a
minimal contract fixture, not statistical evidence of model improvement.
Gold data shares an SQLite database, and is not confidential from a database
administrator. Future training requires a separate isolated Trainer receiving
the train export only.

## Verification surface

- Advisory contract tests: `tests/unit/test_neural_crew_advice.py`
- Admission/holdout/recovery tests: `tests/unit/test_neural_crew_corpus.py`
- Write-once SQL triggers: `nci4a_generations_no_update`,
  `nci4a_generations_no_delete`
- Permanent critical mutations:
  - `neural-crew-advice-unknown-fields-denied`
  - `nci4a-private-source-admission-denied`
  - `nci4a-gold-holdout-never-exported-for-training`
  - `nci4a-external-generation-pin-required`
- Independent CI execution: GroX Wheel bootstrap, Python 3.11–3.14,
  Post-Apex integration, and permanent mutation matrix.
- Deliberate pre-pin red result in CI #679 documented the exact seed
  generation digest; the source-controlled pin was then committed.
- **Final exact-head CI:** must be green on the final reviewed PR head
  after all documentation changes; report its GitHub Actions run in the PR
  review record before approval. No green CI result should be claimed solely
  from an earlier branch head.

## Independent review checklist

1. Compare advisory output schema against the existing read-only Inspect
   Crew cognition and Mission Order/Tool Gateway boundaries.
2. Confirm unknown output fields, action/authority keywords, malformed
   confidence, and contradicting stop/evidence states fail closed.
3. Inspect that provenance verification resolves only source/test `.py`
   files beneath the explicitly selected source checkout and checks exact
   SHA-256; negative/private source types never auto-admit.
4. Check that free-form Commander content cannot enter the 7-field synthetic
   case input and that full private Mission trajectories remain excluded.
5. Independently verify the 12-case manifest digest against the checked-in
   pin and read-only database reconstruction.
6. Prove the write-once generation and external digest requirements resist
   split changes, DB row mutations, trigger deletion/tampering, and recovery.
7. Confirm the trainer-facing export cannot return any gold input, case ID,
   expected decision, or test label.
8. Review the negative test and mutation coverage, including restored-green
   behavior after each mutation and the exact CI source SHA.
9. Challenge the small synthetic gold benchmark for semantic label errors,
   contamination, misleading confidence, and scenario bias before it is used
   to compare models.
10. Ensure no code path invokes models, changes policy, or expands authority
    through this feature; no PR merge occurs without the project gates.

## Issue #209 exit-criteria traceability

| Exit | Evidence | Status |
| --- | --- | --- |
| 1. Typed advisory contract | `neural_crew_advice.py` | Implemented, review pending |
| 2. Strict field/authority denial | tests + critical mutation | Implemented, review pending |
| 3. Corpus + attribution/admission | `neural_crew_corpus.py` + source-hash cases | Implemented, review pending |
| 4. Immutable gold handling | sealed SQLite + external pin + negative tests | Implemented, review pending |
| 5. Parent/trainer bake-off protocol | `NCI4_NEURAL_CREW_EVOLUTION_001.md` | Planned; no bake-off executed |
| 6. Tiny policy and untrained LM baseline evaluation | Not part of this PR | **Open** |
| 7. No silent private source admission | synthetic-only validator + tests | Implemented, review pending |
| 8. No training or activation | isolated evaluator-only classes | Implemented, review pending |
| 9. Permanent authority invariant checks | four added mutation targets | Implemented, review pending |
| 10. Exact-head and post-merge CI | final PR CI required; no merge yet | **Open** |

## Decision boundary

**Do not close issue #209 or declare NCI-4A qualified from this packet.**
A reviewed, CI-green contract/corpus slice can merge separately, but the
remaining evaluator/baseline and final post-merge qualification gates must
be independently satisfied before the NCI-4A program is complete.
