# Local Installation and Commissioning Contract

**Status:** AUTHORIZED NCI REQUIREMENT — NCI-1A / NCI-1B / NCI-1C FOUNDATION CANONICAL; FULL LOCAL INSTALLATION NOT YET QUALIFIED  
**Originating issue:** #88  
**Program:** Native Cognition Independence Program 001

## Purpose

GroX is intended to be a real local AI personal-assistant and Crew-orchestration application, not a repository that ordinary users must understand or operate from source.

Repository cloning remains a supported developer workflow. It is not the target normal-user installation path.

The public installation objective is:

> A user on a supported macOS or Linux host should be able to install GroX from one documented README command, invoke `grox`, commission a local Vessel, converse with Pilot GorXu, and later reconstitute the same Vessel without requiring a paid AI subscription or a source checkout.

This contract defines the installation and first-run boundary that NCI implementation must satisfy. NCI-1A, NCI-1B, and NCI-1C now implement and qualify workspace commissioning, separated runtime/state/work roles, packaged canonical runtime assets, and standalone installed GorXu startup. They do not yet prove the complete public installer, native general-purpose language model, desktop launcher, automatic first-run wizard, or offline qualification.

## Preserved command architecture

Installation does not alter GroX command authority:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Pilot GorXu remains second-in-command, principal personal-assistant interface, and sole operational orchestrator. The CLI, desktop launcher, installer, workspace manager, model runtime, local/native models, external providers, filesystem roots, state stores, and runtime assets are entry paths, capabilities, or infrastructure—not command layers.

Every supported entry path must reach the same Vessel and the same GorXu authority plane.

### Command is not installation layout

Installation and filesystem diagrams must never be read as organizational charts. The installed/runtime layout exists beneath the command spine:

```text
COMMAND

Commander
    ↓
Pilot GorXu
    ↓
Divisions
    ↓
Standing Crew

INFRASTRUCTURE / RESOURCES USED BY THAT COMMAND SPINE

runtime assets   private state   Commander work   native/external models
      │               │               │                    │
Crew/craft       memory/evidence   Tool Gateway       cognitive energy
policy/schemas   mutable runtime   Mission files      governed capability
```

A Crew dossier being stored in runtime assets does not place Crew above GorXu. A native model powering GorXu or a Crew tour does not become a command layer between GorXu and Crew. A desktop launcher starts the same GorXu-led Vessel; it does not create another Pilot.

This is a non-regression requirement for all installation/NCI work.

## Target normal-user flow

The normal path should converge on an experience equivalent to:

```text
install GroX
    ↓
run `grox`
    ↓
no commissioned Vessel found
    ↓
first-run commissioning
    ↓
workspace selection [default: ~/GroX]
    ↓
hardware/runtime discovery
    ↓
required local assets/model provisioning
    ↓
Standing Crew + persistent state commissioning
    ↓
optional desktop launcher
    ↓
Vessel health/readiness check
    ↓
Pilot GorXu online
    ↓
Commander>
```

The eventual README should place this user path before source/developer installation once the path actually exists and is qualified.

## Supported host target

Minimum distribution target:

| Operating system | Architecture |
|---|---|
| macOS | arm64 / Apple Silicon |
| macOS | x86_64 where practical while the platform remains supportable |
| Linux | x86_64 |
| Linux | arm64 |

A platform is not considered supported merely because Python source could theoretically run on it. User-facing support requires an installable path, commissioning, startup, persistence/reconstitution, and appropriate CI or release evidence for the claimed platform.

## Workspace default

The normal default dedicated Vessel workspace is:

```text
~/GroX
```

This resolves naturally to the current user's home directory on both macOS and Linux.

`/home/Grox` is not the cross-platform default because `/home` is Linux-specific and does not represent the current user's home on macOS or on every Unix-like host.

First run should present the default and permit an alternate Commander-selected path. Pressing Enter should accept `~/GroX`.

Example target interaction:

```text
No commissioned GroX Vessel was found.

Where should GroX establish its dedicated workspace?
[~/GroX]:

Create a desktop launcher? [Y/n]:
```

NCI-1A already provides a non-interactive `grox init` commissioning primitive and explicit workspace binding. The fully interactive no-argument first-run wizard remains future work.

## Installed runtime and Vessel workspace are separate

GroX distinguishes these concepts:

1. **Installed application/runtime assets** — replaceable/versioned GroX executable, Python/runtime assets, schemas, built-in Crew definitions, policy, and other immutable application resources.
2. **Host configuration** — minimal platform-appropriate configuration required to locate the active commissioned Vessel workspace and installation metadata.
3. **Private Vessel state** — mutable internal state such as SQLite, evidence/runtime scratch, memory, snapshots, and later model/runtime state that ordinary Commander-work filesystem authority must not expose.
4. **Commander work** — the user/Mission filesystem boundary within which Tool Gateway performs authorized ordinary work.

