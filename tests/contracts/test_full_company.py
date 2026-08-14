import json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOS=ROOT/'configs/crew/dossiers'
MAN=ROOT/'configs/crew/company-manifest.json'

class FullCompanyTest(unittest.TestCase):
    def test_full_company_manifest_matches_dossiers(self):
        manifest=json.loads(MAN.read_text())
        files={p.stem for p in DOS.glob('*.json')}
        expected=set(manifest['roles'])|set(manifest['native_support_roles'])
        self.assertEqual(manifest['specialist_inspired_crew_count'],81)
        self.assertEqual(manifest['total_expected_dossiers'],82)
        self.assertEqual(files,expected)

    def test_no_orchestrator_is_recruited(self):
        ids={json.loads(p.read_text())['crew_id'] for p in DOS.glob('*.json')}
        self.assertNotIn('agents-orchestrator',ids)
        self.assertNotIn('orchestrator',ids)
        self.assertNotIn('gorxu',ids)
        self.assertNotIn('pilot',ids)

    def test_dossiers_are_native_and_complete(self):
        ids=[]
        for p in DOS.glob('*.json'):
            d=json.loads(p.read_text())
            ids.append(d['crew_id'])
            self.assertTrue(d['division'])
            self.assertTrue(d['title'])
            self.assertIn('repo_read',d['capabilities'])
            self.assertTrue(d.get('tags'))
            if d['crew_id']!='independent-verifier':
                self.assertIn(d.get('risk_posture'),{'low','medium','high','critical'})
                so=d.get('standing_orders',{})
                self.assertIn('GorXu',so.get('command',''))
                self.assertTrue(so.get('currency'))
        self.assertEqual(len(ids),len(set(ids)))

    def test_architect_replaces_bootstrap_overlap(self):
        files={p.stem for p in DOS.glob('*.json')}
        self.assertIn('architect',files)
        self.assertNotIn('systems-architect',files)

    def test_roster_catalogue_load_does_not_require_state_store(self):
        from grox.crew.roster import CrewRoster
        roster=CrewRoster(DOS)
        self.assertEqual(len(roster.all()),82)
        self.assertIsNone(roster.store)

class CompanyRoutingTest(unittest.TestCase):
    def test_domain_specialists_win_domain_routing(self):
        from grox.crew.roster import CrewRoster
        from grox.state import StateStore
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            roster=CrewRoster(DOS,StateStore(Path(td)/'s.sqlite3'))
            cases={
                'database reliability failure resilience':'database-reliability-engineer',
                'aerospace satellite systems constraints':'aerospace-satellite-engineer',
                'privacy engineering controls':'privacy-engineer',
                'fraud forensic investigation evidence':'fraud-forensic-investigation-specialist',
                'orchestration evaluation routing metrics':'orchestration-evaluation-analyst',
            }
            for objective,expected in cases.items():
                with self.subTest(objective=objective):
                    self.assertEqual(roster.select(objective,['repo_read']).crew_id,expected)
