# Phase 2B Context: H-M2

**Generated:** 2026-08-09
**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Hypothesis Statement

Update-norm parity intervention attenuates SR divergence (SR ≤ 1.1 vs baseline SR > 1.2)

## Rationale

If differential convergence rates cause Sharpness Ratio (SR) divergence between majority and minority groups, then enforcing equal update norms across groups should prevent this divergence. This tests the causal mechanism proposed by the main hypothesis.

## Success Criteria

- **Pass:** SR ≤ 1.1 sustained under parity intervention vs SR > 1.2 baseline
- **Fail:** SR remains > 1.2 despite parity intervention

## Prerequisites

- **H-E1:** SR ≈ 1 at initialization (VALIDATED ✅)
  - Result: Mean SR = 0.9999, 95% CI [0.9953, 1.0046] includes 1.0
  - Implication: No intrinsic curvature asymmetry, supporting differential convergence hypothesis

## Experimental Setup

- **Dataset:** Waterbirds (group-imbalanced: landbird/waterbird × land/water background)
- **Model:** ResNet-50 pretrained on ImageNet
- **Optimizer:** SGD with momentum
- **Seeds:** 5
- **Evaluation:** Full test set (~5,000 samples)

## Intervention Design

Update-norm parity: Scale gradients per group to enforce equal ||Δθ|| across majority/minority groups during training.

## Baseline Comparison

- **Baseline:** Standard ERM training (no intervention)
- **Expected:** SR > 1.2 by epoch 50
- **Proposed:** SR ≤ 1.1 sustained with parity intervention

## Dependencies

- Requires SR computation infrastructure from H-E1
- Requires per-group gradient computation capability

---

*Context extracted from 02b_verification_plan.md*
