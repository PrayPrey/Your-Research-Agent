# Product Requirements Document: h-m3

**stepsCompleted:** [Phase 2C Review, Problem Statement, Functional Requirements, NFRs, Success Criteria, Data Specification, Dependencies]

**Hypothesis:** h-m3 — Mechanism Hypothesis (SHOULD_WORK / Incremental)
**Type:** MECHANISM (Capability-Quartile Delta Distribution Test)
**Date:** 2026-08-04
**Author:** Anonymous
**Pipeline:** Bidirectional Alignment Gap — Within-Model Verbosity-Controlled
**Base Hypotheses:** h-e1 (PASSED — r_partial=0.9851), h-m1 (PASSED — |β_win|=21.34 >> |β_len|=4.37), h-m2 (PASSED — rho_resid=0.9739)

---

## 1. Executive Summary

This experiment tests whether the bidirectional alignment gap (Δ = LC_winrate − win_rate) is smaller for high-capability models by applying Kruskal-Wallis nonparametric ANOVA on Δ across win_rate quartiles (Q1=lowest, Q4=highest capability). The experiment leverages the full AlpacaEval 2.0 leaderboard (N=222), reuses all h-e1/h-m1/h-m2 data infrastructure, and adds: (1) Delta computation, (2) quartile binning via pd.qcut, (3) Kruskal-Wallis H-test, (4) Dunn post-hoc with Bonferroni (H-C1 forward-compatibility), (5) OLS on Δ to partial out mathematical composition artifact. Gate: SHOULD_WORK — failure documents scope limitation but does not invalidate H-E1/H-M1/H-M2.

**Deliverable:** A Python script that loads the AlpacaEval 2.0 leaderboard CSV, computes Δ = LC_winrate − win_rate, bins models into win_rate quartiles, runs Kruskal-Wallis H-test, secondary Spearman and OLS analyses, and outputs results with visualizations to `docs/youra_research/h-m3/`.

---

## 2. Problem Statement

**Research Question:** Is the bidirectional alignment gap (Δ = LC_winrate − win_rate) significantly different across capability quartiles, and does high capability correspond to smaller (less negative) Δ?

**Null Hypothesis (H0):** Median Δ is equal across Q1, Q2, Q3, Q4 capability quartiles.

**Alternative Hypothesis (H1):** Kruskal-Wallis p < 0.05 — Delta distributions differ significantly across quartiles, with Q4 (highest capability) having the least-negative Δ.

**SHOULD_WORK Gate:** Kruskal-Wallis on Δ across win_rate quartiles must yield p < 0.05. Given r_partial=0.9851 from H-E1, mathematical expectation is p << 0.001.

**Known Mathematical Dependency:** Δ = LC_winrate − win_rate contains −win_rate, creating mathematical (non-causal) dependency. OLS Δ ~ win_rate_std + avg_length_std addresses this as secondary analysis; Kruskal-Wallis remains the primary gate test.

---

## 3. Scope

### In Scope
- Load AlpacaEval 2.0 leaderboard CSV (cached, shared with h-e1/h-m1/h-m2)
- Compute Δ = length_controlled_winrate − win_rate
- Bin models into win_rate quartiles via pd.qcut (Q1=lowest, Q4=highest capability)
- Verify group sizes ≥ 5 each (Kruskal-Wallis requirement)
- Primary gate: Kruskal-Wallis H-test on Δ across Q1–Q4
- Effect size: epsilon-squared = (H − k + 1) / (N − k)
- Secondary: Spearman ρ(win_rate, Δ) with bootstrap CI (note mathematical dependency caveat)
- Secondary: OLS Δ ~ win_rate_std + avg_length_std (partial contribution)
- Dunn post-hoc (Bonferroni) for pairwise comparisons, specifically Q1 vs Q4
- Descriptive statistics: quartile median Δ, quartile group sizes
- 4+ visualizations saved to `docs/youra_research/h-m3/figures/`
- Output: `docs/youra_research/h-m3/04_validation.md`

### Out of Scope
- Model training or fine-tuning
- GPU computation
- New dataset collection
- H-C1 primary analysis (uses Dunn results but H-C1 gates separately)
- Causal inference on the mathematical dependency

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
| Derived | `delta` = length_controlled_winrate − win_rate; `quartile` = pd.qcut(win_rate, 4) |
| Download | NOT REQUIRED — already cached in repository (reused from h-e1/h-m1/h-m2) |
| Verified | True (cache_path confirmed in verification_state.yaml) |

