# Critical Invariant Mutation Matrix

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 1 — Prove the detectors

**Issue:** #25

**Candidate branch:** `verification/stage1-critical-detector-mutations`

## Purpose

This matrix records whether selected high-consequence GroX detectors actually turn red when the production invariant they protect is deliberately weakened.

The mutation runner never commits weakened source. For each mutation it:

1. requires one exact production mutation seam;
2. applies the mutation only in the CI checkout;
3. runs the targeted production-path regression and requires that exact detector to fail;
4. restores the exact original bytes in a `finally` block;
5. reruns the same detector and requires green;
6. continues through the remaining mutations even if one proof fails;
7. requires the mutated source paths to be Git-clean after the matrix completes.

A detector is marked **KILLED** only when the targeted regression goes red under the mutation and green after exact restoration.

## Preserved red harness evidence

The first complete harness attempt ran on PR #34 head `16e893dd9471e01d708096ec030ee6aaa6200568` in CI run `31950179712`.

The normal regression suites were green, but the Python 3.12 job correctly failed closed during the mutation phase:

- 11/12 mutations were killed;
- 0 mutations survived;
- the immutable CI-action-pin mutation did not execute because its initial search seam matched two `actions/checkout` uses in the workflow;
- the harness reported `source drift: expected exactly one mutation seam, found 2`;
- source restoration remained clean.

This red run is preserved as evidence that the mutation harness itself refuses ambiguous targeting rather than modifying an arbitrary occurrence.

The only remediation was to narrow the CI-action mutation seam to the regression-job checkout/setup-python block. No production invariant or detector was weakened to clear the run.

## Green mutation qualification evidence

PR #34 head `988c97a390a31b5a255385149088ae7e67685fa9` ran as CI `31950265325`.

Python 3.12 recorded:

- pytest: **133 passed, 2 skipped, 19 subtests passed**;
- unittest: **135 tests OK, 2 skipped**;
- mutation proof: **12/12 KILLED**;
- survived mutations: **0**;
- other mutation-proof failures: **0**;
- `source_restored_clean=true`.

All five canonical CI jobs passed.

## Matrix

| # | Invariant | Production mutation | Target detector | Red result | Restored result |
|---|---|---|---|---|---|
| 1 | Snapshot restore enforces source compatibility unless ancestor allowance is explicit | `PersistenceManager.restore_snapshot` changes `enforce_source_binding=True` to `False` | `PersistencePlaneTests.test_restore_rejects_source_mismatch_without_explicit_ancestor_allowance` | KILLED | GREEN |
| 2 | Semantic orchestrator identities cannot enter Standing Crew | Crew ID/title semantic orchestrator filter returns `False` unconditionally | `SpineTest.test_orchestrator_identity_variants_cannot_be_crew` | KILLED | GREEN |
| 3 | Reconstitution purges stale Crew adaptive/performance state | stale `crew_performance` DELETE changed to non-mutating SELECT | `SpineTest.test_reconstitution_purges_stale_crew_operational_state` | KILLED | GREEN |
| 4 | Executor cannot verify its own result | executor/verifier equality rejection disabled | `IndependentVerifierTests.test_same_executor_cannot_verify_own_result` | KILLED | GREEN |
| 5 | Crew cannot forge trusted graph verification evidence | `graph_verification` evidence stripping disabled | `ApexQualificationGauntlet.test_non_verifier_cannot_forge_graph_verification_evidence` | KILLED | GREEN |
| 6 | Mission may spend exactly its budget but must stop before overspend | cost reservation boundary changed from `<= max` to strict `< max` | `ApexQualificationGauntlet.test_fixed_mission_cost_budget_stops_before_overspend` | KILLED | GREEN |
| 7 | Resume reconstitutes previously committed cost before authorizing more work | resumed `spent_cost` forced to `0.0` | `CostRecoveryTests.test_resume_reconstitutes_committed_cost_before_spending` | KILLED | GREEN |
| 8 | Mission Graph Repair requires explicit GorXu mutation authorization | graph Repair authorization guard disabled | `MissionGraphIntegrationTests.test_graph_repair_requires_explicit_mutation_authority` | KILLED | GREEN |
| 9 | Injected filesystem mutation grants remain unusable outside Repair | Tool Gateway Repair-mode defense disabled | `GatewayTest.test_execute_write_denied_even_if_grant_is_injected` | KILLED | GREEN |
| 10 | Critical-risk exceptions escalate to Commander | critical-risk term removed from escalation condition | `DurableOperationsIntegrationTests.test_critical_exception_escalates_to_commander_without_automatic_consultation` | KILLED | GREEN |
| 11 | Installed runtime without a Vessel root fails closed | final `VesselRootError` replaced with fabricated current directory root | `VesselRootTests.test_unbound_installed_runtime_refuses_empty_vessel` | KILLED | GREEN |
| 12 | Third-party Actions remain pinned to immutable full commit SHAs | one regression-job checkout pin changed to mutable `@v7` | `CISupplyChainTest.test_external_actions_are_pinned_to_full_commit_sha` | KILLED | GREEN |

