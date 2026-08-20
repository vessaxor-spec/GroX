# GroX Roadmap

## Current position

GroX `v0.8.0` is the current published Post-Apex Operational Evolution baseline while canonical source continues through protected `main`. The Vessel has 82 Standing Crew, three-plane persistence, qualified A1-A7 Apex behavior, protected CI across Python 3.11-3.14 plus wheel bootstrap, continuous critical-detector mutation proof, a native read-only Vessel health surface, tiered reconstitution planning, controlled context heat, A6 longitudinal operational drift analysis, privacy-safe Mission-to-source provenance, Mission Outcome Truthfulness, bounded Selective Deep-Craft Crew Cognition, and one canonically qualified **live locally trained neural Crew cognition provider** operating through the bounded Inspect seam without widening authority.

The Commander has now set a new strategic direction: **GroX should own its cognition lifecycle and become capable of operating offline without requiring a paid model subscription or vendor-hosted reasoning session.** GroX will evolve its own native cognition runtime and local model family while treating external models such as OpenAI, Anthropic, Google, and future providers as optional governed capabilities rather than required pilots. This direction is a roadmap commitment, not a claim that a general local language model or complete native cognition runtime is already implemented or qualified.

Native command architecture remains:

**Commander → Pilot GorXu → Divisions → Standing Crew**

No model, runtime, trainer, evaluator, external provider, or evolution mechanism becomes a command layer.

## Completed foundation

- GorXu sole operational orchestrator; Mission Control remains subordinate and non-parallel.
- 81 specialist-inspired Standing Crew plus native independent verifier; non-standing or stale operational Crew state is purged.
- Mission Orders, Inspect/Repair separation, deny-wins Tool Gateway, evidence, verifier independence, and Commander escalation boundaries implemented.
- Single-Mission Pilot outcomes distinguish executor lifecycle, actual effect, objective state, remaining mutation state, next required authority, and verification scope; generic inventory fallback is `scan_only` rather than objective completion.
- SQLite Mission/Order/Evidence/Crew/graph/evaluation state plus private `.groxstate` recovery implemented.
- A1 Cognitive Pilot: SESSION-QUALIFIED.
- A2 Mission Graph Orchestration: QUALIFIED.
- A3 Living Company Intelligence: QUALIFIED.
- A4 Executive Exception Loop and Durable Operations: QUALIFIED.
- A5 Governed Capability Expansion: QUALIFIED.
- A6 Orchestration Intelligence and Self-Improvement: QUALIFIED with explicit non-self-activation.
- A7 Apex Qualification: QUALIFIED.
- Operational Audit 001: COMPLETE.
- Canonical `main` protected by PR-only rules, all five required CI gates, strict up-to-date enforcement, deletion/non-fast-forward protection, and no bypass actors.
- External capability intake convention formalized without a duplicate governance layer.
- 12 high-consequence production invariants continuously mutation-proven.
- Native `grox health` surface operational and read-only; 7 critical health behaviors mutation-proven.
- Tiered `grox reconstitution-plan` operational; 9 reconstitution safety decisions mutation-proven.
- Controlled HOT/WARM/COLD context experiment passed with 100% declared critical-fact/provenance retention and 93.47% character reduction on the bounded corpus; runtime activation remains deferred.
- A6 longitudinal operational drift analysis is operational with frozen evidence bindings, fail-closed UNKNOWN semantics, first-class invariant regressions, routing concentration signals, and continuous 4/4 mutation proof.
- Privacy-safe source authorization receipts are implemented in the existing private StateStore plane with exact Repair/scope gating, nonce-bound public commitments, exact-head verification, replay/class-downgrade protection, and continuous 6/6 mutation proof.
- GorXu cognitive context uses an 82/82 descriptive Standing Crew Directory rather than serializing capability grants and expanded routing tags on every cognitive call; provider usage telemetry is observational only and provider caching remains optional.
- Inspect tours may receive bounded Mission-relevant specialist craft with explicit `craft_selection` evidence and may use the provider-neutral read-only Crew cognition seam when a separately supplied provider is present; Verify, Repair, and Execute remain on their existing deterministic paths.
- Issue #76 / PR #79 qualified one **live locally trained neural action-selection provider** through that Inspect seam, proving that learned cognition can occupy a Standing Crew cognition seat without an external model or network dependency.

