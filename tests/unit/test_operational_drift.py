from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import unittest

from grox.operational_drift import OperationalDriftAnalyzer, REGRESSION, STABLE, UNKNOWN
from tests._support import temp_vessel


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _trajectory(
    mission_id: str,
    *,
    crew_id: str = "test-architecture-specialist",
    success: bool = True,
    evidence_quality: float = 1.0,
    latency_ms: float = 10.0,
    cost_units: float = 1.0,
    tool_returncode: int = 0,
    required_capabilities: list[str] | None = None,
) -> dict:
    required = list(required_capabilities or ["repo_read"])
    events = [
        {
            "at": "2026-08-17T00:00:00+00:00",
            "category": "delegation",
            "kind": "mission_order",
            "source_id": f"ORD-{mission_id}",
            "payload": {"crew_id": crew_id, "required_capabilities": required, "mode": "inspect"},
            "source_table": "orders",
        },
        {
            "at": "2026-08-17T00:00:01+00:00",
            "category": "plan",
            "kind": "routing_decision",
            "source_id": "1",
            "payload": {"crew_id": crew_id, "source": "test"},
            "source_table": "evidence",
        },
        {
            "at": "2026-08-17T00:00:02+00:00",
            "category": "tool_action",
            "kind": "test_run",
            "source_id": "2",
            "payload": {"returncode": tool_returncode},
            "source_table": "evidence",
        },
        {
            "at": "2026-08-17T00:00:03+00:00",
            "category": "telemetry",
            "kind": "crew_performance",
            "source_id": f"ORD-{mission_id}",
            "payload": {
                "crew_id": crew_id,
                "latency_ms": latency_ms,
                "cost_units": cost_units,
                "evidence_quality": evidence_quality,
            },
            "source_table": "crew_performance",
        },
    ]
    trajectory = {
        "schema": "grox-trajectory-v1",
        "mission_id": mission_id,
        "mode": "inspect",
        "risk": "low",
        "status": "completed" if success else "exception",
        "directive_sha256": "0" * 64,
        "events": events,
        "source_counts": {
            "orders": 1,
            "evidence": 2,
            "plan_evidence": 1,
            "tool_evidence": 1,
            "verification_evidence": 0,
            "exception_evidence": 0,
            "exception_decisions": 0,
            "graph_nodes": 0,
            "graph_events": 0,
            "performance": 1,
        },
    }
    trajectory["trace_sha256"] = _sha(trajectory)
    return trajectory


