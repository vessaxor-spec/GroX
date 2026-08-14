# GroX Mission Order

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

## Inspect mode

Inspect mode is read-and-report by default.

Typical authority:

- read relevant files or state;
- run safe diagnostics and tests;
- gather evidence;
- analyze findings;
- propose resolutions.

Mutation is forbidden unless a diagnostic mutation is explicitly listed and safely reversible.

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

## Execute mode

Execute mode covers bounded work that is neither inspection-only nor a repair mutation. Any side-effecting action remains subject to explicit capability and action grants.

## Verify mode

Verification receives its own Mission Order and authority envelope. A verifier should not receive mutation capability unless remediation of a verification harness is itself the explicit task.

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

An order is complete only when its required outcome, evidence, verification state, exceptions, and final disposition have been recorded in Mission state.
