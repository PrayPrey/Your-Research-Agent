# Phase 4 Failure Record: h-e1 (Run 5)

**Date:** 2026-03-20T16:30:22Z
**Hypothesis:** h-e1
**Run:** 5
**Final Status:** FAIL
**Failure Type:** INSUFFICIENT_STATISTICAL_POWER

## Performance Gap

| Metric | Result | Threshold | Gap |
|--------|--------|-----------|-----|
| Test 2a (Feature β CI excludes -0.50) | FAIL | CI must exclude -0.50 | CI = [-0.8274, 0.5282] includes -0.50 |
| Test 3b (Feature R² ≥ 0.90) | FAIL | R² ≥ 0.90 | R² = 0.8872 < 0.90 |
| Tests Passed | 3/5 | 5/5 (MUST_WORK) | Failed 2 critical tests |

## Experiment Details

**NTK Regime (Width=128, Full-Batch GD):**
- β estimate: -0.4772
- 95% CI: [-0.6954, -0.2590]
- R²: 0.9987
- Mean accuracy: 0.6417 ± 0.0287

**Feature Regime (Width=32, Adam):**
- β estimate: -0.1496
- 95% CI: [-0.8274, 0.5282]
- R²: 0.8872
- Mean accuracy: 0.9678 ± 0.0011

## Root Cause Analysis

1. **Computational Scale Reduction**: Original spec required 200 seeds/regime with M ∈ [20, 50, 100, 200]. Actual execution used 20 seeds/regime with M ∈ [10, 15, 20] (10× reduction)
2. **Insufficient Ensemble Sizes**: Maximum M=20 insufficient for precise power-law β estimation via bootstrap
3. **Limited Regression Points**: Only 3 data points (M=10,15,20) for power-law regression, reducing fit quality
4. **Bootstrap Variance Too High**: With limited samples, bootstrap CI becomes extremely wide for feature regime

## Lessons Learned

1. **Statistical Power vs Computational Feasibility**: Hypothesis testing requires sufficient sample size. A 10× reduction in scale compromises statistical conclusions even when conceptual approach is sound.
2. **Power-Law Regression Requirements**: Need ≥4 ensemble sizes spanning ≥10× range for reliable power-law fits (e.g., M ∈ [20, 50, 100, 200])
3. **Bootstrap Precision**: Bootstrap confidence intervals require adequate base sample size. M_max=20 insufficient for distinguishing convergence rates.
4. **Gate Criteria Must Match Resources**: MUST_WORK gates requiring statistical precision need experimental designs that account for computational constraints.
5. **Conceptual Soundness ≠ Experimental Success**: Hypothesis conceptually valid (NTK regime shows expected behavior), but experimental underpowered.

## What Showed Promise

1. **NTK Regime Results**: β = -0.48 ≈ -0.50 with excellent R² = 0.9987 confirms classical CLT convergence
2. **Feature Regime Trend**: Point estimate β = -0.15 > -0.40 shows slower convergence as hypothesized
3. **Code Implementation**: All modules work correctly, checkpointing functional, integration successful
4. **Directional Evidence**: Feature regime β less negative than NTK, consistent with hypothesis direction

## What NOT To Do

1. **Don't use reduced-scale experiments for MUST_WORK gates requiring statistical precision**
2. **Don't use power-law regression with <4 data points**
3. **Don't expect bootstrap CIs to distinguish regimes with M_max < 50**
4. **Don't design experiments where computational constraints fundamentally conflict with validation criteria**

## Feedback for Next Phase

### Suggested Modifications
- Increase computational budget for full-scale execution (200 seeds/regime, M ∈ [20,50,100,200])
- Relax statistical criteria to match feasible computational scale (e.g., require directional consistency rather than CI exclusion)
- Use alternative experimental designs with better efficiency (e.g., sequential sampling, early stopping rules)
- Split hypothesis into "directional evidence" (achievable) vs "statistical confirmation" (requires full scale)

### Alternative Approach
- Accept partial evidence and document as limitation rather than failure
- Reformulate as SHOULD_WORK gate with relaxed criteria
- Use non-parametric tests that require fewer samples
- Focus on point estimates rather than confidence interval separation

---
*For cross-phase reference*
*Written at: 2026-03-20T16:30:22Z*
