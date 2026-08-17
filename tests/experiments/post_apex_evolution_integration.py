from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grox.context_heat import ContextHeatPolicy, ContextItem, HOT, WARM
from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.health import FAIL as HEALTH_FAIL, PASS as HEALTH_PASS, VesselHealth
from grox.reconstitution import FAST, FULL, ReconstitutionPlanner
from grox.source_provenance import FAIL as PROVENANCE_FAIL, PASS as PROVENANCE_PASS, UNKNOWN, SourceProvenanceService
from grox.state import StateStore
from tests.experiments.operational_drift_experiment import run as run_operational_drift


def _health_and_reconstitution() -> dict:
    clean_report = VesselHealth(ROOT).collect()
    clean_checks = {check.check_id: check for check in clean_report.checks}
    if clean_report.disposition != "HEALTHY":
        raise AssertionError(clean_report.to_dict())
    if clean_checks["command_integrity"].evidence.get("standing_crew") != 82:
        raise AssertionError(clean_checks["command_integrity"].to_dict())
    if clean_checks["authority_integrity"].status != HEALTH_PASS:
        raise AssertionError(clean_checks["authority_integrity"].to_dict())

    planner = ReconstitutionPlanner()
    fast = planner.plan(clean_report)
    if fast.mode != FAST or fast.planned_surface_count != 4 or fast.structural_reduction_ratio != 0.6:
        raise AssertionError(fast.to_dict())

    with tempfile.TemporaryDirectory() as td:
        fault_root = Path(td) / "vessel"
        shutil.copytree(
            ROOT,
            fault_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo", "grox.sqlite3"),
        )
        state_path = fault_root / "configs" / "state" / "grox.sqlite3"
        if state_path.exists():
            state_path.unlink()
        policy_path = fault_root / "configs" / "tool-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["version"] = 1
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

        fault_report = VesselHealth(fault_root).collect()
        fault_checks = {check.check_id: check for check in fault_report.checks}
        if fault_checks["authority_integrity"].status != HEALTH_FAIL:
            raise AssertionError(fault_checks["authority_integrity"].to_dict())
        if fault_checks["recovery_readiness"].status != HEALTH_FAIL:
            raise AssertionError(fault_checks["recovery_readiness"].to_dict())
        full = planner.plan(fault_report)
        if full.mode != FULL or full.planned_surface_count != full.full_surface_count:
            raise AssertionError(full.to_dict())
        if state_path.exists():
            raise AssertionError("read-only health/reconstitution inspection created operational state")

    return {
        "clean_disposition": clean_report.disposition,
        "standing_crew": clean_checks["command_integrity"].evidence.get("standing_crew"),
        "clean_reconstitution": fast.to_dict(),
        "fault_authority_status": fault_checks["authority_integrity"].status,
        "fault_recovery_status": fault_checks["recovery_readiness"].status,
        "fault_reconstitution": full.to_dict(),
        "inspection_created_state": False,
    }


def _context_heat() -> dict:
    intent = "Commander intent: qualify Program 001 without widening authority."
    authority = "Authority boundary: only an existing bounded Order can permit mutation."
    critical = "Critical evidence: unresolved authority failures must remain visible."
    warm_fact = "Approved decision: preserve evidence gates."
    items = (
        ContextItem(
            "intent",
            "commander_intent",
            intent,
            "mission:integration",
            active=True,
            critical=True,
            required_facts=(intent,),
        ),
        ContextItem(
            "authority",
            "authority",
            authority,
            "order:integration",
            active=True,
            critical=True,
            required_facts=(authority,),
        ),
        ContextItem(
            "critical",
            "critical_evidence",
            critical,
            "evidence:authority-fault",
            active=True,
            critical=True,
            required_facts=(critical,),
        ),
        ContextItem(
            "warm",
            "decision",
            "Long historical decision record with implementation detail that is not needed verbatim for the active tour.",
            "decision:program-001",
            summary=warm_fact,
            relevant=True,
            required_facts=(warm_fact,),
        ),
        ContextItem(
            "cold",
            "completed_history",
            "Re-derivable completed history that is not relevant to the current tour.",
            "history:completed",
        ),
    )
    policy = ContextHeatPolicy()
    pack = policy.pack(items)
    by_id = {item.item_id: item for item in pack.items}
    required = (intent, authority, critical, warm_fact)
    audit = policy.audit_preservation(pack, required)
    if not audit.passed:
        raise AssertionError(audit.to_dict())
    if by_id["intent"].heat != HOT or by_id["intent"].text != intent or by_id["intent"].compressed:
        raise AssertionError(by_id["intent"].to_dict())
    if by_id["authority"].heat != HOT or by_id["authority"].text != authority:
        raise AssertionError(by_id["authority"].to_dict())
    if by_id["critical"].heat != HOT or by_id["critical"].text != critical:
        raise AssertionError(by_id["critical"].to_dict())
    if by_id["warm"].heat != WARM or by_id["warm"].text != warm_fact or not by_id["warm"].compressed:
        raise AssertionError(by_id["warm"].to_dict())
    if "cold" not in pack.omitted_ids:
        raise AssertionError(pack.to_dict())
    if any(not item.provenance for item in pack.items):
        raise AssertionError("retained context lost provenance")

    return {
        "retained_ids": list(pack.retained_ids),
        "omitted_ids": list(pack.omitted_ids),
        "preservation": audit.to_dict(),
        "runtime_activation_claimed": False,
    }


