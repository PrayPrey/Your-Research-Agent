# Product Requirements Document: h-m2

**stepsCompleted:** [Phase 2C Review, Problem Statement, Functional Requirements, NFRs, Success Criteria, Data Specification, Dependencies]

**Hypothesis:** h-m2 — Mechanism Hypothesis (SHOULD_WORK / Incremental)
**Type:** MECHANISM (Residual Capability Signal Confirmation)
**Date:** 2026-08-04
**Author:** Anonymous
**Pipeline:** Bidirectional Alignment Gap — Within-Model Verbosity-Controlled
**Base Hypotheses:** h-e1 (PASSED — r_partial=0.9851), h-m1 (PASSED — |β_win|=21.34 >> |β_len|=4.37)

---

## 1. Executive Summary

This experiment confirms the residual capability signal after removing verbosity (avg_length) from both win_rate and LC_winrate using explicit OLS residualization. Specifically: compute ρ(win_rate_resid, lc_resid) via Spearman correlation where residuals are obtained by regressing avg_length out of each variable. By the Frisch-Waugh-Lovell (FWL) theorem, this must be mathematically equivalent to the H-E1 partial correlation (r_partial=0.9851). Gate: SHOULD_WORK (failure documents mechanism complexity, does not invalidate H-E1/H-M1).

**Deliverable:** A Python script that loads the AlpacaEval 2.0 leaderboard CSV, residualizes win_rate and LC_winrate against avg_length via OLS, computes Spearman ρ of residuals with bootstrap CI, and outputs results to `04_validation.md`. Extends h-e1/h-m1 data pipeline with explicit residualization layer.

---

## 2. Problem Statement

**Research Question:** After explicitly removing verbosity (avg_length) from both win_rate and LC_winrate via OLS residualization, does the Spearman correlation of the residuals confirm a positive capability signal (ρ > 0, p < 0.05)?

**Null Hypothesis (H0):** ρ(win_rate_resid, lc_resid) ≤ 0 — no residual capability signal after verbosity removal.

**Alternative Hypothesis (H1):** ρ(win_rate_resid, lc_resid) > 0 AND p < 0.05 (mechanistic FWL confirmation).

**SHOULD_WORK Gate:** Residual correlation must be positive and significant. FWL theorem guarantees |ρ − r_partial_H-E1| < 0.02 if implementation is correct.

**H-E1/H-M1 Context:** r_partial=0.9851 (FWL theorem implies ρ_H-M2 ≈ 0.985). OLS-based residualization is the explicit mechanistic version of partial correlation.

---

## 3. Scope

### In Scope
- Load AlpacaEval 2.0 leaderboard CSV (same as h-e1/h-m1, already cached)
- Regress avg_length out of win_rate → win_rate_resid (OLS lstsq)
- Regress avg_length out of LC_winrate → lc_resid (OLS lstsq)
- Spearman ρ(win_rate_resid, lc_resid) with two-tailed p-value
- Bootstrap CI: 1000 resamples, seed=42
- FWL consistency check: |ρ − 0.9851| < 0.02
- Pingouin consistency check (partial_corr with x_covar/y_covar) as cross-validation
- 5 visualizations (scatter of residuals, distributions, partial regression plot, FWL consistency, bootstrap)
- Output: `04_validation.md` with full results

### Out of Scope
- Model training or fine-tuning
- GPU computation
- New dataset collection
- H-M3/H-C1 analyses (separate hypotheses)
- Causal inference beyond FWL theorem verification

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | AlpacaEval 2.0 Leaderboard |
| Type | standard (pre-computed, public) |
| File | `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` |
| N | 222–223 models (after dropna) |
| Columns Used | `win_rate`, `length_controlled_winrate`, `avg_length` |
| Download | NOT REQUIRED — already cached in repository (reused from h-e1/h-m1) |
| Verified | True (cache_path confirmed in verification_state.yaml) |

**Loading and Preprocessing Code:**
```python
import pandas as pd
import numpy as np

df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
```

**Preprocessing Steps:**
1. Load CSV (same as h-e1/h-m1)
2. Drop rows with NaN in {win_rate, length_controlled_winrate, avg_length}
3. Assert N_clean ≥ 200
4. No standardization needed (residualization is scale-invariant)

**Synthetic Data:** NONE — real AlpacaEval 2.0 leaderboard data only.

### Baseline Model
| Field | Value |
|-------|-------|
| Name | Null model (no residual correlation) |
| Description | ρ(win_rate_resid, lc_resid) = 0 — verbosity fully explains LC preference |
| Purpose | SHOULD_WORK gate comparison |
| Pretrained | N/A — statistical model |

---

## 5. Functional Requirements

