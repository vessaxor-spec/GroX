from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grox.contracts import MissionMode, RiskClass
from grox.operational_drift import OperationalDriftAnalyzer, REGRESSION
from tests._support import temp_vessel


def run() -> dict:
    td, root, pilot = temp_vessel()
    try:
        smoke = root / "tests" / "test_smoke.py"
        baseline_cases = []
        baseline_missions = []
        for index in range(2):
            result = pilot.command(
                f"Inspect operational drift baseline {index}",
                mode=MissionMode.inspect,
                risk=RiskClass.low,
                crew_id="test-architecture-specialist",
            )
            if result["status"] != "completed":
                raise AssertionError(result)
            captured = pilot.evaluation.capture_mission(result["mission_id"])
            baseline_cases.append(captured["case_id"])
            baseline_missions.append(result["mission_id"])

        smoke.write_text(
            "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(False)\n",
            encoding="utf-8",
        )
        observed_cases = []
        observed_missions = []
        for index in range(2):
            result = pilot.command(
                f"Inspect operational drift degraded {index}",
                mode=MissionMode.inspect,
                risk=RiskClass.low,
                crew_id="test-architecture-specialist",
            )
            if result["status"] != "exception":
                raise AssertionError(result)
            captured = pilot.evaluation.capture_mission(result["mission_id"])
            observed_cases.append(captured["case_id"])
            observed_missions.append(result["mission_id"])

        smoke.write_text(
            "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n",
            encoding="utf-8",
        )

        analyzer = OperationalDriftAnalyzer(pilot.evaluation)
        baseline = analyzer.record_operational_window("operational-baseline", baseline_cases)
        baseline_before = pilot.evaluation.ledger.run(baseline["run_id"])
        observed = analyzer.record_operational_window("injected-degradation", observed_cases)
        finding = analyzer.compare(baseline["run_id"], observed["run_id"])
        baseline_after = pilot.evaluation.ledger.run(baseline["run_id"])

        if finding.status != REGRESSION:
            raise AssertionError(finding.to_dict())
        if baseline_before["run_sha256"] != baseline_after["run_sha256"]:
            raise AssertionError("baseline run changed during observation")
        if baseline_before["metrics"] != baseline_after["metrics"]:
            raise AssertionError("baseline metrics self-normalized")
        if finding.baseline_metrics["success_rate"] != 1.0:
            raise AssertionError(finding.baseline_metrics)
        if finding.observed_metrics["success_rate"] != 0.0:
            raise AssertionError(finding.observed_metrics)
        if finding.observed_metrics["tool_failure_rate"] <= finding.baseline_metrics["tool_failure_rate"]:
            raise AssertionError(finding.to_dict())

        proposal_id = analyzer.create_advisory_proposal(finding)
        proposal = pilot.evaluation.ledger.proposal(proposal_id)
        activation_blocked = False
        try:
            pilot.evaluation.ledger.activate(proposal_id)
        except PermissionError:
            activation_blocked = True
        if not activation_blocked:
            raise AssertionError("operational drift proposal self-activated")

        return {
            "schema": "grox-operational-drift-experiment-v1",
            "baseline_missions": baseline_missions,
            "observed_missions": observed_missions,
            "baseline_run_id": baseline["run_id"],
            "observed_run_id": observed["run_id"],
            "baseline_run_sha256": baseline["run_sha256"],
            "observed_run_sha256": observed["run_sha256"],
            "baseline_window_sha256": baseline["config"]["window_sha256"],
            "observed_window_sha256": observed["config"]["window_sha256"],
            "finding": finding.to_dict(),
            "proposal_id": proposal_id,
            "proposal_status": proposal["status"],
            "activation_blocked": activation_blocked,
            "baseline_unchanged": baseline_before["run_sha256"] == baseline_after["run_sha256"],
        }
    finally:
        pilot.store.close()
        td.cleanup()


if __name__ == "__main__":
    print("OPERATIONAL_DRIFT_EXPERIMENT_JSON=" + json.dumps(run(), sort_keys=True))