**Loading and Preprocessing Code:**
```python
import pandas as pd
import numpy as np

df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
df['delta'] = df['length_controlled_winrate'] - df['win_rate']
df['quartile'] = pd.qcut(df['win_rate'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
assert all(df.groupby('quartile').size() >= 5), "Kruskal-Wallis requires >= 5 per group"
```

**Expected Delta Range:** Approximately [−0.40, +0.10] based on prior pipeline (mean Δ ≈ −16.37pp from h-m1).
**Expected N per quartile:** ~55 models (222/4 = 55.5) — well above Kruskal-Wallis minimum.

**Synthetic Data:** NONE — real AlpacaEval 2.0 leaderboard data only.

### Baseline Model
| Field | Value |
|-------|-------|
| Name | Null model (equal Δ distributions across quartiles) |
| Description | H0: Kruskal-Wallis H = 0, equal median Δ across Q1–Q4 |
| Purpose | SHOULD_WORK gate comparison |
| Pretrained | N/A — statistical model only |

---

## 5. Functional Requirements

### FR-1: Data Loading and Quality Check (Inherited from h-e1/h-m1/h-m2)
- Load CSV from `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Drop NaN rows in {win_rate, length_controlled_winrate, avg_length}
- Assert N_clean ≥ 200
- Log N_clean to output

### FR-2: Delta Computation and Quartile Binning (Core — NEW in h-m3)
- Compute `delta = length_controlled_winrate − win_rate`
- Create quartile labels: `pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])`
- Q1 = lowest win_rate (lowest capability), Q4 = highest win_rate (highest capability)
- Verify each quartile has ≥ 5 models (Kruskal-Wallis requirement)
- Log group sizes per quartile

### FR-3: Kruskal-Wallis H-Test (Primary Gate Test)
- Extract Delta values per quartile: `q_groups = [df[df['quartile']==q]['delta'].values for q in ['Q1','Q2','Q3','Q4']]`
- Run: `H_stat, kw_p = scipy.stats.kruskal(*q_groups)`
- Gate check: kw_p < 0.05
- Log H statistic and p-value

### FR-4: Effect Size Computation
- Compute epsilon-squared: `epsilon_sq = (H_stat - len(q_groups) + 1) / (len(df) - len(q_groups))`
- Interpretation: > 0.06 = medium effect, > 0.14 = large effect
- Report alongside Kruskal-Wallis result

### FR-5: Quartile Descriptive Statistics
- Compute median Δ per quartile
- Compute mean Δ per quartile
- Compute IQR (Q25–Q75) per quartile
- Log monotonic trend check: is median_Q1 < median_Q2 < median_Q3 < median_Q4?

### FR-6: Secondary — Spearman ρ(win_rate, Δ)
- `rho_raw, p_rho = scipy.stats.spearmanr(df['win_rate'], df['delta'])`
- Note mathematical dependency caveat (Δ contains −win_rate)
- Bootstrap CI: 1000 resamples, random_state=42
- Report with explicit caveat label: "NOTE: mathematical dependency present"

### FR-7: Secondary — OLS Δ ~ win_rate_std + avg_length_std
- Standardize win_rate and avg_length via StandardScaler
- OLS with intercept via statsmodels: `sm.OLS(df['delta'], sm.add_constant(X_std)).fit()`
- Report β_win_rate_std, β_avg_length_std, p-values, R²
- Purpose: partial out composition artifact, show contribution of avg_length to Δ separately

### FR-8: Dunn Post-Hoc Test (H-C1 Forward-Compatibility)
- Run only if Kruskal-Wallis p < 0.05
- `scikit_posthocs.posthoc_dunn(df, val_col='delta', group_col='quartile', p_adjust='bonferroni')`
- Focus on Q1 vs Q4 pairwise comparison (core directionality)
- Store full 4×4 pairwise p-value matrix for H-C1 use

### FR-9: Gate Evaluation
- PRIMARY: passes_gate = (kw_p < 0.05)
- DIRECTIONALITY: monotonic_trend = (median_Q1 < median_Q4)
- Log PASS/FAIL for primary gate and directionality check

### FR-10: Visualizations (4 required)
1. **Boxplot:** Δ distribution per quartile (Q1–Q4) with median lines, jittered data points, Kruskal-Wallis p-value annotation, Dunn Q1 vs Q4 significance bracket
2. **Scatter Plot:** win_rate vs Δ with quartile color-coding (4 colors), LOWESS trend line, Spearman ρ annotation (with dependency caveat)
3. **Dunn Post-Hoc Heatmap:** 4×4 pairwise Bonferroni-corrected p-values (color-coded, log scale)
4. **Quartile Median Bar Chart:** Median Δ per quartile with error bars (IQR), monotonic trend annotation
- Save all to `docs/youra_research/h-m3/figures/`

### FR-11: Results Output
- Write `docs/youra_research/h-m3/04_validation.md` with:
  - Gate result (PASS/FAIL) with Kruskal-Wallis H, p, epsilon-squared
  - Quartile median Δ table (monotonic trend check)
  - Spearman ρ(win_rate, Δ) with caveat and bootstrap CI
  - OLS results: β_win_rate_std, β_avg_length_std, R²
  - Dunn Q1 vs Q4 pairwise p-value
  - Figure paths
  - Comparison with H-E1/H-M1/H-M2 for pipeline coherence

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | All results fully reproducible with seed=42 |
| Performance | Must complete in < 5 minutes on CPU |
| No GPU | Pure statistical analysis, no neural network |
| Dependencies | Standard Python data science stack + scikit-posthocs |
| Data integrity | Assert N_clean ≥ 200 and quartile group sizes ≥ 5 before Kruskal-Wallis |
| Error handling | Raise explicit errors if CSV missing, N_clean < 200, or any quartile < 5 |
| Code reuse | Reuse h-e1/h-m1/h-m2 data loading; add delta/quartile/KW layer |

---

## 7. Dependencies

### 7.1 Python Packages
```
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
scikit-posthocs>=0.7.0
statsmodels>=0.13.0
scikit-learn>=1.0.0
pingouin>=0.5.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 Data Files (Already Cached — NO Download)
- `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` — shared with h-e1/h-m1/h-m2

