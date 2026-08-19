import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from grox.crew_cognition import CrewCognitionError
from grox.openai_crew_cognition import OpenAICrewCognitionProvider


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode('utf-8')


class OpenAICrewCognitionProviderTests(unittest.TestCase):
    def test_requires_runtime_credentials_model_and_official_endpoint(self):
        with self.assertRaises(ValueError):
            OpenAICrewCognitionProvider(api_key='', model='gpt-5.6-luna')
        with self.assertRaises(ValueError):
            OpenAICrewCognitionProvider(api_key='test-key', model='')
        for endpoint in (
            'http://api.openai.com/v1/responses',
            'https://example.test/v1/responses',
            'https://user:secret@api.openai.com/v1/responses',
            'https://api.openai.com/v1/responses?token=secret',
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    OpenAICrewCognitionProvider(api_key='test-key', model='gpt-5.6-luna', endpoint=endpoint)

    def test_responses_request_is_structured_read_only_and_context_bounded(self):
        captured = {}
        payload = {
            'id': 'resp_test_123',
            'model': 'gpt-5.6-luna-test',
            'usage': {
                'input_tokens': 120,
                'input_tokens_details': {'cached_tokens': 30},
                'output_tokens': 24,
                'output_tokens_details': {'reasoning_tokens': 8},
                'total_tokens': 144,
            },
            'output': [
                {
                    'type': 'message',
                    'content': [
                        {
                            'type': 'output_text',
                            'text': json.dumps({'action': 'fs_read', 'path': 'README.md', 'work_product': None}),
                        }
                    ],
                }
            ],
        }

        def fake_urlopen(request, timeout):
            captured['url'] = request.full_url
            captured['timeout'] = timeout
            captured['body'] = json.loads(request.data.decode('utf-8'))
            captured['authorization'] = request.get_header('Authorization')
            return _Response(payload)

        provider = OpenAICrewCognitionProvider(
            api_key='test-runtime-secret',
            model='gpt-5.6-luna',
            timeout=17,
            max_output_tokens=700,
        )
        with patch('grox.openai_crew_cognition.urlopen', side_effect=fake_urlopen):
            step = provider.next_step(
                order={'mission_id': 'MSN-1', 'allowed_actions': ['fs_read']},
                craft_context=[{'heading': 'Safety Boundaries', 'content': 'read only'}],
                memory_context=[{'memory_id': 'MEM-1', 'text': 'prior evidence'}],
                observations=[{'action': 'fs_list', 'files': ['README.md']}],
            )

        self.assertEqual(step['action'], 'fs_read')
        self.assertEqual(step['path'], 'README.md')
        self.assertEqual(captured['url'], 'https://api.openai.com/v1/responses')
        self.assertEqual(captured['timeout'], 17)
        self.assertEqual(captured['authorization'], 'Bearer test-runtime-secret')
        body = captured['body']
        self.assertFalse(body['store'])
        self.assertEqual(body['model'], 'gpt-5.6-luna')
        self.assertEqual(body['max_output_tokens'], 700)
        schema = body['text']['format']['schema']
        self.assertEqual(schema['properties']['action']['enum'], ['finish', 'fs_list', 'fs_read', 'test_run'])
        self.assertNotIn('fs_write', json.dumps(schema))
        self.assertNotIn('repair', json.dumps(schema).lower())
        self.assertIn('MSN-1', body['input'])
        self.assertIn('Safety Boundaries', body['input'])
        self.assertIn('MEM-1', body['input'])
        self.assertIn('README.md', body['input'])
        usage = provider.usage_snapshot()
        self.assertIsNotNone(usage)
        self.assertEqual(usage.model, 'gpt-5.6-luna-test')
        self.assertEqual(usage.input_tokens, 120)
        self.assertEqual(usage.cached_input_tokens, 30)
        self.assertEqual(usage.reasoning_tokens, 8)
        self.assertEqual(usage.total_tokens, 144)
        self.assertEqual(provider.response_id_snapshot(), 'resp_test_123')

    def test_output_text_convenience_shape_is_supported(self):
        provider = OpenAICrewCognitionProvider(api_key='test-key', model='gpt-5.6-luna')
        payload = {
            'id': 'resp_finish',
            'model': 'gpt-5.6-luna',
            'output_text': json.dumps({'action': 'finish', 'path': None, 'work_product': 'bounded result'}),
        }
        with patch('grox.openai_crew_cognition.urlopen', return_value=_Response(payload)):
            step = provider.next_step(order={}, craft_context=[], memory_context=[], observations=[])
        self.assertEqual(step['action'], 'finish')
        self.assertEqual(step['work_product'], 'bounded result')
        self.assertEqual(provider.response_id_snapshot(), 'resp_finish')
        self.assertIsNone(provider.usage_snapshot())

    def test_malformed_or_missing_structured_output_is_bounded_provider_error(self):
        provider = OpenAICrewCognitionProvider(api_key='test-key', model='gpt-5.6-luna')
        with patch(
            'grox.openai_crew_cognition.urlopen',
            return_value=_Response({'output_text': '{not-json'}),
        ):
            with self.assertRaises(CrewCognitionError):
                provider.next_step(order={}, craft_context=[], memory_context=[], observations=[])
        with patch('grox.openai_crew_cognition.urlopen', return_value=_Response({'output': []})):
            with self.assertRaises(CrewCognitionError):
                provider.next_step(order={}, craft_context=[], memory_context=[], observations=[])

    def test_http_and_network_failures_are_bounded_and_http_body_is_not_persisted(self):
        provider = OpenAICrewCognitionProvider(api_key='test-key', model='gpt-5.6-luna')
        secret_sentinel = 'sensitive-provider-message-must-not-persist'
        body = json.dumps({
            'error': {
                'message': secret_sentinel,
                'type': 'rate_limit_error',
                'code': 'rate_limit_exceeded',
            }
        }).encode('utf-8')
        http_error = HTTPError(
            'https://api.openai.com/v1/responses',
            429,
            'rate limited',
            {},
            io.BytesIO(body),
        )
        with patch('grox.openai_crew_cognition.urlopen', side_effect=http_error):
            with self.assertRaises(CrewCognitionError) as caught:
                provider.next_step(order={}, craft_context=[], memory_context=[], observations=[])
        message = str(caught.exception)
        self.assertIn('HTTP 429', message)
        self.assertIn('type=rate_limit_error', message)
        self.assertIn('code=rate_limit_exceeded', message)
        self.assertNotIn(secret_sentinel, message)
        with patch('grox.openai_crew_cognition.urlopen', side_effect=URLError('offline')):
            with self.assertRaisesRegex(CrewCognitionError, 'provider failure'):
                provider.next_step(order={}, craft_context=[], memory_context=[], observations=[])


if __name__ == '__main__':
    unittest.main()
