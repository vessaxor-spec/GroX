# GroX Context Heat Experiment

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 4 — Context heat and bounded compression

**Issue:** #30

**Runtime activation:** NO

## Question

Can GroX reduce long-horizon Mission and reconstitution context load by classifying material as HOT, WARM, or COLD while preserving Commander intent, hard constraints, authority, active state, unresolved contradictions, safety-critical historical facts, provenance, and next action?

This experiment evaluates that question without changing Pilot runtime.

## Policy under test

The experimental `ContextHeatPolicy` in `src/grox/context_heat.py` is deterministic.

### HOT

HOT material is retained verbatim. The policy treats active/currently binding material as HOT, including:

- Commander intent;
- Commander constraints;
- authority;
- active Mission state;
- active graph state;
- unresolved exceptions;
- unresolved contradictions;
- critical evidence;
- safety boundaries;
- next action.

Any item marked critical remains HOT regardless of age. Age alone can never cool a currently binding safety or authority fact.

### WARM

Relevant decisions, Crew findings, retrieved memory, completed-node summaries, relevant history, and verification summaries may be WARM.

WARM material may use a shorter representation only when the source item already carries an attributable summary. If no safe summary exists, raw text is retained. The experiment does not ask a model to invent a summary and then assume it is equivalent.

### COLD

Re-derivable raw output, superseded discussion, and material that is neither active, critical, nor currently relevant may be omitted from the packed context.

Every retained item keeps provenance.

## Controlled scenarios

The CI experiment in `tests/experiments/context_heat_experiment.py` runs four representative scenarios:

1. **Long Mission** — active intent, Inspect-only authority, graph state, unresolved contradiction, next action, two relevant Crew findings, old raw output, and superseded discussion.
2. **Reconstitution** — safe-state resume intent, an old but still binding unrelated-source restore prohibition, current source evidence, recovery authority boundary, a recent decision, historical regression output, and old re-derivable source material.
3. **Adversarial old safety fact** — deliberately places an old privacy/safety rule beside newer but re-derivable noise to prove recency cannot displace safety importance.
4. **Warm material without a safe summary** — proves relevant WARM content remains raw when no attributable summary exists.

For every scenario the experiment declares the facts that must survive packing and independently audits their presence afterward.

## Measured controlled result

The deterministic corpus contains **20,464 source characters** and packs to **1,336 characters**, a controlled character reduction of **93.47%**.

Scenario results:

| Scenario | Original chars | Packed chars | Character reduction |
|---|---:|---:|---:|
| Long Mission | 6,778 | 343 | 94.94% |
| Reconstitution | 6,420 | 267 | 95.84% |
| Adversarial old safety | 5,148 | 108 | 97.90% |
| Warm without safe summary | 2,118 | 618 | 70.82% |
| **Aggregate** | **20,464** | **1,336** | **93.47%** |

Across all four scenarios:

- declared required-fact preservation: **100%**;
- retained-item provenance: **100%**;
- old critical safety facts: retained verbatim;
- unresolved contradiction: retained verbatim;
- active Commander intent/authority/state: retained verbatim;
- WARM material without a safe summary: retained raw;
- COLD re-derivable/superseded material: omitted.

The exact processing-time observation is recorded by CI for diagnostic purposes, but this corpus is too small for nanosecond timing to support a meaningful production latency claim.

## Interpretation

The experiment supports the **HARVEST** decision for the context-heat principle and validates the current bounded design constraints as a useful GroX-native technique.

It does **not** establish that Pilot runtime should immediately adopt automatic context compression. The controlled scenarios are representative but still synthetic and deliberately structured. They prove that the policy can preserve declared critical facts under these cases; they do not prove semantic equivalence for arbitrary future Mission content.

Therefore:

- HOT/WARM/COLD classification is retained as an evidence-supported design technique;
- active intent, authority, unresolved contradictions, critical evidence, safety boundaries, and next action must remain non-compressible HOT material;
- WARM compression requires attributable summaries and must fall back to raw text when a safe summary is absent;
- COLD omission is limited to material that is genuinely re-derivable, superseded, or irrelevant to current authority/outcome;
- runtime activation remains **deferred to integrated operational evidence**, not self-authorized by this experiment.

## What is not claimed

This result is **not**:

- a 93.47% production token saving;
- a production latency reduction;
- an arbitrary semantic-compression guarantee;
- permission to discard old information by age;
- evidence that model-generated summaries are safe by default;
- authority to alter Pilot context assembly automatically.

The ClaudX-reported 57.4% synthetic token reduction was not used as a target, baseline, or proof. GroX measured its own deterministic controlled corpus and reports character reduction only.

## Relationship to Stage 3 and later work

Stage 3 proved that FAST reconstitution can structurally avoid six of ten evidence-loading surfaces when current health is positively known. Stage 4 now shows that, within loaded surfaces, a bounded heat policy can remove large re-derivable/superseded payloads in controlled scenarios without dropping declared critical facts.

These are separate evidence layers:

- Stage 3: **which surfaces must be loaded**;
- Stage 4: **how material within a loaded surface may be retained, summarized, or omitted**.

Stage 5 A6 longitudinal analysis remains separate again: it evaluates operational trajectories over time and must not use context-heat compression to hide invariant failures.

## Exit decision

**Stage 4 controlled experiment: PASSED.**

**Decision:** HARVEST the bounded HOT/WARM/COLD policy as a GroX design technique; defer Pilot runtime activation until the program's integrated operational Mission can test it against real post-evolution evidence.
