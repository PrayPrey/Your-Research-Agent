# Validation Report: H-M4

**Hypothesis:** Reduced diversity hides benchmark-specific overfitting
**Type:** MECHANISM
**Date:** 2026-08-10
**Status:** FAILED (Real Data)

---

## Executive Summary

H-M4 tested whether low benchmark diversity (entropy) correlates with high benchmark concentration. Using **real PWC data** (8,389 papers), the hypothesis was **not supported** at the 0.05 significance level:

- Spearman ρ = -0.332 (weak negative)
- p-value = 0.166 (not significant)
- Only ICML showed significant effect

**Note:** Previous result (ρ=-0.958, p<0.001) was invalid due to synthetic data that embedded the hypothesis.

---

## Gate Results

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| Spearman ρ | < 0 | -0.332 | PASS |
| p-value | < 0.05 | 0.166 | **FAIL** |
| Venue coverage | ≥ 2/3 | 1/3 venues | **FAIL** |

**Gate Verdict:** FAILED

---

## Mock Data Fix Applied

**Issue:** Original code fell back to synthetic data with tautological relationship:
```python
# REMOVED: variance_factor = 0.8 * (1.0 - entropy) + 0.02
```
This hard-coded the expected negative correlation directly into the data.

**Fix:** 
- Removed all synthetic data generation
- Use only real PWC cache: `h-e1/code/pwc_papers_cache.parquet`
- 8,389 papers with 2+ task labels (benchmark diversity proxy)

---

## Statistical Analysis

### Overall Correlation

| Metric | Value |
|--------|-------|
| Spearman ρ | -0.332 |
| p-value | 0.166 |
| N venue-years | 19 |
| Direction | Correct (negative) |
| Effect size | Weak |

### Per-Venue Results

| Venue | Spearman ρ | p-value | N years | Significant? |
|-------|------------|---------|---------|--------------|
| NeurIPS | -0.500 | 0.253 | 7 | No |
| **ICML** | **-0.900** | **0.037** | 5 | **Yes** |
| ICLR | -0.179 | 0.702 | 7 | No |

---

## Data Summary (Real Data)

- **Total papers in cache:** 12,600
- **Multi-benchmark papers (2+ task labels):** 8,389
- **Venue-years included:** 19 (with sufficient data)
- **Papers per venue-year:** min=10, max=1,282, median=239
- **Data source:** Real PWC HuggingFace dataset, cached in parquet

---

## Methodology Adaptation

Original brief specified cross-benchmark **score variance** (requires actual performance metrics). PWC cached data has task labels but not metric values.

**Adaptation:**
- **Benchmark Breadth:** Count of distinct task labels per paper
- **Concentration:** 1 / breadth (higher = narrower evaluation coverage)
- **Test:** Entropy (venue-level) vs Concentration (paper-level aggregated)

This is a valid proxy: papers in concentrated venues should show narrower evaluation coverage.

---

## Interpretation

The weak negative correlation (ρ=-0.332) suggests a **trend** in the expected direction:

1. **Some support:** Direction is correct; ICML shows significant strong effect (ρ=-0.90)
2. **Insufficient evidence:** Overall p=0.166 fails significance threshold
3. **Venue heterogeneity:** Effect may be venue-specific (ICML vs others)

Possible explanations for weak result:
- Task label count may not capture actual evaluation diversity
- 19 venue-years may be underpowered
- True effect may be smaller than hypothesized

---

## Figures Generated

1. `figures/gate_metrics.png` - Entropy vs concentration scatter with regression
2. `figures/entropy_variance_scatter.png` - Venue-colored scatter
3. `figures/per_venue_correlation.png` - Per-venue ρ bar chart
4. `figures/variance_by_entropy_quartile.png` - Box plots by entropy quartile

---

## Files Modified in Mock Fix

| File | Change |
|------|--------|
| `code/data_loader.py` | Removed synthetic fallback, use real PWC cache only |
| `code/variance.py` | Changed from score variance to benchmark breadth |
| `code/analyze.py` | Updated metric names (mean_concentration) |
| `code/visualize.py` | Updated labels for concentration metric |

---

## Conclusion

**H-M4: NOT SUPPORTED** at α=0.05 with real data.

The original "passing" result was an artifact of synthetic data that encoded the hypothesis. The real data shows a weak trend in the expected direction but fails to reach statistical significance.

---

## Artifacts

| File | Description |
|------|-------------|
| `results/results.json` | Full statistical results (real data) |
| `results/breadth_by_venue_year.csv` | Aggregated breadth data |
| `code/` | Fixed implementation (no synthetic) |
| `figures/` | Updated visualizations |
