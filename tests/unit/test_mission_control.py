import unittest
from grox.mission_control.core import MissionControl
from grox.contracts import MissionMode, RiskClass
class MCTest(unittest.TestCase):
 def setUp(self): self.mc=MissionControl()
 def test_inspect_mode(self): self.assertEqual(self.mc.infer_mode('Inspect the vessel'),MissionMode.inspect)
 def test_repair_requires_verification(self): self.assertTrue(self.mc.verification_required(MissionMode.repair,RiskClass.low))
 def test_critical_keyword(self): self.assertEqual(self.mc.assess_risk('rotate credentials'),RiskClass.critical)
