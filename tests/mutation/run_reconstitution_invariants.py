#!/usr/bin/env python3
"""Mutation-prove Stage 3 tiered reconstitution safety decisions.

All weakened variants exist only in the CI checkout. Each mutation must turn its
specific production-path regression red, then exact source bytes are restored
and the same detector must return green. All cases run even after a failure.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TARGET = "src/grox/reconstitution.py"

@dataclass(frozen=True)
class Spec:
    name: str
    invariant: str
    old: str
    new: str
    nodeid: str

@dataclass
class Result:
    name: str
    invariant: str
    nodeid: str
    source_match_count: int
    red_returncode: int | None = None
    target_failed: bool = False
    restored_green: bool = False
    restored_exact: bool = False
    status: str = "ERROR"
    detail: str = ""

SPECS = (
    Spec(
        "fresh-host-full",
        "A fresh host must always select FULL reconstitution.",
        '        if fresh_host:\n            full_reasons.append("fresh host requires full source/state and recovery reconstitution")\n',
        '        if False and fresh_host:\n            full_reasons.append("fresh host requires full source/state and recovery reconstitution")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_fresh_host_forces_full_even_when_health_is_clean",
    ),
    Spec(
        "source-change-full",
        "Changed source must select FULL reconstitution.",
        '        if source_changed:\n            full_reasons.append("source changed since prior operating context")\n',
        '        if False and source_changed:\n            full_reasons.append("source changed since prior operating context")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_source_change_forces_full",
    ),
    Spec(
        "critical-health-full",
        "Critical health failure must select FULL reconstitution.",
        '        if critical_failures:\n            full_reasons.append(f"critical health failure(s): {\', \'.join(critical_failures)}")\n',
        '        if False and critical_failures:\n            full_reasons.append(f"critical health failure(s): {\', \'.join(critical_failures)}")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_critical_health_failure_forces_full",
    ),
    Spec(
        "inflight-state-full",
        "Active/interrupted/unresolved Mission state must select FULL recovery.",
        '        if inflight:\n            full_reasons.append(f"{inflight} active/interrupted/unresolved Mission or graph record(s) require full recovery")\n',
        '        if False and inflight:\n            full_reasons.append(f"{inflight} active/interrupted/unresolved Mission or graph record(s) require full recovery")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_interrupted_or_running_state_forces_full",
    ),
    Spec(
        "dirty-source-full",
        "Dirty/degraded source repository must not select FAST/TARGETED.",
        '        if source_repo and source_repo.status == WARN:\n            full_reasons.append("source repository is dirty or otherwise degraded")\n',
        '        if False and source_repo and source_repo.status == WARN:\n            full_reasons.append("source repository is dirty or otherwise degraded")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_dirty_source_forces_full",
    ),
    Spec(
        "persistence-warning-full",
        "Persistence WARN/FAIL must select FULL reconstitution.",
        '        if persistence and persistence.status in {FAIL, WARN}:\n            full_reasons.append(f"persistence readiness is {persistence.status}")\n',
        '        if False and persistence and persistence.status in {FAIL, WARN}:\n            full_reasons.append(f"persistence readiness is {persistence.status}")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_persistence_warning_forces_full",
    ),
    Spec(
        "mandatory-positive-evidence",
        "Missing/non-PASS mandatory health evidence must select FULL.",
        '        if not_positive:\n            full_reasons.append(f"mandatory health evidence not positively PASS: {\', \'.join(not_positive)}")\n',
        '        if False and not_positive:\n            full_reasons.append(f"mandatory health evidence not positively PASS: {\', \'.join(not_positive)}")\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_missing_mandatory_evidence_defaults_full",
    ),
    Spec(
        "unknown-source-not-fast",
        "UNKNOWN source repository evidence must not select FAST.",
        '        if source_repo is None or source_repo.status != PASS:\n',
        '        if False and (source_repo is None or source_repo.status != PASS):\n',
        "tests/unit/test_reconstitution.py::ReconstitutionPlannerTests::test_unknown_source_repository_selects_targeted_not_fast",
    ),
)

def run(nodeid: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "pytest", "-q", nodeid], cwd=ROOT, text=True, capture_output=True, timeout=180, check=False)

def target_failed(nodeid: str, cp: subprocess.CompletedProcess[str]) -> bool:
    output = cp.stdout + "\n" + cp.stderr
    leaf = nodeid.rsplit("::", 1)[-1]
    return cp.returncode != 0 and leaf in output and "failed" in output.lower()

def prove(spec: Spec) -> Result:
    path = ROOT / TARGET
    original = path.read_text(encoding="utf-8")
    count = original.count(spec.old)
    result = Result(spec.name, spec.invariant, spec.nodeid, count)
    if count != 1:
        result.detail = f"source drift: expected exactly one mutation seam, found {count}"
        return result
    try:
        path.write_text(original.replace(spec.old, spec.new, 1), encoding="utf-8")
        red = run(spec.nodeid)
        result.red_returncode = red.returncode
        result.target_failed = target_failed(spec.nodeid, red)
    except Exception as exc:
        result.detail = f"mutation execution error: {type(exc).__name__}: {exc}"
    finally:
        path.write_text(original, encoding="utf-8")
        result.restored_exact = path.read_text(encoding="utf-8") == original
    if not result.restored_exact:
        result.detail = "failed to restore exact source bytes"
        return result
    green = run(spec.nodeid)
    result.restored_green = green.returncode == 0
    if result.target_failed and result.restored_green:
        result.status = "KILLED"
        result.detail = "target reconstitution regression red under mutation and green after exact restoration"
    elif not result.target_failed:
        result.status = "SURVIVED"
        result.detail = "target reconstitution detector did not fail under mutation"
    else:
        result.status = "RESTORE_FAILED"
        result.detail = "target reconstitution detector did not return green after restoration"
    return result

def main() -> int:
    results = []
    for spec in SPECS:
        result = prove(spec)
        results.append(result)
        print(f"RECONSTITUTION_MUTATION {result.name}: {result.status} — {result.detail}")
    clean = subprocess.run(["git", "diff", "--exit-code", "--", TARGET], cwd=ROOT, text=True, capture_output=True, check=False).returncode == 0
    report = {
        "schema": "grox-reconstitution-invariant-mutations-v1",
        "mutations": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "killed": sum(result.status == "KILLED" for result in results),
            "survived": sum(result.status == "SURVIVED" for result in results),
            "other_failures": sum(result.status not in {"KILLED", "SURVIVED"} for result in results),
            "source_restored_clean": clean,
        },
    }
    print("RECONSTITUTION_MUTATION_MATRIX_JSON=" + json.dumps(report, sort_keys=True))
    return 0 if all(result.status == "KILLED" for result in results) and clean else 1

if __name__ == "__main__":
    raise SystemExit(main())
