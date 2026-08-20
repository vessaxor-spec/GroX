# GroX Persistence Architecture

**Qualified release baseline:** `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`. Canonical source continues on protected `main` and may advance beyond the immutable release through governed PR/CI. Snapshot source binding, ancestor compatibility control, and fail-closed unrelated-source restore are part of the Apex regression boundary. Protected source now also contains the NCI-1A installed-workspace foundation and NCI-1B runtime/state/work filesystem-role separation; those post-release foundations do not move the release or create a new Apex stage.

## Decision

GroX separates continuity by responsibility. No single sandbox, model process, conversation, host, workspace, model artifact, or filesystem directory is the Vessel's permanent home.

The command architecture is independent of these persistence/storage choices:

**Commander → Pilot GorXu → Divisions → Standing Crew**

Pilot GorXu remains the sole operational orchestrator. Persistence planes and filesystem roles are infrastructure beneath that command relationship; they never create organizational rank or command authority.

## Plane 1: Cognitive continuity

**Current home:** ChatGPT project `Space Exploration` while native local GorXu cognition remains under development.

The project holds the durable human/AI operating context needed to reconstitute Pilot GorXu: Commander intent, GroX doctrine, architectural decisions, Apex trajectory, relevant history, and continuity across project conversations.

The active reasoning model occupies a cognitive engine/provider role for Pilot GorXu when invoked. GorXu is therefore a durable Vessel identity and command role, not one eternal model process or chat thread. A future native model may supply more of GorXu's cognition without replacing GorXu as Pilot or changing the command spine.

If project cognition is unavailable, the Vessel must degrade to the deterministic GroX control plane where qualified. Loss of cognition must never widen authority.

## Plane 2: Vessel source

**Durable home:** `vessaxor-spec/GroX` on GitHub.

Git is the authoritative durable body for:

- source code;
- GroX doctrine and architecture;
- Crew dossiers and company configuration;
- tests and evaluation assets;
- machine-readable governance policy;
- Ship's Log and stewardship records intended for source control.

A sandbox is replaceable compute. It may run the Vessel, but it is not repository truth.

Crew dossiers and craft being source-controlled runtime assets does not place Crew above GorXu. They are definitions and resources that GorXu loads, selects, and commands through bounded Mission Orders.

## Plane 3: Operational state

Operational state includes Missions, Mission Orders, evidence, Crew tour state, episodic continuity, durable memory, graph checkpoints, exception/recovery state, evaluation state, and cost commitments.

Operational state is **private runtime data**. It must not be committed raw to the public GitHub repository.

Two path forms currently exist:

- **Legacy/source-checkout operation:** live SQLite state remains `configs/state/grox.sqlite3`; recoverable `.groxstate` snapshots remain under `configs/state/snapshots/` and are ignored by Git.
- **NCI-1B separated operation:** `VesselLayout` assigns a distinct private state root. The active database is stored as `<state_root>/grox.sqlite3`; mutable browser evidence and isolated-workspace scratch are also routed to private state rather than Commander work or runtime assets.

Each `.groxstate` snapshot contains:

- a consistent SQLite backup;
- a versioned manifest;
- SHA-256 integrity evidence;
- the Vessel Git commit when available;
- the cognitive/source binding metadata required to understand what the snapshot belongs to.

Restoration requires explicit confirmation, verifies the snapshot source binding against the active Vessel source, and creates a pre-restore checkpoint before replacing live state. Exact source matches restore normally. A snapshot from a proven ancestor source requires explicit `allow_ancestor=True`; unrelated or unprovable source histories fail closed.

## NCI filesystem roles

NCI-1B introduced three explicit filesystem roles for the installed/local Vessel path. These roles are deliberately distinct from the persistence-plane model above and from the command hierarchy.

```text
Command hierarchy

Commander
   ↓
Pilot GorXu
   ↓
Divisions
   ↓
Standing Crew

Infrastructure/filesystem roles used by that hierarchy

runtime/assets root   private state root   Commander work root
        │                    │                    │
Crew/craft/policy      SQLite/evidence      Mission filesystem
schemas/runtime data   mutable scratch       Tool Gateway scope
```

The three roles mean:

1. **Runtime/assets root** — immutable or versioned GroX application assets such as Crew dossiers/craft, policy, schemas, and later packaged runtime resources.
2. **Private state root** — mutable Vessel state that normal Commander-work filesystem authority must not expose.
3. **Commander work root** — filesystem boundary in which Tool Gateway performs ordinary Mission file/list/read/write/test operations when authorized.

Separated `VesselLayout` requires these roots not to overlap. This is both an installation/persistence boundary and a security boundary. A path from Commander work must not traverse into runtime assets or private state.

These roots do not alter command rank. Runtime assets may contain Crew definitions and model artifacts, but GorXu remains above and orchestrates Crew and model capabilities. The private state root remembers what the Vessel did; it does not decide what the Vessel should do. The Commander work root is where bounded work occurs; it is not a command authority.

## Installed-workspace continuity

NCI-1A established safe local workspace commissioning primitives for supported macOS/Linux direction:

- default dedicated workspace `~/GroX`;
- user-selectable alternate location;
- versioned workspace ownership marker;
- platform-appropriate host configuration/binding;
- idempotent same-workspace commissioning;
- collision and implicit-rebinding refusal;
- recovery of a marked partial commissioning attempt.

NCI-1B then made the runtime/state/work split available beneath Pilot GorXu. Full standalone installed GorXu is **not yet qualified** because canonical runtime assets are not yet packaged into the installed application path. Desktop launchers, the public one-command installer, a bundled general native language model, and offline GorXu qualification also remain future work.

## Reconstitution protocol

A fresh host or sandbox becomes the active flight computer only after the applicable sequence:

1. Restore/reconstitute the current GorXu cognitive identity and Commander context appropriate to the operating mode.
2. Materialize or locate the required verified GroX runtime/source assets.
3. Verify source/state compatibility and restore the latest verified private operational-state snapshot when continuation is required; ancestor-source restoration requires an explicit compatibility allowance.
4. Resolve the commissioned Commander workspace and validate filesystem-role separation where separated operation is used.
5. Run repository/runtime integrity checks and the applicable automated qualification tests.
6. Reconstitute Pilot GorXu on the available qualified cognition path.
7. Confirm the Commander Seat, Crew roster, Mission Control, Tool Gateway, state, and runtime assets are healthy.
8. Resume only from the last committed safe Mission state.

Failure at any recovery gate leaves the Vessel paused rather than silently reconstructing state from model memory.

## Non-negotiable boundaries

- Project memory is cognitive continuity, not executable authority.
- GitHub stores the durable Vessel body, not private raw runtime state.
- Operational snapshots contain no credentials by design and must be treated as private.
- Runtime/assets, state, and Commander work are storage/runtime roles, not command levels.
- Crew storage under runtime assets does not put Crew above GorXu.
- A native or external model may change without replacing GorXu's command role.
- A CLI or desktop launcher may change without creating a second Commander Seat authority or parallel orchestrator.
- A sandbox may disappear without destroying GroX's identity or source.
- A host may change without changing Commander sovereignty, GorXu's position, or GroX doctrine.
- Failure, missing evidence, or degraded cognition may narrow operation or require broader recovery, but never widen authority.
