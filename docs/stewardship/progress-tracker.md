# GroX Progress Tracker

**Status date:** 2026-08-24
**Canonical release:** `v0.8.0`
**Release status:** PUBLISHED — LATEST
**Canonical source branch:** `main`
**Current verified canonical source after transport exact-origin evidence-binding repair:** `main@d7024261f9c49a8b2bb95a26e5ad0a08a6d5a34a`
**Current verified canonical tree:** `d8959016ce59dbd61cb148d974ba0c9e1d351c21`
**Current source package:** `0.8.0`
**Current released source:** `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`
**First Apex-qualified release:** `v0.7.0@71ffd60769d81b5b249dac4eca56333ff27e26d0`
**Apex qualification merge:** `419cc73950f573c3e201106f7949c6bf7829f2af`
**Current operating verdict:** **APEX QUALIFIED — OPERATIONAL AUDIT 001 CLOSED**
**Standing Crew:** **82**
**Prime function:** **Persistent AI personal assistant to the Commander; evolution is subordinate to improving that service**
**Canonical command spine:** **Commander → Pilot GorXu → Divisions → Standing Crew**
**Operational orchestrator:** **Pilot GorXu only**
**Current verified regression:** Python **3.11–3.14 + Wheel bootstrap PASS**; Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **376 passed, 2 skipped, 455 subtests**; unittest **378 OK, 2 skipped**; mutations **17/17**, **7/7**, **9/9**, **4/4**, **6/6** killed; integrated Post-Apex PASS
**Current strategic program:** **Native Cognition Independence Program 001 — IMPLEMENTATION IN PROGRESS; NCI-1 + NCI-2 + NCI-3 QUALIFIED; LIVE ENVIRONMENT AWARENESS IN PROGRESS; LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION + BOUND REMOTE TRANSPORT FRESHNESS EXITS QUALIFIED**
**Next bounded implementation:** **Continue issue #115 beyond the four qualified bounded exits using the smallest repository-native evidence-backed surface. Provider/service readiness beyond origin transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, and adaptive provider/resource routing remain unqualified; adaptive routing must not outrun those gates.**

## Live Environment Awareness — bound remote cognition transport freshness — issue #128 / PR #129

**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED.**

Qualified boundary:

- passive hosted cognition inventory remains zero-network and non-invoking;
- active refresh applies only to one remote cognition resource already bound to a current GorXu/Crew cognition seat;
- awareness requires an **already sealed** Mission Order with exact `net_fetch`, `operation=cognition_transport_probe`, exact current `resource_id`, and exact allowed origin;
- host Tool Gateway policy must independently allow the same normalized origin;
- network I/O reuses `ToolGateway.fetch_url` only; no parallel HTTP/socket authority path exists;
- no provider credential, prompt/model request, Commander content, Crew context, or secret is sent by awareness;
- only volatile observation timestamp, reachable/unreachable state, and bounded HTTP status are retained; response content is discarded;
- transport evidence expires and failure replaces prior positive current transport state; every observation is bound to the exact normalized origin probed, and any endpoint/origin rebind invalidates prior evidence even when provider/model resource identity remains unchanged;
- fresh transport reachability never sets remote `ready`, `authorized`, or `qualified_fit`, never invokes cognition, and never changes provider binding or routing.

Qualification evidence:

- final PR #129 head `ba69209e1a92b48561903d372947bcf2db7c824d`;
- exact-head GroX CI #426 / `32710787713`: PASS Wheel + Python 3.11–3.14;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **373 passed, 2 skipped, 453 subtests**; unittest **375 OK, 2 skipped**; critical mutations **16/16**; health **7/7**; reconstitution **9/9**; operational drift **4/4**; source provenance **6/6**; Post-Apex PASS;
- permanent mutation `cognition-transport-presealed-authority`: KILLED;
- CI-tested synthetic merge `807d4cb70d78ace26349a4fa6412605e89b8dfb8`, tree `9cc6ed2765cfc226e279ae498ebabd6ade675bd5`;
- canonical merge `main@922a35add9c92e7e0d7eed31dc1ff80895e28e61`, tree `9cc6ed2765cfc226e279ae498ebabd6ade675bd5`;
- synthetic-to-canonical tree equality: **PASS**;
- issue #128 closed completed; parent #115 remains **OPEN**.

Still unqualified: provider/service readiness beyond exact-origin transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, provider switching/fallback, and adaptive provider/resource routing. No release/package/NCI/Apex/A8 advancement occurred.

## Live Environment Awareness — transport exact-origin evidence-binding repair — issue #132 / PR #133

**Status: COMPLETE — QUALIFIED REPAIR — CANONICAL MERGED AND EXACT-TREE VERIFIED.**

Post-#131 recalibration found one fail-closed defect in the already-qualified fourth awareness surface: remote transport observations were keyed by cognition resource identity, while that identity does not include endpoint/origin. Rebinding the same provider/model/class to a different endpoint could therefore inherit a still-fresh observation from the prior origin.

Repair boundary:

- every positive or negative transport observation now records the exact normalized origin actually probed;
- passive inventory compares recorded origin with the resource's current bound origin before freshness/reachability can be claimed;
- missing, malformed, invalid-current, or mismatched origin evidence fails closed as `unproven`;
- same-provider/same-model endpoint rebinding immediately invalidates prior transport evidence without network I/O;
- the existing already-sealed exact `net_fetch` Mission Order, exact resource ID, exact allowed origin, and host Tool Gateway origin policy remain unchanged;
- remote provider `ready=False`; authorization, qualification/fit, selection, invocation, fallback, and routing semantics remain unchanged;
- no fifth Live Environment Awareness surface is qualified by this repair.

Qualification evidence:

- red-before-green: test-only PR #133 head `149d09f8c323cd6d51f0f8600523855d408974f6`, GroX CI #443 / `32716652029`, failed the intended endpoint-rebind assertion while Wheel remained green;
- final PR #133 head `b50605bb90660a9f3325fd356df65ab5409666e1`;
- exact-head GroX CI #448 / `32717652432`: PASS Wheel + Python 3.11–3.14;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**; pytest **376 passed, 2 skipped, 455 subtests**; unittest **378 OK, 2 skipped**; critical mutations **17/17**; health **7/7**; reconstitution **9/9**; operational drift **4/4**; source provenance **6/6**; Post-Apex PASS;
- permanent mutation `cognition-transport-origin-binding`: KILLED;
- CI-tested synthetic merge `726fc1ef6b351f7bf0371731dd18abafce8fe882`, tree `d8959016ce59dbd61cb148d974ba0c9e1d351c21`;
- canonical merge `main@d7024261f9c49a8b2bb95a26e5ad0a08a6d5a34a`, tree `d8959016ce59dbd61cb148d974ba0c9e1d351c21`;
- synthetic-to-canonical tree equality: **PASS**;
- issue #132 closed completed; parent #115 remains **OPEN**.

This repair strengthens the already-qualified bound remote transport-freshness exit only. Provider/service readiness beyond exact-origin transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, provider switching/fallback, and adaptive provider/resource routing remain unqualified. No release/package/NCI/Apex/A8 advancement occurred.

## GorXu command/infrastructure invariant — current synchronization

**Status: COMPLETE — CANONICAL DOCUMENTATION SYNCHRONIZED THROUGH PR #95; ISSUE #94 CLOSED**

The Commander identified a representation ambiguity after NCI-1B: a filesystem/runtime diagram can accidentally make Crew or native cognition look as though they sit above Pilot GorXu even when the runtime authority path is correct.

Repository/runtime verification confirmed the implementation remained correct:

- `PilotGorXu` explicitly remains **GroX's sole operational orchestrator**;
- GorXu interprets Commander directives, reconciles mode/risk, selects eligible Crew, constructs bounded Mission Orders, places Crew on duty, invokes execution, receives evidence/exceptions, selects an independent verifier when required, and synthesizes the Commander-facing result;
- Crew do not select, command, or self-authorize GorXu;
- NCI-1B changes filesystem roles beneath the Pilot but does not change the command spine;
- integrated NCI-1B CI retained `gorxu_remains_sole_orchestrator: true`.

The canonical invariant is therefore explicit:

```text
COMMAND

Commander
    ↓
Pilot GorXu
    ↓
Divisions
    ↓
Standing Crew

INFRASTRUCTURE / CAPABILITIES

native and external models
runtime assets / Crew definitions
private Vessel state
Commander workspace
Tool Gateway / tools
memory / evidence
training / evaluation
inference backends
installer / desktop launcher
```

The lower block powers and supports the command spine; it has no command rank. Storage location does not create authority. A native model is cognitive energy/engine capability under GorXu, not the Pilot or an intermediate command layer. CLI/desktop launchers enter the same GorXu-led Vessel and cannot create alternate orchestration or state authority.

Issue #94 synchronized this interpretation across README, builder instructions, principles, architecture, persistence, Crew stewardship, local-installation contract, Roadmap, Progress Tracker, and the Ship's Log. PR #95 merged as `main@1bfc23e641704f802419b10dac413fbc38666058`; issue #94 is closed. The documentation repair changed no runtime authority, Crew count, package/release, Apex status, or A8 posture.

## NCI-1 local installation/runtime foundation

**Status: COMPLETE — NCI-1A / NCI-1B / NCI-1C / NCI-1D CANONICAL; INSTALLED-WHEEL EXIT QUALIFIED; NCI-1 EXIT PASSED**

### Installation/commissioning contract — issue #88 / PR #89

- Commander authorized the normal-user direction: a real installed GroX CLI for supported macOS/Linux hosts rather than requiring ordinary users to operate from a cloned repository;
- default dedicated workspace is `~/GroX`, not `/home/Grox`, while a Commander-selected alternate path remains supported;
- installed application/runtime and mutable Vessel workspace/state are intentionally separate so upgrade/uninstall cannot silently destroy the Vessel;
- desktop launcher is a future convenience path into the same GorXu-led Vessel, not a second application authority;
- public README must not advertise a fictional one-command installer before that path exists and is qualified;
- local/no-paid-provider accessibility is an explicit design objective;
- the contract became canonical through PR #89 before runtime implementation began.

### NCI-1A — installed workspace commissioning — issue #90 / PR #91

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

Implemented:

- `grox init` and `grox workspace` can execute without first resolving an operational source/Vessel root;
- cross-platform default workspace `~/GroX`;
- Linux XDG-style and macOS Application Support per-user configuration;
- versioned workspace ownership marker and host→workspace binding;
- atomic binding writes;
- idempotent same-workspace commissioning;
- refusal of implicit workspace rebinding, ownership collision, malformed/path-mismatched binding, and unsupported platform;
- marked partial-commissioning recovery;
- lazy operational root resolution preserves the existing fail-closed Pilot startup boundary;
- a non-editable installed wheel successfully commissioned and inspected a workspace from outside the repository while unbound operational `grox status` still failed closed.

One CI run exposed an existing test seam that patched `cli.ROOT`; compatibility was restored as a null override without reintroducing eager source-root resolution. Final exact-head CI run **267 / `32349808199`** passed all five required jobs on head `4c0ee4ff3195f75e32636ad38350edb1a99757ae`.

PR #91 merged as `main@2b4e1c8f3fff8081a30dab4702738cf8b5c01480`, canonical tree `e25f239f73e8325ff956962358779f919524e27a`; issue #90 closed completed.

