from pathlib import Path
import tomllib
import unittest

import grox


class VersionConsistencyTest(unittest.TestCase):
    def test_source_version_matches_package_metadata(self) -> None:
        root = Path(__file__).resolve().parents[2]
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(grox.__version__, project["project"]["version"])


if __name__ == "__main__":
    unittest.main()
