import json
import unittest

from grox.contracts import MissionMode, RiskClass, TourResult
from grox.pilot import PilotGorXu
from tests.integration.test_mission_graph import graph_vessel


def durable_plan(directive):
    return {
        'commander_intent': directive,
        'objective': 'Run a durable sequential readiness Mission and independently verify all committed evidence.',
        'budget': {'max_nodes': 12, 'max_parallel': 1, 'max_replans': 4},
        'nodes': [
            {'node_id':'architecture','objective':'Inspect architecture boundaries','mode':'inspect','dependencies':[],
             'candidate_crew_ids':['test-architecture-specialist'],'required_capabilities':['repo_read'],'scope':['.']},
            {'node_id':'research','objective':'Inspect research evidence','mode':'inspect','dependencies':['architecture'],
             'candidate_crew_ids':['researcher'],'required_capabilities':['repo_read'],'scope':['docs']},
            {'node_id':'analysis','objective':'Inspect configuration evidence','mode':'inspect','dependencies':['research'],
             'candidate_crew_ids':['data-analyst'],'required_capabilities':['repo_read'],'scope':['configs']},
            {'node_id':'security','objective':'Inspect authority evidence','mode':'inspect','dependencies':['analysis'],
             'candidate_crew_ids':['application-security-engineer'],'required_capabilities':['repo_read'],'scope':['.']},
            {'node_id':'verify','objective':'Independently verify all durable Mission evidence','mode':'verify',
             'dependencies':['architecture','research','analysis','security'],
             'candidate_crew_ids':['code-reviewer'],'required_capabilities':['repo_read','verify'],'scope':['.'],
             'parameters':{'run_tests':True}},
        ],
    }


class CrashOnCrew:
    def __init__(self, base, crew_id):
        self.base=base; self.crew_id=crew_id; self.crashed=False
    def execute(self, order):
        if order.assigned_crew==self.crew_id and not self.crashed and not order.parameters.get('_exception_consultation'):
            self.crashed=True
            raise SystemExit('injected process interruption')
        return self.base.execute(order)


class FailCrewsOnce:
    def __init__(self, base, crew_ids):
        self.base=base; self.remaining=set(crew_ids)
    def execute(self, order):
        if order.assigned_crew in self.remaining and not order.parameters.get('_exception_consultation'):
            self.remaining.remove(order.assigned_crew)
            return TourResult(order.order_id,order.assigned_crew,'exception','Injected ordinary A4 exception',[],
                              {'type':'crew_unavailable','message':'injected A4 recovery exception'})
        return self.base.execute(order)


class AlwaysBlocker:
    def __init__(self, base): self.base=base
    def execute(self, order):
        return TourResult(order.order_id,order.assigned_crew,'exception','Injected critical blocker',[],
                          {'type':'blocker','message':'critical qualification blocker'})


