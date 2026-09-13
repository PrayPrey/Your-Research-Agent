# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-08T06:15:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** NOT_SUPPORTED
**Gate Type:** MUST_WORK
**Gate Satisfied:** false

## Hypothesis Statement

The coefficient β₁ on log2(params) ≤ -0.10 in mixed-effects regression of relative robustness, with 95% CI entirely below -0.05, consistent across ratio/Δ/residualized metrics.

## Performance Gap

| Metric | Actual | Required Threshold | Gap |
|--------|--------|-------------------|-----|
| β₁ coefficient | -0.0065 | ≤ -0.10 | 15× weaker than required |
| 95% CI upper bound | +0.016 | < -0.05 | Includes zero |

## Root Cause Analysis

- Effect exists but magnitude far below threshold (β₁ = -0.0065 vs required ≤ -0.10)
- 95% CI spans zero [−0.029, +0.016], not entirely below -0.05
- Direction consistent across 3 metrics but not statistically significant
- Family-specific slopes not significant (LRT p=0.979)
- Scale effect on robustness is real but ~15× smaller than hypothesized

## Lessons Learned

1. Initial effect size estimate was overly optimistic — prior literature review should have calibrated expectations
2. Mixed-effects model correctly detected small negative trend, but hypothesis threshold was unrealistic
3. Consistent direction across metrics suggests effect exists but at much smaller magnitude
4. Future hypotheses should use pilot data to calibrate expected effect sizes

## Feedback for Phase 0

### What NOT To Do
- Do not hypothesize specific coefficient thresholds without pilot calibration
- Do not assume large effect sizes from qualitative observations

### What Showed Promise
- Mixed-effects regression framework worked correctly
- Cross-metric consistency check was valuable
- Model family as random effect appropriate

### Suggested Modifications
- Reformulate as existence test (β₁ < 0) rather than magnitude threshold
- Or: investigate what factors DO predict robustness degradation

---
*For cross-phase reference*
*Written at: 2026-08-08T06:15:00Z*
