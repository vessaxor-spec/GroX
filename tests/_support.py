from pathlib import Path
import json, tempfile
from grox.pilot import PilotGorXu

CREW=[
{"crew_id":"test-architecture-specialist","division":"engineering","title":"Systems Architect","capabilities":["repo_read","architecture_review","analysis","test_run"],"tags":["architecture","inspect","review"]},
{"crew_id":"backend-engineer","division":"engineering","title":"Backend Engineer","capabilities":["repo_read","repo_write","python","test_run"],"tags":["repair","write","code"]},
{"crew_id":"code-reviewer","division":"verification","title":"Code Reviewer","capabilities":["repo_read","code_review","verify","test_run"],"tags":["verify","review"],"verification":True},
{"crew_id":"independent-verifier","division":"verification","title":"Independent Verifier","capabilities":["repo_read","verify","test_run"],"tags":["verify","evidence"],"ordinary_routing":False,"verification":True},
]

# Some integration fixtures add these dossiers after temp_vessel() returns. Their
# craft stubs are pre-provisioned so the synthetic Vessel preserves the same
# dossier-to-craft invariant as production when those dossiers are activated.
DYNAMIC_CRAFT_FIXTURES=[
{"crew_id":"devops-engineer","division":"platform","title":"DevOps Engineer","capabilities":["repo_read","workspace_exec"],"tags":["workspace","platform","runtime"]},
]


def _synthetic_craft(dossier):
    crew_id=dossier['crew_id']
    title=dossier['title']
    tags=', '.join(dossier.get('tags',[]))
    return f'''---
name: {crew_id}
description: Synthetic test craft for {title}
freshness_policy: test-fixture
source_repository: GroX-test-fixture
source_revision: test
---

## Identity

{title} test identity for bounded GroX regression fixtures.

## Purpose

Perform {tags or 'bounded'} work only within the issued Mission Order.

## Domain Context

Synthetic regression context for {tags or 'general'} tasks.

## Responsibilities

Inspect evidence, follow scope, and return bounded results to Pilot GorXu.

## Non-Responsibilities

Do not create authority, route other Crew, or widen scope.

## Inputs

Mission Order, bounded source evidence, and selected memory.

## Outputs

Attributable bounded evidence for regression tests.

## Safety Boundaries

Never infer Repair permission from expertise or natural-language wording.

## GroX Operational Binding

Pilot GorXu remains sole operational orchestrator. Mission authority and Repair permission come only from the existing GroX authority path.
'''


def add_synthetic_crew(root: Path, dossier: dict) -> None:
    """Add one synthetic Crew identity with the same craft-card invariant as production."""
    (root/'configs/crew/dossiers').mkdir(parents=True, exist_ok=True)
    (root/'configs/crew/specialists').mkdir(parents=True, exist_ok=True)
    crew_id=dossier['crew_id']
    (root/'configs/crew/dossiers'/f"{crew_id}.json").write_text(json.dumps(dossier))
    (root/'configs/crew/specialists'/f"{crew_id}.md").write_text(_synthetic_craft(dossier))


def temp_vessel():
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    (root/'configs/crew/dossiers').mkdir(parents=True); (root/'configs/crew/specialists').mkdir(parents=True)
    (root/'tests').mkdir(); (root/'docs').mkdir()
    (root/'README.md').write_text('# test\n')
    # A tiny always-passing nested test for ToolGateway.run_tests
    (root/'tests/test_smoke.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
    for d in CREW:
        add_synthetic_crew(root,d)
    for d in DYNAMIC_CRAFT_FIXTURES:
        (root/'configs/crew/specialists'/f"{d['crew_id']}.md").write_text(_synthetic_craft(d))
    return td,root,PilotGorXu(root)
