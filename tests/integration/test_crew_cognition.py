import unittest

from grox.contracts import MissionMode
from grox.crew_cognition import CrewCognitionError
from tests._support import temp_vessel
from tests.integration.test_mission_graph import graph_vessel, qualification_plan


class ReadThenFinishProvider:
    name='fake-read-then-finish'

    def __init__(self):
        self.calls=[]

    def next_step(self, *, order, craft_context, memory_context, observations):
        self.calls.append({
            'order':order,
            'craft_context':craft_context,
            'memory_context':memory_context,
            'observations':observations,
        })
        if not observations:
            return {'action':'fs_read','path':'README.md'}
        return {'action':'finish','work_product':'README evidence inspected with bounded Crew craft.'}


class ScopeListThenFinishProvider:
    name='fake-scope-list'

    def next_step(self, *, order, craft_context, memory_context, observations):
        if not observations:
            return {'action':'fs_list','path':order['scope'][0]}
        return {'action':'finish','work_product':f"Inspected bounded scope for {order['assigned_crew']}."}


class WriteAttemptProvider:
    name='fake-write-attempt'

    def next_step(self, **kwargs):
        return {'action':'fs_write','path':'docs/forbidden.txt'}


class EscapeAttemptProvider:
    name='fake-scope-escape'

    def next_step(self, **kwargs):
        return {'action':'fs_read','path':'../outside.txt'}


class RecoverableFailureProvider:
    name='fake-recoverable-failure'

    def next_step(self, **kwargs):
        raise CrewCognitionError('injected recoverable provider failure')


class CountingProvider:
    name='fake-counting-provider'

    def __init__(self):
        self.calls=0

    def next_step(self, **kwargs):
        self.calls+=1
        return {'action':'finish','work_product':'should not be called'}


class CrewCognitionIntegrationTests(unittest.TestCase):
    def test_inspect_consumes_selective_craft_memory_and_governed_observation(self):
        td,root,p=temp_vessel()
        try:
            p.intelligence.remember(
                kind='semantic',scope='crew',crew_id='backend-engineer',memory_key='readme-review',
                content='README backend inspection evidence should be checked before conclusions.',
                provenance={'mission_id':'M-craft-memory'},
            )
            provider=ReadThenFinishProvider()
            p.executor.cognition_provider=provider
            result=p.command('Inspect README backend evidence',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'completed')
            self.assertIn('Crew cognition: README evidence inspected',result['summary'])
            self.assertGreaterEqual(len(provider.calls),2)
            first=provider.calls[0]
            headings={item['heading'] for item in first['craft_context']}
            self.assertIn('Purpose',headings)
            self.assertIn('Safety Boundaries',headings)
            self.assertIn('GroX Operational Binding',headings)
            self.assertTrue(any('README backend inspection evidence' in m['content'] for m in first['memory_context']))
            self.assertNotIn('parameters',first['order'])

            mission=p.store.mission(result['mission_id'])
            evidence=[e for e in mission['evidence'] if e['kind'] in {'crew_cognition','crew_cognition_observation'}]
            self.assertEqual(len([e for e in evidence if e['kind']=='crew_cognition']),1)
            observation=next(e for e in evidence if e['kind']=='crew_cognition_observation')
            self.assertEqual(observation['content']['action'],'fs_read')
            self.assertEqual(observation['content']['path'],'README.md')
            self.assertIn('sha256',observation['content'])
            self.assertNotIn('content',observation['content'])
            cognition=next(e for e in evidence if e['kind']=='crew_cognition')
            self.assertEqual(cognition['content']['provider'],provider.name)
            self.assertGreater(cognition['content']['selected_chars'],0)
            self.assertIn('GroX Operational Binding',cognition['content']['selected_headings'])
            self.assertGreaterEqual(cognition['content']['observation_count'],1)
        finally:
            td.cleanup()

    def test_mutating_cognition_request_fails_closed_without_fallback_or_mutation(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=WriteAttemptProvider()
            result=p.command('Inspect safely',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'exception')
            self.assertEqual(result['exception']['type'],'crew_cognition_denied')
            self.assertFalse((root/'docs/forbidden.txt').exists())
            mission=p.store.mission(result['mission_id'])
            kinds={e['kind'] for e in mission['evidence']}
            self.assertIn('crew_cognition_denied',kinds)
            self.assertNotIn('inventory',kinds)
        finally:
            td.cleanup()

    def test_read_request_outside_mission_scope_fails_closed(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=EscapeAttemptProvider()
            result=p.command('Inspect docs only',mode=MissionMode.inspect,crew_id='backend-engineer',scope='docs')
            self.assertEqual(result['status'],'exception')
            self.assertEqual(result['exception']['type'],'crew_cognition_denied')
            self.assertIn('scope',result['summary'])
        finally:
            td.cleanup()

    def test_recoverable_provider_failure_degrades_to_existing_deterministic_executor(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=RecoverableFailureProvider()
            result=p.command('Inspect the Vessel',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'completed')
            mission=p.store.mission(result['mission_id'])
            kinds={e['kind'] for e in mission['evidence']}
            self.assertIn('crew_cognition_degraded',kinds)
            self.assertIn('inventory',kinds)
            self.assertIn('test_run',kinds)
        finally:
            td.cleanup()

    def test_repair_never_enters_crew_cognition_seam(self):
        td,root,p=temp_vessel()
        try:
            provider=CountingProvider()
            p.executor.cognition_provider=provider
            result=p.command(
                'Repair the bounded test file',mode=MissionMode.repair,crew_id='backend-engineer',scope='docs/cognitive-repair.txt',
                parameters={'operation':'write_text','path':'docs/cognitive-repair.txt','content':'bounded repair\n'},
            )
            self.assertEqual(result['status'],'completed')
            self.assertEqual(provider.calls,0)
            self.assertEqual((root/'docs/cognitive-repair.txt').read_text(),'bounded repair\n')
        finally:
            td.cleanup()

    def test_mission_graph_inspect_nodes_share_same_bounded_cognition_seam(self):
        td,root,p=graph_vessel()
        try:
            p.executor.cognition_provider=ScopeListThenFinishProvider()
            directive='Inspect the Vessel across architecture, research, data, implementation, and security, then verify the combined result.'
            result=p.command_graph(directive,plan=qualification_plan(directive),plan_source='crew-cognition-controlled')
            self.assertEqual(result['status'],'completed')
            self.assertTrue(result['synthesis']['verification_passed'])
            mission=p.store.mission(result['mission_id'])
            cognitive=[e for e in mission['evidence'] if e['kind']=='crew_cognition']
            self.assertGreaterEqual(len(cognitive),5)
            self.assertTrue(all(e['content']['mode']=='read_only_inspect' for e in cognitive))
            verifier_orders=[o for o in mission['orders'] if o['mode']=='verify']
            self.assertEqual(len(verifier_orders),1)
            verifier_evidence=[e for e in mission['evidence'] if e['order_id']==verifier_orders[0]['order_id']]
            self.assertFalse(any(e['kind']=='crew_cognition' for e in verifier_evidence))
        finally:
            td.cleanup()


if __name__=='__main__':
    unittest.main()
