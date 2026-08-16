from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable


STABLE = "STABLE"
WATCH = "WATCH"
REGRESSION = "REGRESSION"
UNKNOWN = "UNKNOWN"

CRITICAL_INVARIANTS = (
    "capability_violations",
    "verifier_independence_violations",
    "critical_escalation_violations",
    "authority_violations",
)


@dataclass(frozen=True, slots=True)
class DriftThresholds:
    success_rate_drop: float = 0.10
    evidence_quality_drop: float = 0.10
    trace_complete_rate_drop: float = 0.10
    verification_failure_rate_increase: float = 0.05
    cost_per_success_increase_ratio: float = 0.25
    latency_increase_ratio: float = 0.25
    resume_rate_increase: float = 0.25
    escalation_rate_increase: float = 0.25


@dataclass(frozen=True, slots=True)
class DriftFinding:
    status: str
    baseline_run_id: str
    observed_run_id: str
    baseline_digest: str
    observed_digest: str
    baseline_metrics: dict
    observed_metrics: dict
    critical_regressions: tuple[str, ...]
    regressions: tuple[str, ...]
    watch_signals: tuple[str, ...]
    unknown_reasons: tuple[str, ...]
    advisory_only: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


class OperationalDriftAnalyzer:
    """A6 longitudinal comparison over immutable existing evaluation runs.

    No new telemetry truth store is introduced. Baseline and observed windows
    are ordinary SHA-bound A6 evaluation runs. Analysis verifies those records
    through the existing ledger and never modifies either run. Findings are
    advisory only and can at most support an ordinary A6 proposal.
    """

    def __init__(self, evaluator, *, thresholds: DriftThresholds | None = None, min_cases: int = 2):
        self.evaluator = evaluator
        self.ledger = evaluator.ledger
        self.thresholds = thresholds or DriftThresholds()
        self.min_cases = max(1, int(min_cases))

    def record_operational_window(self, label: str, case_ids: Iterable[str], *, suite: str = "operational-history") -> dict:
        ids = tuple(dict.fromkeys(str(case_id) for case_id in case_ids if str(case_id)))
        if len(ids) < self.min_cases:
            raise ValueError(f"operational window requires at least {self.min_cases} trajectory cases")
        case_results: list[dict] = []
        for case_id in ids:
            case = self.ledger.case(case_id)
            if case["case_type"] != "trajectory":
                raise ValueError(f"operational window accepts trajectory cases only: {case_id}")
            provenance = dict(case.get("provenance") or {})
            if provenance.get("source") != "canonical_private_mission_state":
                raise ValueError(f"case {case_id} is not attributable operational Mission history")
            replay = self.evaluator.replay_trajectory(case_id)
            case_results.append({
                "case_id": case_id,
                "metrics": dict(replay["metrics"]),
                "invariants": list(replay["invariants"]),
            })
        metrics, invariants = self._aggregate(case_results)
        run_id = self.ledger.record_run(
            suite=suite,
            evaluator="operational-longitudinal-v1",
            policy_name="frozen-operational-window-v1",
            config={
                "evidence_class": "operational",
                "window_label": str(label),
                "case_ids": list(ids),
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
        for label, run in (("baseline", baseline), ("observed", observed)):
            config = dict(run.get("config") or {})
            if config.get("evidence_class") != "operational":
                unknown.append(f"{label} run is not attributable operational evidence")
            case_results = list(run.get("case_results") or [])
            if len(case_results) < self.min_cases:
                unknown.append(f"{label} run has fewer than {self.min_cases} cases")
        if baseline.get("suite") != observed.get("suite"):
            unknown.append("baseline and observed windows use different suites")
        if unknown:
            return DriftFinding(
                UNKNOWN,
                baseline_run_id,
                observed_run_id,
                baseline["digest"],
                observed["digest"],
                dict(baseline.get("metrics") or {}),
                dict(observed.get("metrics") or {}),
                (), (), (), tuple(unknown), True,
            )

        b = dict(baseline["metrics"])
        o = dict(observed["metrics"])
        critical = tuple(
            name for name in CRITICAL_INVARIANTS
            if float(o.get(name, 0.0)) > float(b.get(name, 0.0))
        )
        regressions: list[str] = []
        watch: list[str] = []
        t = self.thresholds

        self._lower_is_worse("success_rate", b, o, t.success_rate_drop, regressions, watch)
        self._lower_is_worse("evidence_quality", b, o, t.evidence_quality_drop, regressions, watch)
        self._lower_is_worse("trace_complete_rate", b, o, t.trace_complete_rate_drop, regressions, watch)
        self._higher_is_worse("verification_failure_rate", b, o, t.verification_failure_rate_increase, regressions, watch)
        self._ratio_higher_is_worse("cost_per_success", b, o, t.cost_per_success_increase_ratio, regressions, watch)
        self._ratio_higher_is_worse("latency_avg", b, o, t.latency_increase_ratio, regressions, watch)
        self._higher_is_worse("resume_rate", b, o, t.resume_rate_increase, regressions, watch)
        self._higher_is_worse("commander_escalation_rate", b, o, t.escalation_rate_increase, regressions, watch)

        status = REGRESSION if critical or regressions else WATCH if watch else STABLE
        return DriftFinding(
            status,
            baseline_run_id,
            observed_run_id,
            baseline["digest"],
            observed["digest"],
            b, o,
            critical,
            tuple(regressions),
            tuple(watch),
            (),
            True,
        )

    def create_advisory_proposal(self, finding: DriftFinding) -> str:
        if finding.status != REGRESSION:
            raise ValueError("only a regression finding may support a drift proposal")
        return self.ledger.create_proposal(
            "workflow",
            "evaluation:operational-drift",
            {
                "baseline_run_id": finding.baseline_run_id,
                "observed_run_id": finding.observed_run_id,
                "investigate": list(finding.critical_regressions + finding.regressions),
                "activation": "forbidden",
            },
            "Operational evidence regressed against an immutable A6 baseline; investigate through the ordinary GroX authority path.",
            [finding.baseline_run_id, finding.observed_run_id],
            baseline_run_id=finding.baseline_run_id,
            candidate_run_id=finding.observed_run_id,
        )

    @staticmethod
    def _aggregate(case_results: list[dict]) -> tuple[dict, list[str]]:
        n = len(case_results)
        metrics_list = [dict(result.get("metrics") or {}) for result in case_results]
        success_count = sum(bool(m.get("success")) for m in metrics_list)
        verification_events = sum(int(m.get("verification_events", 0) or 0) for m in metrics_list)
        verification_failures = sum(int(m.get("verification_failures", 0) or 0) for m in metrics_list)
        successful_costs = [float(m.get("cost_units", 0.0) or 0.0) for m in metrics_list if bool(m.get("success"))]
        aggregates = {
            "case_count": n,
            "success_rate": success_count / n,
            "evidence_quality": sum(float(m.get("evidence_quality", 0.0) or 0.0) for m in metrics_list) / n,
            "trace_complete_rate": sum(bool(m.get("trace_complete")) for m in metrics_list) / n,
            "verification_failure_rate": verification_failures / verification_events if verification_events else 0.0,
            "cost_per_success": sum(successful_costs) / len(successful_costs) if successful_costs else math.inf,
            "latency_avg": sum(float(m.get("latency_seconds", 0.0) or 0.0) for m in metrics_list) / n,
            "resume_rate": sum(int(m.get("resumes", 0) or 0) for m in metrics_list) / n,
            "commander_escalation_rate": sum(int(m.get("commander_escalations", 0) or 0) for m in metrics_list) / n,
            "retry_rate": sum(int(m.get("retries", 0) or 0) for m in metrics_list) / n,
            "exception_rate": sum(int(m.get("exceptions", 0) or 0) for m in metrics_list) / n,
        }
        invariants: list[str] = []
        for name in CRITICAL_INVARIANTS:
            total = sum(int(m.get(name, 0) or 0) for m in metrics_list)
            aggregates[name] = total
            if total:
                invariants.append(f"{name}:{total}")
        if any(not bool(m.get("trace_complete")) for m in metrics_list):
            invariants.append("trace_incomplete")
        return aggregates, sorted(invariants)

    @staticmethod
    def _lower_is_worse(name: str, baseline: dict, observed: dict, threshold: float, regressions: list[str], watch: list[str]) -> None:
        b = float(baseline.get(name, 0.0))
        o = float(observed.get(name, 0.0))
        delta = b - o
        if delta >= threshold - 1e-12:
            regressions.append(f"{name} dropped by {delta:.4f}")
        elif delta > 1e-12:
            watch.append(f"{name} dropped by {delta:.4f}")

    @staticmethod
    def _higher_is_worse(name: str, baseline: dict, observed: dict, threshold: float, regressions: list[str], watch: list[str]) -> None:
        b = float(baseline.get(name, 0.0))
        o = float(observed.get(name, 0.0))
        delta = o - b
        if delta >= threshold - 1e-12:
            regressions.append(f"{name} increased by {delta:.4f}")
        elif delta > 1e-12:
            watch.append(f"{name} increased by {delta:.4f}")

    @staticmethod
    def _ratio_higher_is_worse(name: str, baseline: dict, observed: dict, threshold: float, regressions: list[str], watch: list[str]) -> None:
        b = float(baseline.get(name, 0.0))
        o = float(observed.get(name, 0.0))
        if not math.isfinite(b) or not math.isfinite(o):
            if math.isfinite(b) and not math.isfinite(o):
                regressions.append(f"{name} became unbounded")
            return
        if b <= 1e-12:
            if o > 1e-12:
                watch.append(f"{name} increased from zero to {o:.4f}")
            return
        ratio = (o - b) / b
        if ratio >= threshold - 1e-12:
            regressions.append(f"{name} increased by {ratio:.1%}")
        elif ratio > 1e-12:
            watch.append(f"{name} increased by {ratio:.1%}")
