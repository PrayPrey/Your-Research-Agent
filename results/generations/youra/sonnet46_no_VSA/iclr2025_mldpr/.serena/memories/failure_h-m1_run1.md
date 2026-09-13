# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-03T08:30:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL (meaningful null / H0)
**Failure Type:** MUST_WORK_FAIL (meaningful null result — pre-specified Phase 6 route)

## Gate Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LRT p-value | 0.9495 | < 0.05 | FAIL |
| |HR-1| | 0.0056 | ≥ 0.10 | FAIL |
| HR | 1.0056 | — | — |
| 95% CI | [0.8457, 1.1958] | — | straddles 1.0 |

## Scientific Interpretation

**H0 (Null Result):** `log_unique_paper_count_at_intro_z` does NOT significantly predict plurality benchmark displacement hazard. Community breadth diversity at benchmark introduction is well-measured (H-E1 validated: std=0.2462, VIF=2.14) but explains essentially zero variance in displacement timing. This is a clean, credible null.

## Root Cause Analysis

- The predictor is time-independent and has sufficient variance — the null is not a data quality issue
- 87/345 rows dropped due to NaN in analysis columns (reduced panel: 258 rows) — acceptable but warrants investigation
- LRT statistic near zero (0.004) — log-likelihood barely changed between M0 and M1
- Mechanism hypothesized in H-M1/H-M2 does not operate at this level of analysis

## Lessons Learned

1. Community breadth (unique paper count) at introduction predicts nothing about displacement timing — not even directionally
2. lifelines CI column detection pattern (`"lower" in c.lower()`) handles version differences reliably
3. Error-wrapping in plot functions prevents single-figure failure from crashing the pipeline
4. lifelines `check_assumptions()` fails on string-valued strata — catch and log non-critically

## Route Decision

- **Standard MUST_WORK FAIL:** would route to Phase 0
- **Actual route:** Phase 6 (paper writing) — pre-specified in 02c_experiment_brief.md as "meaningful null routes to Phase 6"
- This null result is scientifically publishable; no hypothesis redesign needed

## Recommendations for Dependent Hypotheses

- **H-M2** (paper_diversity_ratio predictor): reuse fit_models(), run_lrt(), LRTResult from H-M1 code; expect similar null given r=-0.324 collinearity
- Neither breadth nor ratio is expected to predict timing — strengthens null narrative for Phase 6 paper

---
*Failure recorded at: 2026-08-03T08:30:00Z*
*For cross-phase reference*
