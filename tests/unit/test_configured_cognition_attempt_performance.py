from __future__ import annotations

import unittest

from grox.configured_cognition_attempt_performance import (
    ConfiguredCognitionAttemptPerformance,
    ConfiguredCognitionAttemptPerformanceError,
)


class ConfiguredCognitionAttemptPerformanceTests(unittest.TestCase):
    def test_success_evidence_is_exact_privacy_minimized_and_non_authoritative(self):
        item = ConfiguredCognitionAttemptPerformance(
            resource_id="cognition:configured:openai:abc123",
            provider_kind="openai",
            model="model-a",
            endpoint="https://api.openai.com/v1/responses",
            credential_alias="alias-a",
            mission_id="MSN-1",
            order_id="ORD-1",
            selection_id="SEL-1",
            placement="mission_interpretation",
            outcome="success",
            observation_id="OBS-1",
        )

        evidence = item.evidence()
        self.assertTrue(item.succeeded)
        self.assertFalse(item.timed_out)
        self.assertEqual(evidence["credential_alias"], "alias-a")
        self.assertEqual(evidence["outcome"], "success")
        self.assertEqual(evidence["observation_id"], "OBS-1")
        self.assertTrue(evidence["actual_provider_attempt"])
        self.assertFalse(evidence["ranking_applied"])
        self.assertFalse(evidence["learning_applied"])
        self.assertFalse(evidence["authority_changed"])
        self.assertFalse(evidence["credential_material_returned"])
        self.assertFalse(evidence["secret_value_returned"])

    def test_timeout_requires_no_observation_and_preserves_exact_selection_identity(self):
        item = ConfiguredCognitionAttemptPerformance(
            resource_id="cognition:configured:openai:def456",
            provider_kind="openai",
            model="model-b",
            endpoint="https://api.openai.com/v1/responses",
            credential_alias="alias-b",
            mission_id="MSN-1",
            order_id="ORD-2",
            selection_id="SEL-2",
            placement="mission_interpretation",
            outcome="provider_timeout",
        )

        self.assertFalse(item.succeeded)
        self.assertTrue(item.timed_out)
        self.assertIsNone(item.observation_id)
        self.assertEqual(item.selection_id, "SEL-2")

    def test_malformed_outcome_or_observation_semantics_fail_closed(self):
        kwargs = {
            "resource_id": "cognition:configured:openai:def456",
            "provider_kind": "openai",
            "model": "model-b",
            "endpoint": "https://api.openai.com/v1/responses",
            "credential_alias": "alias-b",
            "mission_id": "MSN-1",
            "order_id": "ORD-2",
            "selection_id": "SEL-2",
            "placement": "mission_interpretation",
        }
        with self.assertRaises(ConfiguredCognitionAttemptPerformanceError):
            ConfiguredCognitionAttemptPerformance(**kwargs, outcome="unknown")
        with self.assertRaises(ConfiguredCognitionAttemptPerformanceError):
            ConfiguredCognitionAttemptPerformance(**kwargs, outcome="success")
        with self.assertRaises(ConfiguredCognitionAttemptPerformanceError):
            ConfiguredCognitionAttemptPerformance(
                **kwargs,
                outcome="provider_timeout",
                observation_id="OBS-not-allowed",
            )


if __name__ == "__main__":
    unittest.main()
