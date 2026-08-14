from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import Evidence, MissionOrder


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS missions(
          mission_id TEXT PRIMARY KEY, directive TEXT NOT NULL, mode TEXT NOT NULL,
          risk TEXT NOT NULL, status TEXT NOT NULL, summary TEXT, created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orders(
          order_id TEXT PRIMARY KEY, mission_id TEXT NOT NULL, crew_id TEXT NOT NULL,
          mode TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(
          id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id TEXT NOT NULL, order_id TEXT NOT NULL,
          kind TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS crew_state(
          crew_id TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'asleep', tours INTEGER NOT NULL DEFAULT 0,
          last_mission TEXT, episodic_notes TEXT NOT NULL DEFAULT '[]', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS graph_nodes(
          mission_id TEXT NOT NULL, node_id TEXT NOT NULL, order_id TEXT, crew_id TEXT,
          status TEXT NOT NULL, attempt INTEGER NOT NULL DEFAULT 0, dependencies TEXT NOT NULL,
          payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          PRIMARY KEY(mission_id,node_id));
        CREATE TABLE IF NOT EXISTS graph_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id TEXT NOT NULL, node_id TEXT,
          event_type TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS memories(
          id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, scope TEXT NOT NULL, crew_id TEXT,
          task_class TEXT, memory_key TEXT NOT NULL, content TEXT NOT NULL, provenance TEXT NOT NULL,
          confidence REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1, supersedes_id INTEGER,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_memories_active_scope ON memories(active,scope,crew_id,kind,task_class);
        CREATE TABLE IF NOT EXISTS crew_performance(
          id INTEGER PRIMARY KEY AUTOINCREMENT, crew_id TEXT NOT NULL, mission_id TEXT NOT NULL,
          order_id TEXT NOT NULL UNIQUE, task_class TEXT NOT NULL, status TEXT NOT NULL,
          evidence_quality REAL NOT NULL, verified INTEGER, latency_ms REAL NOT NULL,
          cost_units REAL NOT NULL, risk TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_crew_performance_task ON crew_performance(crew_id,task_class,created_at);
        ''')
        # Crash recovery: no Crew remains notionally on duty after process death.
        self.db.execute("UPDATE crew_state SET status='asleep' WHERE status='on_duty'")
        self.db.execute("UPDATE missions SET status='interrupted', updated_at=? WHERE status='running'", (now(),))
        self.db.execute("UPDATE graph_nodes SET status='interrupted', updated_at=? WHERE status='running'", (now(),))
        self.db.commit()

    def close(self):
        db = getattr(self, "db", None)
        if db is not None:
            db.close()
            self.db = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def ensure_crew(self, crew_id: str):
        self.db.execute("INSERT OR IGNORE INTO crew_state(crew_id,status,tours,updated_at) VALUES(?, 'asleep', 0, ?)", (crew_id, now()))
        self.db.commit()

    def crew_on_duty(self, crew_id: str, mission_id: str):
        self.ensure_crew(crew_id)
        self.db.execute("UPDATE crew_state SET status='on_duty', last_mission=?, updated_at=? WHERE crew_id=?", (mission_id, now(), crew_id))
        self.db.commit()

    def crew_sleep(self, crew_id: str, mission_id: str, note: str):
        self.ensure_crew(crew_id)
        row = self.db.execute("SELECT episodic_notes,tours FROM crew_state WHERE crew_id=?", (crew_id,)).fetchone()
        notes = json.loads(row['episodic_notes'])
        notes.append({"mission_id": mission_id, "note": note, "at": now()})
        notes = notes[-50:]
        self.db.execute(
            "UPDATE crew_state SET status='asleep', tours=?, last_mission=?, episodic_notes=?, updated_at=? WHERE crew_id=?",
            (row['tours'] + 1, mission_id, json.dumps(notes), now(), crew_id),
        )
        self.db.commit()

    def create_mission(self, mission_id: str, directive: str, mode: str, risk: str):
        t = now()
        self.db.execute("INSERT INTO missions VALUES(?,?,?,?,?,?,?,?)", (mission_id, directive, mode, risk, 'running', None, t, t))
        self.db.commit()

    def update_mission(self, mission_id: str, status: str, summary: str | None = None):
        self.db.execute("UPDATE missions SET status=?, summary=?, updated_at=? WHERE mission_id=?", (status, summary, now(), mission_id))
        self.db.commit()

    def save_order(self, order: MissionOrder, status: str = 'issued'):
        t = now()
        self.db.execute(
            "INSERT OR REPLACE INTO orders VALUES(?,?,?,?,?,?,?,?)",
            (order.order_id, order.mission_id, order.assigned_crew, order.mode.value, status, order.to_json(), t, t),
        )
        self.db.commit()

    def update_order(self, order_id: str, status: str):
        self.db.execute("UPDATE orders SET status=?, updated_at=? WHERE order_id=?", (status, now(), order_id))
        self.db.commit()

    def add_evidence(self, mission_id: str, order_id: str, ev: Evidence):
        self.db.execute(
            "INSERT INTO evidence(mission_id,order_id,kind,content,created_at) VALUES(?,?,?,?,?)",
            (mission_id, order_id, ev.kind, json.dumps(ev.content, sort_keys=True), now()),
        )
        self.db.commit()

    def save_graph_node(
        self,
        mission_id: str,
        node_id: str,
        *,
        payload: dict[str, Any],
        dependencies: list[str],
        status: str = 'pending',
        attempt: int = 0,
        order_id: str | None = None,
        crew_id: str | None = None,
    ):
        t = now()
        self.db.execute(
            """INSERT OR REPLACE INTO graph_nodes
               (mission_id,node_id,order_id,crew_id,status,attempt,dependencies,payload,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,COALESCE((SELECT created_at FROM graph_nodes WHERE mission_id=? AND node_id=?),?),?)""",
            (
                mission_id, node_id, order_id, crew_id, status, attempt,
                json.dumps(dependencies, sort_keys=True), json.dumps(payload, sort_keys=True),
                mission_id, node_id, t, t,
            ),
        )
        self.db.commit()

    def update_graph_node(
        self,
        mission_id: str,
        node_id: str,
        status: str,
        *,
        attempt: int | None = None,
        order_id: str | None = None,
        crew_id: str | None = None,
        dependencies: list[str] | None = None,
        payload: dict[str, Any] | None = None,
    ):
        row = self.db.execute("SELECT * FROM graph_nodes WHERE mission_id=? AND node_id=?", (mission_id, node_id)).fetchone()
        if not row:
            raise KeyError(f"unknown graph node {mission_id}/{node_id}")
        self.db.execute(
            """UPDATE graph_nodes SET status=?, attempt=?, order_id=?, crew_id=?, dependencies=?, payload=?, updated_at=?
               WHERE mission_id=? AND node_id=?""",
            (
                status,
                row['attempt'] if attempt is None else attempt,
                row['order_id'] if order_id is None else order_id,
                row['crew_id'] if crew_id is None else crew_id,
                row['dependencies'] if dependencies is None else json.dumps(dependencies, sort_keys=True),
                row['payload'] if payload is None else json.dumps(payload, sort_keys=True),
                now(), mission_id, node_id,
            ),
        )
        self.db.commit()

    def add_graph_event(self, mission_id: str, event_type: str, content: dict[str, Any], node_id: str | None = None):
        self.db.execute(
            "INSERT INTO graph_events(mission_id,node_id,event_type,content,created_at) VALUES(?,?,?,?,?)",
            (mission_id, node_id, event_type, json.dumps(content, sort_keys=True), now()),
        )
        self.db.commit()

    def graph_nodes(self, mission_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.execute("SELECT * FROM graph_nodes WHERE mission_id=? ORDER BY created_at,node_id", (mission_id,))]

    def graph_events(self, mission_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.execute("SELECT * FROM graph_events WHERE mission_id=? ORDER BY id", (mission_id,))]

    def mission(self, mission_id: str) -> dict[str, Any] | None:
        m = self.db.execute("SELECT * FROM missions WHERE mission_id=?", (mission_id,)).fetchone()
        if not m:
            return None
        orders = [dict(r) for r in self.db.execute("SELECT * FROM orders WHERE mission_id=? ORDER BY created_at", (mission_id,))]
        evidence = [dict(r) for r in self.db.execute("SELECT * FROM evidence WHERE mission_id=? ORDER BY id", (mission_id,))]
        return {
            "mission": dict(m),
            "orders": orders,
            "evidence": evidence,
            "graph_nodes": self.graph_nodes(mission_id),
            "graph_events": self.graph_events(mission_id),
        }

    def recent_missions(self, limit: int = 20):
        return [dict(r) for r in self.db.execute("SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,))]

    def crew_states(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM crew_state ORDER BY crew_id")]

    def episodic_notes(self, crew_id: str, limit: int = 20) -> list[dict[str, Any]]:
        row = self.db.execute("SELECT episodic_notes FROM crew_state WHERE crew_id=?", (crew_id,)).fetchone()
        if not row:
            return []
        limit = max(0, int(limit))
        if limit == 0:
            return []
        notes = json.loads(row['episodic_notes'])
        return list(reversed(notes[-limit:]))

    def remember(
        self,
        *,
        kind: str,
        scope: str,
        crew_id: str | None,
        task_class: str | None,
        memory_key: str,
        content: str,
        provenance: dict[str, Any],
        confidence: float = 1.0,
    ) -> int:
        if kind not in {'semantic', 'procedural', 'vessel'}:
            raise ValueError(f"unsupported memory kind: {kind}")
        if scope not in {'crew', 'vessel'}:
            raise ValueError(f"unsupported memory scope: {scope}")
        if scope == 'crew' and not crew_id:
            raise ValueError("crew-scoped memory requires crew_id")
        if kind == 'vessel' and scope != 'vessel':
            raise ValueError("Vessel memory must use vessel scope")
        if not isinstance(provenance, dict) or not provenance:
            raise ValueError("memory provenance is required")
        if scope == 'vessel':
            crew_id = None
        if not memory_key.strip() or not content.strip():
            raise ValueError("memory_key and content are required")
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("memory confidence must be between 0 and 1")
        prior = self.db.execute(
            """SELECT id FROM memories WHERE active=1 AND kind=? AND scope=? AND COALESCE(crew_id,'')=COALESCE(?, '') AND memory_key=? ORDER BY id DESC LIMIT 1""",
            (kind, scope, crew_id, memory_key),
        ).fetchone()
        t = now()
        if prior:
            self.db.execute("UPDATE memories SET active=0, updated_at=? WHERE id=?", (t, prior['id']))
        cur = self.db.execute(
            """INSERT INTO memories(kind,scope,crew_id,task_class,memory_key,content,provenance,confidence,active,supersedes_id,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,1,?,?,?)""",
            (kind, scope, crew_id, task_class, memory_key, content, json.dumps(provenance, sort_keys=True), confidence, prior['id'] if prior else None, t, t),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def forget_memory(self, memory_id: int) -> None:
        self.db.execute("UPDATE memories SET active=0, updated_at=? WHERE id=?", (now(), int(memory_id)))
        self.db.commit()

    def memories_for(self, crew_id: str, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        where_active = "" if include_inactive else "AND active=1"
        rows = self.db.execute(
            f"""SELECT * FROM memories
                WHERE (scope='vessel' OR (scope='crew' AND crew_id=?)) {where_active}
                ORDER BY active DESC, updated_at DESC, id DESC""",
            (crew_id,),
        ).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            item['provenance'] = json.loads(item['provenance'])
            item['active'] = bool(item['active'])
            out.append(item)
        return out

    def record_performance(
        self,
        *,
        crew_id: str,
        mission_id: str,
        order_id: str,
        task_class: str,
        status: str,
        evidence_quality: float,
        verified: bool | None,
        latency_ms: float,
        cost_units: float,
        risk: str,
    ) -> None:
        self.db.execute(
            """INSERT INTO crew_performance(crew_id,mission_id,order_id,task_class,status,evidence_quality,verified,latency_ms,cost_units,risk,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(order_id) DO UPDATE SET
                 crew_id=excluded.crew_id, mission_id=excluded.mission_id, task_class=excluded.task_class,
                 status=excluded.status, evidence_quality=excluded.evidence_quality, verified=COALESCE(excluded.verified,crew_performance.verified),
                 latency_ms=excluded.latency_ms, cost_units=excluded.cost_units, risk=excluded.risk""",
            (
                crew_id, mission_id, order_id, task_class, status,
                max(0.0, min(1.0, float(evidence_quality))), None if verified is None else int(bool(verified)),
                max(0.0, float(latency_ms)), max(0.0, float(cost_units)), risk, now(),
            ),
        )
        self.db.commit()

    def mark_performance_verified(self, order_id: str, ok: bool) -> None:
        self.db.execute("UPDATE crew_performance SET verified=? WHERE order_id=?", (int(bool(ok)), order_id))
        self.db.commit()

    def performance_history(self, crew_id: str, task_class: str | None = None) -> list[dict[str, Any]]:
        if task_class is None:
            rows = self.db.execute("SELECT * FROM crew_performance WHERE crew_id=? ORDER BY id", (crew_id,)).fetchall()
        else:
            rows = self.db.execute("SELECT * FROM crew_performance WHERE crew_id=? AND task_class=? ORDER BY id", (crew_id, task_class)).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            item['verified'] = None if item['verified'] is None else bool(item['verified'])
            out.append(item)
        return out

    def performance_summary(self, crew_id: str, task_class: str) -> dict[str, Any]:
        rows = self.performance_history(crew_id, task_class)
        if not rows:
            return {
                'samples': 0, 'success_rate': 0.0, 'evidence_quality': 0.0,
                'verified_samples': 0, 'verification_rate': 0.0,
                'latency_ms': 0.0, 'cost_units': 0.0,
            }
        samples = len(rows)
        verified = [r for r in rows if r['verified'] is not None]
        return {
            'samples': samples,
            'success_rate': sum(1 for r in rows if r['status'] == 'completed') / samples,
            'evidence_quality': sum(float(r['evidence_quality']) for r in rows) / samples,
            'verified_samples': len(verified),
            'verification_rate': (sum(1 for r in verified if r['verified']) / len(verified)) if verified else 0.0,
            'latency_ms': sum(float(r['latency_ms']) for r in rows) / samples,
            'cost_units': sum(float(r['cost_units']) for r in rows) / samples,
        }
