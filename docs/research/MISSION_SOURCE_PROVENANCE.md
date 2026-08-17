# Mission-to-Source Provenance Research

**Stage:** Post-Apex Operational Evolution Program 001 — Stage 6  
**Issue:** #31  
**Date:** 2026-08-17  
**Decision:** **ADAPT**

## Executive decision

GroX should adopt the **principle** of verifiable source provenance but adapt it to the Vessel's privacy and authority model rather than publishing raw Mission state or importing a generic supply-chain attestation system as a new source of authority.

The minimal GroX-native design is a **private authorization receipt with a privacy-preserving public commitment**:

1. an authorized private Mission / Mission Order produces a private receipt in the existing operational evidence plane;
2. the receipt contains a fresh high-entropy nonce plus bounded authorization facts;
3. GroX publishes only an opaque receipt identifier, a versioned SHA-256 commitment, and a coarse change class in the pull request;
4. an independent verifier with access to private Vessel state recomputes the commitment and verifies that the public claim corresponds to a real authorized private record whose scope covers the proposed change;
5. public CI validates syntax and structural presence only; it never receives the nonce, Commander directive, raw Mission content, private SQLite, or other sensitive evidence;
6. the final source revision is mapped back to its pull request using the source-control platform's commit-to-PR association, preserving the chain across squash merges and branch deletion.

This creates a verifiable chain without creating a second Mission ledger:

**Commander authorization → private Mission / Order → private receipt → public commitment on PR → protected CI + independent verification → merge → source revision → associated PR → commitment → private receipt**

The public commitment is **evidence of a private witness**, not authority. Mission Orders and the normal GroX authority path remain authoritative.

## Research boundary

The problem is not ordinary build provenance. GroX already has Git history, protected pull requests, CI, and private Mission evidence. The missing property is a privacy-safe bridge between two evidence planes:

- **private operational authority** — Commander intent, GorXu decisions, Mission Orders, evidence and verifier records;
- **public source-control evidence** — pull requests, checks, reviews, merge state, commit/tree identity and history.

Publishing raw private Mission state would violate the Vessel's persistence/privacy boundary. Keeping all linkage private would make public source revisions impossible to relate back to authorization. The design therefore needs a public commitment that leaks as little as practical while remaining independently checkable with the private witness.

## Current authoritative foundations

GroX already provides the important prerequisites:

- source revisions are cryptographically identified by Git commit and tree IDs;
- canonical `main` is protected by pull-request-only governance and required CI checks;
- Mission, Order, Evidence and evaluation state live in existing private SQLite rather than public Git;
- Mission Orders define bounded authority and do not derive authority from Git metadata;
- independent verification is an existing Vessel concept;
- Ship's Log and stewardship records are explanatory history, not a parallel operational authority store.

The provenance mechanism should connect these systems, not replace them.

## External standards and current platform evidence

### SLSA Source Track

SLSA v1.2 defines source provenance as information about how a source revision came to exist and the change-management process used to create it. The Source Track explicitly treats a source revision as a logically immutable source snapshot and, at higher source levels, expects reliable history, technical controls, and provenance evidence. SLSA deliberately leaves detailed source-provenance attestation formats to the source-control system because different systems need different evidence shapes.

This supports GroX's direction: bind evidence to the resulting source revision and preserve the repository's own change-management controls rather than forcing build-provenance semantics onto Commander authorization.

Primary references:

- https://slsa.dev/spec/v1.2/source-requirements
- https://slsa.dev/spec/v1.2/provenance
- https://slsa.dev/spec/v1.2/verifying-source

### in-toto Attestation Framework

The in-toto Statement v1 model binds one or more immutable subjects, identified by digest, to a typed predicate. This is a useful interoperability model for an optional future public attestation because a GroX source revision can be the immutable subject while a custom predicate can carry privacy-minimized provenance metadata.

Primary reference:

- https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md

### GitHub artifact attestations

GitHub's current `actions/attest` supports custom predicate types and content in addition to build provenance and SBOM attestations. GitHub signs attestations through Sigstore and associates them with digest-identified subjects. GitHub also exposes attestation retrieval by subject digest and custom predicate type.

This is technically suitable as **optional public cryptographic hardening**, but not as GroX's first or only authorization witness:

