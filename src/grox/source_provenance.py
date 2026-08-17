from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
from pathlib import PurePosixPath
import re
import secrets
from typing import Iterable

from .state import StateStore, now


SCHEMA = "grox-source-receipt-v1"
PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"

_CHANGE_CLASSES = {"research": 0, "stewardship": 1, "runtime": 2}
_OPERATIONS = {"create", "update", "delete", "mixed"}
_MUTATING_ACTIONS = {"fs_write", "mcp_mutate"}
_RECEIPT_ID_RE = re.compile(r"^SRC-[A-F0-9]{24}$")
_COMMITMENT_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
_PUBLIC_KEYS = (
    "GroX-Source-Provenance",
    "GroX-Authorization-Receipt",
    "GroX-Authorization-Commitment",
    "GroX-Change-Class",
)


@dataclass(frozen=True, slots=True)
class ProvenanceVerification:
    status: str
    reason: str
    receipt_ids: tuple[str, ...] = ()
    covered_paths: tuple[str, ...] = ()
    pr_number: int | None = None
    head_sha: str | None = None
    tree_sha: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PublicReceipt:
    receipt_id: str
    commitment: str
    change_class: str


class SourceProvenanceService:
    """Privacy-safe source authorization evidence over GroX's existing StateStore.

    This service never grants Mission, Repair, Crew, routing, Tool Gateway, or
    source-mutation authority. It can only issue a receipt after finding an
    existing explicit Repair Order with a mutating action and compatible scope.
    Public metadata is a commitment to that private witness, not permission.
    """

    def __init__(self, store: StateStore):
        self.store = store
        self.db = store.db
        self._init()

    def _init(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS source_authorization_receipts(
              receipt_id TEXT PRIMARY KEY,
              schema_version TEXT NOT NULL,
              mission_id TEXT NOT NULL,
              order_ids TEXT NOT NULL,
              change_class TEXT NOT NULL,
              scope_paths TEXT NOT NULL,
              operation TEXT NOT NULL,
              authority_state TEXT NOT NULL,
              nonce_hex TEXT NOT NULL,
              commitment TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL,
              verified_pr INTEGER,
              verified_head TEXT,
              verified_tree TEXT,
              consumed_pr INTEGER,
              consumed_commit TEXT,
              revoked_at TEXT,
              issued_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_source_receipts_mission
              ON source_authorization_receipts(mission_id,status,issued_at);
            """
        )
        self.db.commit()

    @staticmethod
    def canonical_json(value: dict) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    @staticmethod
    def normalize_path(path: str) -> str:
        raw = str(path).strip().replace("\\", "/")
        if not raw or raw.startswith("/"):
            raise ValueError(f"source scope must be repository-relative: {path!r}")
        candidate = PurePosixPath(raw)
        parts = candidate.parts
        if not parts or any(part in {"", ".", ".."} for part in parts):
            if raw == ".":
                return "."
            raise ValueError(f"unsafe or ambiguous source path: {path!r}")
        normalized = candidate.as_posix()
        if normalized.startswith("../") or "/../" in normalized:
            raise ValueError(f"source path escapes repository root: {path!r}")
        return normalized

    @classmethod
    def normalize_paths(cls, paths: Iterable[str]) -> tuple[str, ...]:
        values = sorted({cls.normalize_path(path) for path in paths})
        if not values:
            raise ValueError("at least one source path is required")
        return tuple(values)

    @staticmethod
    def _path_covered(path: str, scope: str) -> bool:
        if scope == ".":
            return True
        return path == scope or path.startswith(scope.rstrip("/") + "/")

    @classmethod
    def _scope_covers(cls, paths: Iterable[str], scopes: Iterable[str]) -> bool:
        normalized_scopes = tuple(cls.normalize_paths(scopes))
        return all(any(cls._path_covered(path, scope) for scope in normalized_scopes) for path in paths)

    @staticmethod
    def _private_payload(
        *,
        receipt_id: str,
        mission_id: str,
        order_ids: tuple[str, ...],
        change_class: str,
        scope_paths: tuple[str, ...],
        operation: str,
        authority_state: str,
        issued_at: str,
    ) -> dict:
        return {
            "schema": SCHEMA,
            "receipt_id": receipt_id,
            "mission_id": mission_id,
            "order_ids": list(order_ids),
            "change_class": change_class,
            "authorized_scope": {"paths": list(scope_paths), "operation": operation},
            "authority_state": authority_state,
            "issued_at": issued_at,
        }

    @classmethod
    def _commitment(cls, nonce_hex: str, payload: dict) -> str:
        nonce = bytes.fromhex(nonce_hex)
        digest = hashlib.sha256(SCHEMA.encode("utf-8") + b"\0" + nonce + cls.canonical_json(payload)).hexdigest()
        return f"sha256:{digest}"

    def issue_receipt(
        self,
        *,
        mission_id: str,
        order_ids: Iterable[str],
        change_class: str,
        scope_paths: Iterable[str],
        operation: str = "mixed",
    ) -> dict:
        if change_class not in _CHANGE_CLASSES:
            raise ValueError(f"unsupported source change class: {change_class}")
        if operation not in _OPERATIONS:
            raise ValueError(f"unsupported source operation: {operation}")
        mission = self.store.mission(mission_id)
        if not mission:
            raise ValueError(f"unknown Mission: {mission_id}")

        selected_ids = tuple(dict.fromkeys(str(order_id).strip() for order_id in order_ids if str(order_id).strip()))
        if not selected_ids:
            raise ValueError("at least one authorizing Mission Order is required")
        rows = {row["order_id"]: row for row in mission["orders"]}
        if any(order_id not in rows for order_id in selected_ids):
            missing = sorted(order_id for order_id in selected_ids if order_id not in rows)
            raise ValueError(f"authorizing Order not found on Mission: {missing}")

        receipt_scope = self.normalize_paths(scope_paths)
        order_scopes: list[str] = []
        for order_id in selected_ids:
            row = rows[order_id]
            if row["mode"] != "repair":
                raise PermissionError(f"source provenance requires explicit Repair authority: {order_id}")
            if row["status"] in {"failed", "cancelled", "blocked", "rejected"}:
                raise PermissionError(f"authorizing Order is not usable: {order_id} status={row['status']}")
            payload = json.loads(row["payload"])
            actions = set(payload.get("allowed_actions") or ())
            if not (actions & _MUTATING_ACTIONS):
                raise PermissionError(f"Repair Order lacks an explicit mutating action: {order_id}")
            order_scopes.extend(payload.get("scope") or ())

        if not self._scope_covers(receipt_scope, order_scopes):
            raise PermissionError("requested source receipt scope exceeds the authorizing Repair Order scope")

        receipt_id = f"SRC-{secrets.token_hex(12).upper()}"
        nonce_hex = secrets.token_hex(32)
        issued_at = now()
        authority_state = "authorized"
        payload = self._private_payload(
            receipt_id=receipt_id,
            mission_id=mission_id,
            order_ids=selected_ids,
            change_class=change_class,
            scope_paths=receipt_scope,
            operation=operation,
            authority_state=authority_state,
            issued_at=issued_at,
        )
        commitment = self._commitment(nonce_hex, payload)
        self.db.execute(
            """INSERT INTO source_authorization_receipts(
                 receipt_id,schema_version,mission_id,order_ids,change_class,scope_paths,operation,
                 authority_state,nonce_hex,commitment,status,issued_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                receipt_id,
                SCHEMA,
                mission_id,
                json.dumps(list(selected_ids), separators=(",", ":")),
                change_class,
                json.dumps(list(receipt_scope), separators=(",", ":")),
                operation,
                authority_state,
                nonce_hex,
                commitment,
                "issued",
                issued_at,
                issued_at,
            ),
        )
        self.db.commit()
        return self.receipt(receipt_id)

    def receipt(self, receipt_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM source_authorization_receipts WHERE receipt_id=?", (receipt_id,)
        ).fetchone()
        if not row:
            raise KeyError(receipt_id)
        out = dict(row)
        out["order_ids"] = json.loads(out["order_ids"])
        out["scope_paths"] = json.loads(out["scope_paths"])
        return out

    @staticmethod
    def render_public_block(receipt: dict) -> str:
        return "\n".join(
            (
                f"GroX-Source-Provenance: {SCHEMA.removeprefix('grox-source-receipt-')}",
                f"GroX-Authorization-Receipt: {receipt['receipt_id']}",
                f"GroX-Authorization-Commitment: {receipt['commitment']}",
                f"GroX-Change-Class: {receipt['change_class']}",
            )
        )

    @staticmethod
    def parse_public_block(block: str) -> PublicReceipt:
        fields: dict[str, str] = {}
        for raw_line in str(block).splitlines():
            if not raw_line.strip():
                continue
            if ":" not in raw_line:
                raise ValueError("malformed public provenance line")
            key, value = raw_line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key not in _PUBLIC_KEYS:
                raise ValueError(f"unsupported public provenance field: {key}")
            if key in fields:
                raise ValueError(f"duplicate public provenance field: {key}")
            fields[key] = value
        if set(fields) != set(_PUBLIC_KEYS):
            missing = sorted(set(_PUBLIC_KEYS) - set(fields))
            raise ValueError(f"incomplete public provenance block; missing={missing}")
        if fields["GroX-Source-Provenance"] != "v1":
            raise ValueError("unsupported public provenance version")
        receipt_id = fields["GroX-Authorization-Receipt"]
        commitment = fields["GroX-Authorization-Commitment"]
        change_class = fields["GroX-Change-Class"]
        if not _RECEIPT_ID_RE.fullmatch(receipt_id):
            raise ValueError("invalid opaque receipt id")
        if not _COMMITMENT_RE.fullmatch(commitment):
            raise ValueError("invalid commitment")
        if change_class not in _CHANGE_CLASSES:
            raise ValueError("invalid change class")
        return PublicReceipt(receipt_id, commitment, change_class)

    @classmethod
    def validate_public_block(cls, block: str) -> ProvenanceVerification:
        try:
            public = cls.parse_public_block(block)
        except ValueError as exc:
            return ProvenanceVerification(FAIL, str(exc))
        return ProvenanceVerification(PASS, "public provenance structure is valid", (public.receipt_id,))

    def _verify_witness(self, public: PublicReceipt, *, pr_number: int, head_sha: str, tree_sha: str) -> ProvenanceVerification:
        row = self.db.execute(
            "SELECT * FROM source_authorization_receipts WHERE receipt_id=?", (public.receipt_id,)
        ).fetchone()
        if not row:
            return ProvenanceVerification(UNKNOWN, "private authorization witness is unavailable", (public.receipt_id,))
        receipt = dict(row)
        if receipt["schema_version"] != SCHEMA:
            return ProvenanceVerification(UNKNOWN, "private authorization witness uses an unsupported schema", (public.receipt_id,))
        if receipt["revoked_at"] or receipt["status"] == "revoked":
            return ProvenanceVerification(FAIL, "private authorization receipt is revoked", (public.receipt_id,))
        if receipt["consumed_pr"] is not None and int(receipt["consumed_pr"]) != int(pr_number):
            return ProvenanceVerification(FAIL, "authorization receipt was already consumed by another change", (public.receipt_id,))

        payload = self._private_payload(
            receipt_id=receipt["receipt_id"],
            mission_id=receipt["mission_id"],
            order_ids=tuple(json.loads(receipt["order_ids"])),
            change_class=receipt["change_class"],
            scope_paths=tuple(json.loads(receipt["scope_paths"])),
            operation=receipt["operation"],
            authority_state=receipt["authority_state"],
            issued_at=receipt["issued_at"],
        )
        expected = self._commitment(receipt["nonce_hex"], payload)
        if not hmac.compare_digest(expected, receipt["commitment"]) or not hmac.compare_digest(expected, public.commitment):
            return ProvenanceVerification(FAIL, "authorization commitment does not match the private witness", (public.receipt_id,))
        if _CHANGE_CLASSES[public.change_class] < _CHANGE_CLASSES[receipt["change_class"]]:
            return ProvenanceVerification(FAIL, "public change class weakens the private authorization class", (public.receipt_id,))

        return ProvenanceVerification(
            PASS,
            "private authorization witness and commitment are valid",
            (public.receipt_id,),
            (),
            int(pr_number),
            str(head_sha),
            str(tree_sha),
        )

    def verify_change(
        self,
        public_blocks: Iterable[str],
        *,
        changed_paths: Iterable[str],
        pr_number: int,
        head_sha: str,
        tree_sha: str,
    ) -> ProvenanceVerification:
        paths = self.normalize_paths(changed_paths)
        blocks = tuple(public_blocks)
        if not blocks:
            return ProvenanceVerification(FAIL, "no public authorization receipts were supplied")

        receipts: list[tuple[PublicReceipt, dict]] = []
        receipt_ids: list[str] = []
        for block in blocks:
            try:
                public = self.parse_public_block(block)
            except ValueError as exc:
                return ProvenanceVerification(FAIL, str(exc), tuple(receipt_ids))
            witness = self._verify_witness(public, pr_number=pr_number, head_sha=head_sha, tree_sha=tree_sha)
            if witness.status != PASS:
                return witness
            receipt = self.receipt(public.receipt_id)
            receipts.append((public, receipt))
            receipt_ids.append(public.receipt_id)

        uncovered = [
            path
            for path in paths
            if not any(
                any(self._path_covered(path, scope) for scope in receipt["scope_paths"])
                for _, receipt in receipts
            )
        ]
        if uncovered:
            return ProvenanceVerification(FAIL, f"changed source paths exceed private authorization scope: {uncovered}", tuple(receipt_ids))

        t = now()
        for _, receipt in receipts:
            if receipt["consumed_pr"] is not None:
                if (
                    int(receipt["consumed_pr"]) != int(pr_number)
                    or receipt["verified_head"] != str(head_sha)
                    or receipt["verified_tree"] != str(tree_sha)
                ):
                    return ProvenanceVerification(FAIL, "consumed receipt cannot be rebound to a different change", tuple(receipt_ids))
                continue
            self.db.execute(
                """UPDATE source_authorization_receipts
                   SET status='verified', verified_pr=?, verified_head=?, verified_tree=?, updated_at=?
                   WHERE receipt_id=?""",
                (int(pr_number), str(head_sha), str(tree_sha), t, receipt["receipt_id"]),
            )
        self.db.commit()
        return ProvenanceVerification(
            PASS,
            "private authorization receipts cover the exact proposed source change",
            tuple(receipt_ids),
            paths,
            int(pr_number),
            str(head_sha),
            str(tree_sha),
        )

    def verification_binding_matches(self, receipt_id: str, *, pr_number: int, head_sha: str, tree_sha: str) -> bool:
        receipt = self.receipt(receipt_id)
        return (
            receipt["status"] in {"verified", "consumed"}
            and receipt["verified_pr"] == int(pr_number)
            and receipt["verified_head"] == str(head_sha)
            and receipt["verified_tree"] == str(tree_sha)
        )

    def consume(
        self,
        receipt_id: str,
        *,
        pr_number: int,
        verified_head: str,
        verified_tree: str,
        canonical_commit: str,
    ) -> dict:
        receipt = self.receipt(receipt_id)
        if receipt["status"] == "consumed":
            if receipt["consumed_pr"] == int(pr_number) and receipt["consumed_commit"] == str(canonical_commit):
                return receipt
            raise PermissionError("authorization receipt has already been consumed")
        if not self.verification_binding_matches(
            receipt_id, pr_number=pr_number, head_sha=verified_head, tree_sha=verified_tree
        ):
            raise PermissionError("receipt must be privately verified against the exact PR head/tree before consumption")
        self.db.execute(
            """UPDATE source_authorization_receipts
               SET status='consumed', consumed_pr=?, consumed_commit=?, updated_at=?
               WHERE receipt_id=?""",
            (int(pr_number), str(canonical_commit), now(), receipt_id),
        )
        self.db.commit()
        return self.receipt(receipt_id)

    def revoke(self, receipt_id: str) -> dict:
        receipt = self.receipt(receipt_id)
        if receipt["status"] == "consumed":
            raise PermissionError("a consumed authorization receipt cannot be retroactively revoked")
        t = now()
        self.db.execute(
            "UPDATE source_authorization_receipts SET status='revoked', revoked_at=?, updated_at=? WHERE receipt_id=?",
            (t, t, receipt_id),
        )
        self.db.commit()
        return self.receipt(receipt_id)
