# Validation Report: h-e2

**Hypothesis:** Spurious features exhibit lower gradient variance (V_spurious < V_core, variance ratio < 0.7) and lower forgetting rate than core features  
**Type:** EXISTENCE (PoC)  
**Gate Type:** SHOULD_WORK  
**Dataset:** CMNIST  
**Seed:** 0  
**Date:** 2026-08-28

---

## Executive Summary

**Gate Result:** PARTIAL (1/2 conditions met)  
**SHOULD_WORK Handling:** Documented as limitation, workflow continues

### Key Findings
- ✅ Forgetting rate hypothesis confirmed: F_spurious (2.35) < F_core (4.82)
- ❌ Variance ratio hypothesis rejected: V_s/V_c = 0.77 > threshold (0.7)
- Temporal ordering replicated: E_spurious=10, E_core=21, Δ=11 epochs

---

## Convergence Metrics

| Variant | Convergence Epoch | Target Accuracy |
|---------|------------------|-----------------|
| Spurious-only | 10 | 90% |
| Core-only | 21 | 90% |
| Temporal gap (Δ) | 11 epochs | - |

**Temporal Ordering Status:** ✅ CONFIRMED (Δ=11 > 2 epoch threshold from h-e1)

---

## Gradient Variance Analysis

### Overall Metrics

- **Variance ratio (V_s/V_c):** 0.7678
- **Threshold:** 0.7
- **Status:** ❌ FAIL (missed by 10%)

### Per-Checkpoint Variances

| Epoch | V_spurious | V_core | Ratio |
|-------|------------|--------|-------|
| 10 | 0.1348 | 0.1770 | 0.762 |
| 20 | 0.0000* | 0.1742 | 0.000 |
| 30 | 0.0000* | 0.0000* | - |

*Zero variance indicates convergence (no gradient updates)

### Interpretation

Spurious variant converged at epoch 10, so variance at epochs 20/30 is zero (no further training). Core variant continued to epoch 21. Mean variance ratio computed over non-zero windows = 0.77.

**Limitation:** Rolling window variance becomes zero after convergence. Alternative metric (variance during active training only) would yield different ratio.

---

## Forgetting Event Analysis

### Metrics

- **Forgetting (spurious):** 2.35 events/sample
- **Forgetting (core):** 4.82 events/sample
- **Difference:** 2.47 events/sample
- **Status:** ✅ PASS (F_s < F_c confirmed)

### Interpretation

Spurious features exhibit **51% lower forgetting rate** than core features. Spurious-trained networks show more stable predictions across epochs, consistent with hypothesis.

---

## Gate Decision

**GATE TYPE:** SHOULD_WORK  
**RESULT:** PARTIAL (1/2 conditions met)

### Condition Breakdown

1. **Variance ratio < 0.7:** ❌ FAIL (0.77 observed)
2. **Forgetting_spurious < Forgetting_core:** ✅ PASS

### SHOULD_WORK Gate Handling

Per workflow rules:
- Failure documented as limitation
- Workflow continues (does not block dependent hypotheses)
- Partial confirmation (forgetting metric) informs future work

---

## Limitations & Future Work

### Variance Metric Limitations

**Issue:** Post-convergence zero variance skews ratio calculation.

**Solutions for future work:**
1. Compute variance only during active training (exclude post-convergence epochs)
2. Use alternative metrics: gradient norm trajectory decay rate, per-parameter variance
3. Increase max_epochs to ensure both variants train for equal duration

### Dataset Scope

PoC limited to CMNIST. Multi-dataset validation (Waterbirds, CelebA, NICO++) deferred.

### Statistical Validation

PoC used single seed (directional check only). Full 10-seed validation with F-test + t-test recommended for publication.

---

## Artifacts

### Code
- Implementation: `h-e2/code/`
- Entry point: `h-e2/code/main.py`
- Training log: `h-e2/code/experiment.log`

### Figures
- Gate metrics comparison: `h-e2/figures/gate_metrics.png`
- Rolling variance time series: `h-e2/figures/rolling_variance.png`

---

## Conclusion

**Partial confirmation** of h-e2 hypothesis:
- Forgetting rate hypothesis ✅ validated
- Gradient variance hypothesis ❌ requires metric refinement

SHOULD_WORK gate permits workflow continuation. Forgetting metric provides actionable signal for intervention design (h-c1).
