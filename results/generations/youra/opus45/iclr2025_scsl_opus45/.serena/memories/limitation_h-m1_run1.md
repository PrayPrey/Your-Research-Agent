# Limitation Record: H-M1 (Run 1)

**Date:** 2026-04-14T09:59:22Z
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Hypothesis Statement

> Under ERM training, if we compute the second derivative of normalized loss curves, then minority samples will show delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds), because prolonged optimization conflict delays the transition from convex to stable loss landscape.

## Limitation Details

The curvature timing mechanism hypothesis (H-M1) was not supported by experimental evidence. The expected 3+ epoch timing gap between minority and majority groups was not observed. Both groups showed rapid curvature stabilization at epoch 2-3, with no systematic timing difference.

This is a SHOULD_WORK gate failure, which indicates an optional mechanism investigation that did not yield expected results. The pipeline continues with this limitation noted for future research.

## Failed Checks

- Timing gap ≥ 3 epochs: FAILED (achieved: 0.20 ± 0.40 epochs)
- Pass rate ≥ 70% seeds: FAILED (achieved: 0% - 0/5 seeds)

## Partial Results

| Metric | Value |
|--------|-------|
| mean_timing_gap | 0.20 epochs |
| std_timing_gap | 0.40 epochs |
| pass_rate | 0.0% |
| seeds_passed | 0/5 |
| minority_median_epoch | 2.0 (typical) |
| majority_median_epoch | 2.0 (typical) |

## Per-Seed Results

| Seed | Timing Gap | Minority Median | Majority Median | Passes |
|------|------------|-----------------|-----------------|--------|
| 42 | 0.0 epochs | 2.0 | 2.0 | No |
| 123 | 0.0 epochs | 2.0 | 2.0 | No |
| 456 | 0.0 epochs | 2.0 | 2.0 | No |
| 789 | 1.0 epochs | 3.0 | 2.0 | No |
| 1011 | 0.0 epochs | 2.0 | 2.0 | No |

## Experiment Summary

The experiment trained ResNet-50 on Waterbirds for 20 epochs across 5 seeds, logging per-sample losses at each epoch. Normalized loss curves were computed and Gaussian-smoothed (σ=1.0). Curvature was calculated via central differences, and sign-flip epochs were detected when curvature exceeded -0.002 for 2 consecutive epochs.

Key findings:
1. **No systematic timing difference** between minority and majority groups
2. **Rapid curvature stabilization** - both groups stabilize at epoch 2-3
3. **100% stabilization rate** - all 4,795 samples stabilized within 20 epochs
4. **Pretrained model effect** - ResNet-50 pretrained on ImageNet converges very quickly

## Root Cause Analysis

1. **Fast Convergence:** Pretrained ResNet-50 converges very quickly on Waterbirds (4,795 samples). By epoch 2-3, the loss landscape has already stabilized for most samples.

2. **Curvature Sensitivity:** The curvature threshold (-0.002) and consecutive epochs (2) may be too lenient, causing both groups to "stabilize" at nearly the same early epoch.

3. **Feature vs. Mechanism:** H-E1 showed trajectory features (especially L₁) predict minority membership with AUROC=0.9452. However, this discriminative signal comes from loss magnitude, not temporal curvature dynamics.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed (timing gap and pass rate thresholds)
2. Whether the limitation is fundamental (curvature may not be the right mechanism) or circumstantial (threshold/parameter choices)
3. Alternative approaches: variance patterns, gradient norms, first-derivative analysis, distribution divergence metrics

## Pivot Recommendation

Alternative temporal signatures to explore:
- **Loss Variance Over Time:** Track variance of loss values rather than curvature
- **First-Derivative Analysis:** Focus on slope/rate of loss decrease
- **Distribution Divergence:** Use W1-distance between groups at each epoch
- **Gradient Norm Patterns:** Track gradient magnitudes during training

## Connection to Parent Hypothesis

H-E1 (EXISTENCE) successfully demonstrated AUROC = 0.9452 for minority prediction using trajectory features. The most discriminative feature was initial loss (L₁), not temporal features. This suggests minority samples are distinguished by *how much* they lose (higher initial loss), not *when* their curvature stabilizes.

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming
- **Phase 2A:** Helps avoid similar mechanism hypotheses
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---

*Limitation recorded at: 2026-04-14T09:59:22Z*
*Project: TEST_scsl_opus45_4*
*Research: Loss Trajectory Divergence Analysis for Spurious Correlation Detection*
*For cross-phase reference*
