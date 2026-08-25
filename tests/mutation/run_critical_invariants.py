#!/usr/bin/env python3
"""Prove critical GroX detectors by killing isolated production mutations.

This harness never commits weakened source. Each mutation is applied to the CI
checkout, its targeted production-path regression must turn red, the exact
original bytes are restored in a finally block, and the same regression must
then return green. All mutations run even if an earlier one is not killed so a
single broken detector cannot blind the rest of the proof surface.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class MutationSpec:
    name: str
    invariant: str
    path: str
    old: str
    new: str
    nodeid: str


@dataclass
class MutationResult:
    name: str
    invariant: str
    path: str
    nodeid: str
    source_match_count: int
    red_returncode: int | None = None
    target_failed: bool = False
    restored_green: bool = False
    restored_exact: bool = False
    status: str = "ERROR"
    detail: str = ""


SPECS: tuple[MutationSpec, ...] = (
    MutationSpec(
        name="source-state-binding",
        invariant="Snapshot restore must enforce source compatibility unless ancestor allowance is explicit.",
        path="src/grox/persistence.py",
        old="            enforce_source_binding=True,\n",
        new="            enforce_source_binding=False,\n",
        nodeid="tests/integration/test_persistence_planes.py::PersistencePlaneTests::test_restore_rejects_source_mismatch_without_explicit_ancestor_allowance",
    ),
    MutationSpec(
        name="semantic-orchestrator-admission",
        invariant="Semantic orchestrator identity variants must never enter Standing Crew.",
        path="src/grox/crew/roster.py",
        old='    return "orchestrator" in cid or "orchestrator" in normalized_title\n',
        new="    return False\n",
        nodeid="tests/contracts/test_command_spine.py::SpineTest::test_orchestrator_identity_variants_cannot_be_crew",
    ),
    MutationSpec(
        name="stale-crew-performance-purge",
        invariant="Reconstitution must purge stale Crew adaptive/performance state while preserving audit history.",
        path="src/grox/crew/roster.py",
        old='    store.db.execute(f"DELETE FROM crew_performance WHERE crew_id IN ({placeholders})", stale_ids)\n',
        new='    store.db.execute(f"SELECT crew_id FROM crew_performance WHERE crew_id IN ({placeholders})", stale_ids)\n',
        nodeid="tests/contracts/test_command_spine.py::SpineTest::test_reconstitution_purges_stale_crew_operational_state",
    ),
    MutationSpec(
        name="verifier-self-independence",
        invariant="An executor must never verify its own result.",
        path="src/grox/verification/core.py",
        old="        if executor_id==verifier_id: return False,'Verifier is not independent from executor'\n",
        new="        if False: return False,'Verifier is not independent from executor'\n",
        nodeid="tests/unit/test_verification.py::IndependentVerifierTests::test_same_executor_cannot_verify_own_result",
    ),
    MutationSpec(
        name="forged-graph-verification-filter",
        invariant="Crew-provided graph_verification evidence must be stripped before persistence or synthesis.",
        path="src/grox/graph/runtime.py",
        old='        result.evidence = [evidence for evidence in result.evidence if evidence.kind != "graph_verification"]\n',
        new="        result.evidence = list(result.evidence)\n",
        nodeid="tests/integration/test_apex_qualification.py::ApexQualificationGauntlet::test_non_verifier_cannot_forge_graph_verification_evidence",
    ),
    MutationSpec(
        name="hard-cost-budget-boundary",
        invariant="A Mission may spend exactly its budget but must stop before overspend.",
        path="src/grox/graph/runtime.py",
        old="                if spent_cost + reserved_cost + node_cost <= plan.budget.max_cost_units + 1e-12:\n",
        new="                if spent_cost + reserved_cost + node_cost < plan.budget.max_cost_units - 1e-12:\n",
        nodeid="tests/integration/test_apex_qualification.py::ApexQualificationGauntlet::test_fixed_mission_cost_budget_stops_before_overspend",
    ),
    MutationSpec(
        name="resume-committed-cost-reconstitution",
        invariant="Resume must reconstruct previously committed Mission cost before authorizing more work.",
        path="src/grox/graph/runtime.py",
        old="        spent_cost = self._committed_cost(mission_id)\n\n        unresolved_reason: str | None = None\n",
        new="        spent_cost = 0.0\n\n        unresolved_reason: str | None = None\n",
        nodeid="tests/integration/test_cost_recovery.py::CostRecoveryTests::test_resume_reconstitutes_committed_cost_before_spending",
    ),
    MutationSpec(
        name="graph-repair-authorization",
        invariant="Mission Graph Repair nodes require explicit GorXu mutation authorization.",
        path="src/grox/graph/runtime.py",
        old='        if any(n.mode is MissionMode.repair for n in plan.nodes) and not allow_repair:\n            raise GraphExecutionError("Mission Graph repair nodes require explicit Pilot mutation authorization")\n',
        new='        if False and any(n.mode is MissionMode.repair for n in plan.nodes) and not allow_repair:\n            raise GraphExecutionError("Mission Graph repair nodes require explicit Pilot mutation authorization")\n',
        nodeid="tests/integration/test_mission_graph.py::MissionGraphIntegrationTests::test_graph_repair_requires_explicit_mutation_authority",
    ),
    MutationSpec(
        name="tool-gateway-repair-boundary",
        invariant="Injected filesystem mutation grants remain unusable outside explicit Repair mode.",
        path="src/grox/tools/gateway.py",
        old='        if action in {"fs_write", "mcp_mutate"} and order.mode is not MissionMode.repair:\n            raise ToolDenied(f"{action} requires explicit Repair authority")\n',
        new='        if False and action in {"fs_write", "mcp_mutate"} and order.mode is not MissionMode.repair:\n            raise ToolDenied(f"{action} requires explicit Repair authority")\n',
        nodeid="tests/unit/test_gateway.py::GatewayTest::test_execute_write_denied_even_if_grant_is_injected",
    ),
    MutationSpec(
        name="critical-commander-escalation",
        invariant="Critical-risk exceptions must escalate to Commander rather than auto-recover.",
        path="src/grox/operations.py",
        old="        if risk is RiskClass.critical or irreversible or material_intent_change:\n",
        new="        if irreversible or material_intent_change:\n",
        nodeid="tests/integration/test_durable_operations.py::DurableOperationsIntegrationTests::test_critical_exception_escalates_to_commander_without_automatic_consultation",
    ),
    MutationSpec(
        name="unbound-vessel-fail-closed",
        invariant="An installed runtime outside a valid Vessel must refuse to fabricate an empty root.",
        path="src/grox/vessel.py",
        old='    raise VesselRootError(\n        "No GroX Vessel root found. Run from a GroX source checkout or set "\n        "GROX_VESSEL_ROOT to the checkout root. Refusing to start an empty Vessel."\n    )\n',
        new="    return Path(cwd or Path.cwd()).resolve()\n",
        nodeid="tests/unit/test_vessel_root.py::VesselRootTests::test_unbound_installed_runtime_refuses_empty_vessel",
    ),
    MutationSpec(
        name="live-resource-authorization-gate",
        invariant="A discovered, ready, and qualified resource must never be selected unless explicit policy also authorizes it.",
        path="src/grox/live_environment.py",
        old='            if not resource.authorized:\n                missing.append("not_authorized")\n',
        new='            if False and not resource.authorized:\n                missing.append("not_authorized")\n',
        nodeid="tests/unit/test_live_environment_awareness.py::LiveEnvironmentAwarenessTests::test_selection_uses_only_policy_order_and_requires_every_gate",
    ),
    MutationSpec(
        name="tool-capability-mission-authorization",
        invariant="Host-enabled or ready Tool Gateway capability state must never imply Mission authorization without sealed Order context.",
        path="src/grox/tool_awareness.py",
        old='            if order is None:\n                return requested, False, "no_mission_context"\n',
        new='            if order is None:\n                return requested, True, "no_mission_context"\n',
        nodeid="tests/unit/test_tool_capability_awareness.py::ToolCapabilityAwarenessTests::test_host_ready_never_implies_mission_authorization",
    ),
    MutationSpec(
        name="hosted-cognition-authorization-gate",
        invariant="A bound or structurally ready hosted cognition provider must never become authorized without explicit exact-resource policy.",
        path="src/grox/cognition_awareness.py",
        old='        authorized = resource_id in policy.authorized_ids if policy is not None else False\n',
        new='        authorized = True if policy is None else resource_id in policy.authorized_ids\n',
        nodeid="tests/unit/test_cognition_provider_awareness.py::CognitionProviderAwarenessTests::test_bound_session_provider_is_discovered_selected_but_not_authorized_or_observed",
    ),
    MutationSpec(
        name="cognition-transport-presealed-authority",
        invariant="Remote cognition transport awareness must never acquire authority by allowing the Tool Gateway to seal an unsealed Mission Order.",
        path="src/grox/cognition_awareness.py",
        old='        if not order.sealed:\n            raise CognitionTransportAuthorizationError("transport refresh requires an already sealed Mission Order")\n',
        new='        if False and not order.sealed:\n            raise CognitionTransportAuthorizationError("transport refresh requires an already sealed Mission Order")\n',
        nodeid="tests/unit/test_cognition_transport_freshness.py::CognitionTransportFreshnessTests::test_unsealed_order_is_rejected_without_becoming_sealed",
    ),
    MutationSpec(
        name="cognition-transport-origin-binding",
        invariant="Remote cognition transport evidence must remain bound to the exact currently configured origin.",
        path="src/grox/cognition_awareness.py",
        old="        if observed_origin != current_origin:\n",
        new="        if False and observed_origin != current_origin:\n",
        nodeid="tests/unit/test_cognition_transport_freshness.py::CognitionTransportFreshnessTests::test_same_resource_identity_endpoint_rebind_invalidates_prior_origin_evidence",
    ),
    MutationSpec(
        name="cognition-endpoint-exact-binding",
        invariant="Remote cognition endpoint-surface refresh must remain bound to the exact currently configured endpoint.",
        path="src/grox/cognition_awareness.py",
        old='        if order.parameters.get("endpoint") != endpoint:\n            raise CognitionEndpointAuthorizationError("sealed Mission Order does not bind this cognition endpoint")\n',
        new='        if False and order.parameters.get("endpoint") != endpoint:\n            raise CognitionEndpointAuthorizationError("sealed Mission Order does not bind this cognition endpoint")\n',
        nodeid="tests/unit/test_cognition_endpoint_freshness.py::CognitionEndpointFreshnessTests::test_exact_endpoint_authority_is_required",
    ),
    MutationSpec(
        name="configured-cognition-discovery-state-separation",
        invariant="Configured cognition discovery must never imply readiness before an independently qualified readiness check.",
        path="src/grox/cognition_discovery.py",
        old='            "ready": False,\n',
        new='            "ready": True,\n',
        nodeid="tests/unit/test_configured_cognition_discovery.py::ConfiguredCognitionDiscoveryTests::test_supported_openai_configuration_is_discovered_only",
    ),
    MutationSpec(
        name="configured-connection-exact-resource-binding",
        invariant="Configured remote connection authorization must remain bound to the exact discovered resource identity.",
        path="src/grox/configured_connection_awareness.py",
        old='        elif parameters.get("resource_id") != resource_id:\n',
        new='        elif False and parameters.get("resource_id") != resource_id:\n',
        nodeid="tests/unit/test_configured_connection_policy_awareness.py::ConfiguredConnectionPolicyAwarenessTests::test_wrong_resource_id_never_authorizes_connection",
    ),
    MutationSpec(
        name="configured-local-readiness-authorization-separation",
        invariant="Configured local cognition readiness must never imply Mission authorization.",
        path="src/grox/configured_local_readiness.py",
        old='            "authorized": False,\n',
        new='            "authorized": True,\n',
        nodeid="tests/unit/test_configured_local_readiness.py::ConfiguredLocalCognitionReadinessTests::test_ready_state_never_implies_authorization",
    ),
    MutationSpec(
        name="secret-alias-exact-binding",
        invariant="Secret-alias availability must remain bound to the exact requested alias rather than any broker secret.",
        path="src/grox/tools/secrets.py",
        old='        return isinstance(alias, str) and bool(alias) and alias in self._secrets\n',
        new='        return isinstance(alias, str) and bool(alias) and bool(self._secrets)\n',
        nodeid="tests/unit/test_secret_alias_awareness.py::SecretAliasAwarenessTests::test_absent_alias_fails_closed_without_enumerating_other_aliases",
    ),
    MutationSpec(
        name="configured-credential-binding-exact-resource",
        invariant="Configured credential-alias binding must preserve the exact configured cognition resource identity.",
        path="src/grox/credential_binding.py",
        old='            "resource_id": resource["resource_id"],\n',
        new='            "resource_id": "cognition:configured:openai:wrong-binding",\n',
        nodeid="tests/unit/test_configured_credential_binding.py::ConfiguredCredentialBindingTests::test_valid_remote_binding_preserves_exact_resource_identity",
    ),
    MutationSpec(
        name="ci-action-immutable-pin",
        invariant="Third-party GitHub Actions must remain pinned to immutable full commit SHAs.",
        path=".github/workflows/ci.yml",
        old="        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1\n      - name: Set up Python\n        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0\n        with:\n          python-version: ${{ matrix.python-version }}\n",
        new="        uses: actions/checkout@v7 # deliberate mutation\n      - name: Set up Python\n        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0\n        with:\n          python-version: ${{ matrix.python-version }}\n",
        nodeid="tests/contracts/test_ci_supply_chain.py::CISupplyChainTest::test_external_actions_are_pinned_to_full_commit_sha",
    ),
)


def run_pytest(nodeid: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", nodeid],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )


def target_failed(nodeid: str, completed: subprocess.CompletedProcess[str]) -> bool:
    output = f"{completed.stdout}\n{completed.stderr}"
    leaf = nodeid.rsplit("::", 1)[-1]
    return completed.returncode != 0 and leaf in output and "failed" in output.lower()


def prove(spec: MutationSpec) -> MutationResult:
    path = ROOT / spec.path
    original = path.read_text(encoding="utf-8")
    count = original.count(spec.old)
    result = MutationResult(
        name=spec.name,
        invariant=spec.invariant,
        path=spec.path,
        nodeid=spec.nodeid,
        source_match_count=count,
    )
    if count != 1:
        result.detail = f"source drift: expected exactly one mutation seam, found {count}"
        return result

    mutated = original.replace(spec.old, spec.new, 1)
    red: subprocess.CompletedProcess[str] | None = None
    try:
        path.write_text(mutated, encoding="utf-8")
        red = run_pytest(spec.nodeid)
        result.red_returncode = red.returncode
        result.target_failed = target_failed(spec.nodeid, red)
    except Exception as exc:  # keep running remaining proofs
        result.detail = f"mutation execution error: {type(exc).__name__}: {exc}"
    finally:
        path.write_text(original, encoding="utf-8")
        result.restored_exact = path.read_text(encoding="utf-8") == original

    if not result.restored_exact:
        result.detail = "failed to restore exact source bytes"
        return result

    green = run_pytest(spec.nodeid)
    result.restored_green = green.returncode == 0

    if result.target_failed and result.restored_green:
        result.status = "KILLED"
        result.detail = "target regression went red under mutation and green after exact restoration"
    elif not result.target_failed:
        output = ""
        if red is not None:
            output = (red.stdout + "\n" + red.stderr)[-1200:].replace("\n", " | ")
        result.status = "SURVIVED"
        result.detail = f"target detector did not fail for the intended target; tail={output}"
    else:
        result.status = "RESTORE_FAILED"
        result.detail = (green.stdout + "\n" + green.stderr)[-1200:].replace("\n", " | ")
    return result


def source_diff_clean(paths: Iterable[str]) -> bool:
    cp = subprocess.run(
        ["git", "diff", "--exit-code", "--", *sorted(set(paths))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if cp.returncode != 0:
        print(cp.stdout)
        print(cp.stderr, file=sys.stderr)
    return cp.returncode == 0


def main() -> int:
    results: list[MutationResult] = []
    for spec in SPECS:
        result = prove(spec)
        results.append(result)
        print(f"MUTATION {result.name}: {result.status} — {result.detail}")

    clean = source_diff_clean(spec.path for spec in SPECS)
    report = {
        "schema": "grox-critical-invariant-mutations-v1",
        "mutations": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "killed": sum(result.status == "KILLED" for result in results),
            "survived": sum(result.status == "SURVIVED" for result in results),
            "other_failures": sum(result.status not in {"KILLED", "SURVIVED"} for result in results),
            "source_restored_clean": clean,
        },
    }
    print("MUTATION_MATRIX_JSON=" + json.dumps(report, sort_keys=True))
    all_killed = all(result.status == "KILLED" for result in results)
    return 0 if all_killed and clean else 1


if __name__ == "__main__":
    raise SystemExit(main())