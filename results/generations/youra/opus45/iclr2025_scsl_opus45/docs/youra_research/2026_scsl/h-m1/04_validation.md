# Phase 4 Validation Report: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Curvature Timing Analysis)
**Date:** 2026-04-14
**Gate:** SHOULD_WORK

---

## Executive Summary

**Gate Result: FAIL**

The H-M1 hypothesis tested whether minority samples exhibit delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds). The experiment found **no significant timing gap** between minority and majority groups.

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Timing Gap | ≥ 3 epochs | 0.20 ± 0.40 epochs | FAIL |
| Pass Rate | ≥ 70% | 0% (0/5 seeds) | FAIL |

---

## Hypothesis Statement

> Under ERM training, if we compute the second derivative of normalized loss curves, then minority samples will show delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds), because prolonged optimization conflict delays the transition from convex to stable loss landscape.

---

## Experimental Setup

### Configuration
- **Dataset:** Waterbirds (4,795 training samples)
- **Model:** ResNet-50 (ImageNet pretrained)
- **Epochs:** 20
- **Seeds:** 5 (42, 123, 456, 789, 1011)
- **Smoothing Sigma:** 1.0
- **Curvature Threshold:** -0.002
- **Consecutive Epochs:** 2

### Methodology
1. Train ResNet-50 on Waterbirds with ERM for 20 epochs
2. Log per-sample losses at each epoch (deterministic eval pass)
3. Normalize losses by initial value: L_norm[t] = L[t] / L[0]
4. Apply Gaussian smoothing (σ=1.0) to loss trajectories
5. Compute curvature via central differences: κ[t] = L[t+1] - 2L[t] + L[t-1]
6. Detect sign-flip epoch (first epoch where κ > -0.002 for 2 consecutive epochs)
7. Compare median sign-flip epochs between minority and majority groups
8. Evaluate gate: timing gap ≥ 3 epochs in ≥ 70% of seeds

---

## Results

### Per-Seed Results

| Seed | Timing Gap | Minority Median | Majority Median | Passes Threshold |
|------|------------|-----------------|-----------------|------------------|
| 42 | 0.0 epochs | 2.0 | 2.0 | No |
| 123 | 0.0 epochs | 2.0 | 2.0 | No |
| 456 | 0.0 epochs | 2.0 | 2.0 | No |
| 789 | 1.0 epochs | 3.0 | 2.0 | No |
| 1011 | 0.0 epochs | 2.0 | 2.0 | No |

### Aggregate Statistics
- **Mean Timing Gap:** 0.20 ± 0.40 epochs
- **Pass Rate:** 0% (0/5 seeds passed ≥3 epoch threshold)
- **Minority Count:** 240 samples (G2 + G3)
- **Majority Count:** 4,555 samples (G1 + G4)

### Key Observations

1. **No Systematic Timing Difference:** Both minority and majority groups show median sign-flip epoch of 2.0 in 4 out of 5 seeds. The curvature stabilizes very early (epoch 2-3) for all samples.

2. **Rapid Curvature Stabilization:** Sign-flip detection found that 100% of samples (4,795/4,795) stabilized their curvature within the 20-epoch window. This suggests the loss curves become stable very quickly.

3. **Curvature Statistics:** Mean curvature ~0.013, std ~0.05 across seeds. Values are near zero, indicating rapid stabilization after initial epochs.

4. **Hypothesis Not Supported:** The expected 3+ epoch gap between minority and majority groups was not observed. Minority samples do not show delayed curvature stabilization.

---

## Gate Evaluation

### SHOULD_WORK Gate Criteria
- **Criterion:** Timing gap ≥ 3 epochs in ≥ 70% of seeds
- **Required:** At least 4/5 seeds (or 7/10) with gap ≥ 3
- **Achieved:** 0/5 seeds

### Gate Decision: **FAIL**

The SHOULD_WORK gate is NOT satisfied. The curvature timing mechanism hypothesis is not supported by the experimental evidence.

---

## Interpretation

### Why the Hypothesis Failed

1. **Fast Convergence:** The pretrained ResNet-50 converges very quickly on Waterbirds (4,795 samples). By epoch 2-3, the loss landscape has already stabilized for most samples, leaving insufficient dynamic range to detect timing differences.

2. **Curvature Sensitivity:** The curvature threshold (-0.002) and consecutive epochs (2) parameters may be too lenient, causing both groups to "stabilize" at nearly the same early epoch.

3. **Minority Group Size:** With only 240 minority samples, statistical power to detect subtle timing differences is limited.

4. **Feature vs. Mechanism Distinction:** H-E1 showed that trajectory *features* (especially L₁) can predict minority membership. However, this does not imply that the *mechanism* involves delayed curvature stabilization - the discriminative signal may come from loss magnitude rather than temporal dynamics.

### Connection to H-E1

H-E1 demonstrated AUROC = 0.9452 for minority prediction using trajectory features. The most discriminative feature was initial loss (L₁), not temporal features like time-to-convergence. This suggests minority samples are distinguished by *how much* they lose (higher initial loss), not *when* their curvature stabilizes.

---

## Pivot Recommendation

Per the SHOULD_WORK gate protocol, the recommended pivot is:

**Alternative temporal signatures (e.g., variance patterns)**

Potential alternatives to explore:
1. **Loss Variance Over Time:** Track variance of loss values rather than curvature
2. **First-Derivative Analysis:** Focus on slope/rate of loss decrease rather than second derivative
3. **Distribution Divergence:** Use W1-distance or other distribution metrics between groups at each epoch
4. **Gradient Norm Patterns:** Track gradient magnitudes during training

---

## Output Files

### Results
- `h-m1/code/outputs/results.json` - Complete numerical results

### Figures
- `h-m1/code/figures/gate_metrics.png` - Gate evaluation visualization
- `h-m1/code/figures/per_seed_timing_gap.png` - Per-seed timing gaps
- `h-m1/code/figures/curvature_trajectories.png` - Curvature trajectories by group
- `h-m1/code/figures/sign_flip_distribution.png` - Sign-flip epoch distributions

### Code
- `h-m1/code/run.py` - Main experiment script
- `h-m1/code/curvature.py` - CurvatureTimingAnalyzer implementation
- `h-m1/code/evaluate.py` - Gate evaluation and visualization
- `h-m1/code/train.py` - Extended training with 20-epoch trajectory logging

---

## Verification State Update

The following updates were made to `verification_state.yaml`:

```yaml
sub_hypotheses:
  h-m1:
    status: COMPLETED
    completed: true
    gate:
      satisfied: false
      result: FAIL
    validation:
      status: COMPLETED
      result: FAIL
      key_findings:
        - "Timing gap = 0.20 +/- 0.40 epochs"
        - "Pass rate = 0.0% (threshold: 70%)"
        - "Gate SHOULD_WORK: FAILED"
```

---

## Conclusion

The H-M1 curvature timing mechanism hypothesis is **NOT SUPPORTED**. Minority samples do not exhibit delayed curvature stabilization compared to majority samples. The loss curvature stabilizes very early (epoch 2-3) for both groups, leaving no measurable timing gap.

This failure does not invalidate the parent hypothesis (H-E1), which successfully demonstrated that trajectory features can predict minority group membership. Rather, it suggests that the mechanistic explanation for this predictive power lies elsewhere - likely in the magnitude of losses rather than their temporal curvature dynamics.

---

*Generated by Phase 4 Validation*
*Hypothesis: H-M1 (Curvature Timing Analysis)*
*Gate: SHOULD_WORK - FAIL*
*Pivot: Alternative temporal signatures recommended*