## Post-Apex matrix extensions

The original Stage 1 qualification above remains historical **12/12 KILLED** evidence. Protected source later extended the same permanent harness with eight additional high-consequence Live Environment Awareness authority/evidence mutations. The current matrix is therefore **20/20 KILLED**; this extension does not rewrite the original Stage 1 run.

| # | Invariant | Production mutation | Target detector | Current evidence |
|---|---|---|---|---|
| 13 | A discovered, ready, and qualified live resource cannot be selected without explicit authorization | disable the `not_authorized` gate in `src/grox/live_environment.py` | `LiveEnvironmentAwarenessTests.test_selection_uses_only_policy_order_and_requires_every_gate` | KILLED |
| 14 | Host-enabled/ready Tool Gateway capability state cannot imply Mission authorization without sealed Order context | make `order is None` return authorized in `src/grox/tool_awareness.py` | `ToolCapabilityAwarenessTests.test_host_ready_never_implies_mission_authorization` | KILLED |
| 15 | A bound/structurally ready hosted cognition provider cannot become authorized without explicit exact-resource policy | force hosted cognition authorization true without policy in `src/grox/cognition_awareness.py` | `CognitionProviderAwarenessTests.test_bound_session_provider_is_discovered_selected_but_not_authorized_or_observed` | KILLED |
| 16 | Remote cognition transport awareness cannot acquire network authority by allowing the Tool Gateway to seal an unsealed Mission Order | disable the pre-sealed Order rejection in `src/grox/cognition_awareness.py` | `CognitionTransportFreshnessTests.test_unsealed_order_is_rejected_without_becoming_sealed` | KILLED |
| 17 | Remote cognition transport evidence must remain bound to the exact currently configured origin | disable current-origin equality rejection in `src/grox/cognition_awareness.py` | `CognitionTransportFreshnessTests.test_same_resource_identity_endpoint_rebind_invalidates_prior_origin_evidence` | KILLED |
| 18 | Remote cognition endpoint-surface refresh must remain bound to the exact currently configured endpoint | disable exact endpoint equality rejection in `src/grox/cognition_awareness.py` | `CognitionEndpointFreshnessTests.test_exact_endpoint_authority_is_required` | KILLED |
| 19 | Configured cognition discovery must never imply readiness before an independently qualified readiness check | change configured-resource `ready` from false to true in `src/grox/cognition_discovery.py` | `ConfiguredCognitionDiscoveryTests.test_supported_openai_configuration_is_discovered_only` | KILLED |
| 20 | Configured remote connection authorization must remain bound to the exact discovered resource identity | disable the exact configured resource-ID mismatch rejection in `src/grox/configured_connection_awareness.py` | `ConfiguredConnectionPolicyAwarenessTests.test_wrong_resource_id_never_authorizes_connection` | KILLED |

Latest exact-head evidence is PR #145 CI #491 / `32775200609`: Python 3.12 killed **20/20** critical mutations with zero survivors while all health, reconstitution, operational-drift, source-provenance, and Post-Apex gates remained green. The #16 mutation remains `cognition-transport-presealed-authority`; #17 is `cognition-transport-origin-binding`; #18 is `cognition-endpoint-exact-binding`; #19 is `configured-cognition-discovery-state-separation`; #20 is `configured-connection-exact-resource-binding`. The original Stage 1 **12/12** qualification remains preserved above as historical evidence.

## New detector coverage added in Stage 1

Two gaps warranted permanent regression tests rather than relying only on indirect coverage:

- `tests/unit/test_verification.py` directly proves the verifier rejects executor self-verification;
- `tests/integration/test_cost_recovery.py` proves a restart reconstructs committed graph cost and cannot authorize a third paid Order after the Mission budget was already committed.

The mutation matrix then proved both new detectors fail when their production seams are weakened.

## Authority and architecture result

Stage 1 changes verification infrastructure and tests only. It does not:

- change Commander or GorXu authority;
- change Crew membership or routing;
- grant Repair capability;
- alter persistence schema;
- alter production cost semantics;
- weaken source/state restore;
- change the released package version;
- create a new qualification stage.

The deliberate weakened variants exist only transiently in the CI checkout and are restored before the mutation step succeeds.

## Exit gate

**PASSED.** The selected critical detector set has a replayable matrix showing the production seam, exact target detector, observed red result, restored green result, and preserved fail-closed harness evidence. Stage 2 may build the Vessel health surface on these proven detector foundations.
