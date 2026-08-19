import unittest

from grox.crew_cognition import CrewCognitionError
from grox.session_crew_cognition import SessionCrewCognitionProvider


class SessionCrewCognitionProviderTests(unittest.TestCase):
    def test_valid_hosted_step_is_returned_as_mapping(self):
        calls=[]
        def responder(order, craft_context, memory_context, observations):
            calls.append((order, craft_context, memory_context, observations))
            return {'action':'fs_read','path':'README.md'}
        provider=SessionCrewCognitionProvider(responder,name='session-crew-test')
        step=provider.next_step(order={'scope':['.']},craft_context=[],memory_context=[],observations=[])
        self.assertEqual(step,{'action':'fs_read','path':'README.md'})
        self.assertEqual(provider.name,'session-crew-test')
        self.assertEqual(len(calls),1)
        self.assertIsNone(provider.usage_snapshot())

    def test_non_mapping_host_output_is_recoverable_contract_error(self):
        provider=SessionCrewCognitionProvider(lambda *args: 'not-a-mapping')
        with self.assertRaisesRegex(CrewCognitionError,'must be a mapping'):
            provider.next_step(order={},craft_context=[],memory_context=[],observations=[])

    def test_recoverable_provider_error_remains_domain_error(self):
        def unavailable(*args):
            raise CrewCognitionError('session provider unavailable')
        provider=SessionCrewCognitionProvider(unavailable)
        with self.assertRaisesRegex(CrewCognitionError,'session provider unavailable'):
            provider.next_step(order={},craft_context=[],memory_context=[],observations=[])

    def test_unexpected_host_defect_is_not_normalized(self):
        def broken(*args):
            raise RuntimeError('session programming defect sentinel')
        provider=SessionCrewCognitionProvider(broken)
        with self.assertRaisesRegex(RuntimeError,'session programming defect sentinel'):
            provider.next_step(order={},craft_context=[],memory_context=[],observations=[])

    def test_invalid_binding_arguments_fail_fast(self):
        with self.assertRaises(TypeError):
            SessionCrewCognitionProvider(None)
        with self.assertRaises(ValueError):
            SessionCrewCognitionProvider(lambda *args: {'action':'finish','work_product':'ok'},name='  ')


if __name__=='__main__':
    unittest.main()
