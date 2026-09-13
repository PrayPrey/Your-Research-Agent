# Phase 4 Validation Report: H-M1

**Hypothesis:** High HHI indicates community convergence on few datasets
**Type:** MECHANISM
**Date:** 2026-08-10
**Gate:** MUST_WORK

---

## Executive Summary

**GATE STATUS: PASSED**

H-M1 validates that HHI correctly indicates benchmark concentration. High-HHI venue-years show significantly higher top-5 dataset share than low-HHI venue-years (p < 0.001), with strong positive correlation (Spearman ρ = 0.90).

---

## Experiment Results

### Statistical Tests

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mann-Whitney U statistic | 104.0 | - | - |
| Mann-Whitney p-value | 0.000319 | < 0.05 | **PASSED** |
| Spearman ρ | 0.90 | > 0.7 | **PASSED** |
| Spearman p-value | 2.79e-08 | < 0.05 | **PASSED** |

### Group Comparison

| Group | N | Mean Top-5 Share |
|-------|---|------------------|
| High HHI (> median) | 10 | 0.226 |
| Low HHI (≤ median) | 11 | 0.147 |

**Median HHI:** 0.0115

### Mechanism Activation

| Check | Result |
|-------|--------|
| groups_differ (high > low) | ✓ True |
| correlation_positive (ρ > 0) | ✓ True |

---

## Interpretation

1. **HHI validity confirmed:** Higher HHI values correspond to higher concentration of top-5 task categories, validating HHI as a concentration metric for ML benchmarks.

2. **Effect magnitude:** High-HHI group has 54% higher top-5 share than low-HHI group (0.226 vs 0.147).

3. **Correlation strength:** ρ = 0.90 indicates very strong monotonic relationship between HHI and top-5 share.

---

## Figures Generated

1. `figures/group_comparison_bar.png` - Bar chart comparing high vs low HHI groups
2. `figures/hhi_vs_top5_scatter.png` - Scatter plot of HHI vs top-5 share by venue
3. `figures/distribution_histograms.png` - Distribution comparison of top-5 share
4. `figures/venue_year_heatmap.png` - Heatmap of top-5 share by venue and year

---

## Gate Evaluation

### Primary Gate (MUST_WORK)
- **Criterion:** Mann-Whitney p < 0.05
- **Result:** p = 0.000319 < 0.05
- **Status:** **PASSED**

### Secondary Criterion (SHOULD)
- **Criterion:** Spearman ρ > 0.7
- **Result:** ρ = 0.90 > 0.7
- **Status:** **PASSED**

---

## Conclusion

H-M1 hypothesis is **VALIDATED**. HHI correctly indicates benchmark concentration in ML research. The mechanism is confirmed: high HHI values indicate that a few task categories (dataset proxies) dominate the research landscape.

**Next Step:** Proceed to H-M2 (Convergence creates implicit evaluation standards).

---

## Artifacts

- `code/results/results.json` - Raw results
- `code/data_loader.py` - Data loading module
- `code/validate.py` - Main validation script
- `code/visualize.py` - Visualization module
- `figures/*.png` - 4 generated figures
