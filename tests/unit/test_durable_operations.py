import hashlib
import subprocess
import unittest
from unittest.mock import patch

from grox.contracts import MissionMode, MissionOrder, RiskClass, TourResult
from grox.operations import ExecutiveExceptionLoop
from tests._support import temp_vessel


class DurableOperationsUnitTests(unittest.TestCase):
    def test_exception_policy_keeps_noncritical_unknown_with_pilot(self):
        td,root,p=temp_vessel()
        try:
            loop=ExecutiveExceptionLoop(p.durable)
            result=TourResult('O','backend-engineer','exception','unknown',[],{'type':'strange_condition'})
            decision=loop.decide(risk=RiskClass.high,result=result)
            self.assertEqual(decision.disposition,'pilot_halt')
            self.assertFalse(decision.requires_commander)
        finally: td.cleanup()

    def test_exception_policy_consults_for_ordinary_blocker(self):
        td,root,p=temp_vessel()
        try:
            loop=ExecutiveExceptionLoop(p.durable)
            result=TourResult('O','backend-engineer','exception','blocked',[],{'type':'blocker'})
            decision=loop.decide(risk=RiskClass.medium,result=result)
            self.assertEqual(decision.disposition,'consult_then_replan')
            self.assertTrue(decision.consult)
        finally: td.cleanup()

    def test_applied_mutation_replays_idempotently_and_becomes_verified(self):
        td,root,p=temp_vessel()
        try:
            target=root/'docs/idempotent.txt'; target.write_text('old')
            p.store.create_mission('M-idem','repair idempotently','repair','medium')
            content='new'
            order=MissionOrder.new(
                'M-idem','repair idempotently','repair file',MissionMode.repair,'backend-engineer',
                required_capabilities=['repo_read','repo_write'],allowed_actions=['fs_list','fs_read','fs_write','test_run'],
                scope=['docs/idempotent.txt'],risk_class=RiskClass.medium,
                parameters={'operation':'write_text','path':'docs/idempotent.txt','content':content,'_idempotency_key':'M-idem:repair:1'},
            )
            before=p.gateway.capture_text(order,'docs/idempotent.txt')
            intended=hashlib.sha256(content.encode()).hexdigest()
            p.durable.begin_mutation(
                idempotency_key='M-idem:repair:1',mission_id='M-idem',order_id=order.order_id,target='docs/idempotent.txt',
                before_exists=True,before_content=before['content'],before_sha256=before['sha256'],intended_sha256=intended,
            )
            applied=p.gateway.write_text(order,'docs/idempotent.txt',content)
            p.durable.update_mutation('M-idem:repair:1','applied',after_sha256=applied['sha256'])
            result=p.executor.execute(order)
            self.assertEqual(result.status,'completed')
            self.assertEqual(target.read_text(),'new')
            self.assertEqual(p.durable.mutation('M-idem:repair:1')['status'],'verified')
        finally: td.cleanup()

    def test_applied_mutation_divergence_is_not_overwritten(self):
        td,root,p=temp_vessel()
        try:
            target=root/'docs/diverged.txt'; target.write_text('old')
            p.store.create_mission('M-diverge','repair safely','repair','medium')
            content='new'
            order=MissionOrder.new(
                'M-diverge','repair safely','repair file',MissionMode.repair,'backend-engineer',
                required_capabilities=['repo_read','repo_write'],allowed_actions=['fs_list','fs_read','fs_write','test_run'],
                scope=['docs/diverged.txt'],risk_class=RiskClass.medium,
                parameters={'operation':'write_text','path':'docs/diverged.txt','content':content,'_idempotency_key':'M-diverge:repair:1'},
            )
            before=p.gateway.capture_text(order,'docs/diverged.txt')
            intended=hashlib.sha256(content.encode()).hexdigest()
            p.durable.begin_mutation(
                idempotency_key='M-diverge:repair:1',mission_id='M-diverge',order_id=order.order_id,target='docs/diverged.txt',
                before_exists=True,before_content=before['content'],before_sha256=before['sha256'],intended_sha256=intended,
            )
            applied=p.gateway.write_text(order,'docs/diverged.txt',content)
            p.durable.update_mutation('M-diverge:repair:1','applied',after_sha256=applied['sha256'])
            target.write_text('external change')
            result=p.executor.execute(order)
            self.assertEqual(result.status,'exception')
            self.assertEqual(result.exception['type'],'mutation_state_diverged')
            self.assertEqual(target.read_text(),'external change')
            self.assertEqual(p.durable.mutation('M-diverge:repair:1')['status'],'applied')
        finally: td.cleanup()

    def test_test_run_timeout_is_normalized_to_timeout_error(self):
        td,root,p=temp_vessel()
        try:
            order=MissionOrder.new(
                'M-time','inspect','bounded tests',MissionMode.verify,'code-reviewer',
                required_capabilities=['repo_read','verify'],allowed_actions=['fs_list','fs_read','test_run'],scope=['.'],
                parameters={'_graph_max_seconds':1},
            )
            with patch('grox.tools.gateway.subprocess.run',side_effect=subprocess.TimeoutExpired(['python'],1)):
                with self.assertRaises(TimeoutError):
                    p.gateway.run_tests(order)
        finally: td.cleanup()

    def test_unexpected_rollback_programming_defect_reaches_pilot_boundary(self):
        td,root,p=temp_vessel()
        try:
            target=root/'docs/rollback-defect.txt'
            with patch.object(p.gateway,'run_tests',return_value={'returncode':1,'stdout':'','stderr':'failure'}), \
                 patch.object(p.gateway,'rollback_text',side_effect=RuntimeError('rollback programming defect sentinel')):
                result=p.repair_write('docs/rollback-defect.txt','new content')
            self.assertEqual(result['status'],'unexpected_defect')
            self.assertEqual(result['exception']['exception_type'],'RuntimeError')
            self.assertIn('rollback programming defect sentinel',result['exception']['traceback'])
        finally: td.cleanup()


if __name__=='__main__':
    unittest.main()
