# Ship's Log 0056 — Independent Verifier Routing Boundary

**Date:** 2026-08-18
**Status:** IMPLEMENTED — FINAL EXACT-HEAD QUALIFICATION PENDING MERGE

Sandbox qualification found that `independent-verifier` could enter ordinary automatic routing even though its canonical craft card says it is not an alternate route for execution. The same card also preserves a deliberate exception: a separately authorized Mission Order may assign a different role or mode.

Repository inspection refined the policy before implementation. Sixteen Standing Crew are verification-capable, so `verification=true` means eligible for verification work and cannot be reused as a verification-only role marker. The bounded solution therefore adds a distinct `ordinary_routing` dossier property with a safe default of `true`, set to `false` only for `independent-verifier`.

## Boundary

- automatic ordinary/non-Verify routing excludes Crew whose dossier sets `ordinary_routing=false`;
- Verify routing continues to use `verification=true` and is unchanged;
- cognitive/preferred Crew recommendations remain advisory and cannot override deterministic ordinary-routing eligibility;
- explicit GorXu `crew_id` assignment remains available as the separately authorized exception path and still passes the normal Mission Order, capability, action, risk, scope, host-policy, and verification boundaries;
- the 82-Crew cognitive directory remains compact and does not serialize the new routing-policy field.

## Red-before-green evidence

Red baseline head `bfe43d87bf490b68e14340f8faf7f49b67f64d76` deliberately added the dossier marker and focused regressions before routing code changed. GroX CI `32078007106` failed exactly the three intended ordinary-routing assertions while Health and Wheel remained green:

1. Living Company ordinary routing still selected `independent-verifier`;
2. legacy roster ordinary routing still selected `independent-verifier`;
3. cognitive preference could still force `independent-verifier` into ordinary routing.

Verify routing, explicit assignment, and the dossier-policy assertion were already green in that red phase.

## Compatibility canary

After the routing boundary was implemented, an existing durable-recovery test failed because it counted all Orders assigned to `test-architecture-specialist` as a proxy for whether the committed architecture graph node had replayed. Excluding `independent-verifier` from ordinary recovery consultation made legitimate reuse of the architecture specialist possible, invalidating that proxy without replaying the committed graph node.

The regression was strengthened to bind its non-replay assertion to the architecture node's actual objective and persisted `order_id`. This preserves the real durability invariant while allowing legitimate Crew reuse during recovery.

## Qualification posture

Implementation head `e8a919ec54945a9a5cc400f9160389318702eb8a` passed the complete Python 3.12 qualification: Vessel Health 10/10 PASS; pytest 215 passed, 2 skipped, 354 subtests; unittest 217 OK, 2 skipped; cognitive context efficiency 82/82 at 45.15% structural reduction; context heat PASS; expected operational-drift REGRESSION with activation blocked; mutations 12/12, 7/7, 9/9, 4/4, 6/6 killed with clean restoration; integrated Post-Apex qualification PASS. Python 3.11, Python 3.14, and Wheel bootstrap were also green; Python 3.13 was still completing when final hygiene/stewardship changes created a new branch head.

Roadmap and Progress Tracker now describe the implemented policy as merge-pending. The final consolidated branch head contains the exact runtime, regression, durability-assertion, hygiene, and stewardship state intended for merge; PR #67 will record its exact SHA and five-job CI result without changing that source after qualification.

Final canonical merge remains gated on a fresh exact-head five-job CI run. No release/tag/version moved, no authority widened, no Crew roster changed, and no A8 or new Apex stage was created or implied.