### FR-1: Data Loading and Quality Check (Inherited from h-e1/h-m1)
- Load CSV from `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Drop NaN rows in {win_rate, length_controlled_winrate, avg_length}
- Assert N_clean ≥ 200
- Log N_clean to output

### FR-2: OLS Residualization (Core Mechanism — NEW in h-m2)
- Define `regress_out(y, x)` using `numpy.linalg.lstsq` with intercept
- Compute `win_rate_resid = regress_out(win_rate, avg_length)`
- Compute `lc_resid = regress_out(lc_winrate, avg_length)`
- Both residuals are orthogonal to avg_length by construction
- Log residual variance explained (R² of each regression)

### FR-3: Spearman Correlation of Residuals (Primary Test)
- Compute `rho, p_value = scipy.stats.spearmanr(win_rate_resid, lc_resid)`
- Two-tailed p-value
- Gate check: rho > 0 AND p_value < 0.05

### FR-4: Bootstrap Confidence Interval
- 1000 resamples of (win_rate_resid, lc_resid) pairs with replacement
- random_state=42 via `numpy.random.default_rng(42)`
- 95% CI: [np.percentile(boot_rhos, 2.5), np.percentile(boot_rhos, 97.5)]
- CI must exclude 0 for gate pass

### FR-5: FWL Consistency Check
- Compute FWL_delta = |rho - 0.9851| (H-E1 r_partial)
- Flag if FWL_delta > 0.02 (unexpected implementation discrepancy → debug)
- Report FWL_delta as diagnostic metric

### FR-6: Pingouin Cross-Validation (Optional Consistency Check)
- Use `pingouin.partial_corr(data=df, x='win_rate', y='length_controlled_winrate', covar='avg_length')`
- Compare pingouin r against rho from residuals (should match within 0.001)
- Report consistency status

### FR-7: Gate Evaluation
- PRIMARY: passes_gate = (rho > 0) AND (p_value < 0.05)
- CONSISTENCY: fwl_consistent = (FWL_delta < 0.02)
- Log PASS/FAIL for both primary gate and FWL consistency

### FR-8: Visualizations (5 required)
1. **Residuals Scatter Plot:** win_rate_resid vs lc_resid with regression line, Spearman ρ annotation, N annotation
2. **Residual Distribution Histograms:** side-by-side histograms of win_rate_resid and lc_resid (verify approximate normality)
3. **Partial Regression Plot (statsmodels):** Added-variable plot for win_rate controlling avg_length (visual confirmation of H-M2)
4. **FWL Consistency Chart:** Bar/point comparison of H-E1 r_partial vs H-M2 ρ with tolerance band (±0.02)
5. **Bootstrap Distribution:** Histogram of 1000 bootstrap ρ values with 95% CI marked and null (ρ=0) reference line
- Save all to `docs/youra_research/h-m2/figures/`

### FR-9: Results Output
- Write `docs/youra_research/h-m2/04_validation.md` with:
  - Gate result (PASS/FAIL)
  - ρ value, p-value, bootstrap CI
  - FWL_delta (consistency diagnostic)
  - Pingouin cross-validation result
  - Residual variance explained (R² of each preliminary regression)
  - Figure paths
  - Comparison with h-e1 (r_partial=0.9851) for FWL theorem verification

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | All results fully reproducible with seed=42 |
| Performance | Must complete in < 5 minutes on CPU |
| No GPU | Pure statistical analysis, no neural network |
| Dependencies | Only standard Python data science stack |
| Data integrity | Assert N_clean ≥ 200 before any analysis |
| Error handling | Raise explicit errors if CSV missing or N_clean < 200 |
| Code reuse | Reuse h-e1/h-m1 data loading pipeline; add residualization layer |

---

## 7. Dependencies

### 7.1 Python Packages
```
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
statsmodels>=0.13.0
pingouin>=0.5.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 Data Files (Already Cached — NO Download)
- `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` — shared with h-e1/h-m1

### 7.3 External References
- tatsu-lab/alpaca_eval (dataset source, column names)
- numpy.linalg.lstsq (OLS residualization)
- scipy.stats.spearmanr (Spearman correlation)
- pingouin.partial_corr (cross-validation consistency check)
- Dubois 2024 (arXiv 2404.04475) — defines LC_winrate GLM mechanism
- FWL Theorem (Frisch-Waugh-Lovell 1933) — mathematical guarantee of equivalence

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| ρ(win_rate_resid, lc_resid) > 0 | Strict > 0 | SHOULD_WORK gate (primary) |
| p_value < 0.05 | < 0.05 | SHOULD_WORK gate (primary) |
| Bootstrap CI excludes 0 | CI lower bound > 0 | SHOULD_WORK gate (consistency) |
| FWL_delta = |ρ − 0.9851| < 0.02 | < 0.02 | FWL consistency check |
| N_clean ≥ 200 | ≥ 200 | Data integrity |
| All 5 figures generated | 5 files | Completeness |
| 04_validation.md written | Exists | Output completeness |

**Gate Logic:** SHOULD_WORK — gate failure documents mechanism complexity but does not stop pipeline.

**Expected Values (FWL theorem guarantee):**
- ρ ≈ 0.985 (mathematically equivalent to H-E1 r_partial via FWL)
- p ≈ 1.69e-170 (same data, equivalent test)
- FWL_delta < 0.005

---

## 9. Implementation Constraints

- **Hypothesis Type:** MECHANISM (Residual) — FULL tier, max 30 tasks
- **No training loop** — pure statistical analysis
- **Single seed** (42 for bootstrap only; main analysis deterministic)
- **No hyperparameter tuning** — thresholds pre-defined by Phase 2B
- **Alpha = 0.05** fixed
- **n_bootstrap = 1000** fixed
- **random_state = 42** fixed
- **Code reuse from h-e1/h-m1:** data loading + VIF pattern; add regress_out + Spearman on residuals
