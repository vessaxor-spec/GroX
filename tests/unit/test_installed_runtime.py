from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from grox.installation import InstallationError, commission_workspace, installed_vessel_layout
from grox.runtime_assets import RuntimeAssetError, validate_asset_root


class InstalledRuntimeTests(unittest.TestCase):
    def _asset_root(self, root: Path, *, count: int = 82) -> Path:
        assets = root / "assets"
        dossiers = assets / "configs" / "crew" / "dossiers"
        specialists = assets / "configs" / "crew" / "specialists"
        dossiers.mkdir(parents=True)
        specialists.mkdir(parents=True)
        (assets / "configs" / "tool-policy.json").write_text("{}\n", encoding="utf-8")
        (assets / "configs" / "crew" / "company-manifest.json").write_text(
            "{}\n", encoding="utf-8"
        )
        for index in range(count):
            crew_id = f"crew-{index:03d}"
            (dossiers / f"{crew_id}.json").write_text(
                json.dumps({"crew_id": crew_id}) + "\n", encoding="utf-8"
            )
            (specialists / f"{crew_id}.md").write_text(
                f"# {crew_id}\n", encoding="utf-8"
            )
        return assets

    def test_canonical_source_runtime_assets_validate(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(validate_asset_root(root), root.resolve())

    def test_missing_standing_crew_dossier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            assets = self._asset_root(Path(td))
            next((assets / "configs" / "crew" / "dossiers").glob("*.json")).unlink()
            with self.assertRaisesRegex(RuntimeAssetError, "exactly 82 Standing Crew dossiers"):
                validate_asset_root(assets)

    def test_malformed_dossier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            assets = self._asset_root(Path(td))
            target = next((assets / "configs" / "crew" / "dossiers").glob("*.json"))
            target.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeAssetError, "Malformed packaged Crew dossier"):
                validate_asset_root(assets)

    def test_dossier_and_craft_identity_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            assets = self._asset_root(Path(td))
            target = next((assets / "configs" / "crew" / "specialists").glob("*.md"))
            target.rename(target.with_name("orphan-craft.md"))
            with self.assertRaisesRegex(RuntimeAssetError, "Crew/craft identity mismatch"):
                validate_asset_root(assets)

    def test_dossier_filename_identity_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            assets = self._asset_root(Path(td))
            target = next((assets / "configs" / "crew" / "dossiers").glob("*.json"))
            target.write_text(json.dumps({"crew_id": "wrong-id"}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeAssetError, "dossier identity mismatch"):
                validate_asset_root(assets)

    def test_installed_layout_requires_commissioned_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            assets = self._asset_root(root)
            with self.assertRaisesRegex(InstallationError, "No commissioned GroX workspace"):
                installed_vessel_layout(
                    config_dir=root / "config",
                    system="Linux",
                    environ={},
                    home=root / "home",
                    asset_root=assets,
                )

    def test_installed_layout_separates_assets_state_and_commander_work(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            assets = self._asset_root(root)
            workspace = root / "GroX"
            config = root / "config"
            commission_workspace(
                workspace,
                config_dir=config,
                system="Linux",
                environ={},
                home=root / "home",
            )
            layout = installed_vessel_layout(
                config_dir=config,
                system="Linux",
                environ={},
                home=root / "home",
                asset_root=assets,
            )
            self.assertFalse(layout.legacy_single_root)
            self.assertEqual(layout.asset_root, assets.resolve())
            self.assertEqual(layout.state_root, (workspace / "state").resolve())
            self.assertEqual(layout.work_root, (workspace / "workspace").resolve())
            self.assertNotEqual(layout.asset_root, layout.state_root)
            self.assertNotEqual(layout.asset_root, layout.work_root)
            self.assertNotEqual(layout.state_root, layout.work_root)

    def test_installed_layout_rejects_incomplete_runtime_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            assets = self._asset_root(root, count=81)
            workspace = root / "GroX"
            config = root / "config"
            commission_workspace(workspace, config_dir=config)
            with self.assertRaisesRegex(InstallationError, "exactly 82 Standing Crew dossiers"):
                installed_vessel_layout(config_dir=config, asset_root=assets)


if __name__ == "__main__":
    unittest.main()
