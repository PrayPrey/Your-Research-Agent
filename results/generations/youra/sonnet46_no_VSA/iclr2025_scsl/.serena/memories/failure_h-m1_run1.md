# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-04T06:00:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_INCORRECT — assumed differential confidence trajectories do not materialize

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| p_minority at t* | 0.9919 | target ∈[0.3,0.7] | +0.2919 above upper bound |
| p_majority at t* | 0.9982 | target >0.80 | satisfied |
| Seeds passing | 0/5 | 4/5 required | -4 |

## Root Cause Analysis

- ERM on Waterbirds with ResNet-50 does NOT create boundary-condition minority confidence (0.3–0.7); both minority and majority samples reach near-1.0 confidence by t* (epoch with peak Hessian AUROC).
- SGD spurious-feature-first learning (LaBonte & Muthukumar 2026) does cause differential learning speed, but confidence saturates for BOTH groups before t*, so no differential trajectory window is observable at t*.
- The hypothesis assumed minority samples remain in the "boundary" regime at t*; empirically both groups saturate to ~0.99 confidence, collapsing the predicted differential.
- Hutchinson Hessian trace (h-e3, VALIDATED) correctly identifies minority membership via curvature, but confidence alone cannot — the mechanism link from curvature signal to confidence trajectory was incorrect.

## Lessons Learned

1. High Hessian trace AUROC (h-e3 PASS) does not imply differential confidence trajectories; these are orthogonal signals.
2. SGD spurious-feature exploitation manifests in curvature / gradient geometry before it manifests in prediction confidence — confidence saturates too fast.
3. Confidence-based minority detection criteria (p_min ∈ [0.3,0.7]) are too fragile for standard ERM on Waterbirds; the model converges confidence aggressively even on minority samples.
4. Future mechanism hypotheses should target gradient or Hessian geometry (already validated) rather than logit/confidence-level signals.

## Feedback for Next Phase

### Suggested Modifications
- Pivot mechanism hypothesis to gradient-alignment or feature-attribution signals rather than confidence.
- Consider early-epoch (t < t*) differential loss landscape analysis instead of confidence at t*.
- Explore whether minority samples show higher gradient variance or loss volatility across SGD steps even when confidence is saturated.

### What NOT To Do
- Do not use softmax confidence as the mechanism signal for minority detection on Waterbirds ERM — it saturates for all groups.
- Do not assume LaBonte & Muthukumar's ordering implies a persistent confidence gap at any specific checkpoint.

### What Showed Promise
- h-e3 Hessian trace AUROC ≥ 0.85 is a validated strong signal — build mechanism hypotheses around curvature geometry.
- The Hutchinson K=50 vmap+vjp pipeline is functional and reusable.

---
*For cross-phase reference*
*Written at: 2026-08-04T06:10:00+00:00*
