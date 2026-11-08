from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from grox.neural_crew_advice import SCHEMA as ADVICE_SCHEMA
from grox.neural_crew_corpus import (
    CASE_SCHEMA, GENERATION_SCHEMA, NeuralCrewCorpus, NeuralCrewCorpusError,
)


class NeuralCrewCorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = self.root / "tests" / "unit" / "source_case.py"
        source.parent.mkdir(parents=True)
        source.write_text("x = 1\n", encoding="utf-8")
        self.provenance = {
            "source_kind": "canonical_test",
            "source_path": "tests/unit/source_case.py",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "rights": "grox-owned",
            "privacy_class": "synthetic",
        }
        self.db_path = self.root / "private-state.sqlite3"
        self.db = sqlite3.connect(self.db_path)
        self.corpus = NeuralCrewCorpus(self.db, self.root)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def case(self, cid: str, split: str) -> dict:
        denied = split == "gold"
        return {
            "schema": CASE_SCHEMA, "case_id": cid, "task_class": "policy_denial" if denied else "test_interpretation",
            "split": split,
            "features": {
                "observation_count": 0, "test_requested": True,
                "test_status": "not_run", "craft_present": False,
                "memory_present": False, "evidence_sufficient": False,
                "policy_denied": denied,
            },
            "expected": {
                "schema": ADVICE_SCHEMA,
                "recommended_action": "stop" if denied else "suggest_test_run",
                "evidence_sufficient": False,
                "test_interpretation": "not_run",
                "continue_or_stop": "stop" if denied else "continue",
                "failure_classification": "policy_denied" if denied else "none",
                "confidence": 0.75,
                "requested_evidence": [],
            },
            "invariants": ["no_authority_widening", "read_only_inspect", "stop_on_denial"],
            "provenance": copy.deepcopy(self.provenance),
        }

    def pair(self):
        return [self.case("case-gold", "gold"), self.case("case-train", "train")]

    def seal(self):
        return self.corpus.seal_generation("generation-001", self.pair())

    def test_explicit_admission_seals_deterministic_write_once_generation(self):
        digest = self.seal()
        self.assertEqual(len(digest), 64)
        self.assertEqual(self.corpus.seal_generation("generation-001", list(reversed(self.pair()))), digest)
        summary = self.corpus.manifest_summary("generation-001", expected_digest=digest)
        self.assertEqual(summary["schema"], GENERATION_SCHEMA)
        self.assertEqual(summary["manifest_sha256"], digest)
        self.assertEqual((summary["train_count"], summary["gold_count"]), (1, 1))
        self.assertFalse(summary["training_or_activation"])
        row = self.db.execute(
            "SELECT manifest_sha256 FROM nci4a_corpus_generations WHERE generation_id='generation-001'"
        ).fetchone()
        self.assertEqual(row[0], digest)

    def test_gold_cannot_leak_into_trainer_facing_export(self):
        digest = self.seal()
        training = self.corpus.training_cases("generation-001", expected_digest=digest)
        gold = self.corpus.gold_cases_for_evaluation("generation-001", expected_digest=digest)
        self.assertEqual([case["case_id"] for case in training], ["case-train"])
        self.assertEqual([case["case_id"] for case in gold], ["case-gold"])
        self.assertNotIn("case-gold", json.dumps(training))
        self.assertFalse(any(case["features"]["policy_denied"] for case in training))
        self.assertNotIn('"failure_classification": "policy_denied"', json.dumps(training))
        self.assertEqual(gold[0]["expected"]["recommended_action"], "stop")
        self.assertEqual(training[0]["expected"]["recommended_action"], "suggest_test_run")

    def test_same_generation_cannot_replace_gold_or_move_it_to_train(self):
        digest = self.seal()
        altered = self.pair()
        altered[0]["split"] = "train"
        altered[1]["split"] = "gold"
        with self.assertRaisesRegex(NeuralCrewCorpusError, "may not be replaced"):
            self.corpus.seal_generation("generation-001", altered)
        self.assertEqual(self.corpus.training_cases("generation-001", expected_digest=digest)[0]["case_id"], "case-train")

    def test_update_delete_are_rejected_by_database_triggers(self):
        digest = self.seal()
        for sql in (
            "UPDATE nci4a_corpus_generations SET manifest_json='{}' WHERE generation_id='generation-001'",
            "DELETE FROM nci4a_corpus_generations WHERE generation_id='generation-001'",
        ):
            with self.subTest(sql=sql):
                with self.assertRaisesRegex(sqlite3.DatabaseError, "write-once"):
                    self.db.execute(sql)
                self.db.rollback()
        self.assertEqual(self.corpus.read_generation("generation-001", expected_digest=digest)["generation_id"], "generation-001")

    def test_replace_cannot_overwrite_sealed_generation_with_recursive_triggers_off(self):
        digest = self.seal()
        original = self.db.execute(
            "SELECT manifest_json, manifest_sha256 FROM nci4a_corpus_generations WHERE generation_id=?",
            ("generation-001",),
        ).fetchone()
        previous_setting = self.db.execute("PRAGMA recursive_triggers").fetchone()[0]
        self.db.execute("PRAGMA recursive_triggers=OFF")
        try:
            for command in ("INSERT OR REPLACE", "REPLACE"):
                with self.subTest(command=command):
                    try:
                        with self.assertRaisesRegex(sqlite3.DatabaseError, "write-once"):
                            self.db.execute(
                                f"{command} INTO nci4a_corpus_generations "
                                "(generation_id, manifest_json, manifest_sha256) VALUES (?,?,?)",
                                ("generation-001", '{"schema":"forged"}', "0" * 64),
                            )
                    finally:
                        self.db.rollback()
                    self.assertEqual(
                        self.db.execute(
                            "SELECT manifest_json, manifest_sha256 FROM nci4a_corpus_generations WHERE generation_id=?",
                            ("generation-001",),
                        ).fetchone(),
                        original,
                    )
            self.assertEqual(
                self.corpus.read_generation("generation-001", expected_digest=digest)["generation_id"],
                "generation-001",
            )
        finally:
            self.db.execute(f"PRAGMA recursive_triggers={previous_setting}")

    def test_external_pin_detects_tamper_even_if_database_owner_disables_triggers(self):
        digest = self.seal()
        self.db.execute("DROP TRIGGER nci4a_generations_no_update")
        changed = '{"schema":"forged","generation_id":"generation-001","cases":[]}'
        forged_digest = hashlib.sha256(changed.encode("utf-8")).hexdigest()
        self.db.execute(
            "UPDATE nci4a_corpus_generations SET manifest_json=?, manifest_sha256=? WHERE generation_id=?",
            (changed, forged_digest, "generation-001"),
        )
        self.db.commit()
        with self.assertRaisesRegex(NeuralCrewCorpusError, "pinned SHA-256 mismatch"):
            self.corpus.read_generation("generation-001", expected_digest=digest)

    def test_reopen_preserves_exact_split_and_digest(self):
        digest = self.seal()
        self.db.close()
        self.db = sqlite3.connect(self.db_path)
        self.corpus = NeuralCrewCorpus(self.db, self.root)
        self.assertEqual(len(self.corpus.training_cases("generation-001", expected_digest=digest)), 1)
        self.assertEqual(len(self.corpus.gold_cases_for_evaluation("generation-001", expected_digest=digest)), 1)

    def test_pinned_generation_rechecks_source_at_each_training_and_gold_read(self):
        digest = self.seal()
        source = self.root / "tests" / "unit" / "source_case.py"
        source.write_text("x = 2\n", encoding="utf-8")
        for load in (
            self.corpus.training_cases,
            self.corpus.gold_cases_for_evaluation,
            self.corpus.read_generation,
        ):
            with self.subTest(load=load.__name__):
                with self.assertRaisesRegex(NeuralCrewCorpusError, "source SHA-256"):
                    load("generation-001", expected_digest=digest)
        source.write_text("x = 1\n", encoding="utf-8")
        self.assertEqual(len(self.corpus.training_cases("generation-001", expected_digest=digest)), 1)
        source.unlink()
        with self.assertRaisesRegex(NeuralCrewCorpusError, "source file is not available"):
            self.corpus.gold_cases_for_evaluation("generation-001", expected_digest=digest)

    def test_wrong_pin_and_missing_generation_refuse_load(self):
        digest = self.seal()
        for bad in ("0" * 64, "", None, "not-a-hash"):
            with self.subTest(bad=bad):
                with self.assertRaises(NeuralCrewCorpusError):
                    self.corpus.training_cases("generation-001", expected_digest=bad)
        with self.assertRaises(KeyError):
            self.corpus.read_generation("missing", expected_digest=digest)

    def test_implicit_private_or_unverified_sources_are_denied(self):
        for invalid in ("commander_conversation", "private_trace", "verified_mission", "external_model", "unverified_trace"):
            with self.subTest(kind=invalid):
                cases = self.pair()
                cases[0]["provenance"]["source_kind"] = invalid
                with self.assertRaises(NeuralCrewCorpusError):
                    self.corpus.seal_generation("attempt", cases)
        for key, value in (
            ("rights", "public-web"),
            ("privacy_class", "restricted"),
            ("source_sha256", "a" * 64),
            ("source_path", "../configs/state/grox.sqlite3"),
            ("source_path", "tests/unit/missing.py"),
            ("source_path", "/tmp/leak.py"),
        ):
            with self.subTest(key=key):
                cases = self.pair()
                cases[0]["provenance"][key] = value
                with self.assertRaises((NeuralCrewCorpusError, FileNotFoundError)):
                    self.corpus.seal_generation("attempt", cases)

    def test_case_schema_rejects_authority_fields_and_raw_private_text(self):
        for modification in (
            lambda case: case.update(allowed_actions=["fs_write"]),
            lambda case: case["features"].update(mission_order={"mode": "repair"}),
            lambda case: case["features"].update(commander_message="private"),
            lambda case: case["expected"].update(tool_parameters={"path": "."}),
            lambda case: case["provenance"].update(origin="untrusted"),
            lambda case: case.update(task_class="self_training"),
        ):
            with self.subTest(modification=modification):
                cases = self.pair()
                modification(cases[0])
                with self.assertRaises(NeuralCrewCorpusError):
                    self.corpus.seal_generation("attempt", cases)

    def test_features_and_expected_labels_must_agree(self):
        for change in (
            lambda case: case["features"].update(observation_count=True),
            lambda case: case["features"].update(observation_count=999),
            lambda case: case["features"].update(test_status="injected"),
            lambda case: case["expected"].update(evidence_sufficient=True),
            lambda case: case["expected"].update(test_interpretation="fail"),
            lambda case: case["features"].update(policy_denied=True),
            lambda case: case["invariants"].append("malicious_invariant"),
            lambda case: case["invariants"].append("stop_on_denial"),
        ):
            with self.subTest(change=change):
                cases = self.pair()
                change(cases[1])
                with self.assertRaises(NeuralCrewCorpusError):
                    self.corpus.seal_generation("attempt", cases)

    def test_frozen_synthetic_generation_is_pinned_and_gold_isolated(self):
        from tests.fixtures.nci4a_synthetic_seed import GENERATION_ID, synthetic_g1_cases

        cases = synthetic_g1_cases()
        self.assertEqual(len(cases), 12)
        self.assertEqual(sum(case["split"] == "train" for case in cases), 6)
        self.assertEqual(sum(case["split"] == "gold" for case in cases), 6)
        # The origin file lives in the actual checkout, not this temporary test root.
        from pathlib import Path
        import shutil
        origin = Path(__file__).resolve().parents[1] / "fixtures" / "nci4a_synthetic_seed.py"
        dest = self.root / "tests" / "fixtures" / "nci4a_synthetic_seed.py"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, dest)
        digest = self.corpus.seal_generation(GENERATION_ID, cases)
        pin = origin.with_suffix(".sha256")
        self.assertTrue(pin.exists(), f"Independent fixed-generation pin missing: {digest}")
        self.assertEqual(pin.read_text(encoding="utf-8").strip(), digest)
        training = self.corpus.training_cases(GENERATION_ID, expected_digest=digest)
        gold = self.corpus.gold_cases_for_evaluation(GENERATION_ID, expected_digest=digest)
        self.assertEqual(len(training), 6)
        self.assertEqual(len(gold), 6)
        self.assertTrue(all(row["case_id"].startswith("g1-trn-") for row in training))
        self.assertTrue(all(row["case_id"].startswith("g1-gld-") for row in gold))
        self.assertFalse(any("g1-gld-" in json.dumps(row) for row in training))

    def test_generation_rejects_duplicates_missing_split_and_unbounded_size(self):
        cases = self.pair()
        cases[1]["case_id"] = "case-gold"
        with self.assertRaisesRegex(NeuralCrewCorpusError, "duplicate"):
            self.corpus.seal_generation("attempt", cases)
        cases = self.pair()
        cases[1]["split"] = "gold"
        with self.assertRaisesRegex(NeuralCrewCorpusError, "disjoint"):
            self.corpus.seal_generation("attempt", cases)
        with self.assertRaises(NeuralCrewCorpusError):
            self.corpus.seal_generation("attempt", [self.case("alone", "train")])
        with self.assertRaises(NeuralCrewCorpusError):
            self.corpus.seal_generation("bad/name", self.pair())


if __name__ == "__main__":
    unittest.main()
