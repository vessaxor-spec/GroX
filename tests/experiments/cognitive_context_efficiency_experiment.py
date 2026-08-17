from __future__ import annotations

import json
from pathlib import Path

from grox.crew.roster import CrewRoster


ROOT = Path(__file__).resolve().parents[2]
DOSSIERS = ROOT / "configs/crew/dossiers"
SPECIALISTS = ROOT / "configs/crew/specialists"


def _json_chars(value) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def main() -> None:
    roster = CrewRoster(DOSSIERS)
    compact = roster.cognitive_directory()
    legacy = [
        {
            "crew_id": crew.crew_id,
            "division": crew.division,
            "title": crew.title,
            "capabilities": sorted(crew.capabilities),
            "tags": sorted(crew.tags),
            "verification": crew.verification,
        }
        for crew in roster.all()
    ]

    compact_chars = _json_chars(compact)
    legacy_chars = _json_chars(legacy)
    reduction_ratio = 1.0 - (compact_chars / legacy_chars)
    craft_chars = sum(len(path.read_text(encoding="utf-8")) for path in SPECIALISTS.glob("*.md"))

    result = {
        "schema": "grox-cognitive-context-efficiency-v1",
        "standing_crew": len(compact),
        "all_crew_visible": len(compact) == len(roster.all()) == 82,
        "legacy_roster_chars": legacy_chars,
        "compact_directory_chars": compact_chars,
        "serialized_character_reduction_ratio": round(reduction_ratio, 4),
        "compact_fields": sorted(compact[0].keys()) if compact else [],
        "capabilities_serialized_to_cognition": any("capabilities" in entry for entry in compact),
        "expanded_tags_serialized_to_cognition": any("tags" in entry for entry in compact),
        "canonical_deep_craft_chars": craft_chars,
        "deep_craft_injected_by_directory": False,
        "qualification_gate": compact_chars <= int(legacy_chars * 0.80),
        "token_claim": False,
    }

    assert result["all_crew_visible"], result
    assert not result["capabilities_serialized_to_cognition"], result
    assert not result["expanded_tags_serialized_to_cognition"], result
    assert result["qualification_gate"], result
    print("COGNITIVE_CONTEXT_EFFICIENCY_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
