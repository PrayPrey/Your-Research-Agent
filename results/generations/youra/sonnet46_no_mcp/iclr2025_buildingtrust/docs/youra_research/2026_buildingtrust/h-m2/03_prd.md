# Product Requirements Document: H-M2
# Epistemic Composite Predictive Validity for Adversarial Robustness

---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_metrics
  - success_criteria
  - dependencies
---

## Executive Summary

**Hypothesis ID:** H-M2
**Type:** MECHANISM (SHOULD_WORK gate)
**Pipeline Position:** Phase 3 — Implementation Planning

H-M2 tests whether the epistemic reliability composite (ECE + TruthfulQA% + Brier score) has **predictive validity** for adversarial robustness beyond raw capability. Building on H-E1 (cross-property correlation structure) and H-M1 (capability-independent calibration-hallucination link), H-M2 asks: does knowing a model's calibration and hallucination profile give out-of-sample predictive signal about adversarial failure?

**This is a purely statistical analysis experiment** — no model training, no GPU required. All evaluation data is reused from H-E1's score matrix (N=30 × 8 columns, already computed).

**PoC Success:** Composite LOO-AUC ≥ 0.70 AND ΔR² ≥ 0.10 with bootstrap 95% CI excluding zero.

---

## Problem Statement

Given the N=30 LLM population with precomputed benchmark scores (H-E1 output), we need to determine whether:
1. The partial correlation ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40 (capability-independent adversarial link)
2. The composite epistemic predictor (ECE + TruthfulQA% + Brier) achieves LOO-AUC ≥ 0.70 for top-quartile AdvGLUE failure prediction
3. The composite exceeds MMLU-only baseline by ΔR² ≥ 0.10 with bootstrap 95% CI excluding zero

**Gate Behavior (SHOULD_WORK):**
- Full pass: Both criteria met → H-M2 PASS, proceed to H-M3
- Partial pass (AUC 0.60–0.70 or ΔR² 0.05–0.10): Document limitation, proceed to H-M3
- Explore (AUC < 0.60 or ΔR² CI includes zero): Downgrade predictive claim; H-E1/H-M1 still valid; proceed to H-M3

---

## Functional Requirements

### FR-1: Score Matrix Loading
**Source:** H-E1 Phase 4 output
- Load `{research_folder}/h-e1/score_matrix.csv` (N=30 × 8 columns)
- Required columns: `model_id`, `ECE`, `Brier`, `TruthfulQA_pct`, `AdvGLUE_drop`, `ANLI_drop`, `MMLU_acc`, `HumanEval_pass1`
- Validate all 30 rows present, no NaN in key columns
- Derive `top_quartile_advglue` binary label: 1 if AdvGLUE_drop ≥ 75th percentile, else 0

### FR-2: Partial Spearman Correlation Analysis
**Primary gate metric (secondary):**
- Compute partial ρ(ECE, AdvGLUE_drop | MMLU_acc) using pingouin `partial_corr`
- Compute partial ρ(ECE, ANLI_drop | MMLU_acc) using pingouin `partial_corr`
- Bootstrap 10,000 BCa CIs for both partial correlations
- Expected: partial ρ(ECE, AdvGLUE_drop | MMLU) ≈ -0.65 to -0.72

### FR-3: LOO Logistic Regression — Composite Predictor
**Primary gate metric:**
- Features: ECE, TruthfulQA_pct, Brier (standardized via StandardScaler)
- Target: `top_quartile_advglue` (binary, N_pos ≈ 7–8)
- Protocol: LeaveOneOut cross-validation (N=30 iterations)
- Model: LogisticRegression(C=1.0, max_iter=1000)
- Output: LOO probability scores → AUC-ROC via `roc_auc_score`
- Gate: LOO-AUC ≥ 0.70

### FR-4: LOO Logistic Regression — MMLU-Only Baseline
- Feature: MMLU_acc only (standardized)
- Same LOO protocol as FR-3
- Output: Baseline LOO-AUC
- Purpose: ΔR² computation

### FR-5: ΔR² Bootstrap CI
**Primary gate metric:**
- ΔR² = AUC_composite − AUC_MMLU_only (using AUC as proxy)
- Bootstrap 10,000 resamples of LOO-AUC difference
- Compute 95% percentile CI; check if lower bound > 0
- Gate: ΔR² ≥ 0.10 AND bootstrap 95% CI excludes zero

### FR-6: Results Reporting
- Print all gate metrics with pass/fail status
- Save structured results to `h-m2/results.json`
- Generate 6+ required figures (see Visualization Requirements)
- Write `h-m2/04_validation.md` summary

### FR-7: Ablation — MMLU-Only Baseline (explicit comparison)
- Run identical LOO protocol with MMLU_acc as sole predictor
- Compare ROC curves: composite vs. MMLU-only
- Report coefficient stability across LOO folds for composite

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42 for all random operations
- Deterministic LOO protocol (no random train/test splits)
- All bootstrap CIs use `np.random.default_rng(42)`

### NFR-2: Compute Efficiency
- No GPU required — CPU-only statistical analysis
- Estimated runtime: < 10 minutes total
- Memory: < 1 GB

### NFR-3: Code Quality
- Single self-contained script: `h-m2/run_experiment.py`
- All gate checks automated (no manual inspection required)
- Clear console output: pass/fail for each criterion

