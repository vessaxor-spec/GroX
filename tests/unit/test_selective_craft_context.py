import unittest
from pathlib import Path

from grox.contracts import MissionMode, MissionOrder
from grox.craft_context import select_craft_context
from tests._support import temp_vessel


ROOT = Path(__file__).resolve().parents[2]


class SelectiveCraftContextTests(unittest.TestCase):
    def test_relevant_section_and_mandatory_boundaries_are_selected(self):
        card = '''---
name: security-reviewer
freshness_policy: live-verification-required
source_revision: abc123
---

## Identity

Security reviewer identity.

## Purpose

Review systems safely.

## Responsibilities

General review responsibilities.

## Database Protocol

Inspect query plans and schema migrations.

## Security Protocol

Trace authentication, authorization, secret handling, and trust boundaries.

## Safety Boundaries

Never widen authority or mutate without explicit Repair permission.

## GroX Operational Binding

Pilot GorXu remains sole operational orchestrator and Mission authority remains deterministic.
'''
        selected = select_craft_context(
            card,
            'Inspect authentication authorization and secret handling',
            max_sections=4,
            max_chars=1800,
        )
        headings = selected['selected_headings']
        self.assertIn('Purpose', headings)
        self.assertIn('Safety Boundaries', headings)
        self.assertIn('GroX Operational Binding', headings)
        self.assertIn('Security Protocol', headings)
        self.assertNotIn('Database Protocol', headings)
        self.assertLessEqual(selected['selected_chars'], 1800)
        self.assertFalse(selected['full_card_injected'])
        self.assertEqual(selected['freshness_policy'], 'live-verification-required')
        self.assertEqual(selected['source_revision'], 'abc123')
        by_heading={item['heading']:item['content'] for item in selected['selected_sections']}
        self.assertEqual(by_heading['Purpose'],'## Purpose\n\nReview systems safely.')
        self.assertEqual(by_heading['Safety Boundaries'],'## Safety Boundaries\n\nNever widen authority or mutate without explicit Repair permission.')
        self.assertEqual(by_heading['GroX Operational Binding'],'## GroX Operational Binding\n\nPilot GorXu remains sole operational orchestrator and Mission authority remains deterministic.')

    def test_mandatory_context_fails_closed_instead_of_being_truncated(self):
        card='''## Purpose\n\n%s\n\n## Safety Boundaries\n\n%s\n\n## GroX Operational Binding\n\n%s\n''' % ('p'*180,'s'*180,'g'*180)
        with self.assertRaisesRegex(ValueError,'complete mandatory safety context'):
            select_craft_context(card,'Inspect safely',max_sections=6,max_chars=256)

    def test_all_canonical_deep_cards_fit_complete_mandatory_context_at_default_budget(self):
        cards=sorted((ROOT/'configs/crew/specialists').glob('*.md'))
        self.assertEqual(len(cards),82)
        for path in cards:
            with self.subTest(card=path.name):
                selected=select_craft_context(path.read_text(encoding='utf-8'),'Inspect Vessel safety and operational readiness')
                headings=set(selected['selected_headings'])
                self.assertIn('Purpose',headings)
                self.assertIn('Safety Boundaries',headings)
                self.assertIn('GroX Operational Binding',headings)
                self.assertLessEqual(selected['selected_chars'],4500)

    def test_real_deep_card_selection_is_deterministic_and_bounded(self):
        card = (ROOT / 'configs/crew/specialists/code-reviewer.md').read_text(encoding='utf-8')
        objective = 'Review AI-authored code for dependency provenance security regressions and test quality'
        first = select_craft_context(card, objective, max_sections=6, max_chars=3200)
        second = select_craft_context(card, objective, max_sections=6, max_chars=3200)
        self.assertEqual(first, second)
        self.assertLessEqual(first['selected_chars'], 3200)
        self.assertLessEqual(len(first['selected_sections']), 6)
        self.assertLess(first['selected_chars'], first['card_chars'])
        self.assertFalse(first['full_card_injected'])
        self.assertTrue(first['truncated'])
        self.assertIn('AI-Authored Code Review Protocol', first['selected_headings'])
        self.assertIn('Safety Boundaries', first['selected_headings'])
        self.assertIn('GroX Operational Binding', first['selected_headings'])

    def test_living_company_injects_bounded_craft_alongside_memory_before_sealing(self):
        td, root, pilot = temp_vessel()
        try:
            order = MissionOrder.new(
                'MSN-craft-test',
                'Inspect backend code',
                'Inspect backend code',
                MissionMode.inspect,
                'backend-engineer',
                required_capabilities=['repo_read'],
                allowed_actions=['fs_list', 'fs_read'],
                forbidden_actions=['fs_write'],
                scope=['.'],
            )
            meta = pilot.intelligence.inject_order_context(order, order.objective)
            self.assertIn('_memory_context', order.parameters)
            self.assertIn('_craft_context', order.parameters)
            self.assertIn('_craft_context_meta', order.parameters)
            self.assertGreater(len(order.parameters['_craft_context']), 0)
            self.assertLessEqual(order.parameters['_craft_context_meta']['selected_chars'], pilot.intelligence.craft_chars)
            self.assertFalse(order.parameters['_craft_context_meta']['full_card_injected'])
            self.assertEqual(meta['craft']['craft_sha256'], order.parameters['_craft_context_meta']['craft_sha256'])
            pilot.store.save_order(order)
            self.assertTrue(order.sealed)
            with self.assertRaises(AttributeError):
                order.parameters = {'_craft_context': []}
        finally:
            td.cleanup()

    def test_non_inspect_order_keeps_memory_context_without_deep_craft_injection(self):
        td, root, pilot = temp_vessel()
        try:
            order = MissionOrder.new(
                'MSN-no-craft-verify',
                'Verify backend evidence',
                'Verify backend evidence',
                MissionMode.verify,
                'code-reviewer',
                required_capabilities=['repo_read','verify'],
                allowed_actions=['fs_list','fs_read','test_run'],
                forbidden_actions=['fs_write'],
                scope=['.'],
            )
            meta=pilot.intelligence.inject_order_context(order,order.objective)
            self.assertIn('_memory_context',order.parameters)
            self.assertNotIn('_craft_context',order.parameters)
            self.assertNotIn('_craft_context_meta',order.parameters)
            self.assertIsNone(meta['craft'])
        finally:
            td.cleanup()


if __name__ == '__main__':
    unittest.main()
