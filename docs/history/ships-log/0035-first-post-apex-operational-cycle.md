# Ship's Log Entry 0035 - First Post-Apex Operational Cycle

**Date:** 2026-08-16
**Pilot:** GorXu
**Vessel:** GroX
**State:** Apex-qualified; first real operational evidence converted into bounded hardening

## Mission

The Commander authorized GroX to leave the synthetic qualification path and begin real post-Apex operation. The first operational objective was a bounded Inspect Mission against canonical source: determine whether the released Apex-qualified Vessel could reconstitute, execute its regression path, and return independently verified readiness evidence without source mutation.

## Red operational evidence

Run `31919127956` used a normal non-editable Python installation. The old CLI derived its Vessel root from the installed module location, so it came online under site-packages with **0 Standing Crew** and returned the bounded routing exception `No standing Crew covers required capabilities: ['repo_read']`. GorXu did not invent Crew or widen authority. The failure was preserved as evidence.

## Green operational evidence

Run `31919157280` repeated the objective through the documented editable-source bootstrap on exact canonical source. GroX reconstituted **82 Standing Crew** and completed Mission `MSN-8a86f094509b`:

- mode: Inspect;
- risk: medium;
- executor: `code-reviewer`;
- inventory: 198 files;
- regression return code: 0;
- independent verifier: `independent-verifier`;
- verification: PASS;
- Mission status: completed;
- source mutation: none.

## Bounded repair

The evidence justified two operational changes only:

1. portable, explicit, fail-closed Vessel-root binding;
2. persistent least-privilege CI on pull requests and `main`.

Current source package advances to `0.7.1`. Vessel discovery now prefers explicit `GROX_VESSEL_ROOT`, then current-checkout ancestry, then editable source-module ancestry. A wheel-installed CLI may operate from a valid checkout or explicit binding; outside any bound Vessel it refuses to start rather than fabricating an empty company.

Canonical CI uses GitHub-hosted Ubuntu 24.04, Python 3.11 and 3.12 regression jobs, the existing digest-pinned A5 Docker workspace fallback, and an independent non-editable wheel-bootstrap job. Workflow permissions are read-only for repository contents.

CI run `31919583794` passed all three jobs. Python 3.12 recorded **126 pytest passed, 2 skipped** and **128 unittest OK, 2 skipped**. The wheel job independently proved checkout binding, explicit environment binding, and fail-closed unbound behavior.

## Authority result

No Commander authority, GorXu orchestration authority, Division/Crew structure, routing policy, persistence schema, or capability grant was widened. Apex remains a regression boundary, not inherited permission for future power.
