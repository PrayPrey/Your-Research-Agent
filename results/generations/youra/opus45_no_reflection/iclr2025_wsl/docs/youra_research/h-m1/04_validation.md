# Validation Report: H-M1

**Date:** 2026-08-19
**Hypothesis:** Weight Matrices Encode Behavioral Information
**Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Executive Summary

**GATE: FAILED**

The proposed weight statistics approach (mean R² = -0.084) did NOT outperform the stratified baseline (mean R² = 0.117). Weight features failed to predict class-wise accuracy better than a simple model using overall accuracy + class difficulty.

---

## Experiment Results

### Dataset
- **Models:** 193 (Small CNN Zoo, CIFAR-10, final epoch)
- **Train/Test Split:** 154 / 39 (80/20)
- **Features:** 25 (5 layers × 5 statistics: mean, std, min, max, norm)

### Gate Metrics

| Metric | Baseline (Stratified) | Proposed (Weight Features) |
|--------|----------------------|---------------------------|
| Mean R² | 0.1168 | -0.0842 |
| Delta R² | — | -0.2009 |

### Per-Class R² Comparison

| Class | Baseline R² | Proposed R² | Winner |
|-------|-------------|-------------|--------|
| 0 | -0.014 | 0.202 | Proposed |
| 1 | 0.187 | 0.220 | Proposed |
| 2 | -0.111 | 0.112 | Proposed |
| 3 | -0.025 | -0.041 | Baseline |
| 4 | -0.090 | **-2.739** | Baseline |
| 5 | 0.276 | 0.252 | Baseline |
| 6 | 0.187 | 0.231 | Proposed |
| 7 | 0.286 | 0.158 | Baseline |
| 8 | 0.135 | 0.262 | Proposed |
| 9 | 0.336 | 0.501 | Proposed |

**Note:** Class 4 shows extreme negative R² (-2.739) for proposed model, indicating severe overfitting or feature-target misalignment on this class.

---

## Gate Verdict

| Gate | Condition | Result |
|------|-----------|--------|
| MUST_WORK | proposed_R² > baseline_R² | **FAIL** |

---

## Analysis

### Why Did It Fail?

1. **Small sample size (n=193)**: With only 39 test samples and 25 features, the Ridge regression likely overfits on train and generalizes poorly. Unterthiner et al. 2020 used ~30,000 models.

2. **Class 4 anomaly**: The extreme negative R² on class 4 suggests the weight features capture noise rather than signal for this class.

3. **Per-layer statistics may be too coarse**: Simple statistics (mean, std, min, max, norm) may not capture the fine-grained weight structure needed to predict behavioral variance.

### Recommendations

1. **Increase sample size**: Use full Small CNN Zoo (~30k models) instead of filtered subset.
2. **Feature engineering**: Try weight histograms, spectral features, or learned representations.
3. **Alternative probe**: Use gradient boosting (GBM) as in Unterthiner et al. 2020 instead of Ridge.

---

## Workflow Impact

Since H-M1 is a **MUST_WORK** gate, failure stops the hypothesis chain:
- H-M2, H-M3, H-M4 (dependent hypotheses) are **BLOCKED**

**Next Action:** Return to Phase 2A to redesign the mechanism hypothesis, or investigate why the weight statistics approach failed with this dataset.

---

## Figures

1. `figures/gate_comparison.png` - Mean R² bar chart
2. `figures/per_class_r2.png` - Per-class R² comparison
3. `figures/pred_vs_actual_class0.png` - Class 0 scatter plot

---

## Raw Results

```json
{
  "baseline_r2_mean": 0.1168,
  "proposed_r2_mean": -0.0842,
  "delta_r2": -0.2009,
  "gate_pass": false,
  "n_models": 193,
  "n_train": 154,
  "n_test": 39
}
```
