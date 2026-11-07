"""NCI-4A synthetic-only case admission and write-once gold generation.

This is an evaluation substrate, not the operational A6 evaluation ledger or
a Mission/provider/trainer interface.  There is deliberately no automatic
private-Mission import, network access, model invocation, or tool execution.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
from typing import Any, Mapping

from .neural_crew_advice import NeuralCrewAdvice, NeuralCrewAdviceError


CASE_SCHEMA = "grox-nci4a-case-v1"
GENERATION_SCHEMA = "grox-nci4a-corpus-generation-v1"
_CASE_FIELDS = frozenset({
    "schema", "case_id", "task_class", "split", "features",
    "expected", "invariants", "provenance",
})
_FEATURE_FIELDS = frozenset({
    "observation_count", "test_requested", "test_status", "craft_present",
    "memory_present", "evidence_sufficient", "policy_denied",
})
_PROVENANCE_FIELDS = frozenset({
    "source_kind", "source_path", "source_sha256", "rights", "privacy_class",
})
_TASK_CLASSES = frozenset({
    "action_selection", "evidence_triage", "test_interpretation",
    "failure_triage", "stop_decision", "policy_denial",
})
_SOURCE_KINDS = frozenset({"synthetic_contract", "canonical_test", "verified_negative"})
_INVARIANTS = frozenset({
    "no_authority_widening", "read_only_inspect", "test_interpretation",
    "evidence_sufficiency", "stop_on_denial", "advice_schema",
})
_SPLITS = frozenset({"train", "gold"})
_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
_SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_MAX_CASES = 128


class NeuralCrewCorpusError(ValueError):
    """Corpus provenance, admission, split, or integrity violation."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(value: str | bytes) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode("utf-8")).hexdigest()


def _exact(raw: Any, fields: frozenset[str], name: str) -> None:
    if not isinstance(raw, Mapping) or set(raw) != fields:
        raise NeuralCrewCorpusError(f"{name} must contain exactly the declared fields")


def _identifier(value: Any, name: str) -> str:
    if type(value) is not str or _ID_PATTERN.fullmatch(value) is None:
        raise NeuralCrewCorpusError(f"{name} is not a valid bounded identifier")
    return value


def _reference(value: Any) -> str:
    if type(value) is not str or len(value) > 200 or "\\" in value:
        raise NeuralCrewCorpusError("provenance source_path is invalid")
    path = PurePosixPath(value)
    if (
        path.is_absolute() or ".." in path.parts or "." in path.parts
        or path.suffix != ".py"
        or not (value.startswith("src/grox/") or value.startswith("tests/"))
        or path.as_posix() != value
    ):
        raise NeuralCrewCorpusError("provenance must name a canonical Python source/test file")
    return value


