---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: h-m2
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# PRD: H-M2 — Variance Selection Reduces Zero-Gradient Groups in GRPO

## 1. Executive Summary

H-M2 validates that GRPO training on variance-selected problems (variance-50) produces fewer zero-gradient groups (`frac_reward_zero_std`) than training on random-selected problems (random-50) at short-horizon checkpoints (steps 10, 20, 50). This is a **mechanism experiment**: same model, same config, only the dataset subset differs. The metric `frac_reward_zero_std` is logged automatically by TRL GRPOTrainer — no custom instrumentation required.

**Gate:** SHOULD_WORK — mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL three checkpoints. Failure triggers PIVOT to online selection.

**Prerequisite:** H-M1 VALIDATED — top-50 variance-selected MBPP problem IDs available, profiling confirms selection signal is real.

---

## 2. Problem Statement

H-M1 confirmed that variance profiling selects MBPP problems with genuinely higher mean variance_i. H-M2 tests the causal mechanism: does training on this high-variance selection actually reduce zero-gradient group frequency during GRPO? A zero-gradient group occurs when all G=4 completions receive identical rewards (all pass or all fail), giving zero std and thus zero policy gradient. Variance-selected problems should have intermediate pass rate (p_i ≈ 0.5), producing mixed reward groups and nonzero gradients more often.

**Success demonstrates:** Variance profiling not only identifies high-variance problems statistically but also provides meaningful gradient signal during GRPO training — confirming the core YOURA selection mechanism.

---

## 3. Functional Requirements

### FR-1: Load H-M1 Variance-50 Problem IDs
- Load `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- Extract top-50 problem IDs by variance_i (already validated in H-M1)
- Store as `variance_50_ids: list[int]` (50 task_ids)
- Validate: exactly 50 IDs, all present in MBPP train split

### FR-2: Load MBPP Dataset
- Load via HuggingFace Datasets: `load_dataset("google-research-datasets/mbpp", "sanitized")`
- Use `train` split (374 problems)
- Fields used: `task_id` (int), `text` (prompt), `code` (reference), `test_list` (list of assert strings)

### FR-3: Construct Variance-50 Dataset (Condition A)
- Filter MBPP train to problems with `task_id` in `variance_50_ids`
- Expected: exactly 50 problems
- Validate count; raise on mismatch

### FR-4: Construct Random-50 Dataset (Condition B)
- Sample 50 problems from MBPP train with fixed seed=42
- `rng = numpy.random.default_rng(42); random_ids = rng.choice(374_problem_ids, 50, replace=False)`
- Store as `random_50_ids: list[int]`

### FR-5: Binary Execution Reward Function
- For each completion: execute code against `test_list` unit tests using `exec()` in subprocess/timeout
- Reward: 1.0 if all tests pass, 0.0 otherwise
- Must handle timeouts (default 5s per problem), syntax errors, runtime errors → reward=0.0
- Compatible with TRL GRPOTrainer `reward_funcs` interface

### FR-6: GRPO Training — Condition A (Variance-50)
- Model: `deepseek-ai/deepseek-coder-7b-instruct-v1.5` (bfloat16)
- Config (see Section 5 for full spec):
  - `num_generations=4`, `generation_batch_size=4`
  - `max_steps=50`, `logging_steps=1`, `save_steps=[10, 20, 50]`
  - `beta=0.0`, `use_vllm=False`, seed=42
- Dataset: variance-50 (50 problems)
- Output dir: `docs/youra_research/h-m2/results/variance50/`

### FR-7: GRPO Training — Condition B (Random-50)
- Identical config as FR-6 (same model, same hyperparameters, same seed)
- Dataset: random-50 (50 problems)
- Output dir: `docs/youra_research/h-m2/results/random50/`

### FR-8: Extract `frac_reward_zero_std` from Training Logs
- Read from `trainer.state.log_history` after each run
- Extract per-step values for steps 1–50 from both conditions
- Validate: exactly 50 values per condition (one per step, `logging_steps=1`)

### FR-9: Compute Gate Metrics at Checkpoints 10, 20, 50
```python
mean_frac_10_var  = mean(frac_zero_std_variance50[steps 1-10])   # steps 0-index 0:10
mean_frac_20_var  = mean(frac_zero_std_variance50[steps 1-20])
mean_frac_50_var  = mean(frac_zero_std_variance50[steps 1-50])

