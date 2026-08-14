import unittest
from tests._support import temp_vessel
class RecoveryTest(unittest.TestCase):
 def test_on_duty_resets_after_restart(self):
  td,root,p=temp_vessel()
  try:
   p.store.crew_on_duty('backend-engineer','M-X'); p2=type(p)(root); st={x['crew_id']:x for x in p2.store.crew_states()}; self.assertEqual(st['backend-engineer']['status'],'asleep')
  finally: td.cleanup()
