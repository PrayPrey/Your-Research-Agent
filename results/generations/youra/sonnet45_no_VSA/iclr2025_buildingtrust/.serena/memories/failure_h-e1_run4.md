# Phase 4 Failure Record: h-e1 (Run 4)

**Date:** 2026-07-09T22:35:27Z
**Hypothesis:** h-e1
**Run:** 4
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Actual | Required | Result |
|--------|--------|----------|--------|
| Pearson r | -0.486 | < -0.5 | ✗ FAIL |
| p-value | 0.1542 | < 0.05 | ✗ NOT SIGNIFICANT |
| 95% CI | [-0.854, 0.207] | - | Includes positive values |

## Root Cause Analysis

- **Insufficient effect size**: Pearson r=-0.486 does not reach the required threshold of r < -0.5
- **Lack of statistical significance**: p-value=0.1542 is well above the significance threshold (p < 0.05)
- **Small sample size**: Only 10 benchmarks analyzed, leading to wide confidence intervals
- **High variability**: CV range [0.130, 0.458] and mean ρ range [-0.245, 0.283] show inconsistent patterns
- **Fundamental assumption violation**: CV may not be the right predictor for cross-benchmark stability

## Lessons Learned

1. **Coefficient of Variation alone is insufficient**: CV does not capture enough information about benchmark quality to predict ranking stability
2. **Sample size matters**: 10 benchmarks may be too few to detect the hypothesized moderate-to-strong correlation with statistical power
3. **Alternative quality signals needed**: Score distribution shape (skewness, kurtosis), inter-rater reliability, or model coverage diversity may be better predictors
4. **Threshold mismatch**: The hypothesis specified r < -0.5 which is borderline moderate-strong; the actual r=-0.486 is very close but doesn't meet the strict gate criteria

## Feedback for Next Phase (Phase 0)

### Suggested Modifications
- Explore alternative meta-features beyond CV (e.g., score skewness, percentile spread, model diversity metrics)
- Consider composite quality metrics that combine multiple distributional properties
- Relax correlation threshold to r < -0.4 with larger sample size requirement
- Investigate non-linear relationships (Spearman correlation on CV vs ρ might reveal monotonic but non-linear patterns)

### What NOT To Do
- Do not simply add more benchmarks hoping r will cross -0.5 without theoretical justification
- Do not weaken statistical significance threshold (p < 0.05 is appropriate)
- Do not pursue CV-based approach further without additional theoretical support

### What Showed Promise
- The negative direction (r = -0.486) aligns with hypothesis direction, suggesting the intuition may be partially correct
- High-CV benchmarks (CV > 0.35) do show some tendency toward lower mean ρ
- The methodology for computing cross-benchmark Spearman ρ worked correctly

---

## Gate Decision

**MUST_WORK gate:** ❌ FAILED

**Routing Decision:** Phase 0 (Fundamental Redesign Required)

The MUST_WORK gate failure indicates that the core methodology does not work as hypothesized. CV is not a valid predictor of cross-benchmark stability under the specified criteria. This requires returning to Phase 0 to explore fundamentally different quality signals.

---
*For cross-phase reference*
*Written at: 2026-07-09T22:35:27Z*
