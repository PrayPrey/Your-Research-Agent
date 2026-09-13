# Phase 4 Limitation: h-m3

**Date:** 2026-07-12
**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)
**Gate Type:** SHOULD_WORK
**Gate Result:** PARTIAL
**Phase:** Phase 4 (PoC Implementation & Validation)

## Limitation Summary

H-m3 tested whether reliability-robustness correlation magnitudes differ significantly between factual and misinformation prompt strata using Fisher z-test. The experiment completed successfully but achieved only PARTIAL gate satisfaction due to insufficient sample size.

## Root Cause

**Primary Issue:** Sample size limitation from prerequisite h-m1
- H-m1 provided only n=10 samples per stratum (factual and misinformation)
- This small sample size led to:
  - Weak correlations with high uncertainty (wide confidence intervals)
  - Non-significant Fisher z-test (p=0.788, threshold: p<0.05)
  - Both correlations negative, contradicting theoretical predictions

## Gate Evaluation

- ✗ Primary (p < 0.05): FAIL (p=0.788)
- ✓ Secondary (|Δr| ≥ 0.1): PASS (|Δr|=0.134)
- ✗ Tertiary (directional): FAIL (both correlations negative)

## Failed Criteria

1. **Statistical significance**: Fisher z-test p-value (0.788) far exceeded threshold (0.05)
2. **Directional hypothesis**: Both strata showed negative correlations instead of expected positive pattern
   - Expected: r_factual > 0.4, r_misinfo < 0.3
   - Observed: r_factual = -0.325, r_misinfo = -0.191

## Why Self-Modification Was Not Possible

- The limitation originates from prerequisite h-m1 data quality
- H-m3 cannot increase sample size without re-running h-m1
- No parameter adjustment can fix insufficient input data
- Scope is already minimal (2 strata, 1 statistical test)

## Lessons Learned

1. **Sample Size Validation**: Always verify prerequisite hypothesis sample sizes before starting dependent analyses
   - Correlation comparison requires larger samples (typically n≥30 per group)
   - Check statistical power of base hypothesis outputs

2. **INCREMENTAL Hypothesis Dependencies**: Quality of incremental hypothesis depends on base hypothesis data quality
   - Validate base hypothesis outputs meet statistical requirements
   - Document minimum sample size requirements in PRD

3. **SHOULD_WORK Gate Behavior**: Correctly allows proceeding with documented limitations
   - Unlike MUST_WORK gates, SHOULD_WORK gates don't block pipeline
   - Recorded limitations can be addressed in discussion section

## What Worked

- Fisher z-test implementation was correct
- Code executed without errors
- Effect size (Cohen's q=0.144) suggests medium magnitude difference
- Proper visualizations generated
- Methodology was sound

## Recommendation for Future Work

If revisiting this hypothesis:
1. Re-run h-m1 with full 817-sample TruthfulQA dataset
2. Ensure n≥30 per stratum for reliable correlation estimation
3. Then re-execute h-m3 with larger sample statistical power

## Impact on Pipeline

- Decision: LIMITATION_RECORDED
- Action: Continue to Phase 5 (Baseline Comparison)
- No routing to Phase 0/2A (SHOULD_WORK gates don't route)
- Limitation will be noted in final paper discussion

## Related Memories

- See `mem:phase4/h-m1` for prerequisite hypothesis context
- See `mem:phase4/h-m2` for similar INCREMENTAL hypothesis pattern
