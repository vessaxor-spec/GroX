# Ship's Log 0055 — Runtime Integrity Repair Canaries

**Date:** 2026-08-18
**Status:** IN PROGRESS — EXACT-HEAD QUALIFICATION REQUIRED

An isolated sandbox qualification of canonical `main@8470a715a0bc37877013608c9daa178acfa4cbab` reproduced three runtime-integrity defects now tracked by issue #63: post-Repair verification timeout could leave a mutation applied, explicitly authorized Mission Graph Repair crossed a Pilot-owned SQLite connection into a worker thread, and snapshot-present Vessel Health consumed fields not exposed by `SnapshotReport`.

Focused red regressions were written before repair. The bounded repair candidate makes all four focused cases green locally: timeout rollback, authorized Graph Repair journaling, valid snapshot readiness, and invalid snapshot readiness.

## Preserved red canaries

During local mutation qualification, the sandbox execution ceiling interrupted deliberate mutation harnesses before their restore phases. Static PR inspection subsequently caught two temporary critical graph mutants that had been carried into the first branch candidate: reserved `graph_verification` evidence filtering had been weakened and the hard graph cost ceiling comparison had been altered. Neither mutant reached `main`.

Both were restored exactly to canonical behavior before qualification continued. The corrected PR diff retains only the authorized issue #63 repair. This incident is evidence for preserving red-canary discipline: interrupted mutation runs must be treated as potentially dirty until source is compared against a trusted committed baseline.

## Qualification boundary

Local sandbox evidence is supportive, not canonical merge evidence. Exact-head GitHub CI must complete all required interpreter, wheel, mutation, health, reconstitution, drift, provenance, and integrated Post-Apex gates before PR #65 can merge. Post-merge CI on the exact resulting `main` SHA is required before issue #63 can be closed.

No release/tag/version moved, no authority widened, no Crew roster changed, and no A8 or new Apex stage was created or implied. Issue #64 remains a separate policy question and is not implemented by this repair.