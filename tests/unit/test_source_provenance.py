import json
import tempfile
import unittest
from pathlib import Path

from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.source_provenance import FAIL, PASS, UNKNOWN, SourceProvenanceService
from grox.state import StateStore


class SourceProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.tmp.name) / "state.sqlite3")
        self.service = SourceProvenanceService(self.store)
        self.mission_id = "MSN-provenance-test"
        self.store.create_mission(self.mission_id, "Implement bounded source change", "repair", "high")
        self.order = MissionOrder.new(
            self.mission_id,
            "Implement bounded source change",
            "Modify source provenance implementation and tests",
            MissionMode.repair,
            "backend-engineer",
            required_capabilities=("repo_read", "fs_write"),
            allowed_actions=("fs_read", "fs_write", "test_run"),
            forbidden_actions=("mcp_mutate",),
            scope=("src/grox", "tests", "docs/architecture"),
            risk_class=RiskClass.high,
            evidence_requirements=("diff", "tests"),
            verification_requirements=("independent_verifier",),
        )
        self.store.save_order(self.order)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def issue(self, **kwargs):
        params = {
            "mission_id": self.mission_id,
            "order_ids": [self.order.order_id],
            "change_class": "runtime",
            "scope_paths": ["src/grox/source_provenance.py", "tests/unit/test_source_provenance.py"],
            "operation": "mixed",
        }
        params.update(kwargs)
        return self.service.issue_receipt(**params)

    def test_receipt_requires_real_repair_order_with_mutation_authority(self):
        inspect_order = MissionOrder.new(
            self.mission_id,
            "Inspect only",
            "Inspect source",
            MissionMode.inspect,
            "code-reviewer",
            allowed_actions=("fs_read",),
            scope=("src/grox",),
        )
        self.store.save_order(inspect_order)
        with self.assertRaises(PermissionError):
            self.service.issue_receipt(
                mission_id=self.mission_id,
                order_ids=[inspect_order.order_id],
                change_class="runtime",
                scope_paths=["src/grox/source_provenance.py"],
            )

        repair_without_write = MissionOrder.new(
            self.mission_id,
            "No write grant",
            "Analyze a Repair path without mutation grant",
            MissionMode.repair,
            "code-reviewer",
            allowed_actions=("fs_read", "test_run"),
            scope=("src/grox",),
        )
        self.store.save_order(repair_without_write)
        with self.assertRaises(PermissionError):
            self.service.issue_receipt(
                mission_id=self.mission_id,
                order_ids=[repair_without_write.order_id],
                change_class="runtime",
                scope_paths=["src/grox/source_provenance.py"],
            )

    def test_injected_mutation_grant_cannot_turn_non_repair_order_into_receipt_authority(self):
        injected = MissionOrder.new(
            self.mission_id,
            "Repair authority seed",
            "Create a row that will be downgraded after persistence",
            MissionMode.repair,
            "backend-engineer",
            allowed_actions=("fs_read", "fs_write"),
            scope=("src/grox",),
        )
        self.store.save_order(injected)
        self.store.db.execute("UPDATE orders SET mode='inspect' WHERE order_id=?", (injected.order_id,))
        self.store.db.commit()
        with self.assertRaises(PermissionError):
            self.service.issue_receipt(
                mission_id=self.mission_id,
                order_ids=[injected.order_id],
                change_class="runtime",
                scope_paths=["src/grox/source_provenance.py"],
            )

    def test_scope_cannot_exceed_repair_order(self):
        with self.assertRaises(PermissionError):
            self.issue(scope_paths=["configs/tool-policy.json"])
        for path in ("../secret", "/etc/passwd", "src/../secret"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    self.issue(scope_paths=[path])

    def test_same_authorization_uses_fresh_nonce_and_distinct_commitment(self):
        first = self.issue()
        second = self.issue()
        self.assertNotEqual(first["receipt_id"], second["receipt_id"])
        self.assertNotEqual(first["nonce_hex"], second["nonce_hex"])
        self.assertNotEqual(first["commitment"], second["commitment"])
        self.assertEqual(len(bytes.fromhex(first["nonce_hex"])), 32)

    def test_public_block_is_privacy_minimized_and_structurally_valid(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.assertEqual(self.service.validate_public_block(block).status, PASS)
        self.assertIn(receipt["receipt_id"], block)
        self.assertIn(receipt["commitment"], block)
        for private_value in (
            self.mission_id,
            self.order.order_id,
            receipt["nonce_hex"],
            "backend-engineer",
            "Implement bounded source change",
        ):
            self.assertNotIn(private_value, block)

    def test_missing_private_witness_is_unknown_not_pass(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        other_store = StateStore(Path(self.tmp.name) / "other.sqlite3")
        try:
            result = SourceProvenanceService(other_store).verify_change(
                [block],
                changed_paths=["src/grox/source_provenance.py"],
                pr_number=45,
                head_sha="a" * 40,
                tree_sha="b" * 40,
            )
        finally:
            other_store.close()
        self.assertEqual(result.status, UNKNOWN)

    def test_private_verification_rechecks_current_authorizing_order(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.store.update_order(self.order.order_id, "failed")
        result = self.service.verify_change(
            [block],
            changed_paths=["src/grox/source_provenance.py"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(result.status, FAIL)

    def test_missing_authorizing_order_is_unknown(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.store.db.execute("DELETE FROM orders WHERE order_id=?", (self.order.order_id,))
        self.store.db.commit()
        result = self.service.verify_change(
            [block],
            changed_paths=["src/grox/source_provenance.py"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(result.status, UNKNOWN)

    def test_forged_commitment_fails(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt).replace(receipt["commitment"], "sha256:" + "0" * 64)
        result = self.service.verify_change(
            [block],
            changed_paths=["src/grox/source_provenance.py"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(result.status, FAIL)

    def test_change_class_cannot_be_downgraded(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt).replace("GroX-Change-Class: runtime", "GroX-Change-Class: research")
        result = self.service.verify_change(
            [block],
            changed_paths=["src/grox/source_provenance.py"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(result.status, FAIL)

    def test_exact_scope_and_head_binding_then_consumption(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        paths = ["src/grox/source_provenance.py", "tests/unit/test_source_provenance.py"]
        result = self.service.verify_change(
            [block], changed_paths=paths, pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
        )
        self.assertEqual(result.status, PASS)
        self.assertTrue(
            self.service.verification_binding_matches(
                receipt["receipt_id"], pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
            )
        )
        self.assertFalse(
            self.service.verification_binding_matches(
                receipt["receipt_id"], pr_number=45, head_sha="c" * 40, tree_sha="b" * 40
            )
        )
        with self.assertRaises(PermissionError):
            self.service.consume(
                receipt["receipt_id"],
                pr_number=45,
                verified_head="c" * 40,
                verified_tree="b" * 40,
                canonical_commit="d" * 40,
            )
        consumed = self.service.consume(
            receipt["receipt_id"],
            pr_number=45,
            verified_head="a" * 40,
            verified_tree="b" * 40,
            canonical_commit="d" * 40,
        )
        self.assertEqual(consumed["status"], "consumed")
        self.assertEqual(consumed["consumed_commit"], "d" * 40)

    def test_consumed_receipt_cannot_be_replayed_on_another_pr(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.assertEqual(
            self.service.verify_change(
                [block], changed_paths=["src/grox/source_provenance.py"], pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
            ).status,
            PASS,
        )
        self.service.consume(
            receipt["receipt_id"],
            pr_number=45,
            verified_head="a" * 40,
            verified_tree="b" * 40,
            canonical_commit="d" * 40,
        )
        replay = self.service.verify_change(
            [block], changed_paths=["src/grox/source_provenance.py"], pr_number=46, head_sha="e" * 40, tree_sha="f" * 40
        )
        self.assertEqual(replay.status, FAIL)

    def test_multiple_receipts_cover_independent_scopes_without_widening(self):
        first = self.service.issue_receipt(
            mission_id=self.mission_id,
            order_ids=[self.order.order_id],
            change_class="runtime",
            scope_paths=["src/grox/source_provenance.py"],
        )
        second = self.service.issue_receipt(
            mission_id=self.mission_id,
            order_ids=[self.order.order_id],
            change_class="runtime",
            scope_paths=["tests/unit/test_source_provenance.py"],
        )
        blocks = [self.service.render_public_block(first), self.service.render_public_block(second)]
        covered = self.service.verify_change(
            blocks,
            changed_paths=["src/grox/source_provenance.py", "tests/unit/test_source_provenance.py"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(covered.status, PASS)
        uncovered = self.service.verify_change(
            blocks,
            changed_paths=["src/grox/source_provenance.py", "README.md"],
            pr_number=45,
            head_sha="a" * 40,
            tree_sha="b" * 40,
        )
        self.assertEqual(uncovered.status, FAIL)

    def test_private_row_tampering_breaks_commitment(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.store.db.execute(
            "UPDATE source_authorization_receipts SET scope_paths=? WHERE receipt_id=?",
            (json.dumps(["."]), receipt["receipt_id"]),
        )
        self.store.db.commit()
        result = self.service.verify_change(
            [block], changed_paths=["README.md"], pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
        )
        self.assertEqual(result.status, FAIL)

    def test_revoke_fails_verification_and_consumed_receipt_cannot_be_revoked(self):
        receipt = self.issue()
        block = self.service.render_public_block(receipt)
        self.service.revoke(receipt["receipt_id"])
        self.assertEqual(
            self.service.verify_change(
                [block], changed_paths=["src/grox/source_provenance.py"], pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
            ).status,
            FAIL,
        )

        second = self.issue()
        second_block = self.service.render_public_block(second)
        self.service.verify_change(
            [second_block], changed_paths=["src/grox/source_provenance.py"], pr_number=45, head_sha="a" * 40, tree_sha="b" * 40
        )
        self.service.consume(
            second["receipt_id"], pr_number=45, verified_head="a" * 40, verified_tree="b" * 40, canonical_commit="d" * 40
        )
        with self.assertRaises(PermissionError):
            self.service.revoke(second["receipt_id"])


if __name__ == "__main__":
    unittest.main()
