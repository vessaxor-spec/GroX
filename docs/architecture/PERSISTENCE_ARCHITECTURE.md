# GroX Persistence Architecture

**Qualified release baseline:** `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`. Canonical source continues on `main`. Snapshot source binding, ancestor compatibility control, and fail-closed unrelated-source restore are part of the Apex regression boundary.

## Decision

GroX uses three separate persistence planes. No single sandbox, model process, or conversation is the Vessel's permanent home.

## Plane 1: Cognitive continuity

**Current home:** ChatGPT project `Space Exploration`.

The project holds the durable human/AI operating context needed to reconstitute Pilot GorXu: Commander intent, GroX doctrine, architectural decisions, Apex trajectory, relevant history, and continuity across project conversations.

The active reasoning model occupies the Pilot seat when invoked. The current preferred runtime is **GPT-5.6 Sol with high reasoning**. GorXu is therefore a durable project identity, not one eternal model process or chat thread.

If project cognition is unavailable, the Vessel must degrade to the deterministic GroX control plane. Loss of cognition must never widen authority.

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

## Plane 3: Operational state

Operational state includes Missions, Mission Orders, evidence, Crew tour state, episodic continuity, durable memory, graph checkpoints, exception/recovery state, evaluation state, and cost commitments.

The live SQLite database is `configs/state/grox.sqlite3`.

Operational state is **private runtime data**. It must not be committed raw to the public GitHub repository. GroX exports recoverable `.groxstate` snapshots under `configs/state/snapshots/`, which are ignored by Git.

Each snapshot contains:

- a consistent SQLite backup;
- a versioned manifest;
- SHA-256 integrity evidence;
- the Vessel Git commit when available;
- the cognitive/source binding metadata required to understand what the snapshot belongs to.

Restoration requires explicit confirmation, verifies the snapshot source binding against the active Vessel source, and creates a pre-restore checkpoint before replacing live state. Exact source matches restore normally. A snapshot from a proven ancestor source requires explicit `allow_ancestor=True`; unrelated or unprovable source histories fail closed.

## Reconstitution protocol

A fresh host or sandbox becomes the active flight computer only after this sequence:

1. Restore the Space Exploration project context and GorXu identity.
2. Materialize the latest verified GroX source from GitHub.
3. Verify source/state compatibility and restore the latest verified private operational-state snapshot when continuation is required; ancestor-source restoration requires an explicit compatibility allowance.
4. Run repository integrity checks and the full automated test suite.
5. Reconstitute Pilot GorXu on the active reasoning model.
6. Confirm the Commander Seat, Crew roster, Mission Control, and Tool Gateway are healthy.
7. Resume only from the last committed safe Mission state.

Failure at any recovery gate leaves the Vessel paused rather than silently reconstructing state from model memory.

## Non-negotiable boundaries

- Project memory is cognitive continuity, not executable authority.
- GitHub stores the Vessel body, not private raw runtime state.
- Operational snapshots contain no credentials by design and must be treated as private.
- A sandbox may disappear without destroying GroX's identity or source.
- A model may change without replacing GorXu's command role.
- A host may change without changing Commander sovereignty or GroX doctrine.
