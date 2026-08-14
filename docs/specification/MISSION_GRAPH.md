# GroX Mission Graph

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
- an executive summary.

Crew reports are inputs to synthesis. No Crew member owns the final Mission conclusion.

## Current A2 boundary

A2 implements dependency-aware decomposition, parallel scheduling, bounded replanning for recoverable Crew/runtime failures, explicit verification nodes, graph persistence, and structural Pilot synthesis.

Deeper semantic reconciliation of contradictory specialist judgments, learned routing, generalized exception investigation, and exact crash-resume workflow replay remain later Apex stages unless separately promoted by evidence.