### NFR-4: Statistical Rigor
- LOO (not k-fold) for N=30 — gold standard for small-N AUC estimation
- BCa bootstrap for partial ρ CIs (not normal approximation)
- Percentile bootstrap for ΔR² CI (robust for N=30)

---

## Data Specification

### Section 4: Input Data

| Dataset | Source | Role | New Collection? |
|---------|--------|------|-----------------|
| H-E1 Score Matrix | `h-e1/score_matrix.csv` | PRIMARY INPUT | **No — reused** |
| MMLU | lm-eval-harness (already in score matrix) | ECE/Brier/MMLU_acc | **No** |
| TruthfulQA | lm-eval-harness (already in score matrix) | TruthfulQA_pct | **No** |
| AdvGLUE | lm-eval-harness (already in score matrix) | AdvGLUE_drop (PRIMARY OUTCOME) | **No** |
| ANLI | lm-eval-harness (already in score matrix) | ANLI_drop (secondary check) | **No** |

**Score Matrix Schema (N=30 × 8):**
```
model_id (str), ECE (float), Brier (float), TruthfulQA_pct (float),
AdvGLUE_drop (float), ANLI_drop (float), MMLU_acc (float), HumanEval_pass1 (float)
```

**Derived column:**
```
top_quartile_advglue (int): 1 if AdvGLUE_drop >= 75th percentile (top 7-8 models), else 0
```

**No manual data download tasks required** — H-E1 score matrix is already on disk.

---

## Evaluation Metrics

### Primary Gate Metrics (PoC pass condition):
1. **LOO-AUC (composite):** `roc_auc_score(y_true, y_proba_composite)` ≥ 0.70
2. **ΔR² (composite − MMLU-only):** ≥ 0.10 with bootstrap 95% CI lower bound > 0

### Secondary Metrics (informative):
3. **partial ρ(ECE, AdvGLUE_drop | MMLU):** ≥ 0.40 with BCa CI excluding zero
4. **partial ρ(ECE, ANLI_drop | MMLU):** ≥ 0.30 (robustness check)
5. **LOO-AUC (MMLU-only baseline):** Expected 0.55–0.65

### Expected Performance (from H-E1/H-M1 context):
- partial ρ(ECE, AdvGLUE_drop | MMLU) ≈ -0.65 to -0.72
- LOO-AUC composite ≈ 0.75–0.85
- LOO-AUC MMLU-only ≈ 0.55–0.65
- ΔR² ≈ 0.15–0.25

---

## Success Criteria

### PoC Gate (SHOULD_WORK):
- **PASS:** LOO-AUC composite ≥ 0.70 AND ΔR² ≥ 0.10 with 95% CI excluding zero
- **PARTIAL:** 0.60 ≤ AUC < 0.70 OR 0.05 ≤ ΔR² < 0.10 → document limitation, proceed to H-M3
- **EXPLORE:** AUC < 0.60 OR ΔR² CI includes zero → downgrade predictive claim, proceed to H-M3

### Code Quality Gate:
- Script runs without error on H-E1 score matrix
- All gate checks automated and printed to console
- All 6+ figures saved to `h-m2/figures/`

---

## Dependencies (Section 7)

### 7.1 Python Packages (environment setup task required)
```
pandas >= 2.0.0
pingouin >= 0.5.3
scipy >= 1.11.0
numpy >= 1.24.0
scikit-learn >= 1.3.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
```
**Note:** All packages inherited from H-E1/H-M1 environment — likely already installed. Environment setup task should verify installation.

### 7.2 External Repositories (reference only)
- EleutherAI/lm-evaluation-harness: Score matrix source (already evaluated in H-E1)
- raphaelvallat/pingouin: Partial correlation computation (used in H-M1)
- scikit-learn/scikit-learn: LOO logistic regression, AUC-ROC

### 7.3 Local Dependencies (from H-E1)
- `h-e1/score_matrix.csv` — **PRIMARY INPUT** (must exist before running H-M2)
- H-E1/H-M1 validation reports — for expected performance context

---

## Visualization Requirements

All figures saved to `h-m2/figures/`:

1. **gate_metrics_comparison.png** — Bar chart: LOO-AUC composite vs. MMLU-only with bootstrap 95% CI error bars; annotate pass/fail vs. 0.70 threshold; ΔR² annotation
2. **roc_curves_comparison.png** — ROC curve overlay: composite vs. MMLU-only LOO predictions with AUC annotations
3. **partial_correlation_comparison.png** — Bar chart of partial ρ(ECE, AdvGLUE drop | MMLU) and partial ρ(ECE, ANLI drop | MMLU) with BCa CIs; comparison to H-M1 partial ρ
4. **advglue_drop_distribution.png** — Histogram of AdvGLUE_drop (N=30) with top-quartile threshold; colored by model family
5. **feature_importance.png** — Standardized logistic regression coefficients for composite predictor across LOO folds
6. **epistemic_vs_adversarial_scatter.png** — Scatter: composite epistemic score (PC1 from H-E1) vs. AdvGLUE_drop; colored by model family; regression line

---

*Generated by Phase 3 Implementation Planning — H-M2*
*Date: 2026-04-30*
*No new data collection required — reuses H-E1 score matrix*
