import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_IDENTITY = "-".join(("systems", "architect"))
LEGACY_CREW_STATUS = "".join(("ret", "ired"))


class CurrentCrewTerminologyTest(unittest.TestCase):
    def test_obsolete_identity_token_is_absent_from_current_text_tree(self):
        findings = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8").lower()
            except (UnicodeDecodeError, OSError):
                continue
            if FORBIDDEN_IDENTITY in text:
                findings.append(str(path.relative_to(ROOT)))
        self.assertEqual(findings, [])

    def test_legacy_crew_status_term_is_absent_outside_specialist_craft(self):
        findings = []
        specialist_root = ROOT / "configs" / "crew" / "specialists"
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            try:
                path.relative_to(specialist_root)
                continue
            except ValueError:
                pass
            try:
                text = path.read_text(encoding="utf-8").lower()
            except (UnicodeDecodeError, OSError):
                continue
            if LEGACY_CREW_STATUS in text:
                findings.append(str(path.relative_to(ROOT)))
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
