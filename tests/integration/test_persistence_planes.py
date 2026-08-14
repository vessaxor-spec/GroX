from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from grox.persistence import PersistenceManager, SNAPSHOT_SCHEMA
from grox.state import StateStore


class PersistencePlaneTests(unittest.TestCase):
    def make_root(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / 'configs/state').mkdir(parents=True)
        (root / 'configs/persistence').mkdir(parents=True)
        binding = {
            'cognitive_home': {'type':'chatgpt_project','project':'Space Exploration','pilot_identity':'GorXu'},
            'vessel_source': {'type':'git','repository':'vessaxor-spec/GroX','branch':'main'},
        }
        (root / 'configs/persistence/project-binding.json').write_text(json.dumps(binding))
        store = StateStore(root / 'configs/state/grox.sqlite3')
        return td, root, store

    def test_snapshot_is_private_state_archive_with_integrity_manifest(self):
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-test','preserve state','inspect','low')
            store.update_mission('MSN-test','completed','done')
            pm = PersistenceManager(root)
            report = pm.create_snapshot(label='test')
            self.assertTrue(report.valid, report.errors)
            self.assertEqual(report.manifest['schema'], SNAPSHOT_SCHEMA)
            self.assertEqual(report.manifest['sensitivity'], 'private_runtime_state')
            self.assertEqual(report.manifest['project_binding']['project'], 'Space Exploration')
            self.assertTrue(Path(report.path).exists())
        finally:
            td.cleanup()

    def test_restore_requires_explicit_confirmation_and_restores_previous_state(self):
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-original','original','inspect','low')
            store.update_mission('MSN-original','completed','original complete')
            pm = PersistenceManager(root)
            snap = Path(pm.create_snapshot(label='original').path)
            store.create_mission('MSN-later','later','inspect','low')
            store.update_mission('MSN-later','completed','later complete')
            store.db.close()

            with self.assertRaises(PermissionError):
                pm.restore_snapshot(snap)
            result = pm.restore_snapshot(snap, confirm=True)
            self.assertTrue(result['restored'])

            db = sqlite3.connect(root / 'configs/state/grox.sqlite3')
            ids = {row[0] for row in db.execute('SELECT mission_id FROM missions')}
            db.close()
            self.assertIn('MSN-original', ids)
            self.assertNotIn('MSN-later', ids)
            self.assertTrue(result['pre_restore_snapshot'])
        finally:
            td.cleanup()

    def test_corrupted_snapshot_fails_verification(self):
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-test','state','inspect','low')
            store.update_mission('MSN-test','completed','done')
            store.db.close()
            pm = PersistenceManager(root)
            snap = Path(pm.create_snapshot(label='good').path)
            raw = bytearray(snap.read_bytes())
            raw[-8:] = b'BROKEN!!'
            bad = snap.with_name('bad.groxstate')
            bad.write_bytes(raw)
            report = pm.verify_snapshot(bad)
            self.assertFalse(report.valid)
        finally:
            td.cleanup()


if __name__ == '__main__':
    unittest.main()
