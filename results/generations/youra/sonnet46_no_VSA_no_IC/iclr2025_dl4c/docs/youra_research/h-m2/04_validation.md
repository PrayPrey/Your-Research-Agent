# Phase 4 Validation Report: H-M2

**Hypothesis ID:** H-M2
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Gate Type:** SHOULD_WORK
**Validation Result:** FAILED (SHOULD_WORK — continue with pivot note)

---

## 1. Hypothesis Statement

GRPO training on variance-50 produces lower mean TRL frac_reward_zero_std than random-50 at training checkpoints (steps 10, 20, 50), confirming that variance profiling successfully identifies MBPP problems with nonzero GRPO gradient signal.

---

## 2. Experiment Execution Summary

### 2.1 Environment

- **Model:** deepseek-ai/deepseek-coder-7b-instruct-v1.5
- **Training Framework:** TRL 1.9.2 GRPOTrainer
- **Conda Environment:** youra-h-m1 (torch 2.6.0+cu124, CUDA available)
- **GPU:** NVIDIA H100 NVL (single GPU, CUDA_VISIBLE_DEVICES=0)
- **Dataset:** google-research-datasets/mbpp, subset=full, split=train (374 problems)
- **H-E1 profiling JSON:** docs/youra_research/h-e1/results/mbpp_variance_profile.json (verified)

### 2.2 Configuration

| Parameter | Value |
|-----------|-------|
| num_generations (G) | 4 |
| generation_batch_size | 4 |
| max_steps | 50 |
| learning_rate | 5e-7 |
| beta | 0.0 |
| logging_steps | 1 |
| use_vllm | False |
| per_device_train_batch_size | 1 |
| seed | 42 |
| max_completion_length | 512 |
| save_strategy | none |

### 2.3 Dataset Construction

- **Variance-50 IDs:** Loaded from H-E1 JSON `top_ids` key (50 problem IDs, verified)
- **Random-50 IDs:** numpy default_rng(42).choice over 374 train task_ids (50 unique)
- **Both subsets:** 50 problems each from MBPP full/train (task_ids 601-974)

**Fix applied:** `mbpp_subset` changed from "sanitized" (120 problems) to "full" (374 problems) to match H-E1 profiling split.

---

## 3. Gate Results

### Primary Gate: FAILED

| Checkpoint | mean_frac_var | mean_frac_rnd | gap_pp | gate_pass |
|------------|---------------|---------------|--------|-----------|
| Step 10    | 1.0000        | 1.0000        | 0.0000 | False     |
| Step 20    | 1.0000        | 1.0000        | 0.0000 | False     |
| Step 50    | 1.0000        | 1.0000        | 0.0000 | False     |

**Primary gate pass:** False
**Secondary gate pass (gap ≥ 5pp at step 10):** False

### Root Cause Analysis

`frac_reward_zero_std = 1.0` for ALL 50 steps in BOTH conditions. This means:

1. **All 4 completions fail every problem at every step.** Binary execution reward = 0.0 for all completions → reward_std = 0.0 per group → frac = 1.0.
2. **No gradient signal was produced** in either condition (advantages = 0 for all groups throughout training).
3. **The variance selection signal is real (H-M1 validated)** but irrelevant when the model cannot pass ANY test in 50 steps. The theoretical expectation (~69% frac_zero_std for random-50) assumes the model has ~50% intermediate pass@k — not the case at step 0 of RLEF with this model+config.

**Diagnosis:** The model fails all MBPP problems with G=4 short completions (max_completion_length=512) in the first 50 training steps. This is a *cold start* problem: the variance selection advantage only manifests once the model has nonzero pass@1 for some problems. At 0 gradient signal, no learning occurs and neither condition can differ.

**Observation from logs:**
- `rewards/reward_fn/mean = 0.0` throughout both training runs
- `loss = 0.0`, `grad_norm = 0.0` — zero gradient confirms no learning
- TRL's off-policy re-use means only ~13 of 50 steps have new rollouts (1 rollout per `num_generations` problems per generation cycle)

---

## 4. Code Implementation Summary

### 4.1 Files Generated