mean_frac_10_rnd  = mean(frac_zero_std_random50[steps 1-10])
mean_frac_20_rnd  = mean(frac_zero_std_random50[steps 1-20])
mean_frac_50_rnd  = mean(frac_zero_std_random50[steps 1-50])

gate_10 = mean_frac_10_var < mean_frac_10_rnd
gate_20 = mean_frac_20_var < mean_frac_20_rnd
gate_50 = mean_frac_50_var < mean_frac_50_rnd
gate_passed = gate_10 and gate_20 and gate_50

gap_at_10 = mean_frac_10_rnd - mean_frac_10_var   # secondary: target >= 0.05
```

### FR-10: Mechanism Verification Asserts
```python
assert len(frac_zero_std_variance50) == 50, "Missing variance-50 steps"
assert len(frac_zero_std_random50) == 50, "Missing random-50 steps"
assert all(0.0 <= v <= 1.0 for v in frac_zero_std_variance50), "Invalid frac values"
print(f"[H-M2] Gate: var50 frac={mean_frac_50_var:.4f} < rnd50 frac={mean_frac_50_rnd:.4f}: {gate_passed}")
print(f"[H-M2] Gap at step 10: {gap_at_10:.3f} (secondary target: >=0.05)")
```

### FR-11: Results JSON
Save `docs/youra_research/h-m2/results/gate_results.json`:
```json
{
  "gate_passed": bool,
  "mean_frac_zero_std": {
    "variance50": {"at_10": float, "at_20": float, "at_50": float},
    "random50":   {"at_10": float, "at_20": float, "at_50": float}
  },
  "gap_at_10_pp": float,
  "gate_by_checkpoint": {"10": bool, "20": bool, "50": bool},
  "frac_reward_zero_std_per_step": {
    "variance50": [float, ...],
    "random50":   [float, ...]
  },
  "variance_50_ids": [int, ...],
  "random_50_ids": [int, ...],
  "seed": 42
}
```

### FR-12: Visualization — 4 Figures
- **Fig 1 (mandatory — gate metric):** Grouped bar chart: mean_frac_zero_std at checkpoints 10, 20, 50 for both conditions. Error bars optional.
- **Fig 2:** Line plot: frac_reward_zero_std per step (1–50) for variance-50 and random-50. Shows trajectory.
- **Fig 3:** Gap trajectory: frac_zero_std(random-50) - frac_zero_std(variance-50) per step 1–50. Horizontal line at 0.0 and 0.05.
- **Fig 4:** Histogram of group reward std at steps 10, 20, 50 for both conditions (reward std ∈ [0, 0.5] for binary G=4).

Output: `docs/youra_research/h-m2/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset: MBPP
- **Source:** HuggingFace `google-research-datasets/mbpp`, config=`"sanitized"`, split=`"train"`
- **Auto-download:** Yes (HuggingFace Datasets API)
- **Size:** 374 problems
- **Loading code:**
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")
  train_data = mbpp["train"]   # 374 problems
  ```

### 4.2 Variance-50 IDs (from H-M1 artifact)
- **Source:** `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- **Key:** `top_ids` field (list of 50 task_ids) or recompute by sorting `problems[*].variance_i` descending, top-50
- **Local file:** Present (no download needed)

### 4.3 No Additional Datasets
- Evaluation at steps 10, 20, 50 uses training-time `frac_reward_zero_std` (no separate eval set)
- This is a training-dynamics experiment, not a generalization experiment