def _external_intake_contract() -> dict:
    text = (ROOT / "docs" / "stewardship" / "EXTERNAL_CAPABILITY_INTAKE.md").read_text(encoding="utf-8")
    required = (
        "ADOPT",
        "ADAPT",
        "HARVEST",
        "REJECT",
        "Circular-novelty",
        "External intelligence never inherits GroX authority",
        "Do not create a separate decisions database",
        "ClaudX",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"external intake contract missing {missing}")
    if "Already native GroX capability; do not re-import or duplicate" not in text:
        raise AssertionError("circular architecture rejection is not preserved")
    return {
        "postures": ["ADOPT", "ADAPT", "HARVEST", "REJECT"],
        "circular_duplicate_rejected": True,
        "separate_authority_layer": False,
    }


def _source_provenance() -> dict:
    with tempfile.TemporaryDirectory() as td:
        state_path = Path(td) / "state.sqlite3"
        store = StateStore(state_path)
        try:
            service = SourceProvenanceService(store)
            mission_id = "MSN-integrated-provenance"
            store.create_mission(mission_id, "Qualify bounded source provenance", "repair", "high")
            order = MissionOrder.new(
                mission_id,
                "Qualify bounded source provenance",
                "Authorize only the bounded integration proof source paths",
                MissionMode.repair,
                "backend-engineer",
                required_capabilities=("repo_read", "fs_write"),
                allowed_actions=("fs_read", "fs_write", "test_run"),
                forbidden_actions=("mcp_mutate",),
                scope=(
                    "src/grox/source_provenance.py",
                    "tests/experiments/post_apex_evolution_integration.py",
                ),
                risk_class=RiskClass.high,
                evidence_requirements=("tests", "diff"),
                verification_requirements=("independent_verifier",),
            )
            store.save_order(order)
            receipt = service.issue_receipt(
                mission_id=mission_id,
                order_ids=[order.order_id],
                change_class="runtime",
                scope_paths=(
                    "src/grox/source_provenance.py",
                    "tests/experiments/post_apex_evolution_integration.py",
                ),
                operation="mixed",
            )
            block = service.render_public_block(receipt)
            for private_value in (mission_id, order.order_id, receipt["nonce_hex"], "backend-engineer"):
                if private_value in block:
                    raise AssertionError("public provenance leaked private witness data")

            changed_paths = (
                "src/grox/source_provenance.py",
                "tests/experiments/post_apex_evolution_integration.py",
            )
            pr_number = 999001
            head_sha = "a" * 40
            tree_sha = "b" * 40
            verified = service.verify_change(
                [block],
                changed_paths=changed_paths,
                pr_number=pr_number,
                head_sha=head_sha,
                tree_sha=tree_sha,
            )
            if verified.status != PROVENANCE_PASS:
                raise AssertionError(verified.to_dict())

            forged = block.replace(receipt["commitment"], "sha256:" + "0" * 64)
            if service.verify_change(
                [forged],
                changed_paths=changed_paths,
                pr_number=pr_number,
                head_sha=head_sha,
                tree_sha=tree_sha,
            ).status != PROVENANCE_FAIL:
                raise AssertionError("forged public commitment did not fail")
            if service.verify_change(
                [block],
                changed_paths=(*changed_paths, "README.md"),
                pr_number=pr_number,
                head_sha=head_sha,
                tree_sha=tree_sha,
            ).status != PROVENANCE_FAIL:
                raise AssertionError("out-of-scope source path did not fail")

            other = StateStore(Path(td) / "missing.sqlite3")
            try:
                missing = SourceProvenanceService(other).verify_change(
                    [block],
                    changed_paths=changed_paths,
                    pr_number=pr_number,
                    head_sha=head_sha,
                    tree_sha=tree_sha,
                )
            finally:
                other.close()
            if missing.status != UNKNOWN:
                raise AssertionError(missing.to_dict())

            canonical_commit = "c" * 40
            consumed = service.consume(
                receipt["receipt_id"],
                pr_number=pr_number,
                verified_head=head_sha,
                verified_tree=tree_sha,
                canonical_commit=canonical_commit,
            )
            if consumed["status"] != "consumed" or consumed["consumed_commit"] != canonical_commit:
                raise AssertionError(consumed)
            replay = service.verify_change(
                [block],
                changed_paths=changed_paths,
                pr_number=pr_number + 1,
                head_sha="d" * 40,
                tree_sha="e" * 40,
            )
            if replay.status != PROVENANCE_FAIL:
                raise AssertionError(replay.to_dict())

            return {
                "public_structure": service.validate_public_block(block).status,
                "private_verification": verified.status,
                "forgery": PROVENANCE_FAIL,
                "out_of_scope": PROVENANCE_FAIL,
                "missing_witness": missing.status,
                "consumed": consumed["status"],
                "replay": replay.status,
                "public_leaks_private_witness": False,
                "source_mutation_authority": False,
            }
        finally:
            store.close()


def run() -> dict:
    health = _health_and_reconstitution()
    context = _context_heat()
    intake = _external_intake_contract()
    drift = run_operational_drift()
    if drift["finding"]["status"] != "REGRESSION" or not drift["baseline_unchanged"]:
        raise AssertionError(drift)
    if drift["proposal_status"] != "proposed" or not drift["activation_blocked"]:
        raise AssertionError(drift)
    provenance = _source_provenance()

    result = {
        "schema": "grox-post-apex-evolution-program-001-integration-v1",
        "health_reconstitution": health,
        "context_heat": context,
        "external_intake": intake,
        "operational_drift": {
            "finding_status": drift["finding"]["status"],
            "baseline_unchanged": drift["baseline_unchanged"],
            "proposal_status": drift["proposal_status"],
            "activation_blocked": drift["activation_blocked"],
        },
        "source_provenance": provenance,
        "authority_widened": False,
        "passed": True,
    }
    return result


if __name__ == "__main__":
    print("POST_APEX_EVOLUTION_INTEGRATION_JSON=" + json.dumps(run(), sort_keys=True))
