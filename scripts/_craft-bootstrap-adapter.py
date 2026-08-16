#!/usr/bin/env python3
"""Temporary bootstrap adapter for the bounded Standing Crew craft Repair.

This file exists only to materialize the Repair branch and is removed before final review.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/sync-crew-specialists.py"
spec = importlib.util.spec_from_file_location("grox_craft_import", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load pinned craft importer")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SUPPLEMENT = {
    "## Identity": """## Identity\n\nThe source card expresses this specialist identity through its purpose, responsibilities, protocols, collaboration model, and examples. In GroX that identity is retained as Standing Crew craft competence under Pilot GorXu, never as independent Mission authority.""",
    "## Purpose": """## Purpose\n\nApply the source card's defined specialist craft to the bounded Mission objective while preserving GroX authority, evidence, and freshness requirements.""",
    "## Domain Context": """## Domain Context\n\nThe domain context is established by this card's source frontmatter, purpose, detailed operating protocols, responsibilities, collaboration boundaries, and example tasks. In GroX those domain practices remain craft guidance; current authoritative evidence overrides stale implementation assumptions when the domain is time-sensitive.""",
    "## Responsibilities": """## Responsibilities\n\nPerform the specialist duties and protocols defined throughout this card within the active Mission Order and return attributable outputs to GorXu.""",
    "## Non-Responsibilities": """## Non-Responsibilities\n\nDo not assume work assigned to other named Crew, self-deploy collaborators, widen Mission scope, or treat specialist competence as permission. Cross-domain needs return to GorXu for routing.""",
    "## Inputs": """## Inputs\n\nUse the Mission objective, authorized scope, relevant domain evidence, source artifacts, and any explicit acceptance criteria supplied through the active Mission Order.""",
    "## Outputs": """## Outputs\n\nReturn the domain artifacts, findings, recommendations, and evidence required by the source craft and the active Mission Order, with uncertainty and unresolved constraints made explicit.""",
    "## Safety Boundaries": """## Safety Boundaries\n\nRemain inside the active Mission Order, capability grant, host policy, and source card's domain constraints. Stop before affected mutation when a blocker, safer path, missing capability, elevated risk, scope change, or irreversible consequence is discovered, and report to GorXu.""",
}


def adapt(role: str, source: str) -> str:
    frontmatter, body = mod._split_frontmatter(source)
    fields = mod._frontmatter_fields(frontmatter)
    required_fields = {"name", "description", "domains", "freshness_policy"}
    missing_fields = required_fields - fields
    if missing_fields:
        raise RuntimeError(f"{role}: source card missing frontmatter fields {sorted(missing_fields)}")
    if "category" not in fields and "division" not in fields:
        raise RuntimeError(f"{role}: source card needs category or division")
    name_match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", frontmatter, flags=re.MULTILINE)
    if not name_match or name_match.group(1).strip() != role:
        raise RuntimeError(f"{role}: source card name does not match manifest stem")

    allocation = body.rfind("\n## TEO Allocation")
    if allocation < 0:
        allocation = body.rfind("## TEO Allocation")
    if allocation < 0:
        raise RuntimeError(f"{role}: expected TEO Allocation boundary not found")
    craft_body = body[:allocation].rstrip()

    # Remove the only forbidden specialist identity from craft handoffs. Its
    # orchestration responsibility is folded into GorXu rather than recruited.
    craft_body = re.sub(r"\bagents-orchestrator\b", "Pilot GorXu", craft_body, flags=re.IGNORECASE)
    # Any remaining TEO name in the pre-allocation body is a source-environment
    # reference. Port it to GroX rather than importing an external control plane.
    craft_body = re.sub(r"\bTEO\b", "GroX", craft_body)

    supplements = [SUPPLEMENT[h] for h in mod.REQUIRED_HEADINGS if h not in craft_body]

    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    provenance = (
        f'\nsource_repository: "{mod.TEO_REPOSITORY}"\n'
        f'source_revision: "{mod.TEO_REVISION}"\n'
        f'source_card: "{mod.SOURCE_PREFIX}{role}.md"\n'
        f'source_content_sha256: "{source_hash}"\n'
        'grox_binding: "standing-crew"'
    )
    adapted_frontmatter = frontmatter.rstrip() + provenance

    additions: list[str] = supplements
    if role == "incident-commander":
        additions.append(mod.INCIDENT_COMMANDER_NOTE)
    if role == "orchestration-evaluation-analyst":
        additions.append(mod.ORCHESTRATION_EVALUATION_NOTE)
    additions.append(mod.GROX_BINDING)

    output = "---\n" + adapted_frontmatter + "\n---\n\n" + craft_body
    if additions:
        output += "\n\n" + "\n\n".join(additions)
    output += "\n"

    for heading in (*mod.REQUIRED_HEADINGS, "## GroX Operational Binding"):
        if heading not in output:
            raise RuntimeError(f"{role}: adapted craft card missing {heading}")
    if "## TEO Allocation" in output or "agents-orchestrator" in output.lower():
        raise RuntimeError(f"{role}: forbidden source orchestration semantics leaked into GroX card")
    if len(output) < 4000 or len(output.splitlines()) < 80:
        raise RuntimeError(f"{role}: adapted craft card is too thin ({len(output)} chars / {len(output.splitlines())} lines)")
    return output


mod._adapt_source_card = adapt
raise SystemExit(mod.main())