### NCI-1B — runtime/assets, private state, Commander work separation — issue #92 / PR #93

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

Implemented:

- immutable `VesselLayout` contract with runtime/assets, private state, and Commander work roles;
- strict non-overlap requirement for separated layouts;
- exact legacy one-root compatibility including historical `configs/state/grox.sqlite3` placement;
- `PilotGorXu(vessel_root)` remains compatible while `PilotGorXu(VesselLayout)` enables separated operation;
- Standing Crew and tool policy load from runtime/assets;
- SQLite, browser evidence, and isolated-workspace scratch route to private state in separated mode;
- Tool Gateway ordinary filesystem authority is rooted only in Commander work;
- regression proves separated Pilot loads all **82** Crew, completes bounded Inspect work against Commander work, leaves runtime assets unchanged, and rejects traversal into private state/runtime assets.

First CI run **269 / `32356141620`** failed only because a new assertion expected the phrase `must be identical` while the implementation correctly emitted `requires ... to be identical`; production code did not change for that correction.

Authoritative final exact-head:

- head `726b29e86e41b56d1e527960960f464a13ede6de`;
- CI run **270 / `32356241254`**: PASS all five required jobs;
- Wheel bootstrap portability PASS;
- Python 3.11, 3.12, 3.13, 3.14 PASS;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **277 passed, 2 skipped, 440 subtests**;
- unittest **279 OK, 2 skipped**;
- mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed;
- integrated Post-Apex qualification PASS and retained `gorxu_remains_sole_orchestrator: true`.

PR #93 merged as canonical `main@55c98b13a169476cfedad89c1db2c2c36e9536fd`. Canonical tree `fa4255792801a2b45a2b1daad2ecee334a55484d` exactly matches the CI-tested synthetic merge tree; issue #92 closed completed.

### NCI-1C — packaged runtime assets + standalone installed GorXu — issue #96 / PR #97

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

Implemented:

- the non-editable wheel packages the existing canonical runtime `configs/` rather than maintaining a duplicate Crew/config source;
- packaged policy, company manifest, exactly 82 Standing Crew dossiers, exactly 82 matching craft cards, and dossier identity validate before installed Pilot startup;
- source checkout / explicit `GROX_VESSEL_ROOT` remains the developer/recovery path;
- normal installed operation resolves a commissioned workspace plus validated packaged assets into the separated layout and starts the same canonical `PilotGorXu`;
- private SQLite remains in private state while Tool Gateway ordinary filesystem authority remains in Commander work;
- the installed Vessel completed a medium-risk Inspect through `code-reviewer` with PASS from a different independent verifier and no mutation;
- a fresh CLI process reopened the same Mission/private state;
- deliberate packaged-policy removal failed startup closed and recovered after restoration.

Qualification evidence:

- preserved red CI `32375299755` / run **274** proved the substantive installed path and exposed only an overly narrow corruption-canary diagnostic assertion; the runtime already failed closed;
- final head `e0c187567213fdf66cd1baaa03e3230ee1f16dd0`;
- exact-head CI `32375436084` / run **275** PASS all five required jobs;
- Python 3.12 Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**;
- pytest **285 passed, 2 skipped, 440 subtests**;
- unittest **287 OK, 2 skipped**;
- mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed;
- integrated Post-Apex qualification PASS with `gorxu_remains_sole_orchestrator: true`;
- PR #97 merged as canonical `main@0eddbc204b1e7b52158c355e9587731a7cbec08c`;
- canonical tree `b4a4bf8f389309e79341ad8df9b6e1f5f6801e35` exactly matches CI synthetic merge `73fb8c58d2bd02271e2122b04a12c8f76bacef2d`.

### NCI-1D — native model registry + local inference runtime — issue #99 / PR #100

**Status: COMPLETE — CANONICAL MERGED; EXACT-HEAD QUALIFIED**

Implemented:

- integrity-bound local model manifest/artifact contract;
- deterministic model registry and lineage validation;
- host hardware/runtime profile and deterministic resource readiness;
- provider-neutral local inference backend contract;
- explicit model load/invoke/unload semantics;
- non-activating reconstitution;
- first registered model: existing qualified `tiny-mlp-policy-5x8x3-v1`;
- dependency-free tiny backend loading the exact previously qualified trained weights and verifying both outer artifact integrity and internal trained-weight identity;
- adapter back into the existing GorXu-owned bounded Inspect Crew cognition seam;
- fail-closed unit/integration coverage and package model registry/artifact alongside existing runtime assets.

Preserved red evidence:

- rejected candidate head `1833310769d443ef18f0fb8fce6262e92b5ab712`;
- CI run **280 / `32392662853`** exposed Python 3.11 trained-weight replay drift;
- the digest gate contained the mismatch and no mismatched model activated;
- the final design packages the exact previously qualified trained weights rather than weakening identity assertions.

Final implementation qualification:

- corrected head `2d68b63222cc69883d7c4252cbeeaaa9b6e5fb46`;
- CI run **281 / `32393064902`**: PASS all five canonical jobs;
- PR #100 merged as `8dde1a1714c38850c681623f1aba9238d6ec8b20`;
- issue #99 closed completed.

### NCI-1 installed packaged-model exit proof — issue #101 / PR #102

**Status: COMPLETE — EXACT-TREE QUALIFIED; NCI-1 EXIT PASSED**

Post-merge stewardship inspection found one legitimate remaining NCI-1 exit gap after NCI-1D: the standalone installed-wheel path and the native model-runtime path had not directly met in one permanent proof outside a checkout.

Issue #101 bounded that missing evidence only. PR #102 added one permanent Wheel-bootstrap qualification check and changed no runtime, model, Crew, authority, package, or release behavior.

Exact-head qualification:

- head `689f1e1f77f49d9ea6eb5fb5fda49c54da3e6d6a`;
- CI run **283 / `32406301653`**: PASS all five canonical jobs;
- installed packaged-model runtime outside checkout: **PASS**;
- Python 3.11–3.14: **PASS**;
- Python 3.12 pytest **294 passed, 2 skipped, 440 subtests**;
- Python 3.12 unittest **296 OK, 2 skipped**;
- mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed;
- integrated Post-Apex: **PASS**;
- `gorxu_remains_sole_orchestrator: true`.

The wheel proof permanently demonstrates that an installed GroX runtime can resolve `packaged_asset_root()`, discover the packaged registry/artifact, report the registered model available but inactive, explicitly load it for Crew placement, invoke it through the GroX-owned runtime contract, report no authority change, and reconstitute with active state cleared and auto-activation still disabled.

Canonical merge/source-equivalence evidence:

- PR #102 merged as `main@41fa4944d1b3e3011561a346b066df54be176a78`;
- canonical tree `734e5b1762271045f0e4ac91c3f66334bdc13361`;
- CI-tested synthetic merge `34dbcb11831a4c5eccbfc5fb3211720ba94f4510`;
- CI-tested synthetic merge tree `734e5b1762271045f0e4ac91c3f66334bdc13361`;
- actual and CI-tested trees are identical.

**NCI-1 EXIT: QUALIFIED.** NCI-1A through NCI-1D plus the installed-wheel model-runtime proof establish the GroX-owned local runtime/install/model-control foundation. This qualification did not by itself establish NCI-2 seed cognition, a general-purpose local language model, offline GorXu cognition, a public installer, desktop launcher, new release, or A8.

## NCI-2 built-in local seed cognition — issue #109 / PR #110

**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED**

NCI-2 closes the installed local seed-cognition exit without widening GroX authority:

- exact seed: `Qwen3-4B-Q4_K_M.gguf`, 2,497,280,256 bytes, SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`, Apache-2.0 provenance at pinned revision `a9a60d009fa7ff9606305047c2bf77ac25dbec49`;
- exact runtime: llama.cpp b10218 / `de699957b`, release-asset SHA-256 `78ec7a1964710918030e85c132a0995b10b07e4f43001bdf54fe0fd48d1eb85b`;
- CPU-first qualification floor: Linux x86_64, at least 8 GiB RAM and 8 GiB free working disk, no accelerator required, maximum four inference threads;
- non-editable wheel installed outside the checkout into a fresh environment and fresh commissioned Vessel;
- exact model admitted through `PersistentModelStore`, AVAILABLE/inactive before explicit GorXu load;
- inference and Mission ran with loopback only, no non-loopback interface/default route, and vendor credential variables removed;
- raw 4B CPU inference passed the unchanged 180-second gate;
- real local `MissionInterpretation` produced cognitive-plan evidence and influenced the ordinary deterministic Crew route without becoming routing authority;
- high-risk Inspect completed with no mutation and independent verification by a different Crew member;
- no cognition degradation/fallback occurred on the qualifying Mission;
- reconstitution returned zero active models with no auto-activation or authority change.

Qualification evidence:

- final PR head `2cbf6ffb2cc61825adf2d284c332818dadc76425`;
- GroX CI #339 / `32623385747`: PASS all five canonical jobs; Python 3.12 pytest **320 passed, 2 skipped, 449 subtests**, unittest **322 OK, 2 skipped**, Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, and mutations **12/12, 7/7, 9/9, 4/4, 6/6** killed;
- live Qwen qualification #42 / `32623385749`: PASS;
- PR #110 merged as `main@720a916b1500b3b5629724e3763d812ff16da948`;
- canonical tree `2c8e85bc5c0c89a619b2fd61bcdaec600b268d46` exactly matches the CI-tested synthetic merge tree;
- issue #109 closed completed.

**NCI-2 EXIT: QUALIFIED.** The Roadmap exit is satisfied: a fresh installed GroX can perform a bounded personal-assistant + orchestration cognitive Mission locally without a vendor credential or external network call. NCI-2 alone did not qualify NCI-3's broader offline conversational GorXu profile; NCI-3 is now separately qualified through issue #113 / PR #114. NCI-2 still does not imply a public installer/desktop launcher, a new release, model self-activation, NCI-4, or A8.

## NCI-3 offline GorXu conversational cognition — issue #113 / PR #114

**Status: COMPLETE — QUALIFIED — CANONICAL MERGED AND EXACT-TREE VERIFIED**

NCI-3 closes the bounded offline conversational GorXu exit while preserving the existing deterministic authority plane:

- final PR head `900d6bbb7f2683844a2182095cce67f374ae4592`;
- GroX CI #353 / `32642076863`: PASS all five canonical jobs; Python 3.12 pytest **333 passed, 2 skipped, 449 subtests**, unittest **335 OK, 2 skipped**, Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, mutations **12/12, 7/7, 9/9, 4/4, 6/6** killed, integrated Post-Apex PASS;
- NCI-3 Offline GorXu Qualification #7 / `32642076857`: PASS;
- non-editable installed `grox_vessel-0.8.0` outside checkout in a fresh commissioned Vessel;
- exact Qwen seed `qwen3-4b-q4-k-m-seed-v1` / `Qwen3-4B-Q4_K_M.gguf`, 2,497,280,256 bytes, SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- exact llama.cpp b10218 / `10218 (de699957b)`, release-asset SHA-256 `78ec7a1964710918030e85c132a0995b10b07e4f43001bdf54fe0fd48d1eb85b`;
- CPU-first qualification: Linux x86_64, >=8 GiB RAM and >=8 GiB free working disk, no accelerator required, max four inference threads;
- loopback-only execution namespace, no non-loopback interface/default route, vendor credential variables absent;
- installed `grox ask` returned useful local direct assistance through `grox-local-llama-cpp` with `mission_created=false`, `crew_delegated=false`, `authority_changed=false`;
- natural-language high-risk Inspect produced local interpretation/planning and proceeded through the existing governed Mission path;
- deterministic selected executor `application-security-engineer`; Mission/execution completed with mutation false and bounded Pilot synthesis;
- independent verifier `code-reviewer`, PASS, different from executor;
- no `cognition_degraded`;
- reconstitution returned `active_after=[]`, `auto_activation=false`, `authority_changed=false`, unload errors empty;
- independent final review found no material blocker and no Mission Control, Tool Gateway, Repair, verifier-core, Crew-eligibility, or reconstitution-policy widening;
- PR #114 merged as `main@a21c9999d220952bff2397754e66c9480de3a750`;
- canonical merge tree `e1d89e1c2e64b3422abb4db72f5263eb757bca03` exactly matches CI-tested synthetic merge `f9e400610e8639ec3b70484555f760cb11cdbc73` tree `e1d89e1c2e64b3422abb4db72f5263eb757bca03`;
- issue #113 closed completed.

**NCI-3 EXIT: QUALIFIED.** Offline, the Commander can converse with GorXu, state a natural-language objective, receive bounded interpretation/planning, route governed Crew work, complete a high-risk Inspect Mission, receive synthesis, and obtain independent verification in the defined qualification profile. This does not qualify every assistant/tool surface offline, a public installer/desktop launcher, NCI-4 neural Crew evolution, model self-activation, a new release/tag, or A8.

## Live Environment Awareness — issue #115

**Status: IMPLEMENTATION IN PROGRESS — THREE BOUNDED AWARENESS SURFACES QUALIFIED**

- local cognition/runtime inventory, policy-constrained selection, execution observation, durable identity-only history, and reconstitution semantics are qualified through PRs #119/#120;
- governed Tool Gateway capability awareness for the existing A5 workspace/network/browser/MCP surface is qualified through issue #122 / PR #123;
- bound hosted/session cognition awareness is qualified through issue #125 / PR #126;
- PR #126 canonical merge is `main@6be03b46ac02d121c8ef7e90c25341504fd1d020`; canonical tree `50bf3333eabb066a74b0e62538ea741d7038a106` exactly matches the CI-tested synthetic tree;
- exact-head CI #410 / `32661093847` passed Wheel and Python 3.11–3.14; Python 3.12 recorded Vessel Health 10 PASS, pytest 364 passed / 2 skipped / 449 subtests, unittest 366 / 2 skipped, mutations 15/15 + 7/7 + 9/9 + 4/4 + 6/6 killed, and Post-Apex PASS;
- bound hosted/session providers are inventoried without callback/network invocation; authorization and qualification are exact independent policy inputs; prior remote observation cannot become current readiness;
- remote provider reachability/freshness, unbound provider/catalog discovery, authorized external-connection awareness, broader process/application awareness, and adaptive resource routing remain unqualified.

Parent issue #115 remains open. No release, NCI, Apex, A8, command, Crew, Repair, Tool Gateway, verifier, or Commander-authority change is implied.

## Live Local Neural Crew Cognition — issue #76 / PR #79

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

- issue #76 bounded the remaining live-provider evidence gate after the provider-neutral Inspect Crew cognition seam was established;
- the sandbox could not obtain Codex, Qwen, llama.cpp, or other downloadable model artifacts because outbound acquisition was blocked, so the qualification did not simulate a vendor model;
- instead, a real neural action-selection model was trained locally in the executing Python process using actual gradient updates and then bound through the canonical `SessionCrewCognitionProvider` path;
- exact provider: `local-neural-session-crew-v1`;
- exact model: `tiny-mlp-policy-5x8x3-v1`;
- architecture: **5 → 8 → 3 multilayer perceptron**;
- learned parameters: **75**;
- training examples: **240**;
- held-out examples: **100**;
- initial held-out accuracy: **0.44**;
- final held-out accuracy: **1.00**;
- initial model SHA-256: `f5c197881e1fbdf90395bbc09d2c1ac7097691ac68101cf573c64a90b419b6b6`;
- trained model SHA-256: `7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`;
- the changed digest proves the learned parameter state changed during training;
- the model performed two real inference calls through the canonical provider seam: before governed evidence it selected `fs_read` with probability **0.999859**; after the governed observation it selected `finish` with probability **0.999892**;
- selected craft and bounded Crew memory were present in the live inference context;
- the read remained governed by the existing sealed Mission Order + Tool Gateway path;
- canonical provider qualification returned PASS with Inspect mode preserved, craft selection evidenced, memory selection evidenced, governed observation evidenced, bounded Crew work product, no cognition denial/degradation, no mutation evidence, `outcome.mutation=false`, and independent verification PASS;
- final implementation head `c8be4d78f92466d3e66ec915b12dcec316396b6d` passed exact-head CI `32336799141` / run **252** across all five required jobs;
- Python 3.12 qualification: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **252 passed, 2 skipped, 440 subtests**, unittest **254 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS;
- PR #79 merged as canonical `main@d49f43246922c6d8c5e3a632423195ffecd9f161`;
- canonical merge tree `109f7d7ddc9712e3d9eec009582025c82317794a` exactly matches the CI-tested synthetic merge tree;
- issue #76 closed as completed;
- Ship's Log 0059 was added through PR #81 and merged as `main@9ca37596c631771ccd0d7ebbab80762d42466179` after documentation-only CI passed;
- the qualified claim is exactly: **GroX has qualified one live locally trained neural action-selection provider through the bounded Inspect Crew cognition seam**;
- this does **not** qualify a general-purpose LLM, Qwen, Codex, the OpenAI Responses adapter in live operation, other external models, all 82 Crew as autonomous model agents, model cognition in Repair/Verify/Execute, unrestricted autonomy, A8, or a new Apex stage.

## Prime Function doctrine — issue #83

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE VERIFIED**

Commander intent makes GroX's purpose ordering explicit:

> **GroX exists first to serve as the Commander's persistent AI personal assistant and operating partner.**

Operational meaning:

- GorXu remains the Commander's principal conversational/assistant interface, second-in-command, and sole operational orchestrator;
- GroX should remain broadly usable for natural conversation, questions, planning, research, files/code/repositories, qualified tools and connected systems, memory, automation, Crew delegation, and multi-step objectives as those surfaces are qualified;
- Commander intent and objectives remain authoritative; GroX may challenge, warn, expose contradictions, or recommend safer/stronger methods but may not replace Commander intent with a self-generated objective;
- native cognition, learning, training, and evolution are core survival/improvement functions whose purpose is to make personal assistance more useful, resilient, private, capable, efficient, offline-capable, and vendor-independent;
- assistance is not primarily a mechanism for collecting training experience; verified experience may support learning only as a governed by-product of accomplishing Commander objectives;
- no Crew member, model, trainer, evaluator, memory system, or evolutionary process may acquire a purpose or authority that supersedes the Commander;
- model-centric benchmark improvement is insufficient if a candidate degrades conversational usefulness, task completion, reliability, latency, affordability, maintainability, recovery, or Commander control;
- a more capable GroX must remain a more capable personal assistant.

Canonical doctrine evidence:

- PR #84 final head `94c7e708fb716dbec161065eae12825ddba02d9d`;
- exact-head CI `32343643297` / run **258** passed all five required jobs;
- PR #84 merged as `main@55260f4753f02ec3d1daf4c5e04df1697a07fa35`;
- canonical merge tree `3427e3f4fd3181fbdecc3871aa8292da359ed12f` exactly matches CI-tested synthetic merge `5633068297a90f620e19586cbb0f3b640feeb46e`.

This doctrine constrains NCI-1 onward. It adds no runtime authority, does not claim currently unqualified assistant/tool surfaces, creates no A8, and does not move package/release state.

## Native Cognition Independence Program 001 — strategic direction

**Status: IMPLEMENTATION IN PROGRESS — NCI-1 + NCI-2 + NCI-3 QUALIFIED; LIVE ENVIRONMENT AWARENESS IN PROGRESS; LOCAL-RUNTIME + GOVERNED TOOL GATEWAY + BOUND HOSTED COGNITION AWARENESS EXITS QUALIFIED**

Commander intent establishes a long-term native-cognition direction under the Prime Function:

> **GroX is a neural organism that becomes progressively better at operating inside GroX.**

Purpose constraint:

> **The organism evolves in order to become a better personal assistant and Crew orchestrator to the Commander. Evolution is a core survival and improvement function, not an independent purpose.**

The intended architecture is native-first rather than vendor-required while preserving the canonical command spine:

**Commander → Pilot GorXu → Divisions → Standing Crew**

- GroX should own its cognition lifecycle: runtime contract, model registry and lineage, local inference placement, context, learning corpus, training, evaluation, model promotion, installation/runtime layout, persistence, and recovery;
- native cognition is an engine/capability under GorXu, not a layer above GorXu or between GorXu and Crew;
- runtime assets, private state, Commander workspace, Tool Gateway, memory, evidence, models, trainers/evaluators, installers, and launchers are infrastructure, not command hierarchy;
- the minimum target operating condition is useful **offline personal-assistant + Crew-orchestration cognition** without a paid model subscription, external API credential, or required network connection;
- external models such as OpenAI, Anthropic, Google, and future providers remain optional governed intelligence capabilities that GorXu may use when they materially improve a Commander objective, Mission, or Crew task;
- vendor models do not become the Vessel's command authority, and external intelligence does not inherit GroX authority merely because it is more capable;
- low-level inference kernels and initial language-capable seed weights may come from permissively licensed open components when that is the smallest effective implementation path; GroX ownership means owning the cognition lifecycle and operating contract, not duplicating numerical kernels without demonstrated need;
- the existing 75-parameter local neural provider is the first canonically qualified GroX-trained learned component and becomes seed evidence for richer native model evolution;
- verified Mission trajectories may become learning material; unverified model output is not training truth, and personal assistance is not subordinated to training-data collection;
- outputs from vendor models may be admitted into training/evaluation only where applicable rights/terms permit it, provenance is retained, and GroX verification admits the material;
- model descendants may be trained and compared, but **evolution cannot self-authorize**: a candidate cannot promote itself because its score improved;
- accepted and rejected generations should retain parentage, architecture, parameter count, corpus/provenance digest, training configuration, model digests, benchmark results, regressions, and disposition;
- larger models are not automatically better; regression in Commander-facing usefulness, GorXu orchestration/delegation quality, authority compliance, generalization, reliability, latency, cost, maintainability, safety, or recovery is grounds for rejection.

Canonical staged roadmap in `docs/stewardship/ROADMAP.md`:

1. **NCI-1 — Native cognition runtime + local Vessel foundation: QUALIFIED.** NCI-1A workspace commissioning, NCI-1B runtime/state/work separation, NCI-1C packaged runtime assets + standalone installed GorXu, NCI-1D native model registry + local inference runtime, and the installed-wheel model-runtime exit proof are canonical and exact-tree qualified at the NCI-1 boundary.
2. **NCI-2 — Built-in local seed cognition: QUALIFIED.** The exact Qwen3-4B Q4_K_M seed is qualified on the installed CPU-first path with integrity/provenance, pinned llama.cpp runtime, external-network isolation, no vendor credential, bounded GorXu cognition, Crew routing, and independent verification.
3. **NCI-3 — Offline GorXu cognition: QUALIFIED.** Issue #113 / PR #114 qualify local conversational interaction, natural-language objective interpretation, planning/synthesis, governed Crew delegation, high-risk Inspect execution, and independent verification while deterministic authority remains authoritative.

**Immediate Commander-designated bounded priority before NCI-4:** **Live Environment Awareness — issue #115.** The local cognition/runtime exit is QUALIFIED through PRs #119/#120, governed Tool Gateway awareness through #122/#123, bound hosted/session cognition awareness through #125/#126, and bound remote origin transport freshness through #128/#129. Broader awareness remains IN PROGRESS; provider/service readiness beyond transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, ambient application/process awareness, and adaptive provider/resource routing remain unqualified. Continue only from canonical runtime evidence and preserve discovery/authorization/readiness/qualification/selection/observation separation. This priority does not renumber NCI-4 through NCI-9 and does not imply any later NCI stage is qualified.
4. **NCI-4 — Neural Crew evolution:** evolve the qualified policy toward richer action/path/evidence/test/confidence/failure decisions with generation-by-generation comparison.
5. **NCI-5 — Mission learning corpus and evolution registry:** structure verified operational experience into provenance-bound learning material and model ancestry without turning assistance into a data-acquisition objective.
6. **NCI-6 — Optional external teacher/tool adapters:** allow governed external intelligence for difficult work and, where permitted, candidate teaching material without dependency or inherited authority.
7. **NCI-7 — Governed model evolution and promotion:** parent-versus-descendant benchmarks including Commander-facing usefulness, GorXu orchestration quality, adversarial tests, preserved red evidence, independent verification, and explicit activation gates.
8. **NCI-8 — Offline Vessel qualification:** prove an installed/local **personal-assistant + Crew-orchestration** profile with conversational Commander↔GorXu interaction, direct assistance, planning, GorXu Crew delegation, local tools/evidence, durable state, and verification, with no paid subscription, external API credential, or network requirement.
9. **NCI-9 — Connected and augmented operation:** after offline qualification, use network, remote compute, and external models as optional capability multipliers under the same Prime Function and authority model.

No later NCI stage is qualified merely because it is listed. No A8 is created or implied. Package/release remain `0.8.0` / `v0.8.0`; Standing Crew remain 82.

## Selective Deep-Craft Crew Cognition — issue #73 / PR #74

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

- Commander authorized the strongest repository-backed post-Apex candidate after Mission Outcome Truthfulness: bounded Mission-relevant specialist craft plus bounded Crew memory, without creating A8 or another command layer;
- canonical starting source was `main@8ffbee2f14e0e915e721835e9e84cc2289fc9661`;
- Inspect-only selective craft now reads only the routed Standing Crew member's canonical craft card, defaults to at most **6 sections / 4,500 characters**, and never injects the complete deep card by default;
- `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` must fit in full when present; insufficient mandatory-context budget fails closed rather than truncating safety or operational binding;
- Verify, Repair, and Execute retain their existing task/memory context without unused deep craft from this seam;
- Inspect execution emits explicit attributable `craft_selection` evidence containing full-card digest, selected headings/size, source revision, and freshness policy;
- a provider-neutral Inspect-only Crew cognition seam may consume a sanitized copy of the sealed Order envelope, selected craft, bounded Crew memory, and governed observations;
- cognitive action requests are limited to already-authorized `fs_list`, `fs_read`, and `test_run` through the existing Mission Order + Tool Gateway boundary;
- default cognitive bounds are **4 steps**, **1 cognitive test run**, **8,000 observation characters**, and **4,000 work-product characters**;
- mutating requests and scope/root escapes fail closed; known recoverable provider/contract failure degrades only to the existing deterministic Inspect executor without authority widening;
- provider-facing Order/craft/memory/observation structures are copied per call; provider-local mutation cannot alter executor-owned authority/context or prior observation history;
- governed cognitive observations remain evidenced if the provider later degrades; persistent read-observation evidence stores bounded metadata/hashes rather than raw file content;
- craft/cognition bookkeeping evidence is excluded from Living Company evidence-quality scoring, preventing the seam from improving routing history merely by creating extra evidence kinds;
- controlled fake-provider regressions cover single Missions, Mission Graph Inspect nodes, mutation denial, scope escape, provider degradation, observation persistence, provider-input mutability, test-run ceiling, work-product ceiling, Inspect-only craft injection, complete mandatory craft preservation across all 82 canonical cards, and routing neutrality;
- material blockers found during implementation/review were repaired rather than waived, including synthetic fixture craft gaps, mandatory-context starvation/truncation, provider-input mutability, lost pre-degradation observations, repeated cognitive test cost, unbounded work products, unnecessary non-Inspect craft injection, weak craft-selection observability, and routing-score inflation;
- final implementation head `db83c557e378e6e3a3471318b50e6b82a5d68641` passed exact-head CI `32166921610` / run 232 across all five required jobs;
- Python 3.12 qualification: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **235 passed, 2 skipped, 354 subtests**, unittest **237 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS;
- integrated qualification retained `new_apex_stage=false`, `qualification_claim=false`, and `release_decision=false`;
- independent final review on the exact head returned PASS with no remaining material blocker;
- PR #74 merged as canonical `main@8420b9cbe5ca046ded87c8feaec83eca7cfdc475` and issue #73 closed as completed;
- canonical merge tree `170bbfb9fe483b1faae362adc15ec944ca5c96c9` exactly matches the CI-tested synthetic PR merge tree, proving exact source equivalence;
- no separate post-merge push run is claimed because none was observable through the available GitHub interface;
- historical issue #73 qualification proved the **provider-neutral controlled seam only**. That boundary was later advanced by issue #76 / PR #79 to one qualified live local neural provider; it still does not imply a general-purpose language model or broader model authority;
- Commander authority, GorXu sole-orchestrator status, Repair boundaries, verifier independence, Mission Graph authority, package `0.8.0`, published `v0.8.0`, 82-Crew company, and no-A8 posture remain unchanged.

## Mission Outcome Truthfulness — issue #70 / PR #71

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED**

- public-readiness testing against `main@16f541480b192ca1f2576e3ed9c3457885b58f5e` showed generic Execute Missions could complete only a bounded repository inventory while plain `completed` could be misread as Commander-objective delivery;
- issue #70 bounded the repair without weakening authority, adding no generic natural-language writer, no implicit Repair, no command layer, no Crew, no Apex stage, and no release change;
- the single-Mission Pilot now separates executor lifecycle from Commander-facing Mission outcome and persists `mission_outcome` evidence with `execution`, `effect`, `objective`, `mutation`, `next_authority`, and `verification_scope`;
- generic Execute inventory fallback now reports `status: scan_only` with `execution_status: completed`, `objective: not_delivered`, `mutation: false`, and `next_authority: explicit_operation_or_repair`;
- verification PASS on an unsatisfied objective is explicitly scoped to bounded execution evidence only and cannot become proof of objective delivery;
- supported explicit `repair-write` remains a Repair-authorized mutation path with independent verification and bounded objective-satisfied semantics;
- independent review found and blocked one unsafe exception-reporting edge before merge: a Repair mutation could remain unresolved after rollback failure while the initial classifier would have said `mutation: false`;
- final behavior is conservative: completed rollback reports `mutation_rolled_back` and no remaining mutation; rollback failure or divergent state reports `mutation_state_unresolved`, `mutation: true`, and `next_authority: pilot_recovery`;
- permanent regressions cover generic build intent, repair-like wording under Execute, supported `repair-write`, unresolved mutation after failed rollback, and completed rollback with no remaining mutation;
- final implementation head `37392878566bbe9ad84eba3b5d723a974cca5164` passed exact-head PR CI `32127267143` across all five required jobs;
- Python 3.12 qualification: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **218 passed, 2 skipped, 354 subtests**, unittest **220 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS;
- integrated qualification explicitly retained `new_apex_stage=false`, `qualification_claim=false`, and `release_decision=false`;
- PR #71 merged as canonical `main@1409605a98e0fd805a55839321f28364505773f5` and issue #70 closed as completed;
- merged `main` tree `fedb4d54bb2e907f6fc9ff1e0125476c6af4f587` exactly matches the final CI-qualified PR-head tree, proving exact source equivalence;
- no separate post-merge push run is claimed because none was observable through the available GitHub interface;
- Commander authority, GorXu sole-orchestrator status, Repair boundaries, verifier independence, Mission Graph semantics, package `0.8.0`, published `v0.8.0`, 82-Crew company, and no-A8 posture remain unchanged.

## Runtime Integrity Repairs — issues #63 and #64

**Issue #63 status: COMPLETE — CANONICAL POST-MERGE VERIFIED**

- isolated sandbox qualification of exact canonical `main@8470a715a0bc37877013608c9daa178acfa4cbab` reproduced three runtime-integrity gaps before repair: Repair timeout rollback bypass, authorized Graph Repair SQLite thread affinity, and snapshot-present Health/SnapshotReport contract mismatch;
- four permanent regressions now cover timeout rollback, authorized Graph Repair, valid snapshot readiness, and invalid snapshot readiness;
- corrected implementation head `9c4c014292d890cfa22e97fd2a6b4607ce74d6dd` passed exact-head PR CI `32075807852` across all five required jobs after one transient A5 Docker-probe rerun on unchanged source;
- PR #65 merged as canonical `main@ccd26f2b7eed0804338667fc9e13190c5e9d389e`;
- independent exact-SHA Actions audit resolved canonical push run `32076103017`, which completed successfully across Python 3.11, 3.12, 3.13, 3.14 and Wheel bootstrap;
- Python 3.12 canonical post-merge evidence: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **209 passed, 2 skipped, 354 subtests**, unittest **211 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, integrated Post-Apex qualification PASS;
- interrupted local mutation qualification temporarily carried two deliberate graph mutants into an early candidate; static PR review caught them before merge, both canonical invariants were restored, and remote mutation proof killed them again with clean restoration;
- no authority widening, release/tag change, Crew roster change, new Apex stage, or A8 was introduced.

**Issue #64 status: COMPLETE — CANONICAL POST-MERGE VERIFIED**

- canonical doctrine says `independent-verifier` is not an alternate automatic execution route, while a separately authorized Mission Order may deliberately assign another role/mode;
- repository inspection confirmed **16 verification-capable Crew**, so `verification=true` remains verification eligibility and cannot serve as a verification-only marker;
- a distinct dossier property `ordinary_routing` defaults to `true` and is `false` only for `independent-verifier`;
- Living Company and legacy roster ordinary routing honor that property; Verify routing remains governed by `verification=true`;
- cognitive/preferred recommendations cannot force a role-only verifier into ordinary routing, while explicit bounded GorXu `crew_id` assignment remains the separately authorized exception path;
- exact red-baseline CI `32078007106` failed the three intended ordinary-routing assertions before implementation and kept Health/Wheel green;
- implementation qualification on Python 3.12 reached Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **215 passed, 2 skipped, 354 subtests**, unittest **217 OK, 2 skipped**, mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6**, and integrated Post-Apex PASS;
- an older durable-recovery assertion was strengthened from incidental Crew assignment count to the committed architecture node's actual objective/order identity after the new routing boundary legitimately changed recovery consultation Crew reuse;
- final exact-head CI `32078828303` passed all five required jobs on `1531f4d4f3e2a222cdef5c32b7c6b70debba35de`; PR #67 merged as `main@d04d21e38ffe1645d9c9e0df61e7ca96ac465066`; exact-SHA post-merge push CI `32079205250` completed successfully;
- canonical Python 3.12 evidence is Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **215 passed, 2 skipped, 354 subtests**, unittest **217 OK, 2 skipped**, mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed with clean restoration, and integrated Post-Apex PASS;
- no release/tag, authority, Crew membership, Apex-stage, or A8 change was introduced.

## Cognitive Context Efficiency — issue #60

**Status: COMPLETE — CANONICAL POST-MERGE VERIFIED**

- Commander authorized a bounded optimization of GorXu's repeated cognitive context; this did not create A8, a new command layer, or any release authority change.
- recalibration source before work was `main@40e8234aecb23d5775e3c407b6ed19a054b35f84`; canonical push CI `32042022453` was green on that exact source.
- implementation was isolated on `agent/cognitive-context-efficiency` and completed through PR #61.
- investigation confirmed that deep Standing Crew craft cards are not automatically injected when Crew are summoned; `CrewRoster.craft_card()` remains an explicit read-only lookup.
- GorXu now receives a deterministic 82/82 Standing Crew Directory containing Crew ID, Division, title, descriptive domains, and verification eligibility; capability grants and expanded routing tags remain local deterministic GroX routing inputs.
- provider-neutral `CognitiveUsage` evidence now records available input, cached input, cache-write where exposed, output, reasoning, total tokens, provider, and model without becoming an execution or authority dependency.
- the OpenAI reasoning adapter now places stable Standing Crew context before the changing Commander directive, supplies a deterministic prompt-cache identity, and retains `store:false`; cache state affects efficiency only.
- the project/session reasoning provider explicitly reports usage unavailable because the host callback does not expose token accounting; GroX does not invent token evidence.
- bounded structural measurement: legacy roster **38,082 characters** → compact directory **20,887 characters**, a **45.15%** serialized-context reduction with all **82/82** Standing Crew still visible.
- the canonical deep specialist craft library measures **1,293,064 characters** and remains outside the per-call cognitive directory; deep craft is not injected merely by Crew selection.
- the structural measurement is not an actual token, provider-cost, or latency claim; real provider token/cache evidence can now be captured when exposed by the active adapter.
- final implementation head `72f460233112240bbe43cf2db2453b6ef860b594` passed exact-head PR CI `32046970220` across all five required jobs and received bounded verification PASS.
- PR #61 merged as `a4534116bdd405fca42c8112271f702108456bce`; canonical post-merge CI `32047295992` completed successfully across all five required jobs on that exact `main` SHA.
- Python 3.12 qualification remained fully green: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **205 passed, 2 skipped, 354 subtests**, unittest **207 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS.
- existing A1 behavior remains intact: invalid cognitive Crew recommendations cannot create eligibility and fall safely through the qualified deterministic routing path.
- hierarchical shortlist routing, embeddings, vector databases, and extra model-routing stages remain deferred because the compact-directory change produced a material reduction without adding architecture; revisit only if real provider usage evidence shows further need.
- the selective deep-craft adjacency identified by issue #60 later advanced through issue #73 / PR #74 and then through issue #76 / PR #79 to one qualified live local neural provider; the historical issue #60 qualification itself remains unchanged.
- hard invariants remained unchanged: Commander intent is verbatim; GorXu remains sole operational orchestrator; deterministic capability, risk, Repair, Tool Gateway, and verifier-independence controls remain authoritative; caching and usage telemetry cannot grant authority; no tag/release moved and no A8 was created or implied.

## Verified Vessel baseline

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified by source, qualification evidence, and automated testing:

- GroX-native command architecture implemented
- Commander Seat CLI and interactive bridge live
- Pilot GorXu is the sole operational orchestrator and principal assistant interface
- Mission Control operates as a native advisory/policy subsystem under GorXu
- 81 specialist-inspired Standing Crew recruited as native GroX identities
- 1 native independent verifier retained, for 82 total standing dossiers
- active Standing Crew membership is canonical, source-defined, and free of stale roster overlap
- non-standing or otherwise stale Crew operational state is purged during roster reconstitution
- orchestration-role recruitment blocked; orchestration remains Pilot authority
- fresh Crew tours with persistent tour/episodic state
- SQLite Mission, Order, Evidence, and Crew state persistence
- Tool Gateway v2 with deny-wins Mission Order, Crew capability, and host-policy enforcement
- governed isolated workspace execution, memory-only secret brokerage, exact-origin network access, offline browser evidence capture, and pre-registered stdio MCP adapters
- Inspect vs Repair mutation separation enforced
- Mission Orders enforce competence/authority intersection
- independent verifier must differ from executor
- interrupted Crew duty state recovers safely on restart
- domain-routing contracts added for the expanded company
- A6 external audit independently collected 102 tests (`pytest`: 100 passed, 2 environment-dependent browser skips; `unittest`: 102 ran OK, 2 skips)
- live Inspect Mission completed successfully
- live medium-risk Repair Mission completed with independent verification
- first post-Apex operational Inspect Mission `MSN-8a86f094509b` completed on the canonical source with `code-reviewer`, full regression evidence, and independent verification PASS by `independent-verifier`
- permanent least-privilege CI now exercises Python 3.11 through 3.14 regressions plus non-editable wheel bootstrap portability on pull requests and `main`; third-party actions are pinned to immutable full commit SHAs
- canonical `main` is protected by an active repository ruleset requiring pull requests and all five canonical CI gates with strict up-to-date enforcement, blocking deletion and non-fast-forward updates, with no bypass actors
- Vessel-root discovery supports explicit `GROX_VESSEL_ROOT` binding, current-checkout discovery, editable-source fallback, and fail-closed refusal to construct an unbound 0-Crew Vessel; NCI-1 now provides commissioned-workspace, separated-layout, validated packaged-runtime operation, native model registry/inference, and installed packaged-model load/inference/reconstitution outside checkout while preserving the same GorXu authority boundary
- package/source version metadata is aligned to released `v0.8.0` and remains guarded by both pytest and unittest
- current published release `v0.8.0` is pinned to `27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`; canonical source may advance beyond that immutable release through the protected PR/CI path
- current protected source includes Mission Outcome Truthfulness with explicit scan-only and mutation-state outcome evidence while package version remains `0.8.0`
- current protected source includes Inspect-only selective deep craft, a CI-qualified provider-neutral controlled Crew cognition seam, one qualified live locally trained neural action-selection provider, the complete qualified NCI-1 local runtime/install/model foundation, qualified NCI-2 Qwen3-4B built-in local seed cognition, qualified NCI-3 offline GorXu conversational cognition, and qualified Live Environment Awareness exits for local runtime, governed Tool Gateway, and currently bound hosted/session cognition resources; a public one-command installer, desktop launcher, current remote reachability qualification, unbound provider discovery, and adaptive resource routing remain future qualification targets.

## Company state

- Total standing dossiers: **82**
- Specialist-inspired Crew: **81**
- Native support Crew: **1 independent verifier**
- Verification-capable Crew: **16**
- Duplicate Crew IDs: **0**
- Recruited command/orchestrator roles: **0**

### Crew-state hygiene

- operational Crew membership is defined only by the current source roster;
- non-standing dossiers fail closed rather than becoming sleeping Crew;
- stale Crew state, Crew-scoped memory, and adaptive performance data are purged at roster reconstitution;
- historical Mission, Order, and Evidence rows remain inert audit history;
- semantic `orchestrator` identities are rejected by Crew ID and title;
- CI run `31933827452` verified the hardening with **128 pytest passed, 2 skipped** and **130 unittest OK, 2 skipped**.

### Division attendance

- Strategy: 17
- Engineering: 14
- Intelligence: 13
- Assurance: 12
- Platform: 10
- Physical Systems: 7
- Operations: 5
- Verification: 3
- Systems: 1

## Evidence boundary

The complete Git-tracked live Vessel source is synchronized to `vessaxor-spec/GroX` on `main`. Private SQLite and `.groxstate` operational state remain outside public Git by design. Operational reconstitution purges stale Crew identities that are not part of the active source-defined company; only current source-defined Standing Crew are operational.

NCI-1B separates runtime/assets, private state, and Commander work when the separated layout is used. NCI-1C binds the qualified packaged runtime assets to that same separated layout for normal commissioned installed startup. NCI-1D adds the GroX-owned local model registry/inference/readiness contract, and the NCI-1 exit proof demonstrates that packaged model path from the installed wheel outside checkout. NCI-2 binds the exact Qwen3-4B seed through that installed model path and proves a bounded local GorXu cognitive Mission without vendor credentials or external network access. Those are filesystem/runtime/cognition capabilities, not command hierarchy: Crew definitions and models in runtime assets remain subordinate to Pilot GorXu, private state has no command authority, and Tool Gateway ordinary filesystem access remains bounded to Commander work.

## First post-Apex operational cycle

**Status: HARDENED AND CI-VERIFIED IN CURRENT SOURCE**

- initial operational run `31919127956` used a normal non-editable install and correctly returned a bounded routing failure after the old CLI root assumption resolved into site-packages with 0 Standing Crew;
- documented editable bootstrap run `31919157280` reconstituted all 82 Standing Crew and completed Inspect Mission `MSN-8a86f094509b`;
- `code-reviewer` inspected 198 files and executed the full regression path with return code 0;
- `independent-verifier` independently verified the Mission PASS;
- no source mutation occurred in either operational observation run;
- the bounded repair candidate introduced portable, explicit, fail-closed Vessel-root binding and the first persistent canonical CI workflow;
- CI run `31919583794` passed wheel-bootstrap portability plus Python 3.11 and 3.12 regression jobs; Python 3.12 recorded **126 pytest passed, 2 skipped** and **128 unittest OK, 2 skipped**;
- the wheel path proved three states: current-checkout binding succeeds with 82 Crew, explicit `GROX_VESSEL_ROOT` succeeds outside the checkout, and an unbound installed runtime fails closed rather than starting an empty Vessel.
- PR #16 aligned `grox.__version__` with package metadata and added a dual-runner consistency invariant; exact-head run `31935094490` passed with **129 pytest passed, 2 skipped** and **131 unittest OK, 2 skipped**; canonical `main` push run `31935204046` passed all three permanent CI jobs.
- release workflow run `31935428439` created and verified `v0.7.1` at the exact source commit `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`.

This operational hardening preserves Apex status because it changes bootstrap/verification infrastructure rather than Commander authority, GorXu orchestration authority, Crew organization, routing policy, persistence schema, or capability grants.

## Post-release Operational Audit 001

**Status: COMPLETE — GOVERNANCE CLOSED**

- native GorXu Inspect Mission `MSN-ac85d2c7192c` completed with `code-reviewer` and independent verification PASS by `independent-verifier` after the qualified digest-pinned workspace fallback was commissioned;
- two earlier audit harness runs failed closed when the commissioned fallback was absent and are preserved as red environment evidence;
- PR #19 candidate CI run `31938365523` passed Python 3.11, 3.12, 3.13, and 3.14 plus Wheel bootstrap portability;
- Python 3.12 recorded **131 pytest passed, 2 skipped** and **133 unittest OK, 2 skipped** using pytest 9.1.1;
- third-party GitHub Actions are pinned to full commit SHAs and an executable contract prevents mutable action references from returning;
- weekly Dependabot monitoring covers GitHub Actions and Python dependencies without auto-merge;
- pytest test/dev constraints now require `>=9.0.3,<10`, removing the audited `PYSEC-2026-1845` exposure from the previous 8.x constraint;
- exact final PR #19 CI run `31938508389` passed all five permanent gates; PR #19 merged as `53ecce335af79bfe9676f4467349fd78ebcdfb71` with zero tree drift at tree `087742f06877000fb5be9de80af64e11ddb21592`; canonical `main` CI run `31938672912` then passed all five gates;
- follow-on maintenance PR #23 consolidated the researched GitHub Actions upgrades while retaining immutable full-SHA pinning; the canonical squash merge `fe16b334dc5a5174fc7a37fe2bc29e0a693d27c5` has the same tested tree `426ad165d1f3134760c6a81b422d237232ab805a` as the PR merge candidate;
- canonical `main` post-merge CI run `31939076253` passed Python 3.11, 3.12, 3.13, 3.14 and Wheel bootstrap portability;
- GitHub ruleset `Protect canonical main` is active against the default branch, requires pull requests, requires all five canonical CI checks with strict up-to-date enforcement, blocks deletion and non-fast-forward updates, and defines no bypass actors;
- issue #18 was independently verified against live GitHub ruleset state and closed as completed.

The audit preserved the existing command relationship, 82-Crew company, source-defined operational roster, Inspect/Repair boundary, routing and persistence semantics, and Apex qualification invariants. There are no remaining Audit 001 blockers.

## Post-Apex Evolution Program 001 — Stage 5

**Status: COMPLETE — A6 LONGITUDINAL OPERATIONAL DRIFT VERIFIED**

- operational windows are digest-bound to attributable A6 trajectory cases and do not create a second telemetry truth store;
- missing, stale, tampered, incompatible, or non-operational evidence is `UNKNOWN`, never PASS;
- critical authority/capability/verifier/escalation/evidence-trace failures remain first-class and cannot be averaged away;
- baseline runs are selected explicitly and are not rewritten by observation;
- the isolated operational experiment proved real GorXu Mission degradation detection with success **1.0 → 0.0** and tool failure rate **0.0 → 0.5** while the baseline digest and metrics remained unchanged;
- A6 drift proposals remain advisory and `activate()` remains denied;
- red run `32004304942` exposed and preserved an experiment bootstrap defect; green implementation run `32004673068` passed all five jobs, pytest **185 passed, 2 skipped, 351 subtests**, unittest **187 OK, 2 skipped**, and all mutation suites including Stage 5 **4/4 KILLED**.

Stage 6 / issue #31 Mission-to-source provenance research is complete with decision **ADAPT**. A bounded implementation of the private receipt/public commitment design is next before integrated program qualification.

## Post-Apex Evolution Program 001 — Stage 6

**Status: COMPLETE — MISSION-TO-SOURCE PROVENANCE RESEARCH PASSED**

- source-backed decision: **ADAPT**;
- private authorization truth remains in the existing Mission/Order/Evidence state plane rather than GitHub;
- recommended public surface is limited to a random opaque receipt ID, nonce-bound SHA-256 commitment, and coarse change class;
- the private nonce is never published, preventing the public digest from becoming a practical dictionary oracle for low-entropy Mission facts;
- public CI performs structural checks only and receives no private SQLite, `.groxstate`, Commander directive, Mission payload, nonce, or secret authority-verification key;
- independent private verification recomputes the commitment, validates Mission/Order attribution and exact source scope, prevents replay/class downgrade, and binds successful consumption to the merged source revision;
- squash-merge survival uses the source-control platform's canonical commit-to-associated-PR relation rather than relying solely on feature-branch commits or commit-message formatting;
- GitHub/Sigstore custom attestations remain optional future hardening for an external consumer and are not the authority witness;
- zero-knowledge proof infrastructure and HMAC/public-CI secret distribution were rejected as unnecessary or trust-widening for the current need.

Research: `docs/research/MISSION_SOURCE_PROVENANCE.md`.

The bounded provenance implementation is now complete and verified. Integrated operational qualification is next.

## Post-Apex Evolution Program 001 — Provenance implementation

**Status: COMPLETE — PRIVATE SOURCE AUTHORIZATION RECEIPTS VERIFIED**

- receipt state is additive to the existing private `StateStore` SQLite plane; no second Mission ledger/database was created;
- issuance requires a real existing Repair Order with an explicit mutating action and source scope covering the requested receipt paths;
- public receipt metadata is restricted to schema version, opaque random receipt ID, nonce-bound SHA-256 commitment, and coarse change class;
- private verification rechecks the originating Mission/Orders, current Repair/mutation authority, commitment, change-class floor, normalized source scope, replay state, and exact PR head/tree binding;
- missing private authority evidence is `UNKNOWN`, not PASS;
- successful consumption requires the exact verified PR/head/tree and records the canonical source revision;
- public CI receives no Commander directive, private Mission/Order IDs, nonce, private SQLite, `.groxstate`, Crew evidence, or secret authority-verification key;
- repository-wide mandatory provenance enforcement remains deferred until integrated qualification and operational private receipt issuance are proven together;
- red source-provenance mutation run `32007023966` killed 4/6 and exposed two non-isolating targets protected by redundant defenses; repaired exact-head run `32007232455` passed all five jobs and killed **6/6** source-provenance mutations with zero survivors and exact restoration;
- exact-head regression at that gate: pytest **200 passed, 2 skipped, 354 subtests**, unittest **202 OK, 2 skipped**.

Architecture: `docs/architecture/SOURCE_PROVENANCE.md`.
Evidence: `docs/verification/SOURCE_PROVENANCE_MUTATION_MATRIX.md`.

Integrated Post-Apex Evolution Program 001 qualification is canonical on protected `main` and post-merge verified; any release remains a Commander decision.

## Post-Apex Evolution Program 001 — Integrated qualification

**Status: COMPLETE — CANONICAL POST-MERGE PASS**

- preserved red run `32008781935` isolated a direct-script import-path defect in the new integration harness after every pre-existing protected gate remained green; the harness loader was corrected rather than bypassed;
- corrected exact-head run `32009009881` passed Python 3.11, 3.12, 3.13, 3.14 and Wheel bootstrap portability;
- Python 3.12 recorded pytest **202 passed, 2 skipped, 354 subtests** and unittest **204 OK, 2 skipped**;
- Vessel Health remained **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN** on the clean source and detected the injected non-Repair `fs_write` authority violation as `UNHEALTHY` without changing the private SQLite bytes;
- clean state selected FAST reconstitution; fresh-host and degraded authority state selected FULL;
- HOT/WARM/COLD packing preserved Commander intent, authority, critical evidence, unresolved critical state, next action, and retained provenance; automatic Pilot runtime activation remained disabled;
- A6 operational degradation remained `REGRESSION`, baseline content remained unchanged, the proposal remained `proposed`, and activation remained blocked;
- external intake continued to reject circular GroX re-import and duplicate decision truth;
- private source provenance verified an exact source binding while public metadata remained privacy-minimized; missing private witness returned `UNKNOWN`, downgrade/replay returned `FAIL`, and Inspect authority could not issue source authorization;
- mutation proof remained fully green: critical **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6** killed.

The experiment deliberately emits `qualification_claim=false`, `release_decision=false`, and `new_apex_stage=false`; the experiment did not self-certify. PR #53 received bounded PASS reviews on candidate head `5c58392a0b9f8fb80f085128588167712003f283` and final closeout head `3a58a8e9df85087cbbe382085e1b1d9ea1ae6fcd`; final PR CI run `32009983924` passed, the PR merged as `4122845858fae6abdf52af7a3a1ce56256e0c5cf`, and canonical post-merge run `32010172588` passed all five jobs. Any later release remains a Commander decision.

Evidence: `docs/verification/POST_APEX_EVOLUTION_001_INTEGRATION_EVIDENCE.md`.

## v0.8.0 release

**Status: PUBLISHED — LATEST**

- Commander authorization completed issue #55 and published `v0.8.0` as GitHub release ID `371649229`;
- release/tag source is exactly `27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`;
- candidate exact-head CI `32014558365` passed before merge;
- canonical post-merge `main` CI `32015076306` passed all five canonical jobs on the exact release source;
- bounded publisher run `32015853726` succeeded after verifying both the exact `main` SHA and the successful canonical CI run before minting the tag/release;
- definition-only publisher run `32015714728` failed before job creation and performed no tag or release mutation; it remains preserved red evidence;
- `refs/tags/v0.8.0` resolves exactly to the release source and `v0.8.0` is non-draft, non-prerelease, and GitHub's current latest release;
- package/source metadata remains aligned at `0.8.0`;
- the earlier release-canary `32014163449` exposed a hard-coded prior package string; the repaired version-drift challenge remains version-agnostic and passed in the final candidate matrix;
- no Commander, GorXu, Crew, Tool Gateway, verifier, persistence, A6 activation, or other authority boundary was widened; no A8 was created or implied.

## Known deliberate limits

- the Prime Function is explicit Commander doctrine, but documentation does not itself qualify every OpenClaw/Hermes-like personal-assistant surface; actual tools, integrations, autonomy, and external-system operations remain bounded by their implementation and evidence;
- GorXu's historical A1 cognitive operating mode remains project/session-hosted through GPT-5.6 Sol when a capable Space Exploration session is active; NCI-2 adds a separately qualified installed local Qwen seed Mission path and NCI-3 separately qualifies the bounded offline conversational GorXu profile. Deterministic authority remains authoritative, and cognition failure must not widen it.
- Standing Crew have a provider-neutral Inspect cognition seam with selective craft + bounded memory, and one live locally trained neural action-selection provider is operationally qualified through that seam. The qualified provider is narrow; no GroX-pretrained general-purpose foundation model is claimed.
- **NCI-1, NCI-2, and NCI-3 are qualified.** The installed Vessel has commissioned workspace/runtime separation, validated packaged runtime assets, a GroX-owned native model registry/inference/readiness/reconstitution contract, the exact Qwen3-4B built-in local seed, and the bounded offline conversational GorXu profile. This does not provide a public installer/desktop launcher, a GroX-pretrained foundation model, NCI-4, or A8.
- the public one-command macOS/Linux installer and desktop launchers are not yet qualified.
- Live Environment Awareness currently qualifies local-runtime awareness, governed Tool Gateway awareness, already-bound hosted/session cognition awareness, and already-bound remote exact-origin transport freshness. It does not yet qualify provider/service readiness beyond transport freshness, credential validity, unbound provider/catalog discovery, broader authorized external-connection awareness, broader ambient application/process discovery, or adaptive provider/resource routing.
- A3 episodic retrieval plus attributable semantic, procedural, and Vessel-wide memory are live with bounded selective retrieval; autonomous consolidation remains future evolution.
- A4 durable Mission Graph resume, checkpointing, bounded cancellation/retry, and text-Repair compensation are live; generic compensation for arbitrary external systems remains intentionally unclaimed.
- A5 qualifies bounded workspace shell/code execution, memory-only secret aliases, exact-origin read-only HTTP(S), offline browser evidence capture, and pre-registered stdio MCP. Unrestricted interactive desktop control, arbitrary/networked MCP processes, runtime image pulls/builds, and optional A2A delegation remain outside the qualified boundary.
- A5 isolation fails closed when neither the preferred namespace backend nor the host-commissioned Docker fallback is available.
- model training, benchmark improvement, external-provider advice, filesystem placement, installation state, registration, readiness, or runtime load does not grant model/Crew activation, independent purpose, command rank, or additional Mission authority.
- broader offline personal-assistant + Crew-orchestration Vessel qualification under later Native Cognition Independence stages remains future evidence work beyond the bounded NCI-3 profile.

## Apex Orchestrator readiness

**Current status: APEX QUALIFIED**

The initial self-assessment Mission `MSN-354de0550dd5` established the baseline gaps. Since then A1 Cognitive Pilot through A7 Apex Qualification have qualified, and Post-Apex Operational Evolution Program 001 has completed. GorXu now has project-hosted cognition, durable dependency-aware multi-Crew graphs, attributable organizational memory, experienced routing, bounded selective memory, same-Mission crash recovery, checkpointed execution, bounded executive consultation/replanning, cancellation, journaled text-Repair compensation, governed multi-tool execution through Tool Gateway v2, replayable evidence-backed orchestration evaluation whose proposals cannot self-activate, continuous health/reconstitution/drift/provenance mutation proof, truthful single-Mission outcome classification that does not overstate bounded execution, a canonical provider-neutral controlled Inspect Crew cognition seam using selective deep craft + bounded Crew memory, one canonically qualified live locally trained neural action-selection provider operating within that seam, a **qualified NCI-1 local Vessel foundation, qualified NCI-2 built-in local seed cognition, qualified NCI-3 offline GorXu conversational profile, and qualified Live Environment Awareness exits for local runtime, governed Tool Gateway, and bound hosted/session cognition resources**.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`; the active strategic direction is recorded in `docs/stewardship/ROADMAP.md` under Native Cognition Independence Program 001. Issue #83 makes explicit that the program serves GroX's Prime Function as the Commander's persistent AI personal assistant. Issue #94 made explicit that native cognition and installation infrastructure must remain subordinate resources while GorXu stays above and orchestrates Divisions/Crew.

