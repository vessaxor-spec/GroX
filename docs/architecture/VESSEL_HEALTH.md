# GroX Vessel Health Architecture

## Purpose

Vessel Health gives GorXu and the Commander one diagnostic view of whether the current GroX materialization is safe to operate or reconstitute. It is an observation surface over existing authoritative systems, not a new command layer, policy engine, repair agent, memory plane, or source of truth.

The provisional user surface is:

```text
grox health
grox health --json
```

Health inspection is read-only by design. A finding may recommend a bounded next action, but the health layer cannot grant Mission authority, issue Repair permission, alter routing, mutate state, activate an A6 proposal, or repair the Vessel.

## Evidence model

Each detector returns an independent `HealthCheck` with:

- stable check identifier;
- domain;
- status;
- human-readable detail;
- whether the check protects a critical boundary;
- compact attributable evidence when useful;
- optional recommendation.

Statuses are:

- **PASS** — the detector directly observed the expected condition;
- **WARN** — a bounded degradation or recovery condition exists, but the observed condition is not itself a critical integrity failure;
- **FAIL** — a critical or explicit integrity condition failed;
- **UNKNOWN** — the detector cannot establish the condition from available evidence.

`UNKNOWN` never means healthy.

Overall disposition is intentionally simple:

- any `FAIL` → **UNHEALTHY**;
- otherwise any `WARN` or `UNKNOWN` → **DEGRADED**;
- otherwise → **HEALTHY**.

Individual findings remain visible regardless of the overall disposition. A composite result may not hide an authority, recovery, command-integrity, memory-integrity, or source-integrity failure.

## Detector isolation

Every detector executes through an isolation wrapper. If one detector raises unexpectedly, only that check becomes `FAIL` when critical or `UNKNOWN` when non-critical. Remaining detectors still run.

This is part of the Stage 1 detector-quality discipline: a malformed subsystem or diagnostic path must not blind the entire health surface.

## Read-only operational-state rule

Constructing `PilotGorXu` or `StateStore` is inappropriate for passive health inspection because normal `StateStore` initialization performs crash-recovery transitions for on-duty Crew, running Missions, and running graph nodes.

Vessel Health therefore opens the private SQLite state using SQLite read-only URI mode when the database exists. It never creates an absent database.

Tests hash the database before and after health collection to prove that a health read does not alter it.

## Health domains

### Command integrity

Source evidence:

- active Crew dossiers;
- `configs/crew/company-manifest.json`.

The detector reconstructs the source roster without a state store and verifies:

- expected Standing Crew count;
- exact manifest/roster identity agreement;
- one native `independent-verifier` identity.

Normal roster admission still enforces the sole-orchestrator semantic identity rule. Health reuses that production path rather than duplicating Crew admission logic.

### Operational state

Private-state evidence:

- SQLite `PRAGMA integrity_check`;
- Mission statuses;
- Mission Graph node statuses.

Interrupted records are surfaced as recovery work rather than silently normalized. An absent private database is valid for a source-only materialization and is not created by the detector.

### Persistence readiness

Evidence:

- presence of private operational history;
- latest private `.groxstate` snapshot when one exists;
- existing `PersistenceManager.verify_snapshot` source/integrity checks.

Operational history without a recovery snapshot is a warning. A present snapshot is verified through the existing persistence implementation; health does not invent a second snapshot validator.

### Authority integrity

Evidence:

- `configs/tool-policy.json`;
- persisted Mission Orders when private state exists.

The detector checks the qualified Tool Gateway policy version, memory-only secret persistence, and persisted Orders for impossible authority widening such as filesystem or MCP mutation grants carried by a non-Repair Order.

This is diagnostic defense in depth. Normal `MissionOrder` construction and Tool Gateway enforcement remain the authority-bearing controls.

### Memory integrity

Evidence:

- active private GroX memories.

The detector validates active memory provenance, supported memory kind/scope, Crew/Vessel scoping consistency, confidence bounds, and duplicate active memory keys. It does not consolidate, rewrite, forget, or reactivate memory.

### Source/version integrity

Evidence:

- `pyproject.toml` package version;
- imported `grox.__version__`;
- source `src/grox/__init__.py` declaration.

Version disagreement is critical. Git metadata is a separate non-critical source observation: when available, health reports HEAD and dirty-worktree state; when unavailable, the repository binding is `UNKNOWN` rather than inferred.

### Verification readiness

Source evidence:

- canonical CI workflow;
- Stage 1 critical mutation harness;
- canonical mutation matrix.

This check establishes that the source materialization still contains the regression, wheel-bootstrap, and continuous critical-detector proof machinery. It does not claim that a historical remote CI run is fresh merely because workflow source exists.

### Isolation readiness

Environment evidence:

- qualified namespace backend probe;
- configured pre-provisioned pinned Docker fallback probe.

If neither is available, health reports `WARN`: governed workspace execution is unavailable and will fail closed. Health never pulls an image or changes the host to make the check green.

### Recovery readiness

Recovery readiness is derived from the preceding direct checks rather than re-reading state independently.

Critical command, operational-integrity, authority, memory, or source-version failure keeps reconstitution paused. Interrupted state or incomplete persistence readiness requires a bounded/full recovery path. A PASS means no currently observed critical health condition blocks bounded reconstitution; it is not permission to bypass the ordinary recovery protocol.

## Mutation proof

Stage 2 adds a dedicated health mutation harness, run inside the required Python 3.12 CI gate after the full regression suite and the Stage 1 critical-invariant proof.

Critical health behaviors are deliberately weakened in the CI checkout and their production-path regressions must turn red. The harness then restores exact bytes, reruns the detector green, and requires the mutated source path to be Git-clean.

The initial Stage 2 red CI caused by an ineffective test-fixture mutation is retained as evidence: the test attempted to replace a package-version string that did not match the actual `pyproject.toml` formatting. The correction added an assertion proving the fixture mutation actually changes source before the detector is evaluated. This follows the same rule established in Stage 1: a test that has not been observed failing for the intended reason is not sufficient evidence.

## Authority boundary

Vessel Health cannot:

- issue or alter Mission Orders;
- wake or route Crew;
- write operational state;
- create or restore snapshots;
- change Tool Gateway policy;
- activate evaluation proposals;
- mutate repository source;
- widen Commander, GorXu, Crew, verifier, or tool authority.

Any repair prompted by a health finding remains a separate Commander/GorXu-authorized Mission with normal Repair, evidence, verification, and protected-source controls.
