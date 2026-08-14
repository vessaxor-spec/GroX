from __future__ import annotations

import json
from typing import Any

from .state import StateStore, now


class DurableState:
    """A4 operational ledger sharing GroX's private SQLite state plane."""

    def __init__(self, store: StateStore):
        self.store = store
        self.db = store.db
        self._init()

    def _init(self) -> None:
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS graph_runs(
          mission_id TEXT PRIMARY KEY, plan TEXT NOT NULL, global_risk TEXT NOT NULL,
          allow_repair INTEGER NOT NULL DEFAULT 0, resume_count INTEGER NOT NULL DEFAULT 0,
          cancelled INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS mission_checkpoints(
          id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id TEXT NOT NULL, node_id TEXT, attempt INTEGER,
          phase TEXT NOT NULL, status TEXT NOT NULL, order_id TEXT, payload TEXT NOT NULL,
          created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_checkpoints_mission ON mission_checkpoints(mission_id,id);
        CREATE TABLE IF NOT EXISTS exception_decisions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id TEXT NOT NULL, node_id TEXT, order_id TEXT,
          exception_type TEXT NOT NULL, risk TEXT NOT NULL, disposition TEXT NOT NULL, reason TEXT NOT NULL,
          requires_commander INTEGER NOT NULL DEFAULT 0, consulted_crew TEXT, consultation_order_id TEXT,
          created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_exception_decisions_mission ON exception_decisions(mission_id,id);
        CREATE TABLE IF NOT EXISTS mutation_journal(
          idempotency_key TEXT PRIMARY KEY, mission_id TEXT NOT NULL, order_id TEXT NOT NULL, target TEXT NOT NULL,
          before_exists INTEGER NOT NULL, before_content TEXT, before_sha256 TEXT, intended_sha256 TEXT NOT NULL,
          after_sha256 TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        ''')
        self.db.execute("UPDATE orders SET status='interrupted', updated_at=? WHERE status='running'", (now(),))
        self.db.commit()

    def save_graph_run(self, mission_id: str, plan: dict[str, Any], global_risk: str, allow_repair: bool) -> None:
        t = now()
        self.db.execute(
            """INSERT INTO graph_runs(mission_id,plan,global_risk,allow_repair,resume_count,cancelled,created_at,updated_at)
               VALUES(?,?,?,?,0,0,?,?)
               ON CONFLICT(mission_id) DO UPDATE SET plan=excluded.plan,global_risk=excluded.global_risk,
                 allow_repair=excluded.allow_repair,updated_at=excluded.updated_at""",
            (mission_id, json.dumps(plan, sort_keys=True), global_risk, int(bool(allow_repair)), t, t),
        )
        self.db.commit()

    def graph_run(self, mission_id: str) -> dict[str, Any] | None:
        row = self.db.execute("SELECT * FROM graph_runs WHERE mission_id=?", (mission_id,)).fetchone()
        if not row:
            return None
        out = dict(row)
        out['plan'] = json.loads(out['plan'])
        out['allow_repair'] = bool(out['allow_repair'])
        out['cancelled'] = bool(out['cancelled'])
        return out

    def increment_resume(self, mission_id: str) -> int:
        self.db.execute("UPDATE graph_runs SET resume_count=resume_count+1, updated_at=? WHERE mission_id=?", (now(), mission_id))
        self.db.commit()
        row = self.db.execute("SELECT resume_count FROM graph_runs WHERE mission_id=?", (mission_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown graph run {mission_id}")
        return int(row['resume_count'])

    def checkpoint(self, mission_id: str, phase: str, status: str, *, node_id: str | None = None,
                   attempt: int | None = None, order_id: str | None = None, payload: dict[str, Any] | None = None) -> int:
        cur = self.db.execute(
            """INSERT INTO mission_checkpoints(mission_id,node_id,attempt,phase,status,order_id,payload,created_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (mission_id, node_id, attempt, phase, status, order_id, json.dumps(payload or {}, sort_keys=True), now()),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def checkpoints(self, mission_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT * FROM mission_checkpoints WHERE mission_id=? ORDER BY id", (mission_id,)).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item['payload']=json.loads(item['payload']); out.append(item)
        return out

    def add_exception_decision(self, *, mission_id: str, node_id: str | None, order_id: str | None,
                               exception_type: str, risk: str, disposition: str, reason: str,
                               requires_commander: bool, consulted_crew: str | None = None,
                               consultation_order_id: str | None = None) -> int:
        cur=self.db.execute(
            """INSERT INTO exception_decisions(mission_id,node_id,order_id,exception_type,risk,disposition,reason,
               requires_commander,consulted_crew,consultation_order_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (mission_id,node_id,order_id,exception_type,risk,disposition,reason,int(bool(requires_commander)),
             consulted_crew,consultation_order_id,now()),
        )
        self.db.commit(); return int(cur.lastrowid)

    def exception_decisions(self, mission_id: str) -> list[dict[str, Any]]:
        rows=self.db.execute("SELECT * FROM exception_decisions WHERE mission_id=? ORDER BY id",(mission_id,)).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item['requires_commander']=bool(item['requires_commander']); out.append(item)
        return out

    def cancel_graph_run(self, mission_id: str, reason: str) -> None:
        t=now()
        self.db.execute("UPDATE graph_runs SET cancelled=1, updated_at=? WHERE mission_id=?",(t,mission_id))
        self.db.execute("UPDATE graph_nodes SET status='cancelled', updated_at=? WHERE mission_id=? AND status IN ('pending','ready','interrupted')",(t,mission_id))
        self.db.execute("UPDATE missions SET status='cancelled', summary=?, updated_at=? WHERE mission_id=?",(reason,t,mission_id))
        self.db.commit()

    def begin_mutation(self, *, idempotency_key: str, mission_id: str, order_id: str, target: str,
                       before_exists: bool, before_content: str | None, before_sha256: str | None,
                       intended_sha256: str) -> dict[str, Any]:
        existing=self.mutation(idempotency_key)
        if existing: return existing
        t=now()
        self.db.execute(
            """INSERT INTO mutation_journal(idempotency_key,mission_id,order_id,target,before_exists,before_content,
               before_sha256,intended_sha256,after_sha256,status,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,'prepared',?,?)""",
            (idempotency_key,mission_id,order_id,target,int(bool(before_exists)),before_content,before_sha256,intended_sha256,None,t,t),
        )
        self.db.commit(); return self.mutation(idempotency_key)

    def mutation(self, idempotency_key: str) -> dict[str, Any] | None:
        row=self.db.execute("SELECT * FROM mutation_journal WHERE idempotency_key=?",(idempotency_key,)).fetchone()
        if not row: return None
        out=dict(row); out['before_exists']=bool(out['before_exists']); return out

    def update_mutation(self, idempotency_key: str, status: str, *, after_sha256: str | None = None) -> None:
        row=self.mutation(idempotency_key)
        if not row: raise KeyError(f"unknown mutation {idempotency_key}")
        self.db.execute("UPDATE mutation_journal SET status=?, after_sha256=?, updated_at=? WHERE idempotency_key=?",
                        (status,row['after_sha256'] if after_sha256 is None else after_sha256,now(),idempotency_key))
        self.db.commit()

    def mutation_history(self, mission_id: str) -> list[dict[str, Any]]:
        rows=self.db.execute("SELECT * FROM mutation_journal WHERE mission_id=? ORDER BY created_at,idempotency_key",(mission_id,)).fetchall()
        out=[]
        for row in rows:
            item=dict(row); item['before_exists']=bool(item['before_exists']); out.append(item)
        return out

    def order_result(self, order_id: str) -> dict[str, Any] | None:
        order=self.db.execute("SELECT * FROM orders WHERE order_id=?",(order_id,)).fetchone()
        if not order: return None
        evidence=[dict(r) for r in self.db.execute("SELECT * FROM evidence WHERE order_id=? ORDER BY id",(order_id,))]
        for ev in evidence: ev['content']=json.loads(ev['content'])
        return {'order':dict(order),'evidence':evidence}