class NeuralCrewCorpus:
    """Write-once generation manifests in GroX's existing private SQLite plane.

    The split is fixed per generation.  Every read is bound to an independently
    retained digest.  SQL triggers reject ordinary UPDATE/DELETE; source/code
    revisions and hostile database owners require external digest pinning.
    """

    def __init__(self, db: sqlite3.Connection, source_root: Path):
        if not isinstance(db, sqlite3.Connection):
            raise TypeError("db must be an existing SQLite connection")
        self.db = db
        self.source_root = Path(source_root).resolve(strict=True)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS nci4a_corpus_generations(
                generation_id TEXT PRIMARY KEY,
                manifest_json TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL
            )"""
        )
        self.db.execute(
            """CREATE TRIGGER IF NOT EXISTS nci4a_generations_no_update
               BEFORE UPDATE ON nci4a_corpus_generations
               BEGIN SELECT RAISE(ABORT, 'NCI-4A generation is write-once'); END"""
        )
        self.db.execute(
            """CREATE TRIGGER IF NOT EXISTS nci4a_generations_no_delete
               BEFORE DELETE ON nci4a_corpus_generations
               BEGIN SELECT RAISE(ABORT, 'NCI-4A generation is write-once'); END"""
        )
        self.db.commit()

    def _verify_source(self, provenance: Mapping[str, Any]) -> dict[str, str]:
        _exact(provenance, _PROVENANCE_FIELDS, "provenance")
        kind = provenance["source_kind"]
        if type(kind) is not str or kind not in _SOURCE_KINDS:
            raise NeuralCrewCorpusError("private, external, or unverified sources are not admitted")
        path = _reference(provenance["source_path"])
        digest = provenance["source_sha256"]
        if type(digest) is not str or _SHA_PATTERN.fullmatch(digest) is None:
            raise NeuralCrewCorpusError("provenance source digest must be SHA-256")
        if provenance["rights"] != "grox-owned" or provenance["privacy_class"] != "synthetic":
            raise NeuralCrewCorpusError("only GroX-owned synthetic evidence is admitted")
        try:
            source = (self.source_root / path).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise NeuralCrewCorpusError("provenance source file is not available") from exc
        if not source.is_relative_to(self.source_root) or not source.is_file():
            raise NeuralCrewCorpusError("provenance file leaves the declared source checkout")
        if _sha256(source.read_bytes()) != digest:
            raise NeuralCrewCorpusError("provenance source SHA-256 does not match checkout")
        return {key: provenance[key] for key in sorted(_PROVENANCE_FIELDS)}

    def _validate_case(self, raw: Any) -> dict[str, Any]:
        _exact(raw, _CASE_FIELDS, "case")
        if raw["schema"] != CASE_SCHEMA:
            raise NeuralCrewCorpusError("unsupported corpus case schema")
        cid = _identifier(raw["case_id"], "case_id")
        task_class = raw["task_class"]
        if type(task_class) is not str or task_class not in _TASK_CLASSES:
            raise NeuralCrewCorpusError("unsupported case task class")
        split = raw["split"]
        if type(split) is not str or split not in _SPLITS:
            raise NeuralCrewCorpusError("split must be train or gold")
        features = raw["features"]
        _exact(features, _FEATURE_FIELDS, "features")
        for key in (
            "test_requested", "craft_present", "memory_present",
            "evidence_sufficient", "policy_denied",
        ):
            if type(features[key]) is not bool:
                raise NeuralCrewCorpusError(f"feature {key} must be boolean")
        count = features["observation_count"]
        if type(count) is not int or not 0 <= count <= 8:
            raise NeuralCrewCorpusError("observation_count is outside the bounded range")
        if type(features["test_status"]) is not str or features["test_status"] not in {"not_run", "pass", "fail", "inconclusive"}:
            raise NeuralCrewCorpusError("invalid test_status")
        if features["policy_denied"] and features["evidence_sufficient"]:
            raise NeuralCrewCorpusError("policy denial cannot mark evidence sufficient")
        expected = raw["expected"]
        try:
            advice = NeuralCrewAdvice.from_mapping(expected)
        except (NeuralCrewAdviceError, TypeError, ValueError) as exc:
            raise NeuralCrewCorpusError("expected advice violates the v1 advisory contract") from exc
        if advice.evidence_sufficient != features["evidence_sufficient"]:
            raise NeuralCrewCorpusError("expected evidence sufficiency disagrees with input")
        if advice.test_interpretation != features["test_status"]:
            raise NeuralCrewCorpusError("expected test interpretation disagrees with input")
        if features["policy_denied"] and (
            advice.failure_classification != "policy_denied" or advice.continue_or_stop != "stop"
        ):
            raise NeuralCrewCorpusError("expected advice must stop on policy denial")
        invariants = raw["invariants"]
        if (
            type(invariants) is not list or not 1 <= len(invariants) <= len(_INVARIANTS)
            or any(type(i) is not str or i not in _INVARIANTS for i in invariants)
            or len(set(invariants)) != len(invariants)
        ):
            raise NeuralCrewCorpusError("case invariants must be unique known invariant IDs")
        return {
            "schema": CASE_SCHEMA, "case_id": cid, "task_class": task_class,
            "split": split, "features": {key: features[key] for key in sorted(_FEATURE_FIELDS)},
            "expected": advice.to_dict(), "invariants": sorted(invariants),
            "provenance": self._verify_source(raw["provenance"]),
        }

    def seal_generation(self, generation_id: str, cases: list[Mapping[str, Any]]) -> str:
        """Explicit admission/seal; never import sources or private state automatically."""
        generation_id = _identifier(generation_id, "generation_id")
        if type(cases) is not list or not 2 <= len(cases) <= _MAX_CASES:
            raise NeuralCrewCorpusError("generation requires 2 to 128 explicitly admitted cases")
        normalized = [self._validate_case(case) for case in cases]
        ids = [case["case_id"] for case in normalized]
        if len(ids) != len(set(ids)):
            raise NeuralCrewCorpusError("duplicate case identity")
        if {case["split"] for case in normalized} != _SPLITS:
            raise NeuralCrewCorpusError("generation requires disjoint train and gold partitions")
        normalized.sort(key=lambda case: case["case_id"])
        manifest = {
            "schema": GENERATION_SCHEMA,
            "generation_id": generation_id,
            "cases": normalized,
        }
        encoded = _canonical(manifest)
        digest = _sha256(encoded)
        existing = self.db.execute(
            "SELECT manifest_sha256 FROM nci4a_corpus_generations WHERE generation_id=?",
            (generation_id,),
        ).fetchone()
        if existing is not None:
            if existing[0] != digest:
                raise NeuralCrewCorpusError("sealed generation may not be replaced or repartitioned")
            self.read_generation(generation_id, expected_digest=digest)
            return digest
        with self.db:
            self.db.execute(
                "INSERT INTO nci4a_corpus_generations VALUES (?,?,?)",
                (generation_id, encoded, digest),
            )
        return digest

    def read_generation(self, generation_id: str, *, expected_digest: str) -> dict[str, Any]:
        """Fail closed if caller does not possess the pinned manifest commitment."""
        generation_id = _identifier(generation_id, "generation_id")
        if type(expected_digest) is not str or _SHA_PATTERN.fullmatch(expected_digest) is None:
            raise NeuralCrewCorpusError("a separately pinned generation SHA-256 is mandatory")
        row = self.db.execute(
            "SELECT manifest_json, manifest_sha256 FROM nci4a_corpus_generations WHERE generation_id=?",
            (generation_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown NCI-4A generation {generation_id}")
        encoded, stored_digest = row
        if stored_digest != expected_digest or _sha256(encoded) != expected_digest:
            raise NeuralCrewCorpusError("generation integrity/pinned SHA-256 mismatch")
        try:
            manifest = json.loads(encoded)
        except (TypeError, json.JSONDecodeError) as exc:
            raise NeuralCrewCorpusError("generation manifest is malformed") from exc
        if (
            not isinstance(manifest, dict)
            or set(manifest) != {"schema", "generation_id", "cases"}
            or manifest["schema"] != GENERATION_SCHEMA
            or manifest["generation_id"] != generation_id
            or type(manifest["cases"]) is not list
            or not 2 <= len(manifest["cases"]) <= _MAX_CASES
        ):
            raise NeuralCrewCorpusError("generation schema/identity mismatch")
        # A pinned manifest proves historical bytes, not that its source remains
        # present at this checkout revision. Recheck source provenance on *every*
        # read so trainer/evaluator access cannot silently accept stale sources.
        for case in manifest["cases"]:
            if not isinstance(case, dict) or not isinstance(case.get("provenance"), dict):
                raise NeuralCrewCorpusError("generation case provenance is malformed")
            self._verify_source(case["provenance"])
        return manifest

    def training_cases(self, generation_id: str, *, expected_digest: str) -> list[dict[str, Any]]:
        """The sole trainer-facing export; never return gold IDs or gold labels."""
        manifest = self.read_generation(generation_id, expected_digest=expected_digest)
        return [case for case in manifest["cases"] if case["split"] == "train"]

    def gold_cases_for_evaluation(
        self, generation_id: str, *, expected_digest: str
    ) -> list[dict[str, Any]]:
        """Evaluator-only export; not part of the trainer-facing interface."""
        manifest = self.read_generation(generation_id, expected_digest=expected_digest)
        return [case for case in manifest["cases"] if case["split"] == "gold"]

    def manifest_summary(self, generation_id: str, *, expected_digest: str) -> dict[str, Any]:
        manifest = self.read_generation(generation_id, expected_digest=expected_digest)
        return {
            "schema": GENERATION_SCHEMA,
            "generation_id": generation_id,
            "manifest_sha256": expected_digest,
            "train_count": sum(case["split"] == "train" for case in manifest["cases"]),
            "gold_count": sum(case["split"] == "gold" for case in manifest["cases"]),
            "admission": "explicit_synthetic_repo_backed_only",
            "training_or_activation": False,
        }
