---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: h-m3
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
base_hypothesis: h-m2
---

# PRD: H-M3 — Proxy Temporal Stability: Gap Retention Over Full Training Budget

## 1. Executive Summary

H-M3 tests whether the gradient concentration advantage of variance-50 over random-50 (lower `frac_reward_zero_std`) is **sustained throughout all training steps** of a warm-start GRPO run (200 steps). H-M2 established the mechanism in principle but failed due to cold-start: all rewards were 0.0, gap = 0.0 throughout. H-M3 redesigns the training configuration (warm-start: max_steps=200, lr=1e-6, max_completion_length=1024) to produce nonzero rewards, enabling temporal analysis of the proxy stability.

**Gate:** SHOULD_WORK — Gap (frac_zero_std(random-50) − frac_zero_std(variance-50)) > 0 at steps 10, 20, AND 50, AND gap_retention (gap_50 / gap_10) ≥ 0.5. Failure triggers EXPLORE — document proxy degradation rate.

**Prerequisite:** H-M2 FAILED (SHOULD_WORK — limitation recorded, non-blocking). H-M3 is a redesigned experiment, not a re-run of H-M2.

**Key Difference from H-M2:** Three warm-start config changes (max_steps 50→200, lr 5e-7→1e-6, max_completion_length 512→1024). All other components reused from H-M2 codebase.

---

## 2. Problem Statement

H-M2 confirmed the infrastructure works (TRL GRPOTrainer, binary reward, MBPP) but failed to produce nonzero rewards in 50 steps. H-M3 tests the temporal dimension: even if variance-50 provides gradient signal advantage at step 10, does that advantage degrade as training progresses and the model policy evolves away from the frozen proxy's assumptions? GradAlign (arXiv:2602.21492) and VI-CuRL (arXiv:2602.12579) suggest offline proxies degrade as policies shift. H-M3 quantifies this degradation (or its absence) via gap_retention.

---

## 3. Functional Requirements

### FR-1: Load H-E1 Variance-50 Problem IDs
- Load `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- Extract `top_ids` key → 50 MBPP task_ids (warm-start requires same subset as H-M2)
- Store as `variance_50_ids: list[int]` (50 task_ids)
- Validate: exactly 50 IDs; all present in MBPP full/train split

### FR-2: Load MBPP Dataset
- Load via HuggingFace Datasets: `load_dataset("google-research-datasets/mbpp", "full", split="train")`
- 374 problems (task_ids 601-974)
- Fields: `task_id` (int), `text` (prompt), `code` (reference), `test_list` (list of assert strings)
- **Difference from H-M2 PRD:** `subset="full"` not `"sanitized"` — matches actual H-M2 code

### FR-3: Construct Variance-50 Dataset (Condition A)
- Filter MBPP full/train to problems with `task_id` in `variance_50_ids`
- Expected: exactly 50 problems; validate count

### FR-4: Construct Random-50 Dataset (Condition B)
- `rng = numpy.random.default_rng(42); random_ids = rng.choice(374_task_ids, 50, replace=False)`
- Same construction as H-M2 for controlled comparison

### FR-5: Binary Execution Reward Function
- Reuse `make_execution_reward()` from H-M2 `reward.py`
- Reward: 1.0 if all `test_list` assertions pass, 0.0 otherwise
- Subprocess execution with `exec_timeout=5.0s`
- Compatible with TRL GRPOTrainer `reward_funcs` interface

### FR-6: Warm-Start GRPO Training — Condition A (Variance-50)
- Model: `deepseek-ai/deepseek-coder-7b-instruct-v1.5` (bfloat16, device_map="auto")
- **Warm-start config (differs from H-M2):**
  - `max_steps=200` (was 50)
  - `learning_rate=1e-6` (was 5e-7)
  - `max_completion_length=1024` (was 512)
- **Same as H-M2:** num_generations=4, generation_batch_size=4, beta=0.0, use_vllm=False, seed=42, logging_steps=1, save_strategy="no"
- Dataset: variance-50 (50 problems)
- Output dir: `docs/youra_research/h-m3/results/variance50/`
- Early-stop criterion: if `max(rewards/reward_fn/mean) == 0.0` after first 50 steps → terminate, log cold-start EXPLORE finding

### FR-7: Warm-Start GRPO Training — Condition B (Random-50)
- Identical warm-start config as FR-6
- Dataset: random-50 (50 problems)
- Output dir: `docs/youra_research/h-m3/results/random50/`

### FR-8: Warm-Start Validation
```python
def verify_warm_start_succeeded(log_history_var50, log_history_rnd50):
    var_rewards = [e.get("rewards/reward_fn/mean", 0.0)
                   for e in log_history_var50 if "rewards/reward_fn/mean" in e]
    rnd_rewards = [e.get("rewards/reward_fn/mean", 0.0)
                   for e in log_history_rnd50 if "rewards/reward_fn/mean" in e]
    warm_start_ok = any(r > 0.0 for r in var_rewards + rnd_rewards)
    return warm_start_ok, {"max_reward_var50": max(var_rewards, default=0.0),
                           "max_reward_rnd50": max(rnd_rewards, default=0.0)}
