# Orchestration Evaluation and Self-Improvement

**Qualification status:** **A6 QUALIFIED** in GroX `v0.7.1`. Evaluation remains advisory after Apex qualification: proposals cannot self-activate and controlled evaluator improvement is not equivalent to production-policy activation.

## Purpose

A6 gives GorXu a native way to measure orchestration quality, replay prior Missions, compare bounded alternatives, and file evidence-backed improvement proposals without granting the evaluation system authority to change the Vessel.

A6 is an intelligence and evidence layer under GorXu. It is not a command layer, a second orchestrator, or an autonomous mutation engine.

## Non-negotiable boundary

**Evaluation may recommend. Evaluation may not activate.**

An A6 proposal cannot change routing, prompts, Crew skills, memory policy, workflows, source, configuration, or operational authority by itself. Any accepted proposal must later travel through the ordinary GroX authority path with an explicit Mission Order, appropriate mutation authority, bounded scope, evidence, and independent verification where required.

No evaluation score, statistical result, model judgment, or proposal status grants capability or permission.

## Canonical trajectory source

A6 reconstructs Mission trajectories from records GroX already owns rather than creating a competing event system. Sources include:

- Mission records;
- Mission Orders;
- Evidence records;
- Mission Graph nodes and relevant graph events;
- Durable graph-run and exception-decision records;
- Crew performance observations.

The evaluator does not become the source of truth for those records. It derives a replayable evaluation case from them.

## Trajectory schema

A trajectory contains privacy-minimized events in the following categories:

- `plan` — cognitive plans, Mission Graph plans, routing decisions, and recorded replans;
- `delegation` — bounded Mission Orders;
- `tool_action` — governed Tool Gateway evidence;
- `exception` — Crew, Pilot, graph-selection, and executive exception records;
- `verification` — independent verification evidence;
- `telemetry` — Crew outcome, latency, cost, evidence-quality, and verification observations;
- `control` — relevant graph and resume/cancellation state;
- `evidence` — remaining attributable evidence that is not one of the categories above.

A stable `trace_sha256` binds the normalized trajectory. Replaying a stored trajectory recomputes that digest and its metrics/invariants. Digest disagreement fails closed.

## Privacy minimization

Evaluation state is private operational state. It should contain enough evidence to grade orchestration without becoming a second copy of sensitive Mission content.

A6 therefore hashes or omits raw content where possible:

- Commander directives are represented by digest in the trajectory;
- Order objective and scope are digested rather than copied verbatim;
- raw Order parameters are omitted;
- stdout/stderr are represented by digests;
- network body previews are omitted;
- browser evidence stores source/screenshot digests and isolation metadata;
- MCP result content is represented by digest;
- unknown evidence stores its key set and content digest.

Secret values must never be admitted to the evaluation corpus merely to improve scoring fidelity.

## Evaluation ledger

A6 adds three private SQLite record classes:

- `evaluation_cases` — replayable trajectory or routing cases;
- `evaluation_runs` — evaluator configuration, case results, metrics, and invariant results;
- `improvement_proposals` — evidence-backed proposals with status `proposed`.

Cases, runs, and proposals are individually SHA-256 bound, including their creation timestamps. Reads verify the stored record before using it. A case ID may be reused only when its complete normalized content is identical.

Every evaluation case requires attributable provenance containing a non-empty `source`.

## Mission trajectory grading

The initial deterministic trajectory grader records:

- success;
- accumulated observed latency;
- attributable cost units;
- retries;
- resumes;
- Commander escalations;
- verification count and failures;
- governed tool-action count;
- exception count;
- average evidence quality;
- capability violations;
- verifier-independence violations;
- critical-escalation violations;
- authority violations;
- trace completeness.

A completed Mission is not automatically a good trajectory. A completed trajectory must contain attributable plan, delegation, governed tool-action, and telemetry evidence; required verification remains additional. Authority, verification, evidence, and trace invariants are graded independently from outcome success.

## Routing replay cases

Routing evaluation is deliberately separated from live production routing.

A routing case records:

- task identifier;
- risk class;
- topology (`sequential` or `parallel`);
- candidate Crew identities;
- precomputed routing components;
- eligibility of each candidate;
- expected eligible Crew identity;
- provenance.

Eligibility is filtered before scoring. Candidate weight changes therefore cannot make an ineligible Crew member selectable.

Production routing continues to use the immutable all-1.0 component-weight baseline unless a later authorized GroX mutation changes source. A6 candidate weights exist only inside an evaluation run.

## Paired improvement gate

A routing candidate qualifies for an improvement proposal only when all of the following hold:

1. baseline and candidate use the same case set;
2. the suite contains at least 20 paired cases;
3. the candidate passes more cases than baseline;
4. candidate-only wins exceed baseline-only wins;
5. an exact one-sided paired sign test meets the effective significance threshold: `0.05` for one predeclared profile, or the family-wise adjusted alpha when multiple profiles are searched;
6. the candidate has zero invariant failures;
7. invariant failures do not regress relative to baseline.

The gate is intentionally stricter than a higher aggregate score. No weighted average may hide an authority, eligibility, or verification failure.

The current bounded search profiles may test risk, reliability, evidence-quality, cost, and latency weight changes. When multiple profiles are searched on the same suite, the family-wise alpha is controlled across the profile set before any proposal may qualify. These are candidate profiles, not production settings.

## Controlled qualification versus operational evidence

A controlled qualification corpus proves that the evaluation machinery can detect a deliberately constructed improvement and reject unsafe or non-improving mutations. It does **not** prove that the same candidate will improve real production Missions.

Operational-history trajectories and future real-world evaluation corpora must remain separately attributable. A candidate derived from a controlled suite remains a proposal until independently validated on appropriate operational evidence and authorized through normal GroX mutation governance.

## Proposal classes

A6 may record proposals of type:

- `routing`;
- `prompt`;
- `skill`;
- `memory`;
- `workflow`.

Every proposal requires:

- target;
- proposed change;
- rationale;
- evidence;
- optional baseline/candidate run references;
- immutable `proposed` status at the A6 boundary.

## No self-activation

The A6 ledger exposes no state transition from `proposed` to `active`.

An activation attempt through the A6 service raises `PermissionError`. GorXu may present or route a proposal for later consideration, but neither GorXu's evaluator nor the proposal itself may convert evidence into mutation authority.

This is deliberate. Self-improvement is governed evolution, not self-authorization.

## Mutation and adversarial testing

A6 qualification must include at least:

- case tampering detection;
- run tampering detection;
- proposal tampering detection;
- ineligible high-scoring Crew cannot be selected;
- a deliberately non-improving routing mutation fails the improvement gate;
- proposal activation is denied;
- production default routing remains behavior-equivalent and immutable during evaluation;
- a real governed multi-tool Mission can be captured and replayed without leaking its secret value.

## Qualified A6 gate

A6 qualification was established when:

1. a real preserved Mission is reconstructed and replayed from canonical private state;
2. required plan/delegation/tool/exception/verification/telemetry evidence is traceable and invariants pass;
3. a replayable controlled corpus exercises at least 20 paired cases across both sequential and parallel topology;
4. a bounded candidate demonstrates statistically better controlled results with zero invariant regression;
5. that result creates an evidence-backed proposal only;
6. an explicit activation attempt is denied;
7. production routing remains unchanged;
8. adversarial/tamper and complete Vessel regression suites pass independently.

A6 passed this gate and later advanced through A7. In the released Apex baseline, the A6 non-self-activation rule remains mandatory: evaluation evidence can support a future authorized change, but can never create its own mutation authority.