## Apex critical path

**COMPLETE — APEX QUALIFIED.** `APEX_ORCHESTRATOR_PLAN.md` remains the regression boundary for future evolution.

Released baselines:

- first Apex release: `v0.7.0@71ffd60769d81b5b249dac4eca56333ff27e26d0`;
- post-Apex operational-hardening release: `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`;
- current published Post-Apex Evolution release: `v0.8.0@27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb`.

Canonical source may advance beyond the release through the protected PR/CI path without moving any immutable release tag.

## Recovery rule

A future host may resume GroX only after source materialization, private-state verification/restoration when needed, integrity gates, and GorXu reconstitution. Failure or ambiguity increases the required recovery scope and never widens authority.

Tiered reconstitution now makes that rule explicit:

- FAST only after positive mandatory health evidence and clean source state;
- TARGETED only for bounded noncritical WARN/UNKNOWN evidence after all FULL triggers are excluded;
- FULL for fresh host, source change, critical failure, non-PASS recovery readiness, unsafe in-flight state, dirty source, persistence warning/failure, or missing/non-PASS mandatory evidence.

FAST structurally loads 4/10 defined reconstitution surfaces versus FULL 10/10. This is an evidence-loading count, not a token-savings claim.

## Context efficiency rule

The controlled Stage 4 experiment supports the HOT/WARM/COLD principle but does not authorize automatic runtime compression.

- HOT active/critical material remains verbatim, including Commander intent, constraints, authority, active Mission/graph state, unresolved exceptions/contradictions, critical evidence, safety boundaries, and next action.
- WARM material may use only an attributable supplied summary; without one, raw text remains.
- COLD material may be omitted only when genuinely re-derivable, superseded, or currently irrelevant.
- Age alone never cools a binding safety or authority fact.

The deterministic four-scenario corpus reduced 20,464 source characters to 1,336 while preserving all declared critical facts and retained provenance. This 93.47% controlled character reduction is **not** a production token/latency claim. Pilot runtime activation remains deferred to integrated operational evidence.

## Cognitive Context Efficiency — issue #60

**Status: COMPLETE — CANONICAL POST-MERGE VERIFIED.** This bounded Post-Apex optimization is implemented on protected `main`; it is not A8 and did not add a command layer.

Implemented:

1. **Provider-neutral usage telemetry.** Cognitive adapters may report input, cached input, cache-write where available, output, reasoning, total tokens, provider, and model. GorXu persists available values as observational `cognitive_usage` Mission evidence; unavailable usage is not invented and telemetry cannot become authority.
2. **Compact Standing Crew Directory.** All 82 Standing Crew remain visible to GorXu through identity, title, Division, descriptive domains, and verification eligibility. Capability grants and expanded routing tags remain local deterministic GroX routing inputs.
3. **Cache-friendly provider framing.** Stable cognitive contract and Standing Crew directory precede Mission-specific Commander input. The OpenAI adapter supplies a deterministic prompt-cache identity while retaining `store:false`; cache hit, miss, expiry, or removal changes efficiency only.
4. **Permanent qualification measurement.** Python 3.12 CI now executes `cognitive_context_efficiency_experiment.py` in addition to the existing A1/A3/Apex regression and mutation chain.

Bounded structural result:

- all Standing Crew visible to cognition: **82/82**;
- legacy serialized roster: **38,082 characters**;
- compact Standing Crew Directory: **20,887 characters**;
- structural serialized-context reduction: **45.15%**;
- canonical deep specialist craft library: **1,293,064 characters**, intentionally outside the per-call directory;
- capabilities serialized to cognition: **no**;
- expanded routing tags serialized to cognition: **no**;
- deep craft injected merely by Crew selection: **no**.

This is a deterministic character/context result, **not** an actual token, provider-cost, or latency claim. Actual token/cache usage can be evidenced when the active provider exposes it; the project/session provider currently reports usage unavailable rather than fabricating numbers.

