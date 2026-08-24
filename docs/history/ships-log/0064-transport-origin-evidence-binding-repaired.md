# Ship’s Log 0064 — Transport Origin Evidence Binding Repaired

**Date:** 2026-08-24

## Event

Post-#131 recalibration found a fail-closed evidence-binding defect in the already-qualified bound remote cognition transport-freshness surface. Transport observations were keyed by cognition resource identity, but that identity does not include endpoint/origin. A same-provider/same-model endpoint rebind could therefore inherit still-fresh transport evidence from the prior origin.

Issue #132 bounded the repair. PR #133 first added a test-only red baseline, then changed only cognition awareness, targeted tests, and the critical mutation harness.

## Repair

- transport observations now carry the exact normalized origin probed on both reachable and unreachable outcomes;
- passive inventory rejects missing, malformed, invalid-current, or mismatched origin evidence as `unproven`;
- same provider/model rebound to a different endpoint immediately loses prior transport freshness without network I/O;
- the existing already-sealed exact `net_fetch` Mission Order and A5 Tool Gateway origin boundary remain unchanged;
- remote `ready=False`; no authorization, qualification/fit, selection, invocation, fallback, routing, Repair, verifier, or command authority changed.

## Qualification evidence

- red-before-green head: `149d09f8c323cd6d51f0f8600523855d408974f6`; GroX CI #443 / `32716652029` failed the intended endpoint-rebind assertion while Wheel remained green;
- final PR head: `b50605bb90660a9f3325fd356df65ab5409666e1`;
- exact-head GroX CI #448 / `32717652432`: PASS Wheel + Python 3.11–3.14;
- Python 3.12: Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN; pytest 376 passed, 2 skipped, 455 subtests; unittest 378 OK, 2 skipped; critical mutations 17/17; health 7/7; reconstitution 9/9; operational drift 4/4; source provenance 6/6; Post-Apex PASS;
- permanent mutation `cognition-transport-origin-binding`: KILLED;
- CI-tested synthetic merge: `726fc1ef6b351f7bf0371731dd18abafce8fe882`; tree `d8959016ce59dbd61cb148d974ba0c9e1d351c21`;
- canonical merge: `main@d7024261f9c49a8b2bb95a26e5ad0a08a6d5a34a`; tree `d8959016ce59dbd61cb148d974ba0c9e1d351c21`;
- canonical/synthetic exact-tree equality: PASS;
- issue #132 closed completed.

## Boundary

This is a repair to the fourth qualified Live Environment Awareness exit, not a fifth exit. Parent issue #115 remains OPEN. Provider/service readiness beyond exact-origin transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, provider switching/fallback, and adaptive provider/resource routing remain unqualified. No release/package, NCI, Apex, A8, public installer/desktop, or general-purpose GroX model claim changed.

Issue #134 tracks this documentation synchronization and is not pre-claimed complete by this log entry.
