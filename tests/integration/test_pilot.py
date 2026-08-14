import unittest
from tests._support import temp_vessel
from grox.contracts import MissionMode, RiskClass
class PilotTest(unittest.TestCase):
 def test_inspection_routes_and_completes(self):
  td,root,p=temp_vessel()
  try:
   r=p.command('Inspect architecture and report',mode=MissionMode.inspect)
   self.assertEqual(r['status'],'completed'); self.assertEqual(r['crew'],'systems-architect')
  finally: td.cleanup()
 def test_repair_is_verified_by_different_crew(self):
  td,root,p=temp_vessel()
  try:
   r=p.repair_write('docs/x.txt','hello')
   self.assertEqual(r['status'],'completed'); self.assertTrue(r['verification']['ok']); self.assertNotEqual(r['crew'],r['verification']['verifier']); self.assertEqual((root/'docs/x.txt').read_text(),'hello')
  finally: td.cleanup()
 def test_persistence_survives_reopen(self):
  td,root,p=temp_vessel()
  try:
   r=p.command('Inspect vessel',mode=MissionMode.inspect); mid=r['mission_id']; p2=type(p)(root); self.assertIsNotNone(p2.store.mission(mid))
  finally: td.cleanup()
 def test_missing_capability_returns_to_pilot(self):
  td,root,p=temp_vessel()
  try:
   r=p.command('Repair file',mode=MissionMode.repair,crew_id='systems-architect',parameters={'operation':'write_text','path':'x','content':'x'},scope='x')
   self.assertEqual(r['status'],'needs_pilot_decision')
  finally: td.cleanup()