Qualification evidence:

- final implementation head: `72f460233112240bbe43cf2db2453b6ef860b594`;
- exact-head PR CI `32046970220`: PASS all five required jobs;
- bounded verification review: PASS with no authority widening;
- PR #61 merged as `a4534116bdd405fca42c8112271f702108456bce`;
- canonical post-merge CI `32047295992`: PASS all five required jobs on that exact `main` SHA;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **205 passed, 2 skipped, 354 subtests**, unittest **207 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS.

Decision gate: hierarchical shortlist routing, embeddings, vector databases, and extra model-routing stages remain deferred because the bounded compact-directory optimization produced a material reduction without adding architecture. Reconsider only if real provider usage evidence shows further need.

The adjacent capability identified here later advanced through issue #73 / PR #74 into bounded selective craft and then through issue #76 / PR #79 into one qualified live local neural Crew provider. Those later milestones do not rewrite the historical issue #60 qualification boundary.

Preserved invariants:

- Commander intent remains verbatim and authoritative;
- GorXu remains sole operational orchestrator;
- all 82 Standing Crew remain cognitively discoverable;
- cognition cannot create eligibility, capability, Repair authority, risk reduction, or verifier independence;
- deterministic Living Company routing remains the authority-bearing selection path;
- cache behavior and usage telemetry cannot widen authority;
- no release/tag moved and no A8 was created or implied.

## Runtime Integrity Repairs — issues #63 and #64

**Issue #63 status: COMPLETE — CANONICAL POST-MERGE VERIFIED.** This bounded reliability repair is canonical on protected `main`; it is not A8 and did not move a release/tag.

Implemented:

1. post-Repair verification timeout now enters the same evidence-bearing rollback path as a nonzero verification result;
2. explicitly authorized Mission Graph Repair remains on the Pilot scheduler thread so Pilot-owned SQLite mutation journaling does not cross thread affinity;
3. Vessel Health persistence readiness consumes the actual `SnapshotReport.manifest` / `errors` contract for valid and invalid snapshot-present paths;
4. permanent regressions cover timeout rollback, authorized Graph Repair, valid snapshot readiness, and invalid snapshot readiness.

Qualification evidence:

- sandbox red baseline: canonical `main@8470a715a0bc37877013608c9daa178acfa4cbab` reproduced all three defects before repair;
- corrected implementation head: `9c4c014292d890cfa22e97fd2a6b4607ce74d6dd`;
- exact-head PR CI `32075807852`: PASS all five required jobs after one transient A5 Docker-probe rerun on unchanged source;
- PR #65 merged as `ccd26f2b7eed0804338667fc9e13190c5e9d389e`;
- canonical post-merge CI `32076103017`: PASS all five required jobs on that exact `main` SHA;
- Python 3.12 canonical post-merge evidence: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **209 passed, 2 skipped, 354 subtests**, unittest **211 OK, 2 skipped**, critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6**, and integrated Post-Apex qualification PASS.

Preserved canary evidence: an interrupted local mutation harness temporarily carried two deliberate graph mutants into the first branch candidate. Static PR inspection caught both before merge; canonical `forged-graph-verification-filter` and `hard-cost-budget-boundary` behavior was restored, and the exact-head plus post-merge mutation suites killed both invariants again with clean source restoration.

Commander/GorXu authority, risk floors, Tool Gateway enforcement, verifier independence, source binding, 82-Crew structure, release state, and Apex-stage state are unchanged.

**Issue #64 status: COMPLETE — CANONICAL POST-MERGE VERIFIED.** Canonical doctrine distinguishes verification capability from ordinary automatic-routing eligibility. Because 16 Standing Crew are verification-capable, `verification=true` remains a verification-eligibility marker and is not reused as a verification-only role flag. A distinct `ordinary_routing` property defaults to `true` and is `false` only for `independent-verifier`. Ordinary automatic routing and cognitive preference respect that boundary; Verify routing remains unchanged; explicit GorXu `crew_id` assignment remains the separately authorized exception path described by the craft card and still passes normal Mission Order, capability, action, risk, scope, host-policy, and verification gates.

