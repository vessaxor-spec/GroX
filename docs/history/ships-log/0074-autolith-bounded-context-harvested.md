# Ship's Log 0074 — Autolith bounded-context technique harvested

**Date:** 2026-10-02

The Commander asked whether useful techniques from `sylvesterroos/autolith` could be integrated into GroX.

The user fork was inspected at `e5f6610b6a67b3f9b31285a06efd6e714db95810`. Because that fork is a September 23 snapshot, current upstream `lambda-symbolics/autolith@ef110edc66e04cc7c263bba3c9ce66845dc0a692` was also inspected to avoid harvesting obsolete behavior.

The review used GroX's existing `ADOPT | ADAPT | HARVEST | REJECT` intake convention.

The first accepted seam was Autolith's content-addressed, read-only context-view discipline. GroX did not import Autolith's Lisp runtime, recursive child agents, self-modifying image, generation mechanism, or command structure. Instead issue #211 / PR #212 implemented a dependency-free GroX-native primitive:

- immutable content-addressed context objects with deterministic SHA-256 identity;
- metadata-only references exposing label, digest and character count without raw content;
- exact bounded slice/search views carrying source digest and offsets;
- shared fail-closed operation/character budgets;
- no provider, network, filesystem, Mission or authority behavior.

The primitive is designed to support NCI-4A Mission Decision Packets and future long-context work without turning context retrieval into authority or adding another orchestrator.

PR #212 exact final head `441f5c4707200afd09a1d6dde15496e34eba42f0` passed GroX CI #665. The permanent critical mutation `context-object-reference-no-raw-content` was killed. PR #212 merged as `main@74c605202115d2094688cdc7492b74bc60edb888`, tree `74f1df28280e3d1e5c23e668e2c8ffa83c6f5a49`, and protected-main GroX CI #666 passed all five required jobs. The critical invariant matrix is now 43/43.

Two further seams are retained as separate bounded follow-ups: #213 for provider prompt-cache health telemetry and #214 for a GroX-native crash-safe pending Commander-input vault. Recursive inference remains deferred.

Autolith's live self-modification/generation model and child-agent command architecture were explicitly rejected for GroX because they would duplicate or weaken the canonical protected-source and Commander → Pilot GorXu → Divisions → Standing Crew authority model.
