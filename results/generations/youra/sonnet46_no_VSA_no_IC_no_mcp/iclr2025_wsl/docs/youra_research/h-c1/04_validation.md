# Validation Report: H-C1 — Sign-Flip Canonicalization Uniqueness Audit

**Hypothesis:** H-C1  
**Type:** CONDITION  
**Date:** 2026-08-27  
**Gate type:** SHOULD_WORK  
**Gate result:** FAIL (SCOPE_BOUNDARY)  
**Validation status:** COMPLETED  

---

## Summary

Sign-flip canonicalization (majority-sign simultaneous flip) does **not** produce a unique canonical form for ≥99% of Schürholt MNIST zoo models. With N=500 sampled models, only 14.4% had no tied neurons (fraction_unique=0.144), far below the 0.99 threshold. Idempotency is perfect (fraction_idempotent=1.00).

**Root cause:** With d_in=784 (even), exactly 392 positive and 392 negative weights in a row yields a sign tie. At the Schürholt zoo weight scale (~±0.2), this occurs in 85.6% of models — multiple neurons per model, on average 2.2 tied neurons per degenerate model.

---

## Gate Checks

| Check | Metric | Threshold | Result |
|-------|--------|-----------|--------|
| P1: fraction_unique | 0.1440 | ≥ 0.99 | **FAIL** |
| P2: fraction_idempotent | 1.0000 | == 1.00 | **PASS** |
| **Gate verdict** | | | **SCOPE_BOUNDARY** |

---

## Experiment Results

### Dataset
- N=500 models from Schürholt MNIST zoo (local archive, seed=1)
- Architecture: M=2 MLP (784→64→10), W1=(64,784), W2=(10,64)

### Uniqueness Audit
| Metric | Value |
|--------|-------|
| n_total | 500 |
| degenerate_count | 428 |
| fraction_unique | **0.1440** |
| fraction_idempotent | **1.0000** |

### Degeneracy Characterization
| Metric | Value |
|--------|-------|
| mean_tied_neurons per degenerate model | 2.20 |
| max_tied_neurons in any model | 8 |
| mean L1-norm of tied neuron rows | 0.0403 |
| mean weight std of tied neuron rows | 0.0505 |

Tied neurons have notably small L1 norms (~0.04 vs typical weight scale ~0.1-0.2), confirming that ties correlate with near-zero weight rows where equal positive/negative weights nearly cancel.

---

## Root Cause Analysis

**Why are ties so frequent?**

With d_in=784 (even), a row has exactly 392 positive and 392 negative weights when the sign count is exactly balanced. Under the Binomial model B(784, p) where p is the probability a weight is positive:
- If p ≈ 0.5 (symmetric weight distribution), Pr(exactly 392 positive) = C(784,392) × 0.5^784 ≈ 0.028 per neuron
- With 64 neurons per model, expected tied neurons per model ≈ 64 × 0.028 ≈ 1.8
- Probability at least one tied neuron per model ≈ 1 - (1-0.028)^64 ≈ 83%

The observed 85.6% degeneracy rate and 2.2 mean tied neurons match this binomial prediction. The Schürholt zoo weight distribution is approximately symmetric (trained networks on MNIST with no weight regularization asymmetry), so the tie rate is determined by combinatorics, not training pathology.

**Why does d_in=784 specifically cause this?**

784 = 16 × 49 is even. If d_in were odd, no exact tie is possible. The M=2 MNIST MLP with 784 input dimensions is structurally vulnerable to sign ties at the input-to-hidden layer regardless of weight scale.

---

## Idempotency Confirmation

All 500 models pass `canon(canon(W)) == canon(W)` with atol=1e-6. The tie-breaking rule (+1 default for tied neurons) makes the algorithm deterministic and idempotent, but the canonical form is ambiguous for degenerate models — the +1 tie-break is a convention, not a symmetry-derived choice.

---

## Implications for Parent Hypotheses

### Impact on H-M3
H-M3's canonicalization applied the same majority-sign algorithm. 85.6% of the 500 models had at least one ambiguously-canonicalized neuron. This means H-M3's "canonicalized" condition D was applying a **deterministic but not symmetry-unique** transformation for most models — the canonical form was reproducible (idempotent) but not the symmetry-group canonical form. This partially explains why H-M3 found no improvement from canonicalization.

### Scope boundary for sign-flip canonicalization
The majority-sign algorithm as defined does not achieve unique canonical forms for M=2 MLPs with even d_in (784). Alternative approaches:
1. **Different tie-breaking:** Use a deterministic secondary criterion (e.g., first weight sign, weight L2-norm magnitude) — this gives a canonical form but is not symmetry-derived
2. **Weight perturbation:** Add tiny noise before computing majority sign — changes the group-theoretic interpretation
3. **Random flip exclusion:** Skip sign-flip for tied neurons (leave them as-is) — reduces the transformation
4. **Scaling-only (Condition B):** Fall back to norm-based scaling without sign-flip — avoids the tie issue entirely
5. **d_in=odd architectures:** Sign-flip canonicalization is exact for odd d_in (e.g., d_in=785 or pad to odd)

---

## Validation Conclusion

**Gate: FAIL / SCOPE_BOUNDARY**

The sign-flip canonicalization algorithm does not produce unique canonical forms for ≥99% of Schürholt MNIST zoo M=2 MLP models. The failure is structural — tied neurons arise from combinatorics of even d_in=784, not from weight scale or training details. Fraction_unique=0.144 is far below the 0.99 threshold and the 0.95 scope boundary.

**Recommendation:** Document this as a limitation of sign-flip canonicalization on even-d_in architectures. The YOURA hypothesis chain should explore:
- Scaling-only canonicalization (Condition B from H-M3, which doesn't have this tie issue)
- Alternative canonicalization that avoids parity sensitivity

**This gate is non-blocking (SHOULD_WORK type).** Document and proceed.

---

## Files

| File | Path |
|------|------|
| Results JSON | `h-c1/results/audit_results.json` |
| Gate metric figure | `h-c1/figures/gate_metric.png` |
| Tied neuron histogram | `h-c1/figures/tied_neuron_hist.png` |
| Experiment log | `h-c1/experiment.log` |
| Code | `h-c1/code/` |
