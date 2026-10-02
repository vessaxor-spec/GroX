# NCI-4 Neural Crew Evolution Plan 001

**Status:** PLANNING ACTIVE / NCI-4A CONTRACT + EVALUATION GATE OPEN / NCI-4 UNQUALIFIED  
**Status date:** 2026-10-02  
**Tracking issue:** #209  
**Command invariant:** Commander → Pilot GorXu → Divisions → Standing Crew

## Purpose

NCI-4 evolves the existing qualified local Crew cognition seam beyond the 75-parameter action-selection policy toward richer Mission-state cognition while preserving deterministic GroX authority.

The target is **better Crew judgment, not more Crew authority**.

A Neural Crew model may recommend a bounded Crew decision. It does not become a Pilot, Mission authority, Tool Gateway, verifier, or parallel orchestrator.

## 2026 recalibration

The original roadmap correctly required isolated training, lineage, evaluation and governed activation, but it was too Trainer/model centric. NCI-4 must not begin by selecting Soup or fine-tuning Qwen.

The revised causal order is:

> typed Crew decision contract → admitted experimental corpus → immutable gold holdout → parent/trainer bake-off → Generation 1 training → shadow qualification → bounded live Inspect qualification → separate activation decision

Trainer and model choices are capabilities inside that process, not architecture.

## NCI-4A — Neural Crew decision contract and evaluation gate

NCI-4A is the first bounded stage. It requires **no model training** and grants **no new operational authority**.

### Decision contract

Define one machine-validated advisory result that may contain:

- `recommended_action`;
- `evidence_sufficient`;
- `test_interpretation`;
- `continue_or_stop`;
- `failure_classification`;
- `confidence`;
- `requested_evidence`.

The contract must fail closed on malformed, ambiguous or unknown fields.

Deterministic GroX remains solely responsible for:

- Mission risk and mode;
- Crew eligibility/capabilities;
- sealed Mission Orders;
- Tool Gateway authority;
- Inspect/Repair/Execute/Verify boundaries;
- Commander escalation requirements;
- verifier independence;
- execution scope;
- actual tool invocation.

Model competence never creates permission.

### Mission Decision Packet

Neural Crew should receive a bounded Mission Decision Packet rather than whole-Vessel context.

Candidate contents:

- exact sealed Order representation;
- relevant Crew craft excerpt;
- bounded relevant memory;
- current observations/evidence;
- eligible advisory decision vocabulary;
- current evidence state.

Large or expensive evidence may be represented through GroX-native content-addressed context references. A reference exposes only a stable label, SHA-256 identity, and size; exact raw material is returned only through bounded read-only slice/search views under a shared operation/character budget. This harvests the useful containment principle from Autolith's recursive-inference context objects without importing recursive agents, Lisp environments, provider recursion, or another command path.

This may harvest the qualified HOT/WARM/COLD context principles but does not activate unrestricted automatic whole-Vessel compression.

### Experimental corpus gate

Before NCI-5, NCI-4A may create only the minimum experimental corpus needed to train/evaluate the decision contract.

Admissible sources:

1. deterministic/synthetic cases derived from GroX contracts;
2. canonical tests, mutation cases, failures and recovery scenarios;
3. privacy-minimized verified Mission trajectories only when explicitly admitted;
4. preserved red/failure evidence as negative cases.

Not admitted by default:

- Commander conversations;
- arbitrary private state;
- unverified Mission traces;
- external-model output treated as truth;
- data lacking provenance or applicable rights metadata.

Each case must record provenance, case identity, task class, expected decision, applicable invariants and train/eval disposition.

A generation-specific **gold holdout** must be immutable and excluded from training.

### Evaluation gate

Parent and candidate models must be compared on the same admitted cases.

Required dimensions include:

- typed-contract validity;
- next-step/action correctness;
- evidence-sufficiency classification;
- test interpretation;
- stop/continue precision and recall;
- failure triage;
- confidence calibration;
- unnecessary-step rate;
- Mission usefulness;
- verifier outcomes;
- latency/resource use;
- prompt/tool-output injection resistance;
- out-of-distribution abstention/escalation;
- authority/invariant violations.

Authority violations must remain exactly zero. No aggregate quality gain may offset an authority regression.

Model-as-judge may be supplementary evidence only, never the sole reward or qualification oracle.

## Parent-model bake-off

