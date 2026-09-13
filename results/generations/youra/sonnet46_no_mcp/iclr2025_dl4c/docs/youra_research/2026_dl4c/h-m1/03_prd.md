# Product Requirements Document: h-m1
# Reward Density Mechanism Verification — Difficulty-Stratified Curriculum GRPO

**Hypothesis ID:** h-m1
**Type:** MECHANISM (MUST_WORK gate)
**Tier:** FULL (30-task budget)
**Phase 2C Source:** h-m1/02c_experiment_brief.md
**Base Hypothesis:** h-e1 (MUST_WORK gate PASSED)
**Date:** 2026-05-02
**Author:** Anonymous
---

## 1. Executive Summary

H-M1 verifies the causal mechanism behind H-E1's result: that difficulty-stratified curriculum ordering during early GRPO training (steps 0-2500) produces measurably higher **reward density** (fraction of GRPO batches where at least one completion passes unit tests) in the curriculum condition compared to the uniform condition.

This is a **log analysis experiment** — no new model architecture is required. The primary deliverable is a Python analysis script that:
1. Runs full 5000-step GRPO training for all 4 conditions (if not already done)
2. Reads per-condition reward density CSV logs from H-E1 infrastructure
3. Computes Wilcoxon signed-rank test (one-tailed, curriculum > uniform, n=5 paired observations at steps 500-2500)
4. Generates required visualizations

**Gate condition:** `p < 0.05` (one-tailed Wilcoxon), curriculum mean reward density > uniform mean reward density during steps 0-2500.

---

## 2. Problem Statement

GRPO advantage estimates collapse to zero when all G=8 completions in a batch fail (std=0, A_i = 0/0). The hypothesis is that curriculum ordering (easy problems early) maintains higher reward density during early training, preventing this degenerate collapse and producing more effective policy gradient updates.

**What H-M1 must demonstrate:**
- Curriculum condition has statistically significantly higher reward density than uniform during steps 0-2500
- The mechanism (tier-difficulty → solve rate → reward density) is quantitatively confirmed

**Prerequisite state:** H-E1 validated training infrastructure (TRL 1.3.0 GRPOTrainer, APPS+CodeContests pipeline, RewardDensityCallback) but only ran a 10-step smoke test. Full 5000-step training is required to generate meaningful reward density logs.

---

## 3. Functional Requirements

### FR-1: Full Training Execution (if needed)
- **What:** Run full 5000-step GRPO training for all 4 conditions using H-E1 infrastructure
- **Conditions:** curriculum, uniform, easy_only, hard_only
- **Checkpoint interval:** every 500 steps (10 checkpoints per condition)
- **Output:** `h-e1/logs/reward_density_{condition}.csv` (4 files, 10 rows each)
- **Reuse:** H-E1 `code/train.py` with all 4 conditions — NO new training code needed
- **Note:** If logs already contain 10 rows with non-zero values, skip training and proceed to analysis

### FR-2: Reward Density Log Loading
- **What:** Load 4 per-condition reward density CSV files
- **Source:** `h-e1/logs/reward_density_{condition}.csv` where condition ∈ {curriculum, uniform, easy_only, hard_only}
- **Schema:** columns `step`, `reward_density` (float in [0,1])
- **Validation:** Each file must have ≥ 10 rows (full training)
- **Implementation:** `pandas.read_csv()`

### FR-3: Early Phase Extraction
- **What:** Extract reward density observations for steps 0-2500 (early training phase)
- **Window:** Steps 500, 1000, 1500, 2000, 2500 (5 checkpoints)
- **Output:** numpy arrays of shape (5,) per condition
- **Function:** `compute_early_phase_density(df, max_step=2500)`

### FR-4: Primary Statistical Test (Gate Metric)
- **What:** One-tailed Wilcoxon signed-rank test: curriculum > uniform (steps 0-2500)
- **Library:** `scipy.stats.wilcoxon(curriculum_vals, uniform_vals, alternative='greater')`
- **n:** 5 paired checkpoint observations
- **Gate:** p < 0.05 AND curriculum_mean > uniform_mean
- **Output:** `{statistic, p_value, passed, curriculum_mean, uniform_mean, delta}`

