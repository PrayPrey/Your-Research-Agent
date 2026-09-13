# Product Requirements Document: h-m4
# RLEF-Fraction Monotonic Difficulty Scaling + Scale Sanity Check

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**Hypothesis:** h-m4
**Type:** MECHANISM (INCREMENTAL, base: h-m3 / h-e1)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

---

## 1. Executive Summary

This PRD specifies the implementation of a monotonicity analysis of Δ(RLEF-Fraction, SFT) across five benchmark difficulty levels, plus a DeepSeek-Coder-1.3B scale sanity check. The primary 7B analysis reuses evaluation results from h-e1 — **no new 7B training required**. New compute is required only for the 1.3B SFT and RLEF-Fraction training runs.

The experiment tests whether harder benchmarks yield larger improvement from RLEF-Fraction training, as predicted by the difficulty-scaling hypothesis (arXiv:2603.07779). Statistical confirmation uses the Jonckheere-Terpstra (JT) nonparametric trend test across five ordered groups.

**Gate:** SHOULD_WORK — JT test p < 0.05 (positive trend direction) AND 1.3B Δ ratio ≥ 1.0 (Δ_LCB / Δ_HumanEval). Failure triggers EXPLORE (document null result + report descriptive trend).

**h-m3 limitation context:** h-m3 showed Δ_Fraction ≈ Δ_Binary at LCB-Hard (p=0.552). h-m4 uses a different comparison (RLEF-Fraction vs SFT across difficulty, not Fraction vs Binary), so h-m3's null result does not directly invalidate h-m4. However, absolute Δ values may be modest, potentially limiting JT test power.

---

## 2. Problem Statement

RLEF with fraction-of-tests reward provides denser gradient signal than binary reward. The difficulty-scaling hypothesis predicts that this advantage should be more pronounced on harder problems, where partial correctness is more prevalent and the incremental gradient signal matters most. Confirming monotonic Δ growth across difficulty levels would validate that RLEF-Fraction's gradient density has a difficulty-dependent effect, rather than uniform improvement.

If confirmed, this validates difficulty-stratified training as a principled approach for code generation models. If non-monotonic, the binary (easy vs hard) claim or uniform improvement model would be more appropriate.

---

## 3. Functional Requirements

### FR-1: 7B Re-Analysis (Zero New Training)

**Description:** Collect Δ(RLEF-Fraction, SFT) values at all 5 benchmark difficulty levels from h-e1 validation data. No new training or evaluation required.

**Data Sources:**
- `docs/youra_research/h-e1/04_validation.md` — primary source of pass@1 results for SFT and RLEF-Fraction at 5 benchmarks
- `docs/youra_research/h-e1/experiment_results.json` — raw evaluation results (if available)

**Validation:** All 5 Δ values extracted and non-null; values consistent with h-e1 report.

```python
def load_he1_delta_values(
    he1_results_path: str,  # path to h-e1 evaluation results
) -> dict:                  # {"humaneval": Δ, "mbpp": Δ, "lcb_easy": Δ, "lcb_medium": Δ, "lcb_hard": Δ}
    """Extract Δ(RLEF-Fraction, SFT) from h-e1 results for 7B model."""
    ...
```

**Acceptance:** 5 Δ values loaded, all non-null, humaneval Δ > 0 (from h-e1 prior).

### FR-2: 1.3B SFT Training

**Description:** Fine-tune DeepSeek-Coder-1.3B-base on APPS training split using same SFT procedure as h-e1 7B training. This is a new training run.

**Training Configuration:**
```python
# SFT training for 1.3B (same APPS data + procedure as h-e1 7B SFT)
SFT_CONFIG_1_3B = {
    "model": "deepseek-ai/deepseek-coder-1.3b-base",
    "dataset": "codeparrot/apps",
    "split": "train",
    "optimizer": "AdamW",
    "lr": 2e-5,              # higher than 7B due to smaller model capacity
    "batch_size": 8,         # 1.3B allows larger batch than 7B
    "grad_accum": 4,         # effective batch = 32
    "epochs": 3,
    "max_length": 2048,
    "max_new_tokens": 512,
    "seed": 1,               # same seed as h-e1 for reproducibility
    "precision": "bfloat16",
    "warmup_ratio": 0.1,
    "lr_schedule": "cosine",
}
```

