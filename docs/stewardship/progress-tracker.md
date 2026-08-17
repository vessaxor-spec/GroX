# GroX Progress Tracker

**Status date:** 2026-08-17
**Canonical release:** `v0.7.1`
**Canonical source branch:** `main`
**Current source package:** `0.7.1`
**Current released source:** `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`
**First Apex-qualified release:** `v0.7.0@71ffd60769d81b5b249dac4eca56333ff27e26d0`
**Apex qualification merge:** `419cc73950f573c3e201106f7949c6bf7829f2af`
**Current operating verdict:** **APEX QUALIFIED — OPERATIONAL AUDIT 001 CLOSED**
**Standing Crew:** **82**
**Current verified regression:** pytest **202 passed, 2 skipped, 354 subtests**; unittest **204 OK, 2 skipped**

## Verified Vessel baseline

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified by source, qualification evidence, and automated testing:

- GroX-native command architecture implemented
- Commander Seat CLI and interactive bridge live
- Pilot GorXu is the sole operational orchestrator
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
- Vessel-root discovery now supports explicit `GROX_VESSEL_ROOT` binding, current-checkout discovery, editable-source fallback, and fail-closed refusal to construct an unbound 0-Crew Vessel
- package/source version metadata is synchronized at `0.7.1` and guarded by both pytest and unittest
- release `v0.7.1` is pinned to the fully verified post-Apex operational-hardening source commit `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`

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

Integrated Post-Apex Evolution Program 001 qualification has passed independent review; protected merge finalization remains before canonical closure.

## Post-Apex Evolution Program 001 — Integrated qualification

**Status: COMPLETE — INDEPENDENT PASS; PROTECTED MERGE PENDING**

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

The experiment deliberately emits `qualification_claim=false`, `release_decision=false`, and `new_apex_stage=false`; the experiment did not self-certify. Independent review on PR #53 recorded PASS against exact candidate head `5c58392a0b9f8fb80f085128588167712003f283` after run `32009679294`. These closeout edits require a new exact-head CI/review cycle before protected merge. Any later release remains a Commander decision.

Evidence: `docs/verification/POST_APEX_EVOLUTION_001_INTEGRATION_EVIDENCE.md`.

## Known deliberate limits

- GorXu cognition is project-hosted through GPT-5.6 Sol when a capable Space Exploration session is active; deterministic control remains the safe fallback when cognition is unavailable.
- A3 episodic retrieval plus attributable semantic, procedural, and Vessel-wide memory are live with bounded selective retrieval; autonomous consolidation remains future evolution.
- A4 durable Mission Graph resume, checkpointing, bounded cancellation/retry, and text-Repair compensation are live; generic compensation for arbitrary external systems remains intentionally unclaimed.
- A5 qualifies bounded workspace shell/code execution, memory-only secret aliases, exact-origin read-only HTTP(S), offline browser evidence capture, and pre-registered stdio MCP. Unrestricted interactive desktop control, arbitrary/networked MCP processes, runtime image pulls/builds, and optional A2A delegation remain outside the qualified boundary.
- A5 isolation fails closed when neither the preferred namespace backend nor the host-commissioned Docker fallback is available.

## Apex Orchestrator readiness

**Current status: APEX QUALIFIED**

The initial self-assessment Mission `MSN-354de0550dd5` established the baseline gaps. Since then A1 Cognitive Pilot, A2 Mission Graph Orchestration, A3 Living Company Intelligence, A4 Executive Exception Loop and Durable Operations, A5 Governed Capability Expansion, and A6 Orchestration Intelligence and Self-Improvement have qualified. GorXu now has project-hosted cognition, durable dependency-aware multi-Crew graphs, attributable organizational memory, experienced routing, bounded selective memory, same-Mission crash recovery, checkpointed execution, bounded executive consultation/replanning, cancellation, journaled text-Repair compensation, governed multi-tool execution through Tool Gateway v2, and replayable evidence-backed orchestration evaluation whose proposals cannot self-activate.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`.

Apex critical path: **COMPLETE**. A1 through A7 are qualified; future changes must preserve the qualification invariants rather than inherit Apex automatically.

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

**A1 status: SESSION-QUALIFIED.** A capable ChatGPT GPT-5.6 Sol project session may act as GorXu's cognitive provider. No API key, OAuth flow, or vendor CLI is required for this operating mode. If the hosting session is unavailable, GorXu degrades to the deterministic control plane rather than widening authority.

A1 exit gate is closed; the current Apex stage is tracked below.

## Persistence foundation

**Status: LOCKED AND IMPLEMENTED**

- cognitive continuity home: ChatGPT project `Space Exploration`;
- Pilot identity: GorXu; preferred reasoning runtime: GPT-5.6 Sol / high reasoning;
- durable Vessel source home: `vessaxor-spec/GroX`;
- operational state remains private and outside public Git;
- `.groxstate` snapshot creation, SHA-256 verification, SQLite integrity checking, and confirmation-gated restore implemented;
- restore creates a pre-restore checkpoint;
- `configs/persistence/project-binding.json` records the active persistence bindings;
- automated suite: **31 tests passing** after persistence-plane implementation.

The sandbox is explicitly classified as a replaceable flight computer rather than the Vessel's permanent home. The persistence foundation is closed. The Apex critical path is complete; future evolution must preserve the qualified Apex invariants.

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

A6 does not grant proposals authority to mutate the Vessel. Accepted future improvements must still traverse the ordinary GroX authority path with explicit mutation authority and required verification.

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
- current release `v0.7.1` is pinned to `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2` and canonical source continues on protected `main`;
- the released company remains **82 Standing Crew**;
- A1 through A7 remain qualified;
- future evolution must re-prove affected Apex invariants rather than silently inheriting qualification;
- no A8 is currently defined: operational Mission evidence should determine the next evolution.
