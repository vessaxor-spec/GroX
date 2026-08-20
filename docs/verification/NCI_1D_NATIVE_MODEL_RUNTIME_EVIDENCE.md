# NCI-1D Native Model Runtime Evidence

**Status:** QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED  
**Issue:** #99 — CLOSED / COMPLETED  
**Program:** Native Cognition Independence Program 001

## Objective

Prove that GroX can own the control contract around a registered local model without turning the model, registry, or inference backend into command authority.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Models, registries, inference backends, hardware profiles, and readiness state are subordinate runtime capabilities. They cannot issue Mission Orders, select Crew, grant Repair or verification authority, or activate themselves.

## Qualified implementation

NCI-1D introduced:

- an integrity-bound model manifest/artifact contract;
- deterministic local model registration and lineage validation;
- model readiness states for available, unavailable, corrupt, and unsupported conditions;
- host CPU/RAM/runtime discovery with explicit resource constraints;
- a provider-neutral local inference backend contract;
- explicit cognition placement that does not alter GroX hierarchy;
- explicit load/invoke/unload semantics;
- reconstitution that clears active model handles and never auto-activates a registered model;
- packaging for the local model registry/artifact alongside the existing immutable runtime assets.

The first registered model is the already-qualified narrow neural action-selection policy:

- provider: `local-neural-session-crew-v1`;
- model: `tiny-mlp-policy-5x8x3-v1`;
- kind: locally trained neural action-selection policy;
- architecture: 5 → 8 → 3 MLP;
- learned parameters: 75;
- placement: Crew only;
- qualified boundary: bounded Inspect Crew cognition only.

The qualified artifact packages the exact trained weights corresponding to the prior live local neural qualification. The artifact retains the prior training provenance and trained model identity:

`7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`

Runtime loading verifies the outer artifact SHA-256/byte size and the internal trained-weight digest before inference. Training is not replayed during startup, so model identity does not depend on floating-point training reproduction across Python versions.

Registration does not bind the provider to Pilot GorXu. An explicit runtime load and the existing separate Pilot-owned Crew cognition binding are both still required.

## Preserved red evidence

The first candidate head `1833310769d443ef18f0fb8fce6262e92b5ab712` reconstructed the trained weights during model load from the correct deterministic training recipe. Protected CI `32392662853` / run **280** exposed that design as insufficiently portable: Python 3.11 reproduced the initial model identity and held-out setup but not the exact final trained-weight digest.

The integrity gate correctly rejected the mismatched model. No mismatched model was activated and no authority widened.

The design was corrected by packaging the already-qualified trained weights directly rather than weakening the digest assertion or accepting Python-version-dependent model identities.

## Exact-head qualification

Corrected implementation head:

`2d68b63222cc69883d7c4252cbeeaaa9b6e5fb46`

Protected exact-head CI:

- run: **281 / `32393064902`**;
- Wheel bootstrap portability: PASS;
- Regression / Python 3.11: PASS;
- Regression / Python 3.12: PASS;
- Regression / Python 3.13: PASS;
- Regression / Python 3.14: PASS.

Python 3.12 evidence:

- Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest: **294 passed, 2 skipped, 440 subtests**;
- unittest: **296 tests OK, 2 skipped**;
- critical invariant mutations: **12/12 killed**;
- Health mutations: **7/7 killed**;
- reconstitution mutations: **9/9 killed**;
- operational-drift mutations: **4/4 killed**;
- source-provenance mutations: **6/6 killed**;
- integrated Post-Apex qualification: PASS;
- `gorxu_remains_sole_orchestrator: true`;
- the previously qualified live local neural Crew provider remained PASS.

The new runtime regressions proved:

1. registry and manifest validation;
2. artifact identity, SHA-256, and byte-size integrity;
3. duplicate registration refusal;
4. lineage unknown-parent/cycle refusal;
5. missing artifact → unavailable;
6. artifact mismatch → corrupt;
7. unsupported resource/backend conditions → unsupported;
8. backend load/inference failures are contained;
9. registration/readiness do not bind a Pilot or widen Mission authority;
10. explicit load is required before invocation;
11. the registered tiny policy executes through the existing GorXu-owned bounded Inspect Crew cognition seam;
12. no mutation authority is introduced;
13. independent verification still passes;
14. reconstitution never auto-activates a model and surfaces missing/corrupt readiness safely;
15. the existing live local neural qualification remains non-regressed;
16. all canonical Python, Wheel, Health, mutation, provenance, and Post-Apex gates remain green.

## Canonical merge and source equivalence

PR **#100 — NCI-1D: add native model registry and local inference runtime** merged as:

`8dde1a1714c38850c681623f1aba9238d6ec8b20`

CI synthetic merge:

- commit: `9ff3296c87328cdcc55bb8653ed8675c111ebd5d`;
- tree: `c68425bcefe02449476c73d5e93b6450ac27b369`.

Canonical merge tree:

`c68425bcefe02449476c73d5e93b6450ac27b369`

The canonical merge tree exactly equals the tree exercised by protected CI. Issue #99 was then closed as completed.

## NCI-1 installed-package exit proof

NCI-1D source qualification alone did not establish the broader NCI-1 exit because its integration test loaded the model from a source/test materialization. Issue #101 therefore required one additional installed-wheel proof joining NCI-1C and NCI-1D.

PR #102 added a permanent required Wheel-bootstrap assertion that runs from `/tmp` using the non-editable installed wheel. It proved that the packaged runtime assets can:

- resolve the packaged model registry and artifact;
- report `tiny-mlp-policy-5x8x3-v1` AVAILABLE and inactive;
- explicitly load it for Crew placement;
- invoke it through the GroX-owned runtime contract;
- reject requested authority widening by keeping `authority_changed=false` and `pilot_binding_changed=false`;
- reconstitute from an active model to zero active models;
- preserve `auto_activation=false` and model readiness;
- operate without a network/model-download dependency.

Exact-head installed exit proof:

- head: `689f1e1f77f49d9ea6eb5fb5fda49c54da3e6d6a`;
- CI: **283 / `32406301653`** — PASS all five required jobs;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **294 passed, 2 skipped, 440 subtests**;
- unittest **296 tests OK, 2 skipped**;
- mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed;
- integrated Post-Apex qualification PASS.

PR #102 merged as:

`41fa4944d1b3e3011561a346b066df54be176a78`

CI synthetic merge:

- commit: `34dbcb11831a4c5eccbfc5fb3211720ba94f4510`;
- tree: `734e5b1762271045f0e4ac91c3f66334bdc13361`.

Canonical merge tree:

`734e5b1762271045f0e4ac91c3f66334bdc13361`

The canonical tree exactly equals the CI-tested synthetic merge tree.

## Claim boundary

NCI-1D and the NCI-1 installed runtime exit evidence do **not** establish:

- a general-purpose local language model;
- NCI-2 seed cognition;
- offline GorXu language reasoning;
- Repair/Verify/Execute model authority;
- model self-activation or self-promotion;
- a public one-command installer;
- a desktop launcher;
- a new package or release version;
- a new Apex stage or A8.

NCI-1D is qualified within its exact bounded runtime/model contract. Overall NCI-1 may be marked qualified only when the canonical Roadmap and Progress Tracker are synchronized to the installed-wheel exit evidence above.