# AI Instructions for GroX

**Current qualified release baseline:** `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb` / **APEX QUALIFIED** / **82 Standing Crew**. Canonical source continues on protected `main` and may advance beyond the immutable release through the governed PR/CI path.

Apex qualification is a regression boundary, not inherited permission. Any consequential future change that touches Commander sovereignty, GorXu's sole-orchestrator role, Mission Order authority, verifier independence, evidence integrity, recovery, source/state compatibility, routing, governed tool execution, native cognition, or local installation must preserve those invariants through appropriate tests and independent verification.

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

Pilot GorXu is the principal personal-assistant interface, primary orchestrator, and second-in-command. Mission Control is a native GroX policy/advisory service used by GorXu; it is not a command layer. No Crew member, Division, verifier, tool, scheduler, cognitive provider, model, installer, launcher, runtime component, or external system may become a parallel orchestrator.

### Command and infrastructure must never be confused

The command spine above is the only operational hierarchy. Infrastructure and capabilities power that hierarchy; they do not rank within it.

The following are subordinate resources of the Vessel, not command layers: native cognition, external models, runtime assets, Crew dossiers and craft, private state, Commander workspace, Tool Gateway, memory, evidence, training/evaluation systems, inference backends, installers, launchers, and host/runtime services.

Builders must not implement, describe, or illustrate any of those resources as sitting above Pilot GorXu, as a peer to Pilot GorXu, or as an intermediate command authority between Pilot GorXu and Divisions/Standing Crew. A native model may power GorXu and relevant Crew cognition, but the model is an engine/capability of the Vessel, not its Pilot. Physical storage location or runtime dependency does not imply command authority.

When diagrams show command relationships, use the canonical spine explicitly. When diagrams show infrastructure, label it as infrastructure/resources and keep it visually distinct from command rank.

## Hard constraints

- Do not introduce an external orchestration system as architectural authority.
- Do not create a second command spine parallel to GorXu.
- Do not insert native cognition, a provider/model layer, runtime assets, tools, installation components, or any other infrastructure between GorXu and Divisions/Crew as command authority.
- Do not allow Crew to self-authorize, self-promote, widen scope, or mutate outside a Mission Order.
- Do not conflate competence with authority. Knowing how to perform an action does not grant permission to perform it.
- Keep inspection and repair authority separate.
- Do not conflate successful bounded execution with delivery of the Commander objective. Mission synthesis must state actual effect, objective state, mutation state, and verification scope truthfully.
- Crew craft, memory, cognitive-provider output, confidence, and prior performance are competence/advisory context only. None may create eligibility, capability, Repair authority, risk reduction, scope expansion, routing authority, or verifier independence.
- Selective Crew craft context must remain bounded and attributable. Do not inject complete deep craft cards per summon by default, and do not omit mandatory safety/operational-binding context merely to fit optional task detail.
- Provider-driven Crew actions must traverse the existing sealed Mission Order and Tool Gateway. The first bounded Crew-cognition seam is Inspect-only and read/test-only; Verify, Repair, and Execute must not silently inherit model-backed Crew cognition.
- Craft-selection and Crew-cognition bookkeeping must not improve Crew performance or routing scores merely by adding evidence kinds. Only calibrated operational evidence may affect evidence-quality history.
- Crew encountering blockers, safer alternatives, better methods, missing capability, or elevated risk must stop the affected mutation and report to GorXu.
- GorXu should resolve ordinary and reversible issues using Mission Control and relevant Crew. Escalate to the Commander only for critical, irreversible, or material intent-changing decisions.
- Independent verification must remain independent from the executor when required by GroX policy.
- Significant actions must produce evidence sufficient for audit and verification.
- Tool access must be capability-gated and constrained to the current Mission Order.
- Sleeping Crew are logically persistent identities, not necessarily persistent model processes. Fresh working context per tour is preferred over eternal chat context.
- Recruitment creates durable standing Crew only after a real capability gap is established. Recruitment may not create an orchestration rival to GorXu.
- Mission Graph scheduling is a mechanical Pilot runtime, not an independent command layer or parallel orchestrator.
- Graph replanning may recover reversible Crew or runtime failure, but it may not widen authority, change Commander intent, bypass required verification, or silently convert inspection into mutation.
- Native cognition and model evolution may improve capability but cannot self-activate, self-promote, redefine GroX's purpose, or displace GorXu's orchestration role.
- CLI and desktop launchers are Commander Seat entry paths into the same GorXu-led Vessel. They must not create alternate orchestration paths or duplicate state authorities.

## Persistence and filesystem doctrine

- Treat the `Space Exploration` ChatGPT project as GorXu's current cognitive reconstitution home while native local cognition remains under development.
- Treat `vessaxor-spec/GroX` as the durable source body of the Vessel.
- Treat operational state and `.groxstate` archives as private; never commit them to the public repository.
- Legacy source-checkout operation stores live SQLite state at `configs/state/grox.sqlite3`.
- NCI-1B establishes an explicit `VesselLayout` for installed/runtime evolution with three filesystem roles: runtime/assets root, private state root, and Commander work root. In separated mode the active database is under the private state root, while Tool Gateway filesystem authority remains rooted only in Commander work.
- Filesystem roles are infrastructure, not command rank. Crew dossiers/craft residing under runtime assets does not place Crew above GorXu; GorXu loads and orchestrates those Crew identities.
- Runtime/assets, private state, and Commander work must remain non-overlapping in separated operation so ordinary filesystem authority cannot traverse into GroX internals or private state.
- Never assume a sandbox survives. Before material host migration or risky state work, create and verify an operational snapshot.
- Reconstitution on a fresh host must restore/source-bind the required Vessel assets and state, run integrity and tests, and only then resume Missions.
- A missing cognitive provider causes safe degradation, never authority expansion.

## Local installation doctrine

- Normal-user direction is an installed GroX CLI for macOS and Linux; repository cloning is the developer path, not the intended long-term consumer path.
- First-run commissioning defaults the dedicated workspace to `~/GroX` while allowing the user to choose another location.
- NCI-1A has established safe workspace commissioning primitives and host-to-workspace binding. NCI-1B has established runtime/assets, private-state, and Commander-work separation. These foundations do not yet prove a standalone installed GorXu because canonical runtime assets are not yet packaged for that path.
- Do not advertise a public one-command installer, desktop launcher, bundled native language model, or offline GorXu as available until the corresponding implementation and qualification evidence exists.
- Installation, upgrade, launcher, model provisioning, and uninstall behavior must preserve the same command spine and must not silently destroy the Commander's Vessel state.

## Working rules

- Recalibrate against repository truth before making material changes.
- Prefer small, testable changes over speculative redesign.
- Preserve strict file organization. Put every artifact in its canonical location.
- Update the progress tracker when a material milestone changes project state.
- Record major architectural milestones in the Ship's Log.
- Treat implementation claims as unverified until source and tests are inspected.
- Preserve approved architecture when synchronizing or recovering runtime state; do not replace richer canonical doctrine with bootstrap summaries.
- Distinguish controlled/fake-provider CI from live model-backed operation. A provider-neutral seam is not a live-provider qualification claim.
- Preserve historical red evidence when it reveals a real defect or ambiguity; do not rewrite history merely to create a cleaner narrative.

## Builder objective

Build and evolve GroX as the Commander's commandable, persistent AI personal assistant and operating environment with a capable Pilot GorXu above and orchestrating Divisions and Standing Crew, native Mission Control under GorXu, durable Missions and Mission Graphs, bounded tools, evidence, verification, memory, recovery, local installation, progressively owned native cognition, and controlled evolution.
