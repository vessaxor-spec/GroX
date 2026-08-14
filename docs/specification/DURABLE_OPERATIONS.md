# GroX Durable Operations and Executive Exception Loop

A4 makes long-running Mission Graphs resumable and gives GorXu a bounded executive exception loop without creating another command layer.

## Authority boundary

The command spine remains:

**Commander → Pilot GorXu → Divisions → Standing Crew**

Durable Operations and the Executive Exception Loop are native services under GorXu. They may preserve state, classify exceptions, request bounded consultation, retry safe work, replan within existing Mission authority, cancel future work, and compensate a journaled mutation. They may not:

- change Commander intent;
- grant new capability or Repair authority;
- lower the Mission risk floor;
- bypass verifier independence;
- continue through unknown mutation state;
- turn a resumable runtime service into a parallel orchestrator.

## Durable Mission Graph state

Every A4 Mission Graph persists:

- the validated graph plan and Commander directive binding;
- global risk and whether Repair was explicitly authorized;
- node state and attempt identity;
- Order state;
- execution checkpoints;
- exception decisions and consultation Orders;
- bounded resume count;
- cancellation state;
- mutation journal entries when Repair occurs.

On process reopen, `running` Missions, Orders, and graph nodes become `interrupted`. Completed nodes remain committed and are not replayed. Interrupted work resumes only from the last persisted state.

A graph may be resumed at most three times automatically. Exhausting that bound returns the Mission to GorXu rather than looping indefinitely.

## Idempotent step identity

Graph Orders receive a stable idempotency key derived from Mission, node, and logical attempt. A process restart does not invent a new mutation identity for the same interrupted step.

Read-only interrupted work is safe to re-execute. Repair work uses the mutation journal described below and is never inferred from conversational history.

## Executive exception loop

Returned exceptions pass through deterministic policy under GorXu:

1. **critical, irreversible, authority-divergent, or material-intent exceptions** → Commander decision;
2. **ordinary recoverable exceptions** such as Crew unavailability, transient failure, timeout, blocker, better/safer path, or missing capability → bounded consultation and eligible-Crew replan when budgets permit;
3. **post-Repair verification failure** → compensate the journaled mutation before halting for Pilot review;
4. **other non-critical exceptions** → Pilot halt without unnecessary Commander escalation.

For an ordinary recoverable graph failure, GorXu compares an eligible replacement through Living Company routing, issues that Crew a real read-only consultation Order against the bounded scope, records the consultation evidence, and only then commits the replan. Consultation cannot widen the failed Order's authority.

## Checkpoints and cancellation

Checkpoints are written around graph start, execution boundaries, recovered interrupted steps, consultations, node commitment, and Pilot synthesis.

Cancellation is checkpoint-bound. Cancelling a durable graph marks future pending/interrupted work cancelled and prevents later resume. It does not claim to preempt an arbitrary host operation already outside GroX's bounded tool boundary.

## Timeout and retry semantics

Tool-level operations own their enforceable timeout. The current test runner is bounded by the graph node time budget and normalizes subprocess timeout as `TimeoutError`, which enters the ordinary recovery policy.

Recoverable execution failure consumes existing node/Mission replan budgets. Process resume is separately bounded to three resumptions. No retry path may widen authority.

## Mutation journal and rollback

Supported `write_text` Repair is atomic and privately journaled in SQLite before mutation. The journal stores:

- stable idempotency key;
- target path;
- whether the target previously existed;
- bounded pre-mutation UTF-8 content for rollback;
- before, intended, and applied hashes;
- lifecycle state: `prepared`, `applied`, `verified`, or `rolled_back`.

Rollback capture is limited to 256 KiB. Larger or non-UTF-8 targets are denied rather than repaired without compensation evidence.

After restart:

- `prepared` + old state means the write may proceed;
- `prepared` + intended state means the atomic write occurred and can be reconciled as applied;
- `applied` + intended hash may continue to verification;
- `verified` + matching state is an idempotent replay;
- any externally diverged state halts and is not overwritten.

If post-Repair tests fail, GroX restores the exact journaled pre-state when the current target still matches the journaled mutation. If rollback itself cannot prove a safe state transition, the condition becomes an irreversible divergence and escalates rather than guessing.

Mutation journal state is private operational state and remains outside public Git.

## A4 qualification

A4 is qualified only when all of the following are demonstrated:

1. a multi-stage Mission is interrupted after at least one committed node;
2. a fresh Pilot instance marks running state interrupted and resumes the same Mission ID;
3. already committed work is not replayed;
4. at least two later ordinary Crew/runtime exceptions are independently recorded, consulted, compared, and replanned within budget;
5. the resumed Mission reaches independent verification and completed closure without Commander escalation;
6. a critical exception produces `needs_commander_decision` without automatic consultation;
7. cancellation prevents subsequent resume;
8. a failed bounded Repair is automatically rolled back to its exact pre-state;
9. an applied repair can resume idempotently, while an externally diverged target is never overwritten;
10. timeout normalization and bounded resume/replan controls remain enforced;
11. all A1-A3 authority, persistence, memory, routing, Tool Gateway, and verification tests remain green.

**Exit gate:** a long-running Mission survives process interruption plus multiple injected exceptions, resumes safely, and reaches independently verified closure without unnecessary Commander escalation.
