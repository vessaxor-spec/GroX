# GroX Progress Tracker

## Repository truth

**Status date:** 2026-08-14

The GitHub repository has now been initialized with the GroX-native constitutional and architectural baseline.

### Verified present on GitHub

- `README.md`
- `AI_INSTRUCTIONS.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/specification/PRINCIPLES.md`
- `docs/specification/MISSION_ORDER.md`
- stewardship baseline

### Architecture status

- Commander authority: **locked**
- Pilot GorXu as primary orchestrator: **locked**
- Mission Control as GroX-native subsystem under GorXu: **locked**
- Standing Crew model: **locked conceptually**
- Inspect vs Repair separation: **locked**
- Crew exception path through GorXu: **locked**
- Commander escalation threshold limited to critical, irreversible, or material intent-changing decisions: **locked**
- Competence separated from Mission authority: **locked**
- Independent verification principle: **locked**
- Durable Mission target architecture: **defined**
- Tool Gateway target architecture: **defined**
- Layered memory target architecture: **defined**
- Recruitment/evolution boundaries: **defined**
- Three-plane persistence architecture: **locked**

## Persistence foundation

GroX now separates continuity by responsibility:

1. **Cognitive continuity:** ChatGPT project `Space Exploration` is the current reconstitution home for Pilot GorXu and durable project context. The preferred active reasoning runtime is GPT-5.6 Sol with high reasoning.
2. **Vessel source:** `vessaxor-spec/GroX` is designated as the durable source body for code, doctrine, Crew dossiers, tests, configuration, and source-controlled history.
3. **Operational state:** Mission, evidence, Crew-tour, and runtime-memory state is private operational data and must not be committed raw to this public repository. Verified private checkpoints carry recoverable state.

A sandbox or host is classified as replaceable flight compute. Recovery must restore source and state, run integrity checks and tests, reconstitute GorXu, and resume only from the last committed safe Mission state.

**Evidence boundary:** the three-plane doctrine and binding metadata are durable on GitHub. The newer live sandbox runtime itself has not yet been fully synchronized to GitHub, so GitHub is not yet a complete copy of the current executable Vessel. That synchronization remains a separate controlled step.

## Implementation evidence boundary

A prior sandbox build was reported to contain a substantially larger implementation, including a working CLI, Crew roster, persistence, tools, tests, and Ship's Log history. That original source tree was not recovered. A new GroX-native live runtime has since been built in the current sandbox, but its complete executable source has not yet been synchronized to GitHub.

Until that synchronization is completed and verified, repository truth and live-sandbox truth must remain explicitly distinguished.

## Current milestone

**GroX Independence Baseline: COMPLETE**

**Three-Plane Persistence Architecture: COMPLETE**

The active architecture no longer depends on an external orchestration authority. GroX owns its command model, Mission Control, Mission Order contract, Crew doctrine, verification principles, evolutionary boundaries, and persistence model.

## Open checkpoint

The live Vessel's Apex run is the critical implementation path. Durable source synchronization and private operational-state custody must remain explicit prerequisites for relying on a fresh host as an immediate continuation environment.
