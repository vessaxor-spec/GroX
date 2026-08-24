# GroX Roadmap Doctrine 001 — Live Environment Awareness

**Status:** ROADMAP-BOUND / IMPLEMENTATION IN PROGRESS / LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS + BOUND REMOTE ENDPOINT-SURFACE FRESHNESS + SUPPORTED CONFIGURED COGNITION DISCOVERY + CONFIGURED REMOTE CONNECTION POLICY AWARENESS + CONFIGURED LOCAL LLAMA.CPP READINESS EXITS QUALIFIED

**Placement:** NCI-3 is qualified. Live Environment Awareness is the Commander-designated immediate bounded workstream before the next numbered Native Cognition Independence stage, unless later repository evidence supports replanning.

**Command invariant:** Commander → Pilot GorXu → Divisions → Standing Crew

## Doctrine

GroX must evolve from awareness of resources represented inside the Vessel toward evidence-backed awareness of the execution environment actually available to the Vessel at runtime.

Pilot GorXu should be able to determine what usable resources presently exist, what each resource is permitted and fit to do, what execution configuration is actually active, and what evidence resulted from using it. Discovery must never create authority.

The target operating principle is:

> **Know what exists → determine what is permitted and fit → select deliberately → execute through bounded authority → verify the outcome → preserve continuity.**

## Runtime awareness scope

The bounded discovery surface may include, where supported and authorized:

- local models that are installed, registered, reachable, loaded, or currently running;
- configured and reachable remote/cloud cognition providers;
- inference runtimes and execution backends;
- host hardware and resource readiness;
- installed or exposed tools available through governed GroX interfaces;
- local applications or machine capabilities exposed through an authorized Tool Gateway path;
- network and external-service connections that the Commander has authorized;
- Standing Crew and capability surfaces currently operational in the Vessel;
- current execution configuration, including the actual model/runtime/backend selected for a cognitive or Crew tour;
- recent evidence about observed fitness, reliability, latency, resource cost, failure behavior, and qualification state where GroX has legitimate measurements.

Absence, reachability, installation, registration, connection, or discovery alone does not make a resource eligible for use.

## Required separation of concerns

GroX must preserve distinct states rather than collapsing them into one routing decision:

1. **Discovered** — the Vessel has evidence that a resource exists or is reachable.
2. **Authorized** — Commander policy and GroX authority boundaries permit that resource to be considered for the Mission.
3. **Ready** — the resource and host configuration satisfy integrity, availability, compatibility, and resource-readiness requirements.
4. **Qualified / fit** — available evidence supports use for the bounded work class under the relevant risk and verification requirements.
5. **Selected** — Pilot GorXu chooses the resource for this Mission or Crew tour.
6. **Observed** — GroX records what actually executed and what evidence resulted.

No later state may be inferred merely from an earlier one. In particular, discovery, connectivity, model capability, benchmark strength, or historical success cannot widen Commander authority, lower Mission risk, bypass Tool Gateway policy, remove verifier requirements, or create self-activation rights.

## GorXu responsibility

Pilot GorXu remains the sole operational orchestrator. Runtime awareness is a capability beneath the Pilot, not a new command layer.

GorXu should use runtime evidence to:

- reconcile the Commander's objective with currently available Vessel resources;
- avoid routing to resources that are absent, unreachable, unready, unauthorized, or unqualified;
- prefer the smallest sufficient execution configuration consistent with Mission requirements;
- bind calibration and qualification evidence to the actual model/runtime/backend/configuration being used rather than to a vendor or model name in the abstract;
- maintain policy-constrained fallback when a preferred resource disappears or fails;
- record observed execution identity so reconstitution can distinguish intended routing from what actually ran;
- preserve deterministic authority and fail-closed behavior when runtime evidence is ambiguous.

## Local and remote resource posture

Local and remote resources are peers at the capability layer unless Commander policy or Mission constraints require otherwise. Neither locality nor provider identity creates command rank, eligibility, trust, or priority by itself.