class OperationalDriftTests(unittest.TestCase):
    def setUp(self):
        self.td, self.root, self.pilot = temp_vessel()
        self.evaluator = self.pilot.evaluation

    def tearDown(self):
        self.pilot.store.close()
        self.td.cleanup()

    def _case(self, name: str, **kwargs) -> str:
        trajectory = _trajectory(name, **kwargs)
        return self.evaluator.ledger.add_case(
            suite="operational-history",
            case_type="trajectory",
            case_id=f"EVC-{name}",
            source_mission_id=name,
            payload={"trajectory": trajectory},
            expected={"status": trajectory["status"], "trace_sha256": trajectory["trace_sha256"]},
            provenance={"source": "canonical_private_mission_state", "mission_id": name},
        )

    def _healthy_windows(self):
        ids = [self._case("healthy-a"), self._case("healthy-b")]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", ids)
        observed = analyzer.record_operational_window("observed", ids)
        return analyzer, baseline, observed

    def test_identical_digest_bound_operational_windows_are_stable(self):
        analyzer, baseline, observed = self._healthy_windows()
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, STABLE)
        self.assertTrue(finding.advisory_only)
        self.assertEqual(finding.baseline_window_sha256, finding.observed_window_sha256)
        self.assertEqual(finding.baseline_metrics["trace_complete_rate"], 1.0)

    def test_injected_operational_degradation_is_detected_without_rewriting_baseline(self):
        baseline_ids = [self._case("base-a"), self._case("base-b")]
        observed_ids = [
            self._case("bad-a", success=False, evidence_quality=0.5, latency_ms=50, tool_returncode=1),
            self._case("bad-b", success=False, evidence_quality=0.5, latency_ms=50, tool_returncode=1),
        ]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", baseline_ids)
        before = self.evaluator.ledger.run(baseline["run_id"])
        observed = analyzer.record_operational_window("observed", observed_ids)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        after = self.evaluator.ledger.run(baseline["run_id"])
        self.assertEqual(finding.status, REGRESSION)
        self.assertEqual(before["run_sha256"], after["run_sha256"])
        self.assertEqual(before["metrics"], after["metrics"])
        self.assertTrue(any("success_rate" in item for item in finding.regressions))
        self.assertTrue(any("tool_failure_rate" in item for item in finding.regressions))

    def test_critical_invariant_failure_cannot_hide_behind_good_averages(self):
        baseline_ids = [self._case("critical-base-a"), self._case("critical-base-b")]
        observed_ids = [
            self._case("critical-observed-a", required_capabilities=["repo_write"]),
            self._case("critical-observed-b"),
        ]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", baseline_ids)
        observed = analyzer.record_operational_window("observed", observed_ids)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, REGRESSION)
        self.assertIn("capability_violations", finding.critical_regressions)

    def test_baseline_with_critical_violation_is_unknown_not_normalized(self):
        baseline_ids = [
            self._case("invalid-base-a", required_capabilities=["repo_write"]),
            self._case("invalid-base-b"),
        ]
        observed_ids = [self._case("valid-observed-a"), self._case("valid-observed-b")]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", baseline_ids)
        observed = analyzer.record_operational_window("observed", observed_ids)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, UNKNOWN)
        self.assertTrue(any("baseline contains critical invariant failure" in x for x in finding.unknown_reasons))

    def test_missing_or_tampered_source_case_makes_comparison_unknown(self):
        analyzer, baseline, observed = self._healthy_windows()
        case_id = observed["config"]["case_ids"][0]
        self.evaluator.ledger.db.execute(
            "UPDATE evaluation_cases SET payload=? WHERE case_id=?",
            (json.dumps({"trajectory": {"tampered": True}}), case_id),
        )
        self.evaluator.ledger.db.commit()
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, UNKNOWN)
        self.assertTrue(any("source case unavailable or invalid" in x for x in finding.unknown_reasons))

    def test_stale_observed_window_is_unknown(self):
        ids = [self._case("fresh-a"), self._case("fresh-b")]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", ids)
        observed = analyzer.record_operational_window("observed", ids)
        created = datetime.fromisoformat(observed["created_at"])
        stale_analyzer = OperationalDriftAnalyzer(
            self.evaluator,
            max_observed_age_seconds=60,
            clock=lambda: created.astimezone(timezone.utc) + timedelta(seconds=61),
        )
        finding = stale_analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, UNKNOWN)
        self.assertTrue(any("is stale" in x for x in finding.unknown_reasons))

    def test_non_operational_case_cannot_enter_operational_window(self):
        trajectory = _trajectory("controlled")
        case_id = self.evaluator.ledger.add_case(
            suite="operational-history",
            case_type="trajectory",
            payload={"trajectory": trajectory},
            expected={"status": trajectory["status"], "trace_sha256": trajectory["trace_sha256"]},
            provenance={"source": "controlled_experiment"},
        )
        analyzer = OperationalDriftAnalyzer(self.evaluator, min_cases=1)
        with self.assertRaisesRegex(ValueError, "not attributable operational Mission history"):
            analyzer.record_operational_window("invalid", [case_id])

    def test_routing_concentration_is_first_class_signal(self):
        baseline_ids = [
            self._case("route-base-a", crew_id="test-architecture-specialist"),
            self._case("route-base-b", crew_id="backend-engineer"),
        ]
        observed_ids = [
            self._case("route-observed-a", crew_id="test-architecture-specialist"),
            self._case("route-observed-b", crew_id="test-architecture-specialist"),
        ]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", baseline_ids)
        observed = analyzer.record_operational_window("observed", observed_ids)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        self.assertEqual(finding.status, REGRESSION)
        self.assertTrue(any("routing_concentration_hhi" in x for x in finding.regressions))
        self.assertEqual(baseline["metrics"]["routing_concentration_hhi"], 0.5)
        self.assertEqual(observed["metrics"]["routing_concentration_hhi"], 1.0)

    def test_regression_proposal_is_evidence_bound_and_cannot_self_activate(self):
        baseline_ids = [self._case("proposal-base-a"), self._case("proposal-base-b")]
        observed_ids = [self._case("proposal-bad-a", success=False), self._case("proposal-bad-b", success=False)]
        analyzer = OperationalDriftAnalyzer(self.evaluator)
        baseline = analyzer.record_operational_window("baseline", baseline_ids)
        observed = analyzer.record_operational_window("observed", observed_ids)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        proposal_id = analyzer.create_advisory_proposal(finding)
        proposal = self.evaluator.ledger.proposal(proposal_id)
        self.assertEqual(proposal["status"], "proposed")
        self.assertEqual(proposal["proposed_change"]["activation"], "forbidden")
        self.assertEqual(proposal["evidence"]["baseline_run_sha256"], finding.baseline_run_sha256)
        with self.assertRaises(PermissionError):
            self.evaluator.ledger.activate(proposal_id)


if __name__ == "__main__":
    unittest.main()
