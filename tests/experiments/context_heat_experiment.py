#!/usr/bin/env python3
"""Controlled Stage 4 experiment for GroX context heat and bounded compression.

This is evidence generation, not Pilot runtime wiring. It measures exact
character retention/reduction and preservation of declared critical facts and
provenance across representative Mission/reconstitution scenarios.
"""
from __future__ import annotations

import json
from time import perf_counter_ns

from grox.context_heat import ContextHeatPolicy, ContextItem


def scenario_long_mission():
    required = (
        "INTENT: inspect the Vessel without widening authority",
        "AUTHORITY: Inspect only; fs_write forbidden",
        "STATE: verify-2 pending after implementation completed",
        "CONTRADICTION: Crew A says safe; Crew B says source binding unproven",
        "NEXT: resolve contradiction before synthesis",
    )
    items = [
        ContextItem("intent", "commander_intent", required[0], "MSN-LONG", active=True),
        ContextItem("authority", "authority", required[1], "ORD-LONG", active=True),
        ContextItem("state", "active_graph_state", required[2], "GR-LONG", active=True),
        ContextItem("conflict", "unresolved_contradiction", required[3], "EVID-A+B", active=True),
        ContextItem("next", "next_action", required[4], "GR-LONG", active=True),
        ContextItem("finding-1", "crew_finding", "Crew finding raw: " + "gateway evidence repeated " * 35, "EVID-11", summary="Finding: gateway remained fail-closed.", relevant=True),
        ContextItem("finding-2", "crew_finding", "Crew finding raw: " + "recovery evidence repeated " * 30, "EVID-12", summary="Finding: recovery preserved committed work.", relevant=True),
        ContextItem("old-tool", "raw_tool_output", "old raw command output " * 120, "TOOL-OLD"),
        ContextItem("superseded-chat", "superseded_discussion", "superseded design branch " * 80, "CHAT-OLD"),
    ]
    return "long_mission", items, required


def scenario_reconstitution():
    required = (
        "INTENT: resume only from committed safe state",
        "CONSTRAINT: unrelated-source snapshot restore must fail closed",
        "SOURCE: canonical main is verified",
        "AUTHORITY: recovery does not grant Repair",
    )
    items = [
        ContextItem("intent", "commander_intent", required[0], "VESSEL", active=True),
        ContextItem("old-safety", "relevant_history", required[1], "SHIPLOG-RECOVERY", critical=True),
        ContextItem("source", "critical_evidence", required[2], "GIT-HEAD", active=True),
        ContextItem("authority", "authority", required[3], "POLICY", active=True),
        ContextItem("recent-decision", "decision", "Recovery decision raw: " + "compatibility rationale " * 35, "SHIPLOG-RECENT", summary="Decision: exact source match restores normally; ancestor requires explicit allowance.", relevant=True),
        ContextItem("old-suite", "raw_tool_output", "historical regression output " * 100, "CI-OLD"),
        ContextItem("old-doc", "rederivable_source", "old source documentation excerpt " * 75, "GIT-OLD"),
    ]
    return "reconstitution", items, required


def scenario_adversarial_old_fact():
    required = (
        "SAFETY: never expose private raw runtime state in public Git",
        "INTENT: optimize context only if safety survives",
    )
    items = [
        ContextItem("intent", "commander_intent", required[1], "MSN-ADV", active=True),
        ContextItem("ancient-safety", "relevant_history", required[0], "SHIPLOG-ANCIENT", critical=True, summary="old note"),
        ContextItem("recent-noise", "raw_tool_output", "recent but re-derivable output " * 90, "TOOL-RECENT"),
        ContextItem("old-noise", "superseded_discussion", "ancient superseded prose " * 90, "CHAT-ANCIENT"),
    ]
    return "adversarial_old_safety", items, required


def scenario_warm_without_safe_summary():
    required = (
        "INTENT: preserve unresolved evidence exactly",
        "DECISION: relevant decision has no safe summary",
    )
    items = [
        ContextItem("intent", "commander_intent", required[0], "MSN-WARM", active=True),
        ContextItem("decision", "decision", required[1] + "; " + "supporting rationale " * 25, "DEC-NOSUM", relevant=True, required_facts=(required[1],)),
        ContextItem("cold", "raw_tool_output", "re-derivable diagnostics " * 60, "RAW-WARM"),
    ]
    return "warm_without_summary", items, required


def main() -> int:
    policy = ContextHeatPolicy()
    scenarios = [
        scenario_long_mission(),
        scenario_reconstitution(),
        scenario_adversarial_old_fact(),
        scenario_warm_without_safe_summary(),
    ]
    results = []
    total_original = total_packed = 0
    preservation_ok = True
    start = perf_counter_ns()
    for name, items, required in scenarios:
        pack = policy.pack(items)
        audit = policy.audit_preservation(pack, required)
        preservation_ok = preservation_ok and audit.passed
        total_original += pack.original_chars
        total_packed += pack.packed_chars
        results.append({
            "scenario": name,
            "original_chars": pack.original_chars,
            "packed_chars": pack.packed_chars,
            "reduction_ratio": pack.reduction_ratio,
            "retained_items": len(pack.items),
            "omitted_items": len(pack.omitted_ids),
            "required_fact_preservation": audit.passed,
            "missing_required_facts": list(audit.missing_required_facts),
            "retained_provenance": all(bool(item.provenance) for item in pack.items),
        })
    elapsed_ns = perf_counter_ns() - start
    aggregate_reduction = round((total_original - total_packed) / total_original, 4) if total_original else 0.0
    report = {
        "schema": "grox-context-heat-experiment-v1",
        "runtime_activation": False,
        "scenarios": results,
        "aggregate": {
            "original_chars": total_original,
            "packed_chars": total_packed,
            "reduction_ratio": aggregate_reduction,
            "required_fact_preservation": preservation_ok,
            "all_retained_items_have_provenance": all(row["retained_provenance"] for row in results),
            "experiment_elapsed_ns": elapsed_ns,
        },
    }
    print("CONTEXT_HEAT_EXPERIMENT_JSON=" + json.dumps(report, sort_keys=True))

    # The controlled corpus must show material reduction while preserving every
    # declared critical fact. This threshold is a GroX experiment gate, not an
    # external benchmark target or a promise about production token savings.
    ok = (
        preservation_ok
        and report["aggregate"]["all_retained_items_have_provenance"]
        and aggregate_reduction >= 0.50
        and all(row["required_fact_preservation"] for row in results)
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
