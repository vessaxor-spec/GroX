# GroX Architecture

**Qualified release baseline:** GroX `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`. Canonical source continues on protected `main` and may advance beyond that immutable release through governed PR/CI. GorXu is **APEX QUALIFIED** with **82 Standing Crew**. A1–A7 are qualified for the current project-hosted operating model.

## Purpose

GroX is an independent persistent AI command environment. The running system is the Vessel. The human Commander directs the Vessel through Pilot GorXu, the primary orchestrator and second-in-command.

## Command architecture

```text
Commander
    │ intent / directives
    ▼
Pilot GorXu
    │
    ├── Mission Control
    │     ├── risk and authority analysis
    │     ├── routing intelligence
    │     ├── verification policy
    │     └── operational research
    │
    └── Divisions
          └── Standing Crew
                ├── mission-specific tour context
                ├── bounded tools
                ├── evidence production
                └── durable identity and memory
```

GorXu is the single operational orchestrator. Mission Control is a native GroX subsystem managed by GorXu. It may enforce GroX constitutional constraints, but it does not create an independent command hierarchy.

## Authority flow

1. The Commander provides intent.
2. GorXu interprets the directive and determines the work required.
3. GorXu consults Mission Control and relevant Crew for risk, capability, research, and verification needs.
4. GorXu issues bounded Mission Orders to selected Crew.
5. Crew execute only within the granted authority.
6. Exceptions return to GorXu. GorXu may consult additional Crew before deciding.
7. Critical, irreversible, or material intent-changing decisions escalate to the Commander.
8. Evidence and verification return through GorXu for synthesis and closure.

Authority may narrow as it travels downward. It may not widen without a new decision from the appropriate authority.

## Runtime layers

1. **Commander Seat:** CLI/bridge for directives, status, intervention, and review.
2. **Pilot GorXu:** interprets intent, plans, consults Mission Control, selects Crew, issues Orders, and synthesizes outcomes.
3. **Mission Control:** risk, authority, routing, verification, evidence, and advisory policy.
4. **Standing Crew:** durable organizational identity with fresh mission-specific tours, bounded selected craft/memory context, and optional governed read-only cognition when separately configured.
5. **Tool Gateway:** deny-wins capability enforcement and host/Vessel confinement.
6. **Mission Store:** durable Mission, Order, Evidence, Crew, memory, and performance state.
7. **Living Company Intelligence:** advisory memory retrieval, selective specialist craft context, and experienced eligible-Crew ranking under GorXu.
8. **Durable Operations:** private graph-run/checkpoint/exception/mutation ledger for safe resume and compensation under GorXu.
9. **Executive Exception Loop:** deterministic classification and bounded consultation/replan policy under GorXu.
10. **Verification:** independent verification path where policy requires it.
11. **Persistence Manager:** private operational-state snapshots, integrity checking, and confirmation-gated restore.

Selective Crew cognition is not another runtime command layer. It is an optional bounded working mode inside an already-issued Standing Crew Inspect tour and remains subordinate to the same Mission Order and Tool Gateway.

## Standing Crew model

Crew are logically persistent organizational identities with durable dossiers, competencies, procedures, history, memory, and canonical specialist craft. They need not remain as live model processes while asleep.

Each wake creates a fresh tour context containing only what is needed for the current Mission plus relevant retrieved memory and bounded Mission-relevant craft. The complete historical memory store and complete deep craft card are not injected by default. This preserves continuity and expertise without allowing old working context or million-character craft libraries to accumulate indiscriminately.

Crew competence and Mission authority are separate:

- Competence describes what a Crew member knows how to do.
- Mission authority describes what that Crew member may do now.

Craft, memory, provider output, confidence, and prior performance belong to the competence/advisory side of that boundary. They cannot manufacture authority.

## Mission Control

Mission Control is a GroX-native service layer available to GorXu. Its responsibilities include:

- risk analysis;
- authority-envelope validation;
- capability matching;
- routing support;
- independent verification requirements;
- evidence requirements;
- research and advisory support;
- anomaly and exception analysis.

Mission Control does not issue operational orders directly to Crew unless GorXu explicitly delegates a bounded control function. Such delegation never creates a parallel orchestrator.

## Inspect and repair protocol

Inspection and mutation are separate modes.

### Inspect

- read, analyze, test, and report;
- no mutation authority unless explicitly required for a safe diagnostic and granted in the Mission Order;
- findings return to GorXu.

An optional provider-neutral Crew cognition seam may assist Inspect tours. It receives a sanitized copy of the issued Order plus bounded selected craft, bounded relevant memory, and observations produced through the existing Tool Gateway. The first bounded seam permits only `fs_list`, `fs_read`, and `test_run`; all requests remain subject to the sealed Order, Crew capability, scope, host policy, and Tool Gateway denial. The provider does not own tools directly.

### Repair

- issued only after GorXu has accepted a repair path within delegated authority or the Commander has approved where required;
- mutation is restricted to explicit capabilities, paths, systems, and stop conditions;
- blockers, better methods, elevated risk, or scope changes return to GorXu before affected mutation continues.

The first bounded Crew cognition seam does not operate in Repair. Model or craft output cannot create Repair authority.

## Selective craft and Crew cognition

After Crew routing and before Mission Order sealing, Living Company Intelligence may attach bounded competence context for the assigned Standing Crew member.

The selective-craft path:

- reads only the assigned active Crew member's canonical craft card;
- reserves context for `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` when present;
- selects additional Mission-relevant sections deterministically;
- defaults to at most **6 sections / 4,500 characters**;
- records the full-card SHA-256, selected headings/size, source revision, and freshness policy;
- never treats craft prose as authority;
- never injects the complete deep card by default.

When a Crew cognition provider is separately configured, the first governed cognitive seam is **Inspect-only**. It defaults to:

- at most **4** cognitive steps;
- at most **1** cognitive `test_run` per tour;
- at most **8,000** characters in each bounded observation returned to cognition;
- at most **4,000** characters in the final cognitive work product.

Provider-facing Order, craft, memory, and observation values are copies. Provider-local mutation cannot alter the executor-owned context, sealed Order, or prior observation history. Governed observations remain attributable evidence even when the provider later fails. Persistent read-observation evidence retains path/count/hash metadata rather than copying raw file contents into the cognitive evidence record.

A mutating action request or scope escape is denied and does not gain a broader fallback. Known recoverable provider/contract failures may degrade to the existing deterministic Inspect executor. Verify, Repair, and Execute remain on their existing deterministic paths in this first seam.

Controlled fake-provider CI qualifies only the provider-neutral seam and its safety properties. It is **not** evidence that a live project/session or external model provider is operational for Crew cognition. Live provider activation requires separate operational evidence.

## Verification

Verification is independent where policy requires it. The executor may provide self-checks, but self-checks are not independent verification.

Verification should evaluate the evidence package, requested outcome, authority compliance, and actual resulting state.

The first bounded Crew cognition seam does not run in Verify mode and therefore cannot become an alternate automatic verifier or satisfy verifier independence by itself.

## Mission outcome truthfulness

Successful bounded execution is not automatically proof that the Commander objective was delivered. In the single-Mission Pilot path, GorXu separates executor lifecycle state from Commander-facing Mission outcome and persists `mission_outcome` evidence containing:

- execution state;
- actual effect;
- objective delivery/proof state;
- remaining mutation state;
- next required authority path where applicable;
- verification scope.

A generic Execute fallback that only inventories bounded Mission context is reported as `scan_only` at Mission level while retaining `execution_status: completed`. Its objective is `not_delivered`, mutation is false, and any verification PASS is explicitly scoped to the bounded execution evidence rather than the requested objective.

