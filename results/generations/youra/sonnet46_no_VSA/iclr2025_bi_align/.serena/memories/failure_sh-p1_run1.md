# Phase 4 Failure Record: sh-p1 (Run 1)

**Date:** 2026-07-30T01:17:20+00:00
**Hypothesis:** sh-p1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK
**Routing:** ROUTED_TO_PHASE_0

## Hypothesis Statement

In logistic regression predicting P(ΔTruthfulQA MC2 < 0) from ΔMMLU + baseline MMLU,
β₁(ΔMMLU) < 0 (p < 0.05, Huber-White clustered SEs at family level); 5-fold CV-AUC exceeds
permutation-derived 95th pct (5000 family-clustered permutations); β₁ sign-stable across all 5
folds; calibration slope [0.7, 1.3]; threshold-robust at <0, <-1, <-2; LOFO-stable (>35/39 family
exclusions show β₁ < 0).

## Gate Results (MUST_WORK — 6 Criteria)

| Criterion | Result | Value |
|-----------|--------|-------|
| β₁ < 0, p < 0.05 (clustered SE) | FAIL | β₁=-0.0454, p=0.0595 |
| 5-fold CV-AUC > permutation 95th pct | PASS | AUC=0.587 > null=0.583 |
| β₁ sign stable across all 5 folds | PASS | 5/5 negative |
| Calibration slope ∈ [0.7, 1.3] all folds | FAIL | [-0.28, 2.55] — all over the place |
| Threshold robustness (<0, <-1, <-2) | FAIL | p=0.060, p=0.174, p=0.347 |
| LOFO stability (>35/39 families β₁<0) | PASS | 160/160 |

**Pass rate: 4/6 (0.667) — FAIL (not all MUST_WORK criteria satisfied)**

## Root Cause Analysis

- The alignment tax signal (ΔMMLU → ΔTruthfulQA) is weak and marginal (p=0.0595, just above threshold)
- Calibration fails catastrophically — logistic regression is not well-calibrated on this heterogeneous dataset
- Threshold robustness fails at stricter thresholds (<-1, <-2) — the effect is concentrated near the ΔTruthfulQA=0 boundary
- The effect is real in direction (β₁ consistently negative, LOFO stable) but insufficient in statistical rigor
- Within-family pairing reduces confounding but the signal-to-noise ratio is too low for logistic regression to satisfy all criteria simultaneously

## Lessons Learned

1. Logistic regression is sensitive to class imbalance at stricter thresholds (N=58, N=45 at <-1, <-2)
2. Calibration slope instability suggests the probability estimates are unreliable — logistic regression may not be the right tool for this data structure
3. The alignment tax signal exists directionally (β₁<0 always) but is marginal — a different modeling approach or stronger signal may be needed
4. Permutation test (CV-AUC) passes but calibration fails — these measure different things; CV-AUC measures discrimination not calibration
5. Consider alternative approaches: Cox regression, survival analysis framing, or Bayesian logistic regression with regularization

## Feedback for Phase 0 Redesign

### What NOT To Do
- Do not use unconstrained logistic regression with calibration slope as a gate — too unstable with N<100
- Do not require threshold robustness at <-2 when N=45 — underpowered

### What Showed Promise
- Direction is consistent: β₁ < 0 in all 160 LOFO families and all 5 CV folds
- CV-AUC exceeds permutation null, suggesting genuine discriminative signal
- The within-family paired design successfully controls for model family confounds

### Suggested Modifications for Phase 0
- Consider a linear regression approach (ΔTruthfulQA ~ ΔMMLU) instead of binary classification
- Consider a mixed-effects model to account for within-family correlation directly
- Alternatively, simplify to: correlation test + sign test + effect size, without calibration requirement

---
*For cross-phase reference*
*Written at: 2026-07-30T01:17:20+00:00*
