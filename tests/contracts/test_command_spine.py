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
