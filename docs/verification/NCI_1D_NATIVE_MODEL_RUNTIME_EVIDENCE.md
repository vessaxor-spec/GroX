# NCI-1D Native Model Runtime Evidence

**Status:** IMPLEMENTED CANDIDATE — QUALIFICATION PENDING  
**Issue:** #99  
**Program:** Native Cognition Independence Program 001

## Objective

Prove that GroX can own the control contract around a registered local model without turning the model, registry, or inference backend into command authority.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Models, registries, inference backends, hardware profiles, and readiness state are subordinate runtime capabilities. They cannot issue Mission Orders, select Crew, grant Repair or verification authority, or activate themselves.

## Candidate implementation

The NCI-1D candidate introduces:

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

The candidate packages the exact trained weights corresponding to the prior live local neural qualification. The artifact retains the prior training provenance and the trained model identity:

`7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`

Runtime loading verifies the outer artifact SHA-256/byte size and the internal trained-weight digest before inference. Training is not replayed during startup, so model identity does not depend on floating-point training reproduction across Python versions.

Registration does not bind the provider to Pilot GorXu. An explicit runtime load and the existing separate Pilot-owned Crew cognition binding are both still required.

## Preserved red evidence

The first candidate head `1833310769d443ef18f0fb8fce6262e92b5ab712` used the correct deterministic training recipe but reconstructed the trained weights during model load. Protected CI run `32392662853` / run **280** exposed that design as insufficiently portable: Python 3.11 reproduced the initial digest and held-out setup but not the exact final trained-weight digest, while later Python versions followed a different floating-point path.

The failure was contained by the digest gate; no mismatched model was activated. The design was corrected by packaging the already-qualified trained weights directly rather than weakening the integrity assertion or accepting version-dependent model identities.

## Required qualification

Protected CI must prove:

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
11. the registered tiny policy can execute through the existing GorXu-owned bounded Inspect Crew cognition seam;
12. no mutation authority is introduced;
13. independent verification still passes;
14. reconstitution never auto-activates a model and surfaces missing/corrupt readiness safely;
15. the existing live local neural qualification remains non-regressed;
16. all canonical Python 3.11–3.14, Wheel, Health, mutation, provenance, and integrated Post-Apex gates remain green.

## Evidence state

This file intentionally contains no PASS result, final successful CI run identifier, final candidate head, canonical merge SHA, or qualified tree yet.

Those facts will be recorded only after they actually occur.

## Claim boundary

NCI-1D does **not** establish:

- a general-purpose local language model;
- NCI-2 seed cognition;
- offline GorXu cognition;
- Repair/Verify/Execute model authority;
- model self-activation or self-promotion;
- a public one-command installer;
- a desktop launcher;
- a new package or release version;
- a new Apex stage or A8.

Until protected exact-head CI, review, canonical merge, and source-equivalence verification pass, NCI-1D remains an implementation candidate and NCI-1 remains unqualified.
