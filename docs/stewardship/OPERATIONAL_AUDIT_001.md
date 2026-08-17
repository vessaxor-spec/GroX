# Operational Audit 001 - Post-release Vessel readiness

**Date:** 2026-08-16
**Baseline:** `v0.7.1` / `main@42639228526c1808c36b9b6798bd2c0964057174`
**Mission class:** Inspect with bounded reversible hardening

## Objective

Exercise the released Vessel in a real operational audit and identify evidence-backed weaknesses that affect long-term daily use without widening authority or inventing a new qualification stage.

## Native Mission evidence

A commissioned audit workspace completed native GorXu Mission `MSN-ac85d2c7192c` with deterministic high risk, executor `code-reviewer`, and independent verification by `independent-verifier`. GorXu inspected 207 files and the Mission test path returned zero.

The initial audit harness produced two preserved red runs because the qualified digest-pinned Docker workspace fallback had not yet been commissioned. This was an environment commissioning failure rather than a product bypass; the run failed closed. After commissioning the exact qualified Alpine digest, the native Mission completed successfully.

## Proven findings

### F-001 - canonical main is not protected

**Severity:** High operational governance

GitHub reports canonical `main` as `protected: false`, and the repository currently has no rulesets. Direct repository settings therefore do not enforce the PR/CI path even though permanent CI exists.

This cannot be repaired from normal repository source or the least-privilege Actions token. Repository administration authority is required. Issue #18 tracks the external settings action. Until protection is independently verified, CI is evidence but not an enforced merge boundary.

### F-002 - GitHub Actions used mutable major tags

**Severity:** Medium supply-chain

Permanent CI referenced `actions/checkout@v5` and `actions/setup-python@v6`. The audit hardens these to the exact full commit SHAs already proven by successful GroX CI runs and adds an executable contract preventing mutable external action references from returning.

### F-003 - dependency monitoring was absent

**Severity:** Medium maintenance

No Dependabot configuration existed. A bounded weekly configuration now monitors both GitHub Actions and Python dependencies without auto-merge or authority widening.

### F-004 - CI did not cover the full claimed Python support range

**Severity:** Medium compatibility

Package metadata claims Python `>=3.11`, while canonical CI covered only 3.11 and 3.12. The audit expands the regression matrix through Python 3.14 and requires all supported-version jobs to pass before this hardening can merge.

### F-005 - pytest test dependency was held on a vulnerable major line

**Severity:** Medium dependency security

`pip-audit` identified `PYSEC-2026-1845` against pytest 8.4.2, with a fixed version of 9.0.3. GroX constrained test/dev environments to `pytest>=8,<9`, preventing resolution to the fixed release. The audit changes the constraint to `pytest>=9.0.3,<10` and re-runs the complete regression suite across the supported Python matrix.

### F-006 - static-quality debt exists but does not justify broad mutation

**Severity:** Low / tracked debt

Advisory Ruff inspection reported 142 legacy style/import/modernization findings. Bandit reported 29 low/medium findings and no high-severity finding; most are expected surfaces in the governed subprocess, workspace, MCP, persistence, and network tooling paths. Broad exception handling at the Pilot boundary is deliberate containment behavior. No mass formatting or speculative security refactor is authorized by this audit.

## Preserved boundaries

- Commander authority is unchanged.
- GorXu remains the sole operational orchestrator.
- Standing Crew remains 82 with source-defined operational Crew only.
- Inspect/Repair separation remains mandatory.
- No Crew, routing, persistence, Mission Order, Gateway, or authority semantics are widened.
- Historical qualification branches remain preserved because they contain red-to-green evidence.
- Private SQLite and `.groxstate` operational state remain outside public Git.

## Completion criteria

This audit closes only when the final candidate passes permanent CI on Python 3.11, 3.12, 3.13, and 3.14 plus wheel bootstrap portability, the temporary audit workflow is absent from the net tree, documentation is reconciled, and the final merged `main` tree is independently re-verified. Repository-level `main` protection remains an externally gated settings item until GitHub reports it active.

## Completion evidence

**Status: COMPLETE WITH EXTERNAL GOVERNANCE ITEM OPEN**

- exact final PR #19 CI run `31938508389`: **SUCCESS** across Python 3.11, 3.12, 3.13, 3.14, and Wheel bootstrap portability;
- PR #19 squash merge: `53ecce335af79bfe9676f4467349fd78ebcdfb71`;
- the tested PR merge candidate and canonical squash merge share tree `087742f06877000fb5be9de80af64e11ddb21592`, proving zero tree drift;
- canonical `main` CI run `31938672912`: **SUCCESS** across all five permanent gates;
- issue #18 remains the sole externally gated repository-administration item because `main` protection requires GitHub repository administration authority.

PR #19 candidate CI run `31938365523` passed all five permanent gates: Python 3.11, 3.12, 3.13, 3.14, and Wheel bootstrap portability. Python 3.12 recorded **131 pytest passed, 2 skipped** and **133 unittest OK, 2 skipped** with pytest 9.1.1.

The net candidate contains only the permanent CI workflow; both temporary Audit 001 workflow harnesses have been removed. Issue #18 is the sole externally gated repository-administration finding and remains open until `main` protection is independently verified.