- a GitHub/Sigstore attestation proves that an authorized workflow identity signed a public predicate; it does not by itself prove the existence or scope of the private Commander-authorized Mission;
- generating attestations adds OIDC/attestation workflow permissions and a platform dependency;
- GitHub documents that attestations can be deleted, so the GitHub attestation service should not become the sole durable authority record.

Primary references:

- https://github.com/actions/attest
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations
- https://docs.github.com/en/rest/repos/attestations

### GitHub squash-merge and source-to-PR linkage

Squash merging changes the commit topology, so provenance must not depend on a feature-branch commit surviving unchanged. GitHub provides an API to list pull requests associated with a commit. This gives the final canonical source revision a platform-native route back to the pull request that introduced it, even after the source branch is deleted.

The squash commit message may also contain PR information depending on repository settings, but that is presentation metadata and should not be the only lookup mechanism.

Primary references:

- https://docs.github.com/en/rest/commits/commits#list-pull-requests-associated-with-a-commit
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests

## Options considered

### Option A — Publish Mission IDs directly

**Decision: REJECT.**

Advantages:

- simple;
- easy to search;
- no new cryptographic mechanism.

Problems:

- exposes internal operational identifiers;
- creates a stable correlation handle across private and public records;
- may leak Mission frequency/timing and allow unwanted inference;
- a string in a PR proves only that somebody typed the string.

### Option B — Publish a raw hash of the Commander directive or Mission payload

**Decision: REJECT.**

A hash hides the exact text only when the preimage has sufficient entropy. Commander directives, Mission titles, Crew names, common scopes and status fields are often low-entropy or guessable. An observer could hash candidate phrases and test guesses. A raw hash therefore does not meet the privacy requirement.

### Option C — HMAC over private Mission state

**Decision: REJECT AS THE PRIMARY DESIGN.**

HMAC prevents public offline guessing without the secret key, but public CI could not verify it without receiving a secret. Distributing such a key to GitHub Actions would widen the trust and secret-management surface for no necessary benefit. The private verifier already has access to the private witness and can recompute a nonce-based commitment without giving CI private verification capability.

### Option D — Zero-knowledge proof of Mission authorization

**Decision: REJECT FOR CURRENT NEED.**

A zero-knowledge circuit could theoretically prove possession of a private authorization witness without revealing it. The engineering, key/circuit lifecycle, auditability and long-term maintenance cost are disproportionate to the present requirement. GroX can achieve the required privacy and traceability with a much smaller commitment-and-witness design.

### Option E — GitHub/Sigstore custom attestation as the sole record

**Decision: REJECT AS SOLE AUTHORITY; HARVEST AS OPTIONAL HARDENING.**

Custom attestations provide a strong signed public envelope around digest-bound metadata, but the workflow cannot truthfully attest to private Commander authorization unless it receives trusted evidence of that authorization. Giving the public workflow raw private state violates the boundary. The attestation also remains a platform-hosted object whose lifecycle is not the Vessel's private authority ledger.

### Option F — Private receipt + public nonce-bound commitment

**Decision: ADAPT.**

This is the smallest design that satisfies the privacy, verification, squash-survival and no-duplicate-ledger requirements.

## Proposed GroX receipt model

### Private authorization receipt

A receipt is stored inside the **existing private operational evidence plane**. It is not a public Git file and not a second standalone database.

Recommended fields:

```json
{
  "schema": "grox-source-receipt-v1",
  "receipt_id": "SRC-<random opaque id>",
  "mission_id": "<private Mission id>",
  "order_ids": ["<private Order id>"],
  "change_class": "runtime | stewardship | research",
  "authorized_scope": {
    "paths": ["<normalized path or bounded prefix>"],
    "operation": "create | update | delete | mixed"
  },
  "authority_state": "authorized",
  "nonce": "<at least 128 bits cryptographically random>",
  "issued_at": "<private timestamp>",
  "consumed_by": null,
  "revoked_at": null
}
```

Only fields needed to prove the authorization relation belong in the receipt. Commander directive text, free-form Mission reasoning, Crew notes, credentials and raw evidence should not be copied into it.

### Canonical private payload

Before commitment, the private receipt payload must be canonicalized deterministically. Recommended v1 rules:

- UTF-8 JSON;
- fixed schema version;
- sorted object keys;
- no insignificant whitespace;
- normalized repository-relative POSIX paths;
- ordered lists where order is semantically meaningful; otherwise explicit sorting;
- timestamps, if included in the commitment, use one normalized UTC representation.

