# Failure Record: h-e1 (Run 2)

**Hypothesis ID:** h-e1
**Phase:** Phase 4
**Failure Type:** MUST_WORK Gate FAIL → ROUTED_TO_PHASE_0
**Written At:** 2026-03-15T01:35:00Z
**Run:** 2 (second execution attempt)

---

## Hypothesis Statement

Under GRPO-based RLEF training with Qwen2.5-Coder-7B on high-S_term APPS problems (S_term > 0.85), substituting R_binary with R_ratio decreases zero-reward fraction by ≥20% and increases gradient SNR by ≥1.5x in the first 25% of training steps.

---

## Performance Gap

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| ZRF Reduction (R_binary vs R_ratio) | ≥ 20% | 0.0% | FAIL |
| Gradient SNR Ratio | ≥ 1.5x | undefined (0.0 / 0.0) | FAIL |
| Zero Reward Fraction (R_binary) | < 0.80 | 1.000 | FAIL |
| Zero Reward Fraction (R_ratio) | < 0.80 | 1.000 | FAIL |

**Experiment scope:** 6 runs (2 conditions × 3 seeds), 30 steps/run, 8 rollouts/step → 1440 total rollouts, 0 non-zero rewards.

---

## Root Cause Analysis

1. **Fundamental assumption violated:** The hypothesis assumed partial-pass solutions exist at high S_term (S_term > 0.85) difficulty. In reality, Qwen2.5-Coder-7B-Instruct produces k_pass = 0 for ALL rollouts on competition/interview-level APPS problems.

2. **R_ratio ≡ R_binary when k_pass = 0 always:** Both reward functions collapse to 0 identically. The informative gradient signal mechanism cannot activate when no partial-pass solutions exist.

3. **S_term > 0.85 selects completely-intractable regime:** This is NOT a "partially tractable" regime. The model cannot even partially solve problems at this difficulty level.

---

## Lessons Learned

1. **Pre-screen k_pass distribution before running GRPO:** Require ≥10% of rollouts to produce k_pass > 0 as a necessary precondition. Add this as a dataset/model compatibility check.

2. **Target S_term ∈ [0.4, 0.75] for R_ratio benefit:** The reward granularity mechanism requires a mid-difficulty regime where partial solutions exist but full solutions are rare.

3. **Validated technical components (reuse in Phase 0 redesign):**
   - TRL GRPOTrainer v0.29.0 API: use `args=grpo_config` (not `config=`)
   - Load tokenizer from original model ID, not SFT checkpoint
   - `per_device_train_batch_size = num_generations = 8`
   - `kl_coef` not supported in TRL v0.29.0; use `kl_beta`
   - APPS loading via huggingface_hub (datasets 4.7.0 no script support)
   - CSV logging per seed/condition works correctly
   - H100 NVL single GPU sufficient for 7B model

4. **Alternative directions for Phase 0:**
   - Use APPS introductory/medium problems (S_term ∈ [0.4, 0.75])
   - Use stronger base model (13B+) or better SFT checkpoint
   - Consider HumanEval or MBPP with partial credit scoring
   - Pre-check that ≥10% rollouts produce k_pass > 0 before full experiment

---

## Cascade Effects

- h-m1, h-m2, h-m3 → CASCADE_FAILED (all blocked by h-e1 prerequisite failure)
- All 4 sub-hypotheses in this pipeline branch are now stopped
- Routing: ROUTED_TO_PHASE_0 for hypothesis redesign

---

## Context

**Model:** Qwen2.5-Coder-7B-Instruct
**Dataset:** APPS (codeparrot/apps), competition+interview subset
**Optimizer:** GRPO (TRL v0.29.0)
**GPU:** NVIDIA H100 NVL
**Conda env:** youra-h-e1 (Python 3.10)
**reflection_outcome:** ROUTED_TO_PHASE_0
**gate_action:** ROUTE_TO_PHASE_0