### 7.3 External References
- scipy.stats.kruskal — primary gate test API
- scikit-posthocs.posthoc_dunn — Dunn post-hoc with Bonferroni
- statsmodels.OLS — secondary OLS on Delta
- sklearn.preprocessing.StandardScaler — standardization for OLS
- tatsu-lab/alpaca_eval — dataset source and column definitions
- Dubois 2024 (arXiv:2404.04475) — defines LC_winrate GLM mechanism

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Kruskal-Wallis p < 0.05 | < 0.05 | SHOULD_WORK gate (primary) |
| Quartile group sizes ≥ 5 each | ≥ 5 | Data integrity |
| N_clean ≥ 200 | ≥ 200 | Data integrity |
| Monotonic median trend Q1 < Q4 | Strict | Directionality check |
| All 4 figures generated | 4 files | Completeness |
| 04_validation.md written | Exists | Output completeness |

**Gate Logic:** SHOULD_WORK — gate failure (p ≥ 0.05) documents scope limitation; pipeline continues to H-C1 regardless.

**Expected Values (from prior pipeline strength):**
- Kruskal-Wallis H >> 100 (given rho=0.9851 from H-E1); p << 0.001
- epsilon-squared > 0.14 (large effect)
- Median Δ monotonically increases Q1 → Q4 (Q1 most negative, Q4 least negative)
- Dunn Q1 vs Q4 p << 0.001 (Bonferroni-corrected)

---

## 9. Implementation Constraints

- **Hypothesis Type:** MECHANISM (Quartile-Stratified) — FULL tier, max 30 tasks
- **No training loop** — pure statistical analysis
- **Single seed** (42 for bootstrap only; Kruskal-Wallis is deterministic)
- **No hyperparameter tuning** — alpha=0.05, n_bootstrap=1000, random_state=42 fixed
- **Alpha = 0.05** fixed (per Phase 2B plan)
- **n_bootstrap = 1000** fixed (consistency with h-e1/h-m1/h-m2)
- **random_state = 42** fixed
- **Quartile binning:** pd.qcut with q=4 (equal-frequency, not equal-width)
- **scikit-posthocs required** for Dunn post-hoc (new dependency vs h-m2)
