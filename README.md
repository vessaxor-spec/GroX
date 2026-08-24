<a id="readme-top"></a>

<p align="center">
  <img src="assets/banner/grox-banner-hd-optimized.png" alt="GroX persistent AI command environment banner" width="100%">
</p>

<div align="center">

# GroX

### Persistent AI personal assistant and command environment

A persistent AI Vessel whose **prime function is to assist the Commander**, translating Commander intent into useful conversation, bounded Missions, durable execution, attributable evidence, independent verification, recoverable continuity, and progressively owned cognition.

[![GroX CI](https://github.com/vessaxor-spec/GroX/actions/workflows/ci.yml/badge.svg)](https://github.com/vessaxor-spec/GroX/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/vessaxor-spec/GroX?label=release)](https://github.com/vessaxor-spec/GroX/releases/latest)

[**Public overview**](https://vessaxor-spec.github.io/grox/) ·
[**Explore the architecture**](docs/architecture/ARCHITECTURE.md) ·
[**See current progress**](docs/stewardship/progress-tracker.md) ·
[**View the roadmap**](docs/stewardship/ROADMAP.md) ·
[**Meet the Crew**](docs/stewardship/CREW_ROSTER.md)

**Release:** `v0.8.0` · **Package:** `0.8.0` · **Operating standard:** `APEX QUALIFIED` · **Standing Crew:** `82`

</div>

---

<details>
<summary><strong>Table of contents</strong></summary>

- [About GroX](#about-grox)
- [Prime function](#prime-function)
- [Command and infrastructure](#command-and-infrastructure)
- [How GroX works](#how-grox-works)
- [What GroX owns](#what-grox-owns)
- [Current state](#current-state)
- [Native cognition direction](#native-cognition-direction)
- [Local installation direction](#local-installation-direction)
- [Qualified limits](#qualified-limits)
- [Quick start](#quick-start)
- [Persistence and recovery](#persistence-and-recovery)
- [Repository map](#repository-map)
- [Governance and evidence](#governance-and-evidence)
- [Roadmap](#roadmap)

</details>

## About GroX

GroX is an independent, persistent **AI personal assistant and command environment** built around one canonical command spine:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

The Commander defines intent and retains final authority. Pilot GorXu is the Vessel's second-in-command, principal assistant interface, and **sole operational orchestrator**. Divisions organize operational areas. Standing Crew perform bounded work through Mission Orders issued under GorXu.

Mission Control is a **GroX-native policy and advisory service** used by GorXu for governance, risk analysis, routing support, verification policy, evidence requirements, and operational intelligence. It is not a command layer and cannot become a parallel orchestrator.

GroX's strategic direction is native-cognition independence: the Vessel should progressively own the runtime, local models, training evidence, evaluation, model lineage, installation path, and governed activation needed to remain useful locally and offline. External models remain valuable, but the target architecture treats them as optional governed capabilities rather than required pilots.

## Prime function

GroX exists first to serve as the Commander's persistent AI personal assistant and operating partner. The normal Commander experience should remain conversational and broadly useful: ask questions, explore ideas, research, plan, work with files and code, operate qualified tools and connected systems, use memory, automate recurring work, delegate bounded work to Crew, and carry multi-step objectives through to evidence-bearing outcomes as capabilities permit.

Native cognition and evolution are **core survival and improvement functions**, not replacement purposes. Their purpose is to make GroX a more useful, resilient, private, capable, cost-independent, and continuously available assistant. GroX must not optimize itself into primarily a model-training or research system at the expense of helping the Commander.

The governing relationship is permanent:

> **Commander intent and objectives govern. GorXu turns that intent into effective assistance and action. Evolution exists to improve that service.**

GroX may challenge an instruction, surface risk, identify contradictions, or recommend a safer or stronger approach. It may not substitute a self-generated objective for Commander intent, and no model, Crew member, trainer, evaluator, memory system, or evolutionary process may acquire authority over the Commander.

A more capable GroX must remain a more capable personal assistant.

## Command and infrastructure

GroX deliberately separates **who commands** from **what powers the Vessel**.

### Command hierarchy

```text
Commander
    ↓
Pilot GorXu
    ↓
Divisions
    ↓
Standing Crew
```

### Infrastructure and governed resources

These are used by the command hierarchy but are **not themselves command layers**:

```text
native cognition / local models      external models
runtime assets / Crew definitions    private Vessel state
Commander workspace                  Tool Gateway / tools
memory / evidence                    training / evaluation
inference backends                   installer / desktop launcher
```

Storage or dependency relationships do not create rank. Crew dossiers may live in runtime assets, but GorXu loads, selects, and commands the Crew. A native model may power GorXu and relevant Crew cognition, but the model is the Vessel's engine/cognitive capability—not its Pilot. CLI and desktop launchers enter the same GorXu-led Vessel; they do not create another command path.

This distinction is a permanent non-regression requirement for Native Cognition Independence and local installation work.

### Why this exists

GroX is designed to make capable AI assistance and execution durable without making authority ambiguous. It is built to prevent several common failures in autonomous systems:

- treating a model session as the whole system;
- confusing competence with permission;
- allowing Crew, tools, evaluators, models, trainers, schedulers, installers, or runtime services to become parallel orchestrators;
- confusing a filesystem/runtime diagram with command hierarchy;
- losing Mission state, evidence, or recovery context when a process or host disappears;
- letting retries, replanning, fallback, or model evolution silently widen authority;
- allowing an executor to satisfy an independence requirement by verifying itself;
- representing experiments, simulations, staged behavior, or model scores as stronger operational proof than the evidence supports;
- representing successful bounded execution as proof that the Commander objective was delivered when only a narrower effect occurred;
- allowing improvement proposals or newly trained models to self-activate;
- making the Vessel's existence depend on one model vendor, paid subscription, or network connection;
- optimizing the Vessel for self-improvement while degrading its usefulness as the Commander's assistant.

## How GroX works

GroX keeps command authority separate from the services and capabilities used to execute work:

```text
Commander intent
  -> Pilot GorXu
     -> provides the primary personal-assistant interface
     -> consults Mission Control when required
     -> answers directly or constructs a Mission / Mission Graph
     -> selects eligible Standing Crew when delegated work is useful
     -> issues bounded Mission Orders
        -> governed capabilities and tools
        -> attributable evidence
     -> independent verification when required
     -> Pilot synthesis
     -> Commander escalation for critical, irreversible,
        authority-divergent, or material intent-changing decisions
```

Capabilities, tools, schedulers, memory, evaluators, models, training systems, runtime assets, state stores, workspaces, installers, launchers, and external intelligence are resources under this relationship. They are not command layers.

### Core operating principles

1. **Commander sovereignty.** The Commander sets intent and retains ultimate authority.
2. **Personal assistance is the prime function.** GroX evolves and operates to become a better persistent assistant to the Commander; self-improvement is subordinate to that purpose.
3. **One operational orchestrator.** GorXu is the sole operational orchestrator and principal assistant interface; no Crew member, model, or subsystem may become a rival command spine.
4. **Infrastructure is not hierarchy.** Models, runtimes, storage roots, tools, installers, and launchers may support the Vessel but cannot acquire command rank.
5. **Competence is not permission.** Crew may act only within the authority granted by the current Mission Order.
6. **Inspection is not mutation.** Inspect and Repair authority remain structurally separate.
7. **Deny wins.** Tool access is capability-gated and constrained by Mission Order, Crew capability, and host policy.
8. **Verification remains independent.** Where policy requires independence, the verifier must differ from the executor and evidence must be attributable.
9. **Failure narrows authority.** Recovery, fallback, replanning, and model degradation may restore reversible execution but may not widen scope or change Commander intent.
10. **Continuity requires evidence.** Persistence, recovery, reconstitution, and model lineage are infrastructure, not assumptions about a surviving process.
11. **Execution completion is not objective completion.** GorXu must report the actual bounded effect, Commander-objective state, remaining mutation state, and verification scope rather than promoting a completed step into a stronger delivery claim.
12. **Evolution is governed.** A trained descendant, external teacher, or higher benchmark score cannot grant itself activation, authority, or independent purpose.

Canonical builder constraints are defined in [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md). Detailed command and runtime architecture is defined in [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md).

## What GroX owns

| GroX owns | GroX deliberately does not own |
|---|---|
| persistent personal assistance to the Commander | authority to redefine who or what GroX serves |
| interpretation and execution of Commander intent | authority to replace or silently rewrite Commander intent |
| Mission and Mission Graph orchestration through GorXu | self-authorizing goals or a second command spine |
| Standing Crew selection and bounded Mission Orders | Crew self-promotion, self-authorization, or scope widening |
| native Mission Control policy and advisory support | a parallel Mission Control command hierarchy |
| capability and Tool Gateway authorization | permission to exceed host policy or Mission authority |
| evidence capture and verifier assignment | executor self-verification where independence is required |
| durable operational state, snapshots, and reconstitution | public storage of private runtime state or secrets |
| local installation/workspace contract | an installer or launcher that becomes a command authority |
| native cognition lifecycle direction: runtime, local models, training/evaluation lineage, governed promotion | a model that replaces GorXu as Pilot or becomes an intermediate command layer |
| evidence-backed evaluation and improvement proposals | automatic self-activation of proposed changes or trained descendants |

## Current state

GroX has completed the A1-A7 Apex qualification path and Post-Apex Operational Evolution Program 001. `v0.8.0` is the current published release baseline. Canonical source has continued beyond that immutable release through protected `main`, including Mission Outcome Truthfulness, bounded Selective Deep-Craft Crew Cognition, the first qualified live locally trained neural Crew cognition provider, and the first Native Cognition Independence installation/runtime foundations.

| Surface | Current state |
|---|---|
| Current released baseline | [`v0.8.0`](https://github.com/vessaxor-spec/GroX/releases/tag/v0.8.0), Post-Apex Operational Evolution |
| First Apex-qualified release | `v0.7.0` |
| Operating standard | **APEX QUALIFIED** |
| Prime function | **Persistent AI personal assistant to the Commander**; evolution is subordinate to improving that service |
| Command spine | Commander → Pilot GorXu → Divisions → Standing Crew |
| Operational orchestrator | **Pilot GorXu only** |
| Standing company | **82 Crew** across nine Divisions |
| Canonical source | protected `main`; source may advance beyond the release through the governed PR/CI path |
| CI boundary | Python 3.11-3.14 regressions plus wheel-bootstrap portability; five required gates |
| Completed evolution program | [`Post-Apex Operational Evolution Program 001`](docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md) |
| Post-release source hardening | Mission Outcome Truthfulness: scan-only execution is no longer represented as Commander-objective delivery; mutation/rollback state is reported conservatively |
| Post-release Crew evolution | Selective deep craft + bounded Crew memory + provider-neutral Inspect cognition seam + **one qualified live locally trained neural action-selection provider** |
| Strategic program | **Native Cognition Independence Program 001 — implementation in progress** |
| NCI installed/offline baseline | **NCI-1, NCI-2, and NCI-3 QUALIFIED**: commissioned installed Vessel, separated runtime/state/work roles, packaged runtime/model assets, qualified local seed cognition, direct offline GorXu conversation, governed Crew delegation, and fail-closed reconstitution under the bounded NCI-3 profile |
| Live Environment Awareness | **IN PROGRESS — five bounded exits QUALIFIED**: local runtime (#119/#120), governed Tool Gateway (#122/#123), bound hosted/session cognition awareness (#125/#126), governed bound-remote origin transport freshness (#128/#129), and exact bound-remote endpoint-surface freshness (#136/#137). Parent #115 remains open; credential validity, authenticated provider/service readiness, model availability/fitness, unbound discovery, broader external-connection/application awareness, and adaptive routing remain unqualified. |
| Native cognition target | Minimum useful offline personal-assistant + Crew-orchestration cognition owned by GroX; vendor models optional capability multipliers rather than required pilots |
| Apex posture | **No A8 is defined or implied.** Native cognition work must preserve the existing Apex regression boundary. |
| Canonical current status | [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md) |

The live Vessel includes Commander Seat interfaces, durable Missions and Mission Graphs, 82 Standing Crew, attributable organizational memory, capability-gated execution, independent verification, crash-safe same-Mission recovery, bounded replanning, Tool Gateway v2, isolated workspace execution, exact-origin network access, offline browser evidence capture, pre-registered stdio MCP adapters, evaluation that cannot self-activate, read-only Vessel health, tiered reconstitution planning, integrity-checked private state snapshots, truthful single-Mission outcome classification, Inspect-only selective deep craft with explicit attribution evidence, a controlled provider-neutral Crew cognition seam, one locally trained neural policy qualified through that seam, installed-workspace commissioning primitives, a separated runtime/state/work layout beneath Pilot GorXu, and packaged canonical runtime assets that allow the same GorXu-led 82-Crew Vessel to start from a commissioned non-editable installation outside a checkout.

<details>
<summary><strong>Current qualification and evidence snapshot</strong></summary>

### Apex qualification

| Stage | Status |
|---|---|
| A1 Cognitive Pilot | SESSION-QUALIFIED |
| A2 Mission Graph Orchestration | QUALIFIED |
| A3 Living Company Intelligence | QUALIFIED |
| A4 Executive Exception Loop and Durable Operations | QUALIFIED |
| A5 Governed Capability Expansion | QUALIFIED |
| A6 Orchestration Intelligence and Self-Improvement | QUALIFIED |
| A7 Apex Qualification Gauntlet | QUALIFIED |
| GorXu operating standard | **APEX QUALIFIED** |

Apex is an evidence-backed regression boundary, not additional authority and not inherited permission for future changes.

### Post-Apex and NCI control evidence

Current protected evolution has added continuous proof around high-consequence controls:

- **18/18** current critical-invariant mutations killed; the original Stage 1 qualification remains historically **12/12**, with six later Live Environment Awareness authority/evidence mutations extending the current matrix;
- **7/7** Stage 2 Vessel-health mutations killed;
- **9/9** Stage 3 reconstitution mutations killed;
- **4/4** A6 operational-drift detector mutations killed;
- **6/6** source-provenance detector mutations killed;
- native `grox health` remains read-only and isolated from Repair authority;
- `grox reconstitution-plan` selects FAST, TARGETED, or FULL recovery scope without duplicating health truth or widening authority;
- Mission Outcome Truthfulness is regression-covered for scan-only Execute, supported explicit Repair, unresolved mutation, and completed rollback;
- all **82** canonical craft cards fit their complete mandatory Purpose / Safety Boundaries / GroX Operational Binding context within the default Inspect craft budget;
- issue #76 / PR #79 qualified `local-neural-session-crew-v1` / `tiny-mlp-policy-5x8x3-v1`, a **75-parameter locally trained neural action-selection policy**, through the bounded Inspect Crew cognition seam;
- NCI-1A proved a non-editable installed wheel can commission a dedicated workspace outside a checkout while unbound operational commands continue to fail closed;
- NCI-1B proved a separated Pilot can load all 82 Crew from runtime assets, place private state outside Commander work, constrain Tool Gateway to Commander work, and reject path escape into state/runtime assets;
- NCI-1B exact-head CI `32356241254` / run **270** passed all five jobs; Python 3.12 recorded **277 pytest passed, 2 skipped, 440 subtests** and **279 unittest tests OK, 2 skipped**, with all mutation suites and integrated Post-Apex qualification green;
- NCI-1C exact-head CI `32375436084` / run **275** passed all five jobs and proved a non-editable installed wheel can validate packaged canonical runtime assets, start the same Pilot GorXu with all 82 Standing Crew outside a checkout, complete bounded Crew work with independent verification, reconstitute the same private state, and fail closed on deliberate packaged-asset corruption;
- NCI-1C Python 3.12 recorded **285 pytest passed, 2 skipped, 440 subtests** and **287 unittest tests OK, 2 skipped**; its canonical merge tree `b4a4bf8f389309e79341ad8df9b6e1f5f6801e35` exactly matches the CI-tested synthetic merge tree;
- integrated evidence explicitly retained `gorxu_remains_sole_orchestrator: true`.

Historical red runs remain evidence rather than being erased to create a clean narrative. Exact milestones, run IDs, and qualification evidence are maintained in the [`Progress Tracker`](docs/stewardship/progress-tracker.md), [`Roadmap`](docs/stewardship/ROADMAP.md), and Ship's Log.

</details>

## Native cognition direction

The strategic north star is:

> **GroX is a neural organism that becomes progressively better at operating inside GroX.**

That evolution is subordinate to the Prime Function: **GroX evolves so that it can serve the Commander better.** It does not assist the Commander merely to gather experience for its own evolution, and it cannot acquire an objective independent of Commander intent.

This does not mean one neural network becomes the Vessel. The evolving organism includes GorXu orchestration, Standing Crew craft, bounded memory, Mission experience, evidence, model checkpoints, training provenance, evaluation history, accepted and rejected descendants, and the authority/recovery infrastructure that constrains them.

The command relationship does **not** change when native cognition is added:

```text
Commander
    ↓
Pilot GorXu
    ↓
Divisions
    ↓
Standing Crew
```

Native cognition belongs to the supporting resource plane:

```text
Pilot GorXu selects and governs
    ├── native/local cognition
    ├── optional external intelligence
    ├── Standing Crew cognition when authorized
    ├── tools and Tool Gateway
    ├── memory and evidence
    └── training/evaluation/evolution systems
```

The native engine strengthens GorXu's ability to interpret, plan, synthesize, and orchestrate; it does **not** sit between GorXu and Crew as command authority. GroX intends to own the cognition lifecycle above the inference backend: model registry and lineage, local inference contract, cognition placement, context construction, learning corpus, training/evaluation, model promotion, persistence, and recovery. Low-level inference kernels or initial language-capable seed weights may come from permissively licensed open components when that is the smallest effective path; adoption does not transfer command authority to those components.

External models remain valuable. GorXu may eventually decide to consult them for difficult work, cross-checking, research, coding, or candidate teaching material. Their output remains advisory evidence. Material may enter GroX training only when applicable rights/terms permit it, provenance is retained, and required verification admits it.

The canonical sequence is defined in the [`Roadmap`](docs/stewardship/ROADMAP.md) under **Native Cognition Independence Program 001**.

## Local installation direction

The target normal-user experience is an installed GroX CLI on supported macOS and Linux hosts, with repository cloning retained as the developer path.

The intended future experience is:

```text
install GroX
    ↓
run `grox`
    ↓
commission local Vessel
    ↓
workspace [default: ~/GroX]
    ↓
Pilot GorXu online
```

Current protected source has established the qualified installed/local cognition foundations:

- **NCI-1A:** `grox init` / `grox workspace`, `~/GroX` defaulting, Linux/macOS user configuration, workspace markers/binding, collision and rebinding refusal, idempotent commissioning, and installed-wheel commissioning outside a checkout.
- **NCI-1B:** explicit runtime/assets, private-state, and Commander-work roles with non-overlap, legacy compatibility, Crew/policy loading from runtime assets, private mutable state outside Commander work, and Tool Gateway confinement to Commander work.
- **NCI-1C:** the non-editable wheel packages and validates the canonical runtime assets, starts the same Pilot GorXu from a commissioned workspace without a checkout or manual `GROX_VESSEL_ROOT`, loads all 82 Standing Crew, persists private state separately, and fails closed on missing/corrupt packaged assets.
- **NCI-1D:** the integrity-bound native model registry, lineage/readiness/resource contract, provider-neutral local inference interface, explicit load/invoke/unload semantics, and fail-closed non-activating reconstitution are qualified; the installed-wheel packaged-model proof closes the overall NCI-1 exit.
- **NCI-2:** the exact Qwen3-4B Q4_K_M seed through pinned `llama.cpp` b10218 is qualified on the recorded installed Linux x86_64 CPU-first path without a vendor credential or external network route.
- **NCI-3:** the bounded offline GorXu conversational + governed Crew-orchestration profile is qualified on that exact NCI-2 seed/runtime path, including direct `grox ask`, high-risk Inspect delegation, synthesis, independent verification, and fail-closed reconstitution.

These qualifications do not imply the broader NCI-8 offline Vessel profile, a public one-command installer, desktop launcher, arbitrary local model/runtime support, or a GroX-pretrained general-purpose foundation model.

The public one-command installer, desktop launcher, and any GroX-pretrained general-purpose foundation-model claim remain **unqualified**. Bounded offline GorXu cognition is now qualified through NCI-3, but that evidence does not imply those broader product or distribution claims.

See [`LOCAL_INSTALLATION_AND_COMMISSIONING_CONTRACT.md`](docs/stewardship/LOCAL_INSTALLATION_AND_COMMISSIONING_CONTRACT.md).

### Live Environment Awareness

Current protected source has four qualified bounded awareness surfaces:

1. defined local cognition/runtime inventory and policy-constrained selection (#119/#120);
2. passive governed Tool Gateway workspace/network/browser/MCP capability awareness (#122/#123);
3. privacy-safe awareness of hosted/session cognition resources already bound to GorXu or Crew seats (#125/#126);
4. explicitly authorized current-session **origin transport freshness** for an already-bound remote cognition resource through the existing Tool Gateway (#128/#129).

The state model remains strict: **Discovered ≠ Authorized ≠ Ready ≠ Qualified/Fit ≠ Selected ≠ Observed**. A successful transport probe proves only exact-origin transport reachability at observation time. It does not validate credentials, provider/model availability or fitness, authorization, provider/service readiness, switching/fallback, or adaptive routing. Parent issue #115 remains open.

## Qualified limits

The Apex baseline does not claim unrestricted power. Current deliberate limits include:

- GroX's Prime Function is explicit doctrine, but the full OpenClaw/Hermes-like breadth of personal-assistant capabilities is not claimed merely by documenting the objective; each tool/system surface remains evidence- and authority-bounded;
- GorXu may use project/session-hosted cognition, and NCI-3 separately qualifies a bounded installed/offline GorXu profile on the exact NCI-2 local seed/runtime path; neither path widens deterministic authority;
- one live locally trained neural action-selection provider is qualified for bounded **Inspect Crew cognition only**; it is not a general-purpose language model and does not extend model cognition to Repair, Verify, or Execute;
- **NCI-1, NCI-2, and NCI-3 are qualified** under their exact evidence boundaries; NCI-4 and the broader NCI-8 offline Vessel qualification are not implied;
- NCI-2 uses the exact qualified Qwen3-4B Q4_K_M open-weight seed through pinned `llama.cpp`; GroX does not claim a GroX-pretrained general-purpose foundation model;
- the public one-command macOS/Linux installer and desktop launchers are not yet qualified;
- unrestricted interactive desktop actuation is outside the qualified boundary;
- arbitrary or networked third-party MCP processes are outside the qualified boundary;
- runtime image pulls or builds are not implicit Crew authority;
- generic compensation for arbitrary external systems is not claimed;
- external-agent/model interoperability remains optional and grants no inherited GroX authority;
- autonomous memory consolidation remains future evolution;
- controlled context compression is not automatically active in Pilot runtime;
- no trained model may self-promote merely because a benchmark improved.

A missing provider, unavailable isolation backend, stale evidence, ambiguous recovery condition, failed native-model health check, or missing runtime asset must cause safe degradation or broader recovery requirements, never authority expansion.

## Quick start

### Current source/developer operation

The currently complete developer path uses a GroX source checkout.

Prerequisites:

- Python **3.11+**
- Git

```bash
git clone https://github.com/vessaxor-spec/GroX.git
cd GroX
python -m pip install -e .
```

For local testing:

```bash
python -m pip install -e '.[test]'
pytest
```

### Current commissioning foundation

Protected source also provides the installed-workspace commissioning foundation:

```bash
grox init
grox workspace
```

The default dedicated workspace is `~/GroX`; an alternate path may be supplied through the commissioning interface. With NCI-1C, a non-editable installed wheel can start the same Pilot GorXu from a commissioned workspace using validated packaged runtime assets. This does not yet supply native general-purpose local cognition or complete the NCI-1 exit.

### Inspect the Vessel

From a valid operational Vessel/source binding or commissioned installed Vessel:

```bash
grox status
grox roster
grox health
grox reconstitution-plan
```

### Run a bounded Mission

```bash
grox mission "Inspect the Vessel and report readiness" --mode inspect
```

For a generic Execute directive without a supported governed operation, GroX may legitimately return `status: scan_only` with `execution_status: completed`. That means the bounded context scan completed, **not** that the wider Commander objective was delivered. Use an explicit supported operation or the explicit Repair path when mutation is actually authorized; do not infer mutation authority from words such as “fix” or “write.”

Selective deep craft is automatically bounded and attributable on Inspect Orders in current protected source. The provider-neutral Crew cognition seam has one qualified local neural provider, but that provider is a narrow action-selection policy rather than the future general native cognition runtime.

### Enter the Commander bridge

```bash
grox bridge
```

The Commander bridge is another interface into the same Pilot GorXu command plane; it is not a second orchestrator.

Explicit Vessel-root binding remains the fail-closed developer/recovery path. Normal installed operation may now use the commissioned workspace plus NCI-1C validated packaged runtime assets without a source checkout or manual `GROX_VESSEL_ROOT`, while preserving the same GorXu command plane and fail-closed behavior.

## Persistence and recovery

GroX separates continuity into three persistence planes:

1. **Cognitive continuity:** the currently qualified project/session path can reconstitute GorXu and active cognitive context; the Native Cognition Independence roadmap adds a future local cognition/model-lineage path without replacing the authority spine.
2. **Vessel source:** this repository is the durable source body.
3. **Operational state:** private SQLite state and `.groxstate` archives preserve Missions, Orders, Evidence, Crew state, memory, performance, graphs, evaluation, exceptions, and recovery state outside public Git.

NCI-1B separately defines three **filesystem roles** for installed/runtime evolution:

- runtime/assets;
- private state;
- Commander work.

Those are storage/security boundaries, not a second hierarchy. In separated mode Tool Gateway works only inside Commander work, while runtime assets and private state remain outside its normal filesystem authority. NCI-1C binds validated packaged runtime assets to those same roles for normal commissioned installed startup.

A sandbox, runner, host, model artifact, or external model provider is replaceable compute/capability, not the permanent Vessel.

### Reconstitution rule

A fresh or uncertain host may resume GroX only after required runtime/source materialization, private-state verification or restoration when needed, workspace/layout validation, integrity gates, and GorXu reconstitution. Recovery scope increases when evidence is missing or unsafe:

- **FAST** requires positive mandatory health evidence and clean source state.
- **TARGETED** is limited to bounded noncritical WARN/UNKNOWN conditions after all FULL triggers are excluded.
- **FULL** is required for fresh hosts, source changes, critical failures, non-PASS recovery readiness, unsafe in-flight state, dirty source, persistence warnings/failures, or missing/non-PASS mandatory evidence.

Failure or ambiguity never grants additional authority.

See [`docs/architecture/PERSISTENCE_ARCHITECTURE.md`](docs/architecture/PERSISTENCE_ARCHITECTURE.md) and the current [`Roadmap`](docs/stewardship/ROADMAP.md).

## Repository map

```text
.
├── README.md                     # public entry point
├── AI_INSTRUCTIONS.md            # repository authority and builder constraints
├── .github/workflows/ci.yml      # protected five-gate CI
├── assets/                       # public visual assets
├── configs/                      # Vessel configuration and source-checkout bindings/assets
├── docker/                       # governed container support
├── docs/                         # architecture, specification, stewardship, history
├── policy/                       # GroX-native policy and authority controls
├── scripts/                      # validation, experiments, mutation and maintenance tools
├── src/                          # GroX runtime implementation
├── tests/                        # unit, integration, contract, experiment and mutation evidence
└── pyproject.toml                # package and CLI definition
```

### Documentation map

| If you want to understand... | Start here |
|---|---|
| repository authority and builder constraints | [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) |
| command and runtime architecture | [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) |
| persistence and reconstitution | [`docs/architecture/PERSISTENCE_ARCHITECTURE.md`](docs/architecture/PERSISTENCE_ARCHITECTURE.md) |
| durable operating principles | [`docs/specification/PRINCIPLES.md`](docs/specification/PRINCIPLES.md) |
| bounded Crew authority and Mission outcome semantics | [`docs/specification/MISSION_ORDER.md`](docs/specification/MISSION_ORDER.md) |
| Living Company memory, routing, selective craft, and controlled Crew cognition | [`docs/specification/LIVING_COMPANY_INTELLIGENCE.md`](docs/specification/LIVING_COMPANY_INTELLIGENCE.md) |
| Mission Graph execution | [`docs/specification/MISSION_GRAPH.md`](docs/specification/MISSION_GRAPH.md) |
| local installation and first-run contract | [`docs/stewardship/LOCAL_INSTALLATION_AND_COMMISSIONING_CONTRACT.md`](docs/stewardship/LOCAL_INSTALLATION_AND_COMMISSIONING_CONTRACT.md) |
| current Vessel status | [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md) |
| current strategic direction | [`docs/stewardship/ROADMAP.md`](docs/stewardship/ROADMAP.md) |
| Apex regression boundary | [`docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`](docs/stewardship/APEX_ORCHESTRATOR_PLAN.md) |
| completed post-Apex evolution program | [`docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md`](docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md) |
| current Standing Crew | [`docs/stewardship/CREW_ROSTER.md`](docs/stewardship/CREW_ROSTER.md) |
| historical milestones | [`docs/history/ships-log/`](docs/history/ships-log/) |

## Governance and evidence

GroX distinguishes authority, implementation, evidence, verification, recovery, training, model promotion, installation, and release decisions rather than treating code or model existence as proof of operational qualification.

### Authority hierarchy

When repository sources disagree, use the hierarchy defined in [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md):

1. Commander directives;
2. `AI_INSTRUCTIONS.md`;
3. canonical architecture and specification documents;
4. stewardship documents;
5. current code and tests;
6. builder judgment.

Higher authority wins when instructions conflict. Historical records remain historical rather than being rewritten to appear current.

### Evidence discipline

- implementation is not qualification;
- successful bounded execution is not automatically Commander-objective delivery;
- a green CI run proves the checks it actually executed, not a broader claim;
- controlled experiments remain distinct from integrated operational evidence;
- controlled fake-provider CI proves the Crew cognition seam and its boundaries, not live model-backed Crew operation;
- issue #76 / PR #79 separately proves one exact live locally trained neural policy through that seam and must not be generalized into a language-model or unrestricted-autonomy claim;
- NCI-1A/NCI-1B/NCI-1C prove the installed commissioning/layout/packaged-runtime foundation including standalone installed GorXu startup; they do not prove a public installer, native general-purpose local cognition, or offline NCI qualification;
- training completion or a higher score is not model promotion;
- external model output is not automatically training truth;
- red evidence and rejected descendants are preserved when they reveal a real weakness or ambiguity;
- consequential changes must preserve Commander sovereignty, GroX's personal-assistant Prime Function, GorXu's sole-orchestrator role, the command/infrastructure boundary, bounded Mission Orders, verifier independence, evidence integrity, recovery, and source/state compatibility;
- private SQLite state, `.groxstate` archives, secrets, and sensitive training material remain outside public Git by design.

The README is an entry point. It does not outrank current repository authority, implementation evidence, the Progress Tracker, or the Roadmap.

## Roadmap

The Apex critical path and **Post-Apex Operational Evolution Program 001** are complete and independently verified. Program 001 added evidence-backed Vessel health, tiered reconstitution, bounded context-heat policy, longitudinal A6 drift analysis, external-capability intake discipline, and privacy-safe Mission-to-source provenance, then qualified those surfaces together.

Post-release protected `main` also includes Mission Outcome Truthfulness, Selective Deep-Craft Crew Cognition, the first live local neural Crew qualification, NCI-1A workspace commissioning, NCI-1B runtime/state/work separation, and NCI-1C packaged runtime assets plus standalone installed GorXu startup. None defines a new Apex stage or release.

The current strategic program is **Native Cognition Independence Program 001**. Its purpose is to strengthen the Prime Function and GorXu's defining orchestration role: preserve and improve GroX as the Commander's personal AI assistant while moving the Vessel from externally supplied cognition toward an installed, offline-capable native cognition runtime and evolving local model family. External models remain optional capabilities and potential teachers where permitted, not required pilots.

The program sequence remains: native runtime/install foundation → built-in local seed cognition → offline GorXu personal-assistant cognition → richer neural Crew evolution → verified Mission learning corpus and model lineage → optional external teacher/tool adapters → governed descendant promotion → offline personal-assistant + Crew-orchestration Vessel qualification → connected/augmented operation.

Within NCI-1, the installation/runtime work is now explicitly staged: **NCI-1A complete → NCI-1B complete → NCI-1C complete → NCI-1D native model registry + local inference runtime contract next**. NCI-1 overall remains unqualified until the remaining model registry/inference/readiness/reconstitution contract passes its own gate.

There is no predeclared A8. Every Native Cognition Independence stage must preserve the existing Apex and Post-Apex regression boundaries, the Prime Function, the canonical `Commander → Pilot GorXu → Divisions → Standing Crew` hierarchy, and Commander authority, and must earn its own evidence before activation.

`v0.8.0` packages the completed Post-Apex Program 001 baseline and remains the current published release. Canonical source may advance beyond it through protected `main`; future release decisions remain Commander-controlled.

See the canonical [`Roadmap`](docs/stewardship/ROADMAP.md) for current sequencing and evidence boundaries.

---

<div align="center">

**Personal assistance. Pilot GorXu at the helm. Standing Crew under bounded command. Native cognition that strengthens the Vessel without replacing its command spine.**

[Back to top](#readme-top)

</div>
