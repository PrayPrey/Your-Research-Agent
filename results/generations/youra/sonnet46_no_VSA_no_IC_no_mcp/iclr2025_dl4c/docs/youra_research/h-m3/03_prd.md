# Product Requirements Document: h-m3
# RLEF-Fraction vs RLEF-Binary Comparative Study

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**Hypothesis:** h-m3
**Type:** MECHANISM (INCREMENTAL, base: h-m2)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

---

## 1. Executive Summary

This PRD specifies the implementation of a controlled comparative experiment between two reward formulations for Reinforcement Learning from Execution Feedback (RLEF): fraction-of-tests reward (RLEF-Fraction) and binary all-or-nothing reward (RLEF-Binary). The experiment tests whether the denser gradient signal of fraction reward produces measurably higher pass@1 than binary reward at LiveCodeBench-Hard difficulty.

The experiment reuses SFT and RLEF-Fraction checkpoints from h-E1, requiring only one new training run (RLEF-Binary). Evaluation spans five benchmarks across three difficulty levels to detect a difficulty-reward interaction.

**Gate:** SHOULD_WORK — Δ_Fraction > Δ_Binary at LiveCodeBench-Hard, p < 0.05 (bootstrap). Failure triggers EXPLORE (document null result), not STOP.

---

## 2. Problem Statement

Standard RLEF for code generation uses binary rewards (1 if all tests pass, else 0), providing zero gradient signal for partially-correct solutions. Fraction-of-tests reward provides continuous signal proportional to test-passing rate, potentially enabling learning from partial solutions. Whether this reward structure advantage materializes as higher pass@1 at hard problems — where partial correctness is most prevalent — is the core question.

Recent literature (arXiv 2605.02944, VeRPO arXiv 2601.03525) suggests the advantage may be smaller than expected or non-existent at convergence, making this a scientifically contested SHOULD_WORK hypothesis.

---

## 3. Functional Requirements

### FR-1: RLEF-Binary Training Run

**Description:** Train DeepSeek-Coder-7B with GRPO using binary reward function on APPS train split.

**Reward Function:**
```python
def binary_reward(completions, test_cases, **kwargs):
    """Binary execution reward: 1.0 if ALL tests pass, else 0.0."""
    rewards = []
    for code, tc in zip(completions, test_cases):
        passed = execute_tests(code, tc["inputs"], tc["outputs"])
        rewards.append(1.0 if all(passed) else 0.0)
    return rewards
```

