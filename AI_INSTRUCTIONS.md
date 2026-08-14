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

## Canonical command spine

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

Pilot GorXu is the primary orchestrator and second-in-command. Mission Control is native to GroX and operates under GorXu. No Crew member, Division, verifier, tool, or external system may become a parallel orchestrator.

## Hard constraints

- Do not introduce an external orchestration system as architectural authority.
- Do not create a second command spine parallel to GorXu.
- Do not allow Crew to self-authorize, self-promote, widen scope, or mutate outside a Mission Order.
- Do not conflate competence with authority.
- Keep inspection and repair authority separate.
- Crew exceptions return to GorXu.
- GorXu resolves routine and reversible issues; escalate only critical, irreversible, or material intent-changing decisions.
- Independent verification remains independent when required.
- Significant actions produce evidence.
- Tool access is capability-gated and constrained to the current Mission Order.
- Sleeping Crew are logically persistent identities, not necessarily persistent model processes.
- Recruitment may not create an orchestration rival to GorXu.

## Persistence doctrine

- Treat `Space Exploration` as GorXu's current cognitive reconstitution home.
- Treat `vessaxor-spec/GroX` as the durable source body of the Vessel.
- Treat `configs/state/grox.sqlite3` and `.groxstate` archives as private operational state; never commit them to the public repository.
- Never assume a sandbox survives. Before material host migration or risky state work, create and verify an operational snapshot.
- Reconstitution on a fresh host must restore source and state, run integrity/tests, and only then resume Missions.
- A missing cognitive provider causes safe degradation, never authority expansion.

