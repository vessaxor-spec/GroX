import unittest
from pathlib import Path
import tempfile

from grox.tools.gateway import ToolGateway, ToolDenied
from grox.contracts import MissionOrder, MissionMode


class GatewayTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.root = Path(self.t.name)
        self.g = ToolGateway(self.root)

    def tearDown(self):
        self.t.cleanup()

    def order(self, mode, allowed, scope=["."]):
        return MissionOrder.new(
            "M", "i", "o", mode, "backend-engineer",
            allowed_actions=allowed, scope=scope,
        )

    def test_path_escape_denied(self):
        order = self.order(MissionMode.inspect, ["fs_read"])
        with self.assertRaises(ToolDenied):
            self.g.read_text(order, "../x")

    def test_inspect_write_denied_even_if_listed(self):
        order = self.order(MissionMode.inspect, ["fs_read"])
        order.allowed_actions.append("fs_write")  # simulate corrupted/deserialized grant
        with self.assertRaises(ToolDenied):
            self.g.write_text(order, "x", "y")

    def test_execute_write_denied_even_if_grant_is_injected(self):
        order = self.order(MissionMode.execute, ["fs_read"])
        order.allowed_actions.append("fs_write")  # defense-in-depth beyond MissionOrder validation
        with self.assertRaisesRegex(ToolDenied, "explicit Repair authority"):
            self.g.write_text(order, "x", "y")

    def test_repair_write_in_scope(self):
        order = self.order(MissionMode.repair, ["fs_write"], ["x.txt"])
        result = self.g.write_text(order, "x.txt", "ok")
        self.assertEqual((self.root / "x.txt").read_text(), "ok")
        self.assertEqual(result["path"], "x.txt")


if __name__ == "__main__":
    unittest.main()
