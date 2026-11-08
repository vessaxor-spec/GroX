# NCI-4A Experimental Corpus Admission and Gold Holdout

**Status:** Implemented as an isolated NCI-4A slice, subject to exact-head CI
and independent review. Does **not** qualify NCI-4A, register a model, or
authorize training or execution.

**Tracking:** issue #209; implementation `src/grox/neural_crew_corpus.py`.

## Scope and single source of truth

NCI-4A uses the existing **private GroX SQLite persistence plane**.
`nci4a_corpus_generations` records one self-contained, versioned generation
manifest and its SHA-256 commitment. It does **not** duplicate A6 operational
`evaluation_cases`, `evaluation_runs`, Mission Orders, or evidence.

A new generation requires an **explicit** `seal_generation` invocation with
the complete list of cases. No harvesting, Commander conversation ingestion,
provider invocation, training, model registration, or live Crew changes occur.

## Case contract

Each `grox-nci4a-case-v1` case has exactly:

- `case_id`: stable bounded identifier, unique within generation;
- `task_class`: one of `action_selection`, `evidence_triage`,
  `test_interpretation`, `failure_triage`, `stop_decision`,
  `policy_denial`;
- `split`: `train` or `gold`, fixed when the generation seals;
- `features`: **only** `observation_count` (integer 0–8),
  `test_requested` (boolean), `test_status` (bounded enum),
  `craft_present` (boolean), `memory_present` (boolean),
  `evidence_sufficient` (boolean), and `policy_denied` (boolean);
- `expected`: exact validated `grox-neural-crew-advice-v1` result
  (suggestion only; no operation or permission);
- `invariants`: nonempty unique canonical invariant IDs;
- `provenance`: exact `source_kind`, `source_path`,
  `source_sha256`, `rights`, `privacy_class`.

All cases are restricted to **GroX-owned synthetic** inputs.
Allowed provenance source kinds are `synthetic_contract`, `canonical_test`,
and `verified_negative`. Source references must resolve to actual
`src/grox/**/*.py` or `tests/**/*.py` files within the explicitly
selected repository checkout, with an exact matching SHA-256 digest.

`verified_negative` here means a case *attributed to a repository test
source*, not proof that a historical failure or real Mission was verified.
The expected decision label requires separate evaluation review.

Not admitted in this slice: Commander chats, private state, Mission traces
(even privacy-minimized ones), third-party model output treated as truth,
external corpora, data lacking explicit GroX rights and synthetic classification,
or arbitrary unbounded free-form input. Adding private trajectory admission
requires a separate review/authorization seam, not a generic exception.

## Generation contract and holdout

A `grox-nci4a-corpus-generation-v1` manifest contains exactly:
`schema`, `generation_id`, and sorted `cases`. It must contain **2–128**
unique cases, with both a train and a gold partition.

- SHA-256 commits to the canonical, complete manifest, including exact case
  contents, provenance, expected labels, and split membership.
- The database enforces write-once generation identity: `UPDATE` and
  `DELETE` are denied, and a duplicate-ID `BEFORE INSERT` guard also rejects
  `INSERT OR REPLACE` / `REPLACE INTO` even with recursive triggers disabled.
  Conflicting resealing fails closed.
- **Every read requires `expected_digest` obtained from a separately
  retained trusted record or reviewed source revision.** An owner who
  deliberately alters SQLite and its triggers cannot bypass this independent
  commitment merely by recomputing the database's stored hash.
- `training_cases` returns **only** train entries. Gold IDs, inputs,
  expected labels, and outcomes do not appear in that export.
- `gold_cases_for_evaluation` is a separately named evaluator-facing view.
  It is not an access-control system: an administrator with direct database
  access can read plaintext stored cases. Future Trainer work must place
  Trainers in an isolated environment with **only** the train export.
- No automatic split algorithm silently moves or reshuffles cases.
- Recovery reopens the existing private SQLite table and checks the pinned
  digest before a case can be exported.

**Boundary of the claim:** write-once SQL triggers, content commitments,
external pin checks, and export filtering establish an enforceable software
holdout protocol. They are not cryptographic protection against a hostile
filesystem/DB owner or unauthorized access to the private state directory.
Repository source pinning and isolation remain necessary.

## Independent evaluation requirements

Prior to NCI-4A closure:

1. Review all expected decisions and negative cases independently of the
   model under evaluation.
2. Establish exact, reproducible parent-vs-candidate scoring on the same
   pinned generation without gold leakage to the Trainer.
3. Score the qualified 75-parameter policy and one untrained language parent
   via separate evaluator adapters, with zero runtime activation.
4. Measure contract errors, action correctness, stop/continue and
   evidence-sufficiency errors, failure triage, calibration, resource cost,
   OOD abstention/injection resistance, and authority violations.
5. Show immutable gold membership and current source/provenance digest
   validity at evaluation time, including explicit source revision.
6. Pass exact-head GroX CI (Wheel + Python 3.11–3.14), mutation proof, and
   post-merge main CI.

**NCI-4A remains unqualified.** No model training, self-registration,
routing authority, or promotion follows automatically from this gate.
