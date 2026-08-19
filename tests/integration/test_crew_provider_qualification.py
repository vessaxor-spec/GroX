import unittest

from grox.crew_provider import (
    CrewProviderBindingError,
    _content,
    bind_crew_cognition_provider,
    bound_crew_cognition_provider,
    qualify_bound_crew_cognition_provider,
)
from grox.session_crew_cognition import SessionCrewCognitionProvider
from tests._support import temp_vessel


class CrewProviderQualificationTests(unittest.TestCase):
    def test_bound_session_provider_passes_bounded_operational_evidence_gate(self):
        calls=[]
        def responder(order, craft_context, memory_context, observations):
            calls.append({
                'order':order,
                'craft_context':craft_context,
                'memory_context':memory_context,
                'observations':observations,
            })
            if not observations:
                return {'action':'fs_read','path':'README.md'}
            return {
                'action':'finish',
                'work_product':'README inspected through the bounded project-session Crew cognition path.',
            }

        td,root,p=temp_vessel()
        try:
            provider=SessionCrewCognitionProvider(responder,name='controlled-session-provider')
            self.assertEqual(bind_crew_cognition_provider(p,provider),'controlled-session-provider')
            self.assertEqual(bound_crew_cognition_provider(p),'controlled-session-provider')
            report=qualify_bound_crew_cognition_provider(
                p,
                directive='Inspect README evidence for bounded provider qualification',
                crew_id='backend-engineer',
            )
            self.assertEqual(report['status'],'PASS')
            self.assertTrue(all(report['checks'].values()))
            self.assertEqual(report['provider'],'controlled-session-provider')
            self.assertFalse(report['live_provider_claim'])
            self.assertGreaterEqual(len(calls),2)
            self.assertIn('craft_selection',report['evidence_kinds'])
            self.assertIn('crew_cognition_observation',report['evidence_kinds'])
            self.assertIn('independent_verification',report['evidence_kinds'])
        finally:
            td.cleanup()

    def test_denied_provider_fails_qualification_without_authority_widening(self):
        provider=SessionCrewCognitionProvider(
            lambda *args: {'action':'fs_write','path':'docs/forbidden.txt'},
            name='controlled-denied-provider',
        )
        td,root,p=temp_vessel()
        try:
            bind_crew_cognition_provider(p,provider)
            report=qualify_bound_crew_cognition_provider(
                p,
                directive='Inspect safely without mutation',
                crew_id='backend-engineer',
            )
            self.assertEqual(report['status'],'FAIL')
            self.assertFalse(report['checks']['mission_completed'])
            self.assertFalse(report['checks']['no_cognition_denial'])
            self.assertTrue(report['checks']['no_mutation_evidence'])
            self.assertFalse((root/'docs/forbidden.txt').exists())
            self.assertFalse(report['live_provider_claim'])
        finally:
            td.cleanup()

    def test_malformed_persisted_cognition_evidence_fails_closed(self):
        self.assertEqual(_content({'content':'{malformed'}),{})
        self.assertEqual(_content({'content':'[]'}),{})

    def test_binding_rejects_missing_or_unnamed_provider(self):
        td,root,p=temp_vessel()
        try:
            with self.assertRaises(CrewProviderBindingError):
                bind_crew_cognition_provider(p,None)
            class MissingName:
                def next_step(self, **kwargs):
                    return {'action':'finish','work_product':'x'}
            with self.assertRaises(CrewProviderBindingError):
                bind_crew_cognition_provider(p,MissingName())
        finally:
            td.cleanup()

    def test_qualification_requires_bound_provider(self):
        td,root,p=temp_vessel()
        try:
            with self.assertRaises(CrewProviderBindingError):
                qualify_bound_crew_cognition_provider(
                    p,
                    directive='Inspect bounded evidence',
                    crew_id='backend-engineer',
                )
        finally:
            td.cleanup()


if __name__=='__main__':
    unittest.main()
