from pathlib import Path
import json, tempfile
from grox.pilot import PilotGorXu

CREW=[
{"crew_id":"test-architecture-specialist","division":"engineering","title":"Systems Architect","capabilities":["repo_read","architecture_review","analysis","test_run"],"tags":["architecture","inspect","review"]},
{"crew_id":"backend-engineer","division":"engineering","title":"Backend Engineer","capabilities":["repo_read","repo_write","python","test_run"],"tags":["repair","write","code"]},
{"crew_id":"code-reviewer","division":"verification","title":"Code Reviewer","capabilities":["repo_read","code_review","verify","test_run"],"tags":["verify","review"],"verification":True},
{"crew_id":"independent-verifier","division":"verification","title":"Independent Verifier","capabilities":["repo_read","verify","test_run"],"tags":["verify","evidence"],"ordinary_routing":False,"verification":True},
]

def temp_vessel():
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    (root/'configs/crew/dossiers').mkdir(parents=True); (root/'tests').mkdir(); (root/'docs').mkdir()
    (root/'README.md').write_text('# test\n')
    # A tiny always-passing nested test for ToolGateway.run_tests
    (root/'tests/test_smoke.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
    for d in CREW: (root/'configs/crew/dossiers'/f"{d['crew_id']}.json").write_text(json.dumps(d))
    return td,root,PilotGorXu(root)
