# H-M2 SHOULD_WORK Limitation Record

**Hypothesis:** h-m2 — DFR head retraining reduces head-only lambda_max vs ERM head
**Gate:** SHOULD_WORK
**Outcome:** LIMITATION_RECORDED (gate FAIL, non-blocking)
**Date:** 2026-08-05

## Failure Summary

- ERM head-only λ_max mean = 4.90 (much lower than full-model ERM = 124.25)
- DFR head-only λ_max mean = 211.78 (opposite direction — DFR head is sharper)
- Paired t-test: t=130.09, p_one_sided=1.000 (DFR > ERM, not DFR < ERM)
- DFR WGA = 0.778 (below expected 0.93-0.97 from Kirichenko 2022)

## Failed Checks

- lmax_direction_correct = False (DFR head λ_max > ERM head λ_max)
- majority_seeds_pass = False (0/3 seeds DFR < ERM)
- mechanism_activated = False

## Root Cause Analysis

1. ERM fc layer (trained with SGD + weight decay) is already smooth (λ_max ~5)
2. DFR via sklearn LogisticRegression C=0.1 creates high-norm weights → sharper head
3. The head-only curvature is dominated by weight geometry, not spurious feature alignment
4. Full-model curvature (H-M1: ERM=124.25) comes primarily from the backbone, not the head

## Lessons for Future Hypotheses

- Head-only Hessian is NOT a proxy for full-model Hessian when backbone dominates curvature
- DFR's benefit is in feature reweighting, not curvature reduction
- LR-based head retraining (sklearn) may create sharper geometry than SGD-trained heads
- SHOULD_WORK failure is non-blocking — pipeline continues to Phase 5
