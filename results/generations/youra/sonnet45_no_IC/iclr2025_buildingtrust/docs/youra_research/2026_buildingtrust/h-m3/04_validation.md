# Validation Report: h-m3

**Date:** 2026-07-12
**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)
**Gate Type:** SHOULD_WORK

---

## Summary

**Gate Result:** ✗ FAIL

## Fisher z-Test Results

| Metric | Factual | Misinformation | Comparison |
|--------|---------|----------------|------------|
| **Correlation (r)** | -0.3250 | -0.1911 | Δr = 0.1339 |
| **p-value** | 0.359566 | 0.597000 | Fisher p = 0.787984 |
| **95% CI** | [-0.7925, 0.3830] | [-0.7326, 0.4986] | - |
| **Sample size (n)** | 10 | 10 | - |
| **Fisher z** | -0.3372 | -0.1935 | z-stat = -0.2689 |

**Effect Size:** Cohen's q = 0.1437 (medium)

## Gate Evaluation

### SHOULD_WORK Gate Criteria

1. **Primary (Fisher z-test significance):** ✗ FAIL
   - Observed: p = 0.787984
   - Threshold: p < 0.05

2. **Secondary (Effect magnitude):** ✓ PASS
   - Observed: |Δr| = 0.1339
   - Threshold: |Δr| ≥ 0.1

3. **Tertiary (Directional pattern):** ✗ FAIL
   - Criteria: r_factual > 0.4 AND r_misinfo < 0.3

**Final Gate Result:** PARTIAL

## Visualizations

Generated figures:
- `figures/gate_metrics_comparison.png` - MANDATORY gate metrics
- `figures/forest_plot.png` - Correlation comparison with 95% CI
- `figures/effect_size.png` - Cohen's q effect size

## Conclusion

**PARTIAL:** SHOULD_WORK gate criteria not fully satisfied.

Failed criteria:
- Primary: Fisher z-test not significant (p ≥ 0.05)
- Tertiary: Directional pattern not satisfied

---

**Status:** COMPLETED