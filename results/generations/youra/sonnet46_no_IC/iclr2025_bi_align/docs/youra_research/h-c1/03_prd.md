# Product Requirements Document: h-c1

**stepsCompleted:** [Phase 2C Review, Problem Statement, Functional Requirements, NFRs, Success Criteria, Data Specification, Dependencies]

**Hypothesis:** h-c1 — Condition Hypothesis (SHOULD_WORK / Incremental)
**Type:** CONDITION (Boundary/Scope Verification — Quartile Monotonicity of LC_winrate)
**Date:** 2026-08-04
**Author:** Anonymous
**Pipeline:** Bidirectional Alignment Gap — Within-Model Verbosity-Controlled
**Base Hypotheses:** h-e1 (PASSED — r_partial=0.9851), h-m1 (PASSED — |β_win|=21.34 >> |β_len|=4.37), h-m2 (PASSED — rho_resid=0.9739), h-m3 (PASSED — KW H=22.19, p=5.97e-05)

---

## 1. Executive Summary

This experiment tests whether the capability-alignment relationship is monotonic at population extremes by applying Kruskal-Wallis nonparametric ANOVA and Dunn post-hoc on **LC_winrate** (not Δ) across win_rate quartiles. The experiment leverages the full AlpacaEval 2.0 leaderboard (N=222), reuses all h-e1/h-m1/h-m2/h-m3 data infrastructure, and adds: (1) LC_winrate as the direct dependent variable (not the composed Δ), (2) Kruskal-Wallis on LC_winrate, (3) Dunn post-hoc Q1 vs Q4 with Bonferroni correction, (4) monotonic trend check Q1 < Q2 < Q3 < Q4. Gate: SHOULD_WORK — failure documents that the relationship holds at population level but not at quartile extremes.

**Deliverable:** A Python script that loads the AlpacaEval 2.0 leaderboard CSV, bins models into win_rate quartiles, runs Kruskal-Wallis H-test on LC_winrate, Dunn post-hoc Q1 vs Q4 (Bonferroni), and outputs results with visualizations to `docs/youra_research/h-c1/`.

**Key Distinction from H-M3:** H-M3 tested KW on Δ = LC_winrate − win_rate (alignment gap). The Dunn Q1 vs Q4 on Δ yielded p=1.0 (non-significant). H-C1 tests LC_winrate **directly**, which — given r_partial=0.9851 — is expected to be strongly monotone with win_rate quartiles, making this test much more likely to pass.

---

## 2. Problem Statement

**Research Question:** Is the capability-LC preference relationship monotonic at population extremes — specifically, does the Q1 (lowest capability) vs Q4 (highest capability) difference in LC_winrate remain significant after Bonferroni correction?

**Null Hypothesis (H0):** Median LC_winrate is equal across Q1, Q2, Q3, Q4 capability quartiles.

**Alternative Hypothesis (H1):** KW p < 0.05 on LC_winrate AND Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05.

**SHOULD_WORK Gate (Primary):** KW p < 0.05 on LC_winrate AND Dunn Q1 vs Q4 Bonferroni p < 0.05. Expected to pass given r_partial=0.9851 from H-E1 — LC_winrate tracks win_rate extremely closely.

**Gate Failure Interpretation:** If gate fails, document that the capability-alignment relationship holds at the population level (H-E1–H-M3 all PASS) but may not be monotonic at quartile extremes. Narrow scope accordingly and proceed.

---

## 3. Scope

### In Scope
- Load AlpacaEval 2.0 leaderboard CSV (cached, shared with h-e1/h-m1/h-m2/h-m3)
- Bin models into win_rate quartiles via pd.qcut (Q1=lowest, Q4=highest capability) — same split as h-m3
- Verify group sizes ≥ 5 each (Kruskal-Wallis requirement)
- Primary gate: Kruskal-Wallis H-test on **LC_winrate** across Q1–Q4
- Primary gate: Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05 on LC_winrate
- Effect size: epsilon-squared = (H − k + 1) / (N − k)
- Dunn post-hoc full 4×4 pairwise matrix (Bonferroni, m=6 pairs)
- Monotonic trend check: Q1 < Q2 < Q3 < Q4 medians (secondary — not required for gate)
- Descriptive statistics: quartile median LC_winrate, quartile group sizes
- Bootstrap CI on Dunn Q1 vs Q4 p-value (1000 resamples, random_state=42)
- 4+ visualizations saved to `docs/youra_research/h-c1/figures/`
- Output: `docs/youra_research/h-c1/04_validation.md`
- Comparison with H-M3: side-by-side display of Δ (H-M3) vs LC_winrate (H-C1) quartile results

