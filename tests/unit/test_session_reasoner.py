import unittest

from grox.reasoning import ReasoningError, SessionReasoningProvider


def valid_response(directive, roster):
    return {
        'commander_intent': directive,
        'objective': 'Assess the cognitive authority boundary',
        'ambiguous': False,
        'ambiguities': [],
        'assumptions': [],
        'information_needs': ['Inspect cognition and authority reconciliation'],
        'candidate_crew_ids': ['formal-methods-engineer'],
        'options': [
            {
                'name': 'prove-boundary-first',
                'rationale': 'Prove the authority invariant before expanding orchestration complexity.',
                'advantages': ['keeps cognition subordinate to deterministic authority'],
                'risks': ['delays A2 by one qualification step'],
                'crew_ids': ['formal-methods-engineer'],
            }
        ],
        'recommended_option': 'prove-boundary-first',
        'confidence': 0.94,
        'proposed_mode': 'inspect',
        'proposed_risk': 'high',
    }


class SessionReasonerTest(unittest.TestCase):
    def test_valid_hosted_reasoning_is_structurally_validated(self):
        provider = SessionReasoningProvider(valid_response)
        out = provider.interpret('Check the boundary', roster=[])
        self.assertEqual(out.commander_intent, 'Check the boundary')
        self.assertEqual(out.candidate_crew_ids, ['formal-methods-engineer'])
        self.assertEqual(provider.name, 'gpt-5.6-sol-session-high')

    def test_invalid_hosted_reasoning_is_rejected(self):
        provider = SessionReasoningProvider(lambda directive, roster: {'commander_intent': directive})
        with self.assertRaises(ReasoningError):
            provider.interpret('Check the boundary', roster=[])

    def test_host_failure_is_normalized(self):
        def broken(directive, roster):
            raise RuntimeError('host unavailable')
        provider = SessionReasoningProvider(broken)
        with self.assertRaises(ReasoningError):
            provider.interpret('Check the boundary', roster=[])


if __name__ == '__main__':
    unittest.main()
