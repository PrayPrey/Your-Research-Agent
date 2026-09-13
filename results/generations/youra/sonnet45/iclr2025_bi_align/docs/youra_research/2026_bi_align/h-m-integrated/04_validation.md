# Phase 4 Validation Report: H-M-Integrated

**Date:** 2026-03-17T15:18:51.110745
**Hypothesis ID:** h-m-integrated
**Hypothesis Type:** MECHANISM

---

## Executive Summary

**Overall Gate Result:** FAIL

| Gate | Criterion | Result | Status |
|------|-----------|--------|--------|
| Primary | Cohen's d ≥ 0.15, p < 0.05 | d=-0.0181, p=0.000000 | FAIL ✗ |
| Secondary | α > 0.7 | α=0.4200 | FAIL ✗ |
| Tertiary | ≥2/2 splits pass | 0/2 passed | FAIL ✗ |

---

## Dataset

**Dataset:** Anthropic/hh-rlhf
**Total Pairs:** 169,352

**Splits:**
- train: 160,800 pairs
- test: 8,552 pairs

---

## Primary Gate: Effect Size Analysis

**Criterion:** Cohen's d ≥ 0.15, p < 0.05, chosen < rejected

**Results:**
- t-statistic: -7.4496
- p-value: 0.000000
- Cohen's d: -0.0181
- Direction: chosen < rejected ✓

**Interpretation:**
✗ Primary gate FAILED. Effect size (|d| = 0.0181) below threshold (0.15). 

**Descriptive Statistics:**
- Chosen mean modal freq: 2.894 ± 2.221
- Rejected mean modal freq: 2.928 ± 2.257
- Mean difference: -0.034 ± 1.868

---

## Secondary Gate: Internal Consistency

**Criterion:** Cronbach's α > 0.7

**Results:**
- Cronbach's α: 0.4200
- Mean inter-item correlation: 0.2861

**Interpretation:**
✗ Secondary gate FAILED. Internal consistency (α = 0.4200) below threshold (0.7), suggesting markers may not measure a unified construct.

---

## Tertiary Gate: Cross-Split Replication

**Criterion:** At least 2 of 2 splits pass primary criteria

**Per-Split Results:**

| Split | N Pairs | Cohen's d | p-value | Status |
|-------|---------|-----------|---------|--------|
| train | 160,800 | -0.0187 | 0.000000 | FAIL ✗ |
| test | 8,552 | -0.0067 | 0.536428 | FAIL ✗ |

**Interpretation:**
✗ Tertiary gate FAILED. Only 0 of 2 splits passed (< 2 required), indicating lack of replication.

---

## Visualizations

All figures saved to `figures/`:

1. **gate_metrics.png** - Gate criteria comparison (MANDATORY)
2. **forest_plot.png** - Effect sizes by split with 95% CI
3. **density_plots.png** - Distribution comparison (chosen vs rejected)
4. **paired_differences.png** - Histogram of paired differences
5. **marker_correlations.png** - Correlation heatmap

---

## Conclusion

✗ **Gate FAILURE.** The hypothesis is not supported. Failed gates: primary (effect size), secondary (consistency), tertiary (replication).

**Recommended Actions:**
- PIVOT to alternative linguistic markers or measurement approaches
- EXPLORE direct user studies for agency perception
- ABANDON computational proxy approach if no viable alternatives

---

**Runtime:** 21762.5 seconds
**Generated:** 2026-03-17T15:18:51.110745
