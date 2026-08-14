from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from time import perf_counter
from typing import Any

from ..contracts import Evidence, MissionMode, MissionOrder, RiskClass, TourResult
from ..crew.roster import CrewDossier, CrewRoster
from ..mission_control.core import MissionControl
from ..runtime.executor import CrewExecutor
from ..state import StateStore
from ..verification.core import IndependentVerifier
from ..intelligence import LivingCompanyIntelligence, RoutingDecision
from .contracts import GraphNodeOutcome, GraphNodeSpec, MissionGraphPlan, PilotSynthesis

_RISK_RANK = {RiskClass.low: 0, RiskClass.medium: 1, RiskClass.high: 2, RiskClass.critical: 3}
_RECOVERABLE_EXCEPTIONS = {"crew_unavailable", "transient_failure", "TimeoutError"}


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
    ):
        self.store = store
        self.roster = roster
        self.executor = executor
        self.mission_control = mission_control
        self.verifier = verifier
        self.intelligence = intelligence

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
        return actions

    def _make_order(
        self,
        mission_id: str,
        directive: str,
        spec: GraphNodeSpec,
        crew: CrewDossier,
        global_risk: RiskClass,
        parent_order_id: str | None = None,
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
            parameters={**dict(spec.parameters), "_graph_max_seconds": spec.budget.max_seconds},
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
        failed_spec: GraphNodeSpec,
        failed_outcome: GraphNodeOutcome,
        failed_result: TourResult,
        specs: dict[str, GraphNodeSpec],
        statuses: dict[str, str],
        attempts: dict[str, int],
        used_crew: set[str],
        replan_count: int,
        plan: MissionGraphPlan,
    ) -> tuple[str | None, int]:
        exc_type = (failed_result.exception or {}).get("type")
        if exc_type not in _RECOVERABLE_EXCEPTIONS:
            return None, replan_count
        current_attempt = attempts[failed_spec.node_id]
        if current_attempt >= failed_spec.budget.max_attempts:
            return None, replan_count
        if replan_count >= plan.budget.max_replans:
            return None, replan_count
        if len(specs) + 1 > plan.budget.max_nodes:
            return None, replan_count

        try:
            replacement_decision = self._select_crew(
                failed_spec,
                exclude={failed_outcome.crew_id},
                dependency_crew=set(),
                risk=failed_spec.risk_class,
            )
            replacement = replacement_decision.crew
        except LookupError:
            return None, replan_count

        new_attempt = current_attempt + 1
        replacement_id = f"{failed_spec.node_id}__replan{new_attempt - 1}"
        while replacement_id in specs:
            new_attempt += 1
            replacement_id = f"{failed_spec.node_id}__replan{new_attempt - 1}"
        recovery_spec = replace(
            failed_spec,
            node_id=replacement_id,
            candidate_crew_ids=[replacement.crew_id],
        )
        specs[replacement_id] = recovery_spec
        statuses[replacement_id] = "pending"
        attempts[replacement_id] = new_attempt
        used_crew.add(replacement.crew_id)
        self.store.save_graph_node(
            mission_id,
            replacement_id,
            payload=recovery_spec.to_dict(),
            dependencies=recovery_spec.dependencies,
            status="pending",
            attempt=new_attempt,
            crew_id=replacement.crew_id,
        )
        statuses[failed_spec.node_id] = "replanned"
        self.store.update_graph_node(mission_id, failed_spec.node_id, "replanned")
        self._rewire_downstream(mission_id, specs, failed_spec.node_id, replacement_id, statuses)
        replan_count += 1
        self.store.add_graph_event(
            mission_id,
            "pilot_replan",
            {
                "failed_node": failed_spec.node_id,
                "replacement_node": replacement_id,
                "failed_crew": failed_outcome.crew_id,
                "replacement_crew": replacement.crew_id,
                "exception_type": exc_type,
                "reason": "recoverable Crew/runtime failure",
                "replan_number": replan_count,
            },
            node_id=failed_spec.node_id,
        )
        return replacement_id, replan_count

    def run(
        self,
        *,
        mission_id: str,
        directive: str,
        plan: MissionGraphPlan,
        global_risk: RiskClass,
        allow_repair: bool = False,
    ) -> tuple[dict[str, GraphNodeOutcome], PilotSynthesis]:
        plan.validate()
        if any(n.mode is MissionMode.repair for n in plan.nodes) and not allow_repair:
            raise GraphExecutionError("Mission Graph repair nodes require explicit Pilot mutation authorization")

        specs = {n.node_id: n for n in plan.nodes}
        statuses = {n.node_id: "pending" for n in plan.nodes}
        attempts = {n.node_id: 1 for n in plan.nodes}
        outcomes: dict[str, GraphNodeOutcome] = {}
        tour_results: dict[str, TourResult] = {}
        replan_count = 0
        used_crew: set[str] = set()
        verification_nodes: set[str] = {n.node_id for n in plan.nodes if n.mode is MissionMode.verify}

        for spec in plan.nodes:
            self.store.save_graph_node(
                mission_id,
                spec.node_id,
                payload=spec.to_dict(),
                dependencies=spec.dependencies,
                status="pending",
                attempt=1,
            )
        self.store.add_graph_event(
            mission_id,
            "graph_started",
            {"objective": plan.objective, "nodes": len(plan.nodes), "budget": plan.to_dict()["budget"]},
        )

        unresolved_reason: str | None = None
        while True:
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
            batch = ready[: plan.budget.max_parallel]
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
                    unresolved_reason = str(exc)
                    break
                batch_crew.add(crew.crew_id)
                used_crew.add(crew.crew_id)
                parent_order = outcomes[spec.dependencies[-1]].order_id if spec.dependencies and spec.dependencies[-1] in outcomes else None
                order = self._make_order(mission_id, directive, spec, crew, global_risk, parent_order)
                memory_meta = self.intelligence.inject_order_context(order, spec.objective)
                self.store.save_order(order)
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
                    except Exception as exc:  # scheduler boundary; normalized as transient runtime exception
                        result = TourResult(
                            order.order_id,
                            order.assigned_crew,
                            "exception",
                            f"Graph node runtime failure: {exc}",
                            [],
                            {"type": type(exc).__name__, "message": str(exc)},
                        )
                    for ev in result.evidence:
                        self.store.add_evidence(mission_id, order.order_id, ev)
                    self.store.update_order(order.order_id, result.status)
                    self.store.crew_sleep(order.assigned_crew, mission_id, result.summary)
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
                            mission_id,
                            "node_completed",
                            {"crew": order.assigned_crew, "summary": result.summary, "attempt": attempts[node_id]},
                            node_id=node_id,
                        )
                        continue
                    statuses[node_id] = "exception"
                    self.store.update_graph_node(mission_id, node_id, "exception")
                    replacement_id, replan_count = self._try_replan(
                        mission_id=mission_id,
                        failed_spec=spec,
                        failed_outcome=outcome,
                        failed_result=result,
                        specs=specs,
                        statuses=statuses,
                        attempts=attempts,
                        used_crew=used_crew,
                        replan_count=replan_count,
                        plan=plan,
                    )
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
        outcome_status = "completed" if not unresolved and unresolved_reason is None else "needs_pilot_decision"
        summary = (
            f"GorXu coordinated {len(completed)} completed graph nodes across {len(used_crew)} Crew; "
            f"replans={replan_count}; verification={'PASS' if verification_passed else 'NOT PROVEN'}"
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
        )
        self.store.add_graph_event(mission_id, "pilot_synthesis", synthesis.to_dict())
        return outcomes, synthesis
