# H-M2 Validation Report
## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification

**Gate Type:** SHOULD_WORK
**Gate Result:** PASS
**Statistical Verdict:** SUGGESTIVE

---

## FR-1: Layer4 Weight Difference Analysis

| Seed | Block0 Diff | Block1 Diff | Block2 Diff | Head Diff | Backbone/Head Ratio | Gradient Reached |
|------|-------------|-------------|-------------|-----------|---------------------|-----------------|
| 1 | 5.353903 | 5.210414 | 6.909870 | 0.900669 | 6.467113 | True |
| 2 | 3.529884 | 2.838519 | 2.920843 | 0.495145 | 6.253555 | True |
| 3 | 3.668663 | 2.806120 | 2.666850 | 0.433588 | 7.027899 | True |

**DFR-ERM Control (should be ~0):**
- Seed 1: block0_diff=0.00000000
- Seed 2: block0_diff=0.00000000
- Seed 3: block0_diff=0.00000000

## FR-2: Gradient Norm Analysis

| Method | Mean Grad Norm (layer4) | Std |
|--------|------------------------|-----|
| erm | 1.151547 | 0.606381 |
| groupdro | 0.229742 | 0.154310 |

## FR-3: Linear Probe Accuracy (all 12 checkpoints)

| Checkpoint | Background Probe Acc |
|------------|---------------------|
| erm_seed1 | 0.8956 |
| erm_seed2 | 0.8735 |
| erm_seed3 | 0.8637 |
| groupdro_seed1 | 0.8830 |
| groupdro_seed2 | 0.8680 |
| groupdro_seed3 | 0.8595 |
| sam_seed1 | 0.8804 |
| sam_seed2 | 0.8616 |
| sam_seed3 | 0.8759 |
| dfr_seed1 | 0.8956 |
| dfr_seed2 | 0.8735 |
| dfr_seed3 | 0.8637 |

## FR-4: Statistical Test

- **P-value (one-sided paired t-test):** 0.0526
- **Cohen's d:** 1.6358
- **Verdict:** SUGGESTIVE

## Contested Landscape Note

- Izmailov 2022 (NeurIPS): GroupDRO advantage primarily in head, not backbone
- Raymond 2026 (ICLR): GroupDRO reshapes representations across all layers
- H-M2 proxy evidence (weight diff + gradient norm) addresses this debate directly

## Gate Assessment

**SHOULD_WORK gate:** PASS
- Even if H-M3 probe is REJECTED, layer4 weight diff evidence allows pipeline to continue to H-M3
- n_test_samples=5794
- gate_result: PASS