Apex critical path: **COMPLETE**. A1 through A7 are qualified; future changes—including native cognition and installation evolution—must preserve the qualification invariants, Prime Function, command/infrastructure boundary, and Commander authority rather than inherit Apex automatically.

## Apex critical-path update - A1 Cognitive Pilot

**Status:** SESSION-QUALIFIED

Verified in the qualified Vessel:

- provider-neutral cognitive interface added;
- structured Mission interpretation contract added;
- Commander intent preservation is validated;
- ambiguity, option comparison, candidate Crew, confidence, and information needs are first-class fields;
- model recommendations cannot lower the Mission Control risk floor;
- model recommendations cannot self-grant Repair mode;
- Crew recommendations remain capability checked;
- cognitive plans are persisted as Mission evidence;
- provider failures degrade to deterministic control without authority widening;
- session-bound GPT-5.6 Sol reasoning provider added;
- live cognitive Mission `MSN-197e7287b267` completed;
- cognition selected `formal-methods-engineer` without relying on the deterministic keyword route;
- cognition raised risk to high while deterministic controls retained mutation authority;
- independent verification passed by `code-reviewer`;
- 28 automated tests passed at A1 qualification.

**A1 status: SESSION-QUALIFIED.** A capable ChatGPT GPT-5.6 Sol project session may act as GorXu's cognitive provider. No API key, OAuth flow, or vendor CLI is required for this historical qualified operating mode. If the hosting session is unavailable, GorXu degrades to the deterministic control plane rather than widening authority. Native Cognition Independence Program 001 now targets an additional local/offline personal-assistant cognition path without rewriting the historical A1 gate.

A1 exit gate is closed; the current Apex stage is tracked below.

## Persistence foundation

**Status: LOCKED AND IMPLEMENTED**

- cognitive continuity home at the historical A1/A2 baseline: ChatGPT project `Space Exploration`;
- Pilot identity: GorXu; historically qualified project-hosted reasoning runtime: GPT-5.6 Sol / high reasoning;
- durable Vessel source home: `vessaxor-spec/GroX`;
- operational state remains private and outside public Git;
- `.groxstate` snapshot creation, SHA-256 verification, SQLite integrity checking, and confirmation-gated restore implemented;
- restore creates a pre-restore checkpoint;
- `configs/persistence/project-binding.json` records the active persistence bindings;
- automated suite: **31 tests passing** after persistence-plane implementation.

The sandbox is explicitly classified as a replaceable flight computer rather than the Vessel's permanent home. The persistence foundation is closed. NCI-1B adds an installed/runtime filesystem-role separation (runtime assets/private state/Commander work), NCI-1C binds packaged runtime assets into the qualified commissioned installed path, and NCI-1D/exit qualification binds the registered local-model runtime into that installed path without replacing the three persistence responsibility planes or changing command authority. The Apex critical path is complete; future evolution must preserve the qualified Apex invariants.

## Durable source synchronization

