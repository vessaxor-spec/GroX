import unittest

from grox.graph import MissionGraphPlan


class MissionGraphContractTests(unittest.TestCase):
    def base(self):
        return {
            'commander_intent': 'Inspect the Vessel',
            'objective': 'Coordinate a bounded inspection',
            'budget': {'max_nodes': 8, 'max_parallel': 3, 'max_replans': 2},
            'nodes': [
                {'node_id':'a','objective':'Inspect architecture','mode':'inspect','dependencies':[],
                 'candidate_crew_ids':['systems-architect'],'required_capabilities':['repo_read'],'scope':['.']},
                {'node_id':'b','objective':'Verify architecture','mode':'verify','dependencies':['a'],
                 'candidate_crew_ids':['code-reviewer'],'required_capabilities':['repo_read','verify'],'scope':['.']},
            ],
        }

    def test_valid_dag_round_trip(self):
        raw=self.base()
        plan=MissionGraphPlan.from_mapping(raw,expected_intent='Inspect the Vessel')
        self.assertEqual([n.node_id for n in plan.nodes],['a','b'])
        self.assertEqual(plan.budget.max_parallel,3)
        self.assertEqual(plan.to_dict()['nodes'][1]['dependencies'],['a'])

    def test_commander_intent_must_be_preserved(self):
        raw=self.base(); raw['commander_intent']='changed'
        with self.assertRaises(ValueError):
            MissionGraphPlan.from_mapping(raw,expected_intent='Inspect the Vessel')

    def test_unknown_dependency_is_rejected(self):
        raw=self.base(); raw['nodes'][1]['dependencies']=['missing']
        with self.assertRaisesRegex(ValueError,'unknown dependencies'):
            MissionGraphPlan.from_mapping(raw,expected_intent='Inspect the Vessel')

    def test_cycle_is_rejected(self):
        raw=self.base(); raw['nodes'][0]['dependencies']=['b']
        with self.assertRaisesRegex(ValueError,'acyclic'):
            MissionGraphPlan.from_mapping(raw,expected_intent='Inspect the Vessel')

    def test_budget_is_enforced(self):
        raw=self.base(); raw['budget']['max_nodes']=1
        with self.assertRaisesRegex(ValueError,'exceeds node budget'):
            MissionGraphPlan.from_mapping(raw,expected_intent='Inspect the Vessel')
