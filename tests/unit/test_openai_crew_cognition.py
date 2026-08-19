import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from grox.crew_cognition import CrewCognitionError
from grox.openai_crew_cognition import OpenAICrewCognitionProvider, OpenAICrewDisclosurePolicy


class _Response:
    def __init__(self, payload): self.payload=payload
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def read(self): return json.dumps(self.payload).encode('utf-8')


def policy(**kwargs):
    base={'allowed_scopes':('README.md',),'allow_order_text':True,'allow_craft':True,'allow_memory':True,'allowed_observation_actions':frozenset({'fs_list','fs_read','test_run'})}
    base.update(kwargs)
    return OpenAICrewDisclosurePolicy(**base)


class OpenAICrewCognitionProviderTests(unittest.TestCase):
    def test_requires_runtime_credentials_model_policy_and_official_endpoint(self):
        p=policy()
        with self.assertRaises(ValueError): OpenAICrewCognitionProvider(api_key='',model='gpt-5.6-luna',disclosure_policy=p)
        with self.assertRaises(ValueError): OpenAICrewCognitionProvider(api_key='k',model='',disclosure_policy=p)
        with self.assertRaises(ValueError): OpenAICrewCognitionProvider(api_key='k',model='gpt-5.6-luna',disclosure_policy=None)
        for endpoint in ('http://api.openai.com/v1/responses','https://example.test/v1/responses','https://user:secret@api.openai.com/v1/responses','https://api.openai.com/v1/responses?token=secret'):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError): OpenAICrewCognitionProvider(api_key='k',model='gpt-5.6-luna',disclosure_policy=p,endpoint=endpoint)

    def test_disclosure_policy_restricts_context_action_schema_and_scope(self):
        captured={}; restricted=OpenAICrewDisclosurePolicy(allowed_scopes=('README.md',)); provider=OpenAICrewCognitionProvider(api_key='k',model='gpt-5.6-luna',disclosure_policy=restricted)
        payload={'output_text':json.dumps({'action':'finish','path':None,'work_product':'done'})}
        def fake(request,timeout): captured['body']=json.loads(request.data.decode()); return _Response(payload)
        order={'mission_id':'MSN-1','scope':['README.md'],'commander_intent':'SECRET-INTENT','objective':'SECRET-OBJECTIVE','allowed_actions':['fs_read']}
        with patch('grox.openai_crew_cognition.urlopen',side_effect=fake): provider.next_step(order=order,craft_context=[{'content':'SECRET-CRAFT'}],memory_context=[{'text':'SECRET-MEMORY'}],observations=[{'action':'fs_read','path':'README.md','content':'SECRET-FILE'}])
        text=captured['body']['input']
        for sentinel in ('SECRET-INTENT','SECRET-OBJECTIVE','SECRET-CRAFT','SECRET-MEMORY','SECRET-FILE'): self.assertNotIn(sentinel,text)
        self.assertEqual(captured['body']['text']['format']['schema']['properties']['action']['enum'],['finish'])
        with patch('grox.openai_crew_cognition.urlopen') as network:
            with self.assertRaisesRegex(CrewCognitionError,'scope exceeds'): provider.next_step(order={'scope':['docs']},craft_context=[],memory_context=[],observations=[])
            network.assert_not_called()

    def test_model_action_schema_is_intersection_of_policy_and_order(self):
        captured={}; provider=OpenAICrewCognitionProvider(api_key='k',model='gpt-5.6-luna',disclosure_policy=policy())
        def fake(request,timeout): captured['body']=json.loads(request.data.decode()); return _Response({'output_text':json.dumps({'action':'finish','path':None,'work_product':'done'})})
        with patch('grox.openai_crew_cognition.urlopen',side_effect=fake): provider.next_step(order={'scope':['README.md'],'allowed_actions':['fs_read']},craft_context=[],memory_context=[],observations=[])
        self.assertEqual(captured['body']['text']['format']['schema']['properties']['action']['enum'],['finish','fs_read'])

    def test_responses_request_is_structured_read_only_and_context_bounded(self):
        captured={}; payload={'id':'resp_test_123','model':'gpt-5.6-luna-test','usage':{'input_tokens':120,'input_tokens_details':{'cached_tokens':30},'output_tokens':24,'output_tokens_details':{'reasoning_tokens':8},'total_tokens':144},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'action':'fs_read','path':'README.md','work_product':None})}]}]}
        def fake(request,timeout): captured['url']=request.full_url; captured['body']=json.loads(request.data.decode()); captured['authorization']=request.get_header('Authorization'); return _Response(payload)
        provider=OpenAICrewCognitionProvider(api_key='test-runtime-secret',model='gpt-5.6-luna',disclosure_policy=policy(),timeout=17,max_output_tokens=700)
        order={'mission_id':'MSN-1','scope':['README.md'],'commander_intent':'Inspect README','objective':'inspect','allowed_actions':['fs_list','fs_read','test_run']}
        with patch('grox.openai_crew_cognition.urlopen',side_effect=fake): step=provider.next_step(order=order,craft_context=[{'heading':'Safety Boundaries','content':'read only'}],memory_context=[{'memory_id':'MEM-1','text':'prior evidence'}],observations=[{'action':'fs_list','path':'README.md','files':['README.md']}])
        self.assertEqual(step['action'],'fs_read'); self.assertEqual(captured['url'],'https://api.openai.com/v1/responses'); self.assertEqual(captured['authorization'],'Bearer test-runtime-secret')
        body=captured['body']; self.assertFalse(body['store']); self.assertEqual(body['model'],'gpt-5.6-luna'); self.assertEqual(body['max_output_tokens'],700); self.assertEqual(body['text']['format']['schema']['properties']['action']['enum'],['finish','fs_list','fs_read','test_run'])
        for value in ('MSN-1','Safety Boundaries','MEM-1','README.md'): self.assertIn(value,body['input'])
        usage=provider.usage_snapshot(); self.assertEqual(usage.model,'gpt-5.6-luna-test'); self.assertEqual(usage.input_tokens,120); self.assertEqual(usage.cached_input_tokens,30); self.assertEqual(usage.reasoning_tokens,8); self.assertEqual(usage.total_tokens,144); self.assertEqual(provider.response_id_snapshot(),'resp_test_123')
        snap=provider.disclosure_policy_snapshot(); self.assertTrue(snap['allow_craft']); self.assertTrue(snap['allow_memory']); self.assertNotIn('allowed_scopes',snap)

    def test_output_and_failures_are_bounded(self):
        provider=OpenAICrewCognitionProvider(api_key='k',model='gpt-5.6-luna',disclosure_policy=policy(allowed_observation_actions=frozenset())); order={'scope':['README.md'],'allowed_actions':[]}
        with patch('grox.openai_crew_cognition.urlopen',return_value=_Response({'id':'r','output_text':json.dumps({'action':'finish','path':None,'work_product':'bounded result'})})): self.assertEqual(provider.next_step(order=order,craft_context=[],memory_context=[],observations=[])['action'],'finish')
        with patch('grox.openai_crew_cognition.urlopen',return_value=_Response({'output_text':'{not-json'})):
            with self.assertRaises(CrewCognitionError): provider.next_step(order=order,craft_context=[],memory_context=[],observations=[])
        secret='sensitive-provider-message-must-not-persist'; err=HTTPError('https://api.openai.com/v1/responses',429,'rate',{},io.BytesIO(json.dumps({'error':{'message':secret,'type':'rate_limit_error','code':'rate_limit_exceeded'}}).encode()))
        with patch('grox.openai_crew_cognition.urlopen',side_effect=err):
            with self.assertRaises(CrewCognitionError) as caught: provider.next_step(order=order,craft_context=[],memory_context=[],observations=[])
        message=str(caught.exception); self.assertIn('HTTP 429',message); self.assertIn('type=rate_limit_error',message); self.assertNotIn(secret,message)
        with patch('grox.openai_crew_cognition.urlopen',side_effect=URLError('offline')):
            with self.assertRaisesRegex(CrewCognitionError,'provider failure'): provider.next_step(order=order,craft_context=[],memory_context=[],observations=[])


if __name__=='__main__': unittest.main()