---

## 5. Training Configuration

### Model
- **ID:** `deepseek-ai/deepseek-coder-7b-instruct-v1.5`
- **dtype:** bfloat16
- **device_map:** `"auto"`
- **Confirmed functional:** H-E1 environment

### GRPOConfig

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `num_generations` | 4 | G=4; per Phase 2B spec |
| `generation_batch_size` | 4 | H-E1 environment constraint |
| `max_steps` | 50 | Short RLEF budget; checkpoints at 10, 20, 50 |
| `learning_rate` | 5e-7 | Phase 2B spec (same as H-E1) |
| `beta` | 0.0 | No KL penalty; avoids spurious KL grads on zero-std groups (TRL #5588) |
| `logging_steps` | 1 | Required: per-step `frac_reward_zero_std` |
| `save_steps` | [10, 20, 50] | Checkpoints at gate evaluation points |
| `use_vllm` | False | H-E1 environment constraint |
| `seed` | 42 | Fixed; single run per condition |
| `max_new_tokens` | 512 | Code generation length limit |

---

## 6. Evaluation Metrics

| Metric | Type | Gate | Threshold |
|--------|------|------|-----------|
| mean_frac_zero_std(var50) < mean_frac_zero_std(rnd50) at step 10 | Primary | SHOULD_WORK | Required |
| mean_frac_zero_std(var50) < mean_frac_zero_std(rnd50) at step 20 | Primary | SHOULD_WORK | Required |
| mean_frac_zero_std(var50) < mean_frac_zero_std(rnd50) at step 50 | Primary | SHOULD_WORK | Required |
| gap_at_10 = rnd50 - var50 ≥ 5pp | Secondary | Diagnostic | ≥ 0.05 |
| Expected random-50 baseline frac_zero_std | Reference | Diagnostic | ~69% (theory) |

**PoC Pass Condition:**
1. Both training runs complete 50 steps without error
2. `frac_reward_zero_std` logged for all 50 steps per condition
3. mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at steps 10, 20, AND 50

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.35
trl>=0.15.0          # requires frac_reward_zero_std metric
datasets>=2.0
numpy>=1.20
matplotlib>=3.5
accelerate>=0.20
```

Note: TRL >= 0.15.x required for `frac_reward_zero_std` metric availability (confirmed via Exa search).

### 7.2 Local Artifacts (no download)
- `docs/youra_research/h-e1/results/mbpp_variance_profile.json` — variance-50 IDs source (present)
- `docs/youra_research/h-m1/results/comparison_results.json` — confirmed variance-50 IDs (optional cross-check)

### 7.3 External Repositories (reference only)
- TRL GRPOTrainer: `pip install trl` (primary)
- RRPO-ARR/Code: reference for GRPO MBPP training patterns
- adaptive-mogrpo: reference for binary reward zero-gradient analysis

---

## 8. Non-Functional Requirements

- **Reproducibility:** seed=42 everywhere; deterministic random-50 sampling via `numpy.random.default_rng(42)`
- **Compute:** Two GRPO training runs × 50 steps × 50 problems. Expected: 2–6h total GPU time (GPU type: H-E1 environment)
- **Isolation:** Condition A and B must use IDENTICAL GRPOConfig (only dataset differs)
- **Logging:** `frac_reward_zero_std` must appear in `trainer.state.log_history` every step (validate before analysis)
- **Output:** All artifacts in `docs/youra_research/h-m2/`

---

## 9. Success Criteria

**PASS:** mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL of steps 10, 20, 50
**PARTIAL:** Passes at step 10 but not 20 or 50 → investigate reward shaping drift; document for H-M3
**FAIL/PIVOT:** Fails at step 10 → variance profiling does not reduce zero-gradient groups; pivot to online selection strategy (H-M3 re-scoped)

**Secondary success:** gap_at_10 ≥ 0.05 (5pp) confirms strong early differentiation signal.
