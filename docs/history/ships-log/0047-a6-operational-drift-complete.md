# Ship's Log — Entry 0047

**Date:** 2026-08-17
**Milestone:** A6 longitudinal operational drift analysis completed

## Mission

Extend the qualified A6 evaluation plane so GorXu can detect meaningful degradation across real operational Mission evidence without allowing the act of measurement to redefine the baseline or activate a fix.

## Result

GroX now supports digest-bound operational comparison windows with `STABLE`, `WATCH`, `REGRESSION`, and `UNKNOWN` outcomes. Operational evidence must remain attributable to canonical private Mission state. Missing, stale, tampered, incompatible, or non-operational evidence fails closed as `UNKNOWN`.

Authority, capability, verifier independence, critical escalation, and evidence-trace failures remain first-class. Success, evidence quality, verification failures, cost, latency, retries, exceptions, replans, recovery, tool failures, Commander escalation, and Crew routing concentration can be compared without collapsing them into one self-normalizing score.

## Operational proof

An isolated production-path experiment ran two healthy GorXu Inspect Missions, injected a reversible test failure, and then ran two degraded Inspect Missions. A6 correctly reported `REGRESSION`: success moved from 1.0 to 0.0, tool failure rate from 0.0 to 0.5, and evidence quality from 0.916667 to 0.666667. The frozen baseline run digest and metrics did not change. The resulting A6 proposal remained `proposed`, and activation was denied.

Run `32004673068` passed all five canonical CI jobs with 185 pytest passes, 187 unittest passes, and Stage 5 detector mutations 4/4 killed, alongside all earlier mutation suites.

## Command integrity

The command relationship and mutation boundaries are unchanged. Drift findings advise GorXu; they do not command the Vessel or self-authorize source, routing, policy, Crew, memory, or Repair changes.
