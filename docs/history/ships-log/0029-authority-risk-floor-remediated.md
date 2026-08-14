# Ship's Log — Entry 0029

**Date:** 2026-08-14  
**Pilot:** GorXu  
**Milestone:** Bounded authority and risk-floor remediation

A read-only verifier audit identified an unsafe ambiguity in deterministic Mission interpretation: natural-language Repair words could previously infer Repair mode, and an explicit risk argument could replace rather than raise the deterministic floor.

The bounded remediation closes both paths without changing the Vessel's command spine. Natural-language words such as `fix`, `write`, `change`, `modify`, and `repair` are now advisory hints only. They cannot grant Repair mode or mutation actions. Filesystem and MCP mutation grants are rejected at Mission Order, Mission Graph, and Tool Gateway boundaries unless the Mission is explicitly authorized as Repair.

Risk is now treated as a floor: deterministic assessment is computed first, explicit risk may raise but not lower it, and GorXu's cognitive reconciliation may raise it further. A lower-risk Commander override is deliberately not hidden inside an ordinary `risk=low` argument; any future override mechanism must be separate and auditable.

Exception handling was also tightened. Known routing, policy, timeout, and recoverable operational failures remain governed domain outcomes. Unexpected programming defects are allowed to reach GorXu's outer containment boundary, where they are recorded distinctly as `unexpected_defect` evidence with exception type, traceback, and execution context rather than being disguised as ordinary replanning events.

Crew dossier loading no longer requires mutation of live SQLite state, and test/install ergonomics now include optional pytest extras plus `src` path configuration while retaining zero mandatory runtime dependencies.

GitHub-hosted remediation qualification run `31845028070` on Ubuntu 24.04 / Python 3.12 passed the complete unittest suite: **83 tests, 2 environment-dependent browser skips**. Pytest independently reported **81 passed, 2 skipped**. The A5 workspace fallback image was commissioned by its existing digest before the green run; the initial fail-closed run without that image was retained as evidence rather than bypassed.

GroX adopts **A1–A5 as its pre-1.0 minor stewardship series**, so the package version is aligned to **0.5.0**. This version number records the qualified Vessel maturity line; it does not declare Apex completion. A6 remains the active Apex stage.

The remediation remains on `remediation/authority-risk-floor` for independent verifier review before merge to `main`.
