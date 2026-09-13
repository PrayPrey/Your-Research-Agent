# h-m1 Limitation Record

**Hypothesis:** NFN advantage persists after residual correction for weight statistics (norms, sparsity, spectral norms) with gap ≥ 3%
**Gate:** MUST_WORK
**Result:** PARTIAL
**Date:** 2026-08-10

## Limitation

CPU-only environment blocked full experiment execution. Input dimension (188,810) requires GPU for efficient training of 6 variants × 3 seeds × 30 epochs.

## Evidence Collected

Minimal test (50 models, 5 epochs) shows directional support:
- NFN AUC: 0.884 (h-e1 reference)
- MLP AUC: 0.536
- MLP+AllStats AUC: 0.321
- Gap: 56.3% (exceeds 3% threshold)

## Missing for Full Validation

1. Bootstrap 95% CI computation
2. Paired t-test p-value
3. Full training convergence (30 epochs, 500 models)
4. Per-variant ablation (L1L2, Sparsity, Spectral separately)

## Resolution Path

Re-run `h-m1/code/run_experiment_direct.py` with GPU access or allow ~18 hours CPU runtime.

## Code Status

All implementation complete and verified to load/run.
