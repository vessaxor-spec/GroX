# Ship's Log — Entry 0032

**Date:** 2026-08-15
**Pilot:** GorXu
**Milestone:** A7 entry hardening independently verified

An external independent audit of canonical `main@481d83e422119d94759685560b61bfccd9e532da` returned PASS WITH CONDITIONS for entry into the final A7 Apex Qualification Gauntlet. The audit independently reproduced the A6 private-state hashes, SQLite integrity, 82-Crew state, preserved Mission `MSN-f09179526ad7`, evaluation case `EVC-10573b245e54`, exact replay trace, zero invariants, verifier separation, authority/risk controls, secret containment, and denial of A6 proposal activation. No Critical finding invalidated A6.

Before A7, the Vessel closed the two findings that could weaken recovery or issued authority. Snapshot restore now verifies source/state compatibility: exact source matches are accepted, state from a proven ancestor source requires explicit `allow_ancestor=True`, and unrelated or unprovable source histories fail closed. Mission Orders now snapshot authority-bearing fields at construction, deep-copy operation parameters, and seal nested grants when persisted or first presented to the Tool Gateway so ordinary post-issuance mutation cannot widen scope, forbidden actions, verification requirements, capabilities, network origins, or MCP grants.

The external audit's stewardship drift finding was accepted for reconciliation. Its dual-routing observation was not used as justification for an unproven routing redesign: a local removal experiment changed established domain-routing behavior, so routing-path consistency remains an explicit A7 gauntlet condition. The absence of the controlled A6 routing rows from the preserved live-Mission snapshot remains an observation rather than a fabricated retrofit; controlled evaluation evidence is still distinct from production policy activation.

Local pre-publication regression passed **107 pytest tests** and **107 unittest tests**. Independent GitHub-hosted canary run `31880124909` remained red because the fresh Ubuntu runner had neither usable user-namespace isolation nor the pre-provisioned A5 Docker workspace image; the Vessel failed closed before the new hardening canary executed. That red result was preserved rather than bypassed.

The verifier path was then commissioned with the same digest-pinned A5 workspace fallback already inside the qualified boundary. Independent run `31880261811` checked out exact code head `2bec6a61dfe4c4cbae26f4ae6a0ddbc93248d6ce` on Ubuntu 24.04 / Python 3.12.13, pulled the pinned Alpine workspace digest, passed **105 pytest tests with 2 environment-dependent browser skips**, ran **107 unittest tests OK with 2 skips**, and closed with exact output `A7_ENTRY_HARDENING_CANARY_FINDINGS=`.

The hardening advances the patch stewardship version to **0.6.1**. A final exact-head verification remains a merge gate after stewardship-only finalization. GorXu remains **NOT YET APEX**; this work strengthens the starting line for A7 and does not execute or pass the Apex gauntlet itself.
