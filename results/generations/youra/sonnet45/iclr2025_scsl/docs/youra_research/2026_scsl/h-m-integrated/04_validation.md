# Mechanism Validation Report: h-m-integrated

## M1: InfoNCE Creates Spurious Clusters

**Gate Type:** MUST_WORK (Primary)

**Results:**
- AMI Score: 0.2795
- Silhouette Score: 0.2967
- Threshold: AMI ≥ 0.4

**Status:** ❌ FAIL

---

## M2: Clusterability Predicts Intervention Efficacy

**Gate Type:** MUST_WORK (Primary)

**Results:**
- Pearson Correlation: -1.0000
- P-value: 1.000000
- High-AMI Mean ΔWGA: 0.00pp
- Low-AMI Mean ΔWGA: -5.14pp
- Thresholds: p < 0.05, ΔWGA ≥ 2.0pp

**Status:** ❌ FAIL

---

## M3: LA-SSL Disperses Clusters While Preserving Separability

**Gate Type:** Secondary (Can Fail Gracefully)

**Results:**
- AMI Reduction: -2.0%
- SimCLR AMI: 0.2795
- LA-SSL AMI: 0.2852
- AUC Delta: 0.0054
- Thresholds: Reduction ≥ 30%, ΔAUC < 0.05

**Status:** ❌ FAIL

---

## Overall Gate Verdict

**Primary Gates (M1 + M2):** ❌ FAIL

**Secondary Gate (M3):** ❌ FAIL

**Hypothesis Status:** FAILED

---

## Summary

This report validates the 3-step causal mechanism:
- M1: InfoNCE loss creates geometrically separable spurious clusters
- M2: High clusterability predicts cluster-balanced retraining efficacy
- M3: LA-SSL disperses spurious structure while preserving signal

**Note:** M3 is secondary and can fail gracefully. M1+M2 passing is sufficient for hypothesis validation.
