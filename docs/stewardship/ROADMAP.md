# GroX Roadmap

## Current position

GroX `v0.7.1` is the current released post-Apex operational-hardening baseline. `v0.7.0` remains the first released Apex-qualified Vessel baseline. The Vessel has a full 82-Crew standing company, project/session-bound GorXu cognition, private operational-state recovery, durable source synchronization to GitHub, persistent canonical CI with immutable action pinning and Python 3.11-3.14 regression coverage, portable fail-closed Vessel binding, protected canonical `main`, qualified A1/A2/A3/A4/A5/A6/A7 stages, continuous critical-invariant mutation proof, and a native read-only Vessel health surface.

The command architecture is native to the Vessel:

**Commander → Pilot GorXu → Divisions → Standing Crew**

## Completed foundation

- Native command hierarchy defined and implemented
- GorXu established as sole primary orchestrator
- Mission Control defined as a GroX-native subsystem under GorXu
- GroX Mission Order defined as the operational authority contract
- 81 specialist-inspired Standing Crew plus native independent verifier
- Inspect/Repair separation enforced
- Crew exception handling routed through GorXu
- Commander escalation threshold narrowed to critical, irreversible, or material intent-changing decisions
- Verification and evidence path implemented
- Bounded filesystem/test Tool Gateway implemented
- SQLite Mission/Order/Evidence/Crew persistence implemented
- Three-plane persistence architecture implemented
- A1 Cognitive Pilot session-qualified with GPT-5.6 Sol
- A2 Mission Graph Orchestration qualified with durable graph state, parallel-ready scheduling, bounded replanning, independent verification, and Pilot-owned synthesis
- A3 Living Company Intelligence qualified with attributable memory, per-task performance history, experienced routing, and bounded selective memory injection
- A4 Executive Exception Loop and Durable Operations qualified with same-Mission resume, committed-step preservation, bounded consultation/replan, cancellation, and journaled Repair compensation
- A5 Governed Capability Expansion qualified with Tool Gateway v2, governed isolated workspaces, memory-only secret aliases, exact-origin network access, offline browser evidence capture, and pre-registered stdio MCP adapters
- A6 Orchestration Intelligence and Self-Improvement qualified with replayable privacy-minimized Mission trajectories, deterministic invariant grading, statistically controlled routing experiments, evidence-backed advisory proposals, and explicit self-activation denial
- A7 Apex Qualification qualified with long-horizon recovery, independently verified contradiction synthesis, hard Mission cost ceilings, prompt-injection resistance, replayable evidence, and red-to-green adversarial canaries
- Post-release Operational Audit 001 completed with CI supply-chain, dependency, compatibility, and repository-governance hardening
- Canonical `main` protected by active repository rules requiring pull requests, all five canonical CI gates, strict up-to-date status, blocked deletion/non-fast-forward updates, and no bypass actors
- External capability intake convention formalized and exercised against the pinned ClaudX comparative review without adding a command layer or duplicate decision store
- Critical detector mutation proving established for 12 high-consequence restore, command-identity, stale-Crew, verification, cost, authority, escalation, bootstrap, and CI supply-chain invariants
- Native `grox health` / `grox health --json` surface added with isolated read-only command, operations, persistence, authority, memory, source, verification, environment, and recovery findings
- Seven critical Vessel-health behaviors mutation-proven continuously in the required Python 3.12 CI gate

## Apex critical path

**Status: COMPLETE - APEX QUALIFIED.** `APEX_ORCHESTRATOR_PLAN.md` now serves as the regression boundary for future evolution.

