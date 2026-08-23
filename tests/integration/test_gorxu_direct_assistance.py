from __future__ import annotations

import unittest

from grox.contracts import MissionMode
from grox.pilot import PilotGorXu
from grox.reasoning import AssistantResponse
from grox.reasoning.contracts import MissionInterpretation
from tests._support import temp_vessel


class ConversationalReasoner:
    name = "fake-conversational-core"

    def respond(self, message):
        return AssistantResponse.from_mapping(
            {"commander_input": message, "response": "Restore verification proves a backup can be recovered."},
            expected_input=message,
        )

    def interpret(self, directive, *, roster):
        candidate = "test-architecture-specialist"
        raw = {
            "commander_intent": directive,
            "objective": "Inspect architecture without mutation",
            "ambiguous": False,
            "ambiguities": [],
            "assumptions": [],
            "information_needs": [],
            "candidate_crew_ids": [candidate],
            "options": [{"name": "inspect", "rationale": "Use governed inspection", "advantages": [], "risks": [], "crew_ids": [candidate]}],
            "recommended_option": "inspect",
            "confidence": 0.8,
            "proposed_mode": "inspect",
            "proposed_risk": "low",
        }
        return MissionInterpretation.from_mapping(raw, expected_intent=directive)

    def usage_snapshot(self):
        return None


class InterpretationOnlyReasoner(ConversationalReasoner):
    respond = None


class BrokenConversationalReasoner(ConversationalReasoner):
    def respond(self, message):
        raise ValueError("bad direct output")


class GorXuDirectAssistanceTests(unittest.TestCase):
    def test_direct_assistance_answers_without_creating_mission_or_delegating_crew(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=ConversationalReasoner())
            before_missions = pilot.store.recent_missions(1000)
            before_states = pilot.store.crew_states()
            result = pilot.ask("Why verify restores?")
            self.assertEqual(result["status"], "answered")
            self.assertIn("restore", result["response"].lower())
            self.assertFalse(result["mission_created"])
            self.assertFalse(result["crew_delegated"])
            self.assertFalse(result["authority_changed"])
            self.assertEqual(pilot.store.recent_missions(1000), before_missions)
            self.assertEqual(pilot.store.crew_states(), before_states)
        finally:
            td.cleanup()

    def test_interpretation_only_provider_remains_usable_for_existing_missions(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=InterpretationOnlyReasoner())
            direct = pilot.ask("hello")
            self.assertEqual(direct["status"], "cognition_unavailable")
            mission = pilot.command("Inspect architecture", mode=MissionMode.inspect)
            self.assertEqual(mission["status"], "completed")
        finally:
            td.cleanup()

    def test_direct_assistance_failure_is_explicit_and_creates_no_mission(self) -> None:
        td, root, _ = temp_vessel()
        try:
            pilot = PilotGorXu(root, reasoner=BrokenConversationalReasoner())
            result = pilot.ask("hello")
            self.assertEqual(result["status"], "cognition_unavailable")
            self.assertIsNone(result["response"])
            self.assertFalse(result["mission_created"])
            self.assertEqual(pilot.store.recent_missions(1000), [])
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