A stronger model is not automatically safer. Risk derives from the Mission, requested action, authority, data sensitivity, mutation potential, and policy. Resource capability may affect fitness and verification strategy, but it does not reduce the underlying authority requirement.

## Continuity requirement

Runtime awareness must survive normal Vessel reconstitution without pretending that stale observations are current facts.

GroX should preserve durable evidence about prior execution and qualification while re-discovering volatile facts such as running processes, reachable providers, available hardware, active models, tool sessions, and network connections on the current host/session.

Historical evidence may inform selection. It must not substitute for current readiness where current readiness is required.

## Canonical local-runtime foundation and qualified awareness state

NCI-3 established reusable bounded primitives. Canonical PRs #119 and #120 extended those primitives into the qualified first bounded Live Environment Awareness exit for defined local cognition/runtime resources:

- `ModelRegistry` as an integrity-bound catalogue of represented local models;
- local model readiness reporting against artifact integrity, backend support, placement, and current host hardware/runtime profile;
- explicit model load/invoke/unload with no registry-, readiness-, or reconstitution-driven auto-activation;
- persistent model-store admission with exact artifact/provenance identity;
- observed provider/model/backend/artifact identity on qualified local execution;
- reconstitution that clears active model state and reports current readiness without silently preserving prior activation.

For defined local cognition/runtime resources, canonical PRs #119 and #120 establish a fresh live-resource inventory; explicit Discovered / Authorized / Ready / Qualified-Fit / Selected / Observed separation; policy-constrained candidate fallback; fail-closed selection; actual execution identity/configuration observation; durable identity-only observation history; and volatile selected/observed invalidation with fresh readiness discovery on reconstitution. Historical observations are explicitly non-authoritative for current readiness.

The qualified local-runtime exit alone did **not** establish remote/cloud provider discovery, governed tool/application awareness, authorized connection awareness, broader operational capability-surface awareness, or adaptive startup/resource routing. Canonical issue #122 / PR #123 separately qualify read-only awareness for the existing governed A5 Tool Gateway workspace/network/browser/MCP surface, while preserving sealed-Mission authorization and no-auto-invocation boundaries. Canonical issue #125 / PR #126 additionally qualify fresh privacy-safe awareness for hosted/session cognition providers already bound to the current GorXu/Crew cognition seats. Binding, authorization, current readiness, qualification/fit, existing binding selection, and prior observation remain separate; prior remote execution never becomes current remote readiness. Canonical issue #128 / PR #129 additionally qualify explicit current-session **origin transport freshness** for an already-bound remote cognition resource, only under an already sealed exact `net_fetch` Mission Order and the existing A5 Tool Gateway origin policy. Issue #132 / PR #133 repair that surface so freshness remains bound to the exact current normalized origin even when provider/model resource identity is unchanged. Canonical issue #136 / PR #137 now additionally qualify explicit current-session **exact endpoint-surface freshness** for the same already-bound remote cognition class: a credential-free bounded GET to the exact configured endpoint path under an already sealed Order carrying exact operation/resource/endpoint/origin authority. Endpoint response evidence remains separate from credential validity, authenticated provider/service readiness, model availability/fitness, authorization, qualification/fit, provider selection, or cognition invocation, and remote `ready` remains false. Issue #140 / PR #141 additionally qualify passive **supported configured cognition-resource discovery** for the existing repository-supported non-secret reasoning configuration kinds `openai` and `local-llama-cpp`. That discovery does not construct or bind providers, inspect credentials, touch network/model/executable runtime, invoke cognition, create a Mission, or imply any state beyond `Discovered`. Issue #144 / PR #145 additionally qualify **configured remote cognition connection-policy awareness** for one valid configured `openai` resource. That surface derives the exact origin from the configured endpoint, separates host-policy permission from already-sealed Mission authorization, and requires exact operation/resource/endpoint/origin authority before reporting authorization. It performs no network request or credential/provider/model/cognition activity, and `ready`, `qualified_fit`, `selected`, and `observed` remain false. Issue #148 / PR #149 additionally qualify **configured local llama.cpp readiness awareness** for one valid supported configured `local-llama-cpp` resource. This explicit readiness surface reuses existing GroX registry/runtime/backend primitives to check exact configured model registration/artifact integrity, host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the bounded existing `llama.cpp --version` support check. `ready=True` remains below and separate from authorization, qualification/fit, selection, and observation; no model load, cognition invocation, provider binding, Mission creation, network/download, credential inspection, fallback, or routing occurs. These exits still do **not** establish ambient application/process scanning, arbitrary tool discovery, arbitrary/unconfigured remote/cloud provider catalog discovery, authenticated provider/service readiness, credential validity, broader authorized external-connection discovery, model existence/availability/fitness, broader operational capability awareness, switching/fallback, or adaptive startup/resource routing.

