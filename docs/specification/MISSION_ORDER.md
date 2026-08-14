# GroX Mission Order

A Mission Order is the bounded operational contract through which Pilot GorXu assigns work to Crew.

Required fields include mission/order ids, Commander intent, objective, mode, assigned Crew, required capabilities, allowed/forbidden actions, scope, risk, evidence and verification requirements, stop conditions, exception channel, parent order, and status.

## Authority rule

Crew may use only the intersection of the current Mission Order, registered Crew capabilities, GroX policy, and host restrictions. Deny wins.

## Modes

- `inspect`: read, diagnose, test, gather evidence, propose. Mutation denied by default.
- `repair`: narrow mutation for an explicit repair objective and scope.
- `execute`: bounded non-repair work.
- `verify`: independent assessment; mutation denied unless explicitly required by the verification task.

## Exception protocol

Blockers, better/safer paths, missing capability, elevated risk, collateral scope, conflict with Commander intent, irreversible consequences, or completion-blocking uncertainty return to GorXu before affected mutation continues.
