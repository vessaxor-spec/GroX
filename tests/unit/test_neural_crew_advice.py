from __future__ import annotations

from dataclasses import FrozenInstanceError
import copy
import math
import unittest

from grox.neural_crew_advice import (
    NeuralCrewAdvice, NeuralCrewAdviceError, SCHEMA,
)


def valid_advice() -> dict:
    return {
        "schema": SCHEMA,
        "recommended_action": "suggest_test_run",
        "evidence_sufficient": False,
        "test_interpretation": "not_run",
        "continue_or_stop": "continue",
        "failure_classification": "none",
        "confidence": 0.7,
        "requested_evidence": [],
    }


class NeuralCrewAdviceContractTests(unittest.TestCase):
    def test_valid_advice_is_immutable_and_round_trips(self):
        advice = NeuralCrewAdvice.from_mapping(valid_advice())
        self.assertEqual(advice.to_dict(), valid_advice())
        self.assertEqual(NeuralCrewAdvice.from_mapping(advice.to_dict()), advice)
        with self.assertRaises(FrozenInstanceError):
            advice.recommended_action = "suggest_finish"

    def test_deny_unknown_authority_bearing_or_ambiguous_fields(self):
        for addition in (
            {"allowed_actions": ["fs_write"]},
            {"mode": "repair"},
            {"approved": True},
            {"tool_parameters": {"path": "../secret"}},
            {"role": "gorxu"},
            {"mission_order": {"sealed": True}},
            {"verifier_id": "self"},
            {"model_activation": True},
        ):
            with self.subTest(addition=addition):
                raw = valid_advice() | addition
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw)
        raw = valid_advice()
        del raw["evidence_sufficient"]
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping(raw)
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping({"schema": SCHEMA})

    def test_malformed_schema_and_nonmapping_rejected(self):
        for raw in (None, [], "", {"schema": "future"}, {"schema": SCHEMA}):
            with self.subTest(raw=raw):
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw)

    def test_unknown_or_mutating_actions_rejected(self):
        for action in ("fs_write", "repair", "execute", "verify", "mcp_mutate",
                       "create_mission", "activate_model", "suggest_shell", "drop_table", "", None):
            with self.subTest(action=action):
                raw = valid_advice()
                raw["recommended_action"] = action
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw)

    def test_malformed_confidence_fail_closed(self):
        for confidence in (True, False, -0.1, 1.01, math.nan, math.inf,
                           -math.inf, "0.5", None, [], {}):
            with self.subTest(confidence=confidence):
                raw = valid_advice()
                raw["confidence"] = confidence
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw)
        for confidence in (0, 1, 0.0, 1.0):
            raw = valid_advice()
            raw["confidence"] = confidence
            self.assertEqual(NeuralCrewAdvice.from_mapping(raw).confidence, confidence)

    def test_boolean_and_enum_fields_are_strict(self):
        for field, invalid in (
            ("evidence_sufficient", 1),
            ("evidence_sufficient", "yes"),
            ("test_interpretation", "successful"),
            ("test_interpretation", None),
            ("continue_or_stop", "maybe"),
            ("continue_or_stop", False),
            ("failure_classification", "network"),
            ("failure_classification", None),
        ):
            with self.subTest(field=field, invalid=invalid):
                raw = valid_advice()
                raw[field] = invalid
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw)

    def test_bounded_evidence_requests_require_missing_evidence(self):
        raw = valid_advice()
        raw.update(
            recommended_action="request_evidence",
            requested_evidence=["test log", "checksum"],
            failure_classification="insufficient_evidence",
        )
        self.assertEqual(NeuralCrewAdvice.from_mapping(raw).requested_evidence,
                         ("test log", "checksum"))
        invalid_requests = (
            ["same", "same"],
            [""],
            [" a "],
            ["a\nmessage"],
            ["x" * 129],
            ["x"] * 9,
            [1],
            None,
            "a file",
            (),
        )
        for requested in invalid_requests:
            with self.subTest(requested=requested):
                attempt = copy.deepcopy(raw)
                attempt["requested_evidence"] = requested
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(attempt)
        for change in (
            {"evidence_sufficient": True},
            {"requested_evidence": []},
            {"continue_or_stop": "stop"},
        ):
            with self.subTest(change=change):
                with self.assertRaises(NeuralCrewAdviceError):
                    NeuralCrewAdvice.from_mapping(raw | change)

    def test_only_request_evidence_may_supply_request_labels(self):
        raw = valid_advice()
        raw["requested_evidence"] = ["unrelated source"]
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping(raw)

    def test_stop_finish_and_denial_are_consistent(self):
        raw = valid_advice()
        raw["recommended_action"] = "suggest_finish"
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping(raw)
        raw.update(evidence_sufficient=True, continue_or_stop="stop")
        self.assertEqual(NeuralCrewAdvice.from_mapping(raw).recommended_action,
                         "suggest_finish")
        raw = valid_advice()
        raw["recommended_action"] = "stop"
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping(raw)
        raw["continue_or_stop"] = "stop"
        NeuralCrewAdvice.from_mapping(raw)
        raw = valid_advice()
        raw["failure_classification"] = "policy_denied"
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice.from_mapping(raw)

    def test_direct_constructor_cannot_bypass_checks(self):
        raw = valid_advice()
        raw.pop("schema")
        raw["recommended_action"] = "fs_write"
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice(**raw)
        raw["recommended_action"] = "suggest_test_run"
        raw["requested_evidence"] = []
        with self.assertRaises(NeuralCrewAdviceError):
            NeuralCrewAdvice(**raw)


if __name__ == "__main__":
    unittest.main()
