from __future__ import annotations

import json
import sqlite3
import tempfile
from unittest.mock import patch
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
            with patch.object(pm, '_git_commit', return_value='exact-source-commit'):
                snap = Path(pm.create_snapshot(label='original').path)
            store.create_mission('MSN-later','later','inspect','low')
            store.update_mission('MSN-later','completed','later complete')
            store.db.close()

            with self.assertRaises(PermissionError):
                pm.restore_snapshot(snap)
            with patch.object(pm, '_git_commit', return_value='exact-source-commit'):
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

    def test_persisting_order_seals_nested_authority_parameters(self):
        from grox.contracts import MissionMode, MissionOrder
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-order','order sealing','execute','low')
            order = MissionOrder.new(
                'MSN-order','intent','objective',MissionMode.execute,'researcher',
                allowed_actions=['net_fetch'],
                parameters={'allowed_origins':['https://example.com']},
            )
            self.assertFalse(order.sealed)
            store.save_order(order)
            self.assertTrue(order.sealed)
            self.assertEqual(order.parameters['allowed_origins'], ('https://example.com',))
            with self.assertRaises(TypeError):
                order.parameters['allowed_origins'] += ('https://evil.example',)
        finally:
            td.cleanup()

    def test_restore_rejects_source_mismatch_without_explicit_ancestor_allowance(self):
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-original','original','inspect','low')
            store.update_mission('MSN-original','completed','done')
            pm = PersistenceManager(root)
            with patch.object(pm, '_git_commit', return_value='older-source'):
                snap = Path(pm.create_snapshot(label='older').path)
            store.db.close()

            with patch.object(pm, '_git_commit', return_value='newer-source'), \
                 patch('grox.persistence.subprocess.run') as ancestry:
                ancestry.return_value.returncode = 0
                with self.assertRaisesRegex(ValueError, 'allow_ancestor=True'):
                    pm.restore_snapshot(snap, confirm=True)

            with patch.object(pm, '_git_commit', return_value='newer-source'), \
                 patch('grox.persistence.subprocess.run') as ancestry:
                ancestry.return_value.returncode = 0
                result = pm.restore_snapshot(snap, confirm=True, allow_ancestor=True)
                self.assertTrue(result['restored'])
        finally:
            td.cleanup()

    def test_restore_rejects_non_ancestor_source_even_with_ancestor_allowance(self):
        td, root, store = self.make_root()
        try:
            store.create_mission('MSN-original','original','inspect','low')
            store.update_mission('MSN-original','completed','done')
            pm = PersistenceManager(root)
            with patch.object(pm, '_git_commit', return_value='unrelated-source'):
                snap = Path(pm.create_snapshot(label='unrelated').path)
            store.db.close()

            with patch.object(pm, '_git_commit', return_value='current-source'), \
                 patch('grox.persistence.subprocess.run') as ancestry:
                ancestry.return_value.returncode = 1
                with self.assertRaisesRegex(ValueError, 'not compatible'):
                    pm.restore_snapshot(snap, confirm=True, allow_ancestor=True)
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