### FR-5: Secondary Check (A1 Assumption)
- **What:** Verify easy_only mean reward density ≥ curriculum mean (steps 0-2500)
- **Purpose:** Confirms tier-difficulty correlation assumption
- **Output:** boolean + delta value
- **Not a gate condition** — informational

### FR-6: Mechanism Activation Verification
- **What:** Pre-analysis check that training logs contain full training data (not smoke test)
- **Check:** `len(df) >= 10` for all 4 condition CSVs
- **Failure action:** Trigger full training run (FR-1)

### FR-7: Results Reporting
- **What:** Generate structured results dict and print summary
- **Contents:** p_value, passed, curriculum_mean, uniform_mean, delta, easy_only check, n_checkpoints
- **Gate result:** PASSED/FAILED with reason

### FR-8: Figure Generation — Required (Gate Metrics Bar Chart)
- **What:** Bar chart — mean reward density (steps 0-2500) per condition with std error bars
- **Conditions:** curriculum, uniform, easy_only, hard_only
- **Output:** `h-m1/figures/reward_density_early_phase_bar.png`
- **Library:** matplotlib

### FR-9: Figure Generation — Time Series
- **What:** Line plot — reward density at each 500-step checkpoint for all 4 conditions
- **X-axis:** steps (500-5000); Y-axis: reward density
- **Output:** `h-m1/figures/reward_density_timeseries.png`

### FR-10: Figure Generation — Wilcoxon Box Plot
- **What:** Box plot of reward density distributions (curriculum vs. uniform, steps 0-2500) with p-value annotation
- **Output:** `h-m1/figures/reward_density_wilcoxon_boxplot.png`

### FR-11: Early vs. Late Phase Comparison Figure
- **What:** Side-by-side bar charts comparing steps 0-2500 vs. steps 2501-5000 reward density
- **Purpose:** Verify curriculum advantage is specific to early phase
- **Output:** `h-m1/figures/reward_density_phase_comparison.png`

---

## 4. Data Specification

### Primary Dataset: H-E1 Reward Density Logs

| Property | Value |
|----------|-------|
| Source | h-e1 full training runs (5000 steps, 4 conditions) |
| Format | CSV files: `h-e1/logs/reward_density_{condition}.csv` |
| Schema | columns: `step` (int), `reward_density` (float) |
| Rows per file | 10 (one per 500-step checkpoint) |
| Total observations | 40 (10 × 4 conditions) |
| Analysis window | Steps 0-2500 (checkpoints 1-5, n=5 per condition) |
| Load method | `pd.read_csv(f"h-e1/logs/reward_density_{condition}.csv")` |
| Type | standard (derived from established APPS + CodeContests datasets) |
| Download required | No — generated by H-E1 full training run |

**Dataset Note:** H-E1 smoke test (10 steps) only produced all-zero reward density. H-M1 requires full 5000-step training logs. If logs contain only 10 steps of data, Phase 4 must run full training first.

### Training Dataset (for FR-1, if needed)

| Property | Value |
|----------|-------|
| Datasets | codeparrot/apps + deepmind/code_contests (HuggingFace) |
| Hub names | `codeparrot/apps`, `deepmind/code_contests` (confirmed working in H-E1) |
| Preprocessing | `_tokenize_and_normalize()` — schema unification (H-E1 confirmed) |
| Special handling | `_safe_str()` using `repr()` for large integers |

---

## 5. Models

### Baseline Model (Uniform Condition)
- **Architecture:** DeepSeek-Coder-7B-base (decoder-only transformer, 7B parameters)
- **Source:** `deepseek-ai/DeepSeek-Coder-7B-base` or `h-e1/checkpoints/uniform/`
- **Role:** Control condition — uniform random sampling from APPS+CodeContests
- **Status:** Confirmed working (H-E1 MUST_WORK gate PASSED)

