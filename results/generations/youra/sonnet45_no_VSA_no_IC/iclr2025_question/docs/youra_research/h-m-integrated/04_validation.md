# Validation Report: h-m-integrated

## Gate Results

**Gate Status:** PASSED ✓
**Reason:** 5/5 non-degenerate methods passed gate

### Method Results

| Method | Spearman ρ | AUROC | AUSE | Pass |
|--------|------------|-------|------|------|
| temp_scaling | 0.810 | 1.000 | 0.362 | ✓ |
| conformal | 0.810 | 1.000 | 0.362 | ✓ |
| mc_k1 (degenerate) | 0.803 | 0.996 | 0.362 | ✓ |
| mc_k3 | 0.810 | 1.000 | 0.362 | ✓ |
| mc_k5 | 0.810 | 1.000 | 0.362 | ✓ |
| mc_k10 | 0.810 | 1.000 | 0.362 | ✓ |

## Figures

- [Gate Metrics Scatter](figures/gate_metrics_scatter.png)
- [Spearman Comparison](figures/spearman_comparison.png)
- [AUSE vs AUROC](figures/ause_vs_auroc.png)
- [Sparsification Curves](figures/sparsification_curves.png)

## Reflection

Mechanism validation PASSED. All non-degenerate UQ methods produce uncertainty scores that correlate with incorrectness. Pipeline works end-to-end at 8B scale.