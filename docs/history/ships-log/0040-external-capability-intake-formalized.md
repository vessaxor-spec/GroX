# Ship's Log 0040 — External Capability Intake Formalized

**Date:** 2026-08-16

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 0 — External capability intake convention

**Issue:** #29

## Commander decision

The Commander approved all actionable recommendations from the ClaudX comparative review and authorized execution in the dependency order recorded by Post-Apex Operational Evolution Program 001.

Stage 0 required GroX to formalize how external repositories, agents, frameworks, protocols, skills, research, and architectural patterns enter evidence-driven evolution without becoming authority or creating duplicate architecture.

## Canonical result

`docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md` now defines the required intake posture:

- `ADOPT`
- `ADAPT`
- `HARVEST`
- `REJECT`

The convention requires explicit checks for existing GroX coverage, novelty provenance, useful evidence, required stripping/adaptation, duplication risk, authority/privacy/portability risk, and the evidence threshold for any later implementation or qualification.

It distinguishes external source facts and external evidence from GroX inference and GroX-native evidence. External claims therefore cannot silently become GroX qualification evidence.

The convention is deliberately lightweight. It creates no new command layer, Crew class, approval body, runtime service, external dependency, or duplicate decisions ledger. Records remain in the existing Mission, issue, research, architecture, or stewardship surfaces appropriate to the work.

## Exercise

The convention was exercised against the pinned ClaudX review source:

`vessaxor-spec/ClaudX@c82162b525ee183757e76300cc4a53f5643884f1`

The exercise demonstrates per-seam classification rather than repository-wide adoption. Useful independent ideas were adapted or harvested, while GroX-derived concepts, duplicate truth stores, host-specific architecture, sleeping retired identities, unsupported synthetic proof, and authority-incompatible conclusions were rejected.

## Authority result

No Commander, GorXu, Crew, Tool Gateway, verifier, persistence, routing, or mutation authority changed.

An intake decision remains advisory/planning evidence. Any implementation after `ADOPT`, `ADAPT`, or `HARVEST` still requires the ordinary GroX Mission, authority, verification, protected PR/CI, and canonical-source path.

## Program transition

Stage 0 exit condition is satisfied.

The next authorized workstream is **Stage 1 / issue #25: prove critical GroX health and governance detectors by mutation**.
