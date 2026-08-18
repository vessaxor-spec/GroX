import unittest

from grox.contracts import Evidence, RiskClass, TourResult
from tests._support import temp_vessel


class CrewCognitionPerformanceTests(unittest.TestCase):
    def test_cognition_and_craft_bookkeeping_do_not_inflate_evidence_quality(self):
        td,root,p=temp_vessel()
        try:
            operational=[
                Evidence('inventory',{'count':1}),
                Evidence('test_run',{'returncode':0}),
            ]
            baseline=TourResult('ORD-baseline','backend-engineer','completed','baseline',list(operational))
            augmented=TourResult(
                'ORD-augmented','backend-engineer','completed','augmented',
                list(operational)+[
                    Evidence('craft_selection',{'craft_sha256':'a'*64}),
                    Evidence('crew_cognition_observation',{'action':'fs_read','sha256':'b'*64}),
                    Evidence('crew_cognition',{'provider':'fake','work_product':'bounded'}),
                ],
            )
            p.intelligence.record_performance(
                crew_id='backend-engineer',mission_id='MSN-baseline',order_id='ORD-baseline',
                task_class='baseline-quality',result=baseline,latency_ms=1.0,risk=RiskClass.low,
            )
            p.intelligence.record_performance(
                crew_id='backend-engineer',mission_id='MSN-augmented',order_id='ORD-augmented',
                task_class='augmented-quality',result=augmented,latency_ms=1.0,risk=RiskClass.low,
            )
            baseline_row=p.store.performance_history('backend-engineer','baseline-quality')[0]
            augmented_row=p.store.performance_history('backend-engineer','augmented-quality')[0]
            self.assertEqual(baseline_row['evidence_quality'],augmented_row['evidence_quality'])
            self.assertAlmostEqual(baseline_row['evidence_quality'],0.916667,places=6)
        finally:
            td.cleanup()


if __name__=='__main__':
    unittest.main()
