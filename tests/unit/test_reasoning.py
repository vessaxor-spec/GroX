import unittest
from grox.reasoning.contracts import MissionInterpretation

class ReasoningContractsTest(unittest.TestCase):
    def test_commander_intent_must_be_preserved(self):
        raw={
            'commander_intent':'changed','objective':'x','ambiguous':False,'ambiguities':[],
            'assumptions':[],'information_needs':[],'candidate_crew_ids':[],'options':[],
            'recommended_option':'','confidence':0.5,'proposed_mode':None,'proposed_risk':None,
        }
        with self.assertRaises(ValueError): MissionInterpretation.from_mapping(raw,expected_intent='original')

    def test_option_reference_is_validated(self):
        raw={
            'commander_intent':'x','objective':'x','ambiguous':False,'ambiguities':[],
            'assumptions':[],'information_needs':[],'candidate_crew_ids':[],
            'options':[{'name':'A','rationale':'brief rationale','advantages':[],'risks':[],'crew_ids':[]}],
            'recommended_option':'B','confidence':0.5,'proposed_mode':None,'proposed_risk':None,
        }
        with self.assertRaises(ValueError): MissionInterpretation.from_mapping(raw,expected_intent='x')