### Out of Scope
- Model training or fine-tuning
- GPU computation
- New dataset collection
- Testing on Δ (H-M3 already covers this)
- Causal inference

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
| Derived | `quartile` = pd.qcut(win_rate, 4); no Δ computation needed |
| Download | NOT REQUIRED — already cached in repository (reused from h-e1/h-m1/h-m2/h-m3) |
| Verified | True (cache_path confirmed in verification_state.yaml) |

**Loading and Preprocessing Code:**
```python
import pandas as pd
import numpy as np

df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
df['quartile'] = pd.qcut(df['win_rate'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
assert all(df.groupby('quartile', observed=True).size() >= 5), "KW requires >= 5 per group"
```

**Expected N per quartile:** ~55 models (222/4 = 55.5) — from h-m3: Q1=56, Q2=56, Q3=55, Q4=56.  
**Expected LC_winrate range:** ~5% to ~68% (correlates very closely with win_rate given r_partial=0.9851).

**Synthetic Data:** NONE — real AlpacaEval 2.0 leaderboard data only.

### Baseline Model
| Field | Value |
|-------|-------|
| Name | Null model (equal LC_winrate distributions across quartiles) |
| Description | H0: Kruskal-Wallis H = 0, equal median LC_winrate across Q1–Q4 |
| Purpose | SHOULD_WORK gate comparison |
| Pretrained | N/A — statistical model only |

---

## 5. Functional Requirements