NCI-1B expresses the runtime/state/work separation through `VesselLayout`. Separated operation requires runtime/assets, private state, and Commander work roots not to overlap. Legacy one-root source-checkout behavior remains supported for compatibility.

A commissioned workspace may contain, as implementation evolves:

```text
~/GroX/
├── state/
├── memory/
├── models/
├── missions/
├── evidence/
├── workspace/
├── snapshots/
├── logs/
└── exports/
```

Exact internal layout remains an implementation decision and must not duplicate canonical persistence truth unnecessarily.

### Upgrade and uninstall rule

- upgrading the GroX application must not silently erase or replace the Commander's persistent Vessel workspace;
- uninstalling the executable must not silently destroy the workspace;
- destructive workspace removal requires an explicit, separately authorized user action;
- source/runtime version changes must remain subject to compatibility, health, and reconstitution checks;
- upgrade or uninstall behavior may not move command authority away from GorXu or create an alternate state authority.

## Host configuration

GroX uses platform-appropriate per-user configuration locations to remember the commissioned workspace rather than requiring a global `/home/Grox` path.

NCI-1A established the current path contract:

- Linux: XDG-style per-user configuration, honoring an absolute `$XDG_CONFIG_HOME` when set and otherwise using the platform default user configuration location;
- macOS: per-user Application Support configuration.

The binding schema is versioned and fail-closed. The visible default Vessel workspace remains `~/GroX` unless the Commander chooses another path.

Environment variables remain useful for development, testing, recovery, or explicit host overrides. NCI-1C now proves that ordinary commissioned installed operation can start GroX without manually setting `GROX_VESSEL_ROOT`; explicit root binding remains a developer/recovery path.

## CLI contract

The primary user entry point remains:

```text
grox
```

Normal no-argument invocation should ultimately mean: enter or start the commissioned Vessel and interact with Pilot GorXu.

If no Vessel has been commissioned, `grox` should route into safe first-run commissioning rather than constructing an empty company silently or failing only because the user is outside a Git checkout.

Current NCI-1A commissioning surface includes:

```text
grox init
grox workspace
```

The broader target lifecycle surface, subject to implementation review, remains:

```text
grox
grox start
grox init
grox status
grox health
grox doctor
grox workspace ...
grox model ...
grox snapshot ...
grox restore ...
grox desktop install
grox desktop remove
grox version
grox update
```

Only the smallest useful command set should be implemented at each stage. This list is a target surface, not evidence that every command exists now.

Existing Mission, Crew, health, snapshot, and Commander-bridge commands remain part of the same CLI rather than being replaced by another command system.

## Commissioning responsibilities

Commissioning should eventually perform, in a bounded and observable sequence:

1. detect whether a valid commissioned Vessel already exists;
2. choose or accept the dedicated workspace;
3. create only required directories/state;
4. record the workspace binding in host configuration;
5. detect OS, architecture, available memory, CPU, available acceleration, and relevant disk capacity;
6. select or recommend an NCI local-runtime/model profile compatible with the host;
7. provision required runtime/model assets with integrity and provenance evidence;
8. initialize or restore persistent Vessel state and Standing Crew resources;
9. optionally install the desktop launcher;
10. run Vessel health/readiness checks;
11. enter Pilot GorXu only after commissioning is safe enough for the claimed operating mode.

NCI-1A implements bounded workspace selection/defaulting, workspace ownership markers, platform-aware host configuration, atomic binding writes, idempotent same-workspace commissioning, collision/refusal rules, and marked partial-commissioning recovery. NCI-1B separates runtime assets, private state, and Commander work. NCI-1C packages/validates the canonical runtime assets and proves the first standalone installed Pilot boot plus bounded Crew orchestration/reconstitution. Hardware/model provisioning, native model runtime/readiness, automatic first-run flow, and launcher installation remain outstanding.

Failure during commissioning must fail closed or leave a recoverable partial state. It must not widen Crew authority or silently bypass health/integrity gates.

## Native model provisioning

The command-line application itself need not contain every model artifact.

The preferred architecture is:

```text
GroX installer/runtime
        ↓
hardware discovery
        ↓
compatible local cognition profile
        ↓
verified model/runtime provisioning
        ↓
commissioned Vessel
```

This is a provisioning flow, **not a command hierarchy**. The resulting cognition remains a governed capability under Pilot GorXu.

Potential profile labels such as Compact, Standard, or Enhanced are not canonical until model selection and hardware evidence support them.

