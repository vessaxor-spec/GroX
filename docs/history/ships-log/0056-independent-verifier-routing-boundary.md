# Ship's Log 0056 — Independent Verifier Routing Boundary

**Date:** 2026-08-18
**Status:** COMPLETE — CANONICAL POST-MERGE VERIFIED

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

## Qualification evidence

- final implementation head: `1531f4d4f3e2a222cdef5c32b7c6b70debba35de`;
- exact-head PR CI `32078828303`: PASS all five required jobs;
- PR #67 merged as `d04d21e38ffe1645d9c9e0df61e7ca96ac465066`;
- canonical push CI `32079205250`: PASS all five required jobs on exact `main@d04d21e38ffe1645d9c9e0df61e7ca96ac465066`;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **215 passed, 2 skipped, 354 subtests**; unittest **217 OK, 2 skipped**; cognitive context efficiency **82/82 Crew** at **45.15%** structural reduction; context heat PASS; expected operational-drift REGRESSION with activation blocked; mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed with clean restoration; integrated Post-Apex qualification PASS.

## Preserved boundaries

No release/tag/version moved, no authority widened, no Crew roster membership changed, and no A8 or new Apex stage was created or implied. The `ordinary_routing` policy constrains only automatic ordinary routing for `independent-verifier`; Verify eligibility and explicit separately authorized assignment remain intact.
