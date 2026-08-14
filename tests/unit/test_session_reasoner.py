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

    def test_recoverable_reasoning_error_remains_domain_error(self):
        def unavailable(directive, roster):
            raise ReasoningError('provider unavailable')
        provider = SessionReasoningProvider(unavailable)
        with self.assertRaises(ReasoningError):
            provider.interpret('Check the boundary', roster=[])

    def test_unexpected_host_defect_is_not_normalized(self):
        def broken(directive, roster):
            raise RuntimeError('programming defect sentinel')
        provider = SessionReasoningProvider(broken)
        with self.assertRaisesRegex(RuntimeError, 'programming defect sentinel'):
            provider.interpret('Check the boundary', roster=[])


if __name__ == '__main__':
    unittest.main()

class SessionGraphReasonerTest(unittest.TestCase):
    def test_session_graph_responder_is_validated(self):
        directive='Coordinate a readiness graph'
        def interpret(directive,roster):
            return {
                'commander_intent':directive,'objective':'readiness','ambiguous':False,
                'ambiguities':[],'assumptions':[],'information_needs':[],
                'candidate_crew_ids':['backend-engineer'],
                'options':[{'name':'inspect','rationale':'inspect first','advantages':[],'risks':[],'crew_ids':['backend-engineer']}],
                'recommended_option':'inspect','confidence':0.8,'proposed_mode':'inspect','proposed_risk':'low'
            }
        def graph(directive,roster):
            return {
                'commander_intent':directive,'objective':'readiness graph',
                'nodes':[{'node_id':'inspect','objective':'inspect','mode':'inspect','dependencies':[],
                          'candidate_crew_ids':['backend-engineer'],'required_capabilities':['repo_read'],'scope':['.']}]
            }
        provider=SessionReasoningProvider(interpret,graph_responder=graph)
        plan=provider.plan_graph(directive,roster=[])
        self.assertEqual(plan.commander_intent,directive)
        self.assertEqual(plan.nodes[0].node_id,'inspect')