**Training Configuration:**
- Model: deepseek-ai/deepseek-coder-7b-base (SFT checkpoint from h-E1)
- Optimizer: AdamW via GRPOTrainer (lr=1e-6, weight_decay=0.01)
- Batch size: 4 per GPU, gradient accumulation=4 (effective batch=16)
- Group size G: 8 completions per prompt
- max_new_tokens: 512 (corrected from h-m2's 128)
- Steps: Match exactly to RLEF-Fraction run in h-E1 (~1250 steps)
- LR schedule: Cosine decay with 100-step warmup
- Seed: 42

**Acceptance:** Training completes without error; checkpoint saved; reward logs recorded.

### FR-2: Fraction Reward Reference (h-E1 Reuse)

**Description:** RLEF-Fraction checkpoint from h-E1 is reused directly — no re-training.

**Validation:** Verify checkpoint file exists and produces valid generations.

### FR-3: SFT Baseline (h-E1 Reuse)

**Description:** SFT checkpoint from h-E1 is reused directly for Δ computation.

**Validation:** Verify checkpoint file exists; confirm HumanEval pass@1 is in expected range (40–55%).

### FR-4: Reward Mechanism Activation Verification

**Description:** During RLEF-Binary training, verify that fraction and binary rewards would differ on the training batch (confirming partial-correctness exists in APPS).

```python
def verify_reward_formulation_active(fraction_rewards, binary_rewards, threshold=0.01):
    """Verifies fraction and binary rewards differ on training batch."""
    import numpy as np
    mean_fraction = np.mean(fraction_rewards)
    mean_binary = np.mean(binary_rewards)
    indicators = {
        "fraction_mean": mean_fraction,
        "binary_mean": mean_binary,
        "reward_differs": abs(mean_fraction - mean_binary) > threshold,
        "fraction_denser": mean_fraction > mean_binary,
    }
    activated = indicators["reward_differs"] and indicators["fraction_denser"]
    if not activated:
        print("WARNING: Fraction reward not producing denser signal than binary")
    return activated, indicators
```

Log activation status every 50 steps to TensorBoard.

### FR-5: Multi-Benchmark Evaluation

**Description:** Evaluate all 3 models (SFT, RLEF-Fraction, RLEF-Binary) on all 5 benchmarks.

**Benchmarks:**
1. HumanEval — 164 problems (easy reference)
2. MBPP — 374 problems (medium-easy reference)
3. LiveCodeBench-Easy (release_v4 subset)
4. LiveCodeBench-Medium (release_v4 subset)
5. LiveCodeBench-Hard (release_v4 subset, primary gate metric)

**Evaluation Commands:**
```bash
# HumanEval + MBPP (bigcode-evaluation-harness)
accelerate launch main.py --model <checkpoint_path> \
    --tasks humaneval,mbpp \
    --n_samples 1 --batch_size 8 --allow_code_execution \
    --save_generations_path generations_<model>.json

# LiveCodeBench (release_v4, all difficulties)
python -m lcb_runner.runner.main --model <checkpoint_path> \
    --release_version release_v4 --n_workers 4
```

### FR-6: Statistical Hypothesis Test

**Description:** Compute bootstrap p-value for Δ_Fraction > Δ_Binary at LiveCodeBench-Hard.

```python
def bootstrap_delta_test(fraction_results, binary_results, sft_results, n_bootstrap=10000, seed=42):
    """
    Bootstrap test: H0: Δ_Fraction <= Δ_Binary at LCB-Hard.
    Returns p-value for one-tailed test.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    delta_fraction = np.array(fraction_results) - np.array(sft_results)  # binary per-problem
    delta_binary = np.array(binary_results) - np.array(sft_results)
    
    observed_diff = delta_fraction.mean() - delta_binary.mean()
    
    bootstrap_diffs = []
    n = len(delta_fraction)
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_diff = delta_fraction[idx].mean() - delta_binary[idx].mean()
        bootstrap_diffs.append(boot_diff)
    
    p_value = np.mean(np.array(bootstrap_diffs) <= 0)  # one-tailed: fraction <= binary
    return p_value, observed_diff, np.array(bootstrap_diffs)
```

**Gate:** p < 0.05 → PASS; p ≥ 0.05 → EXPLORE (null result documented).

### FR-7: Visualization

**Description:** Generate required and optional figures.

**FR-7.1 (Required):** Bar chart — Δ_Fraction vs Δ_Binary per benchmark (with 95% CI error bars)
**FR-7.2:** Reward signal density trajectory (training steps vs mean reward for both functions)
**FR-7.3:** Absolute pass@1 heatmap (3 models × 5 benchmarks)
**FR-7.4:** Difficulty-scaling interaction line plot (Δ across difficulty levels)
**FR-7.5:** Non-zero reward fraction per difficulty histogram

All figures saved to `docs/youra_research/h-m3/figures/`.

### FR-8: Execution Sandbox

**Description:** Implement isolated code execution for test-case evaluation.

**Requirements:**
- Subprocess isolation (or Docker if available)
- Timeout per execution: 10 seconds
- Safe import whitelist
- Memory limit enforcement

---

## 4. Data Specification

### 4.1 Training Dataset: APPS

| Field | Value |
|-------|-------|
| Name | APPS (Automated Programming Progress Standard) |
| Source | HuggingFace — `codeparrot/apps` |
| Split | `train` (5000 problems) |
| Load | `load_dataset("codeparrot/apps", split="train")` |
| Difficulty filter | All difficulties for training; `difficulties=["competition"]` for hard-only monitoring |
| Features | problem_id, question, solutions, input_output, difficulty |
| Manual download? | NO — auto-downloads via HuggingFace |

**Note:** input_output field contains test cases for reward computation.

### 4.2 Evaluation Dataset: HumanEval

| Field | Value |
|-------|-------|
| Name | HumanEval |
| Source | bigcode-evaluation-harness (`--tasks humaneval`) |
| Problems | 164 |
| Manual download? | NO — harness handles |

### 4.3 Evaluation Dataset: MBPP

| Field | Value |
|-------|-------|
| Name | MBPP |
| Source | bigcode-evaluation-harness (`--tasks mbpp`) |
| Problems | 374 |
| Manual download? | NO — harness handles |

### 4.4 Evaluation Dataset: LiveCodeBench (release_v4)

| Field | Value |
|-------|-------|
| Name | LiveCodeBench |
| Source | LiveCodeBench GitHub harness (`release_v4`) |
| Problems | 713 total (Easy + Medium + Hard) |
| Manual download? | NO — harness downloads; **but repo clone required** |
| Clone command | `git clone https://github.com/LiveCodeBench/LiveCodeBench` |
| Difficulty split | Hard = problems labeled "hard" in release_v4 |

### 4.5 Checkpoints from h-E1 (Inherited)

| Checkpoint | Source | Location |
|-----------|--------|----------|
| SFT | h-E1 | `docs/youra_research/h-e1/code/checkpoints/sft/` |
| RLEF-Fraction | h-E1 | `docs/youra_research/h-e1/code/checkpoints/rlef_fraction/` |

Phase 4 must verify these paths exist before training.

---

## 5. Non-Functional Requirements

### NFR-1: Controlled Comparison Integrity
- Only `reward_funcs` parameter differs between RLEF-Binary and RLEF-Fraction runs
- All other hyperparameters (lr, batch size, G, steps, seed, max_new_tokens) identical
- Same SFT checkpoint used as starting point for both RLEF runs

### NFR-2: Reproducibility
- Fixed seed=42 throughout
- All random states seeded (torch, numpy, Python random)
- Checkpoint every 250 steps

### NFR-3: Hardware Safety
- max_new_tokens=512 (mandatory; 128 caused h-m2 failure)
- G=8 (minimum G=4 per mechanism spec)
- Batch size must fit GPU memory; reduce if OOM (min effective batch=8)

### NFR-4: Evaluation Completeness
- All 3 models must be evaluated before statistical test
- All 5 benchmarks required (no partial evaluation)

### NFR-5: Null Result Handling
- If p ≥ 0.05, do NOT discard — document as null result per SHOULD_WORK gate
- Include mechanism analysis (reward activation logs, loss curves) in documentation

---

## 6. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| RLEF-Binary training completes | No errors, checkpoint saved | Required |
| Reward mechanism activated | fraction_mean > binary_mean on APPS batches | Required |
| All benchmarks evaluated | 3 models × 5 benchmarks | Required |
| Gate: Δ_Fraction > Δ_Binary at LCB-Hard | p < 0.05 (bootstrap) | SHOULD_WORK |
| Null result documented (if p ≥ 0.05) | Full mechanism analysis | EXPLORE path |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
trl>=0.8.0          # GRPOTrainer with reward_funcs API
datasets>=2.18.0    # codeparrot/apps loading
accelerate>=0.27.0  # multi-GPU training
numpy>=1.24.0
scipy>=1.10.0       # bootstrap statistics
matplotlib>=3.7.0   # figures
seaborn>=0.12.0     # heatmap visualization
tensorboard>=2.13.0 # training logging
pyyaml>=6.0
```

### 7.2 External Repositories (Manual Clone Required)

| Repository | Purpose | Clone |
|-----------|---------|-------|
| bigcode-project/bigcode-evaluation-harness | HumanEval + MBPP evaluation | `git clone https://github.com/bigcode-project/bigcode-evaluation-harness` |
| LiveCodeBench/LiveCodeBench | LCB difficulty-stratified eval | `git clone https://github.com/LiveCodeBench/LiveCodeBench` |

### 7.3 Inherited from h-E1

- SFT checkpoint (DeepSeek-Coder-7B fine-tuned on APPS)
- RLEF-Fraction checkpoint
- GRPO training configuration (hyperparameters)

---

## 8. Out of Scope

- VeRPO weighted fraction reward (separate hypothesis if needed)
- Rollout pass-rate control curriculum (separate hypothesis per arXiv 2605.05112)
- Multi-seed runs (single seed=42 per comparison constraint)
- Models other than DeepSeek-Coder-7B (unless SFT ceiling ≥90% triggers 1.3B fallback)
