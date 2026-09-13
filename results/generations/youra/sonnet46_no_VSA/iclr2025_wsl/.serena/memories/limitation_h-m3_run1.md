# Limitation Record: h-m3 (Run 1)

**Date:** 2026-08-03T21:30:00Z
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate EXPLORE branch activated. R²(C2)=0.9148 > R²(C1)=0.851 (mechanism direction confirmed), but full gate criteria not met: R²(C2) < 0.984 and closure=0.8720 >> 0.10 threshold. The additive decomposition E[(y-ŷ)²] = MSE_res + MSE_perm does not hold causally — MSE_perm and MSE_res are not independent in CISE representations.

## Failed Checks

- R²(C2) ≥ R²(C0)=0.984: achieved 0.9148 (shortfall 0.0692)
- closure ≤ 0.10: achieved 0.8720 (ΔMSE=0.000785 vs expected MSE_perm^C1=0.006137)

## Partial Results

| Metric | Value |
|--------|-------|
| R²(C2) | 0.9148 |
| R²(C1) | 0.8511 |
| R²(C0) | 0.7316 |
| MSE_perm(C2) | ≈0 (1.16e-14 OrbitVar) |
| MSE_perm(C1) | 0.006137 |
| ΔMSE(C1→C2) | 0.000785 |
| closure | 0.8720 |
| mechanism_indicators | 3/4 pass |

## Experiment Summary

DeepSets (C2) achieves permutation invariance (OrbitVar≈0, MSE_perm≈0) and improves R² from 0.851 to 0.9148. The mechanistic direction (eliminating MSE_perm improves prediction) is confirmed. However the simple additive closure ΔMSE ≈ MSE_perm^C1 fails because permutation sensitivity and residual variance are entangled in CISE representations — eliminating permutation sensitivity also changes MSE_res in a correlated way. NFN (C3) unavailable; C2 used as fallback.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The MSE_perm/MSE_res entanglement — simple additive decomposition overstates expected improvement
2. R²(C0) reference value may be split-dependent (0.731 on N=100 test vs 0.984 in H-M2 training estimate)
3. NFN encoder as genuine C3 (not C2 fallback) may yield different closure results

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-03T21:30:00Z*
*For cross-phase reference*
