# GroX Progress Tracker

**Status date:** 2026-08-14

## Verified Vessel baseline

**Operational bootstrap and full-company recruitment: COMPLETE**

Verified by source, qualification evidence, and automated testing:

- GroX-native command architecture implemented
- Commander Seat CLI and interactive bridge live
- Pilot GorXu is the sole operational orchestrator
- Mission Control operates as a native advisory/policy subsystem under GorXu
- 81 specialist-inspired Standing Crew recruited as native GroX identities
- 1 native independent verifier retained, for 82 total standing dossiers
- former bootstrap `systems-architect` overlap replaced by the canonical `architect` Crew
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
- 65 automated contract/unit/integration tests passing
- live Inspect Mission completed successfully
- live medium-risk Repair Mission completed with independent verification

## Company state

- Total standing dossiers: **82**
- Specialist-inspired Crew: **81**
- Native support Crew: **1 independent verifier**
- Verification-capable Crew: **16**
- Duplicate Crew IDs: **0**
- Recruited command/orchestrator roles: **0**

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

The complete Git-tracked live Vessel source is synchronized to `vessaxor-spec/GroX` on `main`. Private SQLite and `.groxstate` operational state remain outside public Git by design. Historical private state may contain retired Crew identities that are not part of the active source-defined company.

## Known deliberate limits

- GorXu cognition is project-hosted through GPT-5.6 Sol when a capable Space Exploration session is active; deterministic control remains the safe fallback when cognition is unavailable.
- A3 episodic retrieval plus attributable semantic, procedural, and Vessel-wide memory are live with bounded selective retrieval; autonomous consolidation remains future evolution.
- A4 durable Mission Graph resume, checkpointing, bounded cancellation/retry, and text-Repair compensation are live; generic compensation for arbitrary external systems remains intentionally unclaimed.
- A5 qualifies bounded workspace shell/code execution, memory-only secret aliases, exact-origin read-only HTTP(S), offline browser evidence capture, and pre-registered stdio MCP. Unrestricted interactive desktop control, arbitrary/networked MCP processes, runtime image pulls/builds, and optional A2A delegation remain outside the qualified boundary.
- A5 isolation fails closed when neither the preferred namespace backend nor the host-commissioned Docker fallback is available.

## Apex Orchestrator readiness

**Current status: NOT YET APEX**

The initial self-assessment Mission `MSN-354de0550dd5` established the baseline gaps. Since then A1 Cognitive Pilot, A2 Mission Graph Orchestration, A3 Living Company Intelligence, A4 Executive Exception Loop and Durable Operations, and A5 Governed Capability Expansion have qualified. GorXu now has project-hosted cognition, durable dependency-aware multi-Crew graphs, attributable organizational memory, experienced routing, bounded selective memory, same-Mission crash recovery, checkpointed execution, bounded executive consultation/replanning, cancellation, journaled text-Repair compensation, and governed multi-tool execution through Tool Gateway v2.

The canonical evolution path is recorded in `docs/stewardship/APEX_ORCHESTRATOR_PLAN.md`.

Current critical path: **A6 - Orchestration Intelligence and Self-Improvement**. GorXu remains **NOT YET APEX** until A6 and the final A7 gauntlet pass.

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

The sandbox is explicitly classified as a replaceable flight computer rather than the Vessel's permanent home. The persistence foundation is closed; the current Apex critical path is A6 Orchestration Intelligence and Self-Improvement.

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
- active source-defined company remains 82 Standing Crew; a retired historical `systems-architect` row in private state does not re-enter the active company;
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

Current Apex stage: **A6 - Orchestration Intelligence and Self-Improvement**.