## Sequencing

NCI-3 is **QUALIFIED** through issue #113 / PR #114 and its exact-tree canonical merge. Live Environment Awareness is the current bounded architectural workstream tracked by issue #115.

The bounded local-runtime implementation exit is **QUALIFIED** through canonical PRs #119 and #120. The governed Tool Gateway capability-awareness exit is **QUALIFIED** through issue #122 / PR #123 for the existing A5 workspace/network/browser/MCP surface. The bound hosted/session cognition-awareness exit is **QUALIFIED** through issue #125 / PR #126 for providers already bound to GorXu or Crew cognition seats, without network probing or routing changes. The bound remote cognition transport-freshness exit is **QUALIFIED** through issue #128 / PR #129 for current-session exact-origin transport evidence under already sealed A5 network authority. Its exact-origin evidence seam was repaired through issue #132 / PR #133 without adding a new awareness surface. The exact bound remote endpoint-surface freshness exit is **QUALIFIED** through issue #136 / PR #137 for credential-free current-session evidence that the exact configured endpoint path produced a bounded HTTP response under already sealed exact authority; it does not qualify credentials, authenticated provider/service readiness, model availability/fitness, provider qualification, cognition success, selection/fallback, routing, or remote `ready=True`. The supported configured cognition-resource discovery exit is **QUALIFIED** through issue #140 / PR #141 and establishes `Discovered` only from the repository-supported non-secret configuration surface. The configured remote cognition connection-policy awareness exit is **QUALIFIED** through issue #144 / PR #145 and establishes only the separation between host-policy permission and exact already-sealed Mission authorization for one configured remote connection, with zero network/provider/credential/model activity. The configured local llama.cpp readiness-awareness exit is **QUALIFIED** through issue #148 / PR #149 and establishes only explicit current non-activating local readiness for one valid supported configured resource using existing registry/runtime/backend checks and the bounded exact executable `--version` probe; authorization, qualification/fit, selection, observation, model activation, cognition invocation, provider binding, fallback, and routing remain separate. Broader issue #115 remains open. Subsequent slices should expand awareness only through the smallest evidence-backed resource surface that preserves the same state and authority separation; adaptive selection complexity should not outrun fresh discovery, authorization, readiness, qualification, observation, and reconstitution evidence.

Recommended first exit boundary:

- GorXu can obtain a fresh runtime inventory for defined local cognition/runtime resources;
- each item has explicit discovered/authorized/ready/qualified state rather than a single availability flag;
- selection binds to the actual execution identity/configuration;
- unavailable or unauthorized resources cannot be selected;
- fallback remains policy-constrained;
- execution evidence records what actually ran;
- reconstitution invalidates volatile observations and re-discovers them;
- no command, risk, Repair, verification, or self-activation authority is widened.

