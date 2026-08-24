# GroX Architecture

**Qualified release baseline:** GroX `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`. Canonical source continues on protected `main` and may advance beyond that immutable release through governed PR/CI. GorXu is **APEX QUALIFIED** with **82 Standing Crew**. Protected source additionally has **NCI-1, NCI-2, and NCI-3 QUALIFIED** and eight bounded Live Environment Awareness exits qualified: local runtime, governed Tool Gateway capability awareness, already-bound hosted/session cognition awareness, already-bound remote origin transport freshness, already-bound exact endpoint-surface freshness, passive supported configured cognition-resource discovery, configured remote cognition connection-policy awareness, and configured local llama.cpp readiness awareness. These source advances do not create a new command layer, Apex stage, release, NCI-4, or A8.

## Purpose

GroX is an independent persistent AI personal assistant and command environment. The running system is the Vessel. The human Commander directs the Vessel through Pilot GorXu, the principal personal-assistant interface, sole operational orchestrator, and second-in-command.

## Command architecture

The canonical command hierarchy is deliberately small and must remain visually and operationally distinct from infrastructure:

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

No model, runtime, installer, launcher, state store, workspace, tool, memory system, evaluator, trainer, or other capability may be inserted above GorXu, made a command peer to GorXu, or placed between GorXu and Divisions/Standing Crew as an authority layer.

## Command versus infrastructure boundary

GroX distinguishes **authority flow** from **resource flow**.

### Authority flow

```text
Commander
    ↓
Pilot GorXu
    ↓
Divisions
    ↓
Standing Crew
```

### Infrastructure/resources used by that authority flow

```text
native/local cognition            optional external intelligence
runtime assets / Crew definitions private Vessel state
Commander work root               Tool Gateway / governed tools
memory / evidence                 training / evaluation / lineage
inference backends                installer / CLI / desktop launcher
```

The infrastructure block has no command rank. It exists to let GorXu and authorized Crew perform work.

Consequences:

- Crew dossiers and craft can be stored under runtime assets without placing Crew above GorXu;
- a native model may power Pilot cognition and authorized Crew cognition without becoming the Pilot or an intermediate command layer;
- an external model remains a governed capability selected by GorXu, not an inherited authority source;
- a CLI, bridge, or desktop launcher is a Commander Seat entry path into the same GorXu-led Vessel, not another orchestrator;
- private state records and restores Vessel activity but does not decide Commander intent;
- the Commander workspace is a bounded work surface, not a source of command authority.

Physical storage placement, process topology, model dependency, or data flow must never be interpreted as organizational rank.

## Authority flow in operation

1. The Commander provides intent.
2. GorXu interprets the directive and determines the work required.
3. GorXu consults Mission Control and relevant Crew/capabilities for risk, capability, research, and verification needs.
4. GorXu selects eligible Crew and issues bounded Mission Orders.
5. Crew execute only within the granted authority through governed capabilities.
6. Exceptions return to GorXu. GorXu may consult additional Crew before deciding.
7. Critical, irreversible, or material intent-changing decisions escalate to the Commander.
8. Evidence and verification return through GorXu for synthesis and closure.

Authority may narrow as it travels downward. It may not widen without a new decision from the appropriate authority.

## Runtime components

The following list describes runtime components, **not command rank**. Component numbering does not imply that one component commands another.

