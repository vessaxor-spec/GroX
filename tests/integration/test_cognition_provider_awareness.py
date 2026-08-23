from __future__ import annotations

import unittest

from grox.cognition_awareness import CognitionProviderPolicy
from grox.crew_provider import bind_crew_cognition_provider
from grox.pilot import PilotGorXu
from grox.reasoning.session import SessionReasoningProvider
from grox.session_crew_cognition import SessionCrewCognitionProvider
from tests._support import temp_vessel


class PilotCognitionProviderAwarenessTests(unittest.TestCase):
    def test_pilot_inventory_is_fresh_across_crew_rebinding_without_mission_or_authority_change(self):
        td, root, bootstrap = temp_vessel()
        try:
            bootstrap.store.close()
            reasoner_calls = []
            reasoner = SessionReasoningProvider(
                lambda directive, roster: reasoner_calls.append((directive, roster)) or {},
                name="hosted-gorxu-awareness",
            )
            pilot = PilotGorXu(root, reasoner=reasoner)
            try:
                before = pilot.store.recent_missions()
                first = pilot.live_cognition_provider_inventory()
                self.assertEqual(len(first["resources"]), 1)
                self.assertEqual(first["resources"][0]["role"], "gorxu_reasoner")
                self.assertFalse(first["resources"][0]["authorized"])
                self.assertEqual(reasoner_calls, [])

                crew_calls = []
                crew_a = SessionCrewCognitionProvider(
                    lambda *args: crew_calls.append(args) or {"action": "finish", "work_product": "a"},
                    name="hosted-crew-a",
                )
                bind_crew_cognition_provider(pilot, crew_a)
                second = pilot.live_cognition_provider_inventory()
                self.assertEqual({item["role"] for item in second["resources"]}, {"gorxu_reasoner", "crew_cognition"})
                crew_a_id = next(item["resource_id"] for item in second["resources"] if item["role"] == "crew_cognition")

                crew_b = SessionCrewCognitionProvider(
                    lambda *args: {"action": "finish", "work_product": "b"},
                    name="hosted-crew-b",
                )
                bind_crew_cognition_provider(pilot, crew_b)
                third = pilot.live_cognition_provider_inventory(
                    policy=CognitionProviderPolicy(
                        authorized_ids=frozenset({crew_a_id}),
                        qualified_ids=frozenset({crew_a_id}),
                    )
                )
                crew_item = next(item for item in third["resources"] if item["role"] == "crew_cognition")
                self.assertNotEqual(crew_item["resource_id"], crew_a_id)
                self.assertFalse(crew_item["authorized"])
                self.assertFalse(crew_item["qualified_fit"])
                self.assertEqual(crew_calls, [])
                self.assertEqual(pilot.store.recent_missions(), before)
                self.assertFalse(third["authority_changed"])
                self.assertFalse(third["auto_selection"])
                self.assertFalse(third["auto_invocation"])
            finally:
                pilot.store.close()
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