Model artifacts require:

- identity;
- version;
- digest/integrity;
- provenance/license;
- hardware/resource requirements;
- compatibility with the GroX native cognition runtime contract;
- health/readiness evidence;
- explicit qualification status.

A larger model does not acquire more GroX authority. A native model does not become the Pilot. External models remain optional governed resources that GorXu may select for relevant Missions/Crew when available and useful.

## Desktop launcher contract

The desktop launcher is convenience only.

### macOS target

Provide a user-visible launcher/application entry that starts the same installed GroX Vessel. An early implementation may open the terminal-based Commander interface. A future graphical Commander interface may replace the presentation layer without creating a second Vessel or command spine.

### Linux target

Provide a desktop entry compatible with common desktop environments that starts the same installed GroX Vessel. An early implementation may launch the terminal Commander interface.

### Launcher invariants

- one Vessel;
- one Pilot GorXu;
- same workspace binding;
- same `Commander → Pilot GorXu → Divisions → Standing Crew` command spine;
- same authority, persistence, evidence, and verification rules;
- no hidden alternative state store;
- no additional orchestration layer.

## Distribution posture

The target normal-user path should not require knowledge of:

- Git;
- editable Python installs;
- repository directory layout;
- manual virtual-environment management;
- `GROX_VESSEL_ROOT` setup;
- paid vendor API credentials.

A Python/pipx path may remain a useful alternate or developer installation path. The long-term normal-user release should move toward self-contained, platform-specific GroX packages/executables where that materially reduces friction and dependency risk.

Target artifacts should cover the supported host/architecture matrix rather than assuming one universal binary.

An eventual offline bundle may package the installer/runtime, a qualified local cognition profile, Crew/runtime assets, and required integrity metadata so a disconnected machine can be commissioned without first contacting a model vendor.

## README contract

The README must distinguish current evidence from the target experience.

Before a normal-user installer is qualified, it must not publish a fictional one-command installer as if it works.

Once qualified, the README user path should be approximately:

```text
## Install GroX

### macOS / Linux

<one official installation command>

Then:

grox
```

The first run should explain that the default workspace is `~/GroX` and that it can be changed during commissioning.

Until a normal-user installer is qualified, README must accurately distinguish the source/developer path from the now-qualified NCI-1C installed-wheel runtime foundation. It may state that a commissioned non-editable wheel can start standalone Pilot GorXu with packaged runtime assets, but must not imply that the public one-command installer, native general-purpose cognition, desktop launcher, or offline profile is already qualified.

Developer/source installation should remain clearly labeled as the development path.

## NCI implementation integration

### NCI-1A — installed workspace commissioning foundation

**Canonical foundation complete.** Current protected source provides:

- `grox init` and `grox workspace` without requiring operational Vessel-root resolution merely to commission/inspect the workspace binding;
- `~/GroX` default workspace;
- Linux/macOS per-user host configuration;
- versioned workspace marker and host binding;
- atomic binding writes;
- idempotent same-workspace commissioning;
- collision, malformed binding, path mismatch, implicit rebind, and unsupported-platform fail-closed behavior;
- marked partial-workspace recovery;
- non-editable wheel commissioning outside a checkout while unbound operational commands continue to fail closed.

NCI-1A was merged through PR #91 as canonical source `2b4e1c8f3fff8081a30dab4702738cf8b5c01480` before later NCI-1B evolution.

### NCI-1B — runtime/state/work separation

**Canonical foundation complete.** Current protected source provides:

- explicit `VesselLayout` with runtime/assets, private state, and Commander work roles;
- strict non-overlap for separated layouts;
- legacy one-root compatibility;
- Pilot GorXu loading Standing Crew/runtime policy from runtime assets;
- private SQLite/browser/workspace scratch placement outside Commander work in separated mode;
- Tool Gateway filesystem authority rooted only in Commander work;
- regression proof that all 82 Crew load and bounded Inspect work cannot path-escape into private state or runtime assets.

NCI-1B was merged through PR #93 as canonical source `55c98b13a169476cfedad89c1db2c2c36e9536fd` after exact-head CI run `32356241254` / run 270 passed all five required jobs. Its canonical tree `fa4255792801a2b45a2b1daad2ecee334a55484d` exactly matches the CI-tested synthetic merge tree.

### NCI-1C — packaged runtime assets + standalone installed GorXu

**Canonical foundation complete.** Current protected source now provides:

- canonical repository runtime `configs/` packaged directly into the non-editable wheel data area rather than duplicated into a second Crew/config source;
- startup validation for tool policy, company manifest, exactly 82 Standing Crew dossiers, exactly 82 matching craft cards, and dossier identity;
- installed-layout resolution from a commissioned workspace plus packaged runtime assets outside a checkout and without manual `GROX_VESSEL_ROOT`;
- the same canonical `PilotGorXu`, all 82 Standing Crew, separated private state, and Commander-work Tool Gateway boundary;
- bounded medium-risk Inspect Crew orchestration with independent verification and no mutation;
- same-state reconstitution from a fresh CLI process;
- fail-closed behavior under deliberate required packaged-asset removal, followed by successful recovery after restoration.

NCI-1C final head `e0c187567213fdf66cd1baaa03e3230ee1f16dd0` passed exact-head CI `32375436084` / run **275** across all five required jobs. PR #97 merged as canonical `main@0eddbc204b1e7b52158c355e9587731a7cbec08c`; canonical tree `b4a4bf8f389309e79341ad8df9b6e1f5f6801e35` exactly matches CI-tested synthetic merge `73fb8c58d2bd02271e2122b04a12c8f76bacef2d`.

### Remaining NCI-1 runtime work

The broader NCI-1 exit still includes the native model/runtime contract: model registry and lineage, local inference-provider interface, hardware/runtime discovery, deterministic resource/context ceilings, cognition placement, model health/readiness evidence, fail-closed fallback, and reconstitution. **NCI-1D — Native Model Registry + Local Inference Runtime Contract** is the next bounded slice. NCI-1 as a whole is therefore **not yet qualified** merely because NCI-1A, NCI-1B, and NCI-1C are canonical.

### NCI-2

Built-in local seed cognition must be provisionable into an installed/commissioned Vessel without requiring a source checkout.

### NCI-3

Offline GorXu qualification must run from the installed local Vessel path rather than relying on a developer checkout as the product architecture. It must preserve direct Commander↔GorXu interaction and GorXu's Crew-orchestration role.

### NCI-8

Offline Vessel qualification should include a fresh-host installation/commissioning scenario appropriate to the supported platform claim:

```text
fresh supported host
    ↓
install GroX
    ↓
run `grox`
    ↓
commission ~/GroX or selected workspace
    ↓
provision qualified native cognition
    ↓
create/verify launcher where in scope
    ↓
Pilot GorXu online
    ↓
Commander conversation + GorXu Crew delegation + bounded Mission
    ↓
evidence + independent verification
    ↓
restart/relaunch
    ↓
Vessel reconstitution
    ↓
PASS
```

For the no-paid-provider profile:

```text
OpenAI credential:    NONE
Anthropic credential: NONE
Google credential:    NONE
Paid AI subscription: NONE
```

## Accessibility objective

GroX's local distribution should make the minimum useful personal-assistant/orchestration experience available to people who cannot or do not want to pay for commercial model subscriptions.

External models, remote compute, network tools, and paid intelligence remain valuable optional capability multipliers under GorXu's orchestration. Their absence must not be the reason a user cannot begin the minimum qualified local GroX journey.

## Current claim boundary

Current protected source now establishes more than the original contract did, but the consumer installation journey is not finished:

- GroX exposes a Python `grox` CLI entry point;
- `grox init` and `grox workspace` implement real commissioning/binding foundations;
- a non-editable installed wheel has been proven able to commission a workspace outside a checkout;
- NCI-1B provides separated runtime/assets, private-state, and Commander-work roles beneath Pilot GorXu;
- a commissioned non-editable wheel now validates packaged canonical runtime assets and starts the same standalone Pilot GorXu with all 82 Standing Crew outside a checkout;
- source checkout / explicit `GROX_VESSEL_ROOT` remains supported for development and recovery rather than being required for normal commissioned installed startup;
- the current README source quick start remains the truthful developer path while the public normal-user installer remains unqualified;
- the public one-command normal-user installer is not yet qualified;
- automatic no-argument interactive first-run commissioning is not yet complete;
- a self-contained native general-purpose language model is not yet shipped;
- desktop launchers are not yet qualified;
- NCI offline personal-assistant + Crew-orchestration qualification is not yet complete.

## Preserved Vessel state

- Commander retains ultimate authority.
- Pilot GorXu remains principal assistant interface and sole operational orchestrator.
- Divisions and Standing Crew remain under GorXu.
- models, installers, launchers, runtime assets, private state, Commander workspace, tools, and external providers remain capabilities/infrastructure rather than command layers.
- native cognition is an engine/capability of the Vessel, not an intermediate command authority between GorXu and Crew.
- Standing Crew remain 82.
- package remains 0.8.0 until a separately authorized release/version change.
- published release remains v0.8.0 until a separately authorized release decision.
- no A8 exists or is implied.
