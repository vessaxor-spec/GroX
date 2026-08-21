# NCI-1D Native Model Runtime Evidence

**Status:** QUALIFIED — CANONICAL MERGED AND NCI-1 EXIT PROVEN  
**Issue:** #99  
**Exit issue:** #101  
**Implementation PR:** #100  
**Installed-wheel exit PR:** #102  
**Program:** Native Cognition Independence Program 001

## Objective

Prove that GroX can own the control contract around a registered local model without turning the model, registry, or inference backend into command authority, then prove that the same registered packaged model can load and execute from a non-editable installed wheel outside a source checkout.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Models, registries, inference backends, hardware profiles, and readiness state are subordinate runtime capabilities. They cannot issue Mission Orders, select Crew, grant Repair or verification authority, activate themselves, or become an alternate Pilot.

## Qualified implementation — issue #99 / PR #100

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

The runtime packages the exact trained weights corresponding to the prior live local neural qualification. The artifact retains the prior training provenance and trained model identity:

`7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`

Runtime loading verifies the outer artifact SHA-256/byte size and the internal trained-weight digest before inference. Training is not replayed during startup, so model identity does not depend on floating-point training reproduction across Python versions.

Registration does not bind the provider to Pilot GorXu. An explicit runtime load and the existing separate Pilot-owned Crew cognition binding are both still required.

## Preserved red evidence

The first candidate head `1833310769d443ef18f0fb8fce6262e92b5ab712` used the correct deterministic training recipe but reconstructed the trained weights during model load. Protected CI run `32392662853` / run **280** exposed that design as insufficiently portable: Python 3.11 reproduced the initial digest and held-out setup but not the exact final trained-weight digest, while later Python versions followed a different floating-point path.

The failure was contained by the digest gate; no mismatched model was activated. The design was corrected by packaging the already-qualified trained weights directly rather than weakening the integrity assertion or accepting version-dependent model identities.

## NCI-1D exact-head qualification

Corrected implementation head:

`2d68b63222cc69883d7c4252cbeeaaa9b6e5fb46`

Protected CI run **281 / `32393064902`** passed all five canonical jobs and proved the NCI-1D runtime contract across the supported Python matrix. PR #100 then merged as:

`8dde1a1714c38850c681623f1aba9238d6ec8b20`

Issue #99 was closed completed.

The implementation qualification covered:

1. registry and manifest validation;
2. artifact identity, SHA-256, and byte-size integrity;
3. duplicate/ambiguous registration refusal;
4. lineage unknown-parent/cycle refusal;
5. missing artifact → unavailable;
6. artifact mismatch → corrupt;
7. unsupported resource/backend conditions → unsupported;
8. backend load/inference failures are contained;
9. registration/readiness do not bind a Pilot or widen Mission authority;
10. explicit load is required before invocation;
11. the registered tiny policy executes through the existing GorXu-owned bounded Inspect Crew cognition seam;
12. no mutation authority is introduced;
13. independent verification remains intact;
14. reconstitution never auto-activates a model and surfaces missing/corrupt readiness safely;
15. the existing live local neural qualification remains non-regressed;
16. all canonical Python, Wheel, Health, mutation, provenance, and integrated Post-Apex gates remain green.

## Remaining NCI-1 exit gap discovered after PR #100

Post-merge stewardship inspection found one legitimate overall NCI-1 exit gap: source/test materialization had qualified the model registry/runtime, and NCI-1C had qualified the standalone installed wheel, but the installed-wheel path had not directly demonstrated packaged-model discovery, explicit load, inference, and safe reconstitution **outside the checkout** in one permanent proof.

Issue #101 bounded that missing evidence only. PR #102 added one permanent Wheel-bootstrap qualification assertion and changed no runtime/model/authority/Crew behavior.

## Installed-wheel NCI-1 exit qualification — issue #101 / PR #102

Final PR #102 head:

`689f1e1f77f49d9ea6eb5fb5fda49c54da3e6d6a`

Protected CI run **283 / `32406301653`**: **PASS — all five canonical jobs**.

The non-editable wheel, executed from `/tmp` outside the source checkout, permanently proved that it can:

- resolve `packaged_asset_root()`;
- discover the packaged model registry and artifact;
- report `tiny-mlp-policy-5x8x3-v1` as `AVAILABLE` and inactive;
- explicitly load it for Crew placement;
- invoke it through the GroX-owned local model runtime;
- report no authority change from load or invocation;
- reconstitute after prior activation with active state cleared;
- retain `auto_activation == false`;
- retain model readiness as available.

Qualification regression evidence on that exact head:

- installed packaged-model runtime: **PASS**;
- Python **3.11, 3.12, 3.13, 3.14: PASS**;
- Python 3.12 pytest: **294 passed, 2 skipped, 440 subtests**;
- Python 3.12 unittest: **296 OK, 2 skipped**;
- critical mutations: **12/12** killed;
- health mutations: **7/7** killed;
- reconstitution mutations: **9/9** killed;
- operational-drift mutations: **4/4** killed;
- source-provenance mutations: **6/6** killed;
- integrated Post-Apex qualification: **PASS**;
- `gorxu_remains_sole_orchestrator: true`.

## Canonical merge and exact-tree equivalence

PR #102 merged on 2026-08-20 as canonical:

`main@41fa4944d1b3e3011561a346b066df54be176a78`

Actual canonical merge tree:

`734e5b1762271045f0e4ac91c3f66334bdc13361`

The CI-tested synthetic merge was:

`34dbcb11831a4c5eccbfc5fb3211720ba94f4510`

with tree:

`734e5b1762271045f0e4ac91c3f66334bdc13361`

The canonical merge tree is therefore **identical** to the CI-tested synthetic merge tree. The source-equivalence gate is closed.

## NCI-1 exit verdict

**NCI-1 — Native cognition runtime + local Vessel foundation: QUALIFIED.**

The complete NCI-1 chain now proves:

- installed workspace commissioning;
- separated runtime assets / private state / Commander work;
- validated packaged runtime assets and standalone installed Pilot GorXu;
- a GroX-owned native model registry and local inference runtime contract;
- integrity/readiness/resource/lineage/failure/reconstitution behavior;
- one registered local model loaded and invoked from the installed packaged runtime outside a source checkout;
- no model self-activation, authority widening, or command-layer change.

NCI-2 is the next strategic stage. Qualification of NCI-1 does not pre-qualify NCI-2 or any later stage.

## Claim boundary

NCI-1 / NCI-1D does **not** establish:

- a general-purpose local language model;
- NCI-2 seed cognition;
- offline GorXu cognition;
- Repair/Verify/Execute model authority;
- model self-activation or self-promotion;
- a public one-command installer;
- a desktop launcher;
- a new package or release version;
- a new Apex stage or A8.

Package/source version remains `0.8.0`, the current published release remains `v0.8.0`, Standing Crew remain 82, and Pilot GorXu remains the sole operational orchestrator.
