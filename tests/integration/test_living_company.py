import json
import unittest

from grox.contracts import MissionMode, TourResult
from grox.pilot import PilotGorXu
from tests._support import add_synthetic_crew, temp_vessel


EXPERIENCED_BACKEND = {
    'crew_id':'backend-engineer-b','division':'engineering','title':'Backend Engineer B',
    'capabilities':['repo_read','repo_write','python','test_run'],
    'tags':['backend','api','python','service','repair','write','code'],
}


class FailCrewOnce:
    def __init__(self, base, crew_id):
        self.base=base; self.crew_id=crew_id; self.failed=False
    def execute(self, order):
        if order.assigned_crew==self.crew_id and not self.failed:
            self.failed=True
            return TourResult(order.order_id,order.assigned_crew,'exception','Injected A3 performance failure',[],{'type':'crew_unavailable'})
        return self.base.execute(order)


def experienced_vessel():
    td,root,_=temp_vessel()
    original=dict(EXPERIENCED_BACKEND)
    original['crew_id']='backend-engineer'; original['title']='Backend Engineer'
    add_synthetic_crew(root,original)
    add_synthetic_crew(root,EXPERIENCED_BACKEND)
    return td,root,PilotGorXu(root,reasoner=None)


class LivingCompanyIntegrationTests(unittest.TestCase):
    def test_repeated_missions_improve_routing_and_memory_context_stays_bounded(self):
        td,root,p=experienced_vessel()
        try:
            directive='Inspect backend api service readiness'
            baseline=p.intelligence.route(directive,['repo_read'])
            self.assertEqual(baseline.crew.crew_id,'backend-engineer')

            base_executor=p.executor
            p.executor=FailCrewOnce(base_executor,'backend-engineer')
            failed=p.command(directive,mode=MissionMode.inspect,crew_id='backend-engineer')
            self.assertEqual(failed['status'],'exception')
            p.executor=base_executor
            for _ in range(2):
                successful=p.command(directive,mode=MissionMode.inspect,crew_id='backend-engineer-b')
                self.assertEqual(successful['status'],'completed')

            for i in range(20):
                p.intelligence.remember(
                    kind='semantic',scope='vessel',memory_key=f'irrelevant-{i}',
                    content=f'Marketing campaign memory {i} for unrelated audience segmentation.',
                    provenance={'mission_id':'M-memory'},
                )
            for i in range(8):
                p.intelligence.remember(
                    kind='semantic',scope='crew',crew_id='backend-engineer-b',task_class='backend',
                    memory_key=f'backend-{i}',content=f'Backend api evidence item {i} applies to service readiness.',
                    provenance={'mission_id':'M-memory'},
                )
            p.intelligence.remember(
                kind='procedural',scope='crew',crew_id='backend-engineer-b',task_class='backend',
                memory_key='backend-procedure',content='Inspect backend api tests before proposing service changes.',
                provenance={'mission_id':'M-memory'},
            )
            p.intelligence.remember(
                kind='vessel',scope='vessel',task_class='backend',memory_key='backend-vessel-rule',
                content='Backend api changes retain independent verification when policy requires it.',
                provenance={'mission_id':'M-memory'},
            )

            adapted=p.command(directive,mode=MissionMode.inspect)
            self.assertEqual(adapted['status'],'completed')
            self.assertEqual(adapted['crew'],'backend-engineer-b')
            mission=p.store.mission(adapted['mission_id'])
            order=next(o for o in mission['orders'] if o['crew_id']=='backend-engineer-b')
            payload=json.loads(order['payload'])
            memory=payload['parameters']['_memory_context']
            self.assertLessEqual(len(memory),6)
            self.assertLessEqual(sum(len(m['content']) for m in memory),3000)
            self.assertTrue(any(m['kind']=='procedural' for m in memory))
            self.assertTrue(any(m['kind']=='vessel' for m in memory))
            self.assertFalse(any('Marketing campaign' in m['content'] for m in memory))
            evidence_kinds={e['kind'] for e in mission['evidence']}
            self.assertIn('routing_decision',evidence_kinds)
            self.assertIn('memory_selection',evidence_kinds)
            history=p.store.performance_history('backend-engineer-b','backend')
            self.assertGreaterEqual(len(history),3)
            self.assertEqual(p.intelligence.task_class(directive),'backend')
        finally: td.cleanup()

    def test_graph_nodes_share_experienced_routing_memory_and_performance(self):
        td,root,p=experienced_vessel()
        try:
            p.intelligence.remember(
                kind='procedural',scope='crew',crew_id='backend-engineer',task_class='backend',
                memory_key='graph-backend',content='Inspect backend evidence before graph synthesis.',
                provenance={'mission_id':'M-graph-memory'},
            )
            directive='Coordinate a backend api inspection and independent verification.'
            plan={
                'commander_intent':directive,'objective':'Inspect backend readiness and verify the evidence.',
                'nodes':[
                    {'node_id':'inspect','objective':'Inspect backend api readiness','mode':'inspect','dependencies':[],
                     'candidate_crew_ids':['backend-engineer'],'required_capabilities':['repo_read'],'scope':['.']},
                    {'node_id':'verify','objective':'Verify backend api evidence','mode':'verify','dependencies':['inspect'],
                     'candidate_crew_ids':['code-reviewer'],'required_capabilities':['repo_read','verify'],'scope':['.']},
                ],
            }
            result=p.command_graph(directive,plan=plan,plan_source='a3-integration-test')
            self.assertEqual(result['status'],'completed')
            self.assertTrue(result['synthesis']['verification_passed'])
            mission=p.store.mission(result['mission_id'])
            by_order={o['order_id']:o for o in mission['orders']}
            inspect_order=next(o for o in by_order.values() if o['crew_id']=='backend-engineer')
            payload=json.loads(inspect_order['payload'])
            self.assertTrue(any(m['kind']=='procedural' for m in payload['parameters']['_memory_context']))
            evidence=[e for e in mission['evidence'] if e['order_id']==inspect_order['order_id']]
            self.assertTrue(any(e['kind']=='routing_decision' for e in evidence))
            self.assertTrue(any(e['kind']=='memory_selection' for e in evidence))
            perf=p.store.performance_history('backend-engineer','backend')
            self.assertTrue(any(row['order_id']==inspect_order['order_id'] for row in perf))
            self.assertTrue(any(row['verified'] is True for row in perf if row['order_id']==inspect_order['order_id']))
        finally: td.cleanup()


if __name__ == '__main__':
    unittest.main()
