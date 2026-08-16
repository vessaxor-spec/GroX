import os
import tempfile
import unittest
from pathlib import Path

from grox.vessel import VesselRootError, resolve_vessel_root


def make_vessel(root: Path) -> None:
    (root / "configs/crew/dossiers").mkdir(parents=True)
    (root / "configs/tool-policy.json").write_text("{}")
    (root / "pyproject.toml").write_text("[project]\nname='grox-vessel'\n")


class VesselRootTests(unittest.TestCase):
    def test_environment_binding_has_priority(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as elsewhere:
            root = Path(td)
            make_vessel(root)
            resolved = resolve_vessel_root(
                cwd=Path(elsewhere),
                module_file=Path(elsewhere) / "site-packages/grox/vessel.py",
                environ={"GROX_VESSEL_ROOT": str(root)},
            )
            self.assertEqual(resolved, root.resolve())

    def test_invalid_environment_binding_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(VesselRootError, "does not point to a valid GroX Vessel root"):
                resolve_vessel_root(environ={"GROX_VESSEL_ROOT": td})

    def test_installed_runtime_finds_current_source_checkout(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as site:
            root = Path(td)
            make_vessel(root)
            nested = root / "docs" / "nested"
            nested.mkdir(parents=True)
            resolved = resolve_vessel_root(
                cwd=nested,
                module_file=Path(site) / "site-packages/grox/vessel.py",
                environ={},
            )
            self.assertEqual(resolved, root.resolve())

    def test_source_module_fallback_supports_editable_checkout(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as elsewhere:
            root = Path(td)
            make_vessel(root)
            module_file = root / "src/grox/vessel.py"
            module_file.parent.mkdir(parents=True)
            module_file.write_text("# sentinel\n")
            resolved = resolve_vessel_root(cwd=Path(elsewhere), module_file=module_file, environ={})
            self.assertEqual(resolved, root.resolve())

    def test_unbound_installed_runtime_refuses_empty_vessel(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as site:
            with self.assertRaisesRegex(VesselRootError, "Refusing to start an empty Vessel"):
                resolve_vessel_root(
                    cwd=Path(cwd),
                    module_file=Path(site) / "site-packages/grox/vessel.py",
                    environ={},
                )


if __name__ == "__main__":
    unittest.main()
