# AI Instructions for GroX

**Current qualified release baseline:** `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb` / **APEX QUALIFIED** / **82 Standing Crew**. Canonical source continues on protected `main` and may advance beyond the immutable release through the governed PR/CI path.

Apex qualification is a regression boundary, not inherited permission. Any consequential future change that touches Commander sovereignty, GorXu's sole-orchestrator role, Mission Order authority, verifier independence, evidence integrity, recovery, source/state compatibility, routing, or governed tool execution must preserve those invariants through appropriate tests and independent verification.

This repository defines the Vessel. Any AI builder, coding agent, reviewer, or maintainer working here must preserve the command architecture unless the Commander explicitly changes it.

## Authority hierarchy

1. Commander directives
2. This file
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/specification/PRINCIPLES.md`
5. `docs/specification/MISSION_ORDER.md`
6. `docs/specification/MISSION_GRAPH.md`
7. Stewardship documents
8. Existing code and tests
9. Builder judgment

Higher authority wins when instructions conflict.

## Canonical command spine

**Commander → Pilot GorXu → Divisions → Standing Crew**

Pilot GorXu is the primary orchestrator and second-in-command. Mission Control is a native GroX policy/advisory service used by GorXu; it is not a command layer. No Crew member, Division, verifier, tool, scheduler, or external system may become a parallel orchestrator.

## Hard constraints

- Do not introduce an external orchestration system as architectural authority.
- Do not create a second command spine parallel to GorXu.
- Do not allow Crew to self-authorize, self-promote, widen scope, or mutate outside a Mission Order.
- Do not conflate competence with authority. Knowing how to perform an action does not grant permission to perform it.
- Keep inspection and repair authority separate.
- Do not conflate successful bounded execution with delivery of the Commander objective. Mission synthesis must state actual effect, objective state, mutation state, and verification scope truthfully.
- Crew encountering blockers, safer alternatives, better methods, missing capability, or elevated risk must stop the affected mutation and report to GorXu.
- GorXu should resolve ordinary and reversible issues using Mission Control and relevant Crew. Escalate to the Commander only for critical, irreversible, or material intent-changing decisions.
- Independent verification must remain independent from the executor when required by GroX policy.
- Significant actions must produce evidence sufficient for audit and verification.
- Tool access must be capability-gated and constrained to the current Mission Order.
- Sleeping Crew are logically persistent identities, not necessarily persistent model processes. Fresh working context per tour is preferred over eternal chat context.
- Recruitment creates durable standing Crew only after a real capability gap is established. Recruitment may not create an orchestration rival to GorXu.
- Mission Graph scheduling is a mechanical Pilot runtime, not an independent command layer or parallel orchestrator.
- Graph replanning may recover reversible Crew or runtime failure, but it may not widen authority, change Commander intent, bypass required verification, or silently convert inspection into mutation.

## Persistence doctrine

- Treat the `Space Exploration` ChatGPT project as GorXu's current cognitive reconstitution home.
- Treat `vessaxor-spec/GroX` as the durable source body of the Vessel.
- Treat `configs/state/grox.sqlite3` and `.groxstate` archives as private operational state; never commit them to the public repository.
- Never assume a sandbox survives. Before material host migration or risky state work, create and verify an operational snapshot.
- Reconstitution on a fresh host must restore source and state, run integrity and tests, and only then resume Missions.
- A missing cognitive provider causes safe degradation, never authority expansion.

## Working rules

- Recalibrate against repository truth before making material changes.
- Prefer small, testable changes over speculative redesign.
- Preserve strict file organization. Put every artifact in its canonical location.
- Update the progress tracker when a material milestone changes project state.
- Record major architectural milestones in the Ship's Log.
- Treat implementation claims as unverified until source and tests are inspected.
- Preserve approved architecture when synchronizing or recovering runtime state; do not replace richer canonical doctrine with bootstrap summaries.

## Builder objective

Build and evolve GroX as a commandable, persistent AI environment with a real Commander Seat, a capable Pilot GorXu, native Mission Control, standing Crew, durable Missions and Mission Graphs, bounded tools, evidence, verification, memory, recovery, and controlled evolution.
