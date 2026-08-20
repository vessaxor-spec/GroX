# NCI-1 Qualification Evidence

**Program:** Native Cognition Independence Program 001  
**Stage:** NCI-1 — Native cognition runtime + local Vessel foundation  
**Status:** TECHNICAL EXIT SATISFIED — STEWARDSHIP CLOSEOUT PENDING

## Exit contract

NCI-1 requires GroX to commission and locate its local Vessel, resolve packaged runtime assets independently of a source checkout, validate/load/invoke a registered local model through a GroX-owned runtime contract, emit readiness evidence, fail closed on corruption/unavailability, and reconstitute safely without changing Commander authority, Pilot GorXu's personal-assistant/sole-orchestrator role, or the Prime Function.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

## Constituent qualifications

### NCI-1A — installed workspace commissioning

- issue #90 / PR #91;
- exact-head CI run **267 / `32349808199`** PASS;
- canonical merge: `2b4e1c8f3fff8081a30dab4702738cf8b5c01480`;
- canonical tree: `e25f239f73e8325ff956962358779f919524e27a`.

Established installed `grox init` / `grox workspace`, per-user binding, `~/GroX` default workspace, collision/refusal semantics, partial commissioning recovery, and non-editable-wheel commissioning outside a repository checkout.

### NCI-1B — runtime/assets, private state, Commander work separation

- issue #92 / PR #93;
- exact-head CI run **270 / `32356241254`** PASS;
- canonical merge: `55c98b13a169476cfedad89c1db2c2c36e9536fd`;
- canonical tree: `fa4255792801a2b45a2b1daad2ecee334a55484d`.

Established immutable runtime/assets, private state, and Commander-work roles while preserving the legacy layout and keeping Tool Gateway ordinary filesystem authority confined to Commander work.

### NCI-1C — packaged runtime assets + standalone installed GorXu

- issue #96 / PR #97;
- exact-head CI run **275 / `32375436084`** PASS;
- canonical merge: `0eddbc204b1e7b52158c355e9587731a7cbec08c`;
- canonical tree: `b4a4bf8f389309e79341ad8df9b6e1f5f6801e35`.

Established validated packaged runtime assets and standalone installed Pilot GorXu operation from a commissioned workspace without requiring a source checkout/manual root override.

### NCI-1D — native model registry + local inference runtime

- issue #99 / PR #100;
- rejected first candidate: `1833310769d443ef18f0fb8fce6262e92b5ab712`, CI run **280 / `32392662853`** exposed Python 3.11 trained-weight replay drift;
- corrected exact head: `2d68b63222cc69883d7c4252cbeeaaa9b6e5fb46`;
- exact-head CI run **281 / `32393064902`** PASS all five jobs;
- canonical merge: `8dde1a1714c38850c681623f1aba9238d6ec8b20`;
- canonical tree: `c68425bcefe02449476c73d5e93b6450ac27b369`, exactly equal to the CI synthetic merge tree.

Established a GroX-owned model registry, model/artifact integrity, lineage validation, hardware/runtime readiness, provider-neutral inference backend contract, explicit load/invoke/unload, cognition placement, fail-closed corruption/unavailability behavior, and safe non-auto-activating reconstitution.

The first registered model remains exactly the previously qualified narrow policy:

- `tiny-mlp-policy-5x8x3-v1`;
- 5 → 8 → 3 MLP;
- 75 learned parameters;
- trained-weight SHA-256 `7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`;
- bounded Inspect Crew action-selection only;
- not a general-purpose language model.

## Installed packaged-model exit proof — issue #101 / PR #102

The constituent NCI-1D integration test used a source/test materialization, so the broader stage exit was deliberately not inferred from NCI-1D alone.

PR #102 permanently extended the required Wheel bootstrap qualification to execute from `/tmp` with only the non-editable installed wheel. The proof:

1. resolves `packaged_asset_root()`;
2. discovers the packaged model registry/artifact;
3. reports `tiny-mlp-policy-5x8x3-v1` AVAILABLE and inactive;
4. requires explicit Crew-placement load;
5. invokes the model through the GroX-owned runtime contract;
6. confirms `authority_changed=false` and `pilot_binding_changed=false` even when the invocation payload asks for Repair/verifier authority;
7. reconstitutes from an active model to zero active models;
8. confirms `auto_activation=false` and continued readiness;
9. requires no network/model download.

Exact-head evidence:

- head: `689f1e1f77f49d9ea6eb5fb5fda49c54da3e6d6a`;
- protected CI: **run 283 / `32406301653` — PASS**;
- Wheel bootstrap: PASS including `Installed packaged model runtime satisfies NCI-1 exit`;
- Python 3.11, 3.12, 3.13, 3.14: PASS;
- Python 3.12 Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest: **294 passed, 2 skipped, 440 subtests**;
- unittest: **296 tests OK, 2 skipped**;
- mutations: **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed;
- integrated Post-Apex qualification: PASS;
- `gorxu_remains_sole_orchestrator: true` remained intact.

Canonical merge:

- PR #102 merge: `41fa4944d1b3e3011561a346b066df54be176a78`;
- CI synthetic merge commit: `34dbcb11831a4c5eccbfc5fb3211720ba94f4510`;
- CI synthetic merge tree: `734e5b1762271045f0e4ac91c3f66334bdc13361`;
- canonical merge tree: `734e5b1762271045f0e4ac91c3f66334bdc13361`.

The canonical merge tree exactly equals the protected-CI synthetic merge tree.

## Exit assessment

All technical clauses of the NCI-1 exit contract are now evidenced:

| Exit clause | Evidence | Result |
|---|---|---|
| commission/locate local Vessel | NCI-1A | PASS |
| independent runtime/assets/state/work layout | NCI-1B | PASS |
| packaged assets independent of source checkout | NCI-1C | PASS |
| registered local model integrity/readiness | NCI-1D | PASS |
| explicit model load/invoke | NCI-1D + installed Wheel exit proof | PASS |
| installed-wheel packaged model invocation | PR #102 / run 283 | PASS |
| missing/corrupt/unsupported fail closed | NCI-1D regressions | PASS |
| reconstitution clears active model and never auto-activates | NCI-1D + PR #102 | PASS |
| Commander/GorXu authority unchanged | NCI-1D + Post-Apex + PR #102 | PASS |
| all required protected CI gates | run 283 | PASS |

**Technical assessment: NCI-1 exit SATISFIED.**

The stage is not marked canonical `QUALIFIED` in this document until the Roadmap and Progress Tracker are synchronized through the same protected closeout path. Issue #101 remains open until that stewardship closeout is merged and source-equivalence verified.

## Non-claims

NCI-1 does **not** establish:

- a built-in general-purpose local language model;
- NCI-2 seed cognition;
- offline GorXu natural-language reasoning;
- a public one-command installer;
- a desktop launcher;
- all 82 Crew as autonomous model processes;
- model cognition in Repair/Verify/Execute;
- model self-activation/self-promotion;
- a new package/release version;
- a new Apex stage or A8.

The next roadmap stage after canonical stewardship closeout is **NCI-2 — Built-in local seed cognition**.