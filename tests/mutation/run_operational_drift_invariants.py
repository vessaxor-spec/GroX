#!/usr/bin/env python3
"""Mutation-prove Stage 5 operational-drift detectors.

Each mutation exists only in the CI checkout. The targeted regression must turn
red, then the production source must be restored byte-for-byte and the same
regression must return green.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "src/grox/operational_drift.py"


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
        "operational-provenance-only",
        "Controlled or synthetic trajectory evidence must not enter an operational drift window.",
        '            if provenance.get("source") != "canonical_private_mission_state":\n                raise ValueError(f"case {case_id} is not attributable operational Mission history")\n',
        '            if False:\n                raise ValueError(f"case {case_id} is not attributable operational Mission history")\n',
        "tests/unit/test_operational_drift.py::OperationalDriftTests::test_non_operational_case_cannot_enter_operational_window",
    ),
    Spec(
        "baseline-cannot-normalize-critical-failure",
        "A baseline containing a critical invariant failure must be UNKNOWN rather than accepted as normal.",
        '            if int((baseline_invariants.get("critical_totals") or {}).get(name, 0) or 0) > 0:\n                unknown.append(f"baseline contains critical invariant failure: {name}")\n',
        '            if False:\n                unknown.append(f"baseline contains critical invariant failure: {name}")\n',
        "tests/unit/test_operational_drift.py::OperationalDriftTests::test_baseline_with_critical_violation_is_unknown_not_normalized",
    ),
    Spec(
        "observed-critical-failure-first-class",
        "An observed critical invariant failure must independently force REGRESSION.",
        '            if int((observed_invariants.get("critical_totals") or {}).get(name, 0) or 0) > 0\n',
        '            if False\n',
        "tests/unit/test_operational_drift.py::OperationalDriftTests::test_critical_invariant_failure_cannot_hide_behind_good_averages",
    ),
    Spec(
        "stale-observation-unknown",
        "Observed evidence beyond the configured freshness bound must be UNKNOWN.",
        '                elif age > self.max_observed_age_seconds:\n                    reasons.append(\n',
        '                elif False:\n                    reasons.append(\n',
        "tests/unit/test_operational_drift.py::OperationalDriftTests::test_stale_observed_window_is_unknown",
    ),
    Spec(
        "window-binding-digest",
        "The digest binding the selected operational cases must be verified before comparison.",
        '        if config.get("window_sha256") != _sha(bindings):\n            reasons.append(f"{label} window binding digest mismatch")\n',
        '        if False:\n            reasons.append(f"{label} window binding digest mismatch")\n',
        "tests/unit/test_operational_drift.py::OperationalDriftTests::test_window_binding_digest_mismatch_is_unknown",
    ),
)


def run(nodeid: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", nodeid],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )


def target_failed(nodeid: str, cp: subprocess.CompletedProcess[str]) -> bool:
    output = cp.stdout + "\n" + cp.stderr
    leaf = nodeid.rsplit("::", 1)[-1]
    return cp.returncode != 0 and leaf in output and "failed" in output.lower()


def prove(spec: Spec) -> Result:
    original = TARGET.read_text(encoding="utf-8")
    count = original.count(spec.old)
    result = Result(spec.name, spec.invariant, spec.nodeid, count)
    if count != 1:
        result.detail = f"source drift: expected exactly one mutation seam, found {count}"
        return result
    try:
        TARGET.write_text(original.replace(spec.old, spec.new, 1), encoding="utf-8")
        red = run(spec.nodeid)
        result.red_returncode = red.returncode
        result.target_failed = target_failed(spec.nodeid, red)
    except Exception as exc:
        result.detail = f"mutation execution error: {type(exc).__name__}: {exc}"
    finally:
        TARGET.write_text(original, encoding="utf-8")
        result.restored_exact = TARGET.read_text(encoding="utf-8") == original

    if not result.restored_exact:
        result.detail = "failed to restore exact source bytes"
        return result
    green = run(spec.nodeid)
    result.restored_green = green.returncode == 0
    if result.target_failed and result.restored_green:
        result.status = "KILLED"
        result.detail = "target operational-drift regression red under mutation and green after exact restoration"
    elif not result.target_failed:
        result.status = "SURVIVED"
        result.detail = "target operational-drift detector did not fail under mutation"
    else:
        result.status = "RESTORE_FAILED"
        result.detail = "target operational-drift detector did not return green after restoration"
    return result


def main() -> int:
    results = []
    for spec in SPECS:
        result = prove(spec)
        results.append(result)
        print(f"OPERATIONAL_DRIFT_MUTATION {result.name}: {result.status} — {result.detail}")

    clean = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(TARGET.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    report = {
        "schema": "grox-operational-drift-invariant-mutations-v1",
        "mutations": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "killed": sum(result.status == "KILLED" for result in results),
            "survived": sum(result.status == "SURVIVED" for result in results),
            "other_failures": sum(result.status not in {"KILLED", "SURVIVED"} for result in results),
            "source_restored_clean": clean,
        },
    }
    print("OPERATIONAL_DRIFT_MUTATION_MATRIX_JSON=" + json.dumps(report, sort_keys=True))
    return 0 if all(result.status == "KILLED" for result in results) and clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