### Proposed Condition (Curriculum)
- **Architecture:** Same DeepSeek-Coder-7B-base
- **Difference:** Training data ordering (APPS tier 0-2 for steps 0-2500, tier 3-4 for steps 2501-5000)
- **Mechanism:** CurriculumCallback step transitions (H-E1 confirmed working)
- **Status:** Confirmed working (H-E1 MUST_WORK gate PASSED)

### Additional Conditions
- **easy_only:** APPS tier 0-2 for all 5000 steps
- **hard_only:** APPS tier 3-4 for all 5000 steps

---

## 6. Evaluation Metrics

### Primary Gate Metric
| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| Reward density | fraction of GRPO batches where max(rewards_per_group) > 0 | curriculum_mean > uniform_mean AND p < 0.05 |

### Statistical Test
| Property | Value |
|----------|-------|
| Test | One-tailed Wilcoxon signed-rank test |
| H0 | curriculum reward density ≤ uniform reward density (steps 0-2500) |
| H1 | curriculum reward density > uniform reward density (steps 0-2500) |
| Significance | p < 0.05 |
| n | 5 paired checkpoint observations (steps 500, 1000, 1500, 2000, 2500) |
| Library | `scipy.stats.wilcoxon(x, y, alternative='greater')` |

### Secondary Metric (Informational)
| Metric | Definition | Expected |
|--------|-----------|---------|
| A1 assumption | easy_only mean ≥ curriculum mean (steps 0-2500) | True |

### Expected Value Ranges
| Condition | Expected Early-Phase Reward Density |
|-----------|-------------------------------------|
| easy_only | 20-40% (highest — all easy problems) |
| curriculum | 15-35% (high early phase, tier 0-2) |
| uniform | 5-20% (lower — mixture of all tiers) |
| hard_only | 1-5% (lowest — near-zero solve rate) |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.40.0
trl==1.3.0
datasets>=2.14.0
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### 7.2 H-E1 Infrastructure (Reused Directly)
| Component | Path | Usage |
|-----------|------|-------|
| Training script | h-e1/code/train.py | Full 5000-step training (FR-1) |
| Reward density function | h-e1/code/training/reward.py | Reference for `compute_reward_density()` |
| CurriculumCallback | h-e1/code/training/callbacks.py | RewardDensityCallback, CurriculumCallback |
| Config | h-e1/code/config.py | GRPOConfig with `generation_kwargs={"max_new_tokens": 512}` |

### 7.3 Key Implementation Fixes (from H-E1)
| Fix | Value |
|-----|-------|
| Dataset hub names | `codeparrot/apps`, `deepmind/code_contests` (NOT hendrycks/apps) |
| TRL API | `GRPOConfig(generation_kwargs={"max_new_tokens": 512})` |
| No `__init__.py` | Do NOT create `code/__init__.py` (shadows built-in `code` module) |
| Large int handling | Use `repr()` not `str()` for large integers |

---

## 8. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| GPU | Single GPU (A100 80GB recommended) |
| CUDA_VISIBLE_DEVICES | Must be set before training |
| Training time | ~8-12 hours per condition for 5000 steps on A100 |
| Analysis time | < 5 minutes (pure log analysis) |
| Reproducibility | Seed=1 (same as H-E1) |
| Output isolation | h-m1/figures/, h-m1/results/ (separate from h-e1) |

---

## 9. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Full training logs exist | ≥ 10 rows per condition CSV | File row count |
| Direction correct | curriculum_mean > uniform_mean (steps 0-2500) | numpy mean comparison |
| Statistical significance | p < 0.05 (one-tailed Wilcoxon) | scipy.stats.wilcoxon |
| Secondary check | easy_only_mean ≥ curriculum_mean | numpy mean comparison |
| Figures generated | 4 figures in h-m1/figures/ | File existence check |

**PoC Pass:** Criteria 1 + 2 + 3 must ALL pass for MUST_WORK gate.

---

## 10. Out of Scope

- New model architecture (H-M1 reuses H-E1 models exactly)
- New training hyperparameters (same TRL GRPOConfig as H-E1)
- HumanEval+/MBPP+ evaluation (that is H-E1's gate metric; H-M1 only measures reward density)
- Statistical tests beyond Wilcoxon (bootstrap CI is optional informational)
