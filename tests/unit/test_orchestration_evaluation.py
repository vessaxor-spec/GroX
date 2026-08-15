from __future__ import annotations

import json
import unittest

from grox.contracts import MissionMode, RiskClass
from grox.evaluation import DEFAULT_ROUTING_WEIGHTS
from grox.intelligence import weighted_routing_score
from tests._support import temp_vessel


COMPONENT_KEYS = tuple(DEFAULT_ROUTING_WEIGHTS)


def components(**overrides):
    base = {key: 0.0 for key in COMPONENT_KEYS}
    base.update(overrides)
    return base


def add_balanced_routing_suite(pilot, suite="a6-routing-qualification-v1"):
    # 12 high-risk cases where the current all-1.0 component aggregation overweights
    # surface competence versus the already-computed risk/reliability signal.
    # 12 low-risk cases protect efficiency/competence behavior from regression.
    for index in range(12):
        pilot.evaluation.add_routing_case(
            suite=suite,
            case_id=f"EVC-HIGH-{index:02d}",
            task_id=f"high-risk-{index:02d}",
            risk=RiskClass.high,
            topology="parallel" if index % 2 else "sequential",
            candidates=[
                {
                    "crew_id": "reliable-crew",
                    "eligible": True,
                    "components": components(competence=3.0, reliability=0.5, evidence_quality=0.5, risk=2.0),
                },
                {
                    "crew_id": "surface-crew",
                    "eligible": True,
                    "components": components(competence=8.0 + index * 0.02, reliability=0.5, evidence_quality=0.5, risk=-1.5),
                },
                {
                    "crew_id": "ineligible-rogue",
                    "eligible": False,
                    "components": components(competence=100.0, reliability=100.0, evidence_quality=100.0, risk=100.0),
                },
            ],
            expected_crew_id="reliable-crew",
            provenance={"source": "controlled_qualification", "purpose": "A6 paired routing gate"},
        )
    for index in range(12):
        pilot.evaluation.add_routing_case(
            suite=suite,
            case_id=f"EVC-LOW-{index:02d}",
            task_id=f"low-risk-{index:02d}",
            risk=RiskClass.low,
            topology="sequential" if index % 2 else "parallel",
            candidates=[
                {
                    "crew_id": "efficient-crew",
                    "eligible": True,
                    "components": components(competence=6.0, reliability=0.5, evidence_quality=0.5, cost=-0.25, latency=-0.25),
                },
                {
                    "crew_id": "slower-crew",
                    "eligible": True,
                    "components": components(competence=4.0, reliability=0.25, evidence_quality=0.25, cost=-0.5, latency=-0.5),
                },
                {
                    "crew_id": "ineligible-rogue",
                    "eligible": False,
                    "components": components(competence=100.0, reliability=100.0, evidence_quality=100.0),
                },
            ],
            expected_crew_id="efficient-crew",
            provenance={"source": "controlled_qualification", "purpose": "A6 balanced non-trigger regression"},
        )
    return suite


class OrchestrationEvaluationUnitTests(unittest.TestCase):

    def test_default_routing_weights_are_behavior_equivalent_and_immutable(self):
        sample = components(competence=2.0, reliability=1.5, evidence_quality=0.25, cost=-0.5, risk=3.0)
        self.assertEqual(weighted_routing_score(sample), sum(sample.values()))
        with self.assertRaises(TypeError):
            DEFAULT_ROUTING_WEIGHTS["risk"] = 9.0
        self.assertEqual(DEFAULT_ROUTING_WEIGHTS["risk"], 1.0)

    def test_evaluation_case_requires_attributable_source_provenance(self):
        td, root, p = temp_vessel()
        try:
            with self.assertRaisesRegex(ValueError, "provenance with source"):
                p.evaluation.ledger.add_case(
                    suite="bad-provenance", case_type="routing", payload={}, expected={}, provenance={"purpose": "missing source"}
                )
        finally:
            td.cleanup()

    def test_tampered_run_and_proposal_fail_digest_checks(self):
        td, root, p = temp_vessel()
        try:
            suite = add_balanced_routing_suite(p, "tamper-run-proposal")
            run = p.evaluation.run_routing_suite(suite, policy_name="baseline", weights=DEFAULT_ROUTING_WEIGHTS)
            p.store.db.execute("UPDATE evaluation_runs SET metrics='{}' WHERE run_id=?", (run["run_id"],))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "run digest mismatch"):
                p.evaluation.ledger.run(run["run_id"])

            proposal_id = p.propose_improvement(
                proposal_type="routing", target="controlled.routing", proposed_change={"risk": 2.0},
                rationale="Tamper contract", evidence={"source": "test", "run": "controlled"},
            )
            p.store.db.execute("UPDATE improvement_proposals SET rationale='tampered' WHERE proposal_id=?", (proposal_id,))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "proposal digest mismatch"):
                p.evaluation.ledger.proposal(proposal_id)
        finally:
            td.cleanup()
    def test_mission_trajectory_is_replayable_complete_and_privacy_minimized(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect the Vessel for evaluation trace completeness", risk=RiskClass.high)
            self.assertEqual(result["status"], "completed")
            captured = p.evaluate_mission(result["mission_id"], suite="trace-unit")
            trajectory = captured["trajectory"]
            self.assertTrue(captured["metrics"]["trace_complete"])
            self.assertEqual(captured["invariants"], [])
            self.assertGreaterEqual(captured["metrics"]["verification_events"], 1)
            categories = {event["category"] for event in trajectory["events"]}
            self.assertTrue({"plan", "delegation", "tool_action", "verification", "telemetry"}.issubset(categories))
            replay = p.evaluation.replay_trajectory(captured["case_id"])
            self.assertEqual(replay["trace_sha256"], trajectory["trace_sha256"])
            self.assertEqual(replay["metrics"], captured["metrics"])
            encoded = json.dumps(trajectory, sort_keys=True)
            self.assertNotIn('trace completeness', encoded)
            for event in trajectory['events']:
                self.assertNotIn('stdout', event['payload'])
                self.assertNotIn('stderr', event['payload'])
        finally:
            td.cleanup()

    def test_tampered_evaluation_case_fails_digest_check(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect trace tamper handling", risk=RiskClass.high)
            captured = p.evaluate_mission(result["mission_id"], suite="tamper")
            case_id = captured["case_id"]
            p.store.db.execute("UPDATE evaluation_cases SET payload='{}' WHERE case_id=?", (case_id,))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                p.evaluation.replay_trajectory(case_id)
        finally:
            td.cleanup()


    def test_pilot_level_exception_is_persisted_and_traced(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Controlled exception trace", crew_id="crew-that-does-not-exist")
            self.assertEqual(result["status"], "needs_pilot_decision")
            captured = p.evaluate_mission(result["mission_id"], suite="exception-trace")
            exception_events = [e for e in captured["trajectory"]["events"] if e["category"] == "exception"]
            self.assertTrue(any(e["kind"] == "routing_exception" for e in exception_events))
            self.assertGreaterEqual(captured["metrics"]["exceptions"], 1)
        finally:
            td.cleanup()

    def test_unexpected_defect_is_distinct_privacy_minimized_and_traced(self):
        class BrokenExecutor:
            def execute(self, order):
                raise RuntimeError("sensitive programming defect sentinel")

        td, root, p = temp_vessel()
        try:
            p.executor = BrokenExecutor()
            result = p.command("Inspect private defect trace", mode=MissionMode.inspect)
            self.assertEqual(result["status"], "unexpected_defect")
            captured = p.evaluate_mission(result["mission_id"], suite="unexpected-defect-trace")
            events = [e for e in captured["trajectory"]["events"] if e["category"] == "exception"]
            defect = next(e for e in events if e["kind"] == "unexpected_defect")
            self.assertEqual(defect["payload"]["exception_type"], "RuntimeError")
            encoded = json.dumps(defect, sort_keys=True)
            self.assertNotIn("sensitive programming defect sentinel", encoded)
            self.assertNotIn("Inspect private defect trace", encoded)
            self.assertIn("message_sha256", defect["payload"])
            self.assertIn("traceback_sha256", defect["payload"])
            self.assertEqual(defect["payload"]["context"]["operation"], "command")
            self.assertIn("directive_sha256", defect["payload"]["context"])
            self.assertGreaterEqual(captured["metrics"]["exceptions"], 1)
        finally:
            td.cleanup()

    def test_completed_trace_requires_minimum_operational_evidence_and_graph_repair_verification(self):
        td, root, p = temp_vessel()
        try:
            p.store.create_mission("MSN-A6-EMPTY-COMPLETED", "empty completed", "execute", "low")
            p.store.update_mission("MSN-A6-EMPTY-COMPLETED", "completed", "controlled")
            trajectory = p.evaluation.trajectory.build("MSN-A6-EMPTY-COMPLETED")
            metrics, invariants = p.evaluation.trajectory.metrics(trajectory)
            self.assertFalse(metrics["trace_complete"])
            self.assertTrue({
                "required_delegation_missing", "required_plan_missing",
                "required_tool_evidence_missing", "required_telemetry_missing",
            }.issubset(set(invariants)))

            graph_repair = {
                "schema": "grox-trajectory-v1", "mission_id": "MSN-A6-GRAPH-REPAIR",
                "mode": "graph", "risk": "low", "status": "completed", "directive_sha256": "0" * 64,
                "events": [{
                    "at": "2026-08-15T00:00:00+00:00", "category": "delegation", "kind": "mission_order",
                    "source_id": "ORD-1", "source_table": "orders",
                    "payload": {"crew_id": "canary", "mode": "repair", "required_capabilities": [], "allowed_actions": [], "risk_class": "low"},
                }],
                "source_counts": {
                    "orders": 1, "evidence": 0, "plan_evidence": 0, "tool_evidence": 0,
                    "verification_evidence": 0, "exception_evidence": 0, "exception_decisions": 0,
                    "graph_nodes": 0, "graph_events": 0, "performance": 0,
                },
            }
            _, graph_invariants = p.evaluation.trajectory.metrics(graph_repair)
            self.assertIn("required_verification_missing", graph_invariants)
        finally:
            td.cleanup()

    def test_evaluation_record_creation_timestamps_are_digest_bound(self):
        td, root, p = temp_vessel()
        try:
            result = p.command("Inspect timestamp binding", risk=RiskClass.high)
            captured = p.evaluate_mission(result["mission_id"], suite="timestamp-case")
            p.store.db.execute("UPDATE evaluation_cases SET created_at='2099-01-01T00:00:00+00:00' WHERE case_id=?", (captured["case_id"],))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "case digest mismatch"):
                p.evaluation.ledger.case(captured["case_id"])

            suite = add_balanced_routing_suite(p, "timestamp-run")
            run = p.evaluation.run_routing_suite(suite, policy_name="baseline", weights=DEFAULT_ROUTING_WEIGHTS)
            p.store.db.execute("UPDATE evaluation_runs SET created_at='2099-01-01T00:00:00+00:00' WHERE run_id=?", (run["run_id"],))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "run digest mismatch"):
                p.evaluation.ledger.run(run["run_id"])

            proposal_id = p.propose_improvement(
                proposal_type="routing", target="timestamp", proposed_change={"risk": 2.0},
                rationale="timestamp binding", evidence={"source": "test"},
            )
            p.store.db.execute("UPDATE improvement_proposals SET created_at='2099-01-01T00:00:00+00:00' WHERE proposal_id=?", (proposal_id,))
            p.store.db.commit()
            with self.assertRaisesRegex(ValueError, "proposal digest mismatch"):
                p.evaluation.ledger.proposal(proposal_id)
        finally:
            td.cleanup()

    def test_profile_search_controls_family_wise_false_positive_rate(self):
        td, root, p = temp_vessel()
        try:
            suite = "multiple-comparison-regression"
            for index in range(5):
                p.evaluation.add_routing_case(
                    suite=suite, case_id=f"EVC-MC-H-{index:02d}", task_id=f"high-{index}", risk=RiskClass.high,
                    topology="parallel" if index % 2 else "sequential",
                    candidates=[
                        {"crew_id": "reliable", "eligible": True, "components": components(competence=3.0, reliability=0.5, evidence_quality=0.5, risk=2.0)},
                        {"crew_id": "surface", "eligible": True, "components": components(competence=8.0, reliability=0.5, evidence_quality=0.5, risk=-1.5)},
                    ], expected_crew_id="reliable", provenance={"source": "regression_test"},
                )
            for index in range(15):
                p.evaluation.add_routing_case(
                    suite=suite, case_id=f"EVC-MC-L-{index:02d}", task_id=f"low-{index}", risk=RiskClass.low,
                    topology="sequential" if index % 2 else "parallel",
                    candidates=[
                        {"crew_id": "efficient", "eligible": True, "components": components(competence=6.0, reliability=0.5, evidence_quality=0.5, cost=-0.25, latency=-0.25)},
                        {"crew_id": "slower", "eligible": True, "components": components(competence=4.0, reliability=0.25, evidence_quality=0.25, cost=-0.5, latency=-0.5)},
                    ], expected_crew_id="efficient", provenance={"source": "regression_test"},
                )
            result = p.find_routing_improvement(suite)
            self.assertFalse(result["qualified"])
            self.assertTrue(all(c["alpha"] == 0.0125 for c in result["comparisons"]))
            self.assertTrue(any(c["p_value"] == 0.03125 for c in result["comparisons"]))
        finally:
            td.cleanup()

    def test_resumes_are_not_counted_as_retries(self):
        td, root, p = temp_vessel()
        try:
            trajectory = {
                "schema": "grox-trajectory-v1", "mission_id": "MSN-A6-RESUME", "mode": "graph", "risk": "low",
                "status": "needs_pilot_decision", "directive_sha256": "0" * 64,
                "events": [{
                    "at": "2026-08-15T00:00:00+00:00", "category": "control", "kind": "graph_run",
                    "source_id": "MSN-A6-RESUME", "source_table": "graph_runs",
                    "payload": {"resume_count": 2, "cancelled": False},
                }],
                "source_counts": {
                    "orders": 0, "evidence": 0, "plan_evidence": 0, "tool_evidence": 0,
                    "verification_evidence": 0, "exception_evidence": 0, "exception_decisions": 0,
                    "graph_nodes": 0, "graph_events": 0, "performance": 0,
                },
            }
            metrics, _ = p.evaluation.trajectory.metrics(trajectory)
            self.assertEqual(metrics["retries"], 0)
            self.assertEqual(metrics["resumes"], 2)
        finally:
            td.cleanup()

    def test_high_risk_trace_without_verification_is_flagged(self):
        td, root, p = temp_vessel()
        try:
            p.store.create_mission("MSN-A6-NOVERIFY", "High-risk controlled trace", "execute", "high")
            p.store.update_mission("MSN-A6-NOVERIFY", "completed", "controlled")
            trajectory = p.evaluation.trajectory.build("MSN-A6-NOVERIFY")
            metrics, invariants = p.evaluation.trajectory.metrics(trajectory)
            self.assertFalse(metrics["trace_complete"])
            self.assertIn("required_verification_missing", invariants)
        finally:
            td.cleanup()

    def test_statistical_gate_accepts_risk_guarded_candidate_without_invariant_regression(self):
        td, root, p = temp_vessel()
        try:
            suite = add_balanced_routing_suite(p)
            baseline = p.evaluation.run_routing_suite(suite, policy_name="baseline", weights=DEFAULT_ROUTING_WEIGHTS)
            candidate = p.evaluation.run_routing_suite(suite, policy_name="risk-guarded", weights={"risk": 3.0})
            comparison = p.evaluation.compare_routing_runs(baseline["run_id"], candidate["run_id"])
            self.assertEqual(comparison.cases, 24)
            self.assertEqual(comparison.baseline_passes, 12)
            self.assertEqual(comparison.candidate_passes, 24)
            self.assertEqual(comparison.wins, 12)
            self.assertEqual(comparison.losses, 0)
            self.assertLessEqual(comparison.p_value, 0.05)
            self.assertEqual(comparison.invariant_regressions, 0)
            self.assertTrue(comparison.statistically_better)
        finally:
            td.cleanup()

    def test_ineligible_candidate_is_never_selected_even_with_dominant_score(self):
        td, root, p = temp_vessel()
        try:
            suite = "authority-filter"
            p.evaluation.add_routing_case(
                suite=suite, task_id="authority-case", risk=RiskClass.critical, topology="sequential",
                candidates=[
                    {"crew_id": "eligible", "eligible": True, "components": components(competence=1, risk=1)},
                    {"crew_id": "rogue", "eligible": False, "components": components(competence=100, risk=100)},
                ],
                expected_crew_id="eligible",
                provenance={"source": "adversarial_test"},
            )
            run = p.evaluation.run_routing_suite(suite, policy_name="adversarial", weights={"risk": 10.0})
            self.assertEqual(run["case_results"][0]["selected_crew_id"], "eligible")
            self.assertEqual(run["invariants"]["failures"], 0)
        finally:
            td.cleanup()

    def test_mutated_routing_candidate_that_does_not_improve_fails_gate(self):
        td, root, p = temp_vessel()
        try:
            suite = add_balanced_routing_suite(p, "mutation-gate")
            baseline = p.evaluation.run_routing_suite(suite, policy_name="baseline", weights=DEFAULT_ROUTING_WEIGHTS)
            mutated = p.evaluation.run_routing_suite(suite, policy_name="risk-blind", weights={"risk": 0.0})
            comparison = p.evaluation.compare_routing_runs(baseline["run_id"], mutated["run_id"])
            self.assertFalse(comparison.statistically_better)
        finally:
            td.cleanup()

    def test_evidence_driven_search_files_proposal_but_does_not_activate_it(self):
        td, root, p = temp_vessel()
        try:
            suite = add_balanced_routing_suite(p, "proposal-search")
            result = p.find_routing_improvement(suite)
            self.assertTrue(result["qualified"])
            proposal = p.evaluation.ledger.proposal(result["proposal_id"])
            self.assertEqual(proposal["status"], "proposed")
            self.assertEqual(proposal["proposal_type"], "routing")
            self.assertTrue(proposal["evidence"]["comparison"]["statistically_better"])
            with self.assertRaisesRegex(PermissionError, "separate GroX authority path"):
                p.activate_improvement(result["proposal_id"])
            self.assertEqual(p.evaluation.ledger.proposal(result["proposal_id"])["status"], "proposed")
        finally:
            td.cleanup()

    def test_all_a6_proposal_classes_are_advisory_and_evidence_backed(self):
        td, root, p = temp_vessel()
        try:
            for proposal_type in ("routing", "prompt", "skill", "memory", "workflow"):
                proposal_id = p.propose_improvement(
                    proposal_type=proposal_type,
                    target=f"controlled.{proposal_type}",
                    proposed_change={"change": "candidate-only"},
                    rationale="Controlled A6 proposal contract test",
                    evidence={"source": "test", "metric": 1.0},
                )
                proposal = p.evaluation.ledger.proposal(proposal_id)
                self.assertEqual(proposal["status"], "proposed")
                with self.assertRaises(PermissionError):
                    p.activate_improvement(proposal_id)
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
