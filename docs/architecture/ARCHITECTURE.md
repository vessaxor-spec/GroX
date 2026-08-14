# GroX Architecture

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

GorXu is the single operational orchestrator. Mission Control is a native GroX subsystem managed by GorXu.

## Runtime layers

1. Commander Seat: CLI/bridge for directives, status, intervention, and review.
2. Pilot GorXu: interprets intent, consults Mission Control, selects Crew, issues Mission Orders, synthesizes outcomes.
3. Mission Control: risk, authority, routing, verification, and evidence policy.
4. Standing Crew: durable identity with fresh mission-specific tours.
5. Tool Gateway: deny-wins capability enforcement and root confinement.
6. Mission Store: durable mission/order/evidence/Crew state in SQLite.
7. Verification: independent verification path where policy requires it.

## Authority

Authority may narrow as it moves downward and never widens implicitly. Crew competence describes knowledge; Mission authority describes current permission.

## Inspect and repair

Inspect is read/report by default. Repair grants narrow mutation authority for an explicit objective and scope. Exceptions stop affected mutation and return to GorXu.

## Durability

Missions, orders, evidence, decisions, Crew tours, and status are persisted. Interrupted missions are marked and remain inspectable after restart.
## Persistence planes

GroX separates persistence into three planes:

1. **Cognitive continuity:** the `Space Exploration` ChatGPT project is the current reconstitution home for Pilot GorXu and durable project context.
2. **Vessel source:** the GroX GitHub repository is the durable body for code, doctrine, Crew dossiers, tests, and source-controlled history.
3. **Operational state:** private Mission, evidence, Crew, and runtime-memory state is persisted locally and exported as verified private `.groxstate` snapshots.

The active sandbox is a replaceable flight computer, not the permanent Vessel. Full rules and recovery gates are defined in `docs/architecture/PERSISTENCE_ARCHITECTURE.md`.

