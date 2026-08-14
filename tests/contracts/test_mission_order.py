import unittest
from grox.contracts import MissionOrder, MissionMode, RiskClass
class MissionOrderTest(unittest.TestCase):
 def test_order_serializes_native_values(self):
  o=MissionOrder.new('M','intent','obj',MissionMode.inspect,'systems-architect',risk_class=RiskClass.medium)
  d=o.to_dict(); self.assertEqual(d['mode'],'inspect'); self.assertEqual(d['risk_class'],'medium'); self.assertEqual(d['exception_channel'],'GorXu')
