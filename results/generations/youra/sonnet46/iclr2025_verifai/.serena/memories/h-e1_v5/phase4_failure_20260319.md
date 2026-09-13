# Hypothesis Completion Snapshot: h-e1_v5

**Date:** 2026-03-19T19:27:00
**Hypothesis:** h-e1_v5
**Statement:** gamma_p = D_p^w / E[D_p^w] is well-defined (E[D_p^w]>0 for >95% problems) and non-degenerate (IQR>0.1) for ≥4/5 model-benchmark pairs
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results
- Gate: FAIL, 0/5 pairs passing (required: ≥4)
- valid_fraction range: 0.59–0.89 (threshold >0.95)
- IQR(gamma_p): ~4.4e-16 (analytically zero)
- mean_gamma: 1.25 (constant for all valid problems)

## Root Cause
gamma_p = D_p^w / E[D_p^w] is analytically constant (=1.25) by algebraic identity for k=5.
Normalizing a weighted mean pairwise Hamming diversity by its Bernoulli expected value eliminates all inter-problem variance.

## Lessons
- Avoid ratio metrics that normalize by own expected value
- Consider: raw D_p^w (unnormalized), entropy H_p, or variance across temperature
- B_p matrix k=5 solutions insufficient diversity for many problems

## Cascade
- h-e2_v5: CASCADE_FAILED
- h-m1_v5: CASCADE_FAILED

---
*Per-hypothesis snapshot for Phase 2A reference*