Version the canonicalization as part of `grox-source-receipt-v1` so future readers know exactly what bytes were committed.

### Public commitment

Recommended construction:

```text
commitment = SHA256(
    "grox-source-receipt-v1\0" ||
    nonce_bytes ||
    canonical_private_receipt_without_nonce
)
```

Properties:

- the private nonce makes dictionary testing against low-entropy Mission information impractical when the nonce remains private and sufficiently random;
- the schema/domain-separation prefix prevents the digest from being ambiguously reused as a different GroX object type;
- the commitment is deterministic for the same witness and nonce;
- the commitment itself does not reveal the private fields.

The nonce must never be published in the PR. Publishing both the nonce and digest would restore offline guessability of low-entropy fields.

## Public PR metadata

For a consequential source change, publish only a compact block such as:

```text
GroX-Source-Provenance: v1
GroX-Authorization-Receipt: SRC-7YQ4N2K8...
GroX-Authorization-Commitment: sha256:<64 hex chars>
GroX-Change-Class: runtime
```

The receipt ID must be independently random/opaque and must not encode Mission IDs, Crew identity, timestamp, Division, risk or scope.

For multiple contributing Missions, include multiple complete receipt blocks. Do not aggregate private Missions into one public identifier unless a separately authorized parent Mission truly owns the combined source scope.

## Change classes

### Runtime

Source that changes executable behavior, authority enforcement, persistence behavior, routing, Crew capability interpretation, tooling, verification behavior or other runtime semantics.

Recommended policy: receipt **required**.

### Stewardship

Canonical documentation, Roadmap/Progress Tracker, release bookkeeping and other project-state synchronization that does not itself change runtime semantics.

Recommended policy: receipt **required when the stewardship mutation is consequential or records a Commander-authorized project-state decision**. Mechanical follow-up documentation tied to a verified runtime PR may reference that same authorized change only when its private scope explicitly includes the stewardship paths.

### Research

Research documents, design studies and experiments that do not activate runtime behavior.

Recommended policy: receipt **optional at first**, because research does not itself grant mutation authority. If research changes canonical policy/architecture rather than merely recording analysis, classify it as stewardship for provenance purposes.

The implementation should classify conservatively: ambiguity moves upward to the stricter class.

## Verification model

### Public CI: structural verification only

CI may safely verify:

- provenance block exists when required by path/change classification;
- schema version is known;
- receipt ID syntax is opaque and well formed;
- commitment is exactly `sha256:` plus 64 lowercase hexadecimal characters;
- change class is valid;
- no obvious private fields such as Mission IDs, Order IDs, nonce or Commander directive are present in the public block.

CI **must not** claim that the receipt is genuinely authorized because it has no private witness.

CI receives no private SQLite, `.groxstate`, nonce, Mission payload or secret verification key.

### Independent private verifier: authorization verification

Before merge, the verifier should:

1. parse the public provenance block from the PR metadata supplied as evidence;
2. locate the private receipt by opaque `receipt_id` in existing Vessel state;
3. ensure it is not revoked or already consumed by another incompatible change;
4. verify its Mission/Order still exists and represents a valid authorized mutation path;
5. recompute the SHA-256 commitment using the private nonce and canonical receipt payload;
6. compare it in constant-time style with the public commitment;
7. inspect the actual PR changed paths/operation types and verify they are a subset of the private authorized scope;
8. verify the declared public change class is not weaker than the private class;
9. record a private PASS/FAIL evidence item with the PR number and exact PR head/tree identity;
10. on successful canonical merge, mark the receipt consumed by the resulting source revision and PR association.

The verifier may publish a minimal public statement that the opaque receipt/commitment was verified, but it must not reveal the witness.

A failure blocks provenance verification. It does not mutate the receipt, widen scope or automatically issue a replacement authorization.

## Replay and consumption rules

A receipt must not become a reusable bearer token.

Recommended v1 rules:

- receipt may bind to at most one logical PR/change set unless explicitly issued as a multi-PR authorization;
- first private verification records the PR identity but does not yet consume the receipt;
- changes to the PR head after verification invalidate the prior source-scope verification and require re-verification;
- successful merge marks `consumed_by` with repository identity, PR number and canonical merge commit/tree;
- presenting the same receipt on an unrelated PR fails;
- abandoned PR receipts may be revoked or remain unused; they do not authorize future work automatically.

