# A6 Longitudinal Operational Drift Analysis

## Purpose

GroX uses longitudinal operational drift analysis to ask one bounded question:

> Has the Vessel's observed operational behavior materially degraded relative to an explicitly selected, attributable baseline?

The answer is evidence for GorXu. It is not mutation authority.

This capability extends the existing A6 evaluation plane. It does not create another telemetry database, another source of truth, or an autonomous optimization loop.

## Authority boundary

The command relationship is unchanged:

**Commander → GorXu → Divisions → Crew**

Operational drift analysis may:

- bind existing operational trajectory cases into immutable comparison windows;
- aggregate comparable operational signals;
- classify a comparison as `STABLE`, `WATCH`, `REGRESSION`, or `UNKNOWN`;
- create an ordinary A6 advisory proposal when a regression is proven.

It may not:

- change routing weights;
- modify prompts or Crew dossiers;
- activate or retire Crew;
- write memory;
- change Mission Orders, Tool Gateway policy, risk, or verification requirements;
- alter source;
- self-activate an A6 proposal.

A proposal produced by drift analysis remains subject to the same separate GroX authority path as every other A6 proposal.

## Evidence model

### No second telemetry truth store

The analyzer consumes the existing A6 `EvaluationLedger`. Operational source cases must be trajectory cases whose provenance says `canonical_private_mission_state`.

Controlled, synthetic, benchmark, or qualification evidence is not accepted into an operational window merely because it is structurally similar.

### Frozen window binding

Each window records:

- its ordered case IDs;
- each case's digest;
- each replayed trajectory digest;
- a digest of the complete set of case bindings;
- the metric schema used for aggregation;
- the ordinary A6 run digest.

A comparison reopens and verifies those cases through the existing ledger before trusting the window. Missing, tampered, or incompatible source evidence produces `UNKNOWN` rather than silently accepting a changed baseline.

Creating an observed window never rewrites the selected baseline run.

### Freshness

An observed window has a bounded freshness requirement. If its age cannot be established or exceeds the configured bound, the comparison is `UNKNOWN`.

Baseline age by itself is not treated as failure because a historical baseline may be intentionally frozen. Its identity, source cases, and metric schema must still verify.

## First-class invariant failures

The following are not averaged into a health score:

- authority violations;
- Crew capability violations;
- verifier-independence violations;
- critical escalation violations;
- evidence-trace violations.

An observed critical violation produces `REGRESSION` regardless of otherwise healthy averages.

A proposed baseline containing a critical invariant violation or incomplete evidence trace is rejected as `UNKNOWN`. This prevents a degraded condition from becoming the new normal merely because it was observed and saved.

## Longitudinal signals

The current schema derives signals from existing Mission trajectories:

- Mission success rate;
- evidence quality;
- trace completeness;
- verification failure rate;
- cost per successful Mission;
- cost-budget pressure when an attributable Mission Graph budget exists;
- average recorded Crew latency;
- retry rate;
- exception rate;
- Pilot replan rate;
- resume/recovery rate;
- Commander escalation rate;
- tool failure rate;
- Crew utilization count;
- maximum Crew share;
- routing concentration using a Herfindahl-style concentration measure.

A signal that cannot be supported by the source evidence is left unavailable rather than fabricated. Optional metrics therefore do not become false zeroes merely to make comparison easier.

## Status semantics

### `STABLE`

No critical invariant failure and no configured watch or regression threshold crossed.

### `WATCH`

A bounded adverse movement exists below a regression threshold, or a newly measurable condition deserves observation. `WATCH` is not permission to mutate.

### `REGRESSION`

At least one critical invariant fails or a configured operational regression threshold is crossed. A regression may support an evidence-bound A6 investigation proposal, but proposal activation remains forbidden.

### `UNKNOWN`

The comparison cannot be trusted. Examples include:

- missing or tampered source cases;
- incompatible metric schema;
- non-operational provenance;
- stale observed evidence;
- incomplete case bindings;
- an invalid proposed baseline containing critical violations or incomplete trace evidence.

`UNKNOWN` never means PASS.

## Thresholds

Thresholds are explicit configuration, not learned or self-normalized by the act of evaluation. The first implementation uses conservative fixed defaults for significant success/evidence/verification changes, relative cost/latency/recovery changes, and routing concentration.

Changing those defaults is itself a future design decision and does not occur automatically from the measurements they produce.

## Operational experiment

`tests/experiments/operational_drift_experiment.py` exercises the production Mission path in a private temporary Vessel:

1. GorXu runs two successful Inspect Missions and A6 captures them as the baseline.
2. A controlled local test failure is injected.
3. GorXu runs two further Inspect Missions, which fail through the ordinary tool/test evidence path.
4. A6 captures those degraded Missions as the observed window.
5. Drift analysis must report `REGRESSION`.
6. The baseline run digest and metrics must remain unchanged.
7. Any generated proposal must remain `proposed`, and A6 activation must still raise `PermissionError`.
8. The injected test condition is restored when the experiment completes.

This establishes detection against real GroX Mission records while keeping the injected degradation isolated and reversible.

## External design evidence

The design is GroX-native, but two current primary-source principles support its posture:

- NIST AI RMF 1.0 organizes risk work around Govern, Map, Measure, and Manage and treats risk management as a continuous lifecycle activity. NIST states that AI RMF 1.0 is under revision, so GroX treats it as supporting evidence rather than a frozen external dependency.
- OpenTelemetry semantic conventions emphasize meaningful aggregation, consistent error classification, and predictable low-cardinality error semantics. GroX does not adopt OpenTelemetry as a runtime dependency here; the lesson is to preserve stable metric meaning and explicit failure classes.

Primary references:

- NIST, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- NIST AI RMF Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- OpenTelemetry, *Recording errors*: https://opentelemetry.io/docs/specs/semconv/general/recording-errors/

## Qualification boundary

Implementation alone does not close Stage 5. Completion requires:

- the operational degradation experiment to pass;
- baseline immutability and source-binding tests to pass;
- `UNKNOWN` fail-closed behaviors to pass;
- A6 non-self-activation to remain enforced;
- A6/A7 regressions and all canonical CI gates to pass;
- independent verification of the exact final candidate;
- canonical stewardship records to reflect only verified state.
