from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ("systems-" + "architect", "ret" + "ired")


class CurrentCrewTerminologyContract(unittest.TestCase):
    def test_tracked_current_tree_contains_no_obsolete_crew_terms(self) -> None:
        proc = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        violations: list[str] = []
        for raw_path in proc.stdout.split(b"\0"):
            if not raw_path:
                continue
            rel = raw_path.decode("utf-8")
            path = ROOT / rel
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for token in FORBIDDEN:
                if token in text:
                    violations.append(f"{rel}: {token}")
        self.assertFalse(
            violations,
            "obsolete Crew terminology remains in the current tracked tree:\n"
            + "\n".join(sorted(violations)),
        )


if __name__ == "__main__":
    unittest.main()
