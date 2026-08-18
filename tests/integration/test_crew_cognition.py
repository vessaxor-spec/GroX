import json
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


class FailAfterReadProvider:
    name='fake-fail-after-read'

    def next_step(self, *, observations, **kwargs):
        if not observations:
            return {'action':'fs_read','path':'README.md'}
        raise CrewCognitionError('injected failure after governed read')


class MutatingInputProvider:
    name='fake-mutating-input'

    def __init__(self):
        self.snapshots=[]

    def next_step(self, *, order, craft_context, memory_context, observations):
        self.snapshots.append({
            'craft_headings':[item['heading'] for item in craft_context],
            'memory_count':len(memory_context),
            'observation_count':len(observations),
        })
        if not observations:
            craft_context.clear()
            memory_context.clear()
            observations.append({'action':'fake','content':'provider-local mutation'})
            order['scope'].clear()
            return {'action':'fs_read','path':'README.md'}
        return {'action':'finish','work_product':'Provider-local mutations did not alter executor-owned context.'}


class RepeatTestProvider:
    name='fake-repeat-test'

    def next_step(self, **kwargs):
        return {'action':'test_run'}


class OversizedWorkProductProvider:
    name='fake-oversized-output'

    def next_step(self, **kwargs):
        return {'action':'finish','work_product':'x'*5000}


class CountingProvider:
    name='fake-counting-provider'

    def __init__(self):
        self.calls=0

    def next_step(self, **kwargs):
        self.calls+=1
        return {'action':'finish','work_product':'should not be called'}


def _evidence_content(row):
    content=row['content']
    return json.loads(content) if isinstance(content,str) else content


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
            observation=_evidence_content(next(e for e in evidence if e['kind']=='crew_cognition_observation'))
            self.assertEqual(observation['action'],'fs_read')
            self.assertEqual(observation['path'],'README.md')
            self.assertIn('sha256',observation)
            self.assertNotIn('content',observation)
            cognition=_evidence_content(next(e for e in evidence if e['kind']=='crew_cognition'))
            self.assertEqual(cognition['provider'],provider.name)
            self.assertGreater(cognition['selected_chars'],0)
            self.assertIn('GroX Operational Binding',cognition['selected_headings'])
            self.assertGreaterEqual(cognition['observation_count'],1)
            self.assertEqual(cognition['test_run_count'],0)
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
            self.assertIn('escapes Vessel root',result['summary'])
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

    def test_governed_observation_remains_evidenced_when_provider_then_degrades(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=FailAfterReadProvider()
            result=p.command('Inspect README evidence',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'completed')
            mission=p.store.mission(result['mission_id'])
            kinds=[e['kind'] for e in mission['evidence']]
            self.assertIn('crew_cognition_observation',kinds)
            self.assertIn('crew_cognition_degraded',kinds)
            observation=_evidence_content(next(e for e in mission['evidence'] if e['kind']=='crew_cognition_observation'))
            self.assertEqual(observation['action'],'fs_read')
            self.assertEqual(observation['path'],'README.md')
        finally:
            td.cleanup()

    def test_provider_cannot_mutate_executor_owned_context_or_observation_history(self):
        td,root,p=temp_vessel()
        try:
            p.intelligence.remember(
                kind='semantic',scope='crew',crew_id='backend-engineer',memory_key='immutable-provider-view',
                content='README evidence remains attributable despite provider-local mutation attempts.',
                provenance={'mission_id':'M-immutable-view'},
            )
            provider=MutatingInputProvider()
            p.executor.cognition_provider=provider
            result=p.command('Inspect README evidence',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'completed')
            self.assertEqual(len(provider.snapshots),2)
            self.assertIn('GroX Operational Binding',provider.snapshots[0]['craft_headings'])
            self.assertIn('GroX Operational Binding',provider.snapshots[1]['craft_headings'])
            self.assertGreaterEqual(provider.snapshots[0]['memory_count'],1)
            self.assertEqual(provider.snapshots[1]['memory_count'],provider.snapshots[0]['memory_count'])
            self.assertEqual(provider.snapshots[0]['observation_count'],0)
            self.assertEqual(provider.snapshots[1]['observation_count'],1)
            mission=p.store.mission(result['mission_id'])
            cognition=_evidence_content(next(e for e in mission['evidence'] if e['kind']=='crew_cognition'))
            self.assertEqual(cognition['observation_count'],1)
        finally:
            td.cleanup()

    def test_cognitive_test_run_is_limited_to_one_per_tour(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=RepeatTestProvider()
            result=p.command('Inspect and test the Vessel',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'exception')
            self.assertEqual(result['exception']['type'],'crew_cognition_denied')
            self.assertIn('test_run budget exceeded: 1',result['summary'])
            mission=p.store.mission(result['mission_id'])
            observations=[_evidence_content(e) for e in mission['evidence'] if e['kind']=='crew_cognition_observation']
            self.assertEqual(len(observations),1)
            self.assertEqual(observations[0]['action'],'test_run')
            self.assertIn('crew_cognition_denied',{e['kind'] for e in mission['evidence']})
        finally:
            td.cleanup()

    def test_oversized_work_product_degrades_without_persisting_unbounded_output(self):
        td,root,p=temp_vessel()
        try:
            p.executor.cognition_provider=OversizedWorkProductProvider()
            result=p.command('Inspect the Vessel',mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(result['status'],'completed')
            self.assertNotIn('x'*256,result['summary'])
            mission=p.store.mission(result['mission_id'])
            kinds={e['kind'] for e in mission['evidence']}
            self.assertIn('crew_cognition_degraded',kinds)
            self.assertNotIn('crew_cognition',kinds)
            degraded=_evidence_content(next(e for e in mission['evidence'] if e['kind']=='crew_cognition_degraded'))
            self.assertIn('work product exceeds bounded size',degraded['error'])
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
            cognitive=[_evidence_content(e) for e in mission['evidence'] if e['kind']=='crew_cognition']
            self.assertGreaterEqual(len(cognitive),5)
            self.assertTrue(all(content['mode']=='read_only_inspect' for content in cognitive))
            verifier_orders=[o for o in mission['orders'] if o['mode']=='verify']
            self.assertEqual(len(verifier_orders),1)
            verifier_evidence=[e for e in mission['evidence'] if e['order_id']==verifier_orders[0]['order_id']]
            self.assertFalse(any(e['kind']=='crew_cognition' for e in verifier_evidence))
        finally:
            td.cleanup()


if __name__=='__main__':
    unittest.main()
