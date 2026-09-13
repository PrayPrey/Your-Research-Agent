# Phase 4 Failure Record: h-e1 (Run 6)

**Date:** 2026-03-20T16:30:22Z
**Hypothesis:** h-e1
**Run:** 6
**Final Status:** FAIL
**Failure Type:** INSUFFICIENT_STATISTICAL_POWER

## Performance Gap

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test 1 (NTK β CI contains -0.50) | PASS | PASS | ✓ |
| Test 2a (Feature β CI excludes -0.50) | FAIL | PASS | ✗ |
| Test 2b (Feature β > -0.40) | PASS | PASS | ✓ |
| Test 3a (NTK R² ≥ 0.90) | PASS | PASS | ✓ |
| Test 3b (Feature R² ≥ 0.90) | FAIL | PASS | ✗ |

**Gate Result:** FAIL (2 out of 5 criteria failed)

## Root Cause Analysis

- **Primary Cause:** 10× scale reduction (20 seeds/regime vs 200 seeds/regime) severely compromised statistical power
- **Technical Issue:** Wide confidence intervals for Feature regime β [-0.8274, 0.5282] include -0.50 (should exclude)
- **Secondary Issue:** Feature regime R² = 0.8872 < 0.90 threshold suggests power-law model may not perfectly describe convergence
- **Resource Constraint:** Computational feasibility vs experimental requirements mismatch

## Lessons Learned

1. **Statistical Power Planning:** Experimental design must account for computational constraints upfront - 10× scale reduction invalidates hypothesis test
2. **Confidence Interval Width:** Bootstrap with M=[10,15,20] insufficient for reliable power-law β estimation; need M ≥ 50 for regime differentiation
3. **Model Selection:** Feature regime convergence may not follow simple power-law; consider alternative convergence models or non-parametric tests
4. **Suggestive Evidence vs Proof:** Point estimates showed correct direction (NTK β=-0.48 ≈ -0.50, Feature β=-0.15 > -0.40) but precision insufficient for statistical confirmation
5. **MUST_WORK Gate Design:** Gate criteria requiring statistical significance need adequate sample sizes - computational feasibility must be validated in Phase 2C

## Experimental Details

- **NTK Regime:** β=-0.48, 95% CI=[-0.70, -0.26], R²=0.9987 ✓
- **Feature Regime:** β=-0.15, 95% CI=[-0.83, 0.53], R²=0.8872 ✗
- **Total Runs:** 40 experiments (20 per regime)
- **Ensemble Sizes:** M ∈ [10, 15, 20] (vs designed M ∈ [20, 50, 100, 200])

## Feedback for Next Phase

### Suggested Modifications
- Increase computational budget to support M_max ≥ 50 for regime differentiation
- Add preliminary power analysis in Phase 2C to validate sample size requirements
- Consider relaxing R² threshold to 0.85 or using non-parametric convergence tests
- Alternative approach: single-regime CLT validation (simpler, lower computational cost)

### What NOT To Do
- Do not reduce sample sizes below power analysis requirements
- Do not assume power-law convergence without validation
- Do not design MUST_WORK gates requiring statistical tests without computational feasibility check

### What Showed Promise
- NTK regime validation worked perfectly (β=-0.48 ≈ -0.50, R²=0.9987)
- Code implementation successful and robust
- Direction of effect correct (Feature β > NTK β as expected)
- Experimental framework solid, just underpowered

---
*For cross-phase reference*
*Written at: 2026-03-20T16:30:22Z*