Supported explicit Repair remains the mutation authority path. A successful verified `write_text` Repair may report the bounded objective satisfied. A failed Repair that completes rollback reports `mutation_rolled_back` and no remaining mutation. If rollback fails or mutation state diverges, GroX reports `mutation_state_unresolved`, preserves `mutation: true`, and returns the condition to Pilot recovery rather than claiming safe completion.

Outcome classification is evidence and synthesis. It does not grant capability, Repair authority, or broader scope, and it does not change Mission Graph authority semantics.

## Mission durability

A Mission is a first-class durable object. The qualified architecture persists:

- Commander directive;
- GorXu plan;
- Mission Orders;
- Crew assignments and tours;
- tool actions;
- exceptions and decisions;
- approvals when required;
- evidence;
- verifier results;
- final disposition.

A restarted Vessel must determine the last committed Mission state and resume safely rather than reconstructing state from conversational memory.

The qualified Durable Operations implementation persists validated graph-run state, checkpoints, exception decisions, bounded resume/cancellation state, mutation-journal evidence, and hard Mission cost commitments in the private SQLite plane. A fresh Pilot converts in-flight state to `interrupted`, preserves committed nodes without replay, and may resume the same Mission ID from persisted state. Automatic resume is bounded; unknown or divergent mutation state halts rather than being guessed through.

## Durable Operations and executive exceptions

The qualified runtime includes a private `DurableState` service under GorXu. It does not command Crew. It records graph-run state, execution checkpoints, exception decisions, cancellation/resume state, and supported Repair mutation journals in the same private SQLite operational plane.

Ordinary recoverable graph exceptions are evaluated by a deterministic Executive Exception Loop. When policy permits recovery, GorXu compares an eligible replacement, issues that Crew a real read-only consultation Order, records the consultation evidence, and only then commits a bounded replan. Critical, irreversible, authority-divergent, or material-intent exceptions require Commander decision. Unknown non-critical exceptions halt with GorXu rather than escalating unnecessarily.

Supported `write_text` Repair is atomic and journaled before mutation. Post-Repair test failure compensates the exact bounded pre-state when it can be proven safe; externally diverged state is never silently overwritten.

## Tool architecture

Crew do not receive unrestricted raw host access. Tool use passes through a GroX Tool Gateway that intersects:

- Mission authority;
- Crew capability;
- host policy;
- path and origin restrictions;
- secret policy;
- side-effect class;
- resource budget;
- audit and evidence requirements.

The intersection is deny-wins. Host restrictions may narrow authority but never expand it.

The A5-qualified Tool Gateway v2 exposes bounded filesystem/list/test operations plus governed isolated workspace execution, memory-only secret aliases, exact-origin read-only HTTP(S), offline browser evidence capture, and pre-registered stdio MCP adapters. Privileged actions require explicit Mission Order grants and operation-specific policy intersections. Workspace and browser isolation prefer user/PID/network namespaces and may use a pre-provisioned, digest-pinned Docker boundary when the host denies namespace mapping. Neither path permits unrestricted raw-host fallback.

A5 browser capture deliberately keeps network authority in the Gateway: approved HTML is fetched through `net_fetch`, then rendered offline while browser-originated HTTP(S) is blocked. MCP process definitions are host/Pilot registered rather than Crew supplied, and mutating MCP tools require a separate mutation action grant. Secret values remain memory-only and are not durable Mission data.

The Crew cognition seam reuses this same Gateway. It does not add direct provider tool ownership, an alternate filesystem API, broader network access, or an MCP/desktop path.

Unrestricted interactive desktop actuation, arbitrary third-party/networked MCP transports, runtime image pulls/builds, and optional external-agent delegation remain outside the A5-qualified boundary.

## Memory architecture

The qualified memory architecture separates:

1. Working memory: current tour context.
2. Episodic memory: what happened on prior tours.
3. Semantic memory: durable learned facts and relationships.
4. Procedural memory: learned and versioned ways of working.
5. Vessel memory: organizational knowledge shared independently of any single Crew member.