Final A7 implementation evidence at `0724862dcb2634022ad33e6be14be29df6a914dd` is backed by run `31882071412` (16/16 A7; 121 pytest passed with 2 existing browser skips; 123 unittest OK with 2 skips), independent run `31882101734` (`A7_APEX_INDEPENDENT_FINDINGS=`), and synthesis-integrity run `31882083653` (`A7_APEX_SYNTHESIS_FINDINGS=`). Stewardship-final exact-head run `31882589081` re-proved the 16/16 gauntlet, both complete regression runners, both historically pinned independent canaries, version/status assertions, and diff hygiene on the final A7 candidate. PR #11 merged as `419cc73950f573c3e201106f7949c6bf7829f2af` with zero tree drift from the qualified head. Post-Apex documentation stabilization then passed run `31909761968`; the first Apex-qualified release `v0.7.0` remains pinned to `71ffd60769d81b5b249dac4eca56333ff27e26d0`. Post-Apex operational hardening and version reconciliation are released as `v0.7.1`, pinned to `f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`, while canonical source continues on protected `main`.

## Qualified Apex stages

- **A1 Cognitive Pilot:** SESSION-QUALIFIED
- **A2 Mission Graph Orchestration:** QUALIFIED
- **A3 Living Company Intelligence:** QUALIFIED
- **A4 Executive Exception Loop and Durable Operations:** QUALIFIED
- **A5 Governed Capability Expansion:** QUALIFIED
- **A6 Orchestration Intelligence and Self-Improvement:** QUALIFIED
- **A7 Apex Qualification:** QUALIFIED

A3 qualification is backed by repeated-Mission routing adaptation and bounded memory-context evidence. A4 qualification is backed by the **55-test** Vessel suite and live private-Vessel Mission `MSN-a62e95886c0a`, which survived process interruption, resumed the same Mission without replaying committed work, resolved two ordinary Crew failures through consultation and bounded replanning, and reached independent verification PASS. A5 qualification is backed by the **65-test** fresh-host Vessel suite plus live private-Vessel Mission `MSN-5c3b646ce6be`, which completed isolated workspace, secret, exact-origin network, offline browser evidence, read-only MCP, and independent-verification nodes with no authority widening and no secret persistence. A6 qualification is backed by the **102-test** remediated Vessel suite, independent red-to-green adversarial canary, a 24-case statistically controlled routing experiment, and preserved private-Vessel Mission `MSN-f09179526ad7`, whose evaluation case `EVC-10573b245e54` replayed with trace SHA-256 `e6e0b564eee693d43f50e45fbab6dd33c9c1a0943b320f2f68e54dde5e864d5c`, zero invariants, independent verification PASS, and no secret persistence.

## Apex qualification state

- **A7 Apex Qualification Gauntlet: QUALIFIED**
- **GorXu operating standard: APEX QUALIFIED**
- Commander sovereignty, bounded authority, verifier independence, evidence integrity, recovery controls, and deny-wins execution remain mandatory boundaries.
- Apex status does not self-authorize new power; future evolution still requires ordinary GroX authority, evidence, testing, and verification.

## Persistence foundation

The three-plane persistence architecture is foundational infrastructure for every Apex stage:

- Project-bound GorXu cognitive continuity;
- GitHub-bound Vessel source;
- private, integrity-checked operational-state snapshots;
- replaceable sandbox/host compute;
- gated reconstitution before Mission resume.

## Recovery rule

A future host may resume GroX only after source materialization, private-state verification/restoration when needed, test/integrity gates, and Pilot reconstitution. Failure at a recovery gate leaves the Vessel paused rather than reconstructed from memory.

## Post-Apex operating posture

Operational Audit 001 is complete. Native Mission `MSN-ac85d2c7192c`, PR #19, and follow-on maintenance PR #23 drove bounded CI supply-chain, dependency, compatibility, and GitHub Actions hardening without creating a speculative A8 or widening authority. Repository-governance finding #18 is also closed: GitHub reports the active `Protect canonical main` ruleset targeting the default branch, requiring pull requests and all five canonical GroX CI gates with strict up-to-date enforcement, blocking deletion and non-fast-forward updates, and providing no bypass actor.

