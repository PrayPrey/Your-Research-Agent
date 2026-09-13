# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-07-10T00:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** IMPLEMENTATION_ERROR

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Metric | N/A (training failed) | N/A | N/A |

## Root Cause Analysis

- FileNotFoundError in ColoredMNIST dataset loading - MNIST data path resolution error
- Hardcoded relative path './data/MNIST/raw' fails when script runs from different working directory
- Training aborted before completion - no gradient data generated for autocorrelation analysis
- Evaluation script cannot compute gate metrics without gradient data (gradients/gradients.npz missing)
- Implementation logic appears sound - mechanism correctly implements gradient autocorrelation tracking
- Issue is purely path handling, not fundamental methodology flaw

## Lessons Learned

1. **Path Resolution:** Dataset loaders must use absolute paths or environment-aware path resolution (cache_path from config), not hardcoded relative paths
2. **Data Availability Checks:** Experiment runner should verify data exists before starting training to fail fast
3. **Error Propagation:** Shell scripts should stop execution on failure (set -e) to prevent evaluation running on missing data
4. **Implementation Quality:** Static validation passed - architecture follows specifications, code structure is correct
5. **Recommended Fix:** Quick fix in Coder-Validator loop (1 cycle) - only path handling needs correction

## Feedback for Next Phase

### Suggested Modifications
- Update `data/colored_mnist.py` ColoredMNIST constructor to use absolute cache_path from config
- Add data availability check before dataset construction in train.py
- Update run_experiment.sh to add `set -e` flag and verify MNIST data exists before training

### What NOT To Do
- Do not redesign hypothesis - mechanism logic is sound
- Do not route to Phase 0 - this is implementation bug, not fundamental flaw
- Do not change architecture or gradient tracking approach

### What Showed Promise
- Gradient autocorrelation tracking implementation is correct (C(Δt; t₀) computation)
- Power-law vs exponential model fitting with AIC selection is well-designed
- ColoredMNIST dataset construction logic correctly implements ρ control
- MLP architecture matches specification (392 → 256 → 256 → 1)

---
*For cross-phase reference*
*Written at: 2026-07-10T00:00:00Z*
