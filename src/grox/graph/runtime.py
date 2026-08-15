from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
from dataclasses import replace
from time import perf_counter
from typing import Any

from ..contracts import Evidence, MissionMode, MissionOrder, RiskClass, TourResult
from ..crew.roster import CrewDossier, CrewRoster
from ..mission_control.core import MissionControl
from ..runtime.executor import CrewExecutor
from ..state import StateStore
from ..durable_state import DurableState
from ..verification.core import IndependentVerifier
from ..intelligence import LivingCompanyIntelligence, RoutingDecision
from ..operations import ExecutiveExceptionLoop, ExceptionDecision
from .contracts import GraphNodeOutcome, GraphNodeSpec, MissionGraphPlan, PilotSynthesis

_RISK_RANK = {RiskClass.low: 0, RiskClass.medium: 1, RiskClass.high: 2, RiskClass.critical: 3}
_A5_ACTION_CAPABILITY = {
    "workspace_exec": "workspace_exec",
    "secret_use": "secret_use",
    "net_fetch": "net_fetch",
    "browser_capture": "browser_capture",
    "mcp_call": "mcp_call",
    "mcp_mutate": "mcp_mutate",
}


class GraphExecutionError(RuntimeError):
    pass


class MissionGraphRunner:
    """Mechanical graph scheduler under Pilot GorXu authority.

    The runner cannot invent Commander intent or widen authority. It executes a
    validated Pilot-owned graph, persists every node transition, and returns
    recoverable exceptions to the Pilot recovery policy implemented here.
    """

    def __init__(
        self,
        *,
        store: StateStore,
        roster: CrewRoster,
        executor: CrewExecutor,
        mission_control: MissionControl,
        verifier: IndependentVerifier,
        intelligence: LivingCompanyIntelligence,
        exception_loop: ExecutiveExceptionLoop,
        durable: DurableState,
    ):
        self.store = store
        self.roster = roster
        self.executor = executor
        self.mission_control = mission_control
        self.verifier = verifier
        self.intelligence = intelligence
        self.exception_loop = exception_loop
        self.durable = durable

    def _effective_risk(self, global_risk: RiskClass, node_risk: RiskClass) -> RiskClass:
        return node_risk if _RISK_RANK[node_risk] > _RISK_RANK[global_risk] else global_risk

    def _required_caps(self, spec: GraphNodeSpec) -> list[str]:
        required = list(dict.fromkeys(spec.required_capabilities or ["repo_read"]))
        if spec.mode is MissionMode.verify and "verify" not in required:
            required.append("verify")
        return required

    def _select_crew(self, spec: GraphNodeSpec, *, exclude: set[str], dependency_crew: set[str], risk: RiskClass) -> RoutingDecision:
        required = self._required_caps(spec)
        verifier = spec.mode is MissionMode.verify
        excluded = set(exclude)
        if verifier:
            excluded |= dependency_crew
        return self.intelligence.route(
            spec.objective, required, exclude=excluded, verifier=verifier, risk=risk,
            preferred_ids=spec.candidate_crew_ids,
        )

    def _allowed_actions(self, spec: GraphNodeSpec) -> list[str]:
        actions = self.mission_control.default_actions(spec.mode)
        # Graph inspection branches do not each rerun the full test suite unless
        # requested. Verification nodes retain test execution by default.
        if spec.mode is MissionMode.inspect and not spec.parameters.get("run_tests"):
            actions = [x for x in actions if x != "test_run"]
        required = set(self._required_caps(spec))
        for action in spec.allowed_actions:
            capability = _A5_ACTION_CAPABILITY.get(action)
            if capability is None:
                raise GraphExecutionError(f"graph node {spec.node_id} requested unsupported explicit action: {action}")
            if capability not in required:
                raise GraphExecutionError(
                    f"graph node {spec.node_id} requested {action} without required Crew capability {capability}"
                )
            if action == "mcp_mutate" and spec.mode is not MissionMode.repair:
                raise GraphExecutionError(f"graph node {spec.node_id}: mutating MCP action requires explicit Repair authority")
            actions.append(action)
        return list(dict.fromkeys(actions))

    def _make_order(
        self,
        mission_id: str,
        directive: str,
        spec: GraphNodeSpec,
        crew: CrewDossier,
        global_risk: RiskClass,
        parent_order_id: str | None = None,
        attempt: int = 1,
    ) -> MissionOrder:
        risk = self._effective_risk(global_risk, spec.risk_class)
        required = self._required_caps(spec)
        return MissionOrder.new(
            mission_id,
            directive,
            spec.objective,
            spec.mode,
            crew.crew_id,
            required_capabilities=required,
            allowed_actions=self._allowed_actions(spec),
            forbidden_actions=[] if spec.mode is MissionMode.repair else ["fs_write"],
            scope=list(spec.scope),
            risk_class=risk,
            verification_requirements=["independent"] if spec.mode is MissionMode.verify else [],
            stop_conditions=list(spec.stop_conditions),
            parent_order_id=parent_order_id,
            parameters={
                **dict(spec.parameters),
                "_graph_max_seconds": spec.budget.max_seconds,
                "_idempotency_key": f"{mission_id}:{spec.node_id}:{attempt}",
            },
        )

    def _execute_prepared(
        self,
        spec: GraphNodeSpec,
        order: MissionOrder,
        dependency_results: list[TourResult],
    ) -> TourResult:
        result = self.executor.execute(order)
        if spec.mode is not MissionMode.verify or result.status != "completed":
            return result

        checks: list[dict[str, Any]] = []
        ok = True
        for dependency in dependency_results:
            dep_ok, message = self.verifier.verify(dependency.crew_id, order.assigned_crew, dependency)
            checks.append({
                "order_id": dependency.order_id,
                "executor": dependency.crew_id,
                "verifier": order.assigned_crew,
                "ok": dep_ok,
                "message": message,
            })
            ok = ok and dep_ok
        result.evidence.append(Evidence("graph_verification", {"ok": ok, "checks": checks}))
        if not ok:
            result.status = "exception"
            result.summary += "; dependency verification failed"
            result.exception = {
                "type": "verification_failure",
                "recommendation": "Return to GorXu; do not continue dependent work",
            }
        return result

    def _consult_recovery(
        self,
        *,
        mission_id: str,
        directive: str,
        spec: GraphNodeSpec,
        failed_order_id: str,
        crew: CrewDossier,
        risk: RiskClass,
        cost_units: float = 0.0,
    ) -> tuple[str | None, TourResult]:
        objective = f"Consult bounded recovery evidence for: {spec.objective}"
        order = MissionOrder.new(
            mission_id, directive, objective, MissionMode.inspect, crew.crew_id,
            required_capabilities=['repo_read'], allowed_actions=['fs_list','fs_read'],
            forbidden_actions=['fs_write'], scope=list(spec.scope), risk_class=risk,
            parent_order_id=failed_order_id,
            stop_conditions=['elevated_risk','scope_change','irreversible_consequence'],
            parameters={'_exception_consultation': True, '_task_class': self.intelligence.task_class(spec.objective)},
        )
        memory_meta = self.intelligence.inject_order_context(order, objective)
        self.store.save_order(order)
        if cost_units > 0.0:
            self.store.add_graph_event(mission_id, 'cost_committed', {
                'kind': 'recovery_consultation', 'node_id': spec.node_id, 'order_id': order.order_id,
                'attempt': None, 'cost_units': cost_units,
            }, node_id=spec.node_id)
        self.store.add_evidence(mission_id, order.order_id, Evidence('exception_consultation', {
            'failed_order_id': failed_order_id, 'failed_node': spec.node_id, 'consulted_crew': crew.crew_id,
        }))
        self.store.add_evidence(mission_id, order.order_id, Evidence('memory_selection', memory_meta))
        self.store.crew_on_duty(crew.crew_id, mission_id)
        self.store.update_order(order.order_id, 'running')
        self.durable.checkpoint(mission_id, 'exception_consultation', 'running', node_id=spec.node_id, order_id=order.order_id)
        started = perf_counter()
        result = self.executor.execute(order)
        latency_ms = (perf_counter() - started) * 1000.0
        for ev in result.evidence:
            self.store.add_evidence(mission_id, order.order_id, ev)
        self.store.update_order(order.order_id, result.status)
        self.store.crew_sleep(crew.crew_id, mission_id, result.summary)
        self.intelligence.record_performance(
            crew_id=crew.crew_id, mission_id=mission_id, order_id=order.order_id,
            task_class=order.parameters.get('_task_class', 'general'), result=result,
            latency_ms=latency_ms, risk=risk, verified=None, cost_units=cost_units,
        )
        self.durable.checkpoint(
            mission_id, 'exception_consultation', result.status, node_id=spec.node_id,
            order_id=order.order_id, payload={'summary': result.summary},
        )
        return order.order_id, result

    def _restore_execution(
        self,
        mission_id: str,
    ) -> tuple[
        dict[str, GraphNodeSpec], dict[str, str], dict[str, int],
        dict[str, GraphNodeOutcome], dict[str, TourResult], int, set[str]
    ]:
        rows = self.store.graph_nodes(mission_id)
        if not rows:
            raise GraphExecutionError('durable Mission Graph has no persisted nodes')
        specs: dict[str, GraphNodeSpec] = {}
        statuses: dict[str, str] = {}
        attempts: dict[str, int] = {}
        outcomes: dict[str, GraphNodeOutcome] = {}
        tour_results: dict[str, TourResult] = {}
        used_crew: set[str] = set()
        for row in rows:
            spec = GraphNodeSpec.from_mapping(json.loads(row['payload']))
            specs[row['node_id']] = spec
            status = row['status']
            statuses[row['node_id']] = status
            attempts[row['node_id']] = int(row['attempt']) or 1
            if row.get('crew_id'):
                used_crew.add(row['crew_id'])
            if status == 'completed' and row.get('order_id') and row.get('crew_id'):
                persisted = self.durable.order_result(row['order_id'])
                evidence = []
                if persisted:
                    evidence = [Evidence(ev['kind'], ev['content']) for ev in persisted['evidence']]
                result = TourResult(row['order_id'], row['crew_id'], 'completed', f"Recovered committed node {row['node_id']}", evidence)
                outcome = GraphNodeOutcome(
                    node_id=row['node_id'], order_id=row['order_id'], crew_id=row['crew_id'],
                    status='completed', summary=result.summary,
                    evidence_kinds=sorted({ev.kind for ev in evidence}), attempt=attempts[row['node_id']],
                )
                outcomes[row['node_id']] = outcome
                tour_results[row['node_id']] = result
            elif status == 'interrupted':
                statuses[row['node_id']] = 'pending'
                self.store.update_graph_node(mission_id, row['node_id'], 'pending', attempt=attempts[row['node_id']])
                self.durable.checkpoint(
                    mission_id, 'resume_interrupted_step', 'pending', node_id=row['node_id'],
                    attempt=attempts[row['node_id']], order_id=row.get('order_id'),
                    payload={'mode': spec.mode.value, 'idempotent_replay': True},
                )
        replan_count = sum(1 for ev in self.store.graph_events(mission_id) if ev['event_type'] == 'pilot_replan')
        return specs, statuses, attempts, outcomes, tour_results, replan_count, used_crew

    def _rewire_downstream(
        self,
        mission_id: str,
        specs: dict[str, GraphNodeSpec],
        old_node_id: str,
        replacement_node_id: str,
        statuses: dict[str, str],
    ) -> None:
        for node_id, spec in list(specs.items()):
            if statuses.get(node_id) not in {"pending", "ready"}:
                continue
            if old_node_id not in spec.dependencies:
                continue
            dependencies = [replacement_node_id if d == old_node_id else d for d in spec.dependencies]
            updated = replace(spec, dependencies=dependencies)
            specs[node_id] = updated
            self.store.update_graph_node(
                mission_id,
                node_id,
                statuses[node_id],
                dependencies=dependencies,
                payload=updated.to_dict(),
            )

    def _try_replan(
        self,
        *,
        mission_id: str,
        directive: str,
        failed_spec: GraphNodeSpec,
        failed_outcome: GraphNodeOutcome,
        failed_result: TourResult,
        specs: dict[str, GraphNodeSpec],
        statuses: dict[str, str],
        attempts: dict[str, int],
        used_crew: set[str],
        replan_count: int,
        plan: MissionGraphPlan,
        global_risk: RiskClass,
    ) -> tuple[str | None, int]:
        effective_risk = self._effective_risk(global_risk, failed_spec.risk_class)
        exc_type = str((failed_result.exception or {}).get('type') or 'unknown')
        decision = self.exception_loop.decide(
            risk=effective_risk, result=failed_result, mutation=failed_spec.mode is MissionMode.repair,
        )
        if decision.disposition != 'consult_then_replan':
            self.exception_loop.persist(
                mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
                exception_type=exc_type, risk=effective_risk, decision=decision,
            )
            return None, replan_count
        current_attempt = attempts[failed_spec.node_id]
        budget_reason = None
        if current_attempt >= failed_spec.budget.max_attempts:
            budget_reason = 'node attempt budget exhausted'
        elif replan_count >= plan.budget.max_replans:
            budget_reason = 'Mission replan budget exhausted'
        elif len(specs) + 1 > plan.budget.max_nodes:
            budget_reason = 'Mission node budget exhausted'
        if budget_reason:
            halted = ExceptionDecision('pilot_halt', budget_reason)
            self.exception_loop.persist(
                mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
                exception_type=exc_type, risk=effective_risk, decision=halted,
            )
            return None, replan_count

        try:
            replacement_decision = self._select_crew(
                failed_spec, exclude={failed_outcome.crew_id}, dependency_crew=set(), risk=effective_risk,
            )
            replacement = replacement_decision.crew
        except LookupError:
            halted = ExceptionDecision('pilot_halt', 'no eligible replacement Crew remains within the Mission authority envelope')
            self.exception_loop.persist(
                mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
                exception_type=exc_type, risk=effective_risk, decision=halted,
            )
            return None, replan_count

        self.store.add_evidence(
            mission_id, failed_outcome.order_id,
            Evidence('recovery_comparison', {
                'failed_crew': failed_outcome.crew_id, 'candidate': replacement_decision.to_dict(),
                'exception_type': exc_type,
            }),
        )
        consultation_cost = max(0.0, float(failed_spec.budget.cost_units))
        spent_cost = self._committed_cost(mission_id)
        if spent_cost + consultation_cost > plan.budget.max_cost_units + 1e-12:
            reason = 'Mission cost budget exhausted before recovery consultation'
            self.store.add_graph_event(mission_id, 'cost_budget_exhausted', {
                'spent_cost_units': spent_cost, 'max_cost_units': plan.budget.max_cost_units,
                'blocked_node': failed_spec.node_id, 'required_cost_units': consultation_cost,
                'phase': 'recovery_consultation',
            }, node_id=failed_spec.node_id)
            halted = ExceptionDecision('pilot_halt', reason)
            self.exception_loop.persist(
                mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
                exception_type=exc_type, risk=effective_risk, decision=halted,
            )
            return None, replan_count
        consultation_order_id, consultation = self._consult_recovery(
            mission_id=mission_id, directive=directive, spec=failed_spec,
            failed_order_id=failed_outcome.order_id, crew=replacement, risk=effective_risk,
            cost_units=consultation_cost,
        )
        if consultation.status != 'completed':
            halted = ExceptionDecision('pilot_halt', 'bounded recovery consultation failed; do not continue automatically')
            self.exception_loop.persist(
                mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
                exception_type=exc_type, risk=effective_risk, decision=halted,
                consulted_crew=replacement.crew_id, consultation_order_id=consultation_order_id,
            )
            return None, replan_count
        self.exception_loop.persist(
            mission_id=mission_id, node_id=failed_spec.node_id, order_id=failed_outcome.order_id,
            exception_type=exc_type, risk=effective_risk, decision=decision,
            consulted_crew=replacement.crew_id, consultation_order_id=consultation_order_id,
        )
        used_crew.add(replacement.crew_id)

        new_attempt = current_attempt + 1
        replacement_id = f"{failed_spec.node_id}__replan{new_attempt - 1}"
        while replacement_id in specs:
            new_attempt += 1
            replacement_id = f"{failed_spec.node_id}__replan{new_attempt - 1}"
        recovery_spec = replace(failed_spec, node_id=replacement_id, candidate_crew_ids=[replacement.crew_id])
        specs[replacement_id] = recovery_spec
        statuses[replacement_id] = 'pending'
        attempts[replacement_id] = new_attempt
        self.store.save_graph_node(
            mission_id, replacement_id, payload=recovery_spec.to_dict(), dependencies=recovery_spec.dependencies,
            status='pending', attempt=new_attempt, crew_id=replacement.crew_id,
        )
        statuses[failed_spec.node_id] = 'replanned'
        self.store.update_graph_node(mission_id, failed_spec.node_id, 'replanned')
        self._rewire_downstream(mission_id, specs, failed_spec.node_id, replacement_id, statuses)
        replan_count += 1
        self.store.add_graph_event(
            mission_id, 'pilot_replan', {
                'failed_node': failed_spec.node_id, 'replacement_node': replacement_id,
                'failed_crew': failed_outcome.crew_id, 'replacement_crew': replacement.crew_id,
                'exception_type': exc_type, 'reason': 'consulted recoverable Crew/runtime failure',
                'consultation_order_id': consultation_order_id, 'replan_number': replan_count,
            }, node_id=failed_spec.node_id,
        )
        return replacement_id, replan_count

    def _committed_cost(self, mission_id: str) -> float:
        total = 0.0
        for event in self.store.graph_events(mission_id):
            if event['event_type'] != 'cost_committed':
                continue
            try:
                payload = json.loads(event['content'])
                value = float(payload.get('cost_units', 0.0))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if math.isfinite(value) and value > 0.0:
                total += value
        return total

    def _reconcile_contradictions(
        self, tour_results: dict[str, TourResult], *, verification_passed: bool,
    ) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for result in tour_results.values():
            for evidence in result.evidence:
                if evidence.kind != 'finding' or not isinstance(evidence.content, dict):
                    continue
                topic = evidence.content.get('topic')
                position = evidence.content.get('position')
                claim = evidence.content.get('claim')
                if not all(isinstance(value, str) and value.strip() for value in (topic, position, claim)):
                    continue
                try:
                    confidence = float(evidence.content.get('confidence', 0.0))
                    quality = float(evidence.content.get('evidence_quality', 0.0))
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(confidence) or not math.isfinite(quality):
                    continue
                confidence = min(1.0, max(0.0, confidence))
                quality = min(1.0, max(0.0, quality))
                weight = confidence * quality
                grouped.setdefault(topic.strip(), []).append({
                    'order_id': result.order_id, 'crew_id': result.crew_id,
                    'position': position.strip(), 'claim': claim.strip(),
                    'confidence': confidence, 'evidence_quality': quality, 'weight': weight,
                })

        reconciled: list[dict[str, Any]] = []
        for topic in sorted(grouped):
            sources = grouped[topic]
            positions = sorted({source['position'] for source in sources})
            if len(positions) < 2:
                continue
            scores = {position: 0.0 for position in positions}
            for source in sources:
                scores[source['position']] += source['weight']
            ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
            total = sum(scores.values())
            unique_winner = len(ranked) == 1 or not math.isclose(ranked[0][1], ranked[1][1], rel_tol=0.0, abs_tol=1e-12)
            resolved = verification_passed and total > 0.0 and unique_winner
            selected = ranked[0][0] if resolved else None
            calibrated = (ranked[0][1] / total) if resolved and total > 0.0 else 0.0
            reconciled.append({
                'topic': topic,
                'status': 'resolved' if resolved else 'unresolved',
                'selected_position': selected,
                'confidence': calibrated,
                'position_scores': {key: scores[key] for key in sorted(scores)},
                'sources': sorted(sources, key=lambda source: (source['position'], source['crew_id'], source['order_id'])),
                'basis': 'eligible Crew finding evidence ranked by confidence x evidence_quality; independent verification required',
            })
        return reconciled

    def run(
        self,
        *,
        mission_id: str,
        directive: str,
        plan: MissionGraphPlan,
        global_risk: RiskClass,
        allow_repair: bool = False,
        resume: bool = False,
    ) -> tuple[dict[str, GraphNodeOutcome], PilotSynthesis]:
        plan.validate()
        if any(n.mode is MissionMode.repair for n in plan.nodes) and not allow_repair:
            raise GraphExecutionError("Mission Graph repair nodes require explicit Pilot mutation authorization")

        if resume:
            specs,statuses,attempts,outcomes,tour_results,replan_count,used_crew = self._restore_execution(mission_id)
        else:
            specs = {n.node_id: n for n in plan.nodes}
            statuses = {n.node_id: "pending" for n in plan.nodes}
            attempts = {n.node_id: 1 for n in plan.nodes}
            outcomes = {}
            tour_results = {}
            replan_count = 0
            used_crew = set()
            for spec in plan.nodes:
                self.store.save_graph_node(
                    mission_id, spec.node_id, payload=spec.to_dict(), dependencies=spec.dependencies,
                    status="pending", attempt=1,
                )
            self.store.add_graph_event(
                mission_id, "graph_started",
                {"objective": plan.objective, "nodes": len(plan.nodes), "budget": plan.to_dict()["budget"]},
            )
            self.durable.checkpoint(mission_id, 'graph_started', 'committed', payload={'nodes': len(plan.nodes)})
        verification_nodes: set[str] = {node_id for node_id,spec in specs.items() if spec.mode is MissionMode.verify}
        spent_cost = self._committed_cost(mission_id)

        unresolved_reason: str | None = None
        while True:
            run_state = self.durable.graph_run(mission_id)
            if run_state and run_state['cancelled']:
                unresolved_reason = 'mission cancelled'
                break
            pending = [node_id for node_id, status in statuses.items() if status == "pending"]
            if not pending:
                break
            ready = [
                node_id for node_id in pending
                if all(statuses.get(dep) == "completed" for dep in specs[node_id].dependencies)
            ]
            if not ready:
                unresolved_reason = "graph has no runnable nodes; dependency chain is unresolved"
                break
            batch: list[str] = []
            reserved_cost = 0.0
            for node_id in ready:
                if len(batch) >= plan.budget.max_parallel:
                    break
                node_cost = max(0.0, float(specs[node_id].budget.cost_units))
                if spent_cost + reserved_cost + node_cost <= plan.budget.max_cost_units + 1e-12:
                    batch.append(node_id)
                    reserved_cost += node_cost
            if not batch:
                required = min(max(0.0, float(specs[node_id].budget.cost_units)) for node_id in ready)
                unresolved_reason = 'Mission cost budget exhausted'
                self.store.add_graph_event(mission_id, 'cost_budget_exhausted', {
                    'spent_cost_units': spent_cost, 'max_cost_units': plan.budget.max_cost_units,
                    'ready_nodes': ready, 'minimum_required_cost_units': required, 'phase': 'node_execution',
                })
                break
            self.store.add_graph_event(mission_id, "batch_started", {"nodes": batch, "parallel_width": len(batch)})
            prepared: dict[str, tuple[GraphNodeSpec, MissionOrder, list[TourResult]]] = {}
            batch_crew: set[str] = set()
            for node_id in batch:
                spec = specs[node_id]
                dependency_crew = {outcomes[d].crew_id for d in spec.dependencies if d in outcomes}
                try:
                    effective_risk = self._effective_risk(global_risk, spec.risk_class)
                    routing = self._select_crew(spec, exclude=batch_crew, dependency_crew=dependency_crew, risk=effective_risk)
                    crew = routing.crew
                except LookupError as exc:
                    statuses[node_id] = "exception"
                    self.store.update_graph_node(mission_id, node_id, "exception", attempt=attempts[node_id])
                    self.store.add_graph_event(
                        mission_id, "crew_selection_exception",
                        {"type": type(exc).__name__, "message": str(exc), "attempt": attempts[node_id]}, node_id=node_id,
                    )
                    unresolved_reason = str(exc)
                    break
                batch_crew.add(crew.crew_id)
                used_crew.add(crew.crew_id)
                parent_order = outcomes[spec.dependencies[-1]].order_id if spec.dependencies and spec.dependencies[-1] in outcomes else None
                order = self._make_order(mission_id, directive, spec, crew, global_risk, parent_order, attempt=attempts[node_id])
                memory_meta = self.intelligence.inject_order_context(order, spec.objective)
                self.store.save_order(order)
                node_cost = max(0.0, float(spec.budget.cost_units))
                self.store.add_graph_event(mission_id, 'cost_committed', {
                    'kind': 'graph_node', 'node_id': node_id, 'order_id': order.order_id,
                    'attempt': attempts[node_id], 'cost_units': node_cost,
                }, node_id=node_id)
                spent_cost += node_cost
                self.store.add_evidence(mission_id, order.order_id, Evidence("routing_decision", routing.to_dict()))
                self.store.add_evidence(mission_id, order.order_id, Evidence("memory_selection", memory_meta))
                self.store.crew_on_duty(crew.crew_id, mission_id)
                self.store.update_order(order.order_id, "running")
                self.store.update_graph_node(
                    mission_id,
                    node_id,
                    "running",
                    attempt=attempts[node_id],
                    order_id=order.order_id,
                    crew_id=crew.crew_id,
                )
                statuses[node_id] = "running"
                self.durable.checkpoint(
                    mission_id, 'before_execute', 'running', node_id=node_id, attempt=attempts[node_id],
                    order_id=order.order_id, payload={'idempotency_key': order.parameters.get('_idempotency_key')},
                )
                deps = [tour_results[d] for d in spec.dependencies if d in tour_results]
                prepared[node_id] = (spec, order, deps)
            if unresolved_reason:
                break
            futures = {}
            started_at: dict[str, float] = {}
            with ThreadPoolExecutor(max_workers=max(1, len(prepared))) as pool:
                for node_id, (spec, order, dep_results) in prepared.items():
                    started_at[node_id] = perf_counter()
                    futures[pool.submit(self._execute_prepared, spec, order, dep_results)] = node_id
                for future in as_completed(futures):
                    node_id = futures[future]
                    spec, order, _ = prepared[node_id]
                    latency_ms = (perf_counter() - started_at[node_id]) * 1000.0
                    try:
                        result = future.result(timeout=spec.budget.max_seconds)
                    except TimeoutError as exc:
                        result = TourResult(
                            order.order_id,
                            order.assigned_crew,
                            "exception",
                            f"Graph node runtime timeout: {exc}",
                            [],
                            {"type": "runtime_timeout", "message": str(exc)},
                        )
                    for ev in result.evidence:
                        self.store.add_evidence(mission_id, order.order_id, ev)
                    if result.exception:
                        self.store.add_evidence(mission_id, order.order_id, Evidence("crew_exception", dict(result.exception)))
                    self.store.update_order(order.order_id, result.status)
                    self.store.crew_sleep(order.assigned_crew, mission_id, result.summary)
                    self.durable.checkpoint(
                        mission_id, 'after_execute', result.status, node_id=node_id, attempt=attempts[node_id],
                        order_id=order.order_id, payload={'summary': result.summary, 'exception': result.exception or {}},
                    )
                    outcome = GraphNodeOutcome(
                        node_id=node_id,
                        order_id=order.order_id,
                        crew_id=order.assigned_crew,
                        status=result.status,
                        summary=result.summary,
                        evidence_kinds=sorted({e.kind for e in result.evidence}),
                        exception=result.exception,
                        attempt=attempts[node_id],
                    )
                    outcomes[node_id] = outcome
                    tour_results[node_id] = result
                    self.intelligence.record_performance(
                        crew_id=order.assigned_crew, mission_id=mission_id, order_id=order.order_id,
                        task_class=order.parameters.get("_task_class", self.intelligence.task_class(spec.objective)),
                        result=result, latency_ms=latency_ms, risk=order.risk_class, verified=None,
                        cost_units=spec.budget.cost_units,
                    )
                    if spec.mode is MissionMode.verify:
                        for evidence in result.evidence:
                            if evidence.kind != "graph_verification":
                                continue
                            for check in evidence.content.get("checks", []):
                                self.intelligence.mark_verified(check["order_id"], bool(check["ok"]))
                    if result.status == "completed":
                        statuses[node_id] = "completed"
                        self.store.update_graph_node(mission_id, node_id, "completed")
                        self.store.add_graph_event(
                            mission_id, "node_completed",
                            {"crew": order.assigned_crew, "summary": result.summary, "attempt": attempts[node_id]},
                            node_id=node_id,
                        )
                        self.durable.checkpoint(
                            mission_id, 'node_committed', 'completed', node_id=node_id, attempt=attempts[node_id],
                            order_id=order.order_id, payload={'crew': order.assigned_crew},
                        )
                        continue
                    statuses[node_id] = "exception"
                    self.store.update_graph_node(mission_id, node_id, "exception")
                    replacement_id, replan_count = self._try_replan(
                        mission_id=mission_id, directive=directive,
                        failed_spec=spec,
                        failed_outcome=outcome,
                        failed_result=result,
                        specs=specs,
                        statuses=statuses,
                        attempts=attempts,
                        used_crew=used_crew,
                        replan_count=replan_count,
                        plan=plan,
                        global_risk=global_risk,
                    )
                    spent_cost = self._committed_cost(mission_id)
                    if replacement_id is None:
                        unresolved_reason = f"node {node_id} failed: {(result.exception or {}).get('type', 'unknown')}"
            if unresolved_reason:
                break

        completed = sorted(node_id for node_id, status in statuses.items() if status == "completed")
        unresolved = sorted(node_id for node_id, status in statuses.items() if status not in {"completed", "replanned"})
        verification_passed = bool(verification_nodes) and all(
            statuses.get(node_id) in {"completed", "replanned"} for node_id in verification_nodes
        )
        evidence_kinds = sorted({kind for outcome in outcomes.values() for kind in outcome.evidence_kinds})
        contradictions = self._reconcile_contradictions(tour_results, verification_passed=verification_passed)
        spent_cost = self._committed_cost(mission_id)
        decisions = self.durable.exception_decisions(mission_id)
        commander_required = any(d['requires_commander'] for d in decisions)
        run_state = self.durable.graph_run(mission_id)
        if run_state and run_state['cancelled']:
            outcome_status = 'cancelled'
        elif commander_required:
            outcome_status = 'needs_commander_decision'
        else:
            outcome_status = "completed" if not unresolved and unresolved_reason is None else "needs_pilot_decision"
        summary = (
            f"GorXu coordinated {len(completed)} completed graph nodes across {len(used_crew)} Crew; "
            f"replans={replan_count}; exceptions={len(decisions)}; "
            f"resumes={(run_state or {}).get('resume_count',0)}; cost={spent_cost:.3f}/{plan.budget.max_cost_units:.3f}; "
            f"contradictions={len(contradictions)}; verification={'PASS' if verification_passed else 'NOT PROVEN'}"
        )
        if unresolved_reason:
            summary += f"; unresolved: {unresolved_reason}"
        synthesis = PilotSynthesis(
            outcome=outcome_status,
            executive_summary=summary,
            completed_nodes=completed,
            unresolved_nodes=unresolved,
            crew_used=sorted(used_crew),
            replans=replan_count,
            verification_passed=verification_passed,
            evidence_kinds=evidence_kinds,
            contradictions=contradictions,
            cost_units=spent_cost,
            cost_budget=plan.budget.max_cost_units,
        )
        self.store.add_graph_event(mission_id, "pilot_synthesis", synthesis.to_dict())
        self.durable.checkpoint(mission_id, 'pilot_synthesis', synthesis.outcome, payload=synthesis.to_dict())
        return outcomes, synthesis