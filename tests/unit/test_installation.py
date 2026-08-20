from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from grox.installation import (
    InstallationError,
    WORKSPACE_DIRECTORIES,
    commission_workspace,
    default_workspace,
    load_workspace_binding,
    platform_config_dir,
    workspace_binding_file,
    workspace_marker_file,
    workspace_status,
)


class InstallationTests(unittest.TestCase):
    def test_default_workspace_uses_user_home(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.assertEqual(default_workspace(home=home), home / "GroX")

    def test_linux_config_uses_default_xdg_location(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.assertEqual(
                platform_config_dir(system="Linux", environ={}, home=home),
                home / ".config" / "grox",
            )

    def test_linux_config_honors_absolute_xdg_config_home(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            xdg = root / "xdg"
            self.assertEqual(
                platform_config_dir(
                    system="Linux",
                    environ={"XDG_CONFIG_HOME": str(xdg)},
                    home=root / "home",
                ),
                xdg / "grox",
            )

    def test_linux_config_rejects_relative_xdg_config_home(self) -> None:
        with self.assertRaisesRegex(InstallationError, "XDG_CONFIG_HOME must be absolute"):
            platform_config_dir(
                system="Linux",
                environ={"XDG_CONFIG_HOME": "relative/config"},
                home="/tmp/example-home",
            )

    def test_macos_config_uses_application_support(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            self.assertEqual(
                platform_config_dir(system="Darwin", environ={}, home=home),
                home / "Library" / "Application Support" / "GroX",
            )

    def test_unsupported_platform_fails_closed(self) -> None:
        with self.assertRaisesRegex(InstallationError, "not yet supported"):
            platform_config_dir(system="Windows", environ={}, home="/tmp/home")

    def test_unconfigured_status_reports_default_without_creating_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            config = root / "config"
            report = workspace_status(
                config_dir=config,
                system="Linux",
                environ={},
                home=home,
            )
            self.assertFalse(report["configured"])
            self.assertFalse(report["commissioned"])
            self.assertEqual(report["workspace"], str((home / "GroX").resolve()))
            self.assertFalse(config.exists())
            self.assertFalse((home / "GroX").exists())

    def test_commission_creates_bounded_workspace_and_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            result = commission_workspace(
                workspace,
                config_dir=config,
                system="Linux",
                environ={},
                home=root / "home",
            )
            self.assertEqual(result.status, "created")
            self.assertEqual(result.workspace, workspace.resolve())
            self.assertEqual(set(result.created_directories), set(WORKSPACE_DIRECTORIES))
            self.assertTrue(workspace_marker_file(workspace).is_file())
            self.assertTrue(workspace_binding_file(config_dir=config).is_file())
            for name in WORKSPACE_DIRECTORIES:
                self.assertTrue((workspace / name).is_dir(), name)
            self.assertEqual(
                load_workspace_binding(config_dir=config), workspace.resolve()
            )
            report = workspace_status(config_dir=config, home=root / "home")
            self.assertTrue(report["configured"])
            self.assertTrue(report["commissioned"])
            self.assertEqual(report["workspace"], str(workspace.resolve()))

    def test_commission_is_idempotent_for_same_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            first = commission_workspace(workspace, config_dir=config)
            second = commission_workspace(workspace, config_dir=config)
            self.assertEqual(first.status, "created")
            self.assertEqual(second.status, "existing")
            self.assertEqual(second.created_directories, ())
            self.assertEqual(load_workspace_binding(config_dir=config), workspace.resolve())

    def test_nonempty_unrelated_directory_is_not_claimed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "occupied"
            workspace.mkdir()
            (workspace / "unrelated.txt").write_text("keep me", encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "Refusing to claim"):
                commission_workspace(workspace, config_dir=root / "config")
            self.assertEqual((workspace / "unrelated.txt").read_text(), "keep me")
            self.assertFalse(workspace_marker_file(workspace).exists())

    def test_workspace_path_that_is_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "not-a-directory"
            workspace.write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "not a directory"):
                commission_workspace(workspace, config_dir=root / "config")

    def test_layout_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            state_dir = workspace / "state"
            state_dir.rmdir()
            state_dir.write_text("collision", encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "layout collision"):
                commission_workspace(workspace, config_dir=config)

    def test_malformed_binding_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            binding = workspace_binding_file(config_dir=config)
            binding.parent.mkdir(parents=True)
            binding.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "Malformed GroX workspace binding"):
                load_workspace_binding(config_dir=config)

    def test_relative_binding_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            binding = workspace_binding_file(config_dir=config)
            binding.parent.mkdir(parents=True)
            binding.write_text(
                json.dumps(
                    {
                        "kind": "grox-workspace-binding",
                        "schema_version": 1,
                        "workspace": "relative/workspace",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(InstallationError, "must be absolute"):
                load_workspace_binding(config_dir=config, require_marker=False)

    def test_missing_marker_on_configured_workspace_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            workspace_marker_file(workspace).unlink()
            with self.assertRaisesRegex(InstallationError, "missing its marker"):
                load_workspace_binding(config_dir=config)

    def test_wrong_marker_kind_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            marker = workspace_marker_file(workspace)
            payload = json.loads(marker.read_text(encoding="utf-8"))
            payload["kind"] = "not-grox"
            marker.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "Invalid GroX workspace marker kind"):
                load_workspace_binding(config_dir=config)

    def test_marker_path_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "vessel"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            marker = workspace_marker_file(workspace)
            payload = json.loads(marker.read_text(encoding="utf-8"))
            payload["workspace"] = str(root / "other")
            marker.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(InstallationError, "marker path mismatch"):
                load_workspace_binding(config_dir=config)

    def test_implicit_rebind_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "config"
            first = root / "first"
            second = root / "second"
            commission_workspace(first, config_dir=config)
            with self.assertRaisesRegex(InstallationError, "already bound"):
                commission_workspace(second, config_dir=config)
            self.assertFalse(second.exists())
            self.assertEqual(load_workspace_binding(config_dir=config), first.resolve())


if __name__ == "__main__":
    unittest.main()
