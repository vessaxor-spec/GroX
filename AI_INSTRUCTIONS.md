# AI Instructions for GroX

This repository defines the Vessel. Any AI builder, coding agent, reviewer, or maintainer working here must preserve the command architecture unless the Commander explicitly changes it.

## Authority hierarchy

1. Commander directives
2. This file
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/specification/PRINCIPLES.md`
5. `docs/specification/MISSION_ORDER.md`
6. Stewardship documents
7. Existing code and tests
8. Builder judgment

Higher authority wins when instructions conflict.

## Canonical command spine

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

Pilot GorXu is the primary orchestrator and second-in-command. Mission Control is native to GroX and operates under GorXu. No Crew member, Division, verifier, tool, or external system may become a parallel orchestrator.

## Hard constraints

- Do not introduce an external orchestration system as architectural authority.
- Do not create a second command spine parallel to GorXu.
- Do not allow Crew to self-authorize, self-promote, widen scope, or mutate outside a Mission Order.
- Do not conflate competence with authority. Knowing how to perform an action does not grant permission to perform it.
- Keep inspection and repair authority separate.
- Crew encountering blockers, safer alternatives, better methods, missing capability, or elevated risk must stop the affected mutation and report to GorXu.
- GorXu should resolve ordinary and reversible issues using Mission Control and relevant Crew. Escalate to the Commander only for critical, irreversible, or material intent-changing decisions.
- Independent verification must remain independent from the executor when required by GroX policy.
- Significant actions must produce evidence sufficient for audit and verification.
- Tool access must be capability-gated and constrained to the current Mission Order.
- Sleeping Crew are logically persistent identities, not necessarily persistent model processes. Fresh working context per tour is preferred over eternal chat context.
- Recruitment creates durable standing Crew only after a real capability gap is established. Recruitment may not create an orchestration rival to GorXu.

## Working rules

- Recalibrate against repository truth before making material changes.
- Prefer small, testable changes over speculative redesign.
- Preserve strict file organization. Put every artifact in its canonical location.
- Update the progress tracker when a material milestone changes project state.
- Record major architectural milestones in the Ship's Log once that history is recovered into the repository.
- Treat currently missing implementation from the earlier build as unverified until source and tests are recovered and inspected.

## Builder objective

Build and evolve GroX as a commandable, persistent AI environment with a real Commander Seat, a capable Pilot GorXu, native Mission Control, standing Crew, durable Missions, bounded tools, evidence, verification, memory, recovery, and controlled evolution.
