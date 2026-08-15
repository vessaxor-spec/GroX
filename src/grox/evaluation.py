from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Iterable
import uuid

from .contracts import MissionMode, RiskClass
from .crew.roster import CrewRoster
from .durable_state import DurableState
from .intelligence import DEFAULT_ROUTING_WEIGHTS, weighted_routing_score
from .mission_control.core import MissionControl
from .state import StateStore, now


_TOOL_EVIDENCE = {
    "inventory", "test_run", "mutation", "mutation_rollback", "idempotent_replay",
    "workspace_execution", "network_fetch", "browser_capture", "mcp_call",
}
_PLAN_EVIDENCE = {"mission_graph_plan", "cognitive_plan", "routing_decision"}
_VERIFICATION_EVIDENCE = {"independent_verification", "graph_verification"}
_EXCEPTION_EVIDENCE = {"crew_exception", "unexpected_defect"}
_PROPOSAL_TYPES = {"routing", "prompt", "skill", "memory", "workflow"}
_CRITICAL_EXCEPTION_TYPES = {"irreversible_consequence", "mutation_state_diverged", "authority_violation"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    data = value if isinstance(value, (bytes, bytearray)) else _canonical(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _json(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    loaded = json.loads(value)
    return loaded if isinstance(loaded, dict) else {"value": loaded}


def _number(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


@dataclass(frozen=True, slots=True)
class TrajectoryEvent:
    at: str
    category: str
    kind: str
    source_id: str
    payload: dict[str, Any]
    source_table: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluationComparison:
    baseline_run_id: str
    candidate_run_id: str
    cases: int
    baseline_passes: int
    candidate_passes: int
    wins: int
    losses: int
    ties: int
    p_value: float
    alpha: float
    invariant_regressions: int
    statistically_better: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvaluationLedger:
    """Private A6 evaluation state sharing GroX's operational SQLite plane."""

    def __init__(self, store: StateStore):
        self.store = store
        self.db = store.db
        self._init()

    def _init(self) -> None:
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS evaluation_cases(
          case_id TEXT PRIMARY KEY, suite TEXT NOT NULL, case_type TEXT NOT NULL,
          source_mission_id TEXT, payload TEXT NOT NULL, expected TEXT NOT NULL,
          provenance TEXT NOT NULL, case_sha256 TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_evaluation_cases_suite ON evaluation_cases(suite,case_type,created_at);
        CREATE TABLE IF NOT EXISTS evaluation_runs(
          run_id TEXT PRIMARY KEY, suite TEXT NOT NULL, evaluator TEXT NOT NULL,
          policy_name TEXT NOT NULL, config TEXT NOT NULL, metrics TEXT NOT NULL,
          invariants TEXT NOT NULL, case_results TEXT NOT NULL, run_sha256 TEXT NOT NULL,
          created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_evaluation_runs_suite ON evaluation_runs(suite,created_at);
        CREATE TABLE IF NOT EXISTS improvement_proposals(
          proposal_id TEXT PRIMARY KEY, proposal_type TEXT NOT NULL, target TEXT NOT NULL,
          proposed_change TEXT NOT NULL, rationale TEXT NOT NULL, evidence TEXT NOT NULL,
          baseline_run_id TEXT, candidate_run_id TEXT, status TEXT NOT NULL,
          proposal_sha256 TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_improvement_proposals_type ON improvement_proposals(proposal_type,created_at);
        ''')
        self.db.commit()

    def add_case(
        self,
        *,
        suite: str,
        case_type: str,
        payload: dict[str, Any],
        expected: dict[str, Any],
        provenance: dict[str, Any],
        source_mission_id: str | None = None,
        case_id: str | None = None,
    ) -> str:
        if not suite.strip() or not case_type.strip():
            raise ValueError("evaluation suite and case_type are required")
        if not provenance or not str(provenance.get("source") or "").strip():
            raise ValueError("evaluation case provenance with source is required")
        cid = case_id or f"EVC-{uuid.uuid4().hex[:12]}"
        encoded = _canonical(payload)
        expected_encoded = _canonical(expected)
        provenance_encoded = _canonical(provenance)
        record = {
            "case_id": cid, "suite": suite, "case_type": case_type, "source_mission_id": source_mission_id,
            "payload": payload, "expected": expected, "provenance": provenance,
        }
        digest = _sha(record)
        existing = self.db.execute("SELECT case_sha256 FROM evaluation_cases WHERE case_id=?", (cid,)).fetchone()
        if existing:
            if existing["case_sha256"] != digest:
                raise ValueError(f"evaluation case ID conflicts with different content: {cid}")
            return cid
        self.db.execute(
            """INSERT INTO evaluation_cases(case_id,suite,case_type,source_mission_id,payload,expected,provenance,case_sha256,created_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (cid, suite, case_type, source_mission_id, encoded, expected_encoded, provenance_encoded, digest, now()),
        )
        self.db.commit()
        return cid

    def case(self, case_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM evaluation_cases WHERE case_id=?", (case_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown evaluation case {case_id}")
        out = dict(row)
        for key in ("payload", "expected", "provenance"):
            out[key] = json.loads(out[key])
        actual = _sha({
            "case_id": out["case_id"], "suite": out["suite"], "case_type": out["case_type"],
            "source_mission_id": out["source_mission_id"], "payload": out["payload"],
            "expected": out["expected"], "provenance": out["provenance"],
        })
        if actual != out["case_sha256"]:
            raise ValueError(f"evaluation case digest mismatch: {case_id}")
        return out

    def cases(self, suite: str, *, case_type: str | None = None) -> list[dict[str, Any]]:
        if case_type:
            rows = self.db.execute(
                "SELECT case_id FROM evaluation_cases WHERE suite=? AND case_type=? ORDER BY case_id", (suite, case_type)
            ).fetchall()
        else:
            rows = self.db.execute("SELECT case_id FROM evaluation_cases WHERE suite=? ORDER BY case_id", (suite,)).fetchall()
        return [self.case(row["case_id"]) for row in rows]

    def record_run(
        self,
        *,
        suite: str,
        evaluator: str,
        policy_name: str,
        config: dict[str, Any],
        metrics: dict[str, Any],
        invariants: dict[str, Any],
        case_results: list[dict[str, Any]],
    ) -> str:
        run_id = f"EVR-{uuid.uuid4().hex[:12]}"
        record = {"run_id": run_id, "suite": suite, "evaluator": evaluator, "policy_name": policy_name,
                  "config": config, "metrics": metrics, "invariants": invariants, "case_results": case_results}
        digest = _sha(record)
        self.db.execute(
            """INSERT INTO evaluation_runs(run_id,suite,evaluator,policy_name,config,metrics,invariants,case_results,run_sha256,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (run_id, suite, evaluator, policy_name, _canonical(config), _canonical(metrics), _canonical(invariants),
             _canonical(case_results), digest, now()),
        )
        self.db.commit()
        return run_id

    def run(self, run_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM evaluation_runs WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown evaluation run {run_id}")
        out = dict(row)
        for key in ("config", "metrics", "invariants", "case_results"):
            out[key] = json.loads(out[key])
        actual = _sha({"run_id": out["run_id"], "suite": out["suite"], "evaluator": out["evaluator"],
                       "policy_name": out["policy_name"], "config": out["config"], "metrics": out["metrics"],
                       "invariants": out["invariants"], "case_results": out["case_results"]})
        if actual != out["run_sha256"]:
            raise ValueError(f"evaluation run digest mismatch: {run_id}")
        return out

    def create_proposal(
        self,
        *,
        proposal_type: str,
        target: str,
        proposed_change: dict[str, Any],
        rationale: str,
        evidence: dict[str, Any],
        baseline_run_id: str | None = None,
        candidate_run_id: str | None = None,
    ) -> str:
        if proposal_type not in _PROPOSAL_TYPES:
            raise ValueError(f"unsupported improvement proposal type: {proposal_type}")
        if not target.strip() or not rationale.strip() or not evidence:
            raise ValueError("target, rationale, and evidence are required for improvement proposals")
        proposal_id = f"IMP-{uuid.uuid4().hex[:12]}"
        record = {"proposal_id": proposal_id, "proposal_type": proposal_type, "target": target,
                  "proposed_change": proposed_change, "rationale": rationale, "evidence": evidence,
                  "baseline_run_id": baseline_run_id, "candidate_run_id": candidate_run_id, "status": "proposed"}
        digest = _sha(record)
        self.db.execute(
            """INSERT INTO improvement_proposals(proposal_id,proposal_type,target,proposed_change,rationale,evidence,
               baseline_run_id,candidate_run_id,status,proposal_sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (proposal_id, proposal_type, target, _canonical(proposed_change), rationale, _canonical(evidence),
             baseline_run_id, candidate_run_id, "proposed", digest, now()),
        )
        self.db.commit()
        return proposal_id

    def proposal(self, proposal_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM improvement_proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown improvement proposal {proposal_id}")
        out = dict(row)
        out["proposed_change"] = json.loads(out["proposed_change"])
        out["evidence"] = json.loads(out["evidence"])
        actual = _sha({"proposal_id": out["proposal_id"], "proposal_type": out["proposal_type"], "target": out["target"],
                       "proposed_change": out["proposed_change"], "rationale": out["rationale"], "evidence": out["evidence"],
                       "baseline_run_id": out["baseline_run_id"], "candidate_run_id": out["candidate_run_id"], "status": out["status"]})
        if actual != out["proposal_sha256"]:
            raise ValueError(f"improvement proposal digest mismatch: {proposal_id}")
        return out

    def proposals(self) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT proposal_id FROM improvement_proposals ORDER BY created_at,proposal_id").fetchall()
        return [self.proposal(row["proposal_id"]) for row in rows]

    def activate(self, proposal_id: str) -> None:
        self.proposal(proposal_id)
        raise PermissionError(
            "A6 improvement proposals are advisory only; activation requires a separate GroX authority path and explicit mutation Order"
        )


class TrajectoryBuilder:
    """Reconstructs privacy-minimized Mission trajectories from canonical GroX records."""

    def __init__(self, store: StateStore, durable: DurableState, roster: CrewRoster):
        self.store = store
        self.durable = durable
        self.roster = roster
        self.policy = MissionControl()

    def _sanitize_order(self, row: dict[str, Any]) -> dict[str, Any]:
        payload = _json(row["payload"])
        scope = payload.get("scope") or []
        return {
            "order_id": row["order_id"],
            "crew_id": row["crew_id"],
            "mode": row["mode"],
            "status": row["status"],
            "required_capabilities": list(payload.get("required_capabilities") or []),
            "allowed_actions": list(payload.get("allowed_actions") or []),
            "forbidden_actions": list(payload.get("forbidden_actions") or []),
            "risk_class": payload.get("risk_class"),
            "parent_order_id": payload.get("parent_order_id"),
            "objective_sha256": hashlib.sha256(str(payload.get("objective") or "").encode("utf-8")).hexdigest(),
            "scope_count": len(scope),
            "scope_sha256": _sha(scope),
        }

    def _sanitize_evidence(self, kind: str, raw: dict[str, Any]) -> dict[str, Any]:
        if kind == "routing_decision":
            return {k: raw[k] for k in ("crew_id", "task_class", "score", "components", "source") if k in raw}
        if kind == "memory_selection":
            return {k: raw[k] for k in ("task_class", "memory_count", "memory_ids") if k in raw}
        if kind == "cognitive_plan":
            return {k: raw[k] for k in ("provider", "proposed_mode", "proposed_risk", "candidate_crew_ids", "confidence", "recommended_option") if k in raw}
        if kind == "mission_graph_plan":
            nodes = []
            for node in raw.get("nodes") or []:
                if not isinstance(node, dict):
                    continue
                nodes.append({k: node[k] for k in (
                    "node_id", "mode", "dependencies", "candidate_crew_ids", "required_capabilities", "allowed_actions", "risk_class"
                ) if k in node})
            return {
                "source": raw.get("source"),
                "nodes": nodes,
                "budget": raw.get("budget") or {},
                "plan_sha256": _sha(raw),
            }
        if kind == "pilot_synthesis":
            return {k: raw[k] for k in (
                "outcome", "completed_nodes", "unresolved_nodes", "crew_used", "replans", "exceptions", "resumes",
                "resume_count", "verification_passed", "evidence_kinds"
            ) if k in raw}
        if kind == "inventory":
            return {"count": int(raw.get("count") or 0), "files_sha256": _sha(raw.get("files") or [])}
        if kind == "test_run":
            return {
                "returncode": raw.get("returncode"),
                "stdout_sha256": hashlib.sha256(str(raw.get("stdout") or "").encode("utf-8")).hexdigest(),
                "stderr_sha256": hashlib.sha256(str(raw.get("stderr") or "").encode("utf-8")).hexdigest(),
            }
        if kind in {"mutation", "mutation_rollback", "idempotent_replay"}:
            return {k: raw[k] for k in (
                "operation", "path", "status", "before_sha256", "after_sha256", "sha256", "idempotency_key", "restored"
            ) if k in raw}
        if kind == "workspace_execution":
            return {k: raw[k] for k in (
                "returncode", "isolation_backend", "isolation", "workspace_retained", "secret_aliases"
            ) if k in raw} | {
                "stdout_sha256": hashlib.sha256(str(raw.get("stdout") or "").encode("utf-8")).hexdigest(),
                "stderr_sha256": hashlib.sha256(str(raw.get("stderr") or "").encode("utf-8")).hexdigest(),
            }
        if kind == "network_fetch":
            return {k: raw[k] for k in ("origin", "status", "bytes", "sha256", "redirect_followed", "content_type") if k in raw}
        if kind == "browser_capture":
            return {k: raw[k] for k in (
                "origin", "source_status", "source_sha256", "source_bytes", "screenshot_sha256", "browser_network",
                "browser_backend", "browser_isolation", "browser_image_id"
            ) if k in raw}
        if kind == "mcp_call":
            base = {k: raw[k] for k in ("adapter", "tool", "mutating", "returncode") if k in raw}
            base["result_sha256"] = _sha(raw.get("result") if "result" in raw else raw)
            return base
        if kind == "independent_verification":
            return {k: raw[k] for k in ("ok", "executor", "verifier") if k in raw}
        if kind == "graph_verification":
            checks = []
            for check in raw.get("checks") or []:
                if isinstance(check, dict):
                    checks.append({k: check[k] for k in ("order_id", "executor", "verifier", "ok") if k in check})
            return {"ok": bool(raw.get("ok")), "checks": checks}
        if kind == "crew_exception":
            return {k: raw[k] for k in ("type", "recommendation", "irreversible", "material_intent_change") if k in raw}
        if kind == "unexpected_defect":
            context = dict(raw.get("context") or {})
            safe_context = {k: context[k] for k in ("operation", "mode", "risk", "resume_count") if k in context}
            if "directive" in context:
                safe_context["directive_sha256"] = hashlib.sha256(str(context["directive"]).encode("utf-8")).hexdigest()
            return {
                "classification": raw.get("classification"),
                "exception_type": raw.get("exception_type"),
                "message_sha256": hashlib.sha256(str(raw.get("message") or "").encode("utf-8")).hexdigest(),
                "traceback_sha256": hashlib.sha256(str(raw.get("traceback") or "").encode("utf-8")).hexdigest(),
                "context": safe_context,
            }
        return {"content_sha256": _sha(raw), "keys": sorted(raw)}

    def build(self, mission_id: str) -> dict[str, Any]:
        snapshot = self.store.mission(mission_id)
        if not snapshot:
            raise KeyError(f"unknown Mission {mission_id}")
        mission = snapshot["mission"]
        events: list[TrajectoryEvent] = []

        for row in snapshot["orders"]:
            events.append(TrajectoryEvent(
                at=row["created_at"], category="delegation", kind="mission_order", source_id=row["order_id"],
                payload=self._sanitize_order(row), source_table="orders",
            ))

        plan_evidence = tool_evidence = verification_evidence = exception_evidence = 0
        for row in snapshot["evidence"]:
            content = _json(row["content"])
            kind = row["kind"]
            if kind in _PLAN_EVIDENCE:
                category = "plan"; plan_evidence += 1
            elif kind in _TOOL_EVIDENCE:
                category = "tool_action"; tool_evidence += 1
            elif kind in _VERIFICATION_EVIDENCE:
                category = "verification"; verification_evidence += 1
            elif kind in _EXCEPTION_EVIDENCE:
                category = "exception"; exception_evidence += 1
            else:
                category = "evidence"
            events.append(TrajectoryEvent(
                at=row["created_at"], category=category, kind=kind, source_id=str(row["id"]),
                payload=self._sanitize_evidence(kind, content), source_table="evidence",
            ))

        exception_decisions = self.durable.exception_decisions(mission_id)
        for row in exception_decisions:
            events.append(TrajectoryEvent(
                at=row["created_at"], category="exception", kind="exception_decision", source_id=str(row["id"]),
                payload={k: row[k] for k in (
                    "node_id", "order_id", "exception_type", "risk", "disposition", "requires_commander",
                    "consulted_crew", "consultation_order_id"
                )}, source_table="exception_decisions",
            ))

        for row in snapshot["graph_nodes"]:
            events.append(TrajectoryEvent(
                at=row["updated_at"], category="control", kind="graph_node_state", source_id=row["node_id"],
                payload={
                    "node_id": row["node_id"], "order_id": row["order_id"], "crew_id": row["crew_id"],
                    "status": row["status"], "attempt": int(row["attempt"]),
                    "dependencies": json.loads(row["dependencies"]),
                }, source_table="graph_nodes",
            ))

        graph_run = self.durable.graph_run(mission_id)
        if graph_run:
            events.append(TrajectoryEvent(
                at=graph_run["updated_at"], category="control", kind="graph_run", source_id=mission_id,
                payload={"resume_count": int(graph_run["resume_count"]), "cancelled": bool(graph_run["cancelled"])},
                source_table="graph_runs",
            ))

        perf_rows = self.store.db.execute(
            "SELECT * FROM crew_performance WHERE mission_id=? ORDER BY id", (mission_id,)
        ).fetchall()
        for row in perf_rows:
            events.append(TrajectoryEvent(
                at=row["created_at"], category="telemetry", kind="crew_performance", source_id=row["order_id"],
                payload={
                    "crew_id": row["crew_id"], "order_id": row["order_id"], "task_class": row["task_class"],
                    "status": row["status"], "evidence_quality": float(row["evidence_quality"]),
                    "verified": None if row["verified"] is None else bool(row["verified"]),
                    "latency_ms": float(row["latency_ms"]), "cost_units": float(row["cost_units"]), "risk": row["risk"],
                }, source_table="crew_performance",
            ))

        for row in snapshot["graph_events"]:
            event_type = row["event_type"]
            if "exception" in event_type or event_type in {"pilot_replan", "mission_resumed", "mission_cancelled"}:
                if "exception" in event_type:
                    category = "exception"
                elif event_type == "pilot_replan":
                    category = "plan"
                else:
                    category = "control"
                events.append(TrajectoryEvent(
                    at=row["created_at"], category=category, kind=event_type, source_id=str(row["id"]),
                    payload={"node_id": row["node_id"], "content_sha256": hashlib.sha256(row["content"].encode("utf-8")).hexdigest()},
                    source_table="graph_events",
                ))

        ordered = sorted(events, key=lambda ev: (ev.at, ev.category, ev.kind, ev.source_id))
        event_dicts = [ev.to_dict() for ev in ordered]
        trajectory = {
            "schema": "grox-trajectory-v1",
            "mission_id": mission_id,
            "mode": mission["mode"],
            "risk": mission["risk"],
            "status": mission["status"],
            "directive_sha256": hashlib.sha256(mission["directive"].encode("utf-8")).hexdigest(),
            "events": event_dicts,
            "source_counts": {
                "orders": len(snapshot["orders"]),
                "evidence": len(snapshot["evidence"]),
                "plan_evidence": plan_evidence,
                "tool_evidence": tool_evidence,
                "verification_evidence": verification_evidence,
                "exception_evidence": exception_evidence,
                "exception_decisions": len(exception_decisions),
                "graph_nodes": len(snapshot["graph_nodes"]),
                "graph_events": len(snapshot["graph_events"]),
                "performance": len(perf_rows),
            },
        }
        trajectory["trace_sha256"] = _sha({k: v for k, v in trajectory.items() if k != "trace_sha256"})
        return trajectory

    def metrics(self, trajectory: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        events = trajectory["events"]
        category_counts: dict[str, int] = {}
        for event in events:
            category_counts[event["category"]] = category_counts.get(event["category"], 0) + 1
        telemetry = [e for e in events if e["category"] == "telemetry" and e["kind"] == "crew_performance"]
        node_states = [e for e in events if e["kind"] == "graph_node_state"]
        graph_runs = [e for e in events if e["kind"] == "graph_run"]
        exceptions = [e for e in events if e["category"] == "exception"]
        verifications = [e for e in events if e["category"] == "verification"]
        source = trajectory["source_counts"]

        retries = sum(max(0, int(e["payload"].get("attempt") or 0) - 1) for e in node_states)
        resumes = max([int(e["payload"].get("resume_count") or 0) for e in graph_runs] or [0])
        retries += resumes
        escalations = sum(1 for e in exceptions if bool(e["payload"].get("requires_commander")))
        verification_failures = 0
        independence_violations = 0
        for event in verifications:
            payload = event["payload"]
            if payload.get("ok") is False:
                verification_failures += 1
            executor, verifier = payload.get("executor"), payload.get("verifier")
            if executor and verifier and executor == verifier:
                independence_violations += 1
            for check in payload.get("checks") or []:
                if check.get("ok") is False:
                    verification_failures += 1
                if check.get("executor") and check.get("executor") == check.get("verifier"):
                    independence_violations += 1

        capability_violations = 0
        for event in (e for e in events if e["category"] == "delegation"):
            crew_id = event["payload"].get("crew_id")
            required = set(event["payload"].get("required_capabilities") or [])
            try:
                dossier = self.roster.get(crew_id)
            except KeyError:
                capability_violations += 1
                continue
            if not required.issubset(dossier.capabilities):
                capability_violations += 1

        critical_escalation_violations = 0
        authority_exception_count = 0
        for event in exceptions:
            exc_type = str(event["payload"].get("exception_type") or event["payload"].get("type") or "")
            if exc_type == "authority_violation":
                authority_exception_count += 1
            if exc_type in _CRITICAL_EXCEPTION_TYPES and event["kind"] == "exception_decision" and not event["payload"].get("requires_commander"):
                critical_escalation_violations += 1

        trace_failures: list[str] = []
        if category_counts.get("delegation", 0) != source["orders"]:
            trace_failures.append("delegation_trace_incomplete")
        if category_counts.get("tool_action", 0) != source["tool_evidence"]:
            trace_failures.append("tool_trace_incomplete")
        if category_counts.get("verification", 0) != source["verification_evidence"]:
            trace_failures.append("verification_trace_incomplete")
        evidence_events = sum(1 for event in events if event["source_table"] == "evidence")
        if evidence_events != source["evidence"]:
            trace_failures.append("evidence_trace_incomplete")
        if source["plan_evidence"] and category_counts.get("plan", 0) != source["plan_evidence"]:
            trace_failures.append("plan_trace_incomplete")
        if source["exception_decisions"] + source["exception_evidence"] > category_counts.get("exception", 0):
            trace_failures.append("exception_trace_incomplete")

        try:
            risk = RiskClass(trajectory["risk"])
        except ValueError:
            trace_failures.append("invalid_mission_risk")
            risk = RiskClass.low
        raw_mode = trajectory.get("mode")
        if raw_mode == "graph":
            verification_required = (
                risk in {RiskClass.medium, RiskClass.high, RiskClass.critical}
                or any(e["payload"].get("mode") == MissionMode.verify.value for e in events if e["category"] == "delegation")
            )
        else:
            try:
                mode = MissionMode(raw_mode)
            except ValueError:
                trace_failures.append("invalid_mission_mode")
                mode = MissionMode.inspect
            verification_required = self.policy.verification_required(mode, risk)
        if verification_required and not verifications:
            trace_failures.append("required_verification_missing")

        invariants = list(trace_failures)
        if capability_violations:
            invariants.append("crew_capability_violation")
        if independence_violations:
            invariants.append("verifier_independence_violation")
        if critical_escalation_violations:
            invariants.append("critical_exception_not_escalated")
        if authority_exception_count:
            invariants.append("authority_violation_recorded")

        metrics = {
            "success": trajectory["status"] == "completed",
            "latency_ms": round(sum(_number(e["payload"].get("latency_ms")) for e in telemetry), 6),
            "cost_units": round(sum(_number(e["payload"].get("cost_units")) for e in telemetry), 6),
            "retries": retries,
            "resumes": resumes,
            "escalations": escalations,
            "verification_events": len(verifications),
            "verification_failures": verification_failures,
            "tool_actions": category_counts.get("tool_action", 0),
            "exceptions": len(exceptions),
            "evidence_quality": round(
                sum(_number(e["payload"].get("evidence_quality")) for e in telemetry) / len(telemetry), 6
            ) if telemetry else 0.0,
            "capability_violations": capability_violations,
            "verifier_independence_violations": independence_violations,
            "critical_escalation_violations": critical_escalation_violations,
            "authority_violations": authority_exception_count,
            "trace_complete": not trace_failures,
        }
        return metrics, sorted(set(invariants))


class OrchestrationEvaluator:
    """A6 evaluation and proposal service under GorXu; never an authority source."""

    def __init__(self, store: StateStore, durable: DurableState, roster: CrewRoster):
        self.store = store
        self.durable = durable
        self.roster = roster
        self.ledger = EvaluationLedger(store)
        self.trajectory = TrajectoryBuilder(store, durable, roster)

    def capture_mission(self, mission_id: str, *, suite: str = "operational-history") -> dict[str, Any]:
        trajectory = self.trajectory.build(mission_id)
        metrics, invariants = self.trajectory.metrics(trajectory)
        case_id = self.ledger.add_case(
            suite=suite, case_type="trajectory", source_mission_id=mission_id,
            payload={"trajectory": trajectory},
            expected={"status": trajectory["status"], "trace_sha256": trajectory["trace_sha256"]},
            provenance={"source": "canonical_private_mission_state", "mission_id": mission_id},
        )
        return {"case_id": case_id, "trajectory": trajectory, "metrics": metrics, "invariants": invariants}

    def replay_trajectory(self, case_id: str) -> dict[str, Any]:
        case = self.ledger.case(case_id)
        if case["case_type"] != "trajectory":
            raise ValueError("evaluation case is not a trajectory")
        trajectory = case["payload"].get("trajectory")
        if not isinstance(trajectory, dict):
            raise ValueError("trajectory payload missing")
        expected_trace = case["expected"].get("trace_sha256")
        actual_trace = _sha({k: v for k, v in trajectory.items() if k != "trace_sha256"})
        if trajectory.get("trace_sha256") != actual_trace or expected_trace != actual_trace:
            raise ValueError("trajectory replay digest mismatch")
        metrics, invariants = self.trajectory.metrics(trajectory)
        return {"case_id": case_id, "metrics": metrics, "invariants": invariants, "trace_sha256": actual_trace}

    def add_routing_case(
        self,
        *,
        suite: str,
        task_id: str,
        risk: RiskClass,
        topology: str,
        candidates: Iterable[dict[str, Any]],
        expected_crew_id: str,
        provenance: dict[str, Any],
        case_id: str | None = None,
    ) -> str:
        if topology not in {"sequential", "parallel"}:
            raise ValueError("routing evaluation topology must be sequential or parallel")
        normalized = []
        for candidate in candidates:
            cid = str(candidate.get("crew_id") or "").strip()
            if not cid:
                raise ValueError("routing candidate crew_id is required")
            components = dict(candidate.get("components") or {})
            # Validate keys/weights by scoring once with the immutable production baseline.
            weighted_routing_score(components, DEFAULT_ROUTING_WEIGHTS)
            normalized.append({"crew_id": cid, "eligible": bool(candidate.get("eligible", True)), "components": components})
        if len(normalized) < 2:
            raise ValueError("routing evaluation requires at least two candidates")
        expected = next((c for c in normalized if c["crew_id"] == expected_crew_id), None)
        if not expected or not expected["eligible"]:
            raise ValueError("expected Crew must be an eligible candidate")
        return self.ledger.add_case(
            suite=suite, case_type="routing", case_id=case_id,
            payload={"task_id": task_id, "risk": risk.value, "topology": topology, "candidates": normalized},
            expected={"selected_crew_id": expected_crew_id}, provenance=provenance,
        )

    def run_routing_suite(
        self,
        suite: str,
        *,
        policy_name: str,
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        cases = self.ledger.cases(suite, case_type="routing")
        if not cases:
            raise ValueError(f"routing evaluation suite has no cases: {suite}")
        weights = {**DEFAULT_ROUTING_WEIGHTS, **(weights or {})}
        # Validation is centralized in the production scoring function.
        weighted_routing_score({}, weights)
        results = []
        invariant_failures = 0
        topology = {"sequential": 0, "parallel": 0}
        for case in cases:
            payload = case["payload"]
            topology[payload["topology"]] = topology.get(payload["topology"], 0) + 1
            eligible = [c for c in payload["candidates"] if c["eligible"]]
            failures: list[str] = []
            if not eligible:
                selected = None
                failures.append("no_eligible_crew")
            else:
                ranked = sorted(
                    ((weighted_routing_score(c["components"], weights), c["crew_id"], c) for c in eligible),
                    key=lambda item: (-item[0], item[1]),
                )
                selected = ranked[0][1]
                if not ranked[0][2]["eligible"]:
                    failures.append("ineligible_crew_selected")
            expected = case["expected"]["selected_crew_id"]
            passed = selected == expected and not failures
            invariant_failures += len(failures)
            results.append({
                "case_id": case["case_id"], "task_id": payload["task_id"], "risk": payload["risk"],
                "topology": payload["topology"], "selected_crew_id": selected, "expected_crew_id": expected,
                "passed": passed, "invariant_failures": failures,
            })
        passes = sum(1 for r in results if r["passed"])
        metrics = {
            "cases": len(results), "passes": passes, "accuracy": passes / len(results),
            "failures": len(results) - passes, "topology": topology,
        }
        invariants = {"failures": invariant_failures, "authority_filter": invariant_failures == 0}
        run_id = self.ledger.record_run(
            suite=suite, evaluator="routing-replay-v1", policy_name=policy_name,
            config={"weights": weights}, metrics=metrics, invariants=invariants, case_results=results,
        )
        return {"run_id": run_id, "metrics": metrics, "invariants": invariants, "case_results": results, "weights": weights}

    @staticmethod
    def _one_sided_sign_p(wins: int, losses: int) -> float:
        discordant = wins + losses
        if discordant == 0 or wins <= losses:
            return 1.0
        numerator = sum(math.comb(discordant, k) for k in range(wins, discordant + 1))
        return numerator / (2 ** discordant)

    def compare_routing_runs(self, baseline_run_id: str, candidate_run_id: str, *, alpha: float = 0.05) -> EvaluationComparison:
        baseline = self.ledger.run(baseline_run_id)
        candidate = self.ledger.run(candidate_run_id)
        if baseline["suite"] != candidate["suite"]:
            raise ValueError("paired evaluation runs must use the same suite")
        b = {r["case_id"]: r for r in baseline["case_results"]}
        c = {r["case_id"]: r for r in candidate["case_results"]}
        if set(b) != set(c):
            raise ValueError("paired evaluation runs must contain the same cases")
        if len(b) < 20:
            raise ValueError("statistical improvement gate requires at least 20 paired cases")
        wins = losses = ties = 0
        for case_id in sorted(b):
            bp, cp = bool(b[case_id]["passed"]), bool(c[case_id]["passed"])
            if cp and not bp:
                wins += 1
            elif bp and not cp:
                losses += 1
            else:
                ties += 1
        p_value = self._one_sided_sign_p(wins, losses)
        invariant_regressions = max(0, int(candidate["invariants"]["failures"]) - int(baseline["invariants"]["failures"]))
        statistically_better = (
            candidate["metrics"]["passes"] > baseline["metrics"]["passes"]
            and wins > losses
            and p_value <= alpha
            and invariant_regressions == 0
            and int(candidate["invariants"]["failures"]) == 0
        )
        return EvaluationComparison(
            baseline_run_id=baseline_run_id, candidate_run_id=candidate_run_id, cases=len(b),
            baseline_passes=int(baseline["metrics"]["passes"]), candidate_passes=int(candidate["metrics"]["passes"]),
            wins=wins, losses=losses, ties=ties, p_value=p_value, alpha=alpha,
            invariant_regressions=invariant_regressions, statistically_better=statistically_better,
        )

    def find_routing_improvement(self, suite: str) -> dict[str, Any]:
        baseline = self.run_routing_suite(suite, policy_name="production-baseline", weights=DEFAULT_ROUTING_WEIGHTS)
        profiles = {
            "risk-guarded": {"risk": 3.0},
            "reliability-guarded": {"reliability": 2.0, "risk": 2.0},
            "evidence-guarded": {"evidence_quality": 2.0, "risk": 2.0},
            "efficiency-guarded": {"cost": 1.5, "latency": 1.5},
        }
        candidates = []
        for name, override in profiles.items():
            run = self.run_routing_suite(suite, policy_name=name, weights=override)
            comparison = self.compare_routing_runs(baseline["run_id"], run["run_id"])
            candidates.append((comparison.statistically_better, run["metrics"]["accuracy"], -comparison.p_value, name, override, run, comparison))
        qualified = [item for item in candidates if item[0]]
        if not qualified:
            return {"proposal_id": None, "baseline_run_id": baseline["run_id"], "qualified": False,
                    "comparisons": [item[-1].to_dict() for item in candidates]}
        qualified.sort(key=lambda item: (-item[1], -item[2], item[3]))
        _, _, _, name, override, run, comparison = qualified[0]
        proposal_id = self.ledger.create_proposal(
            proposal_type="routing", target="LivingCompanyIntelligence.routing_component_weights",
            proposed_change={"profile": name, "weight_overrides": override},
            rationale="Paired replay shows statistically better routing with no authority, safety, or verification invariant regression.",
            evidence={"suite": suite, "comparison": comparison.to_dict()},
            baseline_run_id=baseline["run_id"], candidate_run_id=run["run_id"],
        )
        return {
            "proposal_id": proposal_id, "baseline_run_id": baseline["run_id"], "candidate_run_id": run["run_id"],
            "qualified": True, "profile": name, "comparison": comparison.to_dict(),
        }

    def propose(
        self,
        *,
        proposal_type: str,
        target: str,
        proposed_change: dict[str, Any],
        rationale: str,
        evidence: dict[str, Any],
    ) -> str:
        return self.ledger.create_proposal(
            proposal_type=proposal_type, target=target, proposed_change=proposed_change,
            rationale=rationale, evidence=evidence,
        )

    def activate_proposal(self, proposal_id: str) -> None:
        self.ledger.activate(proposal_id)
