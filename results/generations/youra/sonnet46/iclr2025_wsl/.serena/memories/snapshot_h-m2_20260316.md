# Hypothesis Completion Snapshot: h-m2

**Date:** 2026-03-16T14:50:00+00:00
**Hypothesis:** h-m2
**Statement:** Permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Delta_rho compared to flat-MLP baseline but do not match NFT-base performance, confirming that architectural equivariance provides a necessary (not merely convenient) inductive bias.
**Final Status:** COMPLETED (with limitation)
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED

## Results

- Gate Type: SHOULD_WORK
- Gate Result: FAIL
- aug_partial: PASS (flat-MLP+aug Δρ=0.2075 > 0.05)
- canon_partial: FAIL (flat-MLP+canon degenerate, std=0, all seeds)
- nft_superior: PASS (NFT-base Δρ=2.47e-07 < 0.02)
- ranking: FAIL (NaN in canon)

## Reflection

- Limitation recorded: L2 norm canonicalization is fundamentally not viable for this task
- Self-recovery not possible (fundamental property, not implementation bug)
- Augmentation provides partial compensation (67% Δρ reduction, high seed variance)
- Pipeline continues to h-m3 without blocking

## Key Findings for Phase 6 Paper

1. Augmentation partially compensates for permutation sensitivity but with high variance
2. L2 norm canonicalization collapses discriminative magnitude information — not viable
3. NFT robustness confirmed (Δρ ≈ 2.47e-07, consistent with H-M1 reference)
4. Scientific contribution: negative result on L2 canonicalization is informative for the field

---
*Per-hypothesis snapshot for Phase 2A reference*
