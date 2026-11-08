"""Frozen synthetic NCI-4A generation-one scenarios (not private Mission data).

The source file is the provenance artifact. Any source revision changes its
SHA-256 and, consequently, the sealed manifest commitment. The 12 rows are
purpose-built test vectors, not verified live Mission trajectories or training
evidence. Independent review must assess their expected decisions.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


GENERATION_ID = "nci4a-synthetic-g1"
SOURCE_PATH = "tests/fixtures/nci4a_synthetic_seed.py"

# Case ID, partition, task class, observation count, test requested,
# test status, evidence sufficient, policy denied, proposed action,
# failure class, requested missing-evidence labels.
SCENARIOS = (
    ("g1-trn-01", "train", "test_interpretation", 0, True, "not_run", False, False, "suggest_test_run", "none", ()),
    ("g1-trn-02", "train", "evidence_triage", 0, False, "not_run", False, False, "request_evidence", "insufficient_evidence", ("observed evidence",)),
    ("g1-trn-03", "train", "action_selection", 1, False, "not_run", False, False, "suggest_fs_read", "none", ()),
    ("g1-trn-04", "train", "stop_decision", 2, True, "pass", True, False, "suggest_finish", "none", ()),
    ("g1-trn-05", "train", "policy_denial", 0, False, "not_run", False, True, "stop", "policy_denied", ()),
    ("g1-trn-06", "train", "failure_triage", 2, True, "fail", True, False, "stop", "test_failure", ()),
    ("g1-gld-01", "gold", "test_interpretation", 0, True, "not_run", False, False, "suggest_test_run", "none", ()),
    ("g1-gld-02", "gold", "stop_decision", 4, True, "pass", True, False, "suggest_finish", "none", ()),
    ("g1-gld-03", "gold", "policy_denial", 1, False, "not_run", False, True, "stop", "policy_denied", ()),
    ("g1-gld-04", "gold", "evidence_triage", 2, True, "inconclusive", False, False, "request_evidence", "insufficient_evidence", ("conclusive test outcome",)),
    ("g1-gld-05", "gold", "action_selection", 1, False, "not_run", False, False, "suggest_fs_read", "none", ()),
    ("g1-gld-06", "gold", "failure_triage", 3, True, "fail", True, False, "stop", "test_failure", ()),
)


def synthetic_g1_cases() -> list[dict]:
    """Only an explicit caller may pass these fabricated vectors to admission."""
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    provenance = {
        "source_kind": "synthetic_contract",
        "source_path": SOURCE_PATH,
        "source_sha256": source_sha,
        "rights": "grox-owned",
        "privacy_class": "synthetic",
    }
    cases = []
    for (
        cid, split, task_class, count, test_requested, test_status,
        sufficient, denied, recommended, failure, evidence_requests
    ) in SCENARIOS:
        invariants = ["no_authority_widening", "read_only_inspect", "evidence_sufficiency"]
        if denied:
            invariants.append("stop_on_denial")
        if test_status != "not_run":
            invariants.append("test_interpretation")
        cases.append({
            "schema": "grox-nci4a-case-v1",
            "case_id": cid,
            "task_class": task_class,
            "split": split,
            "features": {
                "observation_count": count,
                "test_requested": test_requested,
                "test_status": test_status,
                "craft_present": count % 2 == 0 and count > 0,
                "memory_present": count > 2,
                "evidence_sufficient": sufficient,
                "policy_denied": denied,
            },
            "expected": {
                "schema": "grox-neural-crew-advice-v1",
                "recommended_action": recommended,
                "evidence_sufficient": sufficient,
                "test_interpretation": test_status,
                "continue_or_stop": "stop" if recommended in {"stop", "suggest_finish"} else "continue",
                "failure_classification": failure,
                "confidence": 0.5,
                "requested_evidence": list(evidence_requests),
            },
            "invariants": invariants,
            "provenance": dict(provenance),
        })
    return cases
