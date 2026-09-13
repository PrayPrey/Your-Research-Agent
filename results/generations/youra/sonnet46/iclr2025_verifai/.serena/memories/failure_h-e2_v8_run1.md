# Phase 4 Failure Record: h-e2_v8 (Run 1)

**Date:** 2026-03-20T04:30:00Z
**Hypothesis:** h-e2_v8
**Run:** 1
**Final Status:** FAIL
**Failure Type:** OLS_GATE_FAIL

## Gate Summary

- **Gate Type:** MUST_WORK
- **Result:** FAIL
- **Pairs Passing:** 0/5 (threshold: >=4/5)

## Performance Gap

| Criterion | Result |
|-----------|--------|
| All 4 OLS criteria simultaneously | 0/5 pairs pass |
| Positive beta (D_p → pass@1) | Negative in 3/5 pairs |
| ΔR² ≥ 0.02 | Failed in all 5 pairs |
| HC3-robust p-value < 0.05 | Failed in majority of pairs |

## Root Cause Analysis

- D_p (diversity of passing solutions) does not robustly predict pass@1_p when controlling for cross-model difficulty covariates
- Beta coefficient is negative in 3/5 model-benchmark pairs, indicating D_p may be inversely or non-linearly related to pass@1_p in these settings
- ΔR² < 0.02 in all pairs indicates D_p adds negligible explanatory power beyond the baseline covariates
- The OLS relationship hypothesized in H-DpOLS-v8 is not supported by experimental data

## Lessons Learned

1. D_p as an OLS linear predictor of pass@1_p controlling for cross-model difficulty is not a robust relationship
2. Negative betas suggest D_p may capture noise or be confounded with difficulty in ways linear OLS cannot disentangle
3. The existence gate (H-E1_v8: D_p > 0 fraction ≥ 60%) passing does not guarantee OLS significance — existence ≠ predictive power
4. Future hypotheses should consider non-linear relationships or alternative formulations of D_p's role in predicting pass@1

## Cascade Effects

- H-M1_v8: CASCADE_FAILED (blocked by H-E2_v8 FAIL)
- H-M2_v8: CASCADE_FAILED
- H-M3_v8: CASCADE_FAILED

## Routing

- **reflection_outcome:** ROUTED_TO_PHASE_0
- **Route:** Phase 0 (new hypothesis brainstorming)

## Feedback for Phase 0

### What NOT To Do
- Do not use D_p as a direct OLS linear predictor of pass@1_p with difficulty covariates
- Do not assume that D_p > 0 existence implies linear predictive power

### What Showed Promise
- H-E1_v8 passed: D_p > 0 in 5/5 pairs (mean in (0,1), IQR > 0.05) — D_p is a non-trivial, non-constant quantity
- The diversity signal exists but may require a different framing (e.g., threshold-based, non-linear, or interaction terms)

### Suggested Modifications for Phase 0
- Consider non-linear or threshold-based relationships between D_p and pass@k
- Explore whether D_p predicts pass@k for k > 1 (not just pass@1)
- Consider interaction between D_p and difficulty covariate

---
*Failure recorded at: 2026-03-20T04:30:00Z*
*For cross-phase reference*