There is no predeclared A8. The current phase is operation and evidence-driven evolution of the qualified Vessel. Real Commander Missions should produce telemetry, failures, recovery evidence, cost evidence, and operational friction that justify any next capability change. The first post-Apex operational cycle proved that rule in practice: a non-editable CLI launch exposed a Vessel-root portability weakness, the documented source bootstrap completed Mission `MSN-8a86f094509b` with independent verification, and the resulting bounded hardening added persistent CI plus fail-closed portable Vessel binding without widening authority. That hardening is frozen in release `v0.7.1@f7ed57dc9dac2eb9de7857fffb743ecdf27f05f2`; canonical source now continues through the protected PR-and-CI path on `main`.

Known deliberate limits remain candidates for future work, not automatic roadmap commitments: autonomous memory consolidation, more general external-system compensation, unrestricted interactive desktop actuation, broader/networked MCP support, and optional external-agent interoperability. Any promoted change must remain subordinate to the existing command architecture and re-prove affected Apex invariants before release.

## Approved Post-Apex Operational Evolution Program 001

The Commander approved the full set of actionable findings from the ClaudX comparative review. The execution plan is canonicalized in `docs/stewardship/POST_APEX_EVOLUTION_PROGRAM_001.md`. This is an evidence-driven post-Apex program, **not A8**.

Execution tracks:

1. **#29 - External capability intake convention: COMPLETE.** `docs/stewardship/EXTERNAL_CAPABILITY_INTAKE.md` formalizes lightweight `ADOPT | ADAPT | HARVEST | REJECT` classification, evidence distinctions, authority boundaries, and a compact review record. It is exercised against the pinned ClaudX review without adding a command layer or duplicate decision store.
2. **#25 - Critical detector mutation proving: COMPLETE.** `docs/verification/CRITICAL_INVARIANT_MUTATION_MATRIX.md` records 12/12 killed mutations. Run `31950179712` is preserved as the fail-closed red harness case; run `31950265325` passed all five CI gates with pytest **133 passed, 2 skipped, 19 subtests**, unittest **135 OK, 2 skipped**, 12 killed mutations, zero survivors, and clean source restoration.
3. **#26 - Native Vessel health surface: COMPLETE.** `src/grox/health.py` and `grox health` provide a read-only isolated diagnostic surface. Run `31950827151` preserves the ineffective-test-fixture red case; run `31951084789` passed with pytest **143 passed, 2 skipped, 19 subtests**, unittest **145 OK, 2 skipped**, Stage 1 mutations 12/12 killed and Stage 2 health mutations 7/7 killed, zero survivors, and clean source restoration. The Python 3.12 CI gate also smoke-tests a source-checkout `HEALTHY` report without creating operational state.
4. **#27 - Tiered reconstitution: NEXT.** Add fast/targeted/full reconstitution selection without weakening source/state, recovery, authority, or Mission-resume gates; use the Stage 2 health evidence rather than duplicating health truth.
5. **#30 - Context heat experiment.** Test a GroX-native hot/warm/cold context model and bounded compression against long-horizon Mission/reconstitution evidence; external synthetic token-savings claims are not accepted as proof.
6. **#28 - A6 longitudinal operational drift analysis.** Extend A6 with protected-baseline trend analysis from real Mission trajectories while preserving non-self-activation and first-class invariant failures.
7. **#31 - Mission-to-source provenance research.** Threat-model a privacy-safe verifiable link between authorized private Missions and public PR/CI/merge history before any implementation decision.

Standing exclusions from the comparative review are also explicit: do not re-import GroX-derived ClaudX architecture as novelty; do not add a duplicate decisions ledger; do not import host-specific `launchd` architecture; do not retain sleeping retired Crew; do not remove `orchestration-evaluation-analyst` without GroX-native evidence; and do not treat ClaudX's synthetic 57.4% token-savings result as GroX evidence.

The program proceeds in the above dependency order. Each implementation track must recalibrate against then-current repository/runtime truth, re-prove affected Apex invariants, pass the protected five-gate CI path, and use independent verification where required. Completion of the program requires an integrated operational Mission across the changed surfaces. No version bump, release, or new qualification stage is implied until that integrated evidence exists.
