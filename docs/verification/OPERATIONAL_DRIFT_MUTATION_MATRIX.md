# Operational Drift Mutation Matrix

## Purpose

Stage 5 continuously proves that high-consequence longitudinal-drift detectors fail when deliberately weakened and return green only after exact source restoration.

## Green implementation evidence

Canonical PR run `32004673068` passed all five GroX CI jobs. Python 3.12 recorded:

- pytest: **185 passed, 2 skipped, 351 subtests**;
- unittest: **187 OK, 2 skipped**;
- operational drift Mission experiment: **PASS**;
- critical invariant mutations: **12/12 KILLED**;
- Vessel Health mutations: **7/7 KILLED**;
- tiered reconstitution mutations: **9/9 KILLED**;
- operational drift mutations: **4/4 KILLED**, zero survivors, exact source restoration.

## Mutations

| Detector | Required failure behavior | Result |
|---|---|---|
| operational provenance gate | controlled/synthetic evidence cannot enter an operational window | KILLED |
| baseline critical-invariant gate | a degraded baseline cannot become accepted normal | KILLED |
| observed critical-invariant gate | critical violation independently forces REGRESSION | KILLED |
| observed freshness gate | stale observed evidence becomes UNKNOWN | KILLED |

## Preserved red evidence

Run `32004304942` failed after the full regression suite had passed because direct execution of the new operational experiment could not import the repository test-support package. This was a harness/bootstrap defect, not a reason to weaken Stage 5. The script now explicitly binds its repository root before importing test support, after which the operational experiment and all detector mutations passed.

## Authority boundary

These detectors are evidence mechanisms only. Mutation proof does not grant routing, policy, Crew, source, memory, or Repair authority. A6 improvement proposals remain non-self-activating.