**First-exit qualification evidence:** PR #119 merged as `631f7d2086ae6a5d51308f052025c75032ca047b`, establishing the local runtime inventory/state-selection seam and permanent authorization mutation proof. PR #120 merged as `c2e6de3b7a061abfa25a6fbe37b9621cb9370773`, canonical tree `2bd8dc19d71d27a805d500177cf4952843fb09d4`, exactly matching CI-tested synthetic merge tree `2bd8dc19d71d27a805d500177cf4952843fb09d4`. Exact-head CI #381 / `32651553449` passed Wheel plus Python 3.11–3.14; Python 3.12 recorded Vessel Health 10 PASS, pytest 347 passed / 2 skipped / 449 subtests, unittest 349 / 2 skipped, mutations 13/13 + 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex integrated qualification PASS.

**Governed Tool Gateway awareness qualification evidence:** issue #122 / PR #123 merged as `main@bdbd08a11bb93594dbf84c2fc0e81266ca6dc243`; canonical tree `a4a537983d242988b747d04668055cbd0c2e047b` exactly matches CI-tested synthetic merge tree `a4a537983d242988b747d04668055cbd0c2e047b`. Exact-head CI #394 / `32653017307` passed Wheel plus Python 3.11–3.14; Python 3.12 recorded Vessel Health 10 PASS, pytest 354 passed / 2 skipped / 449 subtests, unittest 356 / 2 skipped, mutations 14/14 + 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex integrated qualification PASS. The permanent `tool-capability-mission-authorization` mutation was killed, proving host-enabled/readiness state cannot imply Mission authorization without sealed Order context.

**Bound hosted/session cognition awareness qualification evidence:** issue #125 / PR #126 merged as `main@6be03b46ac02d121c8ef7e90c25341504fd1d020`; canonical tree `50bf3333eabb066a74b0e62538ea741d7038a106` exactly matches CI-tested synthetic merge tree `50bf3333eabb066a74b0e62538ea741d7038a106`. Exact-head CI #410 / `32661093847` passed Wheel plus Python 3.11–3.14; Python 3.12 recorded Vessel Health 10 PASS, pytest 364 passed / 2 skipped / 449 subtests, unittest 366 / 2 skipped, critical mutations 15/15 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex integrated qualification PASS. The permanent `hosted-cognition-authorization-gate` mutation was killed. The qualified boundary is inventory of already-bound hosted/session cognition resources only: qualification remains independent of authorization, prior remote observation does not imply current readiness, and no provider invocation, catalog discovery, credential validation, switching, fallback, startup, or adaptive routing was added.

**Bound remote cognition transport-freshness qualification evidence:** issue #128 / PR #129 merged as `main@922a35add9c92e7e0d7eed31dc1ff80895e28e61`; canonical tree `9cc6ed2765cfc226e279ae498ebabd6ade675bd5` exactly matches CI-tested synthetic merge tree `9cc6ed2765cfc226e279ae498ebabd6ade675bd5` from synthetic merge `807d4cb70d78ace26349a4fa6412605e89b8dfb8`. Exact-head CI #426 / `32710787713` passed Wheel plus Python 3.11–3.14 on head `ba69209e1a92b48561903d372947bcf2db7c824d`; Python 3.12 recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 373 passed / 2 skipped / 453 subtests, unittest 375 / 2 skipped, critical mutations 16/16 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex integrated qualification PASS. The permanent `cognition-transport-presealed-authority` mutation was killed. The qualified boundary is narrow: an explicit already sealed Mission Order with exact `net_fetch`, current resource identity, and exact origin authority may refresh current-session origin transport evidence for an already-bound remote cognition resource through the existing A5 Tool Gateway. The observation contains no provider credential or cognition payload, is not durable current-readiness state, expires or is replaced by failure, and never sets remote provider `ready`, `authorized`, or `qualified_fit`. Provider/service readiness, credential validity, provider/model availability or fitness, unbound provider discovery, provider switching/fallback, and adaptive routing remain unqualified.

