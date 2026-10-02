from __future__ import annotations

import hashlib
import unittest

from grox.context_objects import (
    BoundedContextReader,
    ContentAddressedContextObject,
    ContextBudgetExceeded,
    ContextReadBudget,
)


class ContentAddressedContextObjectTests(unittest.TestCase):
    def test_reference_is_deterministic_metadata_only(self):
        content = "Commander intent and bounded evidence"
        obj = ContentAddressedContextObject("mission-evidence", content)
        reference = obj.reference().to_dict()

        self.assertEqual(
            reference["sha256"],
            hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(reference["chars"], len(content))
        self.assertEqual(reference["label"], "mission-evidence")
        self.assertNotIn("content", reference)
        self.assertNotIn(content, repr(reference))
        self.assertEqual(
            set(reference),
            {"schema", "label", "sha256", "chars"},
        )

    def test_exact_slice_carries_source_identity_and_offsets(self):
        obj = ContentAddressedContextObject("evidence", "0123456789abcdef")
        budget = ContextReadBudget(max_operations=3, max_chars=20)
        view = obj.reader(budget).slice(3, 9)

        self.assertEqual(view.content, "345678")
        self.assertEqual(view.start, 3)
        self.assertEqual(view.end, 9)
        self.assertEqual(view.source_sha256, obj.sha256)
        self.assertEqual(view.to_dict()["chars"], 6)
        expected = hashlib.sha256(
            f"{obj.sha256}:3:9:".encode("utf-8") + b"345678"
        ).hexdigest()
        self.assertEqual(view.view_sha256, expected)
        self.assertEqual(budget.operations_used, 1)
        self.assertEqual(budget.chars_used, 6)

    def test_search_returns_bounded_read_only_views(self):
        content = "alpha evidence beta alpha final"
        obj = ContentAddressedContextObject("trace", content)
        budget = ContextReadBudget(max_operations=2, max_chars=100)
        views = obj.reader(budget).search("alpha", max_matches=2, window=2)

        self.assertEqual(len(views), 2)
        self.assertTrue(all(view.source_sha256 == obj.sha256 for view in views))
        self.assertTrue(all("alpha" in view.content for view in views))
        self.assertTrue(all(view.end - view.start <= len("alpha") + 4 for view in views))
        self.assertEqual(budget.operations_used, 1)
        self.assertEqual(
            budget.chars_used,
            sum(len(view.content) for view in views),
        )

    def test_shared_budget_fails_closed_without_partial_consumption(self):
        first = ContentAddressedContextObject("first", "abcdefghij")
        second = ContentAddressedContextObject("second", "klmnopqrst")
        budget = ContextReadBudget(max_operations=2, max_chars=8)

        first.reader(budget).slice(0, 4)
        before = budget.snapshot()

        with self.assertRaises(ContextBudgetExceeded):
            second.reader(budget).slice(0, 6)

        self.assertEqual(budget.snapshot(), before)

    def test_empty_search_still_consumes_one_operation_but_no_characters(self):
        obj = ContentAddressedContextObject("trace", "bounded evidence")
        budget = ContextReadBudget(max_operations=1, max_chars=10)
        views = obj.reader(budget).search("missing", max_matches=1, window=0)

        self.assertEqual(views, ())
        self.assertEqual(budget.operations_used, 1)
        self.assertEqual(budget.chars_used, 0)

    def test_malformed_bounds_and_search_inputs_fail_closed(self):
        obj = ContentAddressedContextObject("trace", "bounded evidence")
        budget = ContextReadBudget(max_operations=5, max_chars=100)
        reader = obj.reader(budget)

        invalid_calls = (
            lambda: reader.slice(-1, 2),
            lambda: reader.slice(2, 2),
            lambda: reader.slice(0, 1000),
            lambda: reader.search(""),
            lambda: reader.search("x" * (BoundedContextReader.max_pattern_chars + 1)),
            lambda: reader.search("evidence", max_matches=0),
            lambda: reader.search("evidence", window=-1),
        )
        for call in invalid_calls:
            with self.subTest(call=call):
                before = budget.snapshot()
                with self.assertRaises((TypeError, ValueError)):
                    call()
                self.assertEqual(budget.snapshot(), before)

    def test_primitive_exposes_no_authority_or_execution_state(self):
        obj = ContentAddressedContextObject("trace", "bounded evidence")
        budget = ContextReadBudget(max_operations=2, max_chars=20)
        reference = obj.reference().to_dict()
        view = obj.reader(budget).slice(0, 7).to_dict()

        forbidden = {
            "authorized",
            "ready",
            "qualified_fit",
            "selected",
            "observed",
            "mission_created",
            "authority_changed",
            "network_invoked",
            "provider_constructed",
        }
        self.assertTrue(forbidden.isdisjoint(reference))
        self.assertTrue(forbidden.isdisjoint(view))


if __name__ == "__main__":
    unittest.main()
