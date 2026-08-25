from pathlib import Path

pilot_path = Path("src/grox/pilot.py")
pilot = pilot_path.read_text(encoding="utf-8")
import_old = "from .configured_local_readiness import ConfiguredLocalCognitionReadiness\n"
import_new = import_old + "from .credential_binding import ConfiguredCredentialBinding\n"
assert pilot.count(import_old) == 1, "Pilot import seam drifted"
pilot = pilot.replace(import_old, import_new, 1)

method_old = '''    def live_configured_cognition_inventory(self)->dict[str,Any]:
        """Discover supported non-secret cognition configuration without binding or invocation."""
        return ConfiguredCognitionDiscovery(nonsecret_reasoner_config_from_env()).inventory()

    def live_configured_connection_policy_inventory(self, *, order:MissionOrder|None=None)->dict[str,Any]:
'''
method_new = '''    def live_configured_cognition_inventory(self)->dict[str,Any]:
        """Discover supported non-secret cognition configuration without binding or invocation."""
        return ConfiguredCognitionDiscovery(nonsecret_reasoner_config_from_env()).inventory()

    def live_configured_credential_binding_inventory(self)->dict[str,Any]:
        """Report explicit non-secret credential-alias binding without broker or provider activity."""
        return ConfiguredCredentialBinding(nonsecret_reasoner_config_from_env()).inventory()

    def live_configured_connection_policy_inventory(self, *, order:MissionOrder|None=None)->dict[str,Any]:
'''
assert pilot.count(method_old) == 1, "Pilot configured-awareness seam drifted"
pilot = pilot.replace(method_old, method_new, 1)
pilot_path.write_text(pilot, encoding="utf-8")

mutation_path = Path("tests/mutation/run_critical_invariants.py")
mutation = mutation_path.read_text(encoding="utf-8")
anchor = '''    MutationSpec(
        name="ci-action-immutable-pin",
'''
insert = '''    MutationSpec(
        name="configured-credential-binding-exact-resource",
        invariant="Configured credential-alias binding must preserve the exact configured cognition resource identity.",
        path="src/grox/credential_binding.py",
        old='            "resource_id": resource["resource_id"],\\n',
        new='            "resource_id": "cognition:configured:openai:wrong-binding",\\n',
        nodeid="tests/unit/test_configured_credential_binding.py::ConfiguredCredentialBindingTests::test_valid_remote_binding_preserves_exact_resource_identity",
    ),
'''
assert mutation.count(anchor) == 1, "critical mutation insertion seam drifted"
mutation = mutation.replace(anchor, insert + anchor, 1)
mutation_path.write_text(mutation, encoding="utf-8")

assert 'def live_configured_credential_binding_inventory' in pilot_path.read_text(encoding="utf-8")
assert 'configured-credential-binding-exact-resource' in mutation_path.read_text(encoding="utf-8")
