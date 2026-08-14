# GroX Architecture

## Purpose

GroX is an independent persistent AI command environment. The running system is the Vessel. The human Commander directs the Vessel through Pilot GorXu, the primary orchestrator and second-in-command.

## Command architecture

```text
Commander
    │ intent / directives
    ▼
Pilot GorXu
    │
    ├── Mission Control
    │     ├── risk and authority analysis
    │     ├── routing intelligence
    │     ├── verification policy
    │     └── operational research
    │
    └── Divisions
          └── Standing Crew
                ├── mission-specific tour context
                ├── bounded tools
                ├── evidence production
                └── durable identity and memory
```

GorXu is the single operational orchestrator. Mission Control is a native GroX subsystem managed by GorXu. It may enforce GroX constitutional constraints, but it does not create an independent command hierarchy.

## Authority flow

1. The Commander provides intent.
2. GorXu interprets the directive and determines the work required.
3. GorXu consults Mission Control and relevant Crew for risk, capability, research, and verification needs.
4. GorXu issues bounded Mission Orders to selected Crew.
5. Crew execute only within the granted authority.
6. Exceptions return to GorXu. GorXu may consult additional Crew before deciding.
7. Critical, irreversible, or material intent-changing decisions escalate to the Commander.
8. Evidence and verification return through GorXu for synthesis and closure.

Authority may narrow as it travels downward. It may not widen without a new decision from the appropriate authority.

## Standing Crew model

Crew are logically persistent organizational identities with durable dossiers, competencies, procedures, history, and memory. They need not remain as live model processes while asleep.

Each wake creates a fresh tour context containing only what is needed for the current Mission plus relevant retrieved memory. This preserves continuity without allowing old working context to accumulate indefinitely.

Crew competence and Mission authority are separate:

- Competence describes what a Crew member knows how to do.
- Mission authority describes what that Crew member may do now.

## Mission Control

Mission Control is a GroX-native service layer available to GorXu. Its responsibilities include:

- risk analysis;
- authority-envelope validation;
- capability matching;
- routing support;
- independent verification requirements;
- evidence requirements;
- research and advisory support;
- anomaly and exception analysis.

Mission Control does not issue operational orders directly to Crew unless GorXu explicitly delegates a bounded control function. Such delegation never creates a parallel orchestrator.

## Inspect and repair protocol

Inspection and mutation are separate modes.

### Inspect

- read, analyze, test, and report;
- no mutation authority unless explicitly required for a safe diagnostic and granted in the Mission Order;
- findings return to GorXu.

### Repair

- issued only after GorXu has accepted a repair path within delegated authority or the Commander has approved where required;
- mutation is restricted to explicit capabilities, paths, systems, and stop conditions;
- blockers, better methods, elevated risk, or scope changes return to GorXu before affected mutation continues.

## Verification

Verification is independent where policy requires it. The executor may provide self-checks, but self-checks are not independent verification.

Verification should evaluate the evidence package, requested outcome, authority compliance, and actual resulting state.

## Mission durability

A Mission is a first-class durable object. The target architecture must persist:

- Commander directive;
- GorXu plan;
- Mission Orders;
- Crew assignments and tours;
- tool actions;
- exceptions and decisions;
- approvals when required;
- evidence;
- verifier results;
- final disposition.

A restarted Vessel must be able to determine the last committed Mission state and resume safely rather than reconstructing state from conversational memory.

## Tool architecture

Crew do not receive unrestricted raw host access. Tool use should pass through a GroX Tool Gateway that intersects:

- Mission authority;
- Crew capability;
- host policy;
- path and origin restrictions;
- secret policy;
- side-effect class;
- resource budget;
- audit and evidence requirements.

The intersection is deny-wins. Host restrictions may narrow authority but never expand it.

## Memory architecture

The target memory system separates:

1. Working memory: current tour context.
2. Episodic memory: what happened on prior tours.
3. Semantic memory: durable learned facts and relationships.
4. Procedural memory: learned and versioned ways of working.
5. Vessel memory: organizational knowledge shared independently of any single Crew member.

Memory must support provenance, relevance, consolidation, correction, and bounded forgetting.

## Recruitment and evolution

When no existing Crew member sufficiently covers a demonstrated capability gap, GorXu may initiate recruitment under GroX policy.

A recruit becomes durable standing Crew with a canonical dossier. Recruitment must not:

- create a competing orchestrator;
- grant authority merely because competence exists;
- silently duplicate an existing Crew role;
- bypass inspection, validation, or roster integrity checks.

Evolution should modify skills, procedures, routing metadata, and memory through evidence-backed processes rather than uncontrolled self-rewriting.

## Commander Seat

GroX is incomplete without a usable Commander Seat. The Commander must be able to:

- issue directives;
- observe Mission state;
- inspect evidence and decisions;
- answer escalations;
- interrupt or redirect work;
- suspend or terminate a Mission;
- review the Vessel's current condition.

CLI may be the initial interface. Other interfaces can be added without changing the command architecture.

## Persistence planes

GroX separates continuity into three planes:

1. **Cognitive continuity:** the ChatGPT project `Space Exploration` is the current reconstitution home for Pilot GorXu, Commander context, architecture decisions, and Apex trajectory. The active reasoning model occupies the Pilot seat when invoked; GorXu is not defined as one eternal model process.
2. **Vessel source:** `vessaxor-spec/GroX` is the durable body for source code, doctrine, Crew dossiers, tests, source-controlled configuration, and institutional history.
3. **Operational state:** Mission, evidence, Crew-tour, and runtime-memory state is private operational data. It is restored from verified private checkpoints rather than committed raw to the public source repository.

The active sandbox or host is a replaceable flight computer, not the permanent Vessel. Reconstitution on a new host must restore verified source and state, run integrity checks and tests, reconstitute GorXu, and resume only from the last committed safe Mission state.

The normative persistence and recovery design is defined in `docs/architecture/PERSISTENCE_ARCHITECTURE.md`.