1. **Commander Seat:** CLI/bridge and future launcher/UI surfaces for directives, status, intervention, and review.
2. **Pilot GorXu:** interprets intent, plans, consults Mission Control, selects Crew, issues Orders, governs cognition/capability use, and synthesizes outcomes.
3. **Mission Control:** risk, authority, routing, verification, evidence, and advisory policy under GorXu.
4. **Standing Crew:** durable organizational identities with fresh mission-specific tours, bounded relevant memory, selective deep craft on Inspect tours, and optional governed read-only cognition when separately configured.
5. **Native/external cognition resources:** provider/model capabilities that may advise Pilot GorXu or operate inside explicitly authorized Crew cognition placements; never command layers.
6. **Tool Gateway:** deny-wins capability enforcement and Commander-work/host confinement.
7. **Mission Store:** durable Mission, Order, Evidence, Crew, memory, and performance state.
8. **Living Company Intelligence:** advisory memory retrieval, Inspect-only selective craft context, and experienced eligible-Crew ranking under GorXu.
9. **Durable Operations:** private graph-run/checkpoint/exception/mutation ledger for safe resume and compensation under GorXu.
10. **Executive Exception Loop:** deterministic classification and bounded consultation/replan policy under GorXu.
11. **Verification:** independent verification path where policy requires it.
12. **Persistence Manager:** private operational-state snapshots, integrity checking, and confirmation-gated restore.
13. **Installation/runtime layout:** host configuration, runtime assets, private state, Commander work, and future launcher/model provisioning used to materialize the same Vessel on supported hosts.

Selective Crew cognition is not another runtime command layer. It is an optional bounded working mode inside an already-issued Standing Crew Inspect tour and remains subordinate to the same Mission Order and Tool Gateway.

## NCI filesystem-role architecture

NCI-1A through NCI-1D establish the qualified local installation/runtime/model foundation beneath the existing command model. NCI-2 and NCI-3 then qualify the exact local seed-cognition and bounded offline GorXu profile on that foundation.

### NCI-1A — commissioned workspace

Current protected source can commission a dedicated local workspace with:

- default `~/GroX`;
- Commander-selected alternative path;
- platform-aware Linux/macOS host configuration;
- versioned workspace ownership marker and host binding;
- collision and implicit-rebind refusal;
- atomic configuration writes;
- idempotent same-workspace commissioning;
- marked partial-workspace recovery.

This commissioning layer does not create a second Vessel or Pilot.

### NCI-1B — separated runtime, state, and work

`VesselLayout` distinguishes three filesystem roles:

```text
runtime/assets root      private state root      Commander work root
       │                        │                       │
Crew dossiers/craft       grox.sqlite3             Mission files
policy / schemas           browser evidence         Tool Gateway fs scope
versioned app assets       isolated scratch         bounded tests/work
```

Separated layouts require the three roots not to overlap. Legacy `PilotGorXu(vessel_root)` behavior remains supported through a one-root compatibility layout, including the historical `configs/state/grox.sqlite3` path.

In separated mode:

- Pilot GorXu loads the Standing Crew roster and runtime policy from `asset_root`;
- private SQLite state lives under `state_root`;
- browser evidence and isolated-workspace scratch use private state rather than Commander work;
- Tool Gateway ordinary filesystem authority is rooted only at `work_root`;
- runtime assets and private state are outside normal Commander-work filesystem traversal;
- path escape from Commander work into state/assets fails closed.

This is a filesystem/security architecture **below Pilot GorXu**. Crew definitions residing in `asset_root` remain subordinate to GorXu. Model artifacts later placed in runtime/model resources will likewise remain governed capabilities rather than authority layers.

NCI-1C now packages and validates the canonical runtime assets so a commissioned non-editable installation can start the same Pilot GorXu with all 82 Standing Crew outside a source checkout. NCI-1D adds the integrity-bound model registry and explicit local inference runtime. NCI-2 qualifies the exact Qwen3-4B Q4_K_M seed through pinned `llama.cpp`, and NCI-3 qualifies the bounded offline GorXu conversational + governed Crew-orchestration profile. Public one-command installation, desktop launchers, NCI-4, and broader NCI-8 offline Vessel qualification remain separate future gates.

## Live Environment Awareness architecture

Live Environment Awareness is a Pilot-owned capability layer beneath GorXu. It does not create a discovery daemon, command layer, alternate router, or new authority source.

Every represented resource preserves six distinct states:

1. **Discovered** — current evidence says the resource exists or is represented;
2. **Authorized** — Commander/GroX policy permits consideration for the bounded Mission;
3. **Ready** — current host/resource evidence satisfies the relevant readiness requirements;
4. **Qualified / fit** — evidence supports the bounded work class;
5. **Selected** — GorXu selects it under existing policy;
6. **Observed** — GroX records what actually executed or was observed.

