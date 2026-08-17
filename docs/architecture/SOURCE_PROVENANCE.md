# Source Authorization Provenance

## Purpose

GroX source authorization provenance links a proposed public source change to a bounded private authorization witness without publishing Commander directives, Mission/Order identifiers, private nonces, Crew evidence, SQLite state, `.groxstate`, credentials, or sensitive operational content.

It is an **evidence mechanism**, not an authority mechanism.

The authority relationship remains:

**Commander → GorXu → Divisions → Crew**

Mission Orders remain the source of bounded mutation authority. A provenance receipt can only be issued after the private Vessel already contains an explicit Repair Order carrying a mutating action and scope that covers the requested source receipt.

## Evidence planes

### Private operational plane

`SourceProvenanceService` uses the existing `StateStore` SQLite connection and adds one table:

`source_authorization_receipts`

There is no second state database and no public Mission ledger.

A private receipt contains:

- random opaque receipt ID;
- schema version;
- originating private Mission ID;
- authorizing private Repair Order IDs;
- change class;
- normalized source path scope;
- operation class;
- private authority state;
- 256-bit private nonce;
- commitment;
- verification binding;
- consumption/revocation state;
- private timestamps.

The service re-reads the authorizing Mission and Orders during private verification. Missing authority evidence becomes `UNKNOWN`; an Order that no longer carries valid Repair/mutation authority causes verification to fail.

### Public source-control plane

The public block contains only:

```text
GroX-Source-Provenance: v1
GroX-Authorization-Receipt: SRC-<opaque random id>
GroX-Authorization-Commitment: sha256:<digest>
GroX-Change-Class: runtime | stewardship | research
```

The receipt ID is random and does not encode the Mission, Crew, Division, risk, scope, or issuance time.

Public structural validation checks format only. It cannot truthfully assert private authorization because it has no private witness.

## Commitment

The v1 commitment is:

```text
SHA256(
  "grox-source-receipt-v1" || NUL ||
  private_nonce ||
  canonical_private_receipt_without_nonce
)
```

The private receipt is canonical UTF-8 JSON with sorted object keys and no insignificant whitespace.

The private nonce is never published. This prevents the public digest from becoming a practical dictionary oracle for low-entropy Commander/Mission facts.

## Issuance gate

A receipt may be issued only when:

1. the Mission exists in the private `StateStore`;
2. every named authorizing Order belongs to that Mission;
3. each authorizing Order is in `repair` mode;
4. each authorizing Order has an explicit mutating action;
5. no authorizing Order is in a rejected/failed/blocked/cancelled state;
6. the requested receipt paths are fully covered by the union of the selected Order scopes;
7. source paths are normalized repository-relative paths and cannot traverse outside the repository.

Receipt issuance does **not** execute the mutation.

## Private verification

`verify_change()` requires:

- one or more public receipt blocks;
- actual changed repository paths;
- PR identity;
- exact PR head SHA;
- exact PR tree SHA.

For every receipt it:

1. parses the public block;
2. finds the private witness or returns `UNKNOWN`;
3. rejects revoked/replayed receipts;
4. re-checks the current originating Mission and Repair Orders;
5. reconstructs and recomputes the commitment;
6. rejects public class downgrade;
7. calculates coverage from the independent private scopes;
8. fails if any changed source path remains uncovered;
9. binds successful verification to the exact PR/head/tree.

Multiple receipts may cover different changed paths, but their scopes are not merged into a new authority object. Every path must be covered by at least one independently valid receipt.

## Head changes and replay

Verification is exact-head evidence.

If a PR head or tree changes, `verification_binding_matches()` becomes false and the new head requires another private verification. A receipt already consumed by another logical change cannot be rebound to a different PR.

A verified receipt can be consumed only when the caller supplies the exact verified PR/head/tree binding. Consumption then records the resulting canonical source commit.

A consumed receipt is not a reusable bearer token and cannot be retroactively revoked to rewrite history.

## Failure semantics

- `PASS` — private witness is available, currently valid, commitment matches, class is not downgraded, and changed paths are covered.
- `FAIL` — malformed/forged public evidence, invalid/revoked/replayed authority, class downgrade, or scope violation.
- `UNKNOWN` — required private Mission/Order evidence is unavailable or cannot be reliably interpreted.

`UNKNOWN` is never treated as authorization.

## Public CI boundary

The current implementation exposes `validate_public_block()` for structural validation and testing. Repository-wide mandatory PR provenance enforcement is deliberately **not activated yet**.

That enforcement must wait until:

1. the capability passes integrated Post-Apex qualification;
2. a durable private Vessel can issue and retain the private receipt that public metadata commits to;
3. an operational verification path exists for the private witness without copying private state into GitHub Actions.

Public CI must never receive the private nonce, Commander directive, raw Mission/Order payload, private SQLite, `.groxstate`, or a secret that makes CI an authority verifier.

## Squash merges

The private verification binding records the exact PR head/tree. After merge, the source-control platform can associate the final canonical commit with its pull request. The receipt is then consumed by the canonical source revision.

The design does not rely solely on feature-branch commit survival or squash-commit message formatting.

## Security boundary

Source provenance cannot:

- create a Mission;
- issue or alter a Mission Order;
- grant Repair permission;
- route or wake Crew;
- change capabilities;
- alter Tool Gateway policy;
- write repository files;
- approve its own source change;
- activate an A6 improvement proposal;
- turn public Git metadata into Commander authority.

A valid receipt proves that the private Vessel had a bounded authorization witness. It does not itself authorize an action.

## Optional external attestation

A future external consumer may justify wrapping the privacy-minimized public receipt in a signed in-toto/GitHub/Sigstore attestation bound to a canonical source digest.

That would add public cryptographic evidence about the public commitment and workflow identity. It would still not replace the private Mission/Order witness and is outside the current minimal implementation.
