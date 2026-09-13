# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-05-05T09:30:00.000000+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** GATE_FAIL_BOUNDARY_CONDITION
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Performance Gap

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| fraction_near_equiv | 0.05 | > 0.05 | FAIL (equals but not strictly greater) |
| epsilon | 12.690232 | — | — |
| n_models | 200 | — | — |
| n_near_equiv | 995 | — | — |
| n_pairs | 19900 | — | — |
| dist_mean | 18.811 | — | — |
| dist_std | 3.681 | — | — |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Gate Criterion:** fraction_near_equiv > 0.05
- **Result:** FAIL — fraction_near_equiv=0.05 equals threshold 0.05 but is not strictly greater
- **Pass Rate:** 0.0

## Root Cause Analysis

- The near-equivalent fraction exactly hit the 0.05 boundary but failed the strict inequality check
- With 200 CIFAR-10 zoo models and n_probe=1000, only 995/19900 pairs (5.0%) fell within epsilon=12.69
- The hypothesis that model zoo checkpoints share near-equivalent logit distributions was not confirmed
- Boundary condition failure suggests the effect size is marginal at best — genuine near-equivalence may not exist at this scale

## Lessons Learned

1. The MUST_WORK gate uses strict inequality (> 0.05), not >=. Threshold calibration must account for this.
2. With n_models=200, the pairwise distance distribution produces dist_mean=18.81 with std=3.68 — models are more diverse than hypothesized.
3. The adaptive epsilon calibration (12.69) may be too aggressive; a fixed or less aggressive threshold might yield different results.
4. CIFAR-10 zoo models trained independently show less logit similarity than expected — the near-equivalence phenomenon may require controlled training conditions.
5. Consider testing on a smaller, more homogeneous subset of zoo models or adjusting the hypothesis to target gradient/weight similarity rather than logit similarity.

## Feedback for Next Phase (Phase 0 Brainstorm)

### Suggested Modifications
- Re-examine the near-equivalence definition: logit-space L2 may not capture the right similarity
- Try weight-space or activation-space similarity metrics instead
- Consider using a subset of zoo models trained under similar hyperparameter regimes
- Relax the gate criterion or use a different calibration strategy for threshold

### What NOT To Do
- Do not use the same fraction_near_equiv > 0.05 threshold without re-examining calibration
- Do not assume CIFAR-10 zoo models will show strong logit near-equivalence

### What Showed Promise
- The infrastructure (data_utils.py, metrics.py, experiment.py) is fully functional and ran successfully
- The gram-matrix L2 pairwise distance computation worked correctly
- 200 models were processed without errors

---
*Failure record written at: 2026-05-05T09:30:00.000000+00:00*
*For cross-phase reference*
