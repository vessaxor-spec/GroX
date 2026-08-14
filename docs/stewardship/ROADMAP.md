# GroX Roadmap

## Current position

GroX has completed its independence baseline. The command architecture is now native to the Vessel:

**Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew**

The immediate objective is not to add more features blindly. It is to preserve the new authority model and choose the next steering vector deliberately.

## Completed baseline

- Native command hierarchy defined
- GorXu established as sole primary orchestrator
- Mission Control defined as a GroX-native subsystem under GorXu
- GroX Mission Order defined as the operational authority contract
- Standing Crew model retained
- Inspect/Repair separation retained
- Crew exception handling routed through GorXu
- Commander escalation threshold narrowed to critical, irreversible, or material intent-changing decisions
- Verification, evidence, memory, mission durability, tool governance, recruitment, and controlled evolution defined as native GroX concerns

## Recovery track

If the prior sandbox Vessel source can be recovered, it should be imported only through a reconciliation pass:

1. Inventory recovered files and tests.
2. Classify every legacy architectural concept as retain, rename, adapt, or remove.
3. Replace obsolete external-authority terminology with GroX-native concepts.
4. Reconcile dispatch-style contracts into Mission Orders.
5. Verify that GorXu is the sole orchestrator in code, not only documentation.
6. Run the complete test suite and add tests for the new authority invariants.
7. Update progress state from evidence.

## Candidate future vectors

These are intentionally unordered until the Commander selects direction:

- Recover and harden the existing Vessel implementation
- Durable Mission engine and crash-safe resume
- Crew Dossier compiler and persistent organizational memory
- Tool Gateway and secure real-world actuation
- Computer-use architecture
- GorXu reasoning, planning, synthesis, and exception handling
- Crew routing and Division structure
- Recruitment and controlled evolution
- Commander Seat and bridge experience
- Evaluation, telemetry, evidence provenance, and self-improvement loops
- Deployment and host-isolation architecture

## Steering gate

No candidate vector is automatically next.

The roadmap remains at this gate until the Commander decides where to steer the Vessel.

## Locked persistence foundation

The three-plane persistence architecture is foundational infrastructure for every future GroX stage:

- the ChatGPT project `Space Exploration` is GorXu's current cognitive reconstitution home;
- GitHub is the durable Vessel source body;
- private verified checkpoints carry operational Mission and Crew state;
- sandbox and host compute are replaceable;
- recovery must pass integrity and test gates before Mission continuation.

This is not a competing roadmap vector. It exists so the Apex run and every later capability can survive model, session, sandbox, and host turnover.