**Acceptance:** Checkpoint saved; HumanEval pass@1 > 20% (sanity check: 1.3B SFT not saturated).

### FR-3: 1.3B RLEF-Fraction Training

**Description:** Fine-tune DeepSeek-Coder-1.3B-SFT checkpoint with GRPO using fraction-of-tests reward on APPS training split.

**Training Configuration:**
```python
# Same fraction_reward_fn as h-e1 (inherited from h-e1/code/reward.py)
GRPO_CONFIG_1_3B = {
    "model": "deepseek-ai/deepseek-coder-1.3b-base",  # start from 1.3B SFT checkpoint
    "reward_funcs": ["fraction_reward_fn"],            # inherited from h-e1
    "num_generations": 8,                              # G=8
    "learning_rate": 1e-5,                             # same as h-e1 7B RLEF-Fraction
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 8,                  # effective batch = 32
    "num_train_epochs": 3,
    "max_prompt_length": 512,
    "max_completion_length": 1024,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.1,
    "seed": 1,
}
```

**Acceptance:** Training completes; mean reward > 0.05 at final step (non-trivial learning signal).

### FR-4: Reward Mechanism Verification (1.3B)

**Description:** During 1.3B RLEF-Fraction training, verify that the fraction reward provides non-zero signal on APPS training batches.

```python
def verify_fraction_reward_active(
    rewards: list[float],
    threshold: float = 0.01,
) -> tuple[bool, dict]:
    """
    Confirms fraction reward is producing non-trivial signal.
    Returns (activated: bool, stats: dict).
    """
    import numpy as np
    mean_reward = float(np.mean(rewards)) if rewards else 0.0
    nonzero_fraction = float(np.mean([r > 0 for r in rewards]))
    activated = mean_reward > threshold
    stats = {
        "mean_reward": mean_reward,
        "nonzero_fraction": nonzero_fraction,
        "activated": activated,
    }
    return activated, stats
```

Log every 50 steps. Acceptance: nonzero_fraction > 0.05 (at least 5% of completions partially correct).

### FR-5: Multi-Benchmark Evaluation (1.3B)

**Description:** Evaluate SFT-1.3B and RLEF-Fraction-1.3B on all 5 benchmarks.

**Benchmarks:**
1. HumanEval — 164 problems (easy)
2. MBPP — 374 problems (medium-easy)
3. LiveCodeBench-Easy (~250 problems)
4. LiveCodeBench-Medium (~250 problems)
5. LiveCodeBench-Hard (~150 problems)

**Total evaluation samples:** ≥1,188 across 5 difficulty levels. Full standard test sets — no subsampling.

**Evaluation Commands:**
```bash
# HumanEval + MBPP
accelerate launch main.py \
    --model <checkpoint_path> \
    --tasks humaneval,mbpp \
    --n_samples 20 --temperature 0.2 \
    --allow_code_execution \
    --metric_output_path results/h-m4/<model_tag>_bigcode.json

# LiveCodeBench (2024-Q4 snapshot)
python -m lcb_runner.runner.main \
    --model <checkpoint_path> \
    --release_version release_v4 \
    --n_workers 4 \
    --output_path results/h-m4/<model_tag>_lcb.json
```

**Note:** n_samples=20 for unbiased pass@1 estimator (bigcode-harness standard).

### FR-6: Jonckheere-Terpstra Monotonicity Test (7B)

**Description:** Run JT nonparametric trend test on Δ values from h-e1 across 5 ordered difficulty groups.

```python
def jonckheere_terpstra(
    groups: list[list[float]],  # 5 groups, ordered by difficulty (HumanEval → LCB-Hard)
) -> tuple[float, float]:       # (J_statistic, p_value)
    """
    Manual JT test via sum of pairwise Mann-Whitney U statistics.
    H₀: No ordered trend in Δ across difficulty groups.
    H₁: Δ increases monotonically with difficulty.
    """
    from scipy.stats import mannwhitneyu, norm
    
    J = 0.0
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            U, _ = mannwhitneyu(groups[j], groups[i], alternative="greater")
            J += U
    
    n = [len(g) for g in groups]
    N = sum(n)
    E_J = (N**2 - sum(ni**2 for ni in n)) / 4
    Var_J = (N**2 * (2*N + 3) - sum(ni**2 * (2*ni + 3) for ni in n)) / 72
    z = (J - E_J) / (Var_J ** 0.5)
    p = 1 - norm.cdf(z)
    return z, p
```

