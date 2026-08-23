from __future__ import annotations

import unittest

from grox.reasoning.local_llama_cpp import (
    LocalLlamaCppReasoningProvider,
    _MISSION_INTERPRETATION_GBNF,
    _SYSTEM,
)


class LocalLlamaPromptBoundsTests(unittest.TestCase):
    def test_local_directory_keeps_every_valid_crew_identity_but_omits_expanded_metadata(self) -> None:
        roster = [
            {
                "crew_id": f"crew-{index:02d}",
                "division": "Engineering",
                "title": f"Crew Role {index}",
                "domains": ["very-long-domain-description-" * 20],
                "capabilities": ["must-remain-deterministic"],
                "verification": index % 2 == 0,
            }
            for index in range(82)
        ]

        compact = LocalLlamaCppReasoningProvider._local_directory(roster)

        self.assertEqual(len(compact), 82)
        self.assertEqual([row["crew_id"] for row in compact], [row["crew_id"] for row in roster])
        self.assertTrue(all(set(row) <= {"crew_id", "title", "division", "verification"} for row in compact))
        self.assertTrue(all("domains" not in row and "capabilities" not in row for row in compact))

    def test_local_directory_rejects_invalid_identity_rows_and_bounds_role_text(self) -> None:
        compact = LocalLlamaCppReasoningProvider._local_directory(
            [
                {"crew_id": "", "title": "invalid"},
                {"title": "missing identity"},
                {
                    "crew_id": "architect",
                    "title": "x" * 500,
                    "division": "Engineering",
                    "verification": True,
                },
            ]
        )

        self.assertEqual(len(compact), 1)
        self.assertEqual(compact[0]["crew_id"], "architect")
        self.assertEqual(len(compact[0]["title"]), 120)
        self.assertTrue(compact[0]["verification"])

    def test_local_generation_contract_is_bounded_without_bounding_commander_intent(self) -> None:
        self.assertIn('commander-string ::= "\\\"" char* "\\\"" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('short-string ::= "\\\"" char{0,120} "\\\"" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('nonempty-short-string ::= "\\\"" char{1,160} "\\\"" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('crew-id ::= "\\\"" char{1,120} "\\\"" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('bounded-list ::= "[" space (\"]\" space | short-string (\",\" space short-string)? \"]\" space)', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('crew-list ::= "[" space crew-id ("," space crew-id){0,2} "]" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn('options ::= "[" space option "]" space', _MISSION_INTERPRETATION_GBNF)
        self.assertIn("Return exactly one concise strategy option", _SYSTEM)
        self.assertIn("one to three Crew IDs", _SYSTEM)


if __name__ == "__main__":
    unittest.main()
