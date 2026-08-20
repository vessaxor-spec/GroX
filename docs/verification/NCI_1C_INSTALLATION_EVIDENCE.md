# NCI-1C Standalone Installed GorXu Evidence

**Status:** COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED  
**Issue:** #96  
**Program:** Native Cognition Independence Program 001

## Objective

Prove that a non-editable installed GroX wheel can start the same canonical `PilotGorXu` outside a source checkout by using packaged immutable runtime assets and a commissioned NCI-1B separated Vessel layout.

Canonical command relationship remains:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Runtime assets, package metadata, private state, Commander workspace, tools, models, and installers are infrastructure beneath this command hierarchy.

## Qualified implementation

NCI-1C:

- packages the canonical repository `configs/` runtime inputs directly into the wheel data area rather than maintaining a second Crew/config tree;
- validates packaged policy, company manifest, exactly 82 Standing Crew dossiers, exactly 82 matching craft cards, and dossier identity before installed Pilot startup;
- preserves explicit/source-checkout operation as the developer and recovery path;
- falls back outside a checkout to a commissioned workspace plus validated packaged runtime assets;
- constructs the existing `VesselLayout.separated(...)` with immutable assets, private state, and Commander work roots;
- instantiates the existing `PilotGorXu`; no installed-only orchestrator is introduced;
- preserves Tool Gateway confinement to Commander work and private SQLite state outside package assets;
- fails closed when no commissioned workspace exists or packaged runtime assets are incomplete/malformed.

## Preserved red evidence

The first PR qualification run, `32375299755` / run **274**, proved the substantive installed path through startup, 82-Crew loading, bounded Crew orchestration, independent verification, and same-state reconstitution. Its Wheel job went red only at the deliberate corruption canary because the canary expected the narrower diagnostic phrase `packaged runtime assets are incomplete` while the locator reported that the installed distribution no longer contained the required asset bundle after `tool-policy.json` was deliberately removed.

The runtime **did fail closed**. The diagnostic contract was normalized without widening authority or changing the successful installed operating path, and the complete gate was rerun on the new exact head.

## Exact-head qualification

Final implementation head:

`e0c187567213fdf66cd1baaa03e3230ee1f16dd0`

Protected PR CI:

- run ID: `32375436084`;
- run number: **275**;
- result: **PASS — all five required jobs**;
- Wheel bootstrap portability: PASS;
- Regression / Python 3.11: PASS;
- Regression / Python 3.12: PASS;
- Regression / Python 3.13: PASS;
- Regression / Python 3.14: PASS.

The non-editable wheel gate proved from outside the repository:

1. the packaged runtime bundle validates with exactly 82 dossiers and 82 matching craft cards;
2. uncommissioned installed operation fails closed;
3. explicit source binding still works for developer/recovery operation;
4. a commissioned installed Vessel starts canonical Pilot GorXu with all 82 Standing Crew;
5. runtime assets, private state, and Commander workspace remain separated;
6. a bounded medium-risk Inspect Mission is issued by GorXu to `code-reviewer` and independently verified by a different eligible Crew member;
7. the Mission produces no mutation;
8. a fresh CLI process reopens the same private state and sees the same Mission;
9. deliberate removal of a required packaged policy asset causes fail-closed startup and recovery succeeds after restoration.

Python 3.12 additionally recorded:

- Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **285 passed, 2 skipped, 440 subtests passed**;
- unittest **287 tests OK, 2 skipped**;
- critical mutations **12/12** killed;
- Vessel-health mutations **7/7** killed;
- reconstitution mutations **9/9** killed;
- operational-drift mutations **4/4** killed;
- source-provenance mutations **6/6** killed;
- integrated Post-Apex qualification PASS with `gorxu_remains_sole_orchestrator: true`.

## Canonical merge and source equivalence

CI-tested synthetic merge:

`73fb8c58d2bd02271e2122b04a12c8f76bacef2d`

PR #97 canonical merge:

`0eddbc204b1e7b52158c355e9587731a7cbec08c`

Both resolve to the same tree:

`b4a4bf8f389309e79341ad8df9b6e1f5f6801e35`

A direct compare between the CI synthetic merge and canonical merge returned zero changed files. NCI-1C is therefore canonical and exact-tree/source-equivalent to the qualified candidate.

## Claim boundary

NCI-1C establishes packaged runtime assets plus standalone installed GorXu startup/orchestration from a commissioned local Vessel. It does **not** by itself establish:

- a native general-purpose language model;
- the remaining NCI-1 model registry/inference/readiness runtime contract;
- NCI-2 seed cognition;
- offline GorXu cognition;
- a desktop launcher;
- a public one-command installer;
- automatic no-argument first-run commissioning;
- a new package/release version;
- a new Apex stage or A8.

NCI-1 as a whole remains unqualified until the remaining native model/runtime contract earns its own evidence.
