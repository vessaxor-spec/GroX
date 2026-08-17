from pathlib import Path
from types import SimpleNamespace
import json
import unittest

from grox.contracts import RiskClass
from tests._support import temp_vessel


class IndependentVerifierRoutingPolicyTests(unittest.TestCase):
    def test_ordinary_routing_excludes_role_only_independent_verifier(self):
        td, _root, pilot = temp_vessel()
        try:
            decision = pilot.intelligence.route('verify evidence', ['repo_read'])
            self.assertEqual(decision.crew.crew_id, 'code-reviewer')
            self.assertTrue(decision.crew.verification)
        finally:
            td.cleanup()

    def test_verify_routing_still_selects_independent_verifier(self):
        td, _root, pilot = temp_vessel()
        try:
            decision = pilot.intelligence.route(
                'verify evidence', ['repo_read', 'verify'], verifier=True,
            )
            self.assertEqual(decision.crew.crew_id, 'independent-verifier')
        finally:
            td.cleanup()

    def test_cognitive_preference_cannot_force_verifier_into_ordinary_route(self):
        td, _root, pilot = temp_vessel()
        try:
            brief = SimpleNamespace(candidate_crew_ids=['independent-verifier'])
            crew, routing = pilot._select_crew(
                'verify evidence', ['repo_read'], None, brief, RiskClass.low,
            )
            self.assertEqual(crew.crew_id, 'code-reviewer')
            self.assertIsNotNone(routing)
        finally:
            td.cleanup()

    def test_explicit_assignment_preserves_separately_authorized_exception_path(self):
        td, _root, pilot = temp_vessel()
        try:
            crew, routing = pilot._select_crew(
                'bounded explicitly assigned evidence work',
                ['repo_read'],
                'independent-verifier',
                None,
                RiskClass.low,
            )
            self.assertEqual(crew.crew_id, 'independent-verifier')
            self.assertIsNone(routing)
        finally:
            td.cleanup()

    def test_legacy_roster_selector_uses_same_ordinary_routing_boundary(self):
        td, _root, pilot = temp_vessel()
        try:
            ordinary = pilot.roster.select('verify evidence', ['repo_read'])
            verification = pilot.roster.select(
                'verify evidence', ['repo_read', 'verify'], verifier=True,
            )
            self.assertEqual(ordinary.crew_id, 'code-reviewer')
            self.assertEqual(verification.crew_id, 'independent-verifier')
        finally:
            td.cleanup()

    def test_canonical_dossier_declares_independent_verifier_role_boundary(self):
        root = Path(__file__).resolve().parents[2]
        dossier = json.loads(
            (root / 'configs/crew/dossiers/independent-verifier.json').read_text()
        )
        self.assertIs(dossier['ordinary_routing'], False)
        self.assertIs(dossier['verification'], True)


if __name__ == '__main__':
    unittest.main()
