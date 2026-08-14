# GroX

GroX is an independent, persistent AI command environment built around a clear chain of command:

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

The Commander provides intent and retains final authority over critical, irreversible, or intent-changing decisions. Pilot GorXu is the primary orchestrator and second-in-command. Mission Control is a GroX-native command system used by GorXu for governance, risk analysis, routing support, verification policy, and operational intelligence. Standing Crew execute bounded Mission Orders under explicit authority and evidence requirements.

GroX is not a wrapper around an external orchestration system. Its governance, mission control, crew model, memory, verification, tool policy, and evolutionary mechanisms are native parts of the Vessel.

## Core operating model

- The Commander sets intent.
- GorXu interprets intent, plans the Mission, consults Mission Control, selects Crew, issues Mission Orders, resolves ordinary and reversible exceptions, and synthesizes outcomes.
- Mission Control advises and enforces GroX-native policy. It does not independently command Crew or override the Commander–GorXu chain.
- Crew operate only within the authority granted for a specific Mission Order.
- Analysis and mutation authority are separate. Inspection does not imply permission to repair.
- Crew may report blockers or better approaches, but may not widen their own scope.
- GorXu escalates to the Commander only when a decision is critical, irreversible, or materially changes Commander intent.
- Independent verification and evidence are structural requirements where risk warrants them.

## Live Vessel

The current native runtime includes:

- Commander Seat CLI and interactive bridge;
- Pilot GorXu orchestration with project/session cognitive-provider support;
- native Mission Control;
- 81 specialist-inspired Standing Crew plus one independent verifier;
- durable Mission, Order, Evidence, Crew, memory, and performance state;
- Living Company Intelligence with attributable semantic/procedural/Vessel memory and bounded selective retrieval;
- experienced eligible-Crew routing informed by evidence, reliability, load, cost, latency, and risk;
- A4 durable Mission Graph resume with committed-step preservation, checkpointed execution, and bounded cancellation/resume controls;
- executive exception handling with real bounded Crew consultation before ordinary recoverable replans;
- atomic journaled `write_text` Repair with idempotent replay, compensation, and fail-closed divergence handling;
- bounded filesystem/test Tool Gateway;
- Inspect/Repair separation;
- independent verification;
- private integrity-checked `.groxstate` snapshot/restore support.

```bash
python -m pip install -e .
grox status
grox roster
grox mission "Inspect the Vessel and report readiness" --mode inspect
grox bridge
```

## Persistence model

GroX separates continuity into three planes:

1. Cognitive continuity: the Space Exploration project reconstitutes GorXu and project context.
2. Vessel source: this GitHub repository is the durable source body.
3. Operational state: private runtime state travels through verified `.groxstate` snapshots and is not committed publicly.

A sandbox is replaceable compute, not the permanent Vessel.

## Repository authority

The canonical project authority is defined by:

1. `AI_INSTRUCTIONS.md`
2. `docs/architecture/ARCHITECTURE.md`
3. `docs/specification/PRINCIPLES.md`
4. `docs/specification/MISSION_ORDER.md`
5. `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`
6. `docs/stewardship/ROADMAP.md`
7. `docs/stewardship/progress-tracker.md`
8. Code and tests
