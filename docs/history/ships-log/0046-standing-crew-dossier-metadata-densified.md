# Ship's Log 0046 — Standing Crew Dossier Metadata Densified

**Date:** 2026-08-16

**Mission:** Close the non-blocking dossier-metadata condition from the Standing Crew craft-depth Repair

**Mode:** Bounded Repair

## Trigger

Independent verification of the Standing Crew craft-depth Repair accepted PR #40 while identifying one non-blocking follow-up condition: deep craft was restored in the canonical specialist library, but many machine-readable JSON dossiers still exposed only sparse skill and routing metadata when inspected without the matching card.

The condition measured **61 of 82 dossiers** with `skills <= 3` and `tags <= 4` before this follow-up.

## Repair boundary

This Mission densifies descriptive dossier metadata only. It does not alter the command spine, Mission Orders, capability grants, Tool Gateway decisions, verification eligibility, risk posture, standing orders, Crew membership, or the full craft library.

For each of the 82 active dossiers:

- `domains` is derived directly from the matching canonical specialist card frontmatter;
- existing `skills` are preserved and augmented with those declared domains;
- existing `tags` are preserved and augmented with normalized routing terms derived from those declared domains.

`capabilities` remain the action and required-capability eligibility source. Domain, skill, and tag metadata do not create authority or permission.

## Red evidence

The first branch-only deterministic bootstrap run, `31971581433`, failed before committing any dossier changes because its parser assumed all card frontmatter used block YAML lists.

The failure exposed a real source-shape variation: `architect.md` declares domains with inline YAML list syntax. The write step was skipped. The source requirement was not weakened and the card was not bypassed.

The parser was corrected to support both canonical inline and block domain-list forms.

## Green generation evidence

Corrected bootstrap run `31971617744` completed successfully and reported:

- dossiers examined: **82**;
- dossiers changed: **82**;
- thin dossiers before: **61**;
- thin dossiers after: **0**;
- minimum metadata: **9 tags / 6 skills / 3 domains**;
- median metadata: **21 tags / 10 skills / 7 domains**.

The generator asserted that `crew_id`, Division, title, capabilities, verification flag, risk posture, standing orders, and standing status were unchanged, and that every active dossier still retained `repo_read` capability.

The temporary write workflow was removed after materializing the candidate. It is not part of the intended durable change set.

## Routing safety

Dossier tags participate in deterministic `CrewRoster.select()` scoring, so metadata densification is not treated as cosmetic.

A permanent contract therefore verifies:

- exact 82 dossier/card coverage;
- dossier `domains` equal the matching canonical craft-card domains;
- domain metadata is represented in skills and normalized routing tags;
- dossiers no longer regress to the previously observed thin metadata state;
- capability gating remains sourced from dossier capabilities;
- the established domain-routing cases continue to select the same Crew after enrichment.

## Command integrity

The command relationship remains unchanged:

**Commander → GorXu → Crew**

GorXu remains the sole operational orchestrator. Descriptive metadata cannot create Mission authority, Repair permission, verification authority, capability eligibility, or self-activation.

## Status

The bounded candidate is ready for the normal protected pull-request CI path and subsequent independent verification. It is not treated as merged or complete until those gates pass.
