from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from grox.contracts import MissionMode, MissionOrder, RiskClass
from grox.pilot import PilotGorXu
from grox.runtime_layout import RuntimeLayoutError, VesselLayout
from grox.tools.gateway import ToolDenied
from grox.tools.policy import GatewayPolicy


REPO = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VesselLayoutTests(unittest.TestCase):
    def test_legacy_layout_preserves_historical_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            layout = VesselLayout.legacy(root)
            self.assertTrue(layout.legacy_single_root)
            self.assertEqual(layout.asset_root, root)
            self.assertEqual(layout.state_root, root)
            self.assertEqual(layout.work_root, root)
            self.assertEqual(
                layout.state_path("grox.sqlite3"),
                root / "configs" / "state" / "grox.sqlite3",
            )
            self.assertEqual(
                layout.asset_path("configs/tool-policy.json"),
                root / "configs" / "tool-policy.json",
            )

    def test_separated_layout_uses_direct_private_state_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            layout = VesselLayout.separated(
                asset_root=root / "assets",
                state_root=root / "state",
                work_root=root / "work",
            )
            self.assertFalse(layout.legacy_single_root)
            self.assertEqual(layout.state_path("grox.sqlite3"), (root / "state" / "grox.sqlite3").resolve())
            self.assertEqual(layout.work_path("notes.txt"), (root / "work" / "notes.txt").resolve())

    def test_separated_layout_rejects_overlapping_roots(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(RuntimeLayoutError, "must not overlap"):
                VesselLayout.separated(
                    asset_root=root / "assets",
                    state_root=root / "work" / "state",
                    work_root=root / "work",
                )

    def test_legacy_layout_rejects_nonidentical_roles(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(RuntimeLayoutError, "to be identical"):
                VesselLayout(
                    root / "assets",
                    root / "state",
                    root / "work",
                    legacy_single_root=True,
                )


class SeparatedPilotTests(unittest.TestCase):
    def test_pilot_separates_runtime_state_and_commander_work(self) -> None:
        policy_path = REPO / "configs" / "tool-policy.json"
        policy_before = sha256(policy_path)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = root / "state"
            work = root / "work"
            (work / "tests").mkdir(parents=True)
            (work / "notes.txt").write_text("Commander workspace evidence\n", encoding="utf-8")
            (work / "tests" / "test_smoke.py").write_text(
                "import unittest\n\n"
                "class Smoke(unittest.TestCase):\n"
                "    def test_workspace(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )

            layout = VesselLayout.separated(
                asset_root=REPO,
                state_root=state,
                work_root=work,
            )
            pilot = PilotGorXu(layout, reasoner=None)
            try:
                self.assertEqual(pilot.layout, layout)
                self.assertEqual(pilot.root, work.resolve())
                self.assertEqual(pilot.asset_root, REPO.resolve())
                self.assertEqual(pilot.state_root, state.resolve())
                self.assertEqual(pilot.gateway.root, work.resolve())
                self.assertEqual(pilot.gateway.asset_root, REPO.resolve())
                self.assertEqual(pilot.gateway.state_storage_root, state.resolve())
                self.assertEqual(pilot.gateway._browser.root, state.resolve())
                self.assertEqual(len(pilot.roster.all()), 82)
                self.assertTrue((state / "grox.sqlite3").is_file())
                self.assertFalse((work / "configs" / "state" / "grox.sqlite3").exists())
                self.assertEqual(
                    pilot.gateway.policy,
                    GatewayPolicy.from_file(policy_path),
                )

                result = pilot.command(
                    "Inspect Commander workspace",
                    mode=MissionMode.inspect,
                    risk=RiskClass.low,
                    scope=".",
                )
                self.assertEqual(result["status"], "completed")
                self.assertEqual(result["outcome"]["effect"], "inspection")
                self.assertFalse(result["outcome"]["mutation"])
                self.assertTrue((state / "grox.sqlite3").is_file())
                self.assertEqual((work / "notes.txt").read_text(encoding="utf-8"), "Commander workspace evidence\n")
                self.assertEqual(sha256(policy_path), policy_before)

                order = MissionOrder.new(
                    "MSN-layout-boundary",
                    "Inspect bounded Commander work",
                    "Read only inside Commander work root",
                    MissionMode.inspect,
                    "repository-inspector",
                    allowed_actions=["fs_read"],
                    forbidden_actions=["fs_write"],
                    scope=["."],
                    risk_class=RiskClass.low,
                )
                with self.assertRaisesRegex(ToolDenied, "escapes Vessel root"):
                    pilot.gateway.read_text(order, "../state/grox.sqlite3")
                with self.assertRaisesRegex(ToolDenied, "escapes Vessel root"):
                    pilot.gateway.read_text(order, str(policy_path.resolve()))
            finally:
                pilot.store.close()


if __name__ == "__main__":
    unittest.main()
