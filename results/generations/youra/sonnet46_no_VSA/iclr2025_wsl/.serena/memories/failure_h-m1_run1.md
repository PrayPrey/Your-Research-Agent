# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-03T15:00:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MATHEMATICAL_INVARIANCE — hypothesis assumes aliasing that cannot exist by construction

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| mean OrbitVar(C1) | 1.24e-33 | 0.005 (threshold) | -0.005 (100%) |

## Root Cause Analysis

- Per-layer quantile features are ORDER STATISTICS: they are mathematically invariant to any permutation of channels within a layer by construction
- S_16³ channel permutations reorder channels but do not change the sorted quantile distribution
- Therefore OrbitVar(C1) is identically ~0 (machine-epsilon noise only) for ALL models — no aliasing is possible
- The hypothesis was logically ill-posed: it predicted aliasing in an encoder that is provably permutation-invariant

## Lessons Learned

1. Per-layer quantile encoders are permutation-invariant by construction — do not test for aliasing under permutations of the dimension that is being summarized
2. Before designing an aliasing experiment, verify that the encoder CAN produce different outputs under the proposed symmetry group
3. OrbitVar as a metric is correct, but requires an encoder that is NOT invariant to the test symmetry
4. The GBM classifier can still learn useful representations; the aliasing question requires a structurally different encoder (e.g., one that preserves channel identity information)

## Feedback for Next Phase

### Suggested Modifications
- Design encoder C2 that retains channel-order information (e.g., concatenated per-channel statistics, positional encoding, or graph-based approach)
- Verify analytically that the proposed encoder is NOT invariant to the symmetry group before running the experiment
- Consider testing aliasing under layer permutations (not channel permutations) where quantile encoders ARE sensitive

### What NOT To Do
- Do not test permutation-aliasing on any encoder that uses order statistics (quantiles, sorted values, histograms) over the permuted dimension
- Do not assume aliasing exists without checking encoder invariances first

### What Showed Promise
- OrbitVar metric is well-defined and correctly implemented
- ModelZooDataset CIFAR10-GS pipeline (data loading, feature extraction) worked correctly
- LightGBM HP search framework is reusable for h-m2+

---
*For cross-phase reference*
*Written at: 2026-08-03T15:00:00+00:00*
