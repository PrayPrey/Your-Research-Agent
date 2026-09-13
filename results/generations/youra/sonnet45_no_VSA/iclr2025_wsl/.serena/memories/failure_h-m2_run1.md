# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-07-11T07:27:00Z
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Ours (NFN) | Baseline (MLP) | Gap |
|--------|------|----------|-----|
| Best Test Error (d=128) | 0.0550 | 0.0001 | +0.0549 (NFN worse by 54900%) |
| Mean Δ_test | -0.1328 | 0.0000 (expected positive) | -0.1328 |

## Root Cause Analysis

- **Simplified NFN Implementation**: Used residual connections instead of true permutation-equivariant NPLayers from the nfn library
- **Loss Matching Failure**: Training losses differed by 23-8643% (target <1%), preventing fair comparison between MLP and NFN
- **Task Mismatch**: Self-supervised mean-target reconstruction may not leverage the structural advantages of permutation equivariance
- **Hyperparameter Tuning Gap**: MLP and NFN used identical hyperparameters, but NFN likely requires different optimization strategy

## Lessons Learned

1. **Always use true library implementations**: Simplified approximations of equivariant architectures (e.g., residual connections instead of NPLayers) fail to capture the intended inductive biases
2. **Task design matters**: Self-supervised reconstruction tasks may favor MLP expressiveness over NFN equivariance - use tasks that explicitly benefit from permutation symmetry (e.g., predicting model performance)
3. **Independent hyperparameter tuning required**: Architectures with different inductive biases need separate hyperparameter optimization, not shared settings
4. **Loss matching is critical**: Without matched training losses (≤1% tolerance), test error comparisons are invalid - implement Pareto hyperparameter sweep as designed

## Feedback for Next Phase

### Suggested Modifications
- Replace simplified NFN encoder with actual `nfn.layers.NPLayer` from nfn library
- Change task from self-supervised reconstruction to supervised performance prediction (leverages equivariance)
- Implement separate hyperparameter tuning for MLP and NFN (learning rate, hidden dims, etc.)
- Add Pareto hyperparameter sweep to enforce loss matching constraint

### What NOT To Do
- Do not use residual connections as a substitute for true permutation-equivariant layers
- Do not share hyperparameters between MLP and NFN without independent validation
- Do not use self-supervised reconstruction objectives when testing equivariance benefits

### What Showed Promise
- ModelZoo dataset loading and preprocessing infrastructure works correctly
- Training infrastructure successfully trained 10 models across 5 widths
- Monotonicity check implementation passed (though deltas had wrong sign)
- Visualization pipeline generated correct gate metrics and scaling curves

---
*For cross-phase reference*
*Written at: 2026-07-11T07:27:00Z*
