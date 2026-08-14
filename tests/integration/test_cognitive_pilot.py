import unittest
from tests._support import temp_vessel
from grox.pilot import PilotGorXu
from grox.contracts import MissionMode, RiskClass
from grox.reasoning.contracts import MissionInterpretation

class FakeReasoner:
    name='fake-cognitive-core'
    def __init__(self,candidate='backend-engineer',risk='low',mode='execute'):
        self.candidate=candidate; self.risk=risk; self.mode=mode
    def interpret(self,directive,*,roster):
        raw={
            'commander_intent':directive,
            'objective':'Evaluate serializer replacement consequences and implementation surface',
            'ambiguous':True,
            'ambiguities':['Target serializer is not named'],
            'assumptions':[],
            'information_needs':['Locate serializer boundary'],
            'candidate_crew_ids':[self.candidate],
            'options':[
                {'name':'inspect-first','rationale':'Inspect the implementation boundary before changing it','advantages':['lower mutation risk'],'risks':['adds one analysis step'],'crew_ids':[self.candidate]},
                {'name':'direct-change','rationale':'Change immediately only if scope is already proven','advantages':['faster'],'risks':['scope may be wrong'],'crew_ids':[self.candidate]},
            ],
            'recommended_option':'inspect-first','confidence':0.72,
            'proposed_mode':self.mode,'proposed_risk':self.risk,
        }
        return MissionInterpretation.from_mapping(raw,expected_intent=directive)

class BrokenReasoner:
    name='broken-core'
    def interpret(self,directive,*,roster): raise ValueError('bad cognitive output')

class CognitivePilotTest(unittest.TestCase):
    def test_reasoner_can_select_crew_without_keyword_route(self):
        td,root,_=temp_vessel()
        try:
            p=PilotGorXu(root,reasoner=FakeReasoner())
            directive='Consider the consequences of replacing the serializer boundary before we touch anything.'
            r=p.command(directive,mode=MissionMode.execute)
            self.assertEqual(r['crew'],'backend-engineer')
            self.assertEqual(r['cognition']['commander_intent'],directive)
            self.assertEqual(r['cognition']['recommended_option'],'inspect-first')
            mission=p.store.mission(r['mission_id'])
            self.assertTrue(any(e['kind']=='cognitive_plan' for e in mission['evidence']))
        finally: td.cleanup()

    def test_model_may_raise_but_not_lower_risk_floor(self):
        td,root,_=temp_vessel()
        try:
            p=PilotGorXu(root,reasoner=FakeReasoner(risk='low'))
            r=p.command('Update the repository record',mode=MissionMode.execute)
            self.assertEqual(r['risk'],'medium')
            p2=PilotGorXu(root,reasoner=FakeReasoner(risk='critical'))
            r2=p2.command('Inspect harmless metadata',mode=MissionMode.inspect)
            self.assertEqual(r2['risk'],'critical')
        finally: td.cleanup()

    def test_model_cannot_grant_repair_mode(self):
        td,root,_=temp_vessel()
        try:
            p=PilotGorXu(root,reasoner=FakeReasoner(mode='repair'))
            r=p.command('Understand the serializer boundary')
            self.assertEqual(r['mode'],'execute')
        finally: td.cleanup()

    def test_invalid_model_crew_falls_back_to_roster(self):
        td,root,_=temp_vessel()
        try:
            p=PilotGorXu(root,reasoner=FakeReasoner(candidate='nonexistent-crew'))
            r=p.command('Inspect architecture',mode=MissionMode.inspect)
            self.assertEqual(r['crew'],'systems-architect')
        finally: td.cleanup()

    def test_cognition_failure_degrades_without_widening_authority(self):
        td,root,_=temp_vessel()
        try:
            p=PilotGorXu(root,reasoner=BrokenReasoner())
            r=p.command('Inspect architecture',mode=MissionMode.inspect)
            self.assertEqual(r['status'],'completed')
            self.assertIsNotNone(r['cognition_error'])
            mission=p.store.mission(r['mission_id'])
            self.assertTrue(any(e['kind']=='cognition_degraded' for e in mission['evidence']))
        finally: td.cleanup()