**Status: COMPLETE**

- complete Git-tracked Vessel runtime synchronized to GitHub;
- 82 Standing Crew dossiers present in durable source;
- cognition boundary, persistence system, Mission Graph runtime, tests, Apex plan, and Ship's Log are source-controlled;
- private SQLite and `.groxstate` files remain excluded from public Git;
- canonical architecture was reconciled after synchronization to avoid documentation regression.

## Apex critical-path update - A2 Mission Graph Orchestration

**Status: QUALIFIED**

Implemented and verified in the Vessel:

- durable `MissionGraphPlan` and node contracts;
- Commander-intent preservation and DAG validation;
- explicit node attempt/time budgets and Mission node/parallel/replan budgets;
- dependency-aware scheduling with true parallel-ready batches;
- Crew selection per graph node with capability enforcement;
- each node materializes as a bounded native Mission Order;
- graph node/event persistence in SQLite;
- explicit independent verification nodes;
- repair nodes denied unless GorXu receives explicit mutation authorization;
- bounded automatic replanning for recoverable Crew/runtime failures;
- downstream dependency rewiring after replacement;
- Pilot-owned persisted synthesis;
- Commander Seat `graph-mission` command with validated JSON plan input;
- session reasoning provider supports validated Mission Graph proposals;
- **40 automated tests passing**.