Red-before-green evidence: exact red-baseline run `32078007106` failed the three intended ordinary-routing assertions before routing code changed while Health and Wheel remained green. The implemented routing boundary then made those regressions green. A compatibility canary exposed an older durability test that counted every Order assigned to one Crew as a proxy for graph-node replay; that assertion was strengthened to bind to the committed architecture node's actual objective and persisted `order_id`, preserving the real no-replay invariant while allowing legitimate recovery consultation reuse.

Final qualification: exact-head PR CI `32078828303` passed all five required jobs on `1531f4d4f3e2a222cdef5c32b7c6b70debba35de`; PR #67 merged as canonical `main@d04d21e38ffe1645d9c9e0df61e7ca96ac465066`; exact-SHA post-merge push CI `32079205250` completed successfully on that canonical main. Python 3.12 evidence remained Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **215 passed, 2 skipped, 354 subtests**, unittest **217 OK, 2 skipped**, mutations **12/12**, **7/7**, **9/9**, **4/4**, **6/6** killed with clean restoration, and integrated Post-Apex qualification PASS.

No command layer, authority, Crew membership, release/tag, or Apex-stage change is introduced.

## Mission Outcome Truthfulness — issue #70 / PR #71

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED.** This post-release source hardening is canonical on protected `main`; it is not A8 and does not move the `v0.8.0` release tag.

Implemented:

1. single-Mission Pilot output separates `execution_status` from Commander-facing Mission status;
2. a persisted `mission_outcome` contract records execution, actual effect, objective state, remaining mutation state, next required authority, and verification scope;
3. generic Execute inventory fallback reports `status: scan_only`, `objective: not_delivered`, and no mutation instead of plain objective-like completion;
4. verification PASS on an unsatisfied objective is explicitly scoped to bounded execution evidence only;
5. supported explicit `repair-write` retains Repair mutation authority, objective-satisfied semantics, and independent verification;
6. failed Repair reporting is conservative: completed rollback reports no remaining mutation, while rollback failure/divergence reports `mutation_state_unresolved`, `mutation: true`, and `next_authority: pilot_recovery`.

Independent review caught the unresolved-mutation failure-state gap before merge; permanent regressions cover both failed and completed rollback outcomes.

Qualification evidence:

- final implementation head `37392878566bbe9ad84eba3b5d723a974cca5164`;
- exact-head PR CI `32127267143`: PASS all five required jobs;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **218 passed, 2 skipped, 354 subtests**, unittest **220 OK, 2 skipped**;
- critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6** killed;
- integrated Post-Apex qualification PASS with `new_apex_stage=false`, `qualification_claim=false`, and `release_decision=false`;
- PR #71 merged as `main@1409605a98e0fd805a55839321f28364505773f5`;
- the merged `main` tree SHA `fedb4d54bb2e907f6fc9ff1e0125476c6af4f587` exactly matches the final CI-qualified PR-head tree, proving source equivalence;
- issue #70 closed as completed.

No separate post-merge push run is claimed because none was observable through the available GitHub interface. Commander/GorXu authority, Repair boundaries, verifier independence, Mission Graph semantics, Crew membership, package version, published release, and Apex-stage state are unchanged.

## Selective Deep-Craft Crew Cognition — issue #73 / PR #74

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED.** This is bounded protected-main post-Apex evolution. It is not A8, does not move the `v0.8.0` release tag, and did not itself establish live model-backed Standing Crew.

Implemented:

1. Inspect-only selective specialist craft reads only the routed Standing Crew member's canonical craft card and selects at most **6 sections / 4,500 characters** by default;
2. `Purpose`, `Safety Boundaries`, and `GroX Operational Binding` must fit in full when present or craft selection fails closed;
3. complete deep craft cards are never injected by default; Verify, Repair, and Execute do not carry unused deep craft from this seam;
4. Inspect execution emits attributable `craft_selection` evidence with full-card digest, selected headings/size, source revision, and freshness policy;
5. a provider-neutral Inspect-only Crew cognition seam may consume the sealed Order envelope copy, selective craft, bounded Crew memory, and governed observations;
6. cognitive action requests are limited to already-authorized `fs_list`, `fs_read`, and `test_run` through the existing Mission Order + Tool Gateway boundary;
7. default cognitive bounds are **4 steps**, **1 test run**, **8,000 observation characters**, and **4,000 work-product characters**;
8. mutation/scope escape fails closed; known recoverable provider failure degrades only to the existing deterministic Inspect path; provider-local mutation cannot alter executor-owned context;
9. cognition/context bookkeeping is excluded from Living Company evidence-quality scoring so the seam cannot improve routing history merely by creating extra evidence kinds;
10. controlled fake-provider tests exercise the seam for single Missions and Mission Graph Inspect nodes while Verify remains independently deterministic.

Qualification evidence:

- canonical starting point `main@8ffbee2f14e0e915e721835e9e84cc2289fc9661`;
- final implementation head `db83c557e378e6e3a3471318b50e6b82a5d68641`;
- exact-head CI `32166921610` / run 232: PASS all five required jobs;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **235 passed, 2 skipped, 354 subtests**, unittest **237 OK, 2 skipped**;
- critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6** killed; integrated Post-Apex qualification PASS;
- independent exact-head review: PASS with no remaining material blocker;
- PR #74 merged as `main@8420b9cbe5ca046ded87c8feaec83eca7cfdc475` and issue #73 closed as completed;
- canonical merge tree `170bbfb9fe483b1faae362adc15ec944ca5c96c9` exactly matches the CI-tested synthetic PR merge tree, proving exact source equivalence;
- no separate post-merge push run is claimed because none was observable through the available GitHub interface.

Historical claim boundary: PR #74 qualified the **provider-neutral controlled seam** only. That historical boundary was later advanced by issue #76 / PR #79, which qualified one live locally trained neural provider. It still does not imply a general-purpose LLM, all Crew as autonomous agents, or model cognition in Repair/Verify/Execute.

## Live Local Neural Crew Cognition — issue #76 / PR #79

**Status: COMPLETE — CANONICAL MERGED AND EXACT-TREE QUALIFIED.** This is the first GroX qualification in which an actually trained local neural model occupied the bounded Standing Crew cognition seat.

Qualified provider/model:

- provider: `local-neural-session-crew-v1`;
- model: `tiny-mlp-policy-5x8x3-v1`;
- model kind: locally trained neural action-selection policy;
- architecture: **5 → 8 → 3** multilayer perceptron;
- learned parameters: **75**;
- training examples: **240**;
- held-out examples: **100**;
- initial held-out accuracy: **0.44**;
- final held-out accuracy: **1.00**;
- network required: **no**;
- external disclosure: **no**.

The model was trained by actual gradient updates in the executing Python process. Its parameter digest changed from `f5c197881e1fbdf90395bbc09d2c1ac7097691ac68101cf573c64a90b419b6b6` to `7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`.

Live inference evidence:

1. before governed evidence existed, with selected craft and bounded Crew memory present, the model selected `fs_read` with probability **0.999859**;
2. after the governed observation returned through Mission Order + Tool Gateway, it selected `finish` with probability **0.999892**;
3. the canonical provider qualification returned PASS with Inspect mode preserved, governed observation evidence, bounded work product, no cognition denial/degradation, no mutation, and independent verification PASS.

Qualification evidence:

- final implementation head: `c8be4d78f92466d3e66ec915b12dcec316396b6d`;
- exact-head CI: `32336799141` / run **252**, PASS all five required jobs;
- Python 3.12: Vessel Health **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**, pytest **252 passed, 2 skipped, 440 subtests**, unittest **254 OK, 2 skipped**;
- critical mutations **12/12**, health **7/7**, reconstitution **9/9**, operational drift **4/4**, source provenance **6/6** killed; integrated Post-Apex qualification PASS;
- PR #79 merged as `d49f43246922c6d8c5e3a632423195ffecd9f161`;
- canonical merge tree `109f7d7ddc9712e3d9eec009582025c82317794a` exactly matches the CI-tested synthetic merge tree;
- issue #76 closed completed;
- Ship's Log 0059 was later merged through PR #81.

