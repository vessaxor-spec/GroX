from pathlib import Path


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing expected {label}")
    return text.replace(old, new, 1)


# Program state.
p = Path("docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md")
text = p.read_text(encoding="utf-8")
text = replace_required(
    text,
    "**Status:** IN EXECUTION — STAGES 0-6 COMPLETE; PROVENANCE IMPLEMENTATION NEXT",
    "**Status:** IN EXECUTION — STAGES 0-6 + PROVENANCE IMPLEMENTATION COMPLETE; INTEGRATION GATE NEXT",
    "program status",
)
marker = "## Cross-workstream verification rules\n"
section = """### Provenance implementation — COMPLETE

**Issue:** #45

`src/grox/source_provenance.py` implements the Stage 6 ADAPT decision as a private authorization-evidence capability over the existing `StateStore` SQLite plane. It introduces no second state database or public Mission ledger.

Receipt issuance requires an existing explicit Repair Order carrying a mutating action and source scope that covers the requested receipt paths. Each receipt uses a random opaque public ID and 256-bit private nonce. Public metadata exposes only the v1 schema, opaque ID, domain-separated SHA-256 commitment, and coarse change class.

Private verification reopens the originating Mission and Orders, verifies current Repair/mutation authority, recomputes the commitment, rejects class downgrade, enforces normalized path coverage, prevents incompatible replay, and binds PASS to the exact PR head/tree. Missing private authority evidence is `UNKNOWN`, never PASS. Consumption requires that exact verified binding and records the canonical source revision.

Repository-wide mandatory provenance enforcement remains deliberately inactive until integrated qualification and a durable private Vessel can issue/verify the corresponding private receipts operationally. Public CI remains structural-only and receives no raw private authority state.

Preserved red evidence includes temporary harness run `32006665435`, which exposed a missing test-runtime installation, and source-provenance CI run `32007023966`, which killed 4/6 mutations while exposing two non-isolating mutation targets protected by redundant defenses. Neither result was bypassed. The harness and detector targets were corrected without weakening production behavior.

Exact-head green run `32007232455` then passed all five protected jobs with pytest **200 passed, 2 skipped, 354 subtests**, unittest **202 tests, 2 skipped**, all prior Post-Apex experiments/mutation suites green, and source-provenance mutation proof **6/6 KILLED**, zero survivors, exact source restoration.

Architecture: `docs/architecture/SOURCE_PROVENANCE.md`
Evidence: `docs/verification/SOURCE_PROVENANCE_MUTATION_MATRIX.md`
History: `docs/history/ships-log/0049-source-provenance-receipts-operational.md`

**Exit condition:** PASSED. Integrated Post-Apex Evolution Program 001 qualification is next.

"""
if section not in text:
    if marker not in text:
        raise SystemExit("program insertion marker missing")
    text = text.replace(marker, section + marker, 1)
p.write_text(text, encoding="utf-8")

# Roadmap state.
p = Path("docs/stewardship/ROADMAP.md")
text = p.read_text(encoding="utf-8")
text = replace_required(
    text,
    "and a source-backed privacy-safe Mission-to-source provenance design.",
    "a source-backed privacy-safe Mission-to-source provenance design, and an implemented private receipt/public commitment capability with continuous detector proof.",
    "roadmap current position",
)
text = replace_required(
    text,
    "- A6 longitudinal operational drift analysis is operational with frozen evidence bindings, fail-closed UNKNOWN semantics, first-class invariant regressions, routing concentration signals, and continuous 4/4 mutation proof.\n",
    "- A6 longitudinal operational drift analysis is operational with frozen evidence bindings, fail-closed UNKNOWN semantics, first-class invariant regressions, routing concentration signals, and continuous 4/4 mutation proof.\n- Privacy-safe source authorization receipts are implemented in the existing private StateStore plane with exact Repair/scope gating, nonce-bound public commitments, exact-head verification, replay/class-downgrade protection, and continuous 6/6 mutation proof.\n",
    "roadmap completed foundation",
)
text = replace_required(
    text,
    "8. **Bounded provenance implementation: NEXT.** Implement the minimal receipt/commitment mechanism in the existing private state plane, then prove forgery, replay, scope expansion, class downgrade, missing-witness and squash-linkage behavior before integration.\n9. **Integrated operational qualification.** Exercise all changed surfaces together and independently verify that no authority boundary widened before any release decision.\n",
    "8. **#45 — Bounded provenance implementation: COMPLETE.** Private receipts require existing Repair/mutation authority and bounded source scope; public commitments remain privacy-minimized; exact-head verification, replay/class-downgrade defenses, missing-witness UNKNOWN semantics, and 6/6 continuous detector mutations passed.\n9. **Integrated operational qualification: NEXT.** Exercise all changed surfaces together and independently verify that no authority boundary widened before any release decision.\n",
    "roadmap provenance stage",
)
p.write_text(text, encoding="utf-8")

# Progress tracker.
p = Path("docs/stewardship/progress-tracker.md")
text = p.read_text(encoding="utf-8")
text = replace_required(
    text,
    "**Current verified regression:** pytest **185 passed, 2 skipped, 351 subtests**; unittest **187 OK, 2 skipped**",
    "**Current verified regression:** pytest **200 passed, 2 skipped, 354 subtests**; unittest **202 OK, 2 skipped**",
    "progress regression count",
)
text = replace_required(
    text,
    "A separate bounded implementation is warranted before integrated operational qualification.\n",
    "The bounded provenance implementation is now complete and verified. Integrated operational qualification is next.\n",
    "progress Stage 6 conclusion",
)
marker = "## Known deliberate limits\n"
section = """## Post-Apex Evolution Program 001 — Provenance implementation

**Status: COMPLETE — PRIVATE SOURCE AUTHORIZATION RECEIPTS VERIFIED**

- receipt state is additive to the existing private `StateStore` SQLite plane; no second Mission ledger/database was created;
- issuance requires a real existing Repair Order with an explicit mutating action and source scope covering the requested receipt paths;
- public receipt metadata is restricted to schema version, opaque random receipt ID, nonce-bound SHA-256 commitment, and coarse change class;
- private verification rechecks the originating Mission/Orders, current Repair/mutation authority, commitment, change-class floor, normalized source scope, replay state, and exact PR head/tree binding;
- missing private authority evidence is `UNKNOWN`, not PASS;
- successful consumption requires the exact verified PR/head/tree and records the canonical source revision;
- public CI receives no Commander directive, private Mission/Order IDs, nonce, private SQLite, `.groxstate`, Crew evidence, or secret authority-verification key;
- repository-wide mandatory provenance enforcement remains deferred until integrated qualification and operational private receipt issuance are proven together;
- red source-provenance mutation run `32007023966` killed 4/6 and exposed two non-isolating targets protected by redundant defenses; repaired exact-head run `32007232455` passed all five jobs and killed **6/6** source-provenance mutations with zero survivors and exact restoration;
- exact-head regression at that gate: pytest **200 passed, 2 skipped, 354 subtests**, unittest **202 OK, 2 skipped**.

Architecture: `docs/architecture/SOURCE_PROVENANCE.md`.
Evidence: `docs/verification/SOURCE_PROVENANCE_MUTATION_MATRIX.md`.

Integrated Post-Apex Evolution Program 001 qualification is next.

"""
if section not in text:
    if marker not in text:
        raise SystemExit("progress insertion marker missing")
    text = text.replace(marker, section + marker, 1)
p.write_text(text, encoding="utf-8")
