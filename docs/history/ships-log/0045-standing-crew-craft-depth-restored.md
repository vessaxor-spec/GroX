# Ship's Log 0045 — Standing Crew Craft Depth Restored

**Date:** 2026-08-16

**Mission:** Restore Standing Crew craft depth

**Mode:** Bounded Repair

## Commander intent

The Commander identified verified drift in the Standing Company: GroX had 82 operational dossiers, but most dossiers were intentionally compact routing and capability metadata and had become the de facto representation of specialist identity. That left deep Standing Crew craft implicit rather than canonical.

The order was to end the placeholder-roster condition without changing the command spine, weakening authority controls, recruiting an orchestrator-class Crew member, or replacing dossier-based capability gating.

## Repair

A canonical craft library now lives at:

`configs/crew/specialists/<crew_id>.md`

The library contains **82 cards** with exact 1:1 coverage of the active dossier roster:

- **81 specialist-inspired cards** adapted at full depth from the matching cards in `vessaxor-spec/The-ever-evolving-orchestration-`, pinned to source revision `fab4cb1d16e6ed210bdf5555d8fbbe45a609e415`;
- **1 GroX-native `independent-verifier` card** defining structural independence, evidence requirements, PASS/FAIL rules, non-self-activation, verify-only read-only behavior, and the prohibition on executor self-PASS.

Source-era allocation and command semantics were not imported. `agents-orchestrator` remains excluded. TEO allocation sections were removed, source team/control handoffs were rebound to actual GroX Crew or Pilot GorXu, and every card carries a GroX operational binding that keeps command and authority native to the Vessel.

## Runtime boundary

`CrewRoster` still loads `configs/crew/dossiers/*.json` as the machine-readable source for active membership, capability eligibility, routing tags, verification eligibility, and command-identity rejection.

A new read-only `craft_card(crew_id)` lookup exposes deep craft only for a Crew identity already present in the active roster. Craft therefore cannot create Crew, add capabilities, widen Mission authority, or create Repair permission.

No Pilot, Mission Order, Tool Gateway, execution authority, or verification-engine decision logic was changed by this Repair.

## Verification evidence

A dedicated craft contract now enforces:

- 82 dossier/card pairs with no missing or extra craft identities;
- no `agents-orchestrator`, Pilot, GorXu, Mission Control, or semantic orchestrator Crew identity;
- required specialist frontmatter and full operating sections;
- a per-card depth floor of at least 4,000 characters and 80 lines, plus stronger median-library floors;
- pinned source provenance for all 81 imported specialist identities;
- removal of TEO Allocation and source-era command residue;
- explicit Mission-authority and Repair-permission boundaries;
- independent-verifier independence and non-activation doctrine;
- additive roster craft retrieval without changing dossier capability gating.

The temporary craft audit ran on the Repair branch and passed after two deliberately retained red findings exposed and corrected source-era command leakage and an over-broad test assertion. Temporary bootstrap, rewrite, and audit machinery was removed before final review.

## Command integrity

The command relationship remains unchanged:

**Commander → GorXu → Crew**

GorXu remains the sole operational orchestrator. `incident-commander` is explicitly bounded as an incident-domain role, not Vessel command. `orchestration-evaluation-analyst` remains advisory and cannot self-activate findings or routing changes.

## Status

The Repair candidate is ready for the repository's normal independent PR and CI verification path. It is not treated as merged or released until that path completes.
