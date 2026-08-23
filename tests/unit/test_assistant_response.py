from __future__ import annotations

import unittest

from grox.reasoning.contracts import AssistantResponse


class AssistantResponseTests(unittest.TestCase):
    def test_direct_response_preserves_commander_input_and_is_bounded(self) -> None:
        turn = AssistantResponse.from_mapping(
            {"commander_input": "Why verify restores?", "response": "A restore test proves the backup is usable."},
            expected_input="Why verify restores?",
        )
        self.assertEqual(turn.commander_input, "Why verify restores?")
        self.assertIn("restore", turn.response.lower())

    def test_direct_response_rejects_commander_input_drift(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping(
                {"commander_input": "changed", "response": "answer"}, expected_input="original"
            )

    def test_direct_response_rejects_authority_shaped_extra_fields(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping(
                {"commander_input": "x", "response": "answer", "allowed_actions": ["fs_write"]},
                expected_input="x",
            )

    def test_direct_response_rejects_empty_or_oversized_text(self) -> None:
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping({"commander_input": "x", "response": "  "}, expected_input="x")
        with self.assertRaises(ValueError):
            AssistantResponse.from_mapping({"commander_input": "x", "response": "y" * 1201}, expected_input="x")


if __name__ == "__main__":
    unittest.main()
