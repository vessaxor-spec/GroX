# Ornith-Inspired NCI-4 Research Finding

**Status:** RESEARCH FINDING ONLY  
**Disposition:** HARVEST / ADAPT candidates for later NCI-4 design  
**Implementation authority:** NONE  
**Roadmap effect:** NONE  

## Purpose

Record potentially useful techniques observed in Ornith-1.0 / Ornith-1.5 for later consideration during **NCI-4 — Neural Crew evolution**.

This document is deliberately non-operative. It does not authorize implementation, change the NCI sequence, alter the current Live Environment Awareness program, modify routing/fallback behavior, create a new command layer, or qualify any capability.

GroX remains governed by its existing native architecture:

**Commander → Pilot GorXu → Divisions → Standing Crew**

Pilot GorXu remains the sole operational orchestrator. Any future learning or evolutionary mechanism must remain subordinate to Commander intent, existing Mission authority, Tool Gateway controls, evidence requirements, verification policy, and GroX's Prime Function as the Commander's persistent AI personal assistant.

## External inspiration

Ornith explores an agentic reinforcement-learning loop in which the system can improve not only solution behavior but also the tasks used for training and the scaffold used to solve them.

The relevant conceptual loop is:

```text
generate task
    ↓
generate / refine scaffold
    ↓
attempt solution
    ↓
evaluate trajectory
    ↓
learn
    ↓
generate a new frontier task
```

Ornith-1.5 emphasizes task generation near the current capability frontier, using validity/verifiability, difficulty, and novelty to produce useful learning pressure rather than repeatedly solving already-mastered work.

Ornith also treats the scaffold as mutable. Instructions, decomposition strategy, tool-use strategy, and orchestration technique may improve while the outer execution/trust boundary remains controlled. Ornith-1.0 additionally describes staleness handling for asynchronously collected trajectories so experience produced by older policies does not remain equally influential indefinitely.

These observations are external research inputs only. They are not evidence that the same mechanisms will improve GroX.

## GroX relevance

### 1. Frontier qualification Missions

NCI-4 currently targets richer Mission-state cognition including action selection, path choice, evidence sufficiency, test interpretation, confidence, stop/continue decisions, and failure triage.

A later NCI-4 design could investigate controlled synthetic qualification Missions positioned near the current competence boundary instead of relying only on a permanently fixed corpus.

Conceptually:

```text
current behavior becomes reliably successful
    ↓
learning value decreases
    ↓
generate a harder but verifiable bounded variation
    ↓
run controlled attempts
    ↓
measure success / failure frontier
    ↓
retain attributable learning evidence
```

Such work would need to remain explicitly separated from Commander operational Missions. Generated training/evaluation work must not manufacture operational authority or self-activation rights.

### 2. Evolve competence, never authority

The strongest architectural fit is the separation between a mutable problem-solving strategy and an immutable governed authority boundary.

Potentially evolvable surfaces:

- task decomposition;
- evidence-gathering sequence;
- permitted-tool sequencing;
- search strategy;
- recovery strategy;
- context and memory retrieval strategy;
- test interpretation;
- stop/continue heuristics;
- failure triage;
- Crew procedural playbooks.

Non-evolvable authority surfaces include:

- Commander intent;
- Mission authority;
- sealed Mission Orders;
- Tool Gateway policy;
- deterministic authority/risk floors;
- verification requirements;
- Crew organizational identity and rank;
- escalation requirements;
- GroX Prime Function;
- GorXu's position as sole operational orchestrator.

Learning may improve how authorized work is performed. It must never decide that existing authority controls are inconvenient and therefore optional.

### 3. Mission Scaffold candidate concept

A later NCI-4 design may investigate whether a **Mission Scaffold** is useful as a first-class competence/evidence object.

A scaffold could describe a bounded method for approaching a class of authorized work, for example:

```text
Mission Scaffold
├── decomposition strategy
├── preferred evidence sequence
├── allowed-tool ordering
├── recovery branches
├── test strategy
├── context / memory retrieval strategy
├── stop conditions
└── provenance + performance history
```

This would not be a command object and would carry no authority. GorXu could select or permit experimentation with a scaffold only inside an already-valid Mission authority envelope.

The research question is whether procedural evolution can improve Crew performance without mutating GroX's command architecture or deterministic authority plane.

### 4. Learn from failure trajectories

NCI-4 should consider whether verified unsuccessful trajectories can provide structured learning evidence rather than being retained only as generic failure outcomes.

Potential classifications include:

```text
PASS
→ what behavior contributed to success?

PARTIAL
→ where did the trajectory diverge?

FAIL
→ capability gap?
→ Crew mismatch?
→ scaffold weakness?
→ evidence insufficiency?
→ cognition weakness?
→ environmental failure?

BLOCKED
→ missing capability?
→ authority boundary?
→ dependency unavailable?
```

Any future use must distinguish causal evidence from speculation. A failed Mission does not itself prove which component caused the failure.

### 5. Trajectory freshness

Ornith's treatment of stale experience suggests a useful GroX research direction.

Historical Mission experience may have been produced under a different:

- source revision;
- Crew dossier or craft revision;
- cognition resource/model;
- scaffold revision;
- Tool Gateway policy;
- host/runtime environment;
- available capability set.

Therefore a future learning system should investigate whether trajectories require explicit validity/freshness metadata, potentially including:

```text
TrajectoryValidity
├── source revision
├── Crew dossier / craft revision
├── cognition execution identity
├── scaffold revision
├── tool-policy revision
├── environment evidence / fingerprint
├── generation timestamp
└── freshness state
```

Possible states for investigation:

- **CURRENT** — strongly representative of the present system;
- **STALE** — potentially informative but requiring reduced confidence/weight;
- **INVALIDATED** — historical evidence only and unsuitable for current learning decisions.

GroX already has source provenance, longitudinal operational drift analysis, cognition execution identity, and Live Environment Awareness concepts that may eventually provide stronger evidence for such classification. This finding does not authorize composing those systems yet.

## Tool and capability boundary

Ornith-style scaffold evolution must not be interpreted as permission for GroX to generate or install arbitrary executable capabilities.

A future system may potentially learn that one already-authorized tool sequence performs better than another. Discovery that a missing capability would improve performance is instead a capability requirement/proposal and must remain subject to GroX's existing intake, qualification, authority, security, and verification controls.

**Tool composition may evolve. Tool authority may not.**

## Candidate GroX-native experimental loop

For later NCI-4 design consideration only:

```text
Commander objectives / verified operational evidence
                    │
                    ▼
             bounded research corpus
                    │
                    ▼
        generate controlled challenge
                    │
                    ▼
          validate + isolate challenge
                    │
                    ▼
        generate / refine competence scaffold
                    │
                    ▼
           controlled Crew rollouts
                    │
                    ▼
          independent evaluation
                    │
          ┌─────────┴─────────┐
          │                   │
       failure              success
          │                   │
          └─────────┬─────────┘
                    ▼
         attributable learning evidence
                    │
                    ▼
            candidate evolution
                    │
                    ▼
       qualification + regression proof
                    │
                    ▼
     eligible future cognition capability
```

If an isolated training/evaluation environment is later required, it should remain infrastructure beneath GorXu rather than becoming a Division, command peer, alternate orchestrator, or authority source.

## Reward / evaluation implication

A direct copy of an external reward equation would be inappropriate.

Any GroX-native NCI-4 evaluation should first preserve hard validity gates such as:

- authority preserved;
- task objectively verifiable where required;
- evidence/provenance valid;
- evaluation harness trustworthy;
- no reward-hacking boundary violation;
- no critical invariant violation.

A candidate violating a hard authority or safety invariant should be **invalid**, not merely assigned a lower aggregate reward.

Only candidates passing those gates should be compared on softer performance dimensions such as:

- objective success;
- evidence quality;
- robustness;
- recovery quality;
- efficiency/cost/latency where relevant;
- novelty where useful;
- Commander-facing usefulness.

The exact evaluation model remains unresearched and unqualified.

## External model candidate

Ornith-1.5-9B may later be worth evaluating as a provider-neutral Crew cognition candidate if its license, artifacts, runtime requirements, provenance, and current availability remain acceptable at the time of evaluation.

This finding does **not** recommend replacing the currently qualified GroX local seed cognition and does not qualify Ornith for GroX.

A future bounded comparison could hold constant the Mission, Crew, authority, tools, and evaluation harness while comparing cognition candidates. Such a comparison would measure transfer into GroX rather than assuming that Ornith's published agentic training characteristics transfer automatically.

## Risks and open questions

Before any implementation, NCI-4 research would need to resolve at least:

1. How are generated training challenges proven valid and objectively gradable?
2. How is synthetic-task generation prevented from drifting away from Commander-useful work?
3. How are reward hacking and evaluator exploitation detected?
4. Which scaffold fields may evolve without becoming an indirect authority surface?
5. How are failed trajectories causally classified without teaching from incorrect diagnoses?
6. When does historical trajectory evidence become stale or invalid?
7. How is generated experience isolated from canonical operational memory until qualified?
8. How are candidate improvements independently regression-tested against authority, safety, usefulness, latency, cost, and maintainability?
9. Does scaffold evolution outperform simpler deterministic procedures enough to justify its complexity?
10. Does Ornith-derived cognition materially outperform GroX's existing/future cognition resources under identical GroX Missions?

## Current disposition

**HARVEST / ADAPT FOR LATER RESEARCH.**

The most promising ideas are:

1. frontier-generated controlled training/qualification challenges;
2. evolution of competence/scaffolds while authority remains immutable;
3. learning from attributable success and failure trajectories;
4. trajectory freshness tied to actual GroX execution state;
5. hard validity gates before optimization reward.

No implementation is authorized by this finding.

No roadmap restructuring is authorized by this finding.

The active Live Environment Awareness and configured-cognition fallback work remains unchanged. NCI-4 remains a later design/qualification stage according to canonical stewardship unless the Commander separately changes that direction.

## Sources reviewed

External research basis reviewed on 2026-08-30:

- Ornith-1.5 technical/project material: `https://ornith.ai/ornith_1_5.html`
- Ornith-1.0 technical/project material: `https://ornith.ai/ornith_1_0.html`
- Ornith-1.5-9B model distribution: `https://huggingface.co/ornith-ai/Ornith-1.5-9B`

GroX interpretation is deliberately separated from the external claims above. All proposed GroX concepts are research hypotheses until independently designed, implemented, tested, and qualified through the existing GroX process.