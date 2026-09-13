# H-M2 Phase 4 Failure Record
## Hypothesis: Permutation Orbit Variance Dominance

**Date:** 2026-05-21
**Phase:** Phase 4 (PoC Validation)
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Routing:** ROUTED_TO_PHASE_0

---

## Failure Summary

**Hypothesis:** Var_perm / (Var_perm + Var_GL) > 0.60 across Small CNN Zoo checkpoint trajectories

**Result:** var_ratio_mean = 0.3479 ± 0.0536 (n=1000 models, CIFAR-10-GS)

Gate threshold 0.60 NOT met. PIVOT required per hypothesis design.

---

## Key Findings (Scientifically Valuable)

### Layer-Type Breakdown (CRITICAL INSIGHT)
| Layer Type | Var_perm | Var_GL | Ratio | Status |
|------------|----------|--------|-------|--------|
| Conv2d     | 97.62    | 55.29  | 0.637 | PASS   |
| Linear     | 33.84    | 223.52 | 0.133 | FAIL   |

Root cause: Permutation symmetry dominates Conv2d layers, but Linear layers (FC/attention) have substantially larger GL orbit variance. The composite ratio fails because Linear layer GL variance overwhelms the mean.

### Trajectory Evolution
- Ratio decreases monotonically during training (from ~0.49 at epoch 0 to ~0.28 at epoch 50)
- Training learns non-permutation structure in Linear layers over time

---

## Pivot Recommendation

The hypothesis anticipated this outcome: "GATE: if ratio < 0.60, pivot to hybrid orbit-PE + GL trace features before H-M3"

Recommended pivot for next pipeline iteration:
1. Add GL-invariant polynomial features: tr(W W^T), tr((W W^T)^2) for Linear layers
2. Add GL trace features from arXiv:2410.04207: tr(W^Q W^{K,T}) for attention
3. Implement hybrid orbit-PE: permutation orbit for Conv2d + GL traces for Linear

---

## Working Code Infrastructure

All components validated and reusable:
- orbit_projector.py: Permutation orbit basis via SVD + GL orbit via polar decomposition
- variance_decomposer.py: Full trajectory variance decomposition
- evaluate.py: Zoo-scale analysis (1000 models × 50 checkpoints)
- data_loader.py: CNN Zoo CIFAR-10 trajectory loading (fixed symlink followlinks bug)

---

## Lessons Learned

1. Permutation symmetry is layer-type-specific: Works for Conv2d but not Linear/attention
2. GL orbit variance dominates Linear layers - significant non-permutation symmetry in FC layers
3. Hybrid approach required for cross-architecture weight space learning
4. Early training has higher permutation dominance (ratio decreases during training)
5. Data infrastructure fully reusable for H-M3
