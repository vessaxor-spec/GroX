import json
import tempfile
import unittest
from pathlib import Path

from grox.crew.roster import CrewRoster
from grox.state import StateStore


class SpineTest(unittest.TestCase):
    @staticmethod
    def _write_dossier(directory: Path, *, crew_id: str, title: str, status: str = 'standing') -> None:
        (directory / f'{crew_id}.json').write_text(json.dumps({
            'crew_id': crew_id,
            'division': 'test',
            'title': title,
            'capabilities': ['repo_read'],
            'tags': ['test'],
            'status': status,
        }))

    def test_orchestrator_identity_variants_cannot_be_crew(self):
        cases = [
            ('orchestrator', 'Analyst'),
            ('agents-orchestrator', 'Analyst'),
            ('retired-orchestrator', 'Analyst'),
            ('legacy-orchestrator', 'Analyst'),
            ('backup-orchestrator', 'Analyst'),
            ('ordinary-analyst', 'Orchestrator'),
            ('ordinary-analyst', 'Retired Orchestrator'),
        ]
        for crew_id, title in cases:
            with self.subTest(crew_id=crew_id, title=title), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                dossier_dir = root / 'dossiers'
                dossier_dir.mkdir()
                self._write_dossier(dossier_dir, crew_id=crew_id, title=title)
                store = StateStore(root / 'state.sqlite3')
                try:
                    with self.assertRaises(ValueError):
                        CrewRoster(dossier_dir, store)
                finally:
                    store.close()

    def test_non_standing_dossier_cannot_enter_active_roster(self):
        for status in ('retired', 'archived'):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                dossier_dir = root / 'dossiers'
                dossier_dir.mkdir()
                self._write_dossier(dossier_dir, crew_id=f'{status}-analyst', title='Analyst', status=status)
                store = StateStore(root / 'state.sqlite3')
                try:
                    with self.assertRaises(ValueError):
                        CrewRoster(dossier_dir, store)
                finally:
                    store.close()

    def test_reconstitution_purges_stale_crew_operational_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dossier_dir = root / 'dossiers'
            dossier_dir.mkdir()
            self._write_dossier(dossier_dir, crew_id='architect', title='Architect')

            store = StateStore(root / 'state.sqlite3')
            try:
                store.ensure_crew('test-architecture-specialist')
                store.db.execute("UPDATE crew_state SET status='retired' WHERE crew_id='test-architecture-specialist'")
                store.remember(
                    kind='semantic',
                    scope='crew',
                    crew_id='test-architecture-specialist',
                    task_class=None,
                    memory_key='legacy',
                    content='legacy operational memory',
                    provenance={'test': True},
                )
                store.record_performance(
                    crew_id='test-architecture-specialist',
                    mission_id='MSN-history',
                    order_id='ORD-history',
                    task_class='legacy',
                    status='completed',
                    evidence_quality=1.0,
                    verified=True,
                    latency_ms=1.0,
                    cost_units=1.0,
                    risk='low',
                )
                store.db.execute(
                    "INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",
                    ('ORD-audit', 'MSN-audit', 'test-architecture-specialist', 'inspect', 'completed', '{}', 't', 't'),
                )
                store.db.commit()

                roster = CrewRoster(dossier_dir, store)
                self.assertEqual([d.crew_id for d in roster.all()], ['architect'])
                self.assertEqual(
                    store.db.execute("SELECT COUNT(*) FROM crew_state WHERE crew_id='test-architecture-specialist'").fetchone()[0],
                    0,
                )
                self.assertEqual(
                    store.db.execute("SELECT COUNT(*) FROM memories WHERE crew_id='test-architecture-specialist'").fetchone()[0],
                    0,
                )
                self.assertEqual(
                    store.db.execute("SELECT COUNT(*) FROM crew_performance WHERE crew_id='test-architecture-specialist'").fetchone()[0],
                    0,
                )
                self.assertEqual(
                    store.db.execute("SELECT COUNT(*) FROM orders WHERE order_id='ORD-audit'").fetchone()[0],
                    1,
                    'historical Mission/Order evidence must remain audit-only history',
                )
            finally:
                store.close()

    def test_canonical_command_spine_excludes_service_layers(self):
        root=Path(__file__).resolve().parents[2]
        instructions=(root/'AI_INSTRUCTIONS.md').read_text()
        cli=(root/'src/grox/cli.py').read_text()
        self.assertIn('Commander → Pilot GorXu → Divisions → Standing Crew',instructions)
        self.assertNotIn('Commander → Pilot GorXu → Mission Control → Divisions → Standing Crew',instructions)
        self.assertIn('Commander -> Pilot GorXu -> Divisions -> Standing Crew',cli)
