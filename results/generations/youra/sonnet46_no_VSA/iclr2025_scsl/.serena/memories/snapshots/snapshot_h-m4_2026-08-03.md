# Hypothesis Completion Snapshot: h-m4

**Date:** 2026-08-03T13:15:00Z
**Hypothesis:** h-m4
**Statement:** Using top-k% gradient-norm samples (k=5.1%) at t* as DFR reweighting set, ℓ₁-regularized logistic regression on frozen pretrained ResNet-50 features achieves worst-group accuracy ≥ 85% on the Waterbirds test set across ≥4/5 seeds without group annotations at any stage.
**Final Status:** FAILED
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results
- Validation: FAIL
- Gate Type: MUST_WORK
- Seeds passing WGA ≥ 85%: 0/5
- Mean WGA gradnorm-DFR: 0.621 ± 0.042
- Mean WGA loss-DFR: 0.583 ± 0.089
- Mean WGA ERM: 0.559
- Secondary gate (gradnorm > loss-DFR): PASS
- k ablation best (k=15%): 0.646 — still ~20pp below threshold

## Root Cause
Frozen pretrained ResNet-50 features have a ~62-65% WGA ceiling for Waterbirds with any proxy-DFR variant. The bottleneck is representational capacity, not proxy selection quality. Standard DFR achieves ≥85% WGA using ERM-trained features, not ImageNet-pretrained features.

## Key Lessons
1. Gradient norm proxy signal quality ≠ downstream WGA performance
2. Pretrained features have ~62-65% WGA ceiling for Waterbirds
3. k ablation plateau confirms feature-space limit, not tuning problem
4. Gradient norm mechanism itself is sound and reusable (secondary gate PASS)
5. Future work needs ERM-trained features or lower WGA threshold

## Routing
ROUTED_TO_PHASE_0 — fundamental assumption violated (~23pp gap, not a near-miss)

---
*Per-hypothesis snapshot for Phase 2A reference*