```
If `warm_start_ok = False` → log cold-start; proceed to EXPLORE output; skip gate evaluation.

### FR-9: Extract `frac_reward_zero_std` Per Step
- From `trainer.state.log_history` after each run
- Extract per-step values for all logged steps (up to 200)
- Validate: values ∈ [0.0, 1.0] for each condition

### FR-10: Compute Gap Trajectory and Gate Metrics at Checkpoints 10, 20, 50
```python
gap_by_step = {step: frac_rnd[step] - frac_var[step] for step in logged_steps}
gap_at_10 = gap_by_step.get(10, 0.0)
gap_at_20 = gap_by_step.get(20, 0.0)
gap_at_50 = gap_by_step.get(50, 0.0)
gap_retention = gap_at_50 / gap_at_10 if gap_at_10 > 0 else 0.0

# P1 gate
p1_pass = gap_at_10 > 0 and gap_at_20 > 0 and gap_at_50 > 0
# P2 secondary
p2_pass = gap_retention >= 0.5 if gap_at_10 > 0 else False
gate_passed = p1_pass  # primary gate
```

### FR-11: Mechanism Verification Asserts
```python
assert all(0.0 <= v <= 1.0 for v in frac_var_series), "Invalid frac values"
assert all(0.0 <= v <= 1.0 for v in frac_rnd_series), "Invalid frac values"
print(f"[H-M3] Warm-start: {warm_start_ok}")
print(f"[H-M3] P1 gate: gap_10={gap_at_10:.3f}, gap_20={gap_at_20:.3f}, gap_50={gap_at_50:.3f}")
print(f"[H-M3] P2 retention: {gap_retention:.3f} (threshold: >=0.5)")
print(f"[H-M3] Gate passed: {gate_passed}")
```

### FR-12: Results JSON
Save `docs/youra_research/h-m3/results/gate_results.json`:
```json
{
  "warm_start_succeeded": bool,
  "gate_passed": bool,
  "p1_pass": bool,
  "p2_pass": bool,
  "gap_by_checkpoint": {"10": float, "20": float, "50": float},
  "gap_retention": float,
  "frac_reward_zero_std_per_step": {
    "variance50": [float, ...],
    "random50": [float, ...]
  },
  "max_rewards": {"variance50": float, "random50": float},
  "variance_50_ids": [int, ...],
  "random_50_ids": [int, ...],
  "config": {
    "max_steps": 200, "learning_rate": 1e-6, "max_completion_length": 1024,
    "num_generations": 4, "seed": 42
  }
}
```

### FR-13: Visualization — 4 Figures
- **Fig 1 (mandatory — gate metric):** Grouped bar chart comparing `frac_reward_zero_std` at steps 10, 20, 50 for variance-50 vs random-50
- **Fig 2 — Gap Trajectory:** Line plot of gap = frac_zero_std(random-50) − frac_zero_std(variance-50) across all logged steps (up to 200). Horizontal reference at gap=0. Red region if gap < 0. Title: "Proxy Stability: Gap Trajectory Over Training Steps"
- **Fig 3 — Per-Condition Curves:** Two lines (variance-50, random-50) for frac_reward_zero_std over all logged steps
- **Fig 4 — Gap Retention Bar:** Bar at steps 10, 20, 50 showing gap value; annotate P2 retention threshold (gap_50/gap_10 = 0.5)

Output: `docs/youra_research/h-m3/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset: MBPP
- **Source:** HuggingFace `google-research-datasets/mbpp`, `subset="full"`, `split="train"`
- **Auto-download:** Yes (HuggingFace Datasets API) — no manual task needed
- **Size:** 374 problems (task_ids 601-974)
- **Loading code:**
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", "full", split="train")
  ```

### 4.2 Variance-50 IDs (from H-E1 artifact)
- **Source:** `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- **Key:** `top_ids` field (list of 50 task_ids)
- **Local file:** Present — no download needed

