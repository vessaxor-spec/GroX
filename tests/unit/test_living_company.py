import json
import unittest

from grox.contracts import RiskClass
from grox.pilot import PilotGorXu
from tests._support import temp_vessel


EXPERIENCED_BACKEND = {
    'crew_id':'backend-engineer-b','division':'engineering','title':'Backend Engineer B',
    'capabilities':['repo_read','repo_write','python','test_run'],
    'tags':['backend','api','python','service','repair','write','code'],
}


def experienced_vessel():
    td,root,_=temp_vessel()
    original=dict(EXPERIENCED_BACKEND)
    original['crew_id']='backend-engineer'; original['title']='Backend Engineer'
    (root/'configs/crew/dossiers/backend-engineer.json').write_text(json.dumps(original))
    (root/'configs/crew/dossiers/backend-engineer-b.json').write_text(json.dumps(EXPERIENCED_BACKEND))
    return td,root,PilotGorXu(root,reasoner=None)


class LivingCompanyUnitTests(unittest.TestCase):
    def test_memory_planes_persist_and_correction_preserves_history(self):
        td,root,p=experienced_vessel()
        try:
            semantic_old=p.intelligence.remember(
                kind='semantic',scope='crew',crew_id='backend-engineer',task_class='backend',
                memory_key='serializer-boundary',content='Backend serializer uses version one.',
                provenance={'mission_id':'M-1','order_id':'O-1'},confidence=0.8,
            )
            semantic_new=p.intelligence.remember(
                kind='semantic',scope='crew',crew_id='backend-engineer',task_class='backend',
                memory_key='serializer-boundary',content='Backend serializer uses version two.',
                provenance={'mission_id':'M-2','order_id':'O-2'},confidence=0.95,
            )
            p.intelligence.remember(
                kind='procedural',scope='crew',crew_id='backend-engineer',task_class='backend',
                memory_key='backend-review',content='Inspect backend tests before any repair.',
                provenance={'mission_id':'M-2'},
            )
            p.intelligence.remember(
                kind='vessel',scope='vessel',memory_key='verification-rule',
                content='Independent verification remains required when policy demands it.',
                provenance={'mission_id':'M-2'},
            )
            p.store.close()
            p2=PilotGorXu(root,reasoner=None)
            active=p2.store.memories_for('backend-engineer')
            self.assertEqual({m['kind'] for m in active},{'semantic','procedural','vessel'})
            self.assertTrue(any('version two' in m['content'] for m in active if m['kind']=='semantic'))
            history=p2.store.memories_for('backend-engineer',include_inactive=True)
            old=next(m for m in history if m['id']==semantic_old)
            new=next(m for m in history if m['id']==semantic_new)
            self.assertFalse(old['active'])
            self.assertTrue(new['active'])
            self.assertEqual(new['supersedes_id'],semantic_old)
            self.assertEqual(new['provenance']['order_id'],'O-2')
            with self.assertRaisesRegex(ValueError,'Vessel memory must use vessel scope'):
                p2.intelligence.remember(
                    kind='vessel',scope='crew',crew_id='backend-engineer',memory_key='bad-vessel',
                    content='This must not become Crew-scoped Vessel memory.',provenance={'mission_id':'M-bad'},
                )
            with self.assertRaisesRegex(ValueError,'memory provenance is required'):
                p2.intelligence.remember(
                    kind='semantic',scope='vessel',memory_key='unattributed',content='Unattributed memory.',
                )
        finally: td.cleanup()

    def test_load_is_a_routing_signal_but_capability_remains_a_hard_gate(self):
        td,root,p=experienced_vessel()
        try:
            baseline=p.intelligence.route('Inspect backend api service',['repo_read'])
            self.assertEqual(baseline.crew.crew_id,'backend-engineer')
            p.store.crew_on_duty('backend-engineer','M-load')
            loaded=p.intelligence.route('Inspect backend api service',['repo_read'])
            self.assertEqual(loaded.crew.crew_id,'backend-engineer-b')
            p.store.record_performance(
                crew_id='systems-architect',mission_id='M-best',order_id='O-best',task_class='backend',
                status='completed',evidence_quality=1.0,verified=True,latency_ms=1,cost_units=0,risk='high',
            )
            repair=p.intelligence.route('Repair backend api service',['repo_read','repo_write'],risk=RiskClass.high)
            self.assertNotEqual(repair.crew.crew_id,'systems-architect')
            self.assertTrue({'competence','reliability','evidence_quality','load','cost','latency','risk','experience','preference'} <= set(repair.components))
        finally: td.cleanup()

    def test_cost_and_latency_change_ranking_between_equally_reliable_crew(self):
        td,root,p=experienced_vessel()
        try:
            for crew,cost,latency in [('backend-engineer',8.0,4000),('backend-engineer-b',1.0,100)]:
                p.store.record_performance(
                    crew_id=crew,mission_id=f'M-{crew}',order_id=f'O-{crew}',task_class='backend',
                    status='completed',evidence_quality=1.0,verified=True,latency_ms=latency,cost_units=cost,risk='medium',
                )
            decision=p.intelligence.route('Inspect backend api service',['repo_read'],risk=RiskClass.medium)
            self.assertEqual(decision.crew.crew_id,'backend-engineer-b')
            self.assertLess(decision.components['cost'],0)
            self.assertLess(decision.components['latency'],0)
        finally: td.cleanup()

    def test_high_risk_routing_uses_verification_history(self):
        td,root,p=experienced_vessel()
        try:
            p.store.record_performance(
                crew_id='backend-engineer',mission_id='M-a',order_id='O-a',task_class='backend',
                status='completed',evidence_quality=1.0,verified=False,latency_ms=100,cost_units=1,risk='low',
            )
            p.store.record_performance(
                crew_id='backend-engineer-b',mission_id='M-b',order_id='O-b',task_class='backend',
                status='completed',evidence_quality=1.0,verified=True,latency_ms=100,cost_units=1,risk='low',
            )
            low=p.intelligence.route('Inspect backend api service',['repo_read'],risk=RiskClass.low)
            high=p.intelligence.route('Inspect backend api service',['repo_read'],risk=RiskClass.high)
            self.assertEqual(low.crew.crew_id,'backend-engineer')
            self.assertEqual(high.crew.crew_id,'backend-engineer-b')
            self.assertGreater(high.components['risk'],0)
        finally: td.cleanup()


if __name__ == '__main__':
    unittest.main()
