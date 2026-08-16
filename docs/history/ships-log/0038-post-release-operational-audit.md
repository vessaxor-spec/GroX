# Ship's Log 0038 - Post-release Operational Audit

**Date:** 2026-08-16
**Status:** COMPLETE WITH EXTERNAL GOVERNANCE ITEM OPEN

GroX began its first comprehensive post-release Vessel operational audit from canonical `main@42639228526c1808c36b9b6798bd2c0964057174` after the `v0.7.1` release cycle closed.

## Native operational evidence

GorXu Mission `MSN-ac85d2c7192c` completed after the qualified digest-pinned workspace fallback was commissioned. The Mission ran at deterministic high risk, used `code-reviewer` as executor, and received independent verification PASS from `independent-verifier`.

Two earlier audit harness runs failed closed because the qualified workspace fallback had not been commissioned. Those red runs are retained as evidence of correct fail-closed behavior and of the commissioning requirement; they are not reclassified as product passes.

## Findings accepted for bounded hardening

- pin third-party GitHub Actions to immutable full commit SHAs;
- expand CI compatibility evidence from Python 3.11/3.12 to 3.11 through 3.14;
- upgrade pytest test/dev constraints beyond `PYSEC-2026-1845`;
- add bounded weekly Dependabot monitoring for GitHub Actions and Python dependencies;
- enforce action pinning and Python-matrix expectations through regression tests.

Static Ruff and Bandit findings were reviewed as advisory evidence. No mass formatting or speculative security refactor is included because that would increase blast radius without product-failure evidence.

## External governance finding

Canonical `main` was observed as unprotected and repository rulesets were empty. Repository administration authority is required to make PR/status-check enforcement non-bypassable. This is tracked separately and must not be represented as repaired until GitHub independently reports protection active.

## Authority boundary

This audit does not alter the GroX command relationship, Crew authority, Mission Orders, routing policy, persistence semantics, Tool Gateway authority, or Apex qualification boundary. GorXu remains the sole operational orchestrator and the operational company remains 82 Standing Crew with no retired Crew.

PR #19 candidate CI run `31938365523` passed Python 3.11 through 3.14 and Wheel bootstrap portability; exact final run `31938508389` re-proved all five gates. PR #19 then squash-merged as `53ecce335af79bfe9676f4467349fd78ebcdfb71`; its tree `087742f06877000fb5be9de80af64e11ddb21592` exactly matches the tested PR merge-candidate tree. Canonical `main` CI run `31938672912` passed all five gates. Issue #18 remains open solely for repository-level `main` protection.
