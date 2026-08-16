from pathlib import Path
import tomllib

import grox


def test_source_version_matches_package_metadata() -> None:
    root = Path(__file__).resolve().parents[2]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert grox.__version__ == project["project"]["version"]
