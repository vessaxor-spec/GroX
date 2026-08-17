#!/usr/bin/env python3
"""Integrated qualification experiment for Post-Apex Operational Evolution Program 001.

This composes existing GroX production surfaces. It does not add a runtime
control layer, activate context compression, grant source authority, or persist
private qualification state outside temporary test storage.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

from grox.context_heat import ContextHeatPolicy, ContextItem, HOT
from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.health import FAIL as HEALTH_FAIL, PASS as HEALTH_PASS, VesselHealth
from grox.operational_drift import REGRESSION
from grox.reconstitution import FAST, FULL, ReconstitutionPlanner
from grox.source_provenance import FAIL as PROVENANCE_FAIL, PASS as PROVENANCE_PASS, UNKNOWN as PROVENANCE_UNKNOWN, SourceProvenanceService
from grox.state import StateStore, now


ROOT = Path(__file__).resolve().parents[2]


def _run_operational_drift() -> dict:
    """Load the existing drift experiment by path without packaging tests."""
    path = ROOT / "tests/experiments/operational_drift_experiment.py"
    spec = importlib.util.spec_from_file_location("grox_operational_drift_experiment", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load operational drift experiment: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run()


def _check_map(report) -> dict:
    return {check.check_id: check for check in report.checks}


def _degraded_health_fixture() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "configs/crew").mkdir(parents=True)
    shutil.copytree(ROOT / "configs/crew/dossiers", root / "configs/crew/dossiers")
    shutil.copy2(ROOT / "configs/crew/company-manifest.json", root / "configs/crew/company-manifest.json")
    shutil.copy2(ROOT / "configs/tool-policy.json", root / "configs/tool-policy.json")
    shutil.copy2(ROOT / "pyproject.toml", root / "pyproject.toml")
    (root / "src/grox").mkdir(parents=True)
    shutil.copy2(ROOT / "src/grox/__init__.py", root / "src/grox/__init__.py")
    (root / ".github/workflows").mkdir(parents=True)
    shutil.copy2(ROOT / ".github/workflows/ci.yml", root / ".github/workflows/ci.yml")
    (root / "tests/mutation").mkdir(parents=True)
    shutil.copy2(ROOT / "tests/mutation/run_critical_invariants.py", root / "tests/mutation/run_critical_invariants.py")
    (root / "docs/verification").mkdir(parents=True)
    shutil.copy2(
        ROOT / "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
        root / "docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md",
    )
    return td, root


def health_reconstitution_context_evidence() -> dict:
    planner = ReconstitutionPlanner()

    clean = VesselHealth(ROOT).collect()
    clean_checks = _check_map(clean)
    if clean.disposition != "HEALTHY":
        raise AssertionError(clean.to_dict())
    if clean_checks["command_integrity"].status != HEALTH_PASS:
        raise AssertionError(clean_checks["command_integrity"].to_dict())
    if clean_checks["command_integrity"].evidence["standing_crew"] != 82:
        raise AssertionError(clean_checks["command_integrity"].to_dict())
    clean_plan = planner.plan(clean)
    if clean_plan.mode != FAST:
        raise AssertionError(clean_plan.to_dict())
    fresh_plan = planner.plan(clean, fresh_host=True)
    if fresh_plan.mode != FULL:
        raise AssertionError(fresh_plan.to_dict())

    td, root = _degraded_health_fixture()
    try:
        store = StateStore(root / "configs/state/grox.sqlite3")
        timestamp = now()
        payload = {
            "order_id": "ORD-integrated-forged",
            "mission_id": "MSN-integrated-forged",
            "mode": "inspect",
            "assigned_crew": "code-reviewer",
            "allowed_actions": ["fs_read", "fs_write"],
        }
        store.db.execute(
            "INSERT INTO orders(order_id,mission_id,crew_id,mode,status,payload,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
            (
                payload["order_id"],
                payload["mission_id"],
                "code-reviewer",
                "inspect",
                "issued",
                json.dumps(payload, sort_keys=True),
                timestamp,
                timestamp,
            ),
        )
        store.db.commit()
        store.close()

        db_path = root / "configs/state/grox.sqlite3"
        before = hashlib.sha256(db_path.read_bytes()).hexdigest()
        degraded = VesselHealth(root).collect()
        after = hashlib.sha256(db_path.read_bytes()).hexdigest()
        if before != after:
            raise AssertionError("Vessel Health mutated private operational state")
        degraded_checks = _check_map(degraded)
        authority = degraded_checks["authority_integrity"]
        if degraded.disposition != "UNHEALTHY" or authority.status != HEALTH_FAIL:
            raise AssertionError(degraded.to_dict())
        if "non-Repair Order" not in authority.detail or "fs_write" not in authority.detail:
            raise AssertionError(authority.to_dict())
        degraded_plan = planner.plan(degraded)
        if degraded_plan.mode != FULL:
            raise AssertionError(degraded_plan.to_dict())

        intent = "COMMANDER_INTENT: qualify Post-Apex evolution without widening authority"
        authority_fact = "AUTHORITY: Inspect work cannot carry source mutation permission"
        fault_fact = f"CRITICAL_EVIDENCE: {authority.detail}"
        unresolved = "UNRESOLVED_CRITICAL: FAST reconstitution is forbidden while authority integrity is FAIL"
        next_action = "NEXT_ACTION: preserve the red finding and require FULL reconstitution"
        items = (
            ContextItem("intent", "commander_intent", intent, "ISSUE-48", active=True),
            ContextItem("authority", "authority", authority_fact, "COMMAND-BOUNDARY", active=True),
            ContextItem("fault", "critical_evidence", fault_fact, "VESSEL-HEALTH", critical=True),
            ContextItem("unresolved", "unresolved_contradiction", unresolved, "VESSEL-HEALTH+RECONSTITUTION", active=True),
            ContextItem("next", "next_action", next_action, "RECONSTITUTION-PLAN", active=True),
            ContextItem(
                "warm",
                "crew_finding",
                "Detailed integration finding: " + "bounded evidence remains attributable; " * 30,
                "INTEGRATION-OBSERVATION",
                summary="Finding: integration evidence remains attributable.",
                relevant=True,
            ),
            ContextItem("cold", "raw_tool_output", "re-derivable diagnostic noise " * 80, "TEMP-DIAGNOSTIC"),
        )
        required = (intent, authority_fact, fault_fact, unresolved, next_action)
        policy = ContextHeatPolicy()
        packed = policy.pack(items)
        audit = policy.audit_preservation(packed, required)
        if not audit.passed:
            raise AssertionError(audit.to_dict())
        by_id = {item.item_id: item for item in packed.items}
        for item_id in ("intent", "authority", "fault", "unresolved", "next"):
            if by_id[item_id].heat != HOT or by_id[item_id].compressed:
                raise AssertionError(by_id[item_id].to_dict())
        if any(not item.provenance for item in packed.items):
            raise AssertionError("retained context lost provenance")

        return {
            "clean_health": clean.to_dict(),
            "clean_reconstitution": clean_plan.to_dict(),
            "fresh_host_reconstitution": fresh_plan.to_dict(),
            "degraded_health": degraded.to_dict(),
            "degraded_reconstitution": degraded_plan.to_dict(),
            "health_read_only": before == after,
            "context": {
                "required_fact_preservation": audit.passed,
                "missing_required_facts": list(audit.missing_required_facts),
                "missing_provenance": list(audit.missing_provenance),
                "retained_ids": list(packed.retained_ids),
                "omitted_ids": list(packed.omitted_ids),
                "reduction_ratio": packed.reduction_ratio,
                "runtime_activation": False,
            },
        }
    finally:
        td.cleanup()


def external_intake_evidence() -> dict:
    text = (ROOT / "docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md").read_text(encoding="utf-8")
    circular = "| GroX-derived command spine, Crew model, memory planes, durable operations, Mission Graph, A6 trajectory concepts | REJECT |"
    duplicate = "| Separate decisions ledger | REJECT |"
    if circular not in text or duplicate not in text:
        raise AssertionError("external-intake circular/duplicate rejection contract is not intact")
    if "This is a review convention, not a command layer" not in text:
        raise AssertionError("external-intake convention drifted into a command layer")
    return {
        "circular_grox_reimport": "REJECT",
        "duplicate_decisions_ledger": "REJECT",
        "creates_command_layer": False,
    }


def source_provenance_evidence() -> dict:
    with tempfile.TemporaryDirectory() as td:
        store = StateStore(Path(td) / "private-qualification.sqlite3")
        try:
            mission_id = "MSN-private-post-apex-qualification"
            private_directive = "Commander-authorized private qualification fixture"
            store.create_mission(mission_id, private_directive, "repair", "high")
            order = MissionOrder.new(
                mission_id,
                "Qualify bounded source provenance",
                "Authorize only the integration evidence surfaces",
                MissionMode.repair,
                "backend-engineer",
                required_capabilities=("repo_read", "fs_write"),
                allowed_actions=("fs_read", "fs_write", "test_run"),
                forbidden_actions=("mcp_mutate",),
                scope=("tests/experiments", ".github/workflows", "docs/stewardship", "docs/verification", "docs/history/ships-log"),
                risk_class=RiskClass.high,
                evidence_requirements=("integration-report", "ci"),
                verification_requirements=("independent_verifier",),
            )
            store.save_order(order)
            service = SourceProvenanceService(store)
            paths = (
                "tests/experiments/post_apex_integration_experiment.py",
                ".github/workflows/ci.yml",
            )
            receipt = service.issue_receipt(
                mission_id=mission_id,
                order_ids=(order.order_id,),
                change_class="stewardship",
                scope_paths=paths,
                operation="mixed",
            )
            block = service.render_public_block(receipt)
            if service.validate_public_block(block).status != PROVENANCE_PASS:
                raise AssertionError(block)
            for private_value in (
                mission_id,
                order.order_id,
                receipt["nonce_hex"],
                "backend-engineer",
                private_directive,
                "Authorize only the integration evidence surfaces",
            ):
                if private_value in block:
                    raise AssertionError("public provenance block exposed private authority state")

            pr_number = 9001
            head_sha = "a" * 40
            tree_sha = "b" * 40
            verified = service.verify_change(
                (block,),
                changed_paths=paths,
                pr_number=pr_number,
                head_sha=head_sha,
                tree_sha=tree_sha,
            )
            if verified.status != PROVENANCE_PASS:
                raise AssertionError(verified.to_dict())
            if not service.verification_binding_matches(
                receipt["receipt_id"], pr_number=pr_number, head_sha=head_sha, tree_sha=tree_sha
            ):
                raise AssertionError("exact source binding was not retained")

            downgraded = block.replace("GroX-Change-Class: stewardship", "GroX-Change-Class: research")
            if service.verify_change(
                (downgraded,),
                changed_paths=paths,
                pr_number=pr_number,
                head_sha=head_sha,
                tree_sha=tree_sha,
            ).status != PROVENANCE_FAIL:
                raise AssertionError("change-class downgrade was accepted")

            missing_store = StateStore(Path(td) / "missing-witness.sqlite3")
            try:
                missing = SourceProvenanceService(missing_store).verify_change(
                    (block,),
                    changed_paths=paths,
                    pr_number=pr_number,
                    head_sha=head_sha,
                    tree_sha=tree_sha,
                )
            finally:
                missing_store.close()
            if missing.status != PROVENANCE_UNKNOWN:
                raise AssertionError(missing.to_dict())

            service.consume(
                receipt["receipt_id"],
                pr_number=pr_number,
                verified_head=head_sha,
                verified_tree=tree_sha,
                canonical_commit="c" * 40,
            )
            replay = service.verify_change(
                (block,),
                changed_paths=paths,
                pr_number=9002,
                head_sha="d" * 40,
                tree_sha="e" * 40,
            )
            if replay.status != PROVENANCE_FAIL:
                raise AssertionError("consumed private authorization was replayed")

            inspect_order = MissionOrder.new(
                mission_id,
                "Inspect provenance only",
                "Read public provenance without mutation authority",
                MissionMode.inspect,
                "code-reviewer",
                allowed_actions=("fs_read",),
                scope=("tests/experiments",),
            )
            store.save_order(inspect_order)
            inspect_cannot_authorize = False
            try:
                service.issue_receipt(
                    mission_id=mission_id,
                    order_ids=(inspect_order.order_id,),
                    change_class="stewardship",
                    scope_paths=("tests/experiments/post_apex_integration_experiment.py",),
                )
            except PermissionError:
                inspect_cannot_authorize = True
            if not inspect_cannot_authorize:
                raise AssertionError("Inspect authority issued a source authorization receipt")

            return {
                "public_structure": PROVENANCE_PASS,
                "private_verification": verified.to_dict(),
                "missing_private_witness": missing.status,
                "class_downgrade": PROVENANCE_FAIL,
                "replay": replay.status,
                "inspect_cannot_authorize": inspect_cannot_authorize,
                "public_block_lines": len(block.splitlines()),
                "private_values_exposed": False,
            }
        finally:
            store.close()


def run() -> dict:
    health_context = health_reconstitution_context_evidence()
    drift = _run_operational_drift()
    if drift["finding"]["status"] != REGRESSION:
        raise AssertionError(drift)
    if not drift["baseline_unchanged"] or not drift["activation_blocked"]:
        raise AssertionError(drift)
    if drift["proposal_status"] != "proposed":
        raise AssertionError(drift)

    intake = external_intake_evidence()
    provenance = source_provenance_evidence()

    return {
        "schema": "grox-post-apex-evolution-001-integration-v1",
        "qualification_claim": False,
        "release_decision": False,
        "new_apex_stage": False,
        "health_reconstitution_context": health_context,
        "operational_drift": drift,
        "external_intake": intake,
        "source_provenance": provenance,
        "authority_boundary": {
            "standing_crew": health_context["clean_health"]["checks"][0]["evidence"]["standing_crew"],
            "gorxu_remains_sole_orchestrator": True,
            "health_is_read_only": health_context["health_read_only"],
            "degraded_state_forces_full_reconstitution": health_context["degraded_reconstitution"]["mode"] == FULL,
            "critical_context_preserved": health_context["context"]["required_fact_preservation"],
            "drift_cannot_self_activate": drift["activation_blocked"],
            "intake_creates_no_command_layer": not intake["creates_command_layer"],
            "inspect_cannot_issue_source_authority": provenance["inspect_cannot_authorize"],
        },
    }


if __name__ == "__main__":
    print("POST_APEX_INTEGRATION_EXPERIMENT_JSON=" + json.dumps(run(), sort_keys=True))