NCI-4 is parent-model portable.

Initial evaluation set:

- **continuity control:** existing Qwen3-4B family used by NCI-2/NCI-3;
- **current challenger:** Qwen3.5-4B;
- **efficiency challenger:** Qwen3.5-2B.

Admission requires a pinned upstream identity/revision, license/provenance review, trainable checkpoint identity, hardware/resource profile and explicit separation from inference-only GGUF artifacts.

Newer or larger does not mean better.

## Trainer bake-off

Training machinery remains isolated and replaceable.

Initial lanes:

- **Soup 0.75.x** — high-level candidate Trainer; current upstream Python bound is `>=3.10,<3.13`, so it remains outside GroX's Python 3.11–3.14 runtime/CI dependency surface;
- **Hugging Face TRL** — reference post-training lane for SFT/DPO/GRPO and related methods;
- **MLX-LM** — optional Apple-Silicon efficiency lane only where the selected parent/method is actually supported.

Generation 1 technique order:

1. LoRA/QLoRA + SFT;
2. DPO only after legitimate preference pairs exist;
3. GRPO only after GroX owns deterministic/verifiable reward functions.

Training environment requirements:

- isolated environment/container;
- no GroX runtime dependency;
- no Commander credentials;
- parent/dataset/config/dependency/version/seed digests recorded;
- authorized artifact acquisition separated from training;
- network disabled after acquisition where practical;
- outputs quarantined until GroX evaluation;
- no automatic registry admission, selection, promotion or activation.

## NCI-4B through NCI-4E

### NCI-4B — Parent + Trainer bake-off

Run the contract/evaluation gate against the continuity parent and selected challengers using replaceable Trainer lanes. No operational activation.

### NCI-4C — Generation 1

Train the first candidate through the winning bounded lane, beginning with LoRA/QLoRA + SFT. Preserve parent/candidate artifacts, configs, seeds, versions, corpus digests, model digests, evaluation evidence and rejected descendants.

### NCI-4D — Shadow qualification

A candidate observes the same bounded Mission state as live Crew and records what it **would** recommend while having zero operational effect.

Compare against actual verified outcomes and baseline behavior.

### NCI-4E — Bounded live Inspect qualification

Only after shadow qualification passes, allow one or a very small cohort of Inspect Crew to consume neural recommendations through the existing deterministic validation and Tool Gateway path.

No Repair, Execute or Verify neural authority is implied.

## Promotion rule

A descendant may advance only when paired evidence shows meaningful bounded improvement with:

- zero authority regression;
- no verifier-independence regression;
- no Commander-alignment regression;
- no material personal-assistant/orchestration regression;
- acceptable latency/resource cost;
- reconstitution compatibility;
- preserved Apex/Post-Apex invariants.

Training success alone never activates a model.

## Current upstream evidence inspected 2026-10-02

- Soup 0.75.0 declares Python `>=3.10,<3.13`, Alpha status and isolated optional training dependencies.
- Hugging Face TRL exposes SFT, DPO, GRPO and related post-training surfaces.
- MLX-LM provides LoRA/QLoRA fine-tuning on supported model families.
- Qwen3.5-4B and Qwen3.5-2B are current Apache-2.0 trainable/model-family candidates.

These are research inputs, not GroX dependencies or qualifications.

## NCI-4A exit

NCI-4A is complete only when:

1. the typed Neural Crew decision contract is canonical and fail-closed;
2. malformed/unknown decision fields cannot widen execution authority;
3. the experimental corpus schema and provenance/admission rules are canonical;
4. immutable gold-holdout handling is proven;
5. parent-model and Trainer bake-off protocols are canonical and trainer-portable;
6. baseline evaluation can score the current 75-parameter policy and at least one untrained language-model parent without operational activation;
7. no Commander conversation/private trace is silently admitted;
8. no model training or activation is required to pass NCI-4A;
9. permanent invariant tests/mutations protect the authority boundary;
10. exact-head and post-merge canonical CI pass.

## Non-goals

NCI-4A does not:

- train Generation 1;
- activate an LLM-backed Crew;
- qualify Soup, TRL, MLX-LM, Qwen3.5 or any other model/Trainer;
- start NCI-5;
- change the 82-Crew company;
- change Mission authority;
- qualify Repair/Execute/Verify neural cognition;
- change the release;
- create a new Apex stage.