**Transport exact-origin evidence-binding repair:** post-qualification recalibration found that provider/model resource identity does not itself bind endpoint/origin. Issue #132 / PR #133 repaired that evidence seam without adding a new awareness surface. Every transport observation now records the exact normalized origin probed, and passive inventory fails closed when recorded origin is missing, malformed, invalid against the current binding, or differs from the current bound origin. The same provider/model rebound to another endpoint therefore cannot inherit prior transport freshness. Red-before-green CI #443 / `32716652029` captured the canonical defect on test-only head `149d09f8c323cd6d51f0f8600523855d408974f6`. Final head `b50605bb90660a9f3325fd356df65ab5409666e1` passed exact-head CI #448 / `32717652432` across Wheel + Python 3.11–3.14; Python 3.12 recorded Vessel Health 10/0/0/0, pytest 376 passed / 2 skipped / 455 subtests, unittest 378 / 2 skipped, critical mutations 17/17 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. The new permanent `cognition-transport-origin-binding` mutation was killed. Canonical merge `main@d7024261f9c49a8b2bb95a26e5ad0a08a6d5a34a` has tree `d8959016ce59dbd61cb148d974ba0c9e1d351c21`, exactly matching CI-tested synthetic merge `726fc1ef6b351f7bf0371731dd18abafce8fe882`. Remote `ready=False`; provider/service readiness, credential validity, routing, fallback, and all broader #115 gaps remain unqualified.

**Exact bound remote endpoint-surface freshness qualification evidence:** issue #136 / PR #137 qualified the fifth bounded awareness exit from canonical base `main@8184e13141646ee9d232fc10b32714534bf9be5e`. The final head `f86b6dff1cc73b8487ed09ce58720dc4c09f3677` passed exact-head GroX CI #463 / `32742888955` across Wheel + Python 3.11–3.14. Python 3.12 recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 386 passed / 2 skipped / 463 subtests, unittest 388 / 2 skipped, critical mutations 18/18 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. The permanent `cognition-endpoint-exact-binding` mutation was killed. CI-tested synthetic merge `0daa8fe53f1c3d13b7a1a61b7d5d9a18a8348488` had tree `581b492e285f85a43680cb6315ae299b1ea85f33`; guarded canonical merge `main@2b516b8b5e4757c216e5fe561db5325a1471f6de` has the identical tree. The qualified claim is only that the exact configured endpoint surface produced a current bounded HTTP response under explicit pre-sealed authority. Credential validity, authenticated provider/service readiness, model existence/availability/fitness, cognition semantics, provider qualification, provider selection/fallback, adaptive routing, and remote `ready=True` remain unqualified.

**Supported configured cognition-resource discovery qualification evidence:** issue #140 / PR #141 qualified the sixth bounded awareness exit from canonical base `main@f45f9f27169d54b665588d34d92f47c7defc630b`. The red-before-green test-only head `b6ababf3d7395076bc083bd12f0a7d03e3bac1fc` left Wheel green while Python 3.11–3.14 failed on the intended absent `grox.cognition_discovery` seam. Final head `37a0fabe5efbe8d378f3abe11f825316fd468401` passed exact-head GroX CI #476 / `32771922889` across Wheel + Python 3.11–3.14; Python 3.12 recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 392 passed / 2 skipped / 467 subtests, unittest 394 / 2 skipped, critical mutations 19/19 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. Permanent mutation `configured-cognition-discovery-state-separation` was killed. Bounded review `5012089051` passed. CI-tested synthetic merge `5f83c2773c1890b127fd2abbcf178f3e85ef4b03` and canonical merge `main@bf3d0f622ed4088330324f865611e40a4466ae59` share exact tree `baf7841fabbdc02b91fcc750fedc02b0a4e8f929`. This proves only that GroX can recognize repository-supported cognition resources represented by current non-secret configuration and mark them Discovered without activation. Credentials, authenticated readiness, model availability/fitness, qualification, cognition success, arbitrary catalogs, fallback/switching, and routing remain separate and unqualified.

