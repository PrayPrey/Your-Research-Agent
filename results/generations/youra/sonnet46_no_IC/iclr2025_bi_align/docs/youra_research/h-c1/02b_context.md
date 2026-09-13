# Phase 2B Context: H-C1

**Hypothesis ID:** h-c1
**Type:** CONDITION
**Date:** 2026-08-04

---

## Hypothesis Statement

The capability-alignment relationship is monotonic at population extremes: Dunn post-hoc Q1 vs Q4 Bonferroni-corrected p < 0.05 on LC_winrate across win_rate quartiles. Confirms relationship holds beyond average-level effect.

## Hypothesis Type

**CONDITION** (boundary/scope test)  
**Gate:** SHOULD_WORK — failure narrows scope but does not invalidate H-E1, H-M1, H-M2, or H-M3.

## Prerequisites

- h-e1: COMPLETED (PASS) — r_partial=0.9851, p=1.69e-170
- h-m1: COMPLETED (PASS) — |β_win|=21.34 >> |β_len|=4.37
- h-m2: COMPLETED (PASS) — rho_resid=0.9739, p=2.37e-144
- h-m3: COMPLETED (PASS) — KW H=22.19, p=5.97e-05, ε²=0.0876

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** AlpacaEval 2.0 Leaderboard
- **Type:** standard (pre-computed leaderboard CSV)
- **Source:** https://github.com/tatsu-lab/alpaca_eval
- **Path:** docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- **N:** 222 models (N=223 after cleaning in prior runs)
- **Columns used:** win_rate, length_controlled_winrate, avg_length
- **Hypothesis Fit:** Full leaderboard provides complete quartile coverage (Q1-Q4 each ~56 models). Dataset already validated and cached from H-E1 through H-M3 pipeline.

### Model
- **Name:** N/A — statistical analysis study
- **Type:** observational analysis on pre-computed scores
- **Source:** AlpacaEval 2.0 CSV provides pre-computed scores for 222 LLMs
- **Hypothesis Fit:** No model training required. Analysis operates on existing evaluation scores.

## Verification Protocol (from Phase 2B)

1. Create quartile variable: `pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])`
2. Run Kruskal-Wallis on LC_winrate across all 4 quartiles
3. Run `scikit_posthocs.posthoc_dunn` for pairwise comparisons
4. Apply Bonferroni correction; focus on Q1 vs Q4 comparison
5. Visualize: boxplot of LC_winrate per quartile with median lines

## Success Criteria

- **Primary:** Kruskal-Wallis p < 0.05 AND Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05
- **Secondary:** Monotonic median trend Q1 < Q2 < Q3 < Q4 (not required for gate)

## Context from Previous Hypotheses

### H-M3 Results (Direct Predecessor)

H-M3 tested Kruskal-Wallis on **Δ = LC_winrate − win_rate** across quartiles:
- KW H=22.19, p=5.97e-05 (PASS)
- Dunn Q1 vs Q4 on Δ: p=1.0 (NOT significant after Bonferroni)
- Q4 median Δ = 0.91 (not highest — non-monotonic)

**Critical distinction for H-C1:** This hypothesis tests LC_winrate (not Δ) across quartiles.
LC_winrate is NOT mathematically dependent on win_rate in the same way Δ is, so the
Dunn test on LC_winrate should have more statistical power than on Δ.

Expected: LC_winrate should show strong monotonic trend Q1 < Q2 < Q3 < Q4 given
r_partial(win_rate, LC_winrate | avg_length) = 0.9851 (from H-E1).

### Key Prior Results

| Hypothesis | Metric | Value |
|------------|--------|-------|
| H-E1 | r_partial(win_rate, LC_winrate \| avg_length) | 0.9851, p=1.69e-170 |
| H-M1 | \|β_win_std\| vs \|β_len_std\| | 21.34 >> 4.37 |
| H-M2 | rho(win_resid, lc_resid) | 0.9739, p=2.37e-144 |
| H-M3 | KW on Δ across quartiles | H=22.19, p=5.97e-05 |

### Code Infrastructure Available

From h-e1 through h-m3, the following code is reusable:
- CSV loading and cleaning pipeline
- StandardScaler preprocessing
- pd.qcut quartile creation (Q1-Q4, N≈56 per group)
- scipy.stats.kruskal wrapper
- scikit_posthocs.posthoc_dunn with Bonferroni
- Figure generation (boxplot, heatmap)

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Dunn test may not reject after Bonferroni (6 comparisons) | Focus on Q1 vs Q4 specifically; check uncorrected p as secondary |
| LC_winrate has high collinearity with win_rate (r≈0.98) | This supports rather than harms the monotonicity test |
| N per quartile ~56 — sufficient power? | Power analysis: for rho=0.98 at N=56, power > 0.999 |

## Gate Logic

**SHOULD_WORK** — if H-C1 fails:
- Document as scope limitation: "capability-alignment relationship may not hold at population extremes"
- Does NOT invalidate H-E1, H-M1, H-M2, or H-M3
- Proceed to Phase 4.5/5 regardless