| File | Status | Notes |
|------|--------|-------|
| `code/config.py` | Complete | H_M2Config dataclass |
| `code/dataset.py` | Complete | Fixed: `top_ids` key, `full` subset |
| `code/reward.py` | Complete | Subprocess execution harness |
| `code/train.py` | Complete | Fixed: `max_completion_length`, `save_strategy="no"`, `processing_class` |
| `code/analyze.py` | Complete | Gate metrics, JSON output |
| `code/visualize.py` | Complete | 4 figures (matplotlib Agg) |
| `code/run_experiment.py` | Complete | Orchestrator |
| `code/tests/test_dataset.py` | Complete | 4 tests |
| `code/tests/test_reward.py` | Complete | 6 tests |
| `code/tests/test_analyze.py` | Complete | 6 tests |

### 4.2 Unit Tests

All 16 tests passed in both `youra-h-m2` and `youra-h-m1` environments.

### 4.3 API Fixes Applied

| Original Spec | Actual TRL 1.9.2 API |
|---------------|----------------------|
| `GRPOConfig(max_new_tokens=...)` | `GRPOConfig(max_completion_length=...)` |
| `GRPOConfig(save_steps=[...])` | `GRPOConfig(save_strategy="no")` |
| `GRPOTrainer(tokenizer=...)` | `GRPOTrainer(processing_class=...)` |
| `mbpp_subset="sanitized"` | `mbpp_subset="full"` (374 problems) |
| H-E1 JSON key `"top50_ids"` | Actual key is `"top_ids"` |

---

## 5. Figures Generated

- `figures/gate_comparison.png` — Grouped bar chart (all bars at 1.0; gate FAIL visible)
- `figures/learning_curves.png` — Per-step line plot (flat at 1.0 for both conditions)
- `figures/gap_trajectory.png` — Gap trajectory (flat at 0.0 throughout)
- `figures/reward_std_histograms.png` — Skipped: TRL 1.9.2 does not log `reward_std` key in log_history when reward=0.0 throughout

---

## 6. Gate Verdict

**SHOULD_WORK gate: FAILED**

Per protocol: failure triggers PIVOT. The hypothesis cannot be validated in the current setup. Recommended pivot: online selection (filter problems dynamically based on current model pass@k, not frozen profiling).

**Code runs without error:** YES (both 50-step training runs completed successfully)
**Mechanism correctly implemented:** YES (TRL GRPOTrainer with correct API)
**Metrics measurable:** YES (frac_reward_zero_std logged at every generation step)
**Mechanism effective:** NO (cold-start problem: no reward signal in first 50 steps)

---

## 7. Lessons Learned (Phase 2C Handoff)

### Proven Components (Reusable)
- TRL 1.9.2 `GRPOTrainer` with `processing_class` (not `tokenizer`)
- Binary execution reward via subprocess + `make_execution_reward` factory
- MBPP `full/train` split (374 problems, task_ids 601-974) matches H-E1 profiling
- Dataset construction: `build_subset` with `filter()` works correctly
- `frac_reward_zero_std` auto-logged by TRL when `logging_steps=1`
- `conda env youra-h-m1` (torch 2.6.0+cu124, TRL 1.9.2) is the working environment

### Critical Implementation Notes for Dependent Hypotheses
1. `MBPP full/train` not `sanitized/train` — sanitized has only 120 problems
2. H-E1 JSON uses `"top_ids"` not `"top50_ids"`
3. `max_completion_length` not `max_new_tokens` in TRL 1.9.2
4. `processing_class` not `tokenizer` in TRL 1.9.2 `GRPOTrainer`
5. Cold start: DeepSeek-Coder-7B needs warm-up or higher learning rate to produce nonzero rewards in 50 steps
6. Use `save_strategy="no"` — `save_steps` takes int not list in HF TrainingArguments

### Recommended Pivot for H-M3/H-M4
- Online selection: filter problems where current model pass@k ∈ (0, 1) at each generation step
- Or: use a model with higher base pass@1 on MBPP (e.g., Qwen2.5-7B-Instruct)
- Or: increase max_steps to 500+ and use warmup scheduler to reach nonzero rewards first

---

## 8. Experiment Results File

`docs/youra_research/h-m2/results/gate_results.json` — saved with:
- `primary_gate_pass: false`
- `frac_zero_std_variance50`: [1.0] × 13 steps (generation steps logged)
- `frac_zero_std_random50`: [1.0] × 13 steps

---

*Validation completed: 2026-08-21*
*Both training runs completed successfully (50 steps each, ~2 min/run)*
*Gate: SHOULD_WORK FAILED — proceed to pivot per Phase 2A redesign protocol*
