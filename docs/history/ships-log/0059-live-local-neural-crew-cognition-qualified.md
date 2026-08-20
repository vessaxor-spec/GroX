# Ship's Log 0059 — Live Local Neural Crew Cognition Qualified

**Date:** 2026-08-20  
**Status:** COMPLETE — CANONICAL EXACT-TREE QUALIFIED  
**Issue:** #76  
**Runtime qualification:** PR #79

## Mission

Close the remaining live-provider evidence gate for the bounded Inspect-only Crew cognition seam without adding a command layer, widening authority, changing Standing Crew membership, creating A8, or moving the published release.

## Result

GroX qualified **one live locally trained neural Crew cognition provider** through the existing bounded Inspect Crew cognition seam.

Exact provider/model:

- provider: `local-neural-session-crew-v1`
- model: `tiny-mlp-policy-5x8x3-v1`
- model kind: locally trained neural action-selection policy
- architecture: 5 → 8 → 3 multilayer perceptron
- learned parameters: **75**
- training examples: **240**
- held-out examples: **100**
- initial held-out accuracy: **0.44**
- final held-out accuracy: **1.00**
- held-out improvement: **+0.56**
- network required: **no**
- external disclosure: **no**

The model was trained in the executing Python process using actual gradient updates. The pre-training and post-training parameter digests differed:

- initial SHA-256: `f5c197881e1fbdf90395bbc09d2c1ac7097691ac68101cf573c64a90b419b6b6`
- trained SHA-256: `7b44fffbc0840d0572194649e47a79c0b1466253e0b93940584dfd5de1beda60`

## Live inference evidence

The trained model performed two real inference calls after being bound through `SessionCrewCognitionProvider` into the canonical provider-qualification harness.

1. Before governed evidence existed, with selective craft and bounded Crew memory present, the model selected `fs_read` with probability **0.999859**.
2. After the governed observation returned through the existing Mission Order + Tool Gateway boundary, again with craft and memory present, the model selected `finish` with probability **0.999892**.

The canonical `qualify_bound_crew_cognition_provider(...)` report returned **PASS** with every required check true:

- Mission completed;
- Inspect mode preserved;
- selective craft evidenced;
- bounded Crew memory selection evidenced;
- governed cognition observation evidenced;
- bounded Crew work product evidenced;
- provider identity matched;
- read-only cognition mode preserved;
- no cognition denial or degradation;
- no mutation evidence;
- `outcome.mutation=false`;
- independent verification PASS.

The canonical harness intentionally retained `live_provider_claim: false`; host evidence separately established that a trained model actually executed in the qualification process.

## Exact qualification evidence

- PR #79 final head: `c8be4d78f92466d3e66ec915b12dcec316396b6d`
- exact-head CI: `32336799141` / run **252**
- required CI jobs: **5/5 PASS**
- Python 3.12 Vessel Health: **10 PASS / 0 WARN / 0 FAIL / 0 UNKNOWN**
- pytest: **252 passed, 2 skipped, 440 subtests passed**
- unittest: **254 tests OK, 2 skipped**
- critical mutations: **12/12 KILLED**
- Vessel Health mutations: **7/7 KILLED**
- reconstitution mutations: **9/9 KILLED**
- operational drift mutations: **4/4 KILLED**
- source provenance mutations: **6/6 KILLED**
- integrated Post-Apex qualification: **PASS**
- `new_apex_stage=false`
- `qualification_claim=false`
- `release_decision=false`
- CI synthetic merge: `a65c6b295e63fdf2b42b7081d30409d581c1b00b`
- CI synthetic merge tree: `109f7d7ddc9712e3d9eec009582025c82317794a`
- canonical PR #79 merge: `d49f43246922c6d8c5e3a632423195ffecd9f161`
- canonical merge tree: `109f7d7ddc9712e3d9eec009582025c82317794a`

The canonical merge tree exactly matches the CI-tested synthetic merge tree.

## Claim boundary

This qualification is deliberately narrow. It does **not** qualify or imply:

- a general-purpose LLM;
- Qwen or another downloaded local language model;
- the OpenAI Responses Crew adapter in live operation;
- another external provider/model;
- all Standing Crew as autonomous model agents;
- model cognition for Repair, Verify, or Execute;
- unrestricted autonomous Crew;
- a new command layer;
- A8 or another Apex stage.

The qualified claim is exactly:

> GroX has qualified one live locally trained neural action-selection provider through the bounded Inspect Crew cognition seam.

## Preserved Vessel state

- Commander retains ultimate authority.
- GorXu remains sole operational orchestrator.
- Mission Control remains subordinate advisory/policy.
- Mission Order + Tool Gateway remain the execution authority boundary.
- Repair remains the explicit mutation-authority path.
- Independent verification remains separate from the Crew provider.
- Standing Crew remain **82**.
- package remains **0.8.0**.
- published release remains **v0.8.0**.
- no A8 exists or is implied.

Current-state README/Roadmap/Progress Tracker wording still requires synchronization to this narrow claim and is tracked separately in issue #80; stale wording does not invalidate the canonical runtime qualification.