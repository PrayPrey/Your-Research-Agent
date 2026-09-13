# Product Requirements Document: H-C1

**Date:** 2026-08-24
**Hypothesis:** At N=5000, all three methods (Statistics/MLP/NFN) achieve R² within ±0.03 of each other
**Type:** CONDITION | Gate: SHOULD_WORK

---

## 1. Objective

Validate that NFN's data efficiency advantage diminishes at large sample sizes by demonstrating R² convergence across Statistics, MLP, and NFN methods at N=5000 training samples.

## 2. Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Pairwise R² difference | ≤ 0.03 | max(\|R²_i - R²_j\|) for all pairs |
| Individual R² | > 0.5 | Sanity threshold |
| Statistical validity | 10 seeds | Mean ± std reported |

## 3. Scope

### In Scope
- Train Statistics, MLP, NFN on N=5000 model zoo samples
- Evaluate on fixed 500-sample test set
- 10 random seeds per method
- R² comparison visualization

### Out of Scope
- Hyperparameter sweeps (reuse H-M2 settings)
- New model zoo generation (reuse H-M2 data)
- Multi-N convergence curves (optional extension)

## 4. Data Requirements

| Item | Specification |
|------|---------------|
| Training set | 5000 ResNet-20 models |
| Test set | 500 models (fixed from H-M2) |
| Features | Flattened weights + layer statistics |
| Labels | Model accuracy (0-1 range) |

## 5. Model Requirements

### Statistics Baseline
- Linear regression on layer-wise statistics
- Features: mean, std, min, max per layer

### MLP Baseline
- 3-layer: 256 → 128 → 1
- Same input features as Statistics

### NFN (Proposed)
- Official nfn library implementation
- 32 channels, 2 NPLinear layers + HNPPool

## 6. Training Protocol

| Parameter | Value |
|-----------|-------|
| Optimizer | Adam |
| LR | 1e-3 |
| Batch size | 32 |
| Epochs | 100 |
| Loss | MSE |
| Seeds | 10 |

## 7. Deliverables

1. `run_experiment.py` - Main experiment script
2. `figures/r2_comparison_N5000.png` - Bar chart with error bars
3. `results/metrics.json` - R² values for all methods/seeds
4. `04_validation.md` - Gate evaluation report

## 8. Dependencies

- PyTorch ≥ 2.0
- nfn (pip install nfn)
- sklearn
- matplotlib

## 9. Timeline

Single-phase implementation, estimated 2-3 hours execution time.
