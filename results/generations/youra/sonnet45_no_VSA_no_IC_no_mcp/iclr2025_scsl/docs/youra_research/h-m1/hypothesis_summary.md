# Hypothesis Summary: h-m1

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Status**: IN_PROGRESS (Phase 2C COMPLETED)  
**Generated**: 2026-08-24

---

## Statement

BN amplifies early spurious learning: ResNet-BN's batch-level statistics make stochastic batch spurious correlations easier to learn than instance-level core features, causing higher early worst-group gap.

---

## Prerequisites

- **h-e1** (VALIDATED): Confirmed BN shows 9.41pp higher worst-group gap than LN at 90% average accuracy

---

## Causal Mechanism

1. BN processes features with batch statistics (mean/variance over batch dimension)
2. Batch-level spurious correlations are stochastically amplified when present in a batch
3. LN processes features with instance statistics (mean/variance over channel/spatial)
4. Instance-level normalization does not amplify batch-level spurious patterns
5. Result: BN learns spurious features faster than core features in early training

---

## Test Method

Measure gradient flow to spurious vs core features during early training (epochs 1-20):
- Compute gradient magnitude on majority group (spurious-aligned) samples
- Compute gradient magnitude on minority group (spurious-misaligned) samples
- Calculate gradient ratio: spurious_grad / core_grad
- Compare BN vs LN gradient ratios across 10 seeds

---

## Success Criterion

- BN gradient ratio ≥ 20% higher than LN gradient ratio AND
- p < 0.05 (independent t-test) AND
- Cohen's d ≥ 0.5 (medium effect size)

---

## Falsification Criterion

- p > 0.05 OR
- BN gradient ratio < 10% higher than LN gradient ratio OR
- Cohen's d < 0.3 (small effect)

---

## Expected Outcome

If confirmed: Mechanistic understanding of h-e1 validated (BN amplifies batch-level spurious learning)

If falsified: h-e1 gap exists but mechanism unclear (alternative: optimization dynamics, feature scale differences)

**Note**: SHOULD_WORK gate failure does NOT block Phase 5 progression.