**Gate:** p < 0.05 AND positive trend direction (Z > 0).

**Note:** Since Δ values from h-e1 are point estimates (not per-problem distributions), bootstrap CIs are used to construct pseudo-group distributions for the JT test.

### FR-7: 1.3B Scale Sanity Check

**Description:** Compute Δ ratio for 1.3B model and verify ≥ 1.0.

```python
def compute_delta_ratio_1_3b(
    rlef_results_1_3b: dict,   # {benchmark: pass@1}
    sft_results_1_3b: dict,    # {benchmark: pass@1}
) -> tuple[float, dict]:       # (delta_ratio, delta_dict)
    """
    delta_ratio = Δ_LCB_hard / Δ_HumanEval for 1.3B model.
    Success criterion: delta_ratio >= 1.0.
    """
    delta = {b: rlef_results_1_3b[b] - sft_results_1_3b[b]
             for b in rlef_results_1_3b}
    delta_lcb = delta.get("lcb_hard", 0.0)
    delta_he = delta.get("humaneval", 0.0)
    delta_ratio = delta_lcb / delta_he if delta_he != 0 else 0.0
    return delta_ratio, delta
```

**Gate:** delta_ratio ≥ 1.0.

### FR-8: Verify Monotonicity (7B)

**Description:** Check weak monotonicity of 7B Δ vector before reporting JT test results.

```python
def verify_monotonicity(
    deltas: dict,  # {"humaneval": Δ, "mbpp": Δ, "lcb_easy": Δ, "lcb_medium": Δ, "lcb_hard": Δ}
) -> tuple[bool, list[float]]:  # (is_monotone: bool, ordered_deltas: list)
    """Check weak non-decreasing trend across 5 difficulty levels."""
    ordered_keys = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
    ordered = [deltas[k] for k in ordered_keys]
    is_monotone = all(ordered[i] <= ordered[i+1] for i in range(len(ordered)-1))
    return is_monotone, ordered
```

### FR-9: Visualization

**Description:** Generate required and optional figures.

**FR-9.1 (Required):** Bar chart — Δ(RLEF-Fraction, SFT) per benchmark for 7B and 1.3B, with error bars (bootstrap 95% CI). X-axis: 5 difficulty levels; two bar series (7B, 1.3B).
**FR-9.2:** Monotonicity line plot — Δ vs difficulty level for both 7B and 1.3B; x-axis ordered 1–5; reference line at Δ=0; JT p-value annotated.
**FR-9.3:** Absolute pass@1 heatmap — 4 rows (SFT-7B, RLEF-7B, SFT-1.3B, RLEF-1.3B) × 5 benchmark columns.
**FR-9.4:** Scale comparison panel — side-by-side bars for 7B vs 1.3B Δ values across 5 difficulty levels.

All figures saved to `docs/youra_research/h-m4/figures/`.

---

## 4. Data Specification

### 4.1 Training Dataset: APPS

| Field | Value |
|-------|-------|
| Name | APPS (Automated Programming Progress Standard) |
| Source | HuggingFace — `codeparrot/apps` |
| Split | `train` (5000 problems) |
| Load | `load_dataset("codeparrot/apps", split="train")` |
| Difficulty breakdown | ~800 intro / ~2,300 interview / ~1,900 competition |
| Manual download? | NO — auto-downloads via HuggingFace |

### 4.2 Evaluation Dataset: HumanEval

| Field | Value |
|-------|-------|
| Name | HumanEval |
| Source | bigcode-evaluation-harness (`--tasks humaneval`) |
| Problems | 164 (all used) |
| Manual download? | NO — harness handles |

### 4.3 Evaluation Dataset: MBPP

| Field | Value |
|-------|-------|
| Name | MBPP |
| Source | bigcode-evaluation-harness (`--tasks mbpp`) |
| Problems | 374 sanitised (all used) |
| Manual download? | NO — harness handles |

### 4.4 Evaluation Dataset: LiveCodeBench (2024-Q4 snapshot)

| Field | Value |
|-------|-------|
| Name | LiveCodeBench |
| Source | LiveCodeBench harness (release_v4) |
| Problems | ~650 total (Easy ~250, Medium ~250, Hard ~150) |
| Snapshot | 2024-Q4 (prevents contamination) |
| Manual download? | NO — harness downloads; **repo clone required** |
| Clone command | `git clone https://github.com/LiveCodeBench/LiveCodeBench` |

