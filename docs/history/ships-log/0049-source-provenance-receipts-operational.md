# Ship's Log — Entry 0049

**Date:** 2026-08-17
**Milestone:** Privacy-safe source authorization receipts operational

## Mission

Implement the Stage 6 provenance research decision without turning Git metadata into Commander authority, exposing private Mission state, or creating a second Mission ledger.

## Result

GroX now has a bounded `SourceProvenanceService` over the existing private `StateStore` SQLite plane.

A receipt may be issued only from an existing explicit Repair Order carrying a mutating action and source scope that covers the requested receipt paths. The private receipt uses a random opaque public ID and 256-bit private nonce. Its public commitment is domain-separated SHA-256 over canonical private authorization facts plus that nonce.

The public representation exposes only:

- provenance schema version;
- opaque receipt ID;
- commitment digest;
- coarse change class.

Commander directives, Mission/Order IDs, private nonce, Crew evidence, SQLite, `.groxstate`, credentials, and sensitive operational content remain private.

## Verification

Private verification reopens the originating Mission and Orders, verifies current Repair/mutation authority, recomputes the commitment, prevents class downgrade, checks normalized changed paths against independent receipt scopes, and binds PASS to the exact PR head/tree.

Missing private authority evidence is `UNKNOWN`, not PASS. Revoked, forged, replayed, downgraded or out-of-scope evidence fails. Consumption requires the exact previously verified PR/head/tree and records the resulting canonical source revision.

## Detector proof

The first mutation run exposed two non-isolating mutation targets and remained red. The harness was repaired without weakening production defenses.

Exact-head run `32007232455` then passed all five protected CI jobs with:

- pytest **200 passed, 2 skipped, 354 subtests passed**;
- unittest **202 tests, 2 skipped**;
- all previous Post-Apex experiments and mutation suites green;
- source-provenance mutation proof **6/6 KILLED**, zero survivors, exact restoration.

## Command integrity

The command relationship remains unchanged:

**Commander → GorXu → Divisions → Crew**

A provenance receipt is evidence that bounded private authorization already existed. It does not grant Repair permission, route Crew, mutate source, change Tool Gateway authority, or self-approve a change.

Repository-wide mandatory provenance enforcement remains deferred until integrated program qualification proves the capability together with the rest of the Post-Apex evolution surfaces and a durable private Vessel can issue and verify receipts operationally.
