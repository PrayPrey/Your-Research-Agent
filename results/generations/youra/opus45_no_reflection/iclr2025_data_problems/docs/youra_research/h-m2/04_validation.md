# Validation Report: H-M2

**Date:** 2026-08-18
**Hypothesis:** Different attention structures create different Hessian curvature patterns
**Gate Type:** SHOULD_WORK (>10% relative difference)

---

## Gate Result: PASS

**Maximum Difference:** 90.93% (top_eigenvalue)
**Threshold:** 10%

---

## Experimental Results

### BERT Metrics
| Metric | Value |
|--------|-------|
| Top Eigenvalue | 0.0455 |
| Eigenvalue Ratio | 3.36 |
| Trace | 0.113 |
| Loss | 0.0244 |
| Parameters | 109M |

### GPT-2 Metrics
| Metric | Value |
|--------|-------|
| Top Eigenvalue | 0.502 |
| Eigenvalue Ratio | 7.64 |
| Trace | 0.746 |
| Loss | 0.0806 |
| Parameters | 124M |

### Relative Differences
| Metric | Difference | Passes Gate |
|--------|------------|-------------|
| Top Eigenvalue | 90.93% | YES |
| Eigenvalue Ratio | 56.03% | YES |
| Trace | 84.85% | YES |

---

## Configuration

- **Dataset:** SST-2 (67,349 train, 872 val)
- **Fine-tuning:** 3 epochs, AdamW, lr=2e-5
- **Hessian Batch Size:** 256 samples
- **Top-k Eigenvalues:** 20
- **Seed:** 42
- **Device:** CUDA

---

## Figures Generated

1. `gate_comparison.png` - Bar chart comparing BERT vs GPT-2 metrics
2. `eigenvalue_spectrum.png` - Top-20 eigenvalues (log scale)
3. `spectral_density.png` - Spectral density comparison

---

## Interpretation

GPT-2 shows significantly higher curvature (11x top eigenvalue) than BERT on the same task. This supports H-M2: causal attention creates different optimization landscape geometry than bidirectional attention.

Key findings:
- GPT-2 top eigenvalue (0.502) >> BERT top eigenvalue (0.046)
- GPT-2 eigenvalue ratio (7.6) > BERT ratio (3.4) — steeper spectrum decay
- GPT-2 trace (0.75) >> BERT trace (0.11) — higher total curvature

This validates that attention structure differences (H-M1) propagate to measurable Hessian curvature differences.

---

## Next Steps

H-M2 PASS enables continuation to H-M3 (Kronecker factorization hypothesis).