class DurableOperationsIntegrationTests(unittest.TestCase):
    def test_interrupted_graph_resumes_without_replaying_committed_work_and_handles_two_exceptions(self):
        td,root,p=graph_vessel()
        try:
            directive='Run a durable readiness Mission that survives interruption and ordinary Crew exceptions, then verify closure.'
            p.executor=CrashOnCrew(p.executor,'researcher')
            with self.assertRaises(SystemExit):
                p.command_graph(directive,plan=durable_plan(directive),plan_source='a4-crash-test')
            mission_id=p.store.recent_missions(1)[0]['mission_id']
            before=p.store.mission(mission_id)
            architecture_orders=[o for o in before['orders'] if o['crew_id']=='test-architecture-specialist']
            self.assertEqual(len(architecture_orders),1)
            self.assertEqual(next(n for n in before['graph_nodes'] if n['node_id']=='architecture')['status'],'completed')
            self.assertEqual(next(n for n in before['graph_nodes'] if n['node_id']=='research')['status'],'running')
            p.store.close()

            p2=PilotGorXu(root,reasoner=None)
            interrupted=p2.store.mission(mission_id)
            self.assertEqual(interrupted['mission']['status'],'interrupted')
            self.assertEqual(next(n for n in interrupted['graph_nodes'] if n['node_id']=='research')['status'],'interrupted')
            p2.executor=FailCrewsOnce(p2.executor,{'researcher','application-security-engineer'})
            resumed=p2.resume_graph(mission_id)
            self.assertEqual(resumed['status'],'completed')
            self.assertEqual(resumed['resume_count'],1)
            self.assertTrue(resumed['synthesis']['verification_passed'])
            self.assertEqual(resumed['synthesis']['replans'],2)

            mission=p2.store.mission(mission_id)
            self.assertEqual(len([o for o in mission['orders'] if o['crew_id']=='test-architecture-specialist']),1)
            self.assertEqual(len([e for e in mission['graph_events'] if e['event_type']=='pilot_replan']),2)
            self.assertTrue(any(e['event_type']=='mission_resumed' for e in mission['graph_events']))
            decisions=p2.durable.exception_decisions(mission_id)
            self.assertEqual(len(decisions),2)
            self.assertTrue(all(d['disposition']=='consult_then_replan' for d in decisions))
            self.assertTrue(all(d['consulted_crew'] and d['consultation_order_id'] for d in decisions))
            self.assertFalse(any(d['requires_commander'] for d in decisions))
            checkpoints=p2.durable.checkpoints(mission_id)
            self.assertTrue(any(c['phase']=='resume_interrupted_step' for c in checkpoints))
            self.assertTrue(any(c['phase']=='pilot_synthesis' and c['status']=='completed' for c in checkpoints))
            research_orders=[o for o in mission['orders'] if json.loads(o['payload'])['objective']=='Inspect research evidence']
            self.assertTrue(any(o['status']=='interrupted' for o in research_orders))
        finally: td.cleanup()

    def test_critical_exception_escalates_to_commander_without_automatic_consultation(self):
        td,root,p=graph_vessel()
        try:
            directive='Inspect a critical irreversible boundary.'
            plan={
                'commander_intent':directive,'objective':'Prove critical exception escalation boundary.',
                'nodes':[{'node_id':'inspect','objective':'Inspect critical boundary','mode':'inspect','dependencies':[],
                          'candidate_crew_ids':['test-architecture-specialist'],'required_capabilities':['repo_read'],'scope':['.']}],
            }
            p.executor=AlwaysBlocker(p.executor)
            result=p.command_graph(directive,plan=plan,risk=RiskClass.critical,plan_source='a4-critical-test')
            self.assertEqual(result['status'],'needs_commander_decision')
            decisions=p.durable.exception_decisions(result['mission_id'])
            self.assertEqual(len(decisions),1)
            self.assertTrue(decisions[0]['requires_commander'])
            self.assertEqual(decisions[0]['disposition'],'escalate_commander')
            self.assertIsNone(decisions[0]['consultation_order_id'])
        finally: td.cleanup()

    def test_cancelled_interrupted_graph_cannot_resume(self):
        td,root,p=graph_vessel()
        try:
            directive='Run a cancellable durable readiness Mission.'
            p.executor=CrashOnCrew(p.executor,'researcher')
            with self.assertRaises(SystemExit):
                p.command_graph(directive,plan=durable_plan(directive),plan_source='a4-cancel-test')
            mission_id=p.store.recent_missions(1)[0]['mission_id']
            p.store.close()
            p2=PilotGorXu(root,reasoner=None)
            cancelled=p2.cancel_graph(mission_id,'Commander cancelled the qualification branch')
            self.assertEqual(cancelled['status'],'cancelled')
            resumed=p2.resume_graph(mission_id)
            self.assertEqual(resumed['status'],'cancelled')
            mission=p2.store.mission(mission_id)
            self.assertEqual(mission['mission']['status'],'cancelled')
            self.assertTrue(any(e['event_type']=='mission_cancelled' for e in mission['graph_events']))
        finally: td.cleanup()

    def test_failed_repair_is_automatically_rolled_back(self):
        td,root,p=graph_vessel()
        try:
            target=root/'docs/a4-rollback.txt'
            (root/'tests/test_smoke.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_bad(self): self.fail("injected")\n')
            result=p.repair_write('docs/a4-rollback.txt','new content',crew_id='backend-engineer')
            self.assertEqual(result['status'],'exception')
            self.assertFalse(target.exists())
            history=p.durable.mutation_history(result['mission_id'])
            self.assertEqual(len(history),1)
            self.assertEqual(history[0]['status'],'rolled_back')
            evidence=p.store.mission(result['mission_id'])['evidence']
            rollback=[e for e in evidence if e['kind']=='mutation_rollback']
            self.assertEqual(len(rollback),1)
            self.assertEqual(json.loads(rollback[0]['content'])['status'],'rolled_back')
        finally: td.cleanup()


if __name__=='__main__':
    unittest.main()