Claim boundary: GroX has qualified **one live locally trained neural action-selection provider through the bounded Inspect Crew cognition seam**. This does not qualify a general-purpose language model, Qwen, the OpenAI Responses adapter in live operation, model cognition in Repair/Verify/Execute, or unrestricted autonomous Crew.

## Native Cognition Independence Program 001

**Status: ROADMAP AUTHORIZED — IMPLEMENTATION NOT YET QUALIFIED.** This is the new strategic direction after the first live local neural qualification. It is not A8, does not change the current release, and grants no additional authority.

North star:

> **GroX is a neural organism that becomes progressively better at operating inside GroX.**

Strategic objective:

> **GroX should own its cognition lifecycle. Native local cognition should be sufficient for a minimum offline operating condition; external models should increase capability when available but should not be required for the Vessel to exist, reconstitute, reason, or perform bounded work.**

### Program principles

1. **Native-first, not vendor-required.** GroX should boot and retain a useful cognitive operating mode without an OpenAI, Anthropic, Google, or other paid subscription.
2. **Runtime ownership above inference kernels.** GroX owns model registration, cognition placement, context, memory, training, evaluation, evolution, activation, evidence, and recovery. It may initially reuse permissively licensed inference engines or kernels rather than duplicating low-level numerical infrastructure without need.
3. **Weights are part of the Vessel, not the whole Vessel.** GorXu, Crew craft, memory, Mission history, evidence, model checkpoints, training provenance, and evaluation history collectively form the evolving cognitive organism.
4. **External intelligence is a capability.** Vendor models may be consulted through governed adapters when useful, but they inherit no GroX authority and are not the command spine.
5. **External tokens may become learning capital only when permitted.** Provider outputs may enter training/evaluation corpora only when applicable terms/license permit it, provenance is retained, and GroX verification admits the material.
6. **Verified learning only.** Unverified model output is not training truth. Candidate examples must pass appropriate evidence, Crew review, tool validation, and independent verification before durable admission where consequence warrants it.
7. **Evolution cannot self-authorize.** A candidate model cannot promote itself. Parent/child comparison, regression gates, adversarial tests, independent verification, and the ordinary Commander/GorXu authority path remain required for activation.
8. **Offline is a first-class target.** Network availability should expand capabilities, not determine whether GroX can function.

### Planned evolution sequence

#### NCI-1 — Native cognition runtime contract

Build a GroX-owned runtime layer for:

- model registry and model lineage;
- local inference-provider interface;
- hardware/runtime discovery;
- deterministic resource and context ceilings;
- GorXu versus Crew cognition placement;
- local model health/readiness evidence;
- fail-closed fallback and reconstitution.

Exit evidence: GroX can load and execute a registered local model through a native runtime contract without changing command authority.

#### NCI-2 — Built-in local seed cognition

Package a practical local cognitive baseline with the Vessel. The initial language-capable seed may use permissively licensed open weights while the existing GroX-trained neural policy remains the first native learned component.

Requirements:

- license/provenance recorded;
- model artifact integrity verified;
- CPU-first minimum profile defined;
- optional GPU acceleration supported without becoming mandatory;
- no hidden network dependency;
- deterministic fallback retained.

Exit evidence: fresh GroX installation can perform a bounded local cognitive Mission without a vendor credential or network call.

#### NCI-3 — Offline GorXu cognition

Move GorXu from vendor/session-required cognition toward a native local reasoning path while keeping the deterministic authority plane unchanged.

Exit evidence: an offline high-risk Inspect Mission can be interpreted, routed, executed, synthesized, and independently verified with local cognition only under a defined minimum hardware profile.

#### NCI-4 — Neural Crew evolution

Evolve the local Crew policy beyond the 75-parameter seed toward richer Mission-state cognition: action selection, path choice, evidence sufficiency, test interpretation, confidence, stop/continue decisions, and failure triage.

Each generation records:

- parent generation;
- architecture and parameter count;
- training corpus and provenance digest;
- training configuration;
- pre/post model digests;
- benchmark results;
- regressions;
- accepted/rejected disposition;
- qualification status.

