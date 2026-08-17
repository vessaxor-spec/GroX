#!/usr/bin/env python3
"""Mutation-prove source-authorization provenance detectors.

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
TARGET = ROOT / "src/grox/source_provenance.py"


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
        "repair-order-required",
        "Only an explicit Repair Order may support a source authorization receipt.",
        '            if row["mode"] != "repair":\n                raise PermissionError(f"source provenance requires explicit Repair authority: {order_id}")\n',
        '            if False:\n                raise PermissionError(f"source provenance requires explicit Repair authority: {order_id}")\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_receipt_requires_real_repair_order_with_mutation_authority",
    ),
    Spec(
        "commitment-must-match",
        "A forged public commitment must fail private verification.",
        '        if not hmac.compare_digest(expected, receipt["commitment"]) or not hmac.compare_digest(expected, public.commitment):\n            return ProvenanceVerification(FAIL, "authorization commitment does not match the private witness", (public.receipt_id,))\n',
        '        if False:\n            return ProvenanceVerification(FAIL, "authorization commitment does not match the private witness", (public.receipt_id,))\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_forged_commitment_fails",
    ),
    Spec(
        "scope-cannot-widen",
        "Changed source paths outside every private receipt scope must fail verification.",
        '        if uncovered:\n            return ProvenanceVerification(FAIL, f"changed source paths exceed private authorization scope: {uncovered}", tuple(receipt_ids))\n',
        '        if False:\n            return ProvenanceVerification(FAIL, f"changed source paths exceed private authorization scope: {uncovered}", tuple(receipt_ids))\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_multiple_receipts_cover_independent_scopes_without_widening",
    ),
    Spec(
        "change-class-cannot-downgrade",
        "Public provenance cannot downgrade a stricter private change class.",
        '        if _CHANGE_CLASSES[public.change_class] < _CHANGE_CLASSES[receipt["change_class"]]:\n            return ProvenanceVerification(FAIL, "public change class weakens the private authorization class", (public.receipt_id,))\n',
        '        if False:\n            return ProvenanceVerification(FAIL, "public change class weakens the private authorization class", (public.receipt_id,))\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_change_class_cannot_be_downgraded",
    ),
    Spec(
        "missing-witness-unknown",
        "Unavailable private authorization evidence must be UNKNOWN rather than PASS.",
        '        if not row:\n            return ProvenanceVerification(UNKNOWN, "private authorization witness is unavailable", (public.receipt_id,))\n',
        '        if not row:\n            return ProvenanceVerification(PASS, "private authorization witness is unavailable", (public.receipt_id,))\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_missing_private_witness_is_unknown_not_pass",
    ),
    Spec(
        "consumed-receipt-cannot-replay",
        "A receipt consumed by one logical change cannot authorize another PR.",
        '        if receipt["consumed_pr"] is not None and int(receipt["consumed_pr"]) != int(pr_number):\n            return ProvenanceVerification(FAIL, "authorization receipt was already consumed by another change", (public.receipt_id,))\n',
        '        if False:\n            return ProvenanceVerification(FAIL, "authorization receipt was already consumed by another change", (public.receipt_id,))\n',
        "tests/unit/test_source_provenance.py::SourceProvenanceTest::test_consumed_receipt_cannot_be_replayed_on_another_pr",
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
        result.detail = "target source-provenance regression red under mutation and green after exact restoration"
    elif not result.target_failed:
        result.status = "SURVIVED"
        result.detail = "target source-provenance detector did not fail under mutation"
    else:
        result.status = "RESTORE_FAILED"
        result.detail = "target source-provenance detector did not return green after restoration"
    return result


def main() -> int:
    results = []
    for spec in SPECS:
        result = prove(spec)
        results.append(result)
        print(f"SOURCE_PROVENANCE_MUTATION {result.name}: {result.status} — {result.detail}")

    clean = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(TARGET.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    report = {
        "schema": "grox-source-provenance-invariant-mutations-v1",
        "mutations": [asdict(result) for result in results],
        "summary": {
            "total": len(results),
            "killed": sum(result.status == "KILLED" for result in results),
            "survived": sum(result.status == "SURVIVED" for result in results),
            "other_failures": sum(result.status not in {"KILLED", "SURVIVED"} for result in results),
            "source_restored_clean": clean,
        },
    }
    print("SOURCE_PROVENANCE_MUTATION_MATRIX_JSON=" + json.dumps(report, sort_keys=True))
    return 0 if all(result.status == "KILLED" for result in results) and clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
