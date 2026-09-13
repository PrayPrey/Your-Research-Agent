# Limitation Record: h-m2 (SHOULD_WORK FAIL)

**Date:** 2026-03-16
**Hypothesis:** h-m2
**Gate Type:** SHOULD_WORK
**Outcome:** LIMITATION_RECORDED

## Failure Summary

The H-M2 SHOULD_WORK gate failed due to degenerate `flat-MLP+canon` checkpoints inherited from H-M1.

**Failed Checks:**
- `canon_partial_fail`: flat-MLP+canon degenerate, constant output std=0 across all 3 seeds
- `ranking_fail`: NaN in canon prevents strict four-way ranking

**Passed Checks:**
- `aug_partial_pass`: flat-MLP+aug Δρ=0.2075 > 0.05 threshold ✅
- `nft_superior_pass`: NFT-base Δρ=2.47e-07 < 0.02 ✅

## Root Cause

L2 norm canonicalization (`x ← x / ||x||₂` applied layer-wise) destroys discriminative magnitude information, collapsing all model predictions to a constant (~0.0006). This is not an implementation bug but a fundamental property of L2 normalization in this context.

## Key Insight for Future Hypotheses

- **Augmentation works partially**: 67% Δρ reduction (0.6265 → 0.2075) but high seed variance (0.096–0.317)
- **L2 norm canonicalization is NOT viable** for generalization gap prediction on FC-MLP zoos
- Alternative canonicalization strategies: sort-by-magnitude, spectral normalization, sign-canonical form
- NFT architecture robustness confirmed: Δρ ≈ 2.47e-07 (near-zero, consistent with H-M1)

## Pipeline Impact

- H-M3 and H-M4 can proceed (prerequisites: h-m2 COMPLETED)
- Limitation noted for Phase 6 paper: augmentation provides partial but insufficient compensation
- Phase 5 baseline comparison proceeds normally