Larger is not automatically better. A descendant that regresses on safety, authority compliance, generalization, cost, reliability, or maintainability is rejected even if another metric improves.

#### NCI-5 — Mission learning corpus and evolution registry

Turn verified GroX operating experience into structured learning material:

- Commander intent and bounded task class;
- assigned Crew and selected craft;
- bounded memory;
- action/observation trajectory;
- tool evidence;
- verification result;
- Mission outcome;
- failure/recovery path;
- source and licensing/provenance metadata.

Private or sensitive material remains governed by existing persistence/disclosure boundaries and is not automatically admitted into model training.

#### NCI-6 — Optional external teacher/tool adapters

Treat external models as governed intelligence capabilities that can help with difficult or novel work, cross-check local reasoning, generate candidate approaches, or—where terms permit—provide candidate teaching material.

GorXu decides whether external intelligence is worth using based on Mission need, risk, confidence, cost, privacy, connectivity, and policy. External providers never become the default authority source merely because they are more capable.

#### NCI-7 — Governed model evolution and promotion

Create parent-versus-descendant evaluation with preserved red evidence and explicit activation gates.

Required dimensions include:

- task success/generalization;
- authority compliance;
- mutation discipline;
- evidence quality;
- verifier independence;
- prompt/instruction injection resistance;
- latency/resource use;
- offline behavior;
- recovery compatibility;
- regression against Apex and Post-Apex invariants.

A trained candidate remains a candidate until governed activation.

#### NCI-8 — Offline Vessel qualification

Prove a defined offline operating profile with no paid subscription, no external API credential, and no network requirement for the qualified Mission set.

The target qualification should cover:

- Vessel reconstitution;
- GorXu cognition;
- Crew selection;
- at least one model-backed Crew tour;
- local tools/evidence;
- independent verification;
- durable state;
- bounded recovery/failure behavior.

Offline qualification does not forbid connected operation. It establishes the minimum condition under which GroX remains an intelligent Vessel on its own.

#### NCI-9 — Connected and augmented operation

After offline capability is proven, connected GroX may use web/network tools, remote compute, and external models as optional capability multipliers. The authority model remains identical across offline, connected, and augmented operation.

### Deliberately not implied

This roadmap does not claim:

- that GroX already has a complete native language model;
- that the 75-parameter policy is a general-purpose model;
- that GroX will pretrain a frontier foundation model from random weights as the first step;
- that permissively licensed seed weights become GroX authority merely by being bundled;
- that low-level inference kernels must be reimplemented before useful native cognition can ship;
- that all 82 Crew become continuously running autonomous model processes;
- that vendor models are forbidden;
- that model evolution may activate itself;
- that a new Apex stage or A8 exists.

## Post-Apex operating posture

There is no predeclared A8. **Post-Apex Operational Evolution Program 001 is complete and canonical.** `v0.8.0` is published from the verified Program 001 baseline. Later protected-main hardening and evolution—including Mission Outcome Truthfulness, Selective Deep-Craft Crew Cognition, and the live local neural Crew qualification—remain source evolution beyond the immutable release and do not themselves create a new Apex stage or release.

The current strategic program is **Native Cognition Independence Program 001**. Its roadmap is authorized by Commander intent, but its implementation stages must each earn their own evidence. No roadmap item inherits qualification merely because it is listed here.

Other known deliberate limits remain candidates, not automatic commitments: autonomous memory consolidation, generic external-system compensation, unrestricted interactive desktop actuation, broader/networked MCP, and optional external-agent interoperability.

## Post-Apex Operational Evolution Program 001

Canonical plan: `docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md`