## Scope representation

The private receipt should authorize **what may change**, not merely state that "some code change" was approved.

Minimal v1 scope can be repository-relative path patterns plus operation class. Examples:

```json
{
  "paths": [
    "src/grox/provenance.py",
    "tests/unit/test_provenance.py",
    "docs/architecture/SOURCE_PROVENANCE.md"
  ],
  "operation": "mixed"
}
```

For larger authorized workstreams, bounded prefixes may be used, but broad patterns such as `**` should require explicit justification because they reduce the strength of scope verification.

Path scope is intentionally narrower than semantic intent. It is mechanically verifiable and does not require exposing the private directive. Semantic correctness remains part of ordinary review and verification.

## Squash-merge and branch-deletion behavior

The public provenance block lives on the pull request, which survives branch deletion. After merge:

1. canonical `main` identifies the final source revision by Git commit SHA/tree;
2. GitHub's commit-to-associated-PR endpoint maps that source revision back to the merged PR;
3. the PR body exposes the opaque receipt/commitment;
4. the private evidence plane maps that receipt to the authorized Mission/Order witness;
5. private verification evidence records the exact PR head/tree that was checked and the final canonical revision that consumed the receipt.

Do not depend solely on feature-branch commits or the squash commit message.

## Multiple Missions and multiple receipts

When multiple Commander-authorized Missions contribute to one PR:

- each private authorization remains independently attributable;
- public metadata contains one receipt/commitment block per authorization;
- each changed path must be covered by at least one private receipt;
- overlap is allowed but does not combine or widen authority;
- a receipt cannot inherit scope from another receipt merely because both are listed on the same PR.

This preserves deny-wins semantics across provenance: missing coverage remains missing coverage.

## Threat model

| Threat | Required defense |
|---|---|
| Fabricated provenance block | Private verifier must find the receipt and recompute the commitment. |
| Guessing private Mission text from public digest | Fresh private high-entropy nonce; never publish the nonce. |
| Receipt ID leaks Mission semantics | Random opaque receipt IDs with no embedded operational data. |
| Receipt replay on another PR | Private PR binding plus one-change consumption state. |
| PR scope expands after verification | Exact-head/tree binding; head change requires re-verification. |
| Broad scope silently authorizes unrelated files | Narrow normalized path scope; ambiguous/broad scope fails conservative review. |
| Lower public change class bypasses stricter rule | Verifier compares public class against private class and rejects downgrade. |
| Public CI compromised | CI has no private witness/nonce and therefore cannot mint a valid private receipt. |
| Private state compromised | Treat as authority-plane compromise; commitments alone cannot recover trust. Restore from stronger verified state/evidence. |
| Private state lost | Public commitment remains evidence that a witness once existed but cannot prove its contents; provenance becomes unverifiable/UNKNOWN, not PASS. |
| Squash merge loses branch commit IDs | Bind verification to PR head/tree and recover final source→PR via source-control association API. |
| Branch deleted | PR and canonical commit association remain the public linkage. |
| Multiple Mission scopes partially cover PR | Require complete path coverage across independent receipts. |
| Documentation-only change masquerades as research | Conservative change classification; canonical policy/state mutations are stewardship. |
| Attestation platform object deleted | Private receipt/evidence remains authoritative; optional attestation is additional public evidence only. |
| Provenance metadata treated as permission | Explicit code/doc rule: receipt proves prior authorization; it never grants authority. |

## Privacy analysis

### Public by design

- schema version;
- random receipt ID;
- commitment digest;
- coarse change class;
- PR/revision identity already public in GitHub.

### Private by design

- Commander directive;
- Mission and Order IDs;
- nonce;
- precise authorized paths if their disclosure is sensitive before the PR itself reveals them;
- Crew identities/tour notes;
- risk reasoning;
- operational timestamps beyond ordinary public Git events;
- raw evidence;
- SQLite and `.groxstate` contents;
- credentials/secrets.

### Timing leakage

The public PR already reveals when a source change is proposed. The receipt ID must not embed private issuance time. Private `issued_at` need not be published. This prevents the provenance layer from adding a new fine-grained Mission-timing signal beyond the Git event itself.

## Failure semantics

The system must fail closed without converting provenance into a new Commander escalation source for ordinary defects.

Suggested outcomes:

- `PASS` — private witness exists, commitment matches, scope covers exact PR head, classification valid, receipt usable;
- `FAIL` — forged/mismatched commitment, scope gap, replay, downgrade, revoked receipt or invalid authorization;
- `UNKNOWN` — private witness unavailable, private store unavailable, source association unavailable, unsupported schema or incomplete evidence.

`UNKNOWN` is not equivalent to authorization. GorXu may investigate/reconstitute ordinary evidence gaps through normal bounded authority. Critical integrity compromise or an irreversible decision returns to the Commander.

## Optional public cryptographic attestation

After the minimal receipt mechanism proves useful, GroX may optionally attest a tiny public source-provenance artifact such as:

```json
{
  "schema": "grox-public-source-receipt-v1",
  "repository": "vessaxor-spec/GroX",
  "commit": "<canonical source SHA>",
  "pull_request": 123,
  "authorization_receipts": [
    {
      "receipt_id": "SRC-...",
      "commitment": "sha256:...",
      "change_class": "runtime"
    }
  ]
}
```

That artifact can be the digest-bound subject or predicate of an in-toto/GitHub custom attestation. This would prove that a particular GitHub workflow cryptographically signed the public receipt for a specific source revision.

It **still would not replace private authorization verification**. The signed public object says, in effect, "this workflow observed this public commitment for this source revision," not "the Commander authorized these private semantics."

Recommendation: defer this until there is a concrete external consumer or portability requirement. Adding OIDC/attestation permissions before a consumer exists would increase complexity without strengthening the private authority fact.

## Minimal implementation proposal

Research supports a separate bounded implementation stage.

### Runtime additions

1. `src/grox/source_provenance.py`
   - receipt dataclass/schema;
   - canonicalization;
   - `secrets`-based nonce and opaque ID generation;
   - SHA-256 commitment;
   - scope/path normalization and coverage checks;
   - public block parser/renderer;
   - private verification service.

2. Existing private SQLite plane
   - one additive table such as `source_authorization_receipts` in the existing state database;
   - foreign attribution to private Mission/Order IDs;
   - unique `receipt_id` and commitment;
   - private nonce;
   - scope/class/status/consumption fields;
   - no separate database or public ledger.

3. Tests
   - canonicalization stability;
   - nonce-bound dictionary resistance at the interface level (same private payload + different nonces gives distinct commitments);
   - forged commitment rejection;
   - receipt replay rejection;
   - head/scope change invalidation;
   - path traversal/normalization defenses;
   - multi-receipt complete coverage;
   - change-class downgrade rejection;
   - missing private state => UNKNOWN;
   - public renderer never emits private fields;
   - receipt cannot activate or mutate source;
   - exact independent-verifier path.

4. Public CI contract
   - structural PR provenance lint only;
   - do not place private state or secret verification material in Actions.

5. Documentation
   - architecture/source-provenance contract;
   - privacy boundary;
   - verification and recovery semantics;
   - Ship's Log and Progress Tracker only after implementation evidence exists.

### Implementation exit gate

A bounded test PR should demonstrate:

- receipt issued from an actually authorized private Mission/Order;
- public commitment contains no private witness data;
- exact PR head scope verifies privately;
- forged/replayed/out-of-scope/downgraded receipts fail;
- absent private witness is UNKNOWN;
- squash merge resolves canonical source revision back to the correct PR and receipt;
- private receipt becomes consumed by the canonical source revision after merge evidence is available;
- public CI never accesses private raw operational state;
- no provenance code can grant Repair permission, change Mission authority, alter Crew capability, route Crew, or self-activate a change.

## Decision summary

**ADAPT.**

Harvest the source-provenance and digest-bound attestation principles from SLSA, in-toto and GitHub, but keep Commander authorization truth in GroX's existing private operational evidence plane.

Implement a **private nonce-bound authorization receipt + public opaque commitment + independent private verification** as the minimal native solution.

Do **not**:

- publish Mission/Order identifiers or raw private state;
- hash low-entropy Commander/Mission text without a private nonce;
- give public CI access to the private witness or a secret that turns it into an authority verifier;
- make a GitHub/Sigstore attestation the sole authority record;
- create a second Mission ledger;
- treat provenance metadata as permission;
- introduce zero-knowledge infrastructure without a demonstrated need.

Optional custom signed attestations may be layered on later if an external consumer needs portable public cryptographic evidence.
