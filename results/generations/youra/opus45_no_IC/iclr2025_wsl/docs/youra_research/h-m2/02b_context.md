# Phase 2B Context: H-M2

**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Generated:** 2026-08-12

---

## Hypothesis Specification

**Statement:** Under trained NFN, if predictions made on permuted vs non-permuted weights, then predictions are identical, because architectural equivariance propagates to output.

**Rationale:** Confirms that equivariance property extends to final predictions, not just intermediate representations.

---

## Variables

| Type | Variable | Values |
|------|----------|--------|
| Independent | Weight permutation | Applied vs not applied |
| Dependent | Prediction difference | |pred_original - pred_permuted| |
| Controlled | Same trained NFN, same target MLP |

---

## Verification Protocol

1. Take trained NFN from H-E1
2. Make accuracy prediction on CNN weights
3. Permute CNN weights randomly, predict again
4. Verify predictions match within floating point tolerance

---

## Success Criteria (PoC)

- **Primary:** |pred_original - pred_permuted| < 1e-5
- **Secondary:** Consistent across multiple permutations (10+)

---

## Gate Information

| Property | Value |
|----------|-------|
| Gate Type | SHOULD_WORK |
| Failure Response | DEBUG NFN architecture (broken implementation) |

---

## Dependencies

| Prerequisite | Status | Gate Type |
|--------------|--------|-----------|
| H-M1 | COMPLETED | MUST_WORK |

**H-M1 Results:**
- Max Deviation: 1.19e-07
- Invariance Correlation: 0.99999986
- Gate: PASSED

---

## Experimental Setup

**Dataset:** Model Zoo CIFAR-10 CNN Subset (from Phase 2A)
**Model:** NFN (Neural Functional Network) from H-E1 checkpoint
**Source:** h-e1/checkpoints/nfn_model.pt

---

## Connection to Main Hypothesis

H-M2 is part of the causal chain validating H-EquivScale-v1:
```
H-E1 (existence) → H-M1 (layer equivariance) → H-M2 (prediction invariance) → H-M3 → H-M4 → H-M5
```

H-M2 bridges layer-level equivariance (H-M1) to task-level prediction invariance, confirming the mechanism operates end-to-end.
