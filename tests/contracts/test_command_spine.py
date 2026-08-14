import unittest, json
from pathlib import Path
from grox.crew.roster import CrewRoster
from grox.state import StateStore
class SpineTest(unittest.TestCase):
 def test_forbidden_orchestrator_cannot_be_crew(self):
  import tempfile
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=root/'d'; d.mkdir(); (d/'x.json').write_text(json.dumps({'crew_id':'orchestrator','division':'x','title':'x','capabilities':[],'tags':[]}))
   with self.assertRaises(ValueError): CrewRoster(d,StateStore(root/'s.sqlite3'))
 def test_canonical_command_spine_excludes_service_layers(self):
  root=Path(__file__).resolve().parents[2]
  instructions=(root/'AI_INSTRUCTIONS.md').read_text()
  cli=(root/'src/grox/cli.py').read_text()
  self.assertIn('Commander → Pilot GorXu → Divisions → Standing Crew',instructions)
  self.assertNotIn('Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew',instructions)
  self.assertIn('Commander -> Pilot GorXu -> Divisions -> Standing Crew',cli)

