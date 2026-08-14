from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import json
from pathlib import Path
import shutil
import sys
import tempfile
from threading import Thread
import unittest

from grox.contracts import RiskClass
from grox.pilot import PilotGorXu
from grox.tools.mcp import MCPAdapterSpec
from grox.tools.policy import GatewayPolicy
from grox.tools.workspace import docker_backend_available, namespace_backend_available
from grox.tools.secrets import SecretBroker


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "mcp_echo_server.py"
DOCKER_IMAGE = "alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc"
BROWSER_DOCKER_IMAGE = os.environ.get("A5_BROWSER_DOCKER_IMAGE")


class PageHandler(BaseHTTPRequestHandler):
    body = b"<html><title>GroX A5</title><h1>governed</h1><img src='http://example.invalid/blocked.png'><iframe src='file:///etc/passwd'></iframe></html>"
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers(); self.wfile.write(self.body)
    def log_message(self, *_): pass


def write_crew(root: Path, crew_id: str, division: str, caps: list[str], tags: list[str], verification=False):
    raw={"crew_id":crew_id,"division":division,"title":crew_id.replace('-', ' ').title(),"capabilities":caps,"tags":tags,"verification":verification}
    (root/'configs/crew/dossiers'/f'{crew_id}.json').write_text(json.dumps(raw))


class GovernedCapabilityIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(namespace_backend_available() or docker_backend_available(DOCKER_IMAGE), "qualified A5 workspace isolation backend required")
    def test_real_multi_tool_mission_is_order_gated_evidenced_and_independently_verified(self):
        try:
            import playwright  # noqa: F401
        except ImportError:
            self.skipTest("Playwright browser extra required")
        if not any(shutil.which(x) for x in ("chromium","chromium-browser","google-chrome","google-chrome-stable")):
            self.skipTest("Chromium/Chrome required")
        td=tempfile.TemporaryDirectory(); root=Path(td.name)
        server=ThreadingHTTPServer(("127.0.0.1",0),PageHandler)
        Thread(target=server.serve_forever,daemon=True).start()
        secret_value="A5-LIVE-SECRET-MUST-NOT-PERSIST"
        try:
            (root/'configs/crew/dossiers').mkdir(parents=True); (root/'configs/state').mkdir(parents=True)
            (root/'tests').mkdir(); (root/'docs').mkdir(); (root/'README.md').write_text('# A5 qualification\n')
            (root/'tests/test_smoke.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
            write_crew(root,'devops-engineer','platform',['repo_read','workspace_exec','secret_use'],['workspace','shell','isolation'])
            write_crew(root,'researcher','intelligence',['repo_read','net_fetch','browser_capture'],['research','network','browser'])
            write_crew(root,'platform-engineer','platform',['repo_read','mcp_call'],['platform','mcp','adapter'])
            write_crew(root,'independent-verifier','verification',['repo_read','verify','test_run'],['verify','evidence'],True)
            origin=f'http://127.0.0.1:{server.server_port}'
            mcp_spec=MCPAdapterSpec(argv=(sys.executable,str(FIXTURE)),allowed_tools=frozenset({'echo'}))
            p=PilotGorXu(
                root, reasoner=None, extra_allowed_origins=[origin],
                gateway_policy=GatewayPolicy(
                    allowed_origins=frozenset({origin}),
                    workspace_docker_image=DOCKER_IMAGE,
                    browser_docker_image=BROWSER_DOCKER_IMAGE,
                ),
                secret_broker=SecretBroker({'qualification_token':secret_value}),
                mcp_registry={'qualification':mcp_spec},
            )
            directive='Execute a governed multi-tool capability qualification and independently verify every tool path.'
            plan={
                'commander_intent':directive,
                'objective':'Prove isolated workspace, secret brokerage, origin-gated network, offline browser evidence, and MCP adapter governance.',
                'budget':{'max_nodes':8,'max_parallel':1,'max_replans':1},
                'nodes':[
                    {
                        'node_id':'workspace','objective':'Execute a bounded isolated shell workspace with an ephemeral credential alias','mode':'execute','dependencies':[],
                        'candidate_crew_ids':['devops-engineer'],'required_capabilities':['repo_read','workspace_exec','secret_use'],
                        'allowed_actions':['workspace_exec','secret_use'],'scope':['.'],'risk_class':'high',
                        'parameters':{'operation':'workspace_shell','script':'test ! -e /host; printf "%s" "$TOKEN"; printf qualified > /work/result.txt',
                                      'secret_env':{'TOKEN':'qualification_token'},'secret_grants':['qualification_token']},
                    },
                    {
                        'node_id':'network','objective':'Fetch evidence from the exact approved qualification origin','mode':'execute','dependencies':['workspace'],
                        'candidate_crew_ids':['researcher'],'required_capabilities':['repo_read','net_fetch'],'allowed_actions':['net_fetch'],
                        'scope':['.'],'risk_class':'high','parameters':{'operation':'http_fetch','url':origin+'/','allowed_origins':[origin]},
                    },
                    {
                        'node_id':'browser','objective':'Render approved network evidence in offline browser and capture screenshot evidence','mode':'execute','dependencies':['network'],
                        'candidate_crew_ids':['researcher'],'required_capabilities':['repo_read','net_fetch','browser_capture'],
                        'allowed_actions':['net_fetch','browser_capture'],'scope':['.'],'risk_class':'high',
                        'parameters':{'operation':'browser_capture','url':origin+'/','allowed_origins':[origin]},
                    },
                    {
                        'node_id':'mcp','objective':'Call a pre-registered read-only MCP tool through the governed adapter','mode':'execute','dependencies':['browser'],
                        'candidate_crew_ids':['platform-engineer'],'required_capabilities':['repo_read','mcp_call'],'allowed_actions':['mcp_call'],
                        'scope':['.'],'risk_class':'high','parameters':{'operation':'mcp_call','adapter':'qualification','tool':'echo',
                                    'arguments':{'text':'A5 governed'},'mcp_grants':{'qualification':['echo']}},
                    },
                    {
                        'node_id':'verify','objective':'Independently verify all governed capability evidence','mode':'verify','dependencies':['workspace','network','browser','mcp'],
                        'candidate_crew_ids':['independent-verifier'],'required_capabilities':['repo_read','verify'],'scope':['.'],
                        'parameters':{'run_tests':True},
                    },
                ],
            }
            result=p.command_graph(directive,plan=plan,risk=RiskClass.high,plan_source='a5-governed-capability-test')
            self.assertEqual(result['status'],'completed')
            self.assertTrue(result['synthesis']['verification_passed'])
            self.assertEqual(result['synthesis']['replans'],0)
            expected={'workspace_execution','network_fetch','browser_capture','mcp_call','graph_verification'}
            self.assertTrue(expected.issubset(set(result['synthesis']['evidence_kinds'])))
            mission=p.store.mission(result['mission_id'])
            serialized=json.dumps(mission,sort_keys=True)
            self.assertNotIn(secret_value,serialized)
            orders={json.loads(o['payload'])['objective']:json.loads(o['payload']) for o in mission['orders']}
            self.assertIn('workspace_exec',orders['Execute a bounded isolated shell workspace with an ephemeral credential alias']['allowed_actions'])
            self.assertIn('net_fetch',orders['Fetch evidence from the exact approved qualification origin']['allowed_actions'])
            self.assertIn('browser_capture',orders['Render approved network evidence in offline browser and capture screenshot evidence']['allowed_actions'])
            self.assertIn('mcp_call',orders['Call a pre-registered read-only MCP tool through the governed adapter']['allowed_actions'])
            evidence=[(e['kind'],json.loads(e['content'])) for e in mission['evidence']]
            workspace=next(c for k,c in evidence if k=='workspace_execution')
            browser=next(c for k,c in evidence if k=='browser_capture')
            self.assertEqual(workspace['stdout'],'[REDACTED]')
            self.assertIn(workspace['isolation_backend'], {'namespace', 'docker'})
            self.assertTrue(
                'network_namespace' in workspace['isolation']
                or 'docker_network_none' in workspace['isolation']
            )
            self.assertFalse(workspace['workspace_retained'])
            self.assertTrue((root/browser['screenshot']).is_file())
            self.assertEqual(browser['browser_network'],'disabled_after_gateway_fetch')
            self.assertIn(browser['browser_backend'], {'namespace', 'docker'})
            self.assertTrue(
                'network_namespace' in browser['browser_isolation']
                or 'docker_network_none' in browser['browser_isolation']
            )
            if browser['browser_backend'] == 'docker':
                self.assertIn('outer_container_sandbox', browser['browser_isolation'])
                self.assertIn('docker_builtin_seccomp', browser['browser_isolation'])
                self.assertTrue(browser['browser_image_id'])
            self.assertIn('http://example.invalid',browser['blocked_origins'])
        finally:
            server.shutdown(); server.server_close(); td.cleanup()


if __name__=='__main__':
    unittest.main()
