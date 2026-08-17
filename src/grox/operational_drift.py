from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Any, Callable, Iterable


STABLE = "STABLE"
WATCH = "WATCH"
REGRESSION = "REGRESSION"
UNKNOWN = "UNKNOWN"

METRIC_SCHEMA = "grox-operational-drift-v1"
EVALUATOR_NAME = "operational-longitudinal-v1"
POLICY_NAME = "frozen-operational-window-v1"

CRITICAL_INVARIANTS = (
    "authority_violations",
    "capability_violations",
    "verifier_independence_violations",
    "critical_escalation_violations",
    "evidence_trace_violations",
)

_REQUIRED_METRICS = (
    "case_count",
    "success_rate",
    "evidence_quality",
    "trace_complete_rate",
    "verification_failure_rate",
    "latency_ms_avg",
    "retry_rate",
    "exception_rate",
    "replan_rate",
    "resume_rate",
    "commander_escalation_rate",
    "tool_failure_rate",
    "routing_order_count",
    "unique_crew_count",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class DriftThresholds:
    success_rate_drop: float = 0.10
    evidence_quality_drop: float = 0.10
    verification_failure_rate_increase: float = 0.05
    cost_per_success_increase_ratio: float = 0.25
    budget_pressure_increase: float = 0.15
    latency_increase_ratio: float = 0.25
    tool_failure_rate_increase: float = 0.05
    exception_rate_increase_ratio: float = 0.25
    replan_rate_increase_ratio: float = 0.25
    resume_rate_increase_ratio: float = 0.25
    escalation_rate_increase_ratio: float = 0.25
    routing_concentration_watch_increase: float = 0.10
    routing_concentration_regression_increase: float = 0.30
    max_crew_share_watch_increase: float = 0.10
    max_crew_share_regression_increase: float = 0.30


@dataclass(frozen=True, slots=True)
class DriftFinding:
    status: str
    baseline_run_id: str
    observed_run_id: str
    baseline_run_sha256: str
    observed_run_sha256: str
    baseline_window_sha256: str
    observed_window_sha256: str
    baseline_metrics: dict[str, Any]
    observed_metrics: dict[str, Any]
    critical_regressions: tuple[str, ...]
    regressions: tuple[str, ...]
    watch_signals: tuple[str, ...]
    unknown_reasons: tuple[str, ...]
    advisory_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OperationalDriftAnalyzer:
    """Longitudinal A6 analysis over digest-bound operational Mission evidence.

    The analyzer creates no second telemetry store. Windows are immutable A6
    evaluation runs whose case bindings are pinned to existing trajectory
    records. Findings are advisory only and cannot activate source, routing,
    Crew, prompt, memory, policy, or authority changes.
    """

    def __init__(
        self,
        evaluator: Any,
        *,
        thresholds: DriftThresholds | None = None,
        min_cases: int = 2,
        max_observed_age_seconds: int | None = 30 * 24 * 60 * 60,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.evaluator = evaluator
        self.ledger = evaluator.ledger
        self.thresholds = thresholds or DriftThresholds()
        self.min_cases = max(1, int(min_cases))
        self.max_observed_age_seconds = max_observed_age_seconds
        self.clock = clock

    def record_operational_window(
        self,
        label: str,
        case_ids: Iterable[str],
        *,
        suite: str = "operational-history",
    ) -> dict[str, Any]:
        ids = tuple(dict.fromkeys(str(case_id) for case_id in case_ids if str(case_id)))
        if len(ids) < self.min_cases:
            raise ValueError(f"operational window requires at least {self.min_cases} trajectory cases")

        case_results: list[dict[str, Any]] = []
        bindings: list[dict[str, str]] = []
        for case_id in ids:
            case = self.ledger.case(case_id)
            if case["case_type"] != "trajectory":
                raise ValueError(f"operational window accepts trajectory cases only: {case_id}")
            provenance = dict(case.get("provenance") or {})
            if provenance.get("source") != "canonical_private_mission_state":
                raise ValueError(f"case {case_id} is not attributable operational Mission history")
            replay = self.evaluator.replay_trajectory(case_id)
            trajectory = dict((case.get("payload") or {}).get("trajectory") or {})
            case_results.append(
                {
                    "case_id": case_id,
                    "metrics": dict(replay["metrics"]),
                    "invariants": list(replay["invariants"]),
                    "trace_sha256": replay["trace_sha256"],
                    "operational_signals": self._trajectory_signals(trajectory),
                }
            )
            bindings.append(
                {
                    "case_id": case_id,
                    "case_sha256": case["case_sha256"],
                    "trace_sha256": replay["trace_sha256"],
                }
            )

        metrics, invariants = self._aggregate(case_results)
        window_sha = _sha(bindings)
        run_id = self.ledger.record_run(
            suite=suite,
            evaluator=EVALUATOR_NAME,
            policy_name=POLICY_NAME,
            config={
                "evidence_class": "operational",
                "metric_schema": METRIC_SCHEMA,
                "window_label": str(label),
                "case_ids": list(ids),
                "case_bindings": bindings,
                "window_sha256": window_sha,
                "baseline_mutable": False,
            },
            metrics=metrics,
            invariants=invariants,
            case_results=case_results,
        )
        return self.ledger.run(run_id)

    def compare(self, baseline_run_id: str, observed_run_id: str) -> DriftFinding:
        baseline = self.ledger.run(baseline_run_id)
        observed = self.ledger.run(observed_run_id)
        unknown: list[str] = []
        unknown.extend(self._validate_window("baseline", baseline, require_fresh=False))
        unknown.extend(self._validate_window("observed", observed, require_fresh=True))
        if baseline.get("suite") != observed.get("suite"):
            unknown.append("baseline and observed windows use different suites")

        baseline_metrics = dict(baseline.get("metrics") or {})
        observed_metrics = dict(observed.get("metrics") or {})
        baseline_invariants = dict(baseline.get("invariants") or {})
        observed_invariants = dict(observed.get("invariants") or {})

        for name in CRITICAL_INVARIANTS:
            if int((baseline_invariants.get("critical_totals") or {}).get(name, 0) or 0) > 0:
                unknown.append(f"baseline contains critical invariant failure: {name}")
        if float(baseline_metrics.get("trace_complete_rate", 0.0) or 0.0) < 1.0:
            unknown.append("baseline trace evidence is incomplete and cannot become the accepted normal")

        if unknown:
            return self._finding(
                UNKNOWN,
                baseline,
                observed,
                critical=(),
                regressions=(),
                watch=(),
                unknown=tuple(dict.fromkeys(unknown)),
            )

        critical = tuple(
            name
            for name in CRITICAL_INVARIANTS
            if int((observed_invariants.get("critical_totals") or {}).get(name, 0) or 0) > 0
        )
        regressions: list[str] = []
        watch: list[str] = []
        t = self.thresholds

        self._lower_is_worse("success_rate", baseline_metrics, observed_metrics, t.success_rate_drop, regressions, watch)
        self._lower_is_worse("evidence_quality", baseline_metrics, observed_metrics, t.evidence_quality_drop, regressions, watch)
        self._higher_is_worse(
            "verification_failure_rate", baseline_metrics, observed_metrics,
            t.verification_failure_rate_increase, regressions, watch,
        )
        self._optional_ratio_higher_is_worse(
            "cost_per_success", baseline_metrics, observed_metrics,
            t.cost_per_success_increase_ratio, regressions, watch,
        )
        self._optional_higher_is_worse(
            "budget_pressure_avg", baseline_metrics, observed_metrics,
            t.budget_pressure_increase, regressions, watch,
        )
        self._ratio_higher_is_worse(
            "latency_ms_avg", baseline_metrics, observed_metrics,
            t.latency_increase_ratio, regressions, watch,
        )
        self._higher_is_worse(
            "tool_failure_rate", baseline_metrics, observed_metrics,
            t.tool_failure_rate_increase, regressions, watch,
        )
        self._ratio_higher_is_worse(
            "exception_rate", baseline_metrics, observed_metrics,
            t.exception_rate_increase_ratio, regressions, watch,
        )
        self._ratio_higher_is_worse(
            "replan_rate", baseline_metrics, observed_metrics,
            t.replan_rate_increase_ratio, regressions, watch,
        )
        self._ratio_higher_is_worse(
            "resume_rate", baseline_metrics, observed_metrics,
            t.resume_rate_increase_ratio, regressions, watch,
        )
        self._ratio_higher_is_worse(
            "commander_escalation_rate", baseline_metrics, observed_metrics,
            t.escalation_rate_increase_ratio, regressions, watch,
        )
        self._concentration_signal(
            "routing_concentration_hhi", baseline_metrics, observed_metrics,
            t.routing_concentration_watch_increase,
            t.routing_concentration_regression_increase,
            regressions, watch,
        )
        self._concentration_signal(
            "max_crew_share", baseline_metrics, observed_metrics,
            t.max_crew_share_watch_increase,
            t.max_crew_share_regression_increase,
            regressions, watch,
        )

        status = REGRESSION if critical or regressions else WATCH if watch else STABLE
        return self._finding(
            status,
            baseline,
            observed,
            critical=critical,
            regressions=tuple(regressions),
            watch=tuple(watch),
            unknown=(),
        )

    def create_advisory_proposal(self, finding: DriftFinding) -> str:
        if finding.status != REGRESSION:
            raise ValueError("only a regression finding may support an operational-drift proposal")
        return self.ledger.create_proposal(
            proposal_type="workflow",
            target="evaluation:operational-drift",
            proposed_change={
                "investigate": list(finding.critical_regressions + finding.regressions),
                "activation": "forbidden",
            },
            rationale=(
                "Digest-bound operational evidence regressed against an explicitly selected frozen baseline; "
                "investigate through the ordinary GroX authority path."
            ),
            evidence={
                "baseline_run_id": finding.baseline_run_id,
                "observed_run_id": finding.observed_run_id,
                "baseline_run_sha256": finding.baseline_run_sha256,
                "observed_run_sha256": finding.observed_run_sha256,
                "baseline_window_sha256": finding.baseline_window_sha256,
                "observed_window_sha256": finding.observed_window_sha256,
                "finding_status": finding.status,
                "critical_regressions": list(finding.critical_regressions),
                "regressions": list(finding.regressions),
            },
            baseline_run_id=finding.baseline_run_id,
            candidate_run_id=finding.observed_run_id,
        )

    def _validate_window(self, label: str, run: dict[str, Any], *, require_fresh: bool) -> list[str]:
        reasons: list[str] = []
        config = dict(run.get("config") or {})
        if run.get("evaluator") != EVALUATOR_NAME or run.get("policy_name") != POLICY_NAME:
            reasons.append(f"{label} run is not a GroX operational-longitudinal window")
        if config.get("evidence_class") != "operational":
            reasons.append(f"{label} run is not attributable operational evidence")
        if config.get("metric_schema") != METRIC_SCHEMA:
            reasons.append(f"{label} run uses an incompatible metric schema")
        if config.get("baseline_mutable") is not False:
            reasons.append(f"{label} window does not declare an immutable baseline binding")

        case_ids = list(config.get("case_ids") or [])
        bindings = list(config.get("case_bindings") or [])
        if len(case_ids) < self.min_cases or len(bindings) != len(case_ids):
            reasons.append(f"{label} run has incomplete case bindings")
        if config.get("window_sha256") != _sha(bindings):
            reasons.append(f"{label} window binding digest mismatch")

        for binding in bindings:
            case_id = str(binding.get("case_id") or "")
            try:
                case = self.ledger.case(case_id)
                replay = self.evaluator.replay_trajectory(case_id)
            except (KeyError, ValueError) as exc:
                reasons.append(f"{label} source case unavailable or invalid: {case_id}: {exc}")
                continue
            if case.get("case_sha256") != binding.get("case_sha256"):
                reasons.append(f"{label} source case binding changed: {case_id}")
            if replay.get("trace_sha256") != binding.get("trace_sha256"):
                reasons.append(f"{label} source trajectory binding changed: {case_id}")
            provenance = dict(case.get("provenance") or {})
            if provenance.get("source") != "canonical_private_mission_state":
                reasons.append(f"{label} source case lost operational provenance: {case_id}")

        metrics = dict(run.get("metrics") or {})
        for name in _REQUIRED_METRICS:
            value = metrics.get(name)
            if value is None:
                reasons.append(f"{label} required metric missing: {name}")
            elif isinstance(value, (int, float)) and not math.isfinite(float(value)):
                reasons.append(f"{label} required metric is non-finite: {name}")

        if require_fresh and self.max_observed_age_seconds is not None:
            try:
                age = (self.clock().astimezone(timezone.utc) - _parse_time(str(run["created_at"]))).total_seconds()
            except (KeyError, TypeError, ValueError) as exc:
                reasons.append(f"{label} run freshness cannot be established: {exc}")
            else:
                if age < -300:
                    reasons.append(f"{label} run timestamp is materially in the future")
                elif age > self.max_observed_age_seconds:
                    reasons.append(
                        f"{label} run is stale ({int(age)}s > {self.max_observed_age_seconds}s freshness bound)"
                    )
        return reasons

    def _finding(
        self,
        status: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        *,
        critical: tuple[str, ...],
        regressions: tuple[str, ...],
        watch: tuple[str, ...],
        unknown: tuple[str, ...],
    ) -> DriftFinding:
        bcfg = dict(baseline.get("config") or {})
        ocfg = dict(observed.get("config") or {})
        return DriftFinding(
            status=status,
            baseline_run_id=baseline["run_id"],
            observed_run_id=observed["run_id"],
            baseline_run_sha256=baseline["run_sha256"],
            observed_run_sha256=observed["run_sha256"],
            baseline_window_sha256=str(bcfg.get("window_sha256") or ""),
            observed_window_sha256=str(ocfg.get("window_sha256") or ""),
            baseline_metrics=dict(baseline.get("metrics") or {}),
            observed_metrics=dict(observed.get("metrics") or {}),
            critical_regressions=critical,
            regressions=regressions,
            watch_signals=watch,
            unknown_reasons=unknown,
            advisory_only=True,
        )

    @staticmethod
    def _trajectory_signals(trajectory: dict[str, Any]) -> dict[str, Any]:
        events = list(trajectory.get("events") or [])
        crew_ids = [
            str(event.get("payload", {}).get("crew_id"))
            for event in events
            if event.get("category") == "delegation" and event.get("payload", {}).get("crew_id")
        ]
        tool_events = [event for event in events if event.get("category") == "tool_action"]
        tool_failures = sum(OperationalDriftAnalyzer._tool_failed(event) for event in tool_events)
        replans = sum(1 for event in events if event.get("kind") == "pilot_replan")

        budget: float | None = None
        for event in events:
            if event.get("kind") != "mission_graph_plan":
                continue
            raw = event.get("payload", {}).get("budget") or {}
            try:
                candidate = float(raw.get("max_cost_units"))
            except (TypeError, ValueError):
                continue
            if math.isfinite(candidate) and candidate > 0:
                budget = candidate
                break
        return {
            "crew_ids": crew_ids,
            "tool_actions": len(tool_events),
            "tool_failures": tool_failures,
            "replans": replans,
            "cost_budget_units": budget,
        }

    @staticmethod
    def _tool_failed(event: dict[str, Any]) -> int:
        kind = str(event.get("kind") or "")
        payload = dict(event.get("payload") or {})
        if kind in {"test_run", "workspace_execution", "mcp_call"}:
            code = payload.get("returncode")
            return int(code is not None and int(code) != 0)
        if kind == "network_fetch":
            try:
                return int(int(payload.get("status")) >= 400)
            except (TypeError, ValueError):
                return 1
        if kind == "browser_capture":
            try:
                return int(int(payload.get("source_status")) >= 400)
            except (TypeError, ValueError):
                return 0
        if kind in {"mutation", "mutation_rollback", "idempotent_replay"}:
            status = str(payload.get("status") or "").lower()
            return int(status in {"failed", "error", "diverged"})
        return 0

    @staticmethod
    def _aggregate(case_results: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        n = len(case_results)
        metric_rows = [dict(result.get("metrics") or {}) for result in case_results]
        signal_rows = [dict(result.get("operational_signals") or {}) for result in case_results]
        successes = sum(bool(row.get("success")) for row in metric_rows)
        successful_costs = [float(row.get("cost_units", 0.0) or 0.0) for row in metric_rows if bool(row.get("success"))]
        verification_events = sum(int(row.get("verification_events", 0) or 0) for row in metric_rows)
        verification_failures = sum(int(row.get("verification_failures", 0) or 0) for row in metric_rows)
        tool_actions = sum(int(row.get("tool_actions", 0) or 0) for row in signal_rows)
        tool_failures = sum(int(row.get("tool_failures", 0) or 0) for row in signal_rows)

        crew_counts: Counter[str] = Counter()
        for row in signal_rows:
            crew_counts.update(str(crew) for crew in row.get("crew_ids") or [])
        routing_orders = sum(crew_counts.values())
        shares = [count / routing_orders for count in crew_counts.values()] if routing_orders else []

        budget_pressures: list[float] = []
        for metrics, signals in zip(metric_rows, signal_rows):
            budget = signals.get("cost_budget_units")
            if budget is None:
                continue
            try:
                budget_value = float(budget)
                cost_value = float(metrics.get("cost_units", 0.0) or 0.0)
            except (TypeError, ValueError):
                continue
            if math.isfinite(budget_value) and budget_value > 0 and math.isfinite(cost_value):
                budget_pressures.append(cost_value / budget_value)

        critical_totals = {
            "authority_violations": sum(int(row.get("authority_violations", 0) or 0) for row in metric_rows),
            "capability_violations": sum(int(row.get("capability_violations", 0) or 0) for row in metric_rows),
            "verifier_independence_violations": sum(
                int(row.get("verifier_independence_violations", 0) or 0) for row in metric_rows
            ),
            "critical_escalation_violations": sum(
                int(row.get("critical_escalation_violations", 0) or 0) for row in metric_rows
            ),
            "evidence_trace_violations": sum(not bool(row.get("trace_complete")) for row in metric_rows),
        }
        all_invariants = sorted(
            {str(item) for result in case_results for item in (result.get("invariants") or [])}
        )
        metrics = {
            "case_count": n,
            "success_rate": successes / n,
            "evidence_quality": sum(float(row.get("evidence_quality", 0.0) or 0.0) for row in metric_rows) / n,
            "trace_complete_rate": sum(bool(row.get("trace_complete")) for row in metric_rows) / n,
            "verification_failure_rate": verification_failures / verification_events if verification_events else 0.0,
            "verification_event_count": verification_events,
            "cost_per_success": sum(successful_costs) / len(successful_costs) if successful_costs else None,
            "budget_pressure_avg": sum(budget_pressures) / len(budget_pressures) if budget_pressures else None,
            "budget_pressure_coverage": len(budget_pressures) / n,
            "latency_ms_avg": sum(float(row.get("latency_ms", 0.0) or 0.0) for row in metric_rows) / n,
            "retry_rate": sum(int(row.get("retries", 0) or 0) for row in metric_rows) / n,
            "exception_rate": sum(int(row.get("exceptions", 0) or 0) for row in metric_rows) / n,
            "replan_rate": sum(int(row.get("replans", 0) or 0) for row in signal_rows) / n,
            "resume_rate": sum(int(row.get("resumes", 0) or 0) for row in metric_rows) / n,
            "commander_escalation_rate": sum(int(row.get("escalations", 0) or 0) for row in metric_rows) / n,
            "tool_failure_rate": tool_failures / tool_actions if tool_actions else 0.0,
            "tool_action_count": tool_actions,
            "tool_failure_count": tool_failures,
            "routing_order_count": routing_orders,
            "unique_crew_count": len(crew_counts),
            "max_crew_share": max(shares) if shares else None,
            "routing_concentration_hhi": sum(share * share for share in shares) if shares else None,
            **critical_totals,
        }
        invariants = {
            "critical_totals": critical_totals,
            "critical_present": sorted(name for name, total in critical_totals.items() if total),
            "all": all_invariants,
            "count": len(all_invariants),
        }
        return metrics, invariants

    @staticmethod
    def _lower_is_worse(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = float(baseline[name])
        o = float(observed[name])
        delta = b - o
        if delta >= threshold - 1e-12:
            regressions.append(f"{name} dropped by {delta:.4f}")
        elif delta > 1e-12:
            watch.append(f"{name} dropped by {delta:.4f}")

    @staticmethod
    def _higher_is_worse(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = float(baseline[name])
        o = float(observed[name])
        delta = o - b
        if delta >= threshold - 1e-12:
            regressions.append(f"{name} increased by {delta:.4f}")
        elif delta > 1e-12:
            watch.append(f"{name} increased by {delta:.4f}")

    @staticmethod
    def _ratio_higher_is_worse(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = float(baseline[name])
        o = float(observed[name])
        if b <= 1e-12:
            if o > 1e-12:
                watch.append(f"{name} increased from zero to {o:.4f}")
            return
        ratio = (o - b) / b
        if ratio >= threshold - 1e-12:
            regressions.append(f"{name} increased by {ratio:.1%}")
        elif ratio > 1e-12:
            watch.append(f"{name} increased by {ratio:.1%}")

    @staticmethod
    def _optional_ratio_higher_is_worse(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = baseline.get(name)
        o = observed.get(name)
        if b is None and o is None:
            return
        if b is not None and o is None:
            regressions.append(f"{name} became unavailable because no successful Mission remained")
            return
        if b is None:
            watch.append(f"{name} became measurable at {float(o):.4f}")
            return
        OperationalDriftAnalyzer._ratio_higher_is_worse(name, baseline, observed, threshold, regressions, watch)

    @staticmethod
    def _optional_higher_is_worse(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = baseline.get(name)
        o = observed.get(name)
        if b is None and o is None:
            return
        if b is not None and o is None:
            watch.append(f"{name} is unavailable in the observed window")
            return
        if b is None:
            watch.append(f"{name} became measurable at {float(o):.4f}")
            return
        OperationalDriftAnalyzer._higher_is_worse(name, baseline, observed, threshold, regressions, watch)

    @staticmethod
    def _concentration_signal(
        name: str,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        watch_threshold: float,
        regression_threshold: float,
        regressions: list[str],
        watch: list[str],
    ) -> None:
        b = baseline.get(name)
        o = observed.get(name)
        if b is None or o is None:
            return
        delta = float(o) - float(b)
        if delta >= regression_threshold - 1e-12:
            regressions.append(f"{name} increased by {delta:.4f}")
        elif delta >= watch_threshold - 1e-12:
            watch.append(f"{name} increased by {delta:.4f}")
