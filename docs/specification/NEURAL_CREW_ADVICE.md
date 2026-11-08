# NCI-4A Neural Crew Advisory Decision Contract

**State:** proposed implementation slice, not NCI-4A qualification.  
**Tracking:** [GroX issue #209](https://github.com/vessaxor-spec/GroX/issues/209)  
**Schema:** `grox-neural-crew-advice-v1`  
**Implementation:** `src/grox/neural_crew_advice.py`

## Purpose and authority boundary

This is a **typed advisory result**, not a Crew action, Mission Order,
approval, execution instruction, or provider binding. Only the existing
Commander → Pilot GorXu → Divisions → Standing Crew command spine is
operational. GorXu remains the sole orchestrator.

A model may return an advisory candidate, and an isolated evaluator may
score it. The contract does not construct or seal a Mission Order, select
Crew, invoke tools, approve mutations, register models, change provider
routing, change risk, or verify the model's own work.

No live Crew executor or Tool Gateway integration is part of this slice.
The existing bounded Inspect-only Crew cognition path remains unchanged.

## Exact v1 wire format

Every field is required. Missing or extra fields fail closed.

```json
{
  "schema": "grox-neural-crew-advice-v1",
  "recommended_action": "suggest_test_run",
  "evidence_sufficient": false,
  "test_interpretation": "not_run",
  "continue_or_stop": "continue",
  "failure_classification": "none",
  "confidence": 0.7,
  "requested_evidence": []
}
```

| Field | Valid values |
| --- | --- |
| `schema` | exact v1 string |
| `recommended_action` | `suggest_fs_list`, `suggest_fs_read`, `suggest_test_run`, `suggest_finish`, `request_evidence`, `stop` |
| `evidence_sufficient` | JSON boolean |
| `test_interpretation` | `not_run`, `pass`, `fail`, `inconclusive` |
| `continue_or_stop` | `continue`, `stop` |
| `failure_classification` | `none`, `insufficient_evidence`, `test_failure`, `tool_failure`, `policy_denied`, `unknown` |
| `confidence` | finite JSON number, 0 through 1; boolean and non-finite values rejected |
| `requested_evidence` | list of 0–8 unique, trimmed, nonempty text labels up to 128 characters each |

**Semantic restrictions:**

- `suggest_finish` requires `evidence_sufficient=true` and
  `continue_or_stop=stop`. It is *not* evidence that Commander intent
  or a Mission objective was fulfilled.
- `stop` requires `continue_or_stop=stop`.
- `request_evidence` requires `evidence_sufficient=false`,
  `continue_or_stop=continue`, and at least one evidence label.
- Only `request_evidence` may carry evidence request labels.
- `policy_denied` requires `continue_or_stop=stop`.
- Any authority-bearing extension, including `mode`, `allowed_actions`,
  `tool_parameters`, `approval`, or `model_activation`, is invalid.
- Labels describe desired evidence; they are not file paths, instructions,
  authorizations, or requests to operate tools.

The Python validator is the normative executable reference for this slice.
Its immutable value object never executes advice. The version identifier
must change for any future incompatible vocabulary or semantics.

## NCI-4A qualification still required

This slice alone does **not** satisfy issue #209. Before NCI-4A can be
qualified, GroX still needs:

1. A provenance-checked, explicitly admitted experimental case format.
2. An immutable generation-specific gold holdout with train/eval separation.
3. A bounded Mission Decision Packet with no unbounded private context.
4. Trainer-independent parent/candidate scoring, including tiny-policy
   baseline and at least one untrained language-model parent.
5. Negative/injection/OOD cases, authority-invariant mutation proofs, and
   independent evaluation that cannot make authority decisions.
6. Exact-head five-job CI and post-merge protected-main CI evidence.

Training, model registration, model selection, activation, and NCI-4
qualification remain explicitly out of scope.