NCI-4 remains the next numbered Native Cognition Independence stage after this Commander-designated bounded priority unless later repository evidence supports replanning. This doctrine does not renumber or pre-qualify NCI-4 through NCI-9.

## Explicit non-goals

This doctrine does not imply:

- autonomous scanning of the Commander's machine outside authorized GroX interfaces;
- unrestricted shell, filesystem, application, browser, credential, or network access;
- automatic trust of discovered models, tools, plugins, services, or devices;
- model/provider-specific routing as architecture;
- self-installation or self-activation of discovered resources;
- bypass of Commander approval or existing Tool Gateway boundaries;
- removal of deterministic routing/authority controls;
- a new command layer between GorXu and Crew;
- a new Apex stage or A8.

## Relationship to the Prime Function

Live environment awareness exists to make GroX a more capable, resilient, context-aware, and continuous personal AI assistant to the Commander. It is not an independent objective and must not evolve into infrastructure discovery for its own sake.

The success condition is not maximum resource enumeration. It is that GorXu can reliably understand the execution capabilities genuinely available to the Vessel, use only those that are permitted and fit for the Mission, verify what happened, and preserve enough evidence to continue coherently after change or reconstitution.

**Configured remote cognition connection-policy awareness qualification evidence:** issue #144 / PR #145 qualified the seventh bounded awareness exit. Final head `c6257872847746b0ef913f2291a6634ac206cc2b` passed exact-head GroX CI #491 / `32775200609` across Wheel + Python 3.11–3.14. Python 3.12 recorded Vessel Health 10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN, pytest 399 passed / 2 skipped / 470 subtests, unittest 401 / 2 skipped, critical mutations 20/20 plus 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS. The permanent `configured-connection-exact-resource-binding` mutation was killed. Bounded review `5012382826` passed with no review threads. CI-tested synthetic merge `14ac96d070c4c5f22005de3b1a170128dc9b7b88` and guarded canonical merge `main@ef88cf34ea6732b65cf2ca461d06076d6af1221b` share exact tree `1480d54f15a4713a083e53cb7174ed8c6c244adf`. The qualified claim is policy awareness only; credentials, authenticated readiness, model availability/fitness, cognition success, broader connection discovery, switching/fallback, adaptive routing, and all later states remain unqualified.

**Configured local llama.cpp readiness awareness qualification evidence:** issue #148 / PR #149 qualified the eighth bounded awareness exit. Red-before-green tests-only head `059211970cd7d70864c2cb25e1a4170c8fbbcba1` kept Wheel green while Python 3.11–3.14 failed only on the intentionally missing `grox.configured_local_readiness` module and Python 3.12 Health remained 10/0/0/0. Final head `575c05ade14a36e664d90e5e7c0a73fb9999cc76` passed exact-head GroX CI #502 / `32777798243` across Wheel + Python 3.11–3.14; Python 3.12 recorded Health 10/0/0/0, pytest 404 passed / 2 skipped / 470 subtests, unittest 406 / 2 skipped, critical mutations 21/21 plus health 7/7, reconstitution 9/9, operational drift 4/4, source provenance 6/6, and Post-Apex PASS. Permanent mutation `configured-local-readiness-authorization-separation` was KILLED. Bounded review `5012611510` passed with no review threads. CI-tested synthetic merge `01f1864410569ab8d45c0e18aa890fa0beb1a954` and guarded canonical merge `main@b477b785104f2931efb22172eea87e22a602346d` share exact tree `3524a24da5b16d90885b10dfbd227e0f019713d2`; exact-tree equality PASS. This evidence qualifies readiness only for the exact supported configured local resource and does not qualify credentials, remote authenticated readiness, model quality/Mission fitness, successful cognition semantics, arbitrary catalog discovery, ambient process scanning, switching/fallback, adaptive routing, or any release/package/NCI/Apex/A8 advancement.
