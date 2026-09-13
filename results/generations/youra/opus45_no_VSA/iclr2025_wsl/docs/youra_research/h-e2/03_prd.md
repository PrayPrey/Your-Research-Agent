# Phase 3 PRD: H-E2 Correlation Analysis

**Hypothesis**: CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05)  
**Type**: EXISTENCE | **Gate**: MUST_WORK  
**Date**: 2026-08-10

---

## 1. Overview

Validate correlation between CV_PR (extracted in H-E1) and ImageNet top-1 accuracy across 100+ pretrained timm models.

## 2. Success Criteria

| Metric | Threshold |
|--------|-----------|
| Pearson r | < -0.3 |
| p-value | < 0.05 |
| Sample size | >= 80 matched models |

## 3. Inputs

- **CV_PR data**: `h-e1/h-e1/results/results.csv` (100 models)
- **Accuracy data**: timm `results-imagenet.csv` from GitHub

## 4. Outputs

| File | Content |
|------|---------|
| `h-e2/code/correlate.py` | Analysis script |
| `h-e2/results/correlation_results.json` | {r, p, n, ci_low, ci_high} |
| `h-e2/figures/scatter_cv_pr_vs_accuracy.png` | Visualization |

## 5. Scope

### In Scope
- Data loading and merging
- Pearson/Spearman correlation
- Bootstrap CI for correlation
- Scatter plot with regression line
- Outlier detection

### Out of Scope
- Model retraining
- Feature extraction (done in H-E1)
- Causal inference

## 6. Dependencies

```
scipy>=1.10
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
requests
```

## 7. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low match rate | Reduced power | Manual name alignment |
| Confounders | Spurious correlation | Partial correlation w/ param_count |
| Non-normal data | Invalid p-value | Bootstrap CI |

## 8. Timeline

~30 minutes total (data prep 10m, analysis 10m, visualization 10m)
