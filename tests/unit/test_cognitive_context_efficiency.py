import json
import unittest
from pathlib import Path
from unittest.mock import patch

from grox.crew.roster import CrewRoster
from grox.pilot import PilotGorXu
from grox.reasoning import CognitiveUsage
from grox.reasoning.contracts import MissionInterpretation
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from tests._support import temp_vessel


ROOT = Path(__file__).resolve().parents[2]
DOSSIERS = ROOT / "configs/crew/dossiers"


def valid_interpretation(directive: str, crew_id: str = "backend-engineer") -> dict:
    return {
        "commander_intent": directive,
        "objective": "Inspect the requested backend evidence",
        "ambiguous": False,
        "ambiguities": [],
        "assumptions": [],
        "information_needs": ["Inspect repository evidence"],
        "candidate_crew_ids": [crew_id],
        "options": [
            {
                "name": "inspect-first",
                "rationale": "Gather bounded evidence before any change.",
                "advantages": ["preserves authority boundaries"],
                "risks": [],
                "crew_ids": [crew_id],
            }
        ],
        "recommended_option": "inspect-first",
        "confidence": 0.9,
        "proposed_mode": "inspect",
        "proposed_risk": "low",
    }


class _FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class _UsageReasoner:
    name = "usage-test-reasoner"

    def __init__(self):
        self.seen_roster = None

    def interpret(self, directive, *, roster):
        self.seen_roster = roster
        return MissionInterpretation.from_mapping(valid_interpretation(directive), expected_intent=directive)

    def usage_snapshot(self):
        return CognitiveUsage(
            provider=self.name,
            model="test-model",
            input_tokens=1200,
            cached_input_tokens=800,
            output_tokens=120,
            reasoning_tokens=60,
            total_tokens=1320,
        )


class CognitiveContextEfficiencyTests(unittest.TestCase):
    def test_cognitive_directory_keeps_all_crew_without_authority_metadata(self):
        roster = CrewRoster(DOSSIERS)
        compact = roster.cognitive_directory()
        self.assertEqual(len(compact), 82)
        self.assertEqual([entry["crew_id"] for entry in compact], sorted(d.crew_id for d in roster.all()))
        for entry in compact:
            self.assertEqual(set(entry), {"crew_id", "division", "title", "domains", "verification"})
            self.assertNotIn("capabilities", entry)
            self.assertNotIn("tags", entry)
            self.assertIsInstance(entry["domains"], list)

        legacy = [
            {
                "crew_id": d.crew_id,
                "division": d.division,
                "title": d.title,
                "capabilities": sorted(d.capabilities),
                "tags": sorted(d.tags),
                "verification": d.verification,
            }
            for d in roster.all()
        ]
        compact_chars = len(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
        legacy_chars = len(json.dumps(legacy, ensure_ascii=False, separators=(",", ":")))
        self.assertLess(compact_chars, legacy_chars)
        self.assertLessEqual(compact_chars, int(legacy_chars * 0.80))

    def test_pilot_persists_provider_usage_without_giving_it_authority(self):
        td, root, initial = temp_vessel()
        initial.store.close()
        reasoner = _UsageReasoner()
        pilot = PilotGorXu(root, reasoner=reasoner)
        try:
            result = pilot.command("Inspect backend service", crew_id="backend-engineer")
            self.assertEqual(result["status"], "completed")
            self.assertIsNotNone(reasoner.seen_roster)
            self.assertTrue(reasoner.seen_roster)
            self.assertNotIn("capabilities", reasoner.seen_roster[0])
            self.assertNotIn("tags", reasoner.seen_roster[0])

            mission = pilot.store.mission(result["mission_id"])
            usage_rows = [row for row in mission["evidence"] if row["kind"] == "cognitive_usage"]
            self.assertEqual(len(usage_rows), 1)
            usage = json.loads(usage_rows[0]["content"])
            self.assertEqual(usage["provider"], "usage-test-reasoner")
            self.assertEqual(usage["input_tokens"], 1200)
            self.assertEqual(usage["cached_input_tokens"], 800)
            self.assertEqual(usage["reasoning_tokens"], 60)
            self.assertNotIn("allowed_actions", usage)
            self.assertNotIn("capabilities", usage)
        finally:
            pilot.store.close()
            td.cleanup()

    def test_openai_adapter_uses_stable_directory_prefix_and_normalizes_usage(self):
        roster = [
            {
                "crew_id": "backend-engineer",
                "division": "engineering",
                "title": "Backend Engineer",
                "domains": ["API design", "microservices", "database services"],
                "verification": False,
            }
        ]
        directives = ["Inspect backend service", "Inspect backend database"]
        requests = []

        def fake_urlopen(req, timeout):
            body = json.loads(req.data.decode("utf-8"))
            requests.append(body)
            directive = directives[len(requests) - 1]
            payload = {
                "model": "gpt-test-resolved",
                "output_text": json.dumps(valid_interpretation(directive)),
                "usage": {
                    "input_tokens": 1500,
                    "input_tokens_details": {"cached_tokens": 1024},
                    "output_tokens": 200,
                    "output_tokens_details": {"reasoning_tokens": 80},
                    "total_tokens": 1700,
                },
            }
            return _FakeHTTPResponse(payload)

        provider = OpenAIResponsesProvider(api_key="test-key", model="gpt-test")
        with patch("grox.reasoning.openai_responses.urlopen", side_effect=fake_urlopen):
            first = provider.interpret(directives[0], roster=roster)
            first_usage = provider.usage_snapshot()
            second = provider.interpret(directives[1], roster=roster)

        self.assertEqual(first.commander_intent, directives[0])
        self.assertEqual(second.commander_intent, directives[1])
        self.assertEqual(len(requests), 2)
        self.assertFalse(requests[0]["store"])
        self.assertEqual(requests[0]["prompt_cache_key"], requests[1]["prompt_cache_key"])
        self.assertTrue(requests[0]["prompt_cache_key"].startswith("grox-cognitive-"))
        for body, directive in zip(requests, directives):
            self.assertLess(body["input"].index("Standing Crew Directory"), body["input"].index("Commander directive:"))
            self.assertIn(directive, body["input"])
        self.assertIsNotNone(first_usage)
        self.assertEqual(first_usage.input_tokens, 1500)
        self.assertEqual(first_usage.cached_input_tokens, 1024)
        self.assertEqual(first_usage.output_tokens, 200)
        self.assertEqual(first_usage.reasoning_tokens, 80)
        self.assertEqual(first_usage.total_tokens, 1700)


if __name__ == "__main__":
    unittest.main()
