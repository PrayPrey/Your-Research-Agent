# Phase 4 Validation Report: H-M2

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Date:** 2026-08-24  
**Gate Type:** MUST_WORK

## Hypothesis Statement

At N=500 training models, NFN R² exceeds MLP R² by at least 0.1 (p < 0.05).

## Gate Verdict

**PASSED**

## Summary

The NFN (permutation-equivariant) architecture dramatically outperforms the MLP baseline at N=500 training samples, with a delta of 2.50 R² points (far exceeding the 0.1 threshold) and p < 0.00001.

## Results

### Gate Check at N=500 (10 seeds)

| Metric | NFN | MLP |
|--------|-----|-----|
| Mean R² | 0.9985 ± 0.0007 | -1.5015 ± 0.7725 |
| Best R² | 0.9994 | -0.8892 |
| Worst R² | 0.9969 | -3.6988 |

**Delta (NFN - MLP):** 2.5000 ± 0.7725  
**p-value:** 4.58e-06  
**Statistical significance:** Yes (p < 0.05)

### Per-Seed Results

| Seed | NFN R² | MLP R² | Delta |
|------|--------|--------|-------|
| 0 | 0.9992 | -1.3677 | 2.3669 |
| 1 | 0.9990 | -1.2671 | 2.2661 |
| 2 | 0.9979 | -1.1316 | 2.1295 |
| 3 | 0.9994 | -0.8892 | 1.8886 |
| 4 | 0.9986 | -3.6988 | 4.6974 |
| 5 | 0.9983 | -1.4528 | 2.4511 |
| 6 | 0.9982 | -1.2564 | 2.2546 |
| 7 | 0.9986 | -0.9631 | 1.9617 |
| 8 | 0.9987 | -1.8122 | 2.8109 |
| 9 | 0.9969 | -1.1761 | 2.1730 |

## Analysis

### Key Findings

1. **NFN achieves near-perfect R² (0.9985)** at N=500, demonstrating that the equivariant architecture can learn accurate accuracy prediction with limited training data.

2. **MLP completely fails (negative R²)** with the same N=500 samples. Negative R² means predictions are worse than predicting the mean — the MLP cannot learn the weight-to-accuracy mapping without massive data.

3. **Effect size is massive (delta=2.50)**, far exceeding the 0.1 threshold. This is because NFN's architectural equivariance provides an extreme inductive bias advantage.

4. **Results are consistent across all 10 seeds** — every seed shows NFN R² > 0.99 while MLP R² < 0.

### Why MLP Fails

The MLP receives flattened ~270K-dimensional weight vectors with no structure. At N=500 samples:
- Cannot learn permutation invariance from data (would need exponentially more samples)
- Severely overparameterized (more weights than samples)
- No generalization possible without equivariance constraint

### Why NFN Succeeds

The NFN's DeepSets-style equivariant architecture:
- Processes each layer's weights with shared per-neuron MLPs
- Applies permutation-invariant pooling (mean aggregation)
- Eliminates need to learn permutation invariance from data
- Much lower effective parameter count via weight sharing

## Figures

- `figures/gate_comparison.png` — Bar chart comparing NFN vs MLP R² at N=500
- `figures/seed_scatter.png` — Per-seed NFN R² vs MLP R² scatter plot
- `figures/box_distribution.png` — Box plot of R² distributions

## Gate Satisfaction

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| NFN R² - MLP R² | ≥ 0.1 | 2.50 | ✓ PASS |
| p-value | < 0.05 | 4.58e-06 | ✓ PASS |
| Consistent across seeds | Yes | 10/10 NFN > MLP | ✓ PASS |

## Conclusion

**H-M2 is VALIDATED.** The permutation-equivariant NFN architecture provides a dramatic data efficiency advantage over MLP at N=500 training samples. The mechanism hypothesis is confirmed: architectural equivariance eliminates the need to learn permutation invariance from data, enabling effective learning with limited samples.

## Files Generated

- `code/` — Implementation (config, data, nfn_model, mlp_model, train_common, sweep, stats, evaluate)
- `code/figures/` — Visualization outputs
- `code/results/results.json` — Full numerical results
- `04_validation.md` — This report
