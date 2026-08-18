# GroX Mission Graph

**Qualification status:** **A2 QUALIFIED**, extended by A4 durability and A7 Apex synthesis/budget controls in GroX `v0.8.0`.

A Mission Graph is Pilot GorXu's durable execution structure for work that cannot be represented safely or effectively as one Mission Order.

## Authority

The graph does not create a new command layer.

**Commander → Pilot GorXu → Mission Graph → bounded Mission Orders → Standing Crew**

GorXu owns decomposition, graph mutation, replanning, and final synthesis. The graph scheduler is a mechanical runtime under the Pilot. It cannot widen Commander intent, grant capabilities, invent mutation authority, or become a parallel orchestrator.

A reasoning model may propose a graph. The proposal becomes executable only after GroX validates it against deterministic authority and graph invariants.

## Graph requirements

Every graph must contain:

- the Commander directive preserved verbatim;
- a Mission objective;
- uniquely identified nodes;
- explicit dependencies;
- bounded Crew candidates and required capabilities per node;
- node mode and risk;
- explicit scope;
- node attempt/time budgets;
- Mission node/parallel/replan budgets;
- a hard Mission cost ceiling through `MissionBudget.max_cost_units`, with bounded per-node `cost_units`;
- stop conditions;
- explicit verification nodes where verification is required.

Graphs must be acyclic and all dependencies must resolve to known nodes.

## Node execution

Each runnable node becomes a normal GroX Mission Order. Existing Mission Order rules remain authoritative:

- competence is not permission;
- allowed actions are explicit;
- denied actions remain denied;
- Inspect and Verify cannot mutate;
- Repair nodes require explicit Pilot mutation authorization;
- host policy may narrow authority but never expand it.

Parallel nodes may execute concurrently only when their dependencies are satisfied. A Crew identity must not be assigned to two nodes in the same parallel batch.

## Persistence

Graph node state and graph events are persisted independently of conversational context. Durable state records:

- node payload and dependencies;
- assigned Crew and resulting Mission Order;
- attempt number;
- status transitions;
- graph batches;
- replanning events;
- final Pilot synthesis.

A process restart must not require reconstructing the graph from model memory.

## Bounded replanning

A recoverable runtime or Crew-availability failure may be replanned by GorXu without Commander intervention when:

- the decision is reversible;
- Commander intent does not change;
- authority does not widen;
- the node attempt budget permits another attempt;
- the Mission replan and node budgets permit another node;
- a qualified alternate Crew member exists.

The replacement node receives the same bounded objective, authority, dependencies, risk floor, scope, and stop conditions. Downstream dependencies are rewired to the replacement node and the replan is recorded as evidence.

Policy failures, verification failures, irreversible consequences, missing authority, and other non-recoverable exceptions are not silently retried merely to force completion. They remain Pilot decisions and escalate to the Commander only under the normal GroX escalation rule.

## Verification nodes

Verification is represented as an explicit graph node. The verifier must be independent from the Crew whose evidence it reviews.

A verification node may:

- inspect the resulting Vessel state;
- run permitted tests;
- review dependency evidence;
- record independent pass/fail evidence.

Verification nodes do not receive mutation authority by default.

## Pilot synthesis

After the graph converges, GorXu produces and persists the Mission synthesis. The synthesis records at minimum:

- overall outcome;
- completed and unresolved nodes;
- Crew used;
- replan count;
- verification state;
- evidence classes;
- an executive summary;
- contradiction state and whether material conflicts were independently resolved;
- consumed cost units and the hard Mission cost budget.

Crew reports are inputs to synthesis. No Crew member owns the final Mission conclusion.

## Qualified Apex boundary

A2 established dependency-aware decomposition, parallel scheduling, bounded replanning for recoverable Crew/runtime failures, explicit verification nodes, graph persistence, and Pilot-owned synthesis. Later qualified stages extend that same Pilot-owned graph rather than replacing it:

- A3 supplies experienced eligible-Crew routing and bounded relevant-memory injection;
- A4 supplies durable same-Mission resume, checkpoints, bounded consultation/replan, cancellation, and recovery semantics;
- A7 supplies a hard crash-persistent Mission cost ceiling and independently verified contradiction synthesis.

For A7 synthesis, contradictory `finding` evidence remains attributable to its source Order. A contradiction may be marked resolved only when the contributing source Orders satisfy the required independent verification path. Runtime `graph_verification` evidence is trusted only when it comes from the actual verification-node Order. Repeated findings from one Order are normalized rather than allowed to amplify that source, and equal-weight conflicts remain unresolved.

For A7 budgeting, `MissionBudget.max_cost_units` is enforced as a hard ceiling. Node cost commitments are persisted before execution and aggregate parallel reservations are checked against remaining Mission budget, so crash/restart, recovery consultation, or parallel work cannot reset or silently overcommit the budget.
