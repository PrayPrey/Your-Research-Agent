# Phase 4 Failure Record: h-e2 (Run 1)

**Date:** 2026-08-10T09:50:00Z
**Hypothesis:** h-e2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_FALSIFIED

## Gate Details

| Gate Type | Required | Observed | Result |
|-----------|----------|----------|--------|
| MUST_WORK | r < -0.3 | r = +0.6065 | FAIL |

## Performance Data

| Metric | Value |
|--------|-------|
| Pearson r | +0.6065 |
| p-value | 9.24e-11 |
| 95% CI | [0.506, 0.703] |
| Sample size | 94 models |

## Root Cause Analysis

- Hypothesis assumed CV_PR correlates negatively with model quality
- Empirical evidence shows strong POSITIVE correlation (r=+0.61)
- Higher CV_PR associated with higher accuracy, opposite to prediction
- Possible confound: larger models have more parameters, higher accuracy, AND higher CV_PR

## Lessons Learned

1. The fundamental assumption (CV_PR reflects instability → worse performance) is incorrect
2. CV_PR may actually reflect richer feature representations, not instability
3. Cross-model analysis confounded by architecture/parameter count differences
4. Should consider partial correlation controlling for model size

## Feedback for Phase 0

### Suggested Modifications
- Reformulate hypothesis with positive correlation (CV_PR positively predicts accuracy)
- Use partial correlation controlling for param_count
- Stratify by architecture family (ResNet vs ViT vs ConvNeXt)
- Consider within-family comparisons rather than cross-family

### What NOT To Do
- Do not assume negative correlation between spectral variability and performance
- Do not pool heterogeneous architectures without controlling for confounds

### What Showed Promise
- CV_PR extraction is reliable (h-e1 PASS)
- Strong correlation exists (just opposite direction)
- Statistical significance is high (p < 1e-10)

---
*For cross-phase reference*
*Written at: 2026-08-10T09:50:00Z*