### FR-1: Data Loading and Quality Check (Inherited from h-e1/h-m1/h-m2/h-m3)
- Load CSV from `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Drop NaN rows in {win_rate, length_controlled_winrate, avg_length}
- Assert N_clean ≥ 200
- Log N_clean to output

### FR-2: Quartile Binning (Identical to H-M3)
- Create quartile labels: `pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])`
- Q1 = lowest win_rate (lowest capability), Q4 = highest win_rate (highest capability)
- Verify each quartile has ≥ 5 models (Kruskal-Wallis requirement)
- Log group sizes per quartile
- Note: No Δ computation in H-C1 — DV is LC_winrate directly

### FR-3: Kruskal-Wallis H-Test on LC_winrate (Primary Gate Test Part 1)
- Extract LC_winrate values per quartile: `q_groups = [df[df['quartile']==q]['length_controlled_winrate'].values for q in ['Q1','Q2','Q3','Q4']]`
- Run: `H_stat, kw_p = scipy.stats.kruskal(*q_groups)`
- Primary gate check part 1: kw_p < 0.05
- Log H statistic and p-value

### FR-4: Effect Size Computation
- Compute epsilon-squared: `epsilon_sq = (H_stat - len(q_groups) + 1) / (len(df) - len(q_groups))`
- Interpretation: > 0.06 = medium effect, > 0.14 = large effect
- Expected: ε² >> 0.14 (given r_partial=0.9851, LC_winrate tracks win_rate closely)

### FR-5: Dunn Post-Hoc Q1 vs Q4 (Primary Gate Test Part 2)
- Run Dunn post-hoc with Bonferroni: `sp.posthoc_dunn(df, val_col='length_controlled_winrate', group_col='quartile', p_adjust='bonferroni')`
- Extract Q1 vs Q4 p-value: `p_q1_q4 = dunn_result.loc['Q1', 'Q4']`
- Primary gate check part 2: p_q1_q4 < 0.05
- Store full 4×4 pairwise p-value matrix
- Log all pairwise Bonferroni-corrected p-values

### FR-6: Quartile Descriptive Statistics
- Compute median LC_winrate per quartile
- Compute mean LC_winrate per quartile
- Compute IQR (Q25–Q75) per quartile
- Log monotonic trend check: is median_Q1 < median_Q2 < median_Q3 < median_Q4?

### FR-7: Gate Evaluation
- PRIMARY (SHOULD_WORK): passes_gate = (kw_p < 0.05) AND (dunn_q1_q4_p < 0.05)
- SECONDARY: monotonic_trend = all(medians[q] < medians[q_next]) for consecutive quartiles
- Log PASS/FAIL for gate and monotonic trend separately

### FR-8: Comparison with H-M3 Results
- Log H-M3 KW result (H=22.19, p=5.97e-05, ε²=0.0876) for comparison
- Log H-M3 Dunn Q1 vs Q4 Bonferroni p=1.0 (on Δ)
- Contrast with H-C1 results on LC_winrate to show DV distinction

### FR-9: Visualizations (4 required)
1. **Boxplot:** LC_winrate distribution per quartile (Q1–Q4) with median lines, jittered data points, KW p-value annotation, Dunn Q1 vs Q4 significance bracket
2. **Dunn Heatmap:** 4×4 pairwise Bonferroni-corrected p-value heatmap (log scale, green=significant, red=not)
3. **Monotonicity Plot:** Quartile median LC_winrate with 95% bootstrap CI error bars — shows whether trend is monotonic
4. **Comparison with H-M3:** Side-by-side median bars for Δ (H-M3) vs LC_winrate (H-C1) per quartile to show why H-C1 is a cleaner test
- Save all to `docs/youra_research/h-c1/figures/`

### FR-10: Results Output
- Write `docs/youra_research/h-c1/04_validation.md` with:
  - Gate result (PASS/FAIL) with KW H, p, epsilon-squared
  - Dunn Q1 vs Q4 Bonferroni p-value (primary gate condition)
  - Quartile median LC_winrate table (monotonic trend check)
  - Full 4×4 Dunn pairwise p-value matrix
  - Comparison with H-M3 Dunn Q1 vs Q4 on Δ (p=1.0)
  - Figure paths

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
| Code reuse | Reuse h-m3 data loading + quartile binning; replace DV from Δ to LC_winrate |

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
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 Data Files (Already Cached — NO Download)
- `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` — shared with h-e1/h-m1/h-m2/h-m3

### 7.3 External References
- scipy.stats.kruskal — primary KW gate test
- scikit-posthocs.posthoc_dunn — Dunn post-hoc with Bonferroni (m=6 pairs for 4 groups)
- tatsu-lab/alpaca_eval — dataset source and column definitions
- Dubois 2024 (arXiv:2404.04475) — defines LC_winrate GLM mechanism
- h-m3 04_validation.md — baseline comparison (Dunn Q1 vs Q4 on Δ: p=1.0)

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Kruskal-Wallis p < 0.05 on LC_winrate | < 0.05 | SHOULD_WORK gate (part 1) |
| Dunn Q1 vs Q4 Bonferroni p < 0.05 | < 0.05 | SHOULD_WORK gate (part 2 — PRIMARY) |
| Quartile group sizes ≥ 5 each | ≥ 5 | Data integrity |
| N_clean ≥ 200 | ≥ 200 | Data integrity |
| All 4 figures generated | 4 files | Completeness |
| 04_validation.md written | Exists | Output completeness |

**Gate Logic:** SHOULD_WORK — gate failure documents scope limitation (relationship holds at population level, not at quartile extremes); pipeline continues regardless.

**Expected Values (from prior pipeline strength — r_partial=0.9851):**
- Kruskal-Wallis H >> 100 on LC_winrate; p << 1e-100
- epsilon-squared > 0.14 (large effect, much larger than H-M3's 0.0876 on Δ)
- Monotonic median trend Q1 < Q2 < Q3 < Q4 (expected True, unlike H-M3 Δ which was non-monotonic)
- Dunn Q1 vs Q4 Bonferroni p << 0.001 (contrast: H-M3 on Δ was p=1.0)

---

## 9. Implementation Constraints

- **Hypothesis Type:** CONDITION (Boundary Test) — FULL tier, max 30 tasks
- **No training loop** — pure statistical analysis
- **Single seed** (42 for bootstrap only; KW and Dunn are deterministic)
- **No hyperparameter tuning** — alpha=0.05, n_bootstrap=1000, random_state=42 fixed
- **Alpha = 0.05** fixed (per Phase 2B plan)
- **Bonferroni correction** — m=6 pairwise comparisons for 4 groups
- **n_bootstrap = 1000** fixed (consistency with h-e1/h-m1/h-m2/h-m3)
- **random_state = 42** fixed
- **Quartile binning:** pd.qcut with q=4 (equal-frequency, same as h-m3)
- **scikit-posthocs required** for Dunn post-hoc (same as h-m3)
- **DV is LC_winrate** (NOT Δ — this is the key distinction from H-M3)
