# GroX Roadmap Doctrine 001 — Live Environment Awareness

**Status:** ROADMAP-BOUND / CURRENT BOUNDED PRIORITY / IMPLEMENTATION NOT YET STARTED

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

## Post-NCI-3 starting primitives

NCI-3 did not implement this doctrine, but it established reusable bounded primitives that the first implementation slice should extend rather than duplicate:

- `ModelRegistry` as an integrity-bound catalogue of represented local models;
- local model readiness reporting against artifact integrity, backend support, placement, and current host hardware/runtime profile;
- explicit model load/invoke/unload with no registry-, readiness-, or reconstitution-driven auto-activation;
- persistent model-store admission with exact artifact/provenance identity;
- observed provider/model/backend/artifact identity on qualified local execution;
- reconstitution that clears active model state and reports current readiness without silently preserving prior activation.

These primitives prove that GroX can observe some local runtime facts. They do **not** yet establish a unified live-resource inventory, authorization state, qualification/fitness state, resource selection policy, fallback policy, remote-provider discovery, tool/application discovery, or general volatile-observation lifecycle.

## Sequencing

NCI-3 is **QUALIFIED** through issue #113 / PR #114 and its exact-tree canonical merge. Live Environment Awareness is now the current bounded architectural workstream tracked by issue #115.

The first implementation slice should establish the smallest useful live-resource inventory and authority separation before introducing adaptive selection complexity. Reuse the qualified NCI-3 local runtime seams where they fit; do not broaden the first slice merely to enumerate every possible resource type.

Recommended first exit boundary:

- GorXu can obtain a fresh runtime inventory for defined local cognition/runtime resources;
- each item has explicit discovered/authorized/ready/qualified state rather than a single availability flag;
- selection binds to the actual execution identity/configuration;
- unavailable or unauthorized resources cannot be selected;
- fallback remains policy-constrained;
- execution evidence records what actually ran;
- reconstitution invalidates volatile observations and re-discovers them;
- no command, risk, Repair, verification, or self-activation authority is widened.

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
