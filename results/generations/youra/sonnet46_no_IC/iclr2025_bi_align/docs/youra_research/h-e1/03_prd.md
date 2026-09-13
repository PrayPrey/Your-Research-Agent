# Product Requirements Document: h-e1

**stepsCompleted:** [Phase 2C Review, Problem Statement, Functional Requirements, NFRs, Success Criteria, Data Specification, Dependencies]

**Hypothesis:** h-e1 — Existence Hypothesis (MUST_WORK / Foundation)
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-04
**Author:** Anonymous
**Pipeline:** Bidirectional Alignment Gap — Within-Model Verbosity-Controlled

---

## 1. Executive Summary

This experiment tests whether model capability (win_rate) independently predicts length-debiased preference (LC_winrate) after controlling for response verbosity (avg_length), using Spearman partial correlation on the AlpacaEval 2.0 leaderboard dataset (N=222 models). This is a statistical observational study — no model training, no GPU computation. The gate condition is MUST_WORK: if partial correlation fails (r_partial ≤ 0 OR p ≥ 0.05 OR |r_partial| < 0.15), the pipeline stops and routes to Phase 0.

**Deliverable:** A Python script that loads the AlpacaEval 2.0 leaderboard CSV, computes Spearman partial correlation (win_rate, LC_winrate | avg_length), performs bootstrap robustness check, and outputs results to `04_validation.md`.

---

## 2. Problem Statement

**Research Question:** Does model capability independently predict length-debiased preference beyond verbosity, or is the win_rate → LC_winrate relationship fully mediated by avg_length?

**Null Hypothesis (H0):** ρ(win_rate, LC_winrate | avg_length) = 0 — no independent capability-preference association after controlling for verbosity.

**Alternative Hypothesis (H1):** ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15 — capability independently predicts length-debiased preference.

**MUST_WORK Gate:** H-E1 partial correlation must pass to enable downstream H-M1, H-M2, H-M3, H-C1 hypotheses.

---

## 3. Scope

### In Scope
- Load AlpacaEval 2.0 leaderboard CSV (pre-computed, publicly available)
- VIF diagnostic for multicollinearity check
- Spearman partial correlation: ρ(win_rate, LC_winrate | avg_length)
- One-sided test (alternative='greater': r > 0)
- Bootstrap robustness: 1000 resamples, seed=42
- Gate evaluation: r_partial > 0, p < 0.05, |r_partial| ≥ 0.15
- 5 visualizations (scatter, partial regression, bootstrap distribution, VIF diagnostic, Δ pattern)
- Output: `04_validation.md` with full results

### Out of Scope
- Model training or fine-tuning
- GPU computation
- New dataset collection
- Causal inference beyond observational correlation
- H-M1/H-M2/H-M3/H-C1 analysis (separate hypotheses)

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
| Download | NOT REQUIRED — already cached in repository |
| Verified | True (cache_path confirmed in verification_state.yaml) |

**Loading Code:**
```python
import pandas as pd
df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
```

**Preprocessing:**
1. Drop rows with NaN in any of {win_rate, length_controlled_winrate, avg_length}
2. Assert N_clean ≥ 200 (data integrity gate)
3. No normalization (Spearman is rank-based, scale-invariant)

**Synthetic Data:** NONE — real AlpacaEval 2.0 leaderboard data only.

### Baseline Model
- **Type:** Statistical null hypothesis (H0: r_partial = 0)
- **No model artifact to load**
- **Baseline performance:** r_partial = 0 (no association)

---

## 5. Functional Requirements

### FR-1: Data Loading and Quality Check
- Load CSV from `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Drop NaN rows in {win_rate, length_controlled_winrate, avg_length}
- Assert N_clean ≥ 200
- Log N_clean to output

### FR-2: VIF Diagnostic
- Compute VIF for win_rate and avg_length using statsmodels
- Log VIF values; flag if any VIF ≥ 5.0 (multicollinearity warning)

### FR-3: Spearman Partial Correlation (Primary)
- Use `pingouin.partial_corr(data=df, x='win_rate', y='length_controlled_winrate', covar='avg_length', method='spearman', alternative='greater')`
- Extract: r_partial, p_val, CI95, n
- Evaluate gate: r_partial > 0 AND p_val < 0.05 AND |r_partial| ≥ 0.15

### FR-4: Bootstrap Robustness
- 1000 bootstrap resamples (with replacement, n=N_clean each), seed=42
- Compute Spearman partial r for each resample
- Report 95% bootstrap CI [lower, upper]
- Secondary gate check: bootstrap CI lower bound > 0

### FR-5: Gate Evaluation
- Evaluate: passes_gate = (r_partial > 0) AND (p_val < 0.05) AND (|r_partial| >= 0.15)
- Log PASS/FAIL with values

### FR-6: Visualizations (5 required)
1. Scatter plot: win_rate vs LC_winrate, color by avg_length quartile
2. Partial regression plot: residualized win_rate vs residualized LC_winrate
3. Bootstrap histogram: 1000 r_partial values with CI bands
4. VIF diagnostic bar chart: VIF(win_rate), VIF(avg_length)
5. Δ scatter: (LC_winrate − win_rate) vs win_rate with trend line
- Save all to `docs/youra_research/h-e1/figures/`

### FR-7: Results Output
- Write `docs/youra_research/h-e1/04_validation.md` with:
  - Gate result (PASS/FAIL)
  - r_partial, p_val, CI95, n
  - Bootstrap CI
  - VIF values
  - Figure paths
  - Interpretation

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

---

## 7. Dependencies

### 7.1 Python Packages
```
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
pingouin>=0.5.3
statsmodels>=0.13.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 Data Files (Already Cached)
- `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` — NO download needed

### 7.3 External References
- tatsu-lab/alpaca_eval (column name confirmation)
- raphaelvallat/pingouin (partial_corr API)
- statsmodels (VIF, OLS)

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| r_partial > 0 | > 0 | MUST_WORK gate |
| p_val < 0.05 | < 0.05 | MUST_WORK gate |
| \|r_partial\| ≥ 0.15 | ≥ 0.15 | MUST_WORK gate |
| Bootstrap CI lower > 0 | > 0 | Secondary confirmation |
| N_clean ≥ 200 | ≥ 200 | Data integrity |
| All 5 figures generated | 5 files | Completeness |
| 04_validation.md written | Exists | Output completeness |

**Gate Logic:** ALL three primary criteria must pass (AND condition). Failure on any → pipeline stops → route to Phase 0.

---

## 9. Implementation Constraints

- **Hypothesis Type:** EXISTENCE (PoC) — LIGHT tier, max 15 tasks
- **No training loop** — pure statistical analysis
- **Single seed** (42 for bootstrap only)
- **No hyperparameter tuning** — thresholds are pre-defined by Phase 2B
- **Alpha = 0.05** fixed (not tunable)
- **r_partial threshold = 0.15** fixed (not tunable)
