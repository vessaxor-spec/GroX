from pathlib import Path

p = Path('src/grox/source_provenance.py')
text = p.read_text(encoding='utf-8')
old = '''        payload = self._private_payload(
            receipt_id=receipt["receipt_id"],
            mission_id=receipt["mission_id"],
            order_ids=tuple(json.loads(receipt["order_ids"])),
            change_class=receipt["change_class"],
            scope_paths=tuple(json.loads(receipt["scope_paths"])),
            operation=receipt["operation"],
            authority_state=receipt["authority_state"],
            issued_at=receipt["issued_at"],
        )
'''
new = '''        order_ids = tuple(json.loads(receipt["order_ids"]))
        receipt_scope = tuple(json.loads(receipt["scope_paths"]))
        mission = self.store.mission(receipt["mission_id"])
        if not mission:
            return ProvenanceVerification(UNKNOWN, "authorizing Mission is unavailable", (public.receipt_id,))
        current_orders = {row["order_id"]: row for row in mission["orders"]}
        if any(order_id not in current_orders for order_id in order_ids):
            return ProvenanceVerification(UNKNOWN, "authorizing Mission Order is unavailable", (public.receipt_id,))
        current_scopes: list[str] = []
        for order_id in order_ids:
            order = current_orders[order_id]
            if order["mode"] != "repair":
                return ProvenanceVerification(FAIL, "authorizing Mission Order no longer carries Repair authority", (public.receipt_id,))
            if order["status"] in {"failed", "cancelled", "blocked", "rejected"}:
                return ProvenanceVerification(FAIL, "authorizing Mission Order is no longer usable", (public.receipt_id,))
            try:
                order_payload = json.loads(order["payload"])
            except (TypeError, json.JSONDecodeError):
                return ProvenanceVerification(UNKNOWN, "authorizing Mission Order payload is unreadable", (public.receipt_id,))
            if not (set(order_payload.get("allowed_actions") or ()) & _MUTATING_ACTIONS):
                return ProvenanceVerification(FAIL, "authorizing Mission Order no longer carries a mutating action", (public.receipt_id,))
            current_scopes.extend(order_payload.get("scope") or ())
        try:
            scope_valid = self._scope_covers(receipt_scope, current_scopes)
        except ValueError:
            return ProvenanceVerification(UNKNOWN, "authorizing Mission Order scope is unreadable", (public.receipt_id,))
        if not scope_valid:
            return ProvenanceVerification(FAIL, "private receipt scope is no longer covered by its authorizing Mission Orders", (public.receipt_id,))

        payload = self._private_payload(
            receipt_id=receipt["receipt_id"],
            mission_id=receipt["mission_id"],
            order_ids=order_ids,
            change_class=receipt["change_class"],
            scope_paths=receipt_scope,
            operation=receipt["operation"],
            authority_state=receipt["authority_state"],
            issued_at=receipt["issued_at"],
        )
'''
if old not in text:
    raise SystemExit('source provenance witness anchor drifted')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

p = Path('tests/unit/test_source_provenance.py')
text = p.read_text(encoding='utf-8')
anchor = '''    def test_forged_commitment_fails(self):
'''
insert = '''    def test_private_verification_rechecks_current_authorizing_order(self):
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

'''
if anchor not in text:
    raise SystemExit('test insertion anchor drifted')
text = text.replace(anchor, insert + anchor, 1)
p.write_text(text, encoding='utf-8')
