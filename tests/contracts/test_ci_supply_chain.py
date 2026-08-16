from __future__ import annotations

import re
import unittest
from pathlib import Path


class CISupplyChainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[2]

    def test_external_actions_are_pinned_to_full_commit_sha(self) -> None:
        workflows = sorted((self.root / ".github" / "workflows").glob("*.y*ml"))
        self.assertTrue(workflows)
        pattern = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
        sha = re.compile(r"^[0-9a-f]{40}$")
        failures: list[str] = []
        for path in workflows:
            for value in pattern.findall(path.read_text(encoding="utf-8")):
                if value.startswith("./"):
                    continue
                if "@" not in value:
                    failures.append(f"{path}: missing ref: {value}")
                    continue
                ref = value.rsplit("@", 1)[1]
                if not sha.fullmatch(ref):
                    failures.append(f"{path}: mutable action ref: {value}")
        self.assertEqual([], failures, "\n".join(failures))

    def test_ci_matrix_covers_claimed_supported_python_versions(self) -> None:
        text = (self.root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for version in ("3.11", "3.12", "3.13", "3.14"):
            self.assertIn(f"'{version}'", text)


if __name__ == "__main__":
    unittest.main()
