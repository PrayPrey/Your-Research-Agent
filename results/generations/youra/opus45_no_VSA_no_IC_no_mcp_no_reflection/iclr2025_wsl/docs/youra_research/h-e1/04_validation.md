# H-E1 Validation Report

## Hypothesis
Heavy-tailed exponents (α) can be computed with bounded variance (σ < 0.5) for ViT attention weight matrices using the Hill estimator.

## Gate Condition
- **Type**: MUST_WORK
- **Metric**: σ(α) < 0.5
- **Result**: **FAIL**

## Experiment Summary

| Metric | Value |
|--------|-------|
| Models Processed | 53 |
| Models Target | 100 |
| Mean α | 4.327 |
| Median α | 3.521 |
| σ(α) | **2.868** |
| α Range | [2.20, 18.92] |
| Runtime | 1744s |

## Gate Verdict

```
σ(α) = 2.868 > 0.5 threshold
GATE: FAIL
```

The hypothesis is **rejected**. The variance of α across ViT models (σ=2.868) exceeds the gate threshold (0.5) by 5.7x.

## Analysis

### Root Cause
High variance stems from:
1. **Outlier models**: Some fine-tuned models (jaranohaal/vit-base-violence-detection: α=12.6, mlx-vision/vit_base_patch16_224-mlxim: α=14.8) have dramatically different α values
2. **Model heterogeneity**: Mixed architectures (ViT-base, ViT-large, ViT-tiny) with different layer counts
3. **Training state diversity**: Mix of pretrained vs heavily fine-tuned models

### Within-Family Variance
When controlling for model family (e.g., google/vit-*), σ drops to 0.24 for n=6 models, suggesting the methodology works but cross-architecture comparisons introduce noise.

## Artifacts

### Figures
- `figures/gate_check.png` - Gate pass/fail visualization
- `figures/alpha_histogram.png` - α distribution across models
- `figures/family_boxplot.png` - α by model family
- `figures/alpha_vs_size.png` - α vs parameter count

### Data
- `code/results.json` - Full per-model measurements

## Recommendations

1. **Stratify by architecture**: Separate ViT-base/large/tiny analyses
2. **Filter outliers**: Exclude models with α > 10 (likely training artifacts)
3. **Increase homogeneity**: Focus on single model family (e.g., google/vit-*) for tighter bounds

## Conclusion

The Hill estimator successfully computes α values for ViT attention layers, but the cross-model variance is too high for the MUST_WORK gate. The methodology is sound for within-family comparisons but fails as a universal ViT metric.