No state automatically implies the next. Current protected source qualifies eight bounded surfaces: defined local runtime awareness (#119/#120), passive governed Tool Gateway capability awareness (#122/#123), awareness of hosted/session cognition already bound to GorXu/Crew seats (#125/#126), explicit current-session **origin transport freshness** for an already-bound remote cognition resource (#128/#129), exact endpoint-surface freshness for that already-bound remote class (#136/#137), passive supported configured cognition-resource discovery (#140/#141), and configured remote cognition connection-policy awareness (#144/#145), and configured local llama.cpp readiness awareness (#148/#149).

The configured-connection policy-awareness surface is also deliberately non-operational. For one valid configured `openai` cognition resource it derives the exact normalized origin from the configured endpoint, reports host-policy permission separately from an already-sealed Mission Order, and requires exact operation/resource/endpoint/origin authority before reporting `authorized=True`. It performs no network request, credential inspection, provider construction, model activation, cognition invocation, selection, or routing; `ready`, `qualified_fit`, `selected`, and `observed` remain false.

The configured-local readiness surface is likewise explicit and non-activating. For one valid supported configured `local-llama-cpp` cognition resource, it reuses the existing GroX model registry/runtime/backend readiness primitives to check exact model registration and artifact integrity, current host constraints, and the exact configured llama.cpp executable against the pinned supported build. The only local process probe is the existing bounded `llama.cpp --version` support check. `ready=True` remains strictly separate from Mission authorization, qualification/fit, selection, and observation; the surface never loads a model, invokes cognition, touches network or credentials, binds a provider, creates a Mission, performs fallback, or changes routing.

The remote transport refresh is deliberately narrow. Passive inventory remains zero-network. Active refresh requires an already sealed Mission Order granting exact `net_fetch`, `operation=cognition_transport_probe`, the exact current resource ID, and the exact normalized bound origin; the host Tool Gateway policy must independently allow the same origin. Runtime I/O goes only through `ToolGateway.fetch_url`. The observation retains only volatile timestamp/reachable-state/bounded HTTP status and discards response content. It never validates provider credentials, invokes cognition, changes provider binding, sets remote `ready`, creates qualification, or authorizes adaptive routing.

Reconstitution may retain attributable historical execution evidence where separately designed, but volatile current readiness/transport observations must be rediscovered rather than treated as durable fact. Parent issue #115 remains open for broader awareness.

## Standing Crew model

Crew are logically persistent organizational identities with durable dossiers, competencies, procedures, history, memory, and canonical craft. They need not remain as live model processes while asleep.

Each wake creates a fresh tour context containing only what is needed for the current Mission plus relevant retrieved memory. A bounded Inspect tour may additionally receive Mission-relevant craft sections from that Crew member's canonical craft card. Verify, Repair, and Execute do not carry unused deep craft in the first cognition seam. The complete historical memory store and complete deep craft card are never injected by default.

Crew competence and Mission authority are separate:

- Competence describes what a Crew member knows how to do.
- Mission authority describes what that Crew member may do now.

Craft, memory, provider output, confidence, prior performance, and model quality belong to the competence/advisory side of that boundary. They cannot manufacture authority or alter Crew position beneath GorXu.

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

After Crew routing and before an **Inspect** Mission Order is sealed, Living Company Intelligence may attach bounded Mission-relevant craft for the assigned Standing Crew member. Other modes retain their existing task/memory context without selective deep craft.

The selective-craft path:

- reads only the assigned active Crew member's canonical craft card;
- requires `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` to fit **in full** when present;
- fails closed rather than truncating mandatory safety/operational binding when the configured budget is insufficient;
- selects additional Mission-relevant sections deterministically from the remaining budget;
- defaults to at most **6 sections / 4,500 characters**;
- records the full-card SHA-256, selected headings/size, source revision, and freshness policy;
- emits explicit `craft_selection` evidence during Inspect execution;
- never treats craft prose as authority;
- never injects the complete deep card by default.

When a Crew cognition provider is separately configured, the first governed cognitive seam is **Inspect-only**. It defaults to:

- at most **4** cognitive steps;
- at most **1** cognitive `test_run` per tour;
- at most **8,000** characters in each bounded observation returned to cognition;
- at most **4,000** characters in the final cognitive work product.

Provider-facing Order, craft, memory, and observation values are copies. Provider-local mutation cannot alter the executor-owned context, sealed Order, or prior observation history. Governed observations remain attributable evidence even when the provider later fails. Persistent read-observation evidence retains path/count/hash metadata rather than copying raw file contents into the cognitive evidence record.

A mutating action request or scope escape is denied and does not gain a broader fallback. Known recoverable provider/contract failures may degrade to the existing deterministic Inspect executor. Verify, Repair, and Execute remain on their existing deterministic paths in this first seam.

Controlled fake-provider CI historically qualified only the provider-neutral Crew-cognition seam and its safety properties. Issue #76 / PR #79 later supplied separate operational evidence for one live locally trained neural action-selection provider. That later qualification remains bounded to the Inspect Crew cognition seat and does not turn arbitrary project/session or external providers into qualified Crew cognition.

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

Live Environment Awareness also reuses this same Gateway for the #128/#129 remote cognition transport-freshness probe. Awareness cannot open a parallel network client or acquire authority by asking the Gateway to seal an unsealed Order; the pre-sealed exact authority requirement is permanently mutation-proven.

NCI-1B further binds ordinary filesystem access to the Commander work root in separated mode. Private state and runtime assets are outside that root and may not be reached through path escape.

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

Pilot cognition and Crew cognition are distinct placements under the same authority doctrine. Pilot cognition supplies cognitive energy/advice to GorXu before or during orchestration. Optional Crew cognition operates only inside an already-issued bounded Inspect tour. Neither placement can create authority, and external intelligence does not inherit command merely because a provider can reason.

The Native Cognition Independence program changes **who owns and can supply the cognitive engine**, not who is Pilot. Native local cognition exists to make GorXu a stronger, more independent orchestrator and personal assistant. It does not replace GorXu or sit between GorXu and Crew as command authority.

## Recruitment and evolution

When no existing Crew member sufficiently covers a demonstrated capability gap, GorXu may initiate recruitment under GroX policy.

A recruit becomes durable standing Crew with a canonical dossier. Recruitment must not:

- create a competing orchestrator;
- grant authority merely because competence exists;
- silently duplicate an existing Crew role;
- bypass inspection, validation, or roster integrity checks.

Evolution should modify skills, procedures, routing metadata, memory, and cognition through evidence-backed processes rather than uncontrolled self-rewriting. Model evolution cannot self-authorize promotion or change the command hierarchy.

## Persistence planes

GroX separates persistence into three responsibility planes:

1. **Cognitive continuity:** the `Space Exploration` ChatGPT project is the current reconstitution home for Pilot GorXu and durable project context while native local cognition remains under development.
2. **Vessel source:** the GroX GitHub repository is the durable body for code, doctrine, Crew dossiers, tests, and source-controlled history.
3. **Operational state:** private Mission, evidence, Crew, and runtime-memory state is persisted locally and exported as verified private `.groxstate` snapshots.

These persistence planes are separate from NCI-1B's runtime/assets, private-state, and Commander-work filesystem roles. Neither construct is a command hierarchy.

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

CLI is the initial interface. Other interfaces and desktop launchers can be added without changing the command architecture. Every interface must enter the same Pilot GorXu authority plane.

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

## Architecture non-regression statement

All future NCI, model, installer, launcher, persistence, Crew, and capability work must preserve the following interpretation without ambiguity:

> **The Commander directs Pilot GorXu. Pilot GorXu orchestrates Divisions and Standing Crew. Models and infrastructure supply capabilities and energy to that GorXu-led Vessel; they do not command it.**
