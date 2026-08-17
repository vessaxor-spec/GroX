# GroX External Capability Intake

## Purpose

GroX may inspect external repositories, agents, frameworks, protocols, skills, research, and architectural patterns for useful ideas. External material is evidence and input, not authority.

Before any material implementation derived from an external candidate, GorXu records one of four postures:

- **ADOPT** — use essentially as-is only when the behavior, maintenance burden, authority model, security boundary, portability, and canonical placement already fit GroX.
- **ADAPT** — retain the useful pattern but redesign it into GroX-native architecture and constraints.
- **HARVEST** — extract only a specific principle, seam, test discipline, algorithm, or interface idea; do not import the surrounding system.
- **REJECT** — do not incorporate the candidate. Preserve enough rationale to prevent repetitive reevaluation when the relevant evidence has not changed.

This is a review convention, not a command layer, Crew class, approval body, runtime service, or separate decision ledger.

## Authority boundary

External intelligence never inherits GroX authority.

A posture decision:

- does not grant Mission authority;
- does not authorize Repair or execution;
- does not activate an A6 proposal;
- does not create a new Crew identity;
- does not make an external dependency canonical;
- does not replace Commander approval, Mission Orders, Tool Gateway policy, verification, or protected repository controls.

Implementation after an ADOPT, ADAPT, or HARVEST decision still travels through the ordinary GroX path: Commander intent -> GorXu -> bounded Mission/Orders -> implementation -> verification -> protected PR/CI -> canonical source.

## Required review questions

For every material external candidate, answer the smallest set of questions sufficient to make the decision:

1. **Problem** — What concrete problem does the candidate solve?
2. **Existing coverage** — Does GroX already solve this problem? If yes, identify the existing source, service, decision, or qualification evidence.
3. **Novelty provenance** — Is the apparent novelty actually derived from GroX or another source already reviewed?
4. **Useful evidence** — What specific behavior, measured result, failure lesson, interface, algorithm, or test discipline is worth retaining?
5. **Required stripping** — What must be removed or redesigned to preserve GroX identity, Commander/GorXu authority, privacy, security, portability, and canonical structure?
6. **Duplication risk** — Would incorporation create a duplicate truth store, Crew function, command path, policy engine, memory plane, telemetry system, or runtime dependency?
7. **Evidence threshold** — What evidence is still required before implementation or qualification?
8. **Decision** — ADOPT, ADAPT, HARVEST, or REJECT, with a concise rationale.
9. **Next action** — research, bounded design, implementation Mission, experiment, or no action.

## Decision rules

### ADOPT

Use only when all of the following are true:

- behavior already fits GroX's command and authority model;
- no duplicate source of truth or command path is introduced;
- dependency and maintenance ownership are acceptable;
- security and privacy boundaries are understood;
- portability is acceptable;
- current evidence supports the claimed benefit;
- GroX can explain, test, maintain, and remove the adopted behavior.

ADOPT should be uncommon for architecture-level material.

### ADAPT

Use when the underlying pattern is valuable but its native implementation, terminology, host assumptions, authority model, persistence model, or dependencies do not fit GroX.

The adapted result must be GroX-native. The external source must not become an architectural authority merely because it inspired the design.

### HARVEST

Use when only a bounded idea is valuable. Typical examples include:

- a testing discipline;
- a failure mode or postmortem lesson;
- an algorithmic seam;
- an interface shape;
- a measurement method;
- an isolation or recovery technique.

Harvesting intentionally leaves the surrounding external architecture behind.

### REJECT

Use when the candidate is redundant, circular, unsafe, unmaintainable, incompatible, insufficiently evidenced, or would add unjustified complexity.

A rejection may be revisited only when material evidence or GroX requirements change.

## Evidence quality

Claims from an external project are not automatically GroX evidence.

Distinguish:

- **source fact** — what the external source actually implements or claims;
- **external evidence** — tests, measurements, incidents, or operational history produced by that source;
- **GroX inference** — what GorXu concludes may be relevant to the Vessel;
- **GroX evidence** — results reproduced or measured under GroX's own architecture, Missions, tests, or qualified environments.

Synthetic benchmarks, self-reported percentages, marketing claims, and unverified architectural assertions cannot become GroX qualification evidence merely by citation.

## Minimal review record

A material external review should preserve this compact record in the relevant Mission, issue, research note, architecture decision, or stewardship document. Do not create a parallel ledger solely for intake decisions.

```text
Candidate:
Pinned source/version/commit:
Problem addressed:
Existing GroX coverage:
Novelty provenance:
Useful evidence/seams:
Required stripping/adaptation:
Duplication/authority/privacy risks:
Evidence still required:
Decision: ADOPT | ADAPT | HARVEST | REJECT
Rationale:
Next action:
```

If several independent seams from one source receive different postures, record them separately rather than forcing one project-wide classification.

## Worked application — ClaudX comparative review

**Pinned source:** `vessaxor-spec/ClaudX@c82162b525ee183757e76300cc4a53f5643884f1`

The ClaudX review demonstrates that intake decisions are made per candidate seam, not per repository.

| Candidate seam | Decision | Rationale / next action |
|---|---|---|
| Unified Vessel health surface | ADAPT | Useful diagnostic pattern; rebuild from GroX's authoritative services under #26 rather than copy ClaudX implementation. |
| Health/governance detector mutation proving | HARVEST | Retain the test discipline only; apply it to GroX critical invariants under #25. |
| Tiered fast/targeted/full reconstitution | ADAPT | Useful efficiency pattern, but GroX's stronger recovery gates remain authoritative; implement under #27. |
| Long-horizon operational drift detection | ADAPT | Build on GroX A6 trajectories and non-self-activation rather than ClaudX's score implementation; track under #28. |
| Hot/warm/cold context management | HARVEST | Test the principle with GroX-native evidence under #30; the external synthetic savings result is not accepted as proof. |
| Mission-to-source provenance | HARVEST | Retain the traceability question only; next action is research under #31 before any implementation decision. |
| GroX-derived command spine, Crew model, memory planes, durable operations, Mission Graph, A6 trajectory concepts | REJECT | These originated from or are already native to GroX; re-import would be circular duplication. |
| Separate decisions ledger | REJECT | GroX already has canonical Mission/evidence/stewardship records; another ledger would duplicate truth. |
| Host-specific `launchd` heartbeat implementation | REJECT | Host-specific architecture conflicts with Vessel portability. The abstract unattended-health idea may inform #26 without importing the implementation. |
| Sleeping non-standing Crew identities | REJECT | Conflicts with GroX's canonical purge rule. |
| ClaudX synthetic 57.4% token-savings claim as GroX proof | REJECT | External synthetic measurement is not GroX qualification evidence; #30 must establish GroX evidence independently. |
| Remove `orchestration-evaluation-analyst` because ClaudX removed a similar role | REJECT | GroX role decisions must use actual GroX authority and capability evidence. |

## Completion criterion

This convention is successful when it prevents circular or duplicative adoption while allowing useful external evidence to enter GroX through bounded, attributable, GroX-native evolution.
