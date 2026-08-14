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
