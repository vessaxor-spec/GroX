from __future__ import annotations

import unittest

from grox.credential_binding import ConfiguredCredentialBinding
from grox.configured_cognition_readiness import (
    ConfiguredCognitionReadiness,
    ConfiguredCognitionReadinessError,
)


ENDPOINT = "https://api.openai.com/v1/responses"
MODEL = "remote-model-sentinel"
ALIAS = "openai-primary"
CONFIG = {
    "GROX_REASONER_PROVIDER": "openai",
    "GROX_REASONER_MODEL": MODEL,
    "GROX_REASONER_ENDPOINT": ENDPOINT,
    "GROX_REASONER_CREDENTIAL_ALIAS": ALIAS,
}


def _probe(config=CONFIG, *, observed=100.0, **overrides):
    binding = ConfiguredCredentialBinding(config).inventory()["resources"][0]
    evidence = {
        "schema": "grox-openai-authenticated-model-probe-v1",
        "origin": "https://api.openai.com",
        "status": 200,
        "classification": "authenticated_model_visible",
        "requested_model": binding["model"],
        "model_identity": binding["model"],
        "metadata_valid": True,
        "credential_alias": binding["credential_alias"],
        "credential_accepted_for_model_visibility": True,
        "credential_rejected": False,
        "secret_materialized": True,
        "network_invoked": True,
        "response_body_returned": False,
        "cognition_invoked": False,
        "ready": False,
        "qualified_fit": False,
        "selected": False,
        "authority_changed": False,
        "resource_id": binding["resource_id"],
        "provider_kind": "openai",
        "endpoint": ENDPOINT,
        "credential_use_authorized": True,
        "observed_monotonic_seconds": observed,
        "observation_clock": "process_monotonic",
        "persistable_readiness_evidence": False,
        "mission_created": False,
        "observed": False,
        "auto_selection": False,
    }
    evidence.update(overrides)
    return evidence


class ConfiguredCognitionReadinessTests(unittest.TestCase):
    def test_recent_exact_authenticated_visibility_is_ready_only_with_bounded_scope(self):
        result = ConfiguredCognitionReadiness(
            CONFIG,
            clock=lambda: 120.0,
            max_age_seconds=60.0,
        ).evaluate(_probe())

        self.assertTrue(result.ready)
        self.assertEqual(result.status, "READY")
        self.assertIsNone(result.reason)
        self.assertEqual(result.observation_age_seconds, 20.0)
        evidence = result.evidence()
        self.assertEqual(evidence["readiness_scope"], "authenticated_model_visibility")
        self.assertTrue(evidence["volatile_process_local"])
        self.assertFalse(evidence["persistable_readiness_evidence"])
        self.assertFalse(evidence["qualified_fit"])
        self.assertFalse(evidence["routing_fit_claim"])
        self.assertFalse(evidence["selected"])
        self.assertFalse(evidence["observed"])
        self.assertFalse(evidence["secret_materialized_by_evaluator"])
        self.assertFalse(evidence["network_invoked_by_evaluator"])
        self.assertFalse(evidence["ranking_enabled"])
        self.assertFalse(evidence["adaptive_scoring_enabled"])

    def test_stale_authenticated_visibility_expires_without_becoming_ready(self):
        result = ConfiguredCognitionReadiness(
            CONFIG,
            clock=lambda: 160.000001,
            max_age_seconds=60.0,
        ).evaluate(_probe(observed=100.0))

        self.assertFalse(result.ready)
        self.assertEqual(result.status, "NOT_READY")
        self.assertEqual(result.reason, "stale_authenticated_model_visibility")
        self.assertGreater(result.observation_age_seconds, result.max_age_seconds)

    def test_future_missing_and_malformed_monotonic_evidence_fail_closed(self):
        cases = (
            (_probe(observed=101.0), 100.0, "future_monotonic_observation"),
            (_probe(observed=None), 100.0, "invalid_monotonic_observation"),
            (_probe(observed=float("nan")), 100.0, "invalid_monotonic_observation"),
            (_probe(observed=True), 100.0, "invalid_monotonic_observation"),
        )
        for probe, now, reason in cases:
            with self.subTest(reason=reason, observed=probe["observed_monotonic_seconds"]):
                result = ConfiguredCognitionReadiness(CONFIG, clock=lambda now=now: now).evaluate(probe)
                self.assertFalse(result.ready)
                self.assertEqual(result.reason, reason)

    def test_current_configuration_rebind_invalidates_fresh_prior_probe(self):
        old_probe = _probe(observed=100.0)
        rebound = {
            **CONFIG,
            "GROX_REASONER_MODEL": "different-model",
            "GROX_REASONER_CREDENTIAL_ALIAS": "different-alias",
        }
        result = ConfiguredCognitionReadiness(
            rebound,
            clock=lambda: 101.0,
        ).evaluate(old_probe)

        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "current_config_identity_changed")
        self.assertIsNone(result.observation_age_seconds)

    def test_nonpositive_visibility_or_source_state_promotion_never_becomes_ready(self):
        cases = (
            _probe(classification="credential_rejected", status=401, credential_rejected=True, credential_accepted_for_model_visibility=False),
            _probe(metadata_valid=False),
            _probe(credential_use_authorized=False),
            _probe(ready=True),
            _probe(persistable_readiness_evidence=True),
        )
        for probe in cases:
            with self.subTest(classification=probe.get("classification"), ready=probe.get("ready")):
                result = ConfiguredCognitionReadiness(CONFIG, clock=lambda: 101.0).evaluate(probe)
                self.assertFalse(result.ready)

    def test_missing_or_nonofficial_current_binding_fails_closed(self):
        with self.assertRaises(ConfiguredCognitionReadinessError):
            ConfiguredCognitionReadiness(
                {**CONFIG, "GROX_REASONER_CREDENTIAL_ALIAS": ""},
                clock=lambda: 101.0,
            ).evaluate(_probe())

        with self.assertRaises(ConfiguredCognitionReadinessError):
            ConfiguredCognitionReadiness(
                {**CONFIG, "GROX_REASONER_ENDPOINT": "https://compatible.example/v1/responses"},
                clock=lambda: 101.0,
            ).evaluate(_probe())

    def test_freshness_window_is_bounded(self):
        with self.assertRaises(ValueError):
            ConfiguredCognitionReadiness(CONFIG, max_age_seconds=0.0)
        with self.assertRaises(ValueError):
            ConfiguredCognitionReadiness(CONFIG, max_age_seconds=301.0)
        with self.assertRaises(ValueError):
            ConfiguredCognitionReadiness(CONFIG, max_age_seconds=float("inf"))


if __name__ == "__main__":
    unittest.main()