A2 qualification Mission: `MSN-f522e1ff611e`.

Qualification evidence:

- seven Crew identities participated;
- three root branches were scheduled as a parallel batch;
- `database-reliability-engineer` received an injected recoverable availability failure;
- GorXu replaced it with `distributed-systems-engineer` without Commander intervention;
- downstream `operations` dependency was rewired to the replacement node;
- `architect`, `formal-methods-engineer`, `application-security-engineer`, `site-reliability-engineer`, and the replacement Crew all completed bounded branches;
- `code-reviewer` independently verified five branch results and ran the full test suite;
- verification passed;
- final Pilot synthesis recorded `replans=1`, no unresolved nodes, and Mission status `completed`.

**A2 exit gate: PASSED.**

A2 exit gate is closed; A3 qualification is recorded below.

## Fresh-session reconstitution and source-integrity recovery

**Status: QUALIFIED FOR A3 READINESS**

A fresh Space Exploration session reconstituted the Vessel against live GitHub source and the private A2 checkpoint before allowing A3 work.

Recovery evidence:

- live `main` matched the A2 handoff commit before recovery work;
- the private `GROX-A2-qualified.groxstate` checkpoint passed archive-path, schema, SHA-256, and SQLite integrity verification and was restored through GroX's controlled persistence path;
- active source-defined company remains 82 Standing Crew, and current reconstitution removes stale Crew state not present in the source roster;
- two source-integrity defects were found before A3: corrupted bytes in the A2 Mission Graph regression test and one mis-indented runtime statement in bounded replanning;
- both defects were repaired on an isolated recovery branch without changing Mission Graph authority semantics;
- the lost `test_graph_repair_requires_explicit_mutation_authority` invariant was recovered from A2 qualification evidence;
- the repaired Vessel installed cleanly, compiled cleanly, and ran the complete suite on a fresh GitHub-hosted Ubuntu 24.04 / Python 3.12 checkout;
- **40/40 automated tests passed** after recovery, including injected Crew failure/replanning, downstream dependency rewiring, graph mutation-authority denial, persistence restore, cognition boundaries, Tool Gateway confinement, full-company integrity, and independent verification paths;
- the Roadmap was reconciled from stale A2 wording to the actual current stage, A3 Living Company Intelligence.

The recovery repairs restore the qualified A2 baseline; they do not implement A3.

## Apex critical-path update - A3 Living Company Intelligence

**Status: QUALIFIED**

A3 turns Standing Crew from static capability matching into an experienced organization while preserving GorXu as sole orchestrator and keeping authority deterministic.

Implemented and verified:

- existing episodic Crew notes are selectively retrievable;
- durable semantic, procedural, and Vessel memory records are persisted in private SQLite state;
- durable memory requires explicit provenance and confidence and supports supersession/correction plus bounded forgetting by deactivation;
- Vessel memory is constrained to Vessel scope;
- per-Crew/task-class performance history records outcome, evidence quality, verification, observed latency, attributable cost units, and risk;
- experienced routing ranks only otherwise-eligible Crew using competence, evidence quality, reliability, load, cost, latency, risk, experience, and bounded validated-candidate preference;
- capability requirements and verifier independence remain hard gates;
- each Mission Order receives only a capped relevant-memory slice: at most six items and 3000 content characters by default;
- memory retrieval preserves relevant memory-plane diversity rather than allowing one large class to crowd out all others;
- single Missions and Mission Graph nodes use the same Living Company routing/memory service;
- routing and selected-memory metadata are persisted as Mission evidence;
- **46 automated tests pass**.

A3 qualification evidence:

- repeated equivalent Missions in a controlled qualification Vessel began with tied eligible backend Crew;
- an injected failure was recorded for the initial Crew while equivalent successful Missions were recorded for the alternate Crew;
- the subsequent automatic Mission routed to the better-evidenced eligible Crew;
- 20 deliberately unrelated memories plus relevant semantic/procedural/Vessel memories were added, yet the selected tour context remained within six items / 3000 characters and excluded unrelated marketing content;
- graph qualification proved experienced routing, memory injection, performance recording, and independent verification use the same service;
- fresh GitHub-hosted Ubuntu 24.04 / Python 3.12 qualification passed **46/46** tests on A3 head `21195ca7b758bd7602874911ee6ee6a5ee36b480`;
- live private-Vessel qualification Mission `MSN-6627085e3cea` ran the complete suite with `code-reviewer`, returned `tests returncode=0`, and independently verified PASS with `independent-verifier`;
- the private A2 operational state was checkpointed before activation; after A3 schema migration SQLite integrity remained `ok`;
- two source-backed organizational memories were admitted with explicit provenance; no synthetic qualification memory or test Crew was added to the active Standing Crew roster.

**A3 exit gate: PASSED.** Repeated Missions measurably improve routing while per-tour context remains bounded.

## Apex critical-path update - A4 Executive Exception Loop and Durable Operations

**Status: QUALIFIED**

A4 qualification adds:

- private `DurableState` graph-run, checkpoint, exception-decision, and mutation-journal records in the operational SQLite plane;
- crash/reopen handling that marks in-flight Mission, Order, and graph-node state interrupted;
- same-Mission resume from persisted graph state without replaying committed nodes;
- a three-resume automatic bound plus existing node/Mission replan budgets;
- real read-only Crew consultation and evidence before ordinary recoverable replans;
- Commander escalation only for critical, irreversible, authority-divergent, or material-intent exceptions;
- checkpoint-bound cancellation preventing later resume;
- atomic supported `write_text` Repair with stable idempotency keys;
- exact bounded rollback after failed Repair verification;
- fail-closed handling when a journaled mutation target diverges externally;
- timeout normalization into governed exception handling;
- **55 automated tests passing**.

A4 live qualification Mission: `MSN-a62e95886c0a`.

Qualification evidence:

- the A3 private checkpoint re-verified before activation;
- exact independently qualified A4 branch source was materialized on the active flight computer;
- SQLite schema migration completed with integrity `ok`;
- `architect` completed and committed the first node before an injected process interruption occurred on `researcher`;
- fresh Pilot reopen marked the Mission and in-flight research node interrupted;
- resume count was **1** and the architecture Order count remained **1**, proving committed work was not replayed;
- later injected `crew_unavailable` failures on the research and security paths produced **2** persisted exception decisions, each `consult_then_replan` with a real consultation Order;
- neither ordinary failure required Commander escalation;
- final synthesis recorded **2 replans**, **2 exceptions**, **1 resume**, and independent verification **PASS**;
- private SQLite integrity remained `ok`.

**A4 exit gate: PASSED.**

Current Apex stage after A4 was **A5 - Governed Capability Expansion**.

## Apex critical-path update - A5 Governed Capability Expansion

**Status: QUALIFIED**

A5 qualification adds:

- Tool Gateway v2 with explicit `workspace_exec`, `secret_use`, `net_fetch`, `browser_capture`, `mcp_call`, and separately gated `mcp_mutate` actions;
- deny-wins intersection of Commander/Pilot Mission authority, Crew capability, graph requirements, Mission Order action grants, host policy, and operation-specific grants;
- preferred user/PID/network namespace workspace isolation plus a fail-closed, digest-pinned, pre-provisioned Docker fallback for hosts that deny namespace mapping;
- memory-only secret aliases with explicit Mission grants, stdin delivery to isolated workspace setup, captured-output redaction, and ephemeral workspace teardown;
- exact-origin bounded read-only HTTP(S) with redirects denied and fetched content marked untrusted;
- Gateway-fetched HTML rendered in real Chromium offline, with browser-originated networking disabled and screenshot/hash evidence persisted privately;
- pre-registered stdio MCP adapters whose process commands cannot be supplied by Crew;
- separate mutation grant for mutating MCP tools;
- explicit denial rather than unrestricted fallback when required host isolation is unavailable;
- **65 automated tests passing**.

Fresh-host qualification evidence:

- Ubuntu 24.04 / Python 3.12 run `31827486207` passed **65/65** on source head `b1975209752bde569a063276cf6f968440641f16`;
- the runner's preferred user-namespace canary failed at `/proc/self/uid_map` with `Operation not permitted`; this remained evidence and was not bypassed;
- Docker Engine 28.0.4 then proved the governed workspace fallback with network disabled, all capabilities dropped, `no-new-privileges`, read-only root, non-root host UID:GID, and bounded resources;
- a Playwright v1.62.0 Noble browser image pinned by registry digest was explicitly commissioned; runtime did not pull or build it;
- the Docker browser path completed under the outer container sandbox using Docker built-in seccomp, no network, dropped capabilities, `no-new-privileges`, read-only root, bounded resources, and host-recoverable non-root scratch ownership.

Live private-Vessel qualification Mission: `MSN-5c3b646ce6be`.

Qualification evidence:

- sealed A4 snapshot re-verified before restoration and A5 activation;
- private SQLite integrity remained `ok` and all **82** Standing Crew were present;
- `devops-engineer` executed the governed workspace/secret node, `researcher` executed exact-origin network and offline browser nodes, `platform-engineer` executed read-only MCP, and `independent-verifier` closed the Mission;
- workspace output was `[REDACTED]`, the ephemeral workspace was not retained, and the secret literal was absent from both serialized Mission state and the complete SQLite dump;
- browser networking was `disabled_after_gateway_fetch`, `http://example.invalid` was recorded as blocked, and screenshot evidence existed;
- every privileged operation was present in the corresponding Mission Order's explicit action grants;
- synthesis recorded **0 replans**, **0 exceptions**, **0 resumes**, and independent verification **PASS**.

**A5 exit gate: PASSED.**

A5 deliberately does not claim unrestricted interactive desktop automation, arbitrary third-party/networked MCP transports, runtime image acquisition, or the optional A2A external-agent seam.

Current Apex stage after A5 was **A6 - Orchestration Intelligence and Self-Improvement**.

## Apex critical-path update - A6 Orchestration Intelligence and Self-Improvement

**Status: QUALIFIED**

A6 qualification adds:

- privacy-minimized replayable Mission trajectories built from canonical Mission, Order, evidence, graph, exception, and Crew-performance records;
- deterministic success, latency, cost, retry, resume, escalation, verification, evidence-quality, authority, capability, and trace-completeness grading;
- SHA-256-bound evaluation cases, runs, proposals, and creation chronology;
- immutable production routing weights with candidate weights confined to evaluation;
- paired routing evaluation across sequential and parallel cases with family-wise statistical control;
- evidence-backed routing, prompt, skill, memory, and workflow proposals that remain `proposed`;
- explicit denial of proposal activation through the A6 evaluation boundary;
- adversarial coverage for tampering, eligibility, verification, trace completeness, authority, multiple comparisons, and replay integrity.

Qualification evidence:

- GitHub-hosted remediation run `31874649364` passed **102/102** unittest tests and **102 pytest** tests with governed A5 isolation and browser dependencies commissioned;
- the 24-case controlled routing suite improved from **12/24** baseline passes to **24/24** candidate passes, with **12 wins, 0 losses, p=0.000244140625**, family-wise alpha **0.0125**, and **0 invariant regressions**;
- the generated improvement remained `proposed`, and an activation attempt was denied;
- independent canary run `31874579460` first proved five evaluator weaknesses, and unchanged rerun `31874767065` closed with `A6_INDEPENDENT_CANARY_FINDINGS=` after remediation;
- preserved private-Vessel Mission `MSN-f09179526ad7` used `devops-engineer`, `researcher`, `platform-engineer`, and `independent-verifier` across governed workspace, exact-origin network, offline browser, read-only MCP, and verification nodes;
- Mission synthesis recorded **0 replans** and independent verification **PASS**;
- evaluation case `EVC-10573b245e54` was complete with **0 invariants** and replayed the identical trace SHA-256 `e6e0b564eee693d43f50e45fbab6dd33c9c1a0943b320f2f68e54dde5e864d5c`;
- the private `.groxstate` snapshot verified before and after independent restore, SQLite integrity remained `ok`, all **82** Standing Crew were present, and the generated qualification secret was absent from durable SQLite state.

**A6 exit gate: PASSED.**

A6 does not grant proposals authority to mutate the Vessel. Accepted future improvements must still traverse the ordinary GroX authority path with explicit mutation authority and required verification. Native model descendants inherit this same non-self-activation rule.

Next Apex stage after A6 was **A7 - Apex Qualification Gauntlet**.

## A7 entry hardening - external audit response

**Status: PRE-GAUNTLET HARDENING (historical checkpoint)**

An external independent audit of `main@481d83e422119d94759685560b61bfccd9e532da` returned **PASS WITH CONDITIONS** for A7 entry. It independently reproduced the A6 private-state hashes, SQLite integrity, 82-Crew state, preserved Mission `MSN-f09179526ad7`, evaluation case `EVC-10573b245e54`, exact replay trace, zero invariants, verifier separation, authority/risk controls, and proposal activation denial.

The bounded pre-A7 hardening response is limited to proved findings:

- source/state restore compatibility is now enforced: exact source matches are accepted, compatible ancestor state requires explicit allowance, and unrelated or unprovable source state fails closed;
- issued Mission Orders are immutable across authority-bearing fields and nested parameters, preventing ordinary post-issuance scope/grant/verification widening;
- Living Company memory context remains a bounded pre-issuance preparation; persistence or first Tool Gateway use seals the Order against later widening;
- current stewardship/test-count drift is reconciled while historical stage-specific qualification counts remain historical evidence;
- dual routing entry points remain tracked for the A7 gauntlet rather than being removed without proof, because the static catalogue selector is not used by the live Pilot/Graph routing path and premature removal changed established routing-test behavior;
- the A7 gauntlet must include source/state mismatch, post-issuance Order mutation, routing-path consistency, and non-activation of evaluation proposals before Apex can be considered.

Local pre-publication regression on the hardening candidate: **107 pytest tests passed** and **107 unittest tests passed**. This local result is not the independent completion gate; GitHub-hosted and independent verification remain required before merge.

## Apex critical-path update - A7 Apex Qualification Gauntlet

**Status: QUALIFIED**

A7 closed only after every discovered evidence/recovery defect was remediated and independently reverified.

- `31881156996`: red baseline, 11/13;
- `31881548492`: first 13/13 plus complete regressions;
- `31881632862`: independent red on unrelated contradiction verification;
- `31881778987`: 14/14 plus regressions; `31881819968`: unchanged independent canary empty;
- `31881904667`: independent red on forged verifier evidence and duplicate-source amplification;
- final head `0724862dcb2634022ad33e6be14be29df6a914dd`;
- `31882071412`: **16/16 A7, 121 pytest passed with 2 skips, 123 unittest OK with 2 skips**, diff hygiene PASS;
- `31882101734`: `A7_APEX_INDEPENDENT_FINDINGS=`;
- `31882083653`: `A7_APEX_SYNTHESIS_FINDINGS=`;
- private A6 state hashes and SQLite integrity reverified; source ancestry proved;
- A7 entry-hardening conditions remain covered.

A7 adds crash-persistent hard cost ceilings and source-normalized, independently verified contradiction synthesis. Ordinary Crew cannot manufacture runtime verifier evidence, ties remain unresolved, and duplicate findings from one Order cannot multiply its synthesis weight.

**A7 exit gate: PASSED.**

**Apex operating verdict: CANONICAL — APEX QUALIFIED.** Stewardship-final exact-head run `31882589081` passed the 16/16 A7 gauntlet, 121 pytest tests with 2 existing browser skips, 123 unittest tests with 2 skips, both historically pinned independent canaries, and stewardship/diff assertions. PR #11 merged as `419cc73950f573c3e201106f7949c6bf7829f2af` with zero tree drift from the qualified head.

## Post-Apex release baseline

- PR #12 reconciled post-Apex stewardship wording without runtime changes;
- stabilization run `31909761968` passed documentation scope/diff checks plus **121 pytest passed, 2 skipped** and **123 unittest OK, 2 skipped**;
- historical operational-hardening release `v0.7.1` is pinned to `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`; the current published release is `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`, and canonical source continues on protected `main`;
- the company remains **82 Standing Crew**;
- A1 through A7 remain qualified;
- **NCI-1 through NCI-3 are qualified; Live Environment Awareness is the active bounded priority before NCI-4, with local-runtime, governed Tool Gateway, and bound hosted/session cognition awareness exits qualified**;
- future evolution must re-prove affected Apex invariants rather than silently inheriting qualification;
- no A8 is currently defined: operational Mission evidence and Commander intent should determine future evolution.