### 4.5 Checkpoints from h-e1 (Inherited)

| Checkpoint | Source | Location |
|-----------|--------|----------|
| SFT-7B | h-e1 | `docs/youra_research/h-e1/code/checkpoints/sft/` |
| RLEF-Fraction-7B | h-e1 | `docs/youra_research/h-e1/code/checkpoints/rlef_fraction/` |

Phase 4 must verify these paths exist before analysis.

### 4.6 h-e1 Evaluation Results (Reused)

| Data | Source | Location |
|------|--------|----------|
| 7B Δ values (5 benchmarks) | h-e1 | `docs/youra_research/h-e1/04_validation.md` |
| 7B raw results | h-e1 | `docs/youra_research/h-e1/experiment_results.json` |

---

## 5. Non-Functional Requirements

### NFR-1: Controlled Comparison Integrity
- 1.3B RLEF-Fraction uses identical APPS dataset and fraction_reward_fn as 7B in h-e1
- Same bigcode-harness pinned version for all evaluations (7B and 1.3B)
- Same LCB release_v4 snapshot for all evaluations

### NFR-2: Reproducibility
- Fixed seed=1 throughout (same as h-e1 for consistency)
- All random states seeded (torch, numpy, Python random)
- Checkpoint every 500 steps (1.3B trains faster — more frequent saves)

### NFR-3: Hardware Safety
- max_new_tokens=512 (mandatory; consistent with h-e1)
- G=8 (minimum G=4 per mechanism spec)
- 1.3B batch_size=4 per GPU; gradient_accumulation=8 (effective 32)

### NFR-4: Evaluation Completeness
- 1.3B: both SFT and RLEF-Fraction evaluated before computing Δ ratio
- All 5 benchmarks required; no partial evaluation accepted
- n_samples=20 for unbiased pass@1 estimator

### NFR-5: Null Result Handling
- If JT p ≥ 0.05: report actual Δ vector and descriptive trend; explore binary (easy vs hard) claim
- If 1.3B Δ ratio < 1.0: document and report as secondary null
- SHOULD_WORK gate: failure triggers EXPLORE, not STOP

### NFR-6: Statistical Power Note
- h-m3 null result (modest Δ magnitudes) suggests JT test may have limited power
- Report both JT p-value and observed Δ vector regardless of significance

---

## 6. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| h-e1 Δ values extracted (5 benchmarks) | All non-null | Required |
| 1.3B SFT training completes | Checkpoint saved; HumanEval > 20% | Required |
| 1.3B RLEF-Fraction training completes | Checkpoint saved; mean reward > 0.05 | Required |
| 1.3B evaluation completes (5 benchmarks) | Both models × 5 benchmarks | Required |
| Gate: JT p < 0.05 (positive trend, 7B) | p < 0.05, Z > 0 | SHOULD_WORK |
| Gate: 1.3B Δ ratio ≥ 1.0 | Δ_LCB_hard / Δ_HumanEval ≥ 1.0 | SHOULD_WORK |
| Null result documented (if gates fail) | Δ vector + descriptive analysis | EXPLORE path |

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
scipy>=1.10.0       # mannwhitneyu for JT test; norm for p-value
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

### 7.3 Inherited from h-e1

- SFT-7B checkpoint (DeepSeek-Coder-7B fine-tuned on APPS)
- RLEF-Fraction-7B checkpoint
- GRPO training configuration (fraction_reward_fn, hyperparameters)
- Evaluation results at 5 benchmarks (7B Δ values)

### 7.4 Inherited from h-m3

- bigcode-harness invocation wrappers (run_bigcode_eval, run_lcb_eval in h-m3/code/compare.py)
- Evaluation config patterns (BenchmarkPaths, EvalRunConfig dataclasses)

---

## 8. Out of Scope

- New 7B training runs (h-e1 results reused directly)
- Multi-seed replication (single seed=1 per comparison constraint)
- Models other than DeepSeek-Coder-7B and 1.3B
- Curriculum learning or difficulty-stratified training (analysis only, not training intervention)
- Per-difficulty training ablation (future hypothesis if h-m4 passes)
