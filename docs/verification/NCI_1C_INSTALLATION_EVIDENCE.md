# NCI-1C Standalone Installed GorXu Evidence

**Status:** IMPLEMENTED CANDIDATE — QUALIFICATION PENDING  
**Issue:** #96  
**Program:** Native Cognition Independence Program 001

## Objective

Prove that a non-editable installed GroX wheel can start the same canonical `PilotGorXu` outside a source checkout by using packaged immutable runtime assets and a commissioned NCI-1B separated Vessel layout.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Runtime assets, package metadata, private state, Commander workspace, tools, models, and installers are infrastructure beneath this command hierarchy.

## Candidate implementation

The candidate:

- packages the canonical repository `configs/` runtime inputs directly into the wheel data area rather than maintaining a second Crew/config tree;
- validates packaged policy, company manifest, exactly 82 Standing Crew dossiers, exactly 82 matching craft cards, and dossier identity before installed Pilot startup;
- preserves explicit/source-checkout operation as the developer and recovery path;
- falls back outside a checkout to a commissioned workspace plus validated packaged runtime assets;
- constructs the existing `VesselLayout.separated(...)` with immutable assets, private state, and Commander work roots;
- instantiates the existing `PilotGorXu`; no installed-only orchestrator is introduced;
- preserves Tool Gateway confinement to Commander work and private SQLite state outside package assets;
- fails closed when no commissioned workspace exists or packaged runtime assets are incomplete/malformed.

## Qualification gate

Protected CI must prove from a non-editable wheel outside the repository:

1. the packaged runtime bundle validates with exactly 82 dossiers and 82 matching craft cards;
2. uncommissioned installed operation fails closed;
3. explicit source binding still works for developer/recovery operation;
4. a commissioned installed Vessel starts canonical Pilot GorXu with all 82 Standing Crew;
5. runtime assets, private state, and Commander workspace remain separated;
6. a bounded medium-risk Inspect Mission is issued by GorXu to `code-reviewer` and independently verified by a different eligible Crew member;
7. the Mission produces no mutation;
8. a fresh CLI process reopens the same private state and sees the same Mission;
9. deliberate removal of a required packaged policy asset causes fail-closed startup and recovery succeeds after restoration;
10. Python 3.11–3.14 regressions, Wheel bootstrap, Health, reconstitution, context experiments, mutation suites, provenance, and integrated Post-Apex qualification all remain green.

## Evidence state

This file intentionally contains no PASS result yet. Exact-head CI run identifiers, final head/tree digests, and canonical merge/source-equivalence evidence will be added only after those events actually occur.

## Claim boundary

Until exact-head protected CI and canonical merge/source equivalence pass, NCI-1C remains an implementation candidate only.

Even after NCI-1C qualification, it will not by itself establish:

- a native general-purpose language model;
- NCI-2 seed cognition;
- offline GorXu cognition;
- a desktop launcher;
- a public one-command installer;
- a new package/release version;
- a new Apex stage or A8.
