import json
import re
import statistics
import unittest
from pathlib import Path

from grox.crew.roster import CrewRoster


ROOT = Path(__file__).resolve().parents[2]
DOSSIERS = ROOT / "configs/crew/dossiers"
SPECIALISTS = ROOT / "configs/crew/specialists"
MANIFEST = ROOT / "configs/crew/company-manifest.json"
TEO_REPOSITORY = "vessaxor-spec/The-ever-evolving-orchestration-"
TEO_REVISION = "fab4cb1d16e6ed210bdf5555d8fbbe45a609e415"

REQUIRED_HEADINGS = (
    "## Identity",
    "## Purpose",
    "## Domain Context",
    "## Responsibilities",
    "## Non-Responsibilities",
    "## Inputs",
    "## Outputs",
    "## Safety Boundaries",
    "## GroX Operational Binding",
)


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("card has no YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise AssertionError("card has unterminated YAML frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"\'')
    return values


class SpecialistCraftLibraryTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text())
        self.dossier_ids = {p.stem for p in DOSSIERS.glob("*.json")}
        self.card_paths = sorted(SPECIALISTS.glob("*.md"))
        self.card_ids = {p.stem for p in self.card_paths}

    def test_every_active_dossier_has_exactly_one_canonical_craft_card(self):
        self.assertEqual(len(self.dossier_ids), 82)
        self.assertEqual(len(self.card_paths), 82)
        self.assertEqual(self.card_ids, self.dossier_ids)
        self.assertNotIn("agents-orchestrator", self.card_ids)
        self.assertNotIn("orchestrator", self.card_ids)
        self.assertNotIn("gorxu", self.card_ids)
        self.assertNotIn("pilot", self.card_ids)
        self.assertNotIn("mission-control", self.card_ids)
        for crew_id in self.card_ids:
            self.assertNotIn("orchestrator", crew_id.lower())

    def test_cards_have_required_structure_and_non_placeholder_depth(self):
        sizes = []
        line_counts = []
        for path in self.card_paths:
            with self.subTest(card=path.name):
                text = path.read_text(encoding="utf-8")
                fm = _frontmatter(text)
                self.assertEqual(fm.get("name"), path.stem)
                for key in ("name", "description", "domains", "freshness_policy"):
                    self.assertIn(key, fm)
                self.assertTrue("category" in fm or "division" in fm)
                for heading in REQUIRED_HEADINGS:
                    self.assertIn(heading, text)
                self.assertGreaterEqual(len(text), 4000)
                self.assertGreaterEqual(len(text.splitlines()), 80)
                self.assertNotIn("## TEO Allocation", text)
                self.assertNotIn("agents-orchestrator", text.lower())
                self.assertIn("Pilot GorXu", text)
                self.assertIn("Mission authority", text)
                self.assertIn("Repair permission", text)
                sizes.append(len(text))
                line_counts.append(len(text.splitlines()))
        self.assertGreaterEqual(statistics.median(sizes), 8000)
        self.assertGreaterEqual(statistics.median(line_counts), 120)

    def test_specialist_inspired_cards_are_attributable_to_one_pinned_source_revision(self):
        roles = set(self.manifest["roles"])
        self.assertEqual(len(roles), 81)
        for crew_id in sorted(roles):
            with self.subTest(crew_id=crew_id):
                text = (SPECIALISTS / f"{crew_id}.md").read_text(encoding="utf-8")
                fm = _frontmatter(text)
                self.assertEqual(fm.get("source_repository"), TEO_REPOSITORY)
                self.assertEqual(fm.get("source_revision"), TEO_REVISION)
                self.assertEqual(fm.get("source_card"), f"community/specialists/{crew_id}.md")
                self.assertRegex(fm.get("source_content_sha256", ""), r"^[0-9a-f]{64}$")
                self.assertEqual(fm.get("grox_binding"), "standing-crew")

        native = _frontmatter((SPECIALISTS / "independent-verifier.md").read_text(encoding="utf-8"))
        self.assertEqual(native.get("source_repository"), "GroX-native")
        self.assertEqual(native.get("grox_binding"), "standing-crew")

    def test_independent_verifier_card_preserves_independence_and_non_activation(self):
        text = (SPECIALISTS / "independent-verifier.md").read_text(encoding="utf-8")
        self.assertIn("## Independence Doctrine", text)
        self.assertIn("## Evidence Standard", text)
        self.assertIn("## PASS / FAIL Decision Rules", text)
        self.assertIn("## When Verification Applies", text)
        self.assertIn("Never PASS work executed by the same Crew identity", text)
        self.assertIn("Verification cannot self-activate", text)
        self.assertIn("Verify-only work is read-only", text)

    def test_incident_role_does_not_create_a_second_vessel_commander(self):
        text = (SPECIALISTS / "incident-commander.md").read_text(encoding="utf-8")
        self.assertIn("### Vessel command clarification", text)
        self.assertIn("does not supersede the human Commander", text)
        self.assertNotIn("agents-orchestrator", text.lower())

    def test_orchestration_evaluation_remains_advisory(self):
        text = (SPECIALISTS / "orchestration-evaluation-analyst.md").read_text(encoding="utf-8")
        self.assertIn("### Evaluation non-activation boundary", text)
        self.assertIn("evaluation cannot self-activate", text.lower())
        self.assertIn("Proposals return to GorXu", text)

    def test_roster_still_loads_dossiers_and_resolves_craft_additively(self):
        roster = CrewRoster(DOSSIERS)
        self.assertEqual(len(roster.all()), 82)
        backend = roster.get("backend-engineer")
        self.assertIn("repo_read", backend.capabilities)
        craft = roster.craft_card("backend-engineer")
        self.assertIn("## Identity", craft)
        self.assertIn("## GroX Operational Binding", craft)
        with self.assertRaises(KeyError):
            roster.craft_card("gorxu")


if __name__ == "__main__":
    unittest.main()
