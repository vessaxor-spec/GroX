import json
import re
import unittest
from pathlib import Path

from grox.crew.roster import CrewRoster

ROOT = Path(__file__).resolve().parents[2]
DOSSIERS = ROOT / "configs" / "crew" / "dossiers"
CARDS = ROOT / "configs" / "crew" / "specialists"

STOP = {
    "a",
    "an",
    "and",
    "or",
    "the",
    "of",
    "for",
    "to",
    "in",
    "on",
    "by",
    "with",
    "from",
    "into",
    "across",
    "via",
    "using",
    "use",
    "any",
}
KEEP_SHORT = {"ai", "ml", "ux", "ui", "ip", "qa", "xr", "zk"}


def _unique(items):
    seen = set()
    result = []
    for item in items:
        item = str(item).strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'").strip()


def _card_domains(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"missing frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError(f"unclosed frontmatter: {path}") from exc

    domains = []
    active = False
    for line in lines[1:end]:
        inline = re.match(r"^domains:\s*\[(.*)\]\s*$", line)
        if inline:
            domains.extend(_clean(item) for item in inline.group(1).split(","))
            active = False
            continue
        if re.match(r"^domains:\s*$", line):
            active = True
            continue
        if active:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                domains.append(_clean(item.group(1)))
                continue
            if line and not line.startswith((" ", "\t")):
                break

    domains = _unique(domains)
    if not domains:
        raise AssertionError(f"no domains in canonical card: {path}")
    return domains


def _routing_terms(domains: list[str]) -> list[str]:
    terms = []
    for domain in domains:
        slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")
        if slug and slug not in STOP:
            terms.append(slug)
        for token in re.findall(r"[a-z0-9]+", domain.lower()):
            if token in STOP:
                continue
            if len(token) >= 3 or token in KEEP_SHORT:
                terms.append(token)
    return _unique(terms)


class CrewDossierMetadataTest(unittest.TestCase):
    def test_all_dossiers_are_enriched_from_their_canonical_craft_card(self):
        dossier_paths = sorted(DOSSIERS.glob("*.json"))
        card_paths = sorted(CARDS.glob("*.md"))
        self.assertEqual(len(dossier_paths), 82)
        self.assertEqual({p.stem for p in dossier_paths}, {p.stem for p in card_paths})

        for path in dossier_paths:
            with self.subTest(crew_id=path.stem):
                dossier = json.loads(path.read_text(encoding="utf-8"))
                domains = _card_domains(CARDS / f"{path.stem}.md")
                derived_tags = set(_routing_terms(domains))

                self.assertEqual(dossier["domains"], domains)
                self.assertTrue(set(domains).issubset(set(dossier["skills"])))
                self.assertTrue(derived_tags.issubset(set(dossier["tags"])))
                self.assertGreaterEqual(len(dossier["skills"]), 4)
                self.assertGreaterEqual(len(dossier["tags"]), 5)

    def test_metadata_does_not_replace_capability_gating(self):
        roster = CrewRoster(DOSSIERS)
        self.assertEqual(len(roster.all()), 82)

        for path in sorted(DOSSIERS.glob("*.json")):
            with self.subTest(crew_id=path.stem):
                raw = json.loads(path.read_text(encoding="utf-8"))
                crew = roster.get(path.stem)
                self.assertEqual(crew.capabilities, frozenset(raw["capabilities"]))
                self.assertEqual(crew.tags, frozenset(raw["tags"]))

    def test_pre_enrichment_domain_routing_contract_remains_stable(self):
        roster = CrewRoster(DOSSIERS)
        cases = {
            "database reliability failure resilience": "database-reliability-engineer",
            "aerospace satellite systems constraints": "aerospace-satellite-engineer",
            "privacy engineering controls": "privacy-engineer",
            "fraud forensic investigation evidence": "fraud-forensic-investigation-specialist",
            "orchestration evaluation routing metrics": "orchestration-evaluation-analyst",
        }
        for objective, expected in cases.items():
            with self.subTest(objective=objective):
                self.assertEqual(roster.select(objective, ["repo_read"]).crew_id, expected)


if __name__ == "__main__":
    unittest.main()