### 4.3 No Additional Datasets
- H-M3 is a training-dynamics experiment; no separate evaluation set
- HumanEval+ NOT needed (H-M3 tests `frac_reward_zero_std`, not pass@1)

---

## 5. Training Configuration

### Model
- **ID:** `deepseek-ai/deepseek-coder-7b-instruct-v1.5`
- **dtype:** bfloat16
- **device_map:** `"auto"`

### GRPOConfig (Warm-Start)

| Parameter | H-M2 Value | H-M3 Value | Change |
|-----------|-----------|-----------|--------|
| `num_generations` | 4 | 4 | Same |
| `generation_batch_size` | 4 | 4 | Same |
| `max_steps` | 50 | **200** | Warm-start |
| `learning_rate` | 5e-7 | **1e-6** | Warm-start |
| `max_completion_length` | 512 | **1024** | Warm-start |
| `beta` | 0.0 | 0.0 | Same |
| `logging_steps` | 1 | 1 | Same |
| `save_strategy` | "no" | "no" | Same |
| `use_vllm` | False | False | Same |
| `seed` | 42 | 42 | Same |

---

## 6. Evaluation Metrics

| Metric | Type | Gate | Threshold |
|--------|------|------|-----------|
| gap_at_10 = frac_rnd(10) − frac_var(10) > 0 | Primary | P1 | Required |
| gap_at_20 = frac_rnd(20) − frac_var(20) > 0 | Primary | P1 | Required |
| gap_at_50 = frac_rnd(50) − frac_var(50) > 0 | Primary | P1 | Required |
| gap_retention = gap_50 / gap_10 ≥ 0.5 | Secondary | P2 | ≥ 0.5 |
| warm_start_succeeded (max_reward > 0) | Validity | Pre-gate | Required |

**PoC Pass Condition:**
1. Both training runs complete (or early-stop gracefully) without error
2. `warm_start_succeeded = True` (at least one nonzero reward)
3. P1: gap > 0 at steps 10, 20, AND 50

**Failure Modes:**
- Cold-start persists (warm_start_ok=False) → EXPLORE: scope limitation documented
- Gap never positive → EXPLORE: proxy provides no temporal advantage
- Gap degrades (retention < 0.5) → Partial finding: proxy degrades; report rate

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.35
trl>=0.15.0          # frac_reward_zero_std metric; processing_class parameter
datasets>=2.0
numpy>=1.20
matplotlib>=3.5
accelerate>=0.20
pandas>=1.3          # log analysis
```

### 7.2 Local Artifacts (no download)
- `docs/youra_research/h-e1/results/mbpp_variance_profile.json` — variance-50 IDs (`top_ids` key)
- `docs/youra_research/h-m2/code/` — base codebase to reuse/extend

### 7.3 Base Hypothesis Code Reuse
- H-M2 `reward.py`: `make_execution_reward()` — reused as-is
- H-M2 `dataset.py`: `load_variance_50_ids()`, `build_subset()` — reused as-is
- H-M2 `train.py`: `run_grpo()` — modified for warm-start config
- H-M2 `analyze.py`: `extract_frac_zero_std()` — extended with gap_trajectory, gap_retention
- H-M2 `visualize.py`: all 4 plot functions — extended with 200-step x-axis range

---

## 8. Non-Functional Requirements

- **Reproducibility:** seed=42; same random-50 sampling as H-M2 (`numpy.random.default_rng(42)`)
- **Compute:** Two GRPO runs × 200 steps × 50 problems. Estimated: ~16 minutes total on H100 NVL
- **Isolation:** Condition A and B use identical GRPOConfig (only dataset differs)
- **Early-stop:** If frac_reward_zero_std = 1.0 for all of first 50 steps → terminate, log EXPLORE finding
- **Logging:** `frac_reward_zero_std` must appear in `trainer.state.log_history` every step (validate count before analysis)
- **Output:** All artifacts in `docs/youra_research/h-m3/`

---

## 9. Success Criteria

**PASS (P1):** gap > 0 at ALL of steps 10, 20, 50 AND warm_start_succeeded
**PASS + P2:** Also gap_retention ≥ 0.5 (proxy stable through step 50)
**PARTIAL:** Warm-start succeeded but gap degrades (retention < 0.5) → document degradation rate
**EXPLORE:** Warm-start fails (cold-start persists) → scope limitation; proxy temporal stability cannot be tested
