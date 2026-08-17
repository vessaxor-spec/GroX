# Ship's Log — Entry 0048

**Date:** 2026-08-17
**Milestone:** Mission-to-source provenance research completed

## Mission

Determine whether GroX can link a consequential public source revision back to the private Commander-authorized Mission/Order that enabled it without publishing private operational state or creating a second authority ledger.

## Decision

**ADAPT.**

The Vessel will keep authorization truth in its existing private operational evidence plane. The minimal proposed bridge is a private authorization receipt carrying a fresh high-entropy nonce and bounded scope, plus a public opaque receipt identifier, SHA-256 commitment, and coarse source-change class.

Public CI may verify syntax and required presence only. Independent verification with access to the private witness must recompute the commitment, verify the originating Mission/Order and scope, prevent replay or class downgrade, and bind successful consumption to the resulting source revision.

The private nonce, Commander directive, Mission/Order identifiers, Crew evidence, SQLite, `.groxstate`, credentials, and sensitive operational content remain private.

## External evidence

The research used current primary specifications and platform documentation from SLSA v1.2 Source Track, the in-toto Attestation Framework, and GitHub's source/attestation APIs. These support digest-bound provenance and source-revision verification but do not replace GroX's private Commander authority model.

GitHub/Sigstore custom attestations remain optional public hardening if a real external consumer later needs portable cryptographic evidence. They are not required for the minimal design and cannot by themselves prove the private Commander authorization fact.

## Next gate

Implement the bounded receipt/commitment design separately, prove privacy, replay resistance, exact-scope verification and squash linkage, then include it in the integrated post-evolution Mission.

No command, Crew, Tool Gateway, persistence or mutation authority changes as a result of the research itself.
