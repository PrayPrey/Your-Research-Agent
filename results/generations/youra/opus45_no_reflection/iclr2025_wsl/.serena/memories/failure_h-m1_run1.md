# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-19T02:35:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** WORSE_THAN_BASELINE

## Hypothesis

**Title:** Weight Matrices Encode Behavioral Information
**Statement:** Under Small CNN Zoo scope, if we extract features from weight matrices, then these features will correlate with class-wise accuracy profiles

## Performance Gap

| Metric | Proposed | Baseline | Gap |
|--------|----------|----------|-----|
| Mean R² | -0.0842 | 0.1168 | -0.2009 (-172%) |

## Root Cause Analysis

- **Small sample size:** Only 193 models used (vs ~30,000 in Unterthiner et al. 2020). With 39 test samples and 25 features, Ridge regression overfits.
- **Class 4 anomaly:** Extreme negative R² (-2.739) indicates severe overfitting or feature-target misalignment for this specific class.
- **Coarse features:** Simple per-layer statistics (mean, std, min, max, norm) may not capture fine-grained weight structure needed to predict behavioral variance.

## Lessons Learned

1. **Sample size matters:** Linear probes on weight statistics require large model populations to generalize.
2. **Per-class variance:** Some classes may have fundamentally different weight-behavior relationships.
3. **Feature engineering:** Consider weight histograms, spectral features, or learned representations instead of simple statistics.
4. **Alternative models:** Try gradient boosting (GBM) as in original Unterthiner et al. 2020 instead of Ridge regression.

## Feedback for Next Attempt

### Suggested Modifications
- Use full Small CNN Zoo (~30k models) instead of filtered subset
- Try weight histograms or spectral features
- Use GBM instead of Ridge regression
- Consider per-class feature selection

### What NOT To Do
- Don't use simple per-layer statistics with small sample sizes
- Don't assume linear relationships between weight statistics and behavior

### What Showed Promise
- Some classes (0, 1, 2, 6, 8, 9) showed positive R² for proposed method
- Class 9 had strong R² (0.501) suggesting weight features can work for some classes

---
*For cross-phase reference*
*Written at: 2026-08-19T02:35:00+00:00*
