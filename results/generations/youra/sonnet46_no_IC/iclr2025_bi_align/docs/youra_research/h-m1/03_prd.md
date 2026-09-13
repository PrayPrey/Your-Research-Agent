# Product Requirements Document: h-m1

**stepsCompleted:** [Phase 2C Review, Problem Statement, Functional Requirements, NFRs, Success Criteria, Data Specification, Dependencies]

**Hypothesis:** h-m1 — Mechanism Hypothesis (MUST_WORK / Incremental)
**Type:** MECHANISM (PoC)
**Date:** 2026-08-04
**Author:** Anonymous
**Pipeline:** Bidirectional Alignment Gap — Within-Model Verbosity-Controlled
**Base Hypothesis:** h-e1 (PASSED — r_partial=0.9851, p=1.69e-170, VIF=1.764)

---

## 1. Executive Summary

This experiment tests whether capability (win_rate) dominates verbosity (avg_length) as a predictor of LC_winrate using standardized OLS regression. Specifically: in OLS(LC_winrate ~ win_rate_std + avg_length_std) on N=222 AlpacaEval 2.0 models, we require |β_win_rate_std| > |β_avg_length_std| (or Shapley(win_rate) > Shapley(avg_length) if VIF ≥ 5). This is a statistical observational study — no model training, no GPU computation. Gate: MUST_WORK.

**Deliverable:** A Python script that loads the AlpacaEval 2.0 leaderboard CSV, standardizes predictors, runs OLS with VIF-contingent dominance check, and outputs results to `04_validation.md`. Extends h-e1 data pipeline with StandardScaler + OLS layers.

---

## 2. Problem Statement

**Research Question:** Does model capability (win_rate) dominate verbosity (avg_length) as a predictor of length-debiased preference (LC_winrate), or is verbosity the dominant predictor?

**Null Hypothesis (H0):** |β_win_rate_std| ≤ |β_avg_length_std| — verbosity dominates or ties capability as predictor of LC preference.

**Alternative Hypothesis (H1):** |β_win_rate_std| > |β_avg_length_std| AND p_win < 0.05 (OLS path), OR Shapley(win_rate) > Shapley(avg_length) (fallback when VIF ≥ 5).

**MUST_WORK Gate:** H-M1 dominance check must pass to confirm mechanism chapter of bidirectional alignment paper.

**H-E1 Context:** VIF confirmed at 1.764 (well below 5.0) → OLS beta path is valid. r_partial=0.9851 strongly implies β_win_rate_std >> β_avg_length_std.

---

## 3. Scope

### In Scope
- Load AlpacaEval 2.0 leaderboard CSV (same as h-e1, already cached)
- StandardScaler normalization of win_rate and avg_length
- VIF diagnostic (reuse h-e1 infrastructure; expected ~1.764)
- Standardized OLS: LC_winrate ~ win_rate_std + avg_length_std
- Dominance check: |β_win_rate_std| > |β_avg_length_std|
- OLS diagnostics: Breusch-Pagan test, Q-Q plot of residuals, residuals vs fitted
- Fallback (VIF ≥ 5): sklearn permutation_importance (n_repeats=30, seed=42)
- Verbosity-only null model: LC_winrate ~ avg_length_std (baseline comparison)
- 6 visualizations
- Output: `04_validation.md` with full results

### Out of Scope
- Model training or fine-tuning
- GPU computation
- New dataset collection
- H-M2/H-M3/H-C1 analyses (separate hypotheses)
- Causal inference beyond OLS coefficient comparison

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | AlpacaEval 2.0 Leaderboard |
| Type | standard (pre-computed, public) |
| File | `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` |
| N | 222 models |
| Columns Used | `win_rate`, `length_controlled_winrate`, `avg_length` |
| Download | NOT REQUIRED — already cached in repository (reused from h-e1) |
| Verified | True (cache_path confirmed in verification_state.yaml) |

**Loading and Preprocessing Code:**
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"

scaler = StandardScaler()
df['win_rate_std'] = scaler.fit_transform(df[['win_rate']])
df['avg_length_std'] = scaler.fit_transform(df[['avg_length']])
```

**Preprocessing Steps:**
1. Load CSV (same as h-e1)
2. Drop rows with NaN in {win_rate, length_controlled_winrate, avg_length}
3. Assert N_clean ≥ 200
4. Apply StandardScaler to win_rate → win_rate_std (zero mean, unit variance)
5. Apply StandardScaler to avg_length → avg_length_std
6. Add OLS intercept via sm.add_constant()

**Synthetic Data:** NONE — real AlpacaEval 2.0 leaderboard data only.

### Baseline Model
| Field | Value |
|-------|-------|
| Name | Verbosity-only null model |
| Formula | LC_winrate ~ avg_length_std (OLS, standardized) |
| Purpose | Establish β_avg_length_std without capability predictor |
| Pretrained | N/A — statistical model |

---

## 5. Functional Requirements

### FR-1: Data Loading and Quality Check (Inherited from h-e1)
- Load CSV from `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Drop NaN rows in {win_rate, length_controlled_winrate, avg_length}
- Assert N_clean ≥ 200
- Log N_clean to output

### FR-2: StandardScaler Normalization (NEW in h-m1)
- Apply sklearn StandardScaler to win_rate → win_rate_std
- Apply sklearn StandardScaler to avg_length → avg_length_std
- Verify: mean ≈ 0, std ≈ 1 for each standardized column
- Add OLS intercept column via sm.add_constant()

