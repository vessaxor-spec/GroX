# Selective Deep-Craft Crew Cognition

**Date:** 2026-08-18
**Status:** COMPLETE — CANONICAL SOURCE MERGED

After Mission Outcome Truthfulness closed, the Commander authorized the strongest repository-backed post-Apex candidate: give routed Standing Crew access to bounded Mission-relevant specialist craft plus existing bounded Crew memory, while preserving GorXu as sole operational orchestrator and keeping mutation authority outside the new cognition seam.

Issue #73 defined the bounded objective. PR #74 implemented and qualified it without creating A8, a new command layer, a release change, or a live-model claim.

## Canonical behavior

### Inspect-only selective specialist craft

- deep craft is selected only for Inspect Orders;
- only the routed Standing Crew member's canonical craft card is read;
- the default selector admits at most **6 sections / 4,500 characters**;
- `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` must fit in full when present or selection fails closed;
- remaining optional sections are selected deterministically by Mission relevance;
- the complete deep craft card is never injected by default;
- Verify, Repair, and Execute retain their existing task/memory context without unused deep craft;
- Inspect execution emits explicit `craft_selection` evidence with full-card SHA-256, selected headings/size, source revision, and freshness policy.

### Provider-neutral bounded Crew cognition

When a Crew cognition provider is separately supplied, an Inspect tour may consume:

- a sanitized copy of the sealed Mission Order envelope;
- selected specialist craft;
- existing bounded relevant Crew memory;
- observations returned only by governed actions already authorized by that Order.

The first seam permits only:

- `fs_list`;
- `fs_read`;
- `test_run`.

All requests still traverse the existing Mission Order and Tool Gateway. The provider receives no alternate filesystem, mutation, routing, verification, MCP, network, or desktop authority.

Default resource bounds are:

- **4** cognitive steps per tour;
- **1** cognitive `test_run` per tour;
- **8,000** observation characters;
- **4,000** final work-product characters.

Mutating actions and scope/root escape fail closed. Known recoverable provider or contract failure degrades only to the existing deterministic Inspect executor. Provider-facing Order, craft, memory, and observation structures are copied per call, so provider-local mutation cannot alter the sealed Order or executor-owned context.

Governed observations remain attributable evidence even if the provider later degrades. Raw file contents are not duplicated into persistent cognitive-observation evidence; bounded metadata and hashes are retained.

### Routing neutrality

Independent review found that new cognition/context evidence would otherwise increase Living Company evidence-quality scores merely by adding evidence kinds. The final implementation explicitly excludes `craft_selection` and Crew-cognition bookkeeping from performance-quality scoring. A regression proves identical operational evidence receives the same quality score with or without cognition metadata.

## Preserved red and review evidence

The implementation preserved and corrected discovered blockers rather than bypassing them:

1. synthetic test Crew initially lacked craft fixtures;
2. mandatory craft context could be starved by the character budget;
3. first cognition tests incorrectly treated persisted evidence JSON as an in-memory mapping;
4. provider-facing context was initially mutable by reference;
5. governed observations could be lost if the provider degraded after a read;
6. repeated cognitive `test_run` requests had no tour-level ceiling;
7. cognitive work product was initially unbounded;
8. deep craft was initially attached to every Order mode rather than only the qualified Inspect seam;
9. mandatory safety/operational sections could be truncated rather than failing closed;
10. craft attribution was initially nested weakly rather than emitted as explicit `craft_selection` evidence;
11. cognition/context bookkeeping could inflate Living Company routing history.

All eleven were corrected before final qualification.

## Qualification evidence

Canonical starting source: `main@8ffbee2f14e0e915e721835e9e84cc2289fc9661`.

Final implementation head: `db83c557e378e6e3a3471318b50e6b82a5d68641`.

Canonical exact-head CI run `32166921610` / run 232 passed all five required jobs:

- Wheel bootstrap portability;
- Regression / Python 3.11;
- Regression / Python 3.12;
- Regression / Python 3.13;
- Regression / Python 3.14.

Python 3.12 qualification recorded:

- Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **235 passed, 2 skipped, 354 subtests passed**;
- unittest **237 tests OK, 2 skipped**;
- critical invariant mutations **12/12 KILLED**;
- Vessel Health mutations **7/7 KILLED**;
- reconstitution mutations **9/9 KILLED**;
- operational drift mutations **4/4 KILLED**;
- source provenance mutations **6/6 KILLED**;
- integrated Post-Apex qualification PASS with `new_apex_stage=false`, `qualification_claim=false`, and `release_decision=false`.

Independent final review on the exact head returned **PASS — no remaining material blocker**.

PR #74 merged as canonical `main@8420b9cbe5ca046ded87c8feaec83eca7cfdc475` and closed issue #73 as completed. The canonical merge tree is `170bbfb9fe483b1faae362adc15ec944ca5c96c9`, exactly matching the CI-tested synthetic PR merge tree. A separate post-merge push run was not observed through the available GitHub interface and is therefore not claimed.

## Claim boundary

This milestone establishes a **canonical, CI-qualified, provider-neutral controlled read-only Standing Crew cognition seam** that consumes bounded selective specialist craft plus bounded Crew memory during Inspect tours.

It does **not** establish live model-backed Standing Crew. A live project/session or external model provider requires separate operational qualification before GroX may make that claim.

## Boundaries preserved

- Commander sovereignty unchanged;
- GorXu remains sole operational orchestrator;
- Mission Control remains subordinate advisory/policy;
- Mission Order + Tool Gateway remain authority-bearing execution boundaries;
- Verify remains independently deterministic in this first seam;
- Repair remains explicit mutation authority;
- Mission Graph authority and outcome-truthfulness semantics remain unchanged;
- Standing Crew remains **82**;
- package remains `0.8.0`;
- published release remains immutable `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`;
- no A8 or new Apex stage was created or implied.