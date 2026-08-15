# GroX Roadmap

## Current position

GroX `v0.7.0` is the first released Apex-qualified Vessel baseline. It has a full 82-Crew standing company, project/session-bound GorXu cognition, private operational-state recovery, durable source synchronization to GitHub, and qualified A1/A2/A3/A4/A5/A6/A7 stages.

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

## Apex critical path

**Status: COMPLETE - APEX QUALIFIED.** `APEX_ORCHESTRATOR_PLAN.md` now serves as the regression boundary for future evolution.

Final A7 implementation evidence at `0724862dcb2634022ad33e6be14be29df6a914dd` is backed by run `31882071412` (16/16 A7; 121 pytest passed with 2 existing browser skips; 123 unittest OK with 2 skips), independent run `31882101734` (`A7_APEX_INDEPENDENT_FINDINGS=`), and synthesis-integrity run `31882083653` (`A7_APEX_SYNTHESIS_FINDINGS=`). Stewardship-final exact-head run `31882589081` re-proved the 16/16 gauntlet, both complete regression runners, both historically pinned independent canaries, version/status assertions, and diff hygiene on the final A7 candidate. PR #11 merged as `419cc73950f573c3e201106f7949c6bf7829f2af` with zero tree drift from the qualified head. Post-Apex documentation stabilization then passed run `31909761968`, and release `v0.7.0` is pinned to `71ffd60769d81b5b249dac4eca56333ff27e26d0` while canonical source continues on `main`.

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

There is no predeclared A8. The current phase is operation and evidence-driven evolution of the qualified Vessel. Real Commander Missions should produce telemetry, failures, recovery evidence, cost evidence, and operational friction that justify any next capability change.

Known deliberate limits remain candidates for future work, not automatic roadmap commitments: autonomous memory consolidation, more general external-system compensation, unrestricted interactive desktop actuation, broader/networked MCP support, and optional external-agent interoperability. Any promoted change must remain subordinate to the existing command architecture and re-prove affected Apex invariants before release.
