# Ship's Log 0044 — Context Heat Experiment Passed

**Date:** 2026-08-16

**Program:** Post-Apex Operational Evolution Program 001

**Stage:** 4 — Context heat and bounded compression experiment

**Issue:** #30

## Commander intent

The Commander approved testing the useful hot/warm/cold context-management principle identified during the ClaudX comparative review, but explicitly rejected ClaudX's synthetic 57.4% token-savings result as GroX proof. GroX had to establish its own evidence and preserve Commander intent, authority, unresolved critical evidence, provenance, and outcome-critical facts.

## Controlled implementation

`src/grox/context_heat.py` defines an experimental, deterministic `ContextHeatPolicy` that is **not wired into Pilot runtime**.

- HOT material is retained verbatim.
- Relevant WARM material may use only a caller-supplied attributable summary; without one, raw text remains.
- COLD re-derivable or superseded material may be omitted.
- Critical material remains HOT regardless of age.
- Every retained item keeps provenance.

The policy is exercised by unit tests and `tests/experiments/context_heat_experiment.py` on the protected Python 3.12 CI path.

## Evidence

The controlled corpus covers:

- a long-running Mission with active intent, Inspect-only authority, graph state, contradiction, next action, Crew findings, and obsolete raw output;
- a reconstitution case containing an old but still binding unrelated-source restore safety rule;
- an adversarial case where an old privacy rule competes with newer noise;
- relevant WARM material with no safe summary, which must remain raw.

Deterministic corpus result:

- original characters: **20,464**;
- packed characters: **1,336**;
- controlled character reduction: **93.47%**;
- required critical facts retained: **100%**;
- retained-item provenance present: **100%**.

Scenario reductions ranged from **70.82%** to **97.90%** while preserving all declared critical facts.

The CI experiment gate requires at least 50% aggregate character reduction plus complete required-fact/provenance preservation. That threshold is an internal controlled-experiment criterion, not an external benchmark or production token target.

## Decision

**HARVEST** the bounded HOT/WARM/COLD policy as an evidence-supported GroX design technique.

Do not activate automatic Pilot runtime compression from this controlled experiment alone. The corpus proves the bounded policy can work on these representative cases, not that arbitrary Mission context can be safely summarized without further operational evidence.

The integrated post-evolution Mission must test the technique against real program evidence before any runtime activation decision.

## Non-claims

GroX does not claim:

- 93.47% production token savings;
- production latency improvement;
- arbitrary semantic-equivalence guarantees;
- permission to cool information merely because it is old;
- safe model-generated summaries by default.

Old safety- or authority-critical evidence remains protected regardless of age.

## Program transition

Stage 4 controlled experiment is complete.

The next authorized workstream is **Stage 5 / issue #28: extend A6 with longitudinal operational drift analysis using protected baselines and real attributable trajectory evidence**.
