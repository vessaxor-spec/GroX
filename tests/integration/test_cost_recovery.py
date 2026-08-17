from __future__ import annotations

import json
import unittest

from grox.pilot import PilotGorXu
from tests.integration.test_mission_graph import graph_vessel


class CrashOnCrewAfterCommit:
    def __init__(self, base, crew_id: str):
        self.base = base
        self.crew_id = crew_id
        self.crashed = False

    def execute(self, order):
        if order.assigned_crew == self.crew_id and not self.crashed:
            self.crashed = True
            raise SystemExit("injected crash after graph cost commitment")
        return self.base.execute(order)


class CostRecoveryTests(unittest.TestCase):
    def test_resume_reconstitutes_committed_cost_before_spending(self) -> None:
        td, root, pilot = graph_vessel()
        try:
            directive = "Resume a cost-bounded Mission without spending committed cost twice."
            plan = {
                "commander_intent": directive,
                "objective": "Prove committed cost remains charged across restart.",
                "budget": {"max_nodes": 5, "max_parallel": 1, "max_replans": 0, "max_cost_units": 2.0},
                "nodes": [
                    {
                        "node_id": "one", "objective": "Cost recovery step one", "mode": "inspect",
                        "dependencies": [], "candidate_crew_ids": ["test-architecture-specialist"],
                        "required_capabilities": ["repo_read"], "scope": ["."],
                        "budget": {"cost_units": 1.0},
                    },
                    {
                        "node_id": "two", "objective": "Cost recovery step two", "mode": "inspect",
                        "dependencies": ["one"], "candidate_crew_ids": ["researcher"],
                        "required_capabilities": ["repo_read"], "scope": ["."],
                        "budget": {"cost_units": 1.0},
                    },
                    {
                        "node_id": "three", "objective": "Cost recovery step three", "mode": "inspect",
                        "dependencies": ["two"], "candidate_crew_ids": ["data-analyst"],
                        "required_capabilities": ["repo_read"], "scope": ["."],
                        "budget": {"cost_units": 1.0},
                    },
                ],
            }
            pilot.executor = CrashOnCrewAfterCommit(pilot.executor, "researcher")
            with self.assertRaises(SystemExit):
                pilot.command_graph(directive, plan=plan, plan_source="stage1-cost-resume")

            mission_id = pilot.store.recent_missions(1)[0]["mission_id"]
            before = pilot.store.mission(mission_id)
            committed = [
                json.loads(event["content"])
                for event in before["graph_events"]
                if event["event_type"] == "cost_committed"
            ]
            self.assertEqual(sum(float(event["cost_units"]) for event in committed), 2.0)
            self.assertEqual(len(before["orders"]), 2)
            pilot.store.close()

            resumed_pilot = PilotGorXu(root, reasoner=None)
            resumed = resumed_pilot.resume_graph(mission_id)

            self.assertEqual(resumed["status"], "needs_pilot_decision")
            self.assertEqual(resumed["resume_count"], 1)
            self.assertEqual(resumed["synthesis"]["cost_units"], 2.0)
            self.assertEqual(resumed["synthesis"]["cost_budget"], 2.0)
            self.assertIn("two", resumed["synthesis"]["unresolved_nodes"])

            after = resumed_pilot.store.mission(mission_id)
            self.assertEqual(len(after["orders"]), 2, "resume must not create another paid Order after budget exhaustion")
            self.assertTrue(
                any(event["event_type"] == "cost_budget_exhausted" for event in after["graph_events"]),
                "resume must record the cost-budget stop",
            )
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
