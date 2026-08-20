# Local Installation and Commissioning Contract

**Status:** AUTHORIZED NCI REQUIREMENT — NOT YET IMPLEMENTED OR QUALIFIED  
**Issue:** #88  
**Program:** Native Cognition Independence Program 001

## Purpose

GroX is intended to be a real local AI personal-assistant and Crew-orchestration application, not a repository that ordinary users must understand or operate from source.

Repository cloning remains a supported developer workflow. It is not the target normal-user installation path.

The public installation objective is:

> A user on a supported macOS or Linux host should be able to install GroX from one documented README command, invoke `grox`, commission a local Vessel, converse with Pilot GorXu, and later reconstitute the same Vessel without requiring a paid AI subscription or a source checkout.

This contract defines the installation and first-run boundary that NCI implementation must satisfy. It does not claim that the complete installer, native language model, desktop launcher, or offline qualification already exists.

## Preserved command architecture

Installation does not alter GroX command authority:

> **Commander → Pilot GorXu → Divisions → Standing Crew**

Pilot GorXu remains second-in-command, principal personal-assistant interface, and sole operational orchestrator. The CLI, desktop launcher, installer, workspace manager, model runtime, and external providers are entry points or capabilities, not command layers.

Every supported entry path must reach the same Vessel and the same GorXu authority plane.

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

The eventual README should place this user path before source/developer installation.

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

Non-interactive commissioning must eventually provide an explicit path flag or configuration mechanism rather than guessing.

## Installed runtime and Vessel workspace are separate

GroX must distinguish at least these concepts:

1. **Installed application/runtime** — replaceable/versioned GroX executable, Python/runtime assets, schemas, built-in Crew definitions, and other immutable application resources.
2. **Host configuration** — the minimal platform-appropriate configuration required to locate the active commissioned Vessel workspace and installation metadata.
3. **Vessel workspace** — mutable Commander/Vessel state that must survive normal application upgrades.

The target workspace may contain, as implementation evolves:

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
- source/runtime version changes must remain subject to compatibility, health, and reconstitution checks.

## Host configuration target

GroX should use platform-appropriate per-user configuration locations to remember the commissioned workspace rather than requiring a global `/home/Grox` path.

Target conventions:

- Linux: XDG-style per-user configuration, such as `$XDG_CONFIG_HOME/grox/` when set or the corresponding user config default;
- macOS: a per-user Application Support/configuration location appropriate to macOS.

The exact config filename/schema belongs to NCI-1 implementation and must be versioned and recoverable. The visible default Vessel workspace remains `~/GroX` unless the Commander chooses another path.

Environment variables may remain useful for development, testing, recovery, or explicit host overrides, but ordinary installed operation should not require users to manually set `GROX_VESSEL_ROOT` merely to start GroX.

## CLI contract

The primary user entry point remains:

```text
grox
```

Normal no-argument invocation should ultimately mean: enter or start the commissioned Vessel and interact with Pilot GorXu.

If no Vessel has been commissioned, `grox` should route into safe first-run commissioning rather than constructing an empty company silently or failing only because the user is outside a Git checkout.

Target lifecycle surface, subject to implementation review:

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

## First-run commissioning responsibilities

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

This permits multiple hardware profiles while retaining one GroX command architecture.

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

A larger model does not acquire more GroX authority.

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

Developer/source installation should appear separately and remain clearly labeled as the development path.

## NCI stage integration

### NCI-1

NCI-1 must define both:

- the native cognition runtime/model contract; and
- the installed-runtime / commissioned-workspace contract.

NCI-1 should establish the boundaries needed for model registry/lineage, local inference, hardware discovery, resource ceilings, health/reconstitution, application installation, workspace binding, and persistent state placement without changing GorXu's command role.

### NCI-2

Built-in local seed cognition must be provisionable into an installed/commissioned Vessel without requiring a source checkout.

### NCI-3

Offline GorXu qualification must run from the installed local Vessel path rather than relying on a developer checkout as the product architecture.

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
Commander conversation + Crew delegation + bounded Mission
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

As of this contract's authorization:

- GroX already exposes a Python `grox` CLI entry point;
- current non-editable installed operation still requires binding to a valid GroX source/Vessel root;
- the current README source quick start remains a developer/source installation path;
- the one-command normal-user installer is not yet qualified;
- first-run commissioning is not yet implemented as described here;
- a self-contained native language model is not yet shipped;
- desktop launchers are not yet qualified;
- NCI offline personal-assistant qualification is not yet complete.

This contract converts those gaps into explicit NCI requirements without representing them as completed capability.

## Preserved Vessel state

- Commander retains ultimate authority.
- Pilot GorXu remains principal assistant interface and sole operational orchestrator.
- Divisions and Standing Crew remain under GorXu.
- models, installers, launchers, workspaces, and external providers remain capabilities/infrastructure rather than command layers.
- Standing Crew remain 82.
- package remains 0.8.0 until a separately authorized release/version change.
- published release remains v0.8.0 until a separately authorized release decision.
- no A8 exists or is implied.
