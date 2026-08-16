from __future__ import annotations

import unittest

from grox.context_heat import COLD, HOT, WARM, ContextHeatPolicy, ContextItem


class ContextHeatPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = ContextHeatPolicy()

    def test_active_commander_intent_and_authority_are_hot_verbatim(self) -> None:
        items = [
            ContextItem("intent", "commander_intent", "OBJECTIVE: preserve Commander intent exactly", "MSN-1", active=True, required_facts=("OBJECTIVE: preserve Commander intent exactly",)),
            ContextItem("authority", "authority", "AUTHORITY: inspect only; fs_write forbidden", "ORD-1", active=True, required_facts=("AUTHORITY: inspect only; fs_write forbidden",)),
        ]
        pack = self.policy.pack(items)
        self.assertEqual([item.heat for item in pack.items], [HOT, HOT])
        self.assertEqual(pack.items[0].text, items[0].content)
        self.assertEqual(pack.items[1].text, items[1].content)

    def test_relevant_warm_item_uses_only_attributable_summary(self) -> None:
        item = ContextItem(
            "finding",
            "crew_finding",
            "Long raw finding with implementation details and repeated diagnostic material that is no longer required for the active decision.",
            "EVID-7",
            summary="Finding: gateway stayed fail-closed.",
            relevant=True,
        )
        pack = self.policy.pack([item])
        self.assertEqual(pack.items[0].heat, WARM)
        self.assertTrue(pack.items[0].compressed)
        self.assertEqual(pack.items[0].text, "Finding: gateway stayed fail-closed.")
        self.assertEqual(pack.items[0].provenance, "EVID-7")

    def test_warm_without_summary_keeps_raw_text(self) -> None:
        item = ContextItem("decision", "decision", "Decision remains relevant and has no safe precomputed summary.", "DEC-1", relevant=True)
        pack = self.policy.pack([item])
        self.assertEqual(pack.items[0].heat, WARM)
        self.assertFalse(pack.items[0].compressed)
        self.assertEqual(pack.items[0].text, item.content)

    def test_cold_rederivable_material_is_omitted(self) -> None:
        item = ContextItem("raw", "raw_tool_output", "old re-derivable verbose output " * 20, "TOOL-OLD")
        self.assertEqual(self.policy.classify(item), COLD)
        pack = self.policy.pack([item])
        self.assertEqual(pack.items, ())
        self.assertEqual(pack.omitted_ids, ("raw",))

    def test_old_critical_safety_fact_can_never_be_cooled_by_age(self) -> None:
        item = ContextItem(
            "old-safety",
            "relevant_history",
            "SAFETY: never restore an unrelated-source snapshot",
            "SHIPLOG-OLD",
            summary="old history",
            relevant=False,
            critical=True,
            required_facts=("SAFETY: never restore an unrelated-source snapshot",),
        )
        self.assertEqual(self.policy.classify(item), HOT)
        pack = self.policy.pack([item])
        self.assertEqual(pack.items[0].text, item.content)
        self.assertFalse(pack.items[0].compressed)

    def test_unresolved_contradiction_remains_hot(self) -> None:
        item = ContextItem(
            "contradiction",
            "unresolved_contradiction",
            "CONTRADICTION: source says Repair; Commander Order says Inspect only",
            "EVID-CONFLICT",
            active=True,
            required_facts=("CONTRADICTION: source says Repair; Commander Order says Inspect only",),
        )
        self.assertEqual(self.policy.classify(item), HOT)

    def test_preservation_audit_detects_missing_required_fact(self) -> None:
        item = ContextItem("cold-critical-fact", "raw_tool_output", "REQUIRED-FACT-42", "RAW-1")
        pack = self.policy.pack([item])
        audit = self.policy.audit_preservation(pack, ["REQUIRED-FACT-42"])
        self.assertFalse(audit.passed)
        self.assertEqual(audit.missing_required_facts, ("REQUIRED-FACT-42",))

    def test_representative_pack_reduces_context_without_losing_required_facts(self) -> None:
        required = (
            "INTENT: audit GroX without widening authority",
            "CONSTRAINT: Repair is forbidden",
            "STATE: node verify-2 pending",
            "CONTRADICTION: evidence A conflicts with evidence B",
            "SAFETY: unrelated snapshot restore must fail closed",
            "NEXT: independently verify synthesis",
        )
        items = [
            ContextItem("intent", "commander_intent", required[0], "MSN-CTX", active=True),
            ContextItem("constraint", "commander_constraint", required[1], "MSN-CTX", active=True),
            ContextItem("state", "active_graph_state", required[2], "GR-CTX", active=True),
            ContextItem("conflict", "unresolved_contradiction", required[3], "EVID-A+B", active=True),
            ContextItem("old-safety", "relevant_history", required[4], "SHIPLOG-12", critical=True),
            ContextItem("next", "next_action", required[5], "GR-CTX", active=True),
            ContextItem(
                "finding",
                "crew_finding",
                "Detailed Crew finding " + ("diagnostic evidence and repeated implementation detail " * 20),
                "EVID-FINDING",
                summary="Finding: isolation backend stayed fail-closed.",
                relevant=True,
            ),
            ContextItem(
                "decision",
                "decision",
                "Historic but still relevant decision " + ("background rationale " * 20),
                "SHIPLOG-DEC",
                summary="Decision: keep operational state private.",
                relevant=True,
            ),
            ContextItem("raw-old", "raw_tool_output", "re-derivable raw output " * 80, "TOOL-OLD"),
            ContextItem("superseded", "superseded_discussion", "superseded discussion " * 50, "CHAT-OLD"),
        ]
        pack = self.policy.pack(items)
        audit = self.policy.audit_preservation(pack, required)
        self.assertTrue(audit.passed, audit)
        self.assertGreater(pack.reduction_ratio, 0.70)
        self.assertIn("old-safety", pack.retained_ids)
        self.assertIn("raw-old", pack.omitted_ids)
        self.assertIn("superseded", pack.omitted_ids)


if __name__ == "__main__":
    unittest.main()