Memory must support provenance, relevance, consolidation, correction, and bounded forgetting.

The qualified Living Company implementation provides episodic retrieval plus durable semantic, procedural, and Vessel memory. Durable records require explicit provenance, confidence, scope, and keys; corrections supersede rather than silently rewrite prior active records; records can be deactivated for bounded forgetting. Retrieval is relevance-scored and capped by item/character budgets, with memory-plane diversity preserved where relevant.

Living Company Intelligence also persists per-Crew/task-class performance observations and lets GorXu rank only otherwise-eligible Crew using competence, evidence quality, reliability, load, cost, latency, risk, and prior performance. Memory, craft, cognition, and performance remain advisory: they cannot grant capability, lower risk, authorize Repair, alter Commander intent, self-route Crew, or bypass verifier independence. Autonomous memory consolidation is not yet implemented.

## Cognitive Pilot

GorXu may use a provider-neutral reasoning layer for interpretation, uncertainty detection, strategy comparison, and Crew recommendation. Cognition is advisory to the Pilot and never becomes an authority source.

Deterministic Mission Control and Tool Gateway policy remain capable of denying model proposals. A model may raise caution but cannot lower the risk floor or grant itself mutation authority.

Pilot cognition and Crew cognition are distinct placements under the same authority doctrine. Pilot cognition advises GorXu before or during orchestration. Optional Crew cognition operates only inside an already-issued bounded Inspect tour. Neither placement can create authority, and external intelligence does not inherit command merely because a provider can reason.

## Recruitment and evolution

When no existing Crew member sufficiently covers a demonstrated capability gap, GorXu may initiate recruitment under GroX policy.

A recruit becomes durable standing Crew with a canonical dossier. Recruitment must not:

- create a competing orchestrator;
- grant authority merely because competence exists;
- silently duplicate an existing Crew role;
- bypass inspection, validation, or roster integrity checks.

Evolution should modify skills, procedures, routing metadata, and memory through evidence-backed processes rather than uncontrolled self-rewriting.

## Persistence planes

GroX separates persistence into three planes:

1. **Cognitive continuity:** the `Space Exploration` ChatGPT project is the current reconstitution home for Pilot GorXu and durable project context.
2. **Vessel source:** the GroX GitHub repository is the durable body for code, doctrine, Crew dossiers, tests, and source-controlled history.
3. **Operational state:** private Mission, evidence, Crew, and runtime-memory state is persisted locally and exported as verified private `.groxstate` snapshots.

The active sandbox is a replaceable flight computer, not the permanent Vessel. Full rules and recovery gates are defined in `docs/architecture/PERSISTENCE_ARCHITECTURE.md`.

## Commander Seat

GroX is incomplete without a usable Commander Seat. The Commander must be able to:

- issue directives;
- observe Mission state;
- inspect evidence and decisions;
- answer escalations;
- interrupt or redirect work;
- suspend or terminate a Mission;
- review the Vessel's current condition.

CLI is the initial interface. Other interfaces can be added without changing the command architecture.

## Apex synthesis and budget integrity

The A7-qualified Mission Graph extends structural synthesis with attributable contradiction reconciliation and a hard Mission cost ceiling.

- `MissionBudget.max_cost_units` is a hard Mission limit; each node declares bounded `cost_units`.
- Cost commitments are persisted before execution so a crash or resume cannot reset consumed budget.
- Parallel-ready work is reserved against the aggregate remaining budget before execution.
- Contradictory `finding` evidence is reconciled only from attributable source Orders.
- Any source Order contributing to a resolved contradiction must itself be independently verified.
- Runtime verifier evidence is accepted only from the actual verification path; ordinary Crew cannot manufacture verifier authority.
- Repeated findings from one Order are normalized so duplicate output cannot multiply one source's weight.
- Equal-weight conflict remains unresolved rather than manufacturing certainty.

These controls improve orchestration quality without changing the command relationship or granting new authority.
