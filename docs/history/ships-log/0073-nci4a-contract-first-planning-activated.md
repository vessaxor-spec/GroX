# Ship's Log 0073 — NCI-4A contract-first planning activated

**Date:** 2026-10-02

After Live Environment Awareness Program 001 closed, the Commander authorized planning for NCI-4 Neural Crew evolution and requested recalibration against current 2026 technology before implementation.

The existing NCI-4 architectural intent remains valid: improve Crew Mission-state cognition without changing the canonical command spine `Commander → Pilot GorXu → Divisions → Standing Crew` or allowing learned competence to become authority.

The implementation order is recalibrated. NCI-4 will **not** begin by adopting Soup or immediately fine-tuning Qwen. Issue #209 opens **NCI-4A — Neural Crew decision contract and evaluation gate**. NCI-4A must first establish a typed advisory decision contract, bounded Mission Decision Packet, experimental corpus admission/provenance rules, immutable gold holdout and paired evaluation substrate. No model training is required to qualify NCI-4A.

Current 2026 research supports a trainer-portable posture. Soup 0.75.x remains a useful candidate high-level Trainer but is isolated from GroX runtime because its current supported Python range is 3.10–3.12. Hugging Face TRL is a reference alternate SFT/DPO/GRPO lane, and MLX-LM may be evaluated as an optional Apple-Silicon lane where actual model support is proven. Qwen3-4B remains the continuity control while Qwen3.5-4B and Qwen3.5-2B are current small-model challenger candidates. None is adopted or qualified by this planning decision.

Generation 1 will prefer LoRA/QLoRA + SFT. Preference optimization requires legitimate preference data; GRPO requires deterministic/verifiable GroX rewards. Model-as-judge evidence cannot be the sole qualification oracle.

The planned progression is NCI-4A contract/evaluation → NCI-4B parent/Trainer bake-off → NCI-4C Generation 1 → NCI-4D shadow qualification → NCI-4E bounded live Inspect qualification. Any live Neural Crew use remains subordinate to existing sealed Orders, deterministic validation, Tool Gateway authority and independent verification.

This is a planning/stewardship milestone only. No model is trained, registered, promoted, selected or activated; no Crew company, authority, release, NCI qualification or Apex stage changes.