### FR-3: VIF Diagnostic (Inherited from h-e1 pattern)
- Compute VIF for win_rate_std and avg_length_std using statsmodels.stats.outliers_influence.variance_inflation_factor
- Log VIF values; flag if any VIF ≥ 5.0 (triggers fallback path)
- Expected from h-e1: win_rate=1.764, avg_length=1.764

### FR-4: Verbosity-Only Baseline (NEW in h-m1)
- Fit OLS: LC_winrate ~ avg_length_std (with constant)
- Extract β_avg_length_std from baseline model
- Report baseline R²

### FR-5: Standardized OLS — Primary Path (VIF < 5)
- Fit OLS: LC_winrate ~ win_rate_std + avg_length_std (with constant)
- Extract β_win_rate_std = |params[1]|, β_avg_length_std = |params[2]|
- Extract p_win = pvalues[1], p_len = pvalues[2]
- Report R², adjusted R²
- Evaluate dominance: |β_win_rate_std| > |β_avg_length_std| AND p_win < 0.05

### FR-6: OLS Diagnostics (NEW in h-m1)
- Breusch-Pagan test for heteroscedasticity (statsmodels.stats.diagnostic.het_breuschpagan)
- Q-Q plot of OLS residuals (normality check)
- Residuals vs fitted scatter plot

### FR-7: Permutation Importance Fallback (VIF ≥ 5 path)
- If VIF ≥ 5: fit sklearn LinearRegression on [win_rate_std, avg_length_std]
- permutation_importance(model, X_std, y, n_repeats=30, random_state=42)
- Compare importances_mean[0] (win_rate) vs importances_mean[1] (avg_length)
- Report: Shapley(win_rate) > Shapley(avg_length)

### FR-8: Gate Evaluation
- PRIMARY (OLS): passes_gate = (|β_win_rate_std| > |β_avg_length_std|) AND (p_win < 0.05)
- FALLBACK (permutation): passes_gate = (imp_win > imp_len)
- Log PASS/FAIL with path taken (OLS_beta or permutation_importance)

### FR-9: Visualizations (6 required)
1. **Dominance bar chart**: |β_win_rate_std| vs |β_avg_length_std| with p-value annotations
2. **Standardized coefficient plot**: horizontal bar chart with 95% CI error bars
3. **VIF diagnostic bar chart**: VIF(win_rate_std), VIF(avg_length_std) with threshold line at 5.0
4. **OLS residuals vs fitted**: scatter for heteroscedasticity check
5. **Q-Q plot**: normality of OLS residuals
6. **Scatter with color**: win_rate_std vs LC_winrate, colored by avg_length quartile
- Save all to `docs/youra_research/h-m1/figures/`

### FR-10: Results Output
- Write `docs/youra_research/h-m1/04_validation.md` with:
  - Gate result (PASS/FAIL)
  - Path taken (OLS_beta / permutation_importance)
  - β_win_rate_std, β_avg_length_std, p-values
  - R², adjusted R²
  - VIF values
  - OLS diagnostics summary
  - Figure paths
  - Comparison with h-e1 (r_partial=0.9851) for narrative continuity

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
| Code reuse | Reuse h-e1 data loading pipeline; add StandardScaler layer |

---

## 7. Dependencies

### 7.1 Python Packages
```
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
statsmodels>=0.13.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.12.0
```
**Note:** `pingouin` NOT required for h-m1 (used OLS, not partial_corr). `scikit-learn` added for StandardScaler and permutation_importance.

### 7.2 Data Files (Already Cached — NO Download)
- `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` — shared with h-e1

### 7.3 External References
- tatsu-lab/alpaca_eval (dataset source, column names)
- statsmodels OLS (primary regression engine)
- sklearn StandardScaler + permutation_importance (normalization + fallback)
- Dubois 2024 (arXiv 2404.04475) — defines LC_winrate GLM mechanism

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| |β_win_rate_std| > |β_avg_length_std| | Strict > | MUST_WORK gate (OLS path) |
| p_win < 0.05 | < 0.05 | MUST_WORK gate (OLS path) |
| VIF < 5.0 for both predictors | < 5.0 | OLS path validity (expected from h-e1) |
| Shapley(win_rate) > Shapley(avg_length) | Strict > | MUST_WORK gate (fallback path) |
| N_clean ≥ 200 | ≥ 200 | Data integrity |
| All 6 figures generated | 6 files | Completeness |
| 04_validation.md written | Exists | Output completeness |

**Gate Logic:** OLS path (VIF < 5) or fallback path (VIF ≥ 5) — exactly one path must pass.

**Expected Values (from h-e1):**
- VIF ~ 1.764 → OLS path active
- r_partial = 0.9851 strongly implies |β_win_rate_std| ≈ 0.8–0.99, |β_avg_length_std| ≈ 0.01–0.20

---

## 9. Implementation Constraints

- **Hypothesis Type:** MECHANISM (PoC) — FULL tier, max 30 tasks
- **No training loop** — pure statistical analysis
- **Single seed** (42 for permutation_importance fallback only)
- **No hyperparameter tuning** — thresholds pre-defined by Phase 2B
- **Alpha = 0.05** fixed
- **VIF threshold = 5.0** fixed
- **n_repeats = 30** for permutation_importance (fixed)
- **Code reuse from h-e1:** data loading + VIF pattern; add StandardScaler + OLS steps
