from __future__ import annotations

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from grox.native_model_runtime import LocalModelRuntime
from grox.openai_crew_cognition import OpenAICrewCognitionProvider, OpenAICrewDisclosurePolicy
from grox.reasoning.base import CognitiveUsage
from grox.reasoning.openai_responses import OpenAIResponsesProvider
from grox.reasoning.session import SessionReasoningProvider
from grox.session_crew_cognition import SessionCrewCognitionProvider
from grox.cognition_awareness import CognitionProviderAwareness, CognitionProviderPolicy


class CognitionProviderAwarenessTests(unittest.TestCase):
    def test_bound_session_provider_is_discovered_selected_but_not_authorized_or_observed(self):
        calls = []

        def responder(directive, roster):
            calls.append((directive, roster))
            return {}

        provider = SessionReasoningProvider(responder, name="host-session-reasoner")
        inventory = CognitionProviderAwareness(reasoner=provider).inventory()
        self.assertEqual(len(inventory["resources"]), 1)
        item = inventory["resources"][0]
        self.assertEqual(item["role"], "gorxu_reasoner")
        self.assertTrue(item["discovered"])
        self.assertTrue(item["selected"])
        self.assertTrue(item["ready"])
        self.assertEqual(item["readiness_status"], "host_session_bound")
        self.assertFalse(item["authorized"])
        self.assertFalse(item["qualification_recorded"])
        self.assertFalse(item["qualified_fit"])
        self.assertFalse(item["observed"])
        self.assertEqual(calls, [])
        self.assertFalse(inventory["authority_changed"])
        self.assertFalse(inventory["auto_selection"])
        self.assertFalse(inventory["auto_invocation"])

    def test_authorization_and_qualification_are_exact_and_separate(self):
        provider = SessionReasoningProvider(lambda directive, roster: {}, name="session-policy-test")
        awareness = CognitionProviderAwareness(reasoner=provider)
        resource_id = awareness.inventory()["resources"][0]["resource_id"]

        qualified_only = awareness.inventory(
            policy=CognitionProviderPolicy(qualified_ids=frozenset({resource_id}))
        )["resources"][0]
        self.assertFalse(qualified_only["authorized"])
        self.assertTrue(qualified_only["qualification_recorded"])
        self.assertTrue(qualified_only["qualified_fit"])

        authorized_only = awareness.inventory(
            policy=CognitionProviderPolicy(authorized_ids=frozenset({resource_id}))
        )["resources"][0]
        self.assertTrue(authorized_only["authorized"])
        self.assertFalse(authorized_only["qualification_recorded"])
        self.assertFalse(authorized_only["qualified_fit"])

        both = awareness.inventory(
            policy=CognitionProviderPolicy(
                authorized_ids=frozenset({resource_id}),
                qualified_ids=frozenset({resource_id}),
            )
        )["resources"][0]
        self.assertTrue(both["authorized"])
        self.assertTrue(both["qualification_recorded"])
        self.assertTrue(both["qualified_fit"])

    def test_remote_openai_configuration_does_not_imply_reachability_or_authorization_and_hides_secrets(self):
        secret = "super-secret-runtime-key-sentinel"
        provider = OpenAIResponsesProvider(
            api_key=secret,
            model="gpt-test-model",
            endpoint="https://user:password@example.test/v1/responses?token=hidden#frag",
        )
        with patch("grox.reasoning.openai_responses.urlopen") as network:
            inventory = CognitionProviderAwareness(reasoner=provider).inventory()
        network.assert_not_called()
        item = inventory["resources"][0]
        self.assertFalse(item["ready"])
        self.assertEqual(item["readiness_status"], "remote_reachability_unproven")
        self.assertFalse(item["authorized"])
        encoded = json.dumps(inventory, sort_keys=True)
        for forbidden in (secret, "password", "token=hidden", "user:"):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(item["details"]["model"], "gpt-test-model")
        self.assertEqual(item["details"]["endpoint"], "https://example.test/v1/responses")

    def test_existing_remote_observability_does_not_become_current_readiness_or_authorization(self):
        provider = OpenAIResponsesProvider(api_key="k", model="gpt-configured")
        provider._last_usage = CognitiveUsage(provider=provider.name, model="gpt-observed")
        inventory = CognitionProviderAwareness(reasoner=provider).inventory()
        item = inventory["resources"][0]
        self.assertTrue(item["observed"])
        self.assertFalse(item["ready"])
        self.assertEqual(item["readiness_status"], "remote_reachability_unproven")
        self.assertIn("not revalidated", item["readiness_reason"])
        self.assertEqual(item["observed_identity"], {"provider": provider.name, "model": "gpt-observed"})
        self.assertFalse(item["authorized"])
        self.assertFalse(item["qualified_fit"])

    def test_remote_qualification_record_does_not_override_unproven_readiness(self):
        provider = OpenAIResponsesProvider(api_key="k", model="gpt-qualified-history")
        awareness = CognitionProviderAwareness(reasoner=provider)
        resource_id = awareness.inventory()["resources"][0]["resource_id"]
        item = awareness.inventory(
            policy=CognitionProviderPolicy(qualified_ids=frozenset({resource_id}))
        )["resources"][0]
        self.assertTrue(item["qualification_recorded"])
        self.assertFalse(item["authorized"])
        self.assertFalse(item["ready"])
        self.assertFalse(item["qualified_fit"])

    def test_crew_disclosure_observability_is_privacy_minimized_and_inventory_never_invokes(self):
        disclosure = OpenAICrewDisclosurePolicy(
            allowed_scopes=("PRIVATE-SCOPE-SENTINEL",),
            allow_order_text=False,
            allow_craft=True,
            allow_memory=False,
            allowed_observation_actions=frozenset({"fs_read"}),
        )
        provider = OpenAICrewCognitionProvider(
            api_key="CREW-SECRET-SENTINEL",
            model="crew-model",
            disclosure_policy=disclosure,
        )
        with patch("grox.openai_crew_cognition.urlopen") as network:
            inventory = CognitionProviderAwareness(crew_provider=provider).inventory()
        network.assert_not_called()
        item = inventory["resources"][0]
        self.assertEqual(item["role"], "crew_cognition")
        self.assertFalse(item["ready"])
        snapshot = item["details"]["disclosure_policy"]
        self.assertIn("sha256", snapshot)
        self.assertEqual(snapshot["allowed_scope_count"], 1)
        self.assertNotIn("allowed_scopes", snapshot)
        encoded = json.dumps(inventory, sort_keys=True)
        self.assertNotIn("PRIVATE-SCOPE-SENTINEL", encoded)
        self.assertNotIn("CREW-SECRET-SENTINEL", encoded)

    def test_session_crew_provider_is_structurally_ready_without_callback_invocation(self):
        calls = []

        def responder(*args):
            calls.append(args)
            return {"action": "finish", "work_product": "done"}

        provider = SessionCrewCognitionProvider(responder, name="session-crew-awareness")
        inventory = CognitionProviderAwareness(crew_provider=provider).inventory()
        item = inventory["resources"][0]
        self.assertTrue(item["ready"])
        self.assertEqual(item["readiness_status"], "host_session_bound")
        self.assertEqual(calls, [])

    def test_local_runtime_backed_reasoner_is_not_duplicated_on_hosted_surface(self):
        local_runtime = object.__new__(LocalModelRuntime)
        local_provider = SimpleNamespace(
            name="local-llama-cpp",
            model_id="qwen-local",
            runtime=local_runtime,
            interpret=lambda *args, **kwargs: None,
        )
        inventory = CognitionProviderAwareness(reasoner=local_provider).inventory()
        self.assertEqual(inventory["resources"], [])
        self.assertEqual(inventory["local_runtime_delegated_count"], 1)

    def test_policy_rejects_blank_resource_ids(self):
        with self.assertRaises(ValueError):
            CognitionProviderPolicy(authorized_ids=frozenset({" "}))
        with self.assertRaises(ValueError):
            CognitionProviderPolicy(qualified_ids=frozenset({""}))


if __name__ == "__main__":
    unittest.main()
