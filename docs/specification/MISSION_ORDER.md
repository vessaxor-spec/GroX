# GroX Mission Order

**Current contract status:** qualified and regression-protected in GroX `v0.8.0`. Issued authority is immutable; post-issuance scope, grant, verifier, stop-condition, or nested parameter widening requires a newly issued Order through GorXu. Canonical source may advance beyond the immutable release through protected `main`.

A Mission Order is the bounded operational contract through which Pilot GorXu assigns work to Crew.

## Required fields

A Mission Order should contain, at minimum:

- `mission_id`
- `order_id`
- `commander_intent`
- `objective`
- `mode`: `inspect`, `repair`, `execute`, `verify`, or another explicitly defined GroX mode
- `assigned_crew`
- `required_capabilities`
- `allowed_actions`
- `forbidden_actions`
- `scope`
- `risk_class`
- `evidence_requirements`
- `verification_requirements`
- `stop_conditions`
- `exception_channel`: GorXu
- `parent_order_id` when delegated from another Mission slice
- `status`

## Authority rule

A Crew member may use only the intersection of:

1. the authority in the current Mission Order;
2. the Crew member's registered capabilities;
3. GroX constitutional and Mission Control policy;
4. host-level restrictions.

If any layer denies an action, the action is denied.

## Issuance immutability

A Mission Order is an immutable issued authority contract. Authority-bearing scalar and list fields are snapshotted at construction, including required capabilities, allowed and forbidden actions, scope, evidence and verification requirements, stop conditions, risk, mode, and assigned Crew. Operation parameters are deep-copied at construction, may receive bounded pre-issuance context, and are deep-frozen when the Order is persisted or first used by the Tool Gateway.

Runtime code must not widen a sealed Order in place. A broader scope, different grant, changed verifier requirement, or altered parameter envelope requires a newly issued bounded Order through GorXu. Serialization preserves the external JSON list/object shapes even though the sealed in-memory authority envelope is immutable.

### Pre-issuance Crew context

Before persistence/sealing, GorXu's Living Company service may add bounded competence context to Order parameters, including:

- task-class metadata;
- selected relevant Crew memory;
- selected Mission-relevant sections from the assigned Standing Crew member's canonical craft card;
- attribution metadata such as craft digest, selected headings, selected size, source revision, and freshness policy.

This context is not authority-bearing. It cannot add an allowed action, remove a forbidden action, expand scope, lower risk, change mode, grant a capability, replace the assigned Crew, or satisfy an independent-verifier requirement. Once the Order is sealed, the contextual parameter envelope is immutable with the rest of the issued Order.

A separately supplied Crew cognition provider receives a sanitized copy of the Order authority envelope rather than arbitrary internal parameters. Provider-local mutation of that copy has no effect on the sealed Order.

## Inspect mode

Inspect mode is read-and-report by default.

Typical authority:

- read relevant files or state;
- run safe diagnostics and tests;
- gather evidence;
- analyze findings;
- propose resolutions.

Mutation is forbidden unless a diagnostic mutation is explicitly listed and safely reversible.

A bounded optional Crew cognition provider may assist an Inspect tour using selected craft, selected memory, and governed observations. The provider is not a new authority source. Its action requests must still be present in the sealed Order and pass the existing Tool Gateway. The first bounded seam permits only `fs_list`, `fs_read`, and `test_run`, with hard step/output/test-run limits and Mission-scope confinement. Policy denial fails closed; recoverable provider failure may degrade to the existing deterministic Inspect executor without authority widening.

## Repair mode

Repair mode grants narrow mutation authority for a defined finding or approved repair objective.

A repair order must make clear:

- exactly what outcome is authorized;
- where mutation may occur;
- which tools may be used;
- what must not be changed;
- definition of done;
- evidence required;
- stop conditions.

There is no implicit "while I am here" authority.

The first bounded Crew cognition seam does not operate in Repair mode. A cognitive-provider output cannot create or infer Repair permission.

## Execute mode

Execute mode covers bounded work that is neither inspection-only nor a repair mutation. Any side-effecting action remains subject to explicit capability and action grants.

A generic Execute directive that has no explicitly governed operation may complete only a bounded context inventory. In the single-Mission Pilot path, that execution is reported at Mission level as `scan_only`, not as proof that the Commander objective was delivered.

The first bounded Crew cognition seam does not replace or reinterpret Execute behavior.

## Mission outcome versus Order execution

Order execution state and Commander-facing Mission outcome are separate facts.

A bounded Order may finish its permitted work successfully while the wider Commander objective remains `not_delivered` or `not_proven`. Pilot GorXu therefore persists a `mission_outcome` evidence record for the single-Mission path with:

- `execution` — executor lifecycle result;
- `effect` — what the bounded execution actually did;
- `objective` — whether Commander-objective delivery was satisfied, not delivered, or not proven;
- `mutation` — whether a mutation remains in the resulting state;
- `next_authority` — any narrower authority path required to continue;
- `verification_scope` — what the verification result actually covers.

A generic inventory fallback under Execute is `effect: scan_only`, `objective: not_delivered`, and `mutation: false`. If verification is required in that path, a PASS proves the bounded execution evidence only; it does not transform the scan into objective delivery.

For supported Repair, successful verified mutation may satisfy the bounded objective. If Repair fails after mutation, outcome reporting is conservative: a completed rollback reports `mutation_rolled_back` with no remaining mutation, while failed rollback or divergent mutation state reports `mutation_state_unresolved`, `mutation: true`, and returns control to Pilot recovery.

Outcome classification never grants authority. Explicit Repair remains the mutation authority path.

## Verify mode

Verification receives its own Mission Order and authority envelope. A verifier should not receive mutation capability unless remediation of a verification harness is itself the explicit task.

The first bounded Crew cognition seam does not run in Verify mode. Controlled Crew cognition therefore cannot become an alternate automatic verifier or satisfy an independence requirement by itself.

## Exception protocol

Crew must stop the affected mutation and report to GorXu when they encounter:

- a blocker;
- a materially better or safer path;
- missing capability;
- elevated risk;
- unexpected collateral scope;
- conflict with Commander intent;
- an irreversible consequence not already authorized;
- uncertainty that prevents reliable completion.

The report should include evidence, impact, options, and a recommendation where possible.

GorXu may:

1. authorize a revised bounded order;
2. consult additional Crew or Mission Control;
3. assign another Crew member;
4. require independent verification or research;
5. abandon or defer the affected path;
6. escalate to the Commander when the issue is critical, irreversible, or materially changes intent.

## Closure

An Order is closed only when its bounded execution, evidence, verification state, exceptions, and final disposition have been recorded. Order closure does not by itself prove the wider Commander objective was delivered; Mission synthesis records that separately and must not overstate it.