1. **#29 — External capability intake convention: COMPLETE.** Four-posture `ADOPT | ADAPT | HARVEST | REJECT` review convention is canonical and exercised against pinned ClaudX evidence.
2. **#25 — Critical detector mutation proving: COMPLETE.** Red run `31950179712` preserved ambiguous-target fail-closed behavior; green run `31950265325` killed 12/12 critical mutations; final Stage 1 exact-head CI also passed all five gates.
3. **#26 — Native Vessel health surface: COMPLETE.** `grox health` is read-only and isolated. Preserved red runs `31950827151`, `31951286406`, and `31951491116` exposed test-fixture, smoke-order, and ignore-policy weaknesses without weakening health. Final exact-head run `31951586094` passed; PR #35 merged as `7209fa9cf3f5d2cf2cd9d1df840c91ea946c544c`; post-merge run `31951678763` passed.
4. **#27 — Tiered reconstitution: COMPLETE.** FAST/TARGETED/FULL planning consumes Vessel Health rather than duplicating truth. Red run `31951963722` revealed redundant protection rather than unsafe behavior. Green run `31952132782` passed health/reconstitution smokes, pytest **158 passed, 2 skipped, 19 subtests**, unittest **160 OK, 2 skipped**, Stage 1 **12/12**, Stage 2 **7/7**, Stage 3 **9/9** mutations killed, zero survivors, clean restoration, and all five CI jobs. PR #36 completed through the protected merge path.
5. **#30 — Context heat and bounded compression experiment: COMPLETE (CONTROLLED).** HOT/WARM/COLD policy preserved 100% of declared critical facts and retained provenance across four representative scenarios while reducing 20,464 characters to 1,336 (93.47%). Decision: HARVEST the bounded policy as a GroX technique; do not activate automatic Pilot compression until integrated operational evidence supports it. ClaudX's synthetic 57.4% figure was not used as proof or target.
6. **#28 — A6 longitudinal operational drift analysis: COMPLETE.** Digest-bound operational windows, `STABLE | WATCH | REGRESSION | UNKNOWN`, first-class critical invariants, operational Mission degradation proof, and 4/4 continuous detector mutations passed without self-normalization or self-activation.
7. **#31 — Mission-to-source provenance research: COMPLETE.** Decision **ADAPT**: use a private nonce-bound authorization receipt, public opaque commitment, structural-only public CI, and independent private witness verification; optional GitHub/Sigstore attestation remains deferred hardening rather than the authority record.
8. **#45 — Bounded provenance implementation: COMPLETE.** Private receipts require existing Repair/mutation authority and bounded source scope; public commitments remain privacy-minimized; exact-head verification, replay/class-downgrade defenses, missing-witness UNKNOWN semantics, and 6/6 continuous detector mutations passed.
9. **Integrated operational qualification: COMPLETE — CANONICAL POST-MERGE PASS.** The composed health/reconstitution/context/A6/intake/provenance gate passed with no authority widening; PR #53 received two exact-head bounded PASS reviews, merged as `4122845858fae6abdf52af7a3a1ce56256e0c5cf`, and canonical post-merge run `32010172588` passed all five jobs.

## Standing exclusions

Do not:

- re-import GroX-derived ClaudX architecture as external novelty;
- add a duplicate decisions ledger;
- import host-specific `launchd` architecture;
- retain non-standing Crew as sleeping operational identities;
- remove `orchestration-evaluation-analyst` based only on ClaudX naming decisions;
- treat ClaudX synthetic token-savings as GroX proof;
- let health, reconstitution, context heat, evaluation, telemetry, provenance, craft, cognition, model confidence, or training score grant mutation authority;
- let craft/cognition bookkeeping improve Living Company routing history merely by adding evidence kinds;
- claim broader model capability than the exact qualification evidence supports;
- let a newly trained model promote or activate itself;
- admit vendor/model output into training truth without provenance, applicable rights/terms, and required verification;
- make network access or a paid model subscription a prerequisite for the target minimum offline operating condition.

## Release posture

Post-Apex Evolution Program 001 qualification is complete, canonical, and post-merge verified. `v0.8.0` is published from `27da3cbbe60fb53e88af325baeb3fbb3b4adbfeb` after exact-head candidate CI `32014558365` and canonical post-merge CI `32015076306` passed. Issue #55 is complete. Canonical source has since advanced through protected-main hardening and bounded post-Apex evolution without moving the immutable release tag. Native Cognition Independence Program 001 is a new strategic roadmap and does not itself make a release decision. Future release or evolution decisions remain Commander-controlled. No new Apex stage or A8 is implied.