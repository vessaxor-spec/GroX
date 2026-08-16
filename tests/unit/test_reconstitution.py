from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import unittest
from unittest.mock import patch

from grox import cli
from grox.health import FAIL, PASS, UNKNOWN, WARN, HealthCheck, HealthReport
from grox.reconstitution import FAST, FULL, TARGETED, FULL_SURFACES, ReconstitutionPlanner


def check(check_id: str, domain: str, status: str = PASS, *, critical: bool = False, evidence: dict | None = None, detail: str = "ok") -> HealthCheck:
    return HealthCheck(check_id, domain, status, detail, critical, evidence)


def healthy_report(*, source_repository: str = PASS, operational_evidence: dict | None = None) -> HealthReport:
    checks = (
        check("command_integrity", "command", critical=True),
        check("operational_state", "operations", critical=True, evidence=operational_evidence or {"database_present": False}),
        check("persistence_readiness", "persistence"),
        check("authority_integrity", "authority", critical=True),
        check("memory_integrity", "memory", critical=True),
        check("source_version", "source", critical=True),
        check("source_repository", "source", source_repository, detail="source state"),
        check("verification_readiness", "verification", critical=True),
        check("isolation_readiness", "environment"),
        check("recovery_readiness", "recovery", critical=True),
    )
    return HealthReport("HEALTHY" if source_repository == PASS else "DEGRADED", checks, "2026-08-16T14:00:00+00:00", "/vessel")


class ReconstitutionPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = ReconstitutionPlanner()

    def test_clean_positive_health_selects_fast(self) -> None:
        plan = self.planner.plan(healthy_report())
        self.assertEqual(plan.mode, FAST)
        self.assertLess(plan.planned_surface_count, plan.full_surface_count)
        self.assertGreater(plan.structural_reduction_ratio, 0.0)
        self.assertEqual(plan.load_surfaces, ("command_doctrine", "source_integrity", "authority_policy", "cognitive_context"))

    def test_unknown_source_repository_selects_targeted_not_fast(self) -> None:
        plan = self.planner.plan(healthy_report(source_repository=UNKNOWN))
        self.assertEqual(plan.mode, TARGETED)
        self.assertIn("source_integrity", plan.load_surfaces)
        self.assertLess(plan.planned_surface_count, plan.full_surface_count)
        self.assertTrue(any("source_repository is UNKNOWN" in reason for reason in plan.reasons))

    def test_missing_source_repository_selects_targeted_not_fast(self) -> None:
        report = healthy_report()
        checks = tuple(item for item in report.checks if item.check_id != "source_repository")
        plan = self.planner.plan(HealthReport("DEGRADED", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, TARGETED)
        self.assertIn("source_integrity", plan.load_surfaces)
        self.assertTrue(any("source repository evidence missing" in reason for reason in plan.reasons))

    def test_noncritical_environment_warning_selects_targeted(self) -> None:
        report = healthy_report()
        checks = tuple(
            check_item if check_item.check_id != "isolation_readiness" else check("isolation_readiness", "environment", WARN, detail="workspace backend unavailable")
            for check_item in report.checks
        )
        plan = self.planner.plan(HealthReport("DEGRADED", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, TARGETED)
        self.assertIn("environment_capabilities", plan.load_surfaces)

    def test_fresh_host_forces_full_even_when_health_is_clean(self) -> None:
        plan = self.planner.plan(healthy_report(), fresh_host=True)
        self.assertEqual(plan.mode, FULL)
        self.assertEqual(plan.load_surfaces, FULL_SURFACES)
        self.assertTrue(any("fresh host" in reason for reason in plan.reasons))

    def test_source_change_forces_full(self) -> None:
        plan = self.planner.plan(healthy_report(), source_changed=True)
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("source changed" in reason for reason in plan.reasons))

    def test_critical_health_failure_forces_full(self) -> None:
        report = healthy_report()
        checks = tuple(
            item if item.check_id != "authority_integrity" else check("authority_integrity", "authority", FAIL, critical=True, detail="authority failure")
            for item in report.checks
        )
        plan = self.planner.plan(HealthReport("UNHEALTHY", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("critical health failure" in reason for reason in plan.reasons))

    def test_recovery_warning_forces_full(self) -> None:
        report = healthy_report()
        checks = tuple(
            item if item.check_id != "recovery_readiness" else check("recovery_readiness", "recovery", WARN, critical=True, detail="bounded resume required")
            for item in report.checks
        )
        plan = self.planner.plan(HealthReport("DEGRADED", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("recovery readiness is WARN" in reason for reason in plan.reasons))

    def test_interrupted_or_running_state_forces_full(self) -> None:
        report = healthy_report(
            operational_evidence={
                "database_present": True,
                "mission_status": {"running": 1, "interrupted": 1, "needs_pilot_decision": 1},
                "graph_node_status": {"running": 2},
            }
        )
        plan = self.planner.plan(report)
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("5 active/interrupted/unresolved" in reason for reason in plan.reasons))

    def test_dirty_source_forces_full(self) -> None:
        report = healthy_report(source_repository=WARN)
        plan = self.planner.plan(report)
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("source repository is dirty" in reason for reason in plan.reasons))

    def test_persistence_warning_forces_full(self) -> None:
        report = healthy_report()
        checks = tuple(
            item if item.check_id != "persistence_readiness" else check("persistence_readiness", "persistence", WARN, evidence={"runtime_rows": 7, "snapshot_present": False}, detail="runtime state lacks snapshot")
            for item in report.checks
        )
        plan = self.planner.plan(HealthReport("DEGRADED", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("persistence readiness is WARN" in reason for reason in plan.reasons))

    def test_missing_mandatory_evidence_defaults_full(self) -> None:
        report = healthy_report()
        checks = tuple(item for item in report.checks if item.check_id != "verification_readiness")
        plan = self.planner.plan(HealthReport("DEGRADED", checks, report.generated_at, report.vessel_root))
        self.assertEqual(plan.mode, FULL)
        self.assertTrue(any("mandatory health evidence not positively PASS" in reason for reason in plan.reasons))

    def test_fast_and_targeted_are_structurally_lighter_than_full(self) -> None:
        fast = self.planner.plan(healthy_report())
        targeted = self.planner.plan(healthy_report(source_repository=UNKNOWN))
        full = self.planner.plan(healthy_report(), fresh_host=True)
        self.assertLessEqual(fast.planned_surface_count, targeted.planned_surface_count)
        self.assertLess(targeted.planned_surface_count, full.planned_surface_count)
        self.assertEqual(full.structural_reduction_ratio, 0.0)

    def test_cli_plan_does_not_construct_pilot_or_restore_state(self) -> None:
        report = healthy_report()
        out = io.StringIO()
        with patch.object(cli, "pilot", side_effect=AssertionError("planner must not construct Pilot")), patch(
            "grox.cli.VesselHealth.collect", return_value=report
        ), redirect_stdout(out):
            cli.main(["reconstitution-plan", "--json"])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["mode"], FAST)
        self.assertLess(payload["planned_surface_count"], payload["full_surface_count"])

    def test_cli_fresh_host_flag_forces_full(self) -> None:
        report = healthy_report()
        out = io.StringIO()
        with patch("grox.cli.VesselHealth.collect", return_value=report), redirect_stdout(out):
            cli.main(["reconstitution-plan", "--json", "--fresh-host"])
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["mode"], FULL)
        self.assertEqual(payload["planned_surface_count"], payload["full_surface_count"])


if __name__ == "__main__":
    unittest.main()
