# Phase 6.5 Adversarial Review Changelog

**Paper:** DNSI: A Difficulty-Normalized Saturation Index
**Review Date:** 2026-08-28

---

## Round 1 Changes

### Abstract (Line 7)

**Before:**
> Experiments across four benchmarks with published generalization gaps show DNSI correlates strongly with gap magnitude (R = -0.95), functions as a leading indicator (R² = 0.35 for temporal prediction), and generalizes across vision and NLP domains.

**After:**
> In a pilot study across four benchmarks with published generalization gaps, DNSI correlates with gap magnitude (R = -0.95, though n=4 yields wide confidence intervals), shows promise as a temporal predictor (R² = 0.35, with caveats noted below), and exhibits consistent direction across vision and NLP domains.

**Rationale:** Tempered overclaiming; acknowledged sample size limitations.

---

### Introduction Contribution 3 (Line 29)

**Before:**
> We show that pre-saturation DNSI values predict future generalization gaps (R² = 0.349), establishing DNSI as a leading indicator rather than a retrospective measurement, with cross-domain validity in both vision (R = -0.972) and NLP (R = -0.684).

**After:**
> We provide preliminary evidence that pre-saturation DNSI values correlate with future generalization gaps (R² = 0.349), with consistent negative direction across vision (R = -0.972) and NLP (R = -0.684) domains, though small sample sizes warrant cautious interpretation.

**Rationale:** Removed unsupported "leading indicator" claim; added caveat.

---

### Results Section 5.1 (Line 199)

**Before:**
> The correlation substantially exceeds our -0.4 threshold.

**After:**
> The point estimate exceeds our -0.4 threshold, though with n=4, bootstrap confidence intervals span the full range [-1, 1]. [...] We emphasize this as preliminary evidence requiring replication with larger benchmark samples.

**Rationale:** Disclosed bootstrap CI instability.

---

### Results Section 5.2 (Line 203)

**Before:**
> Pre-2019 DNSI predicts post-2019 gaps: R² = **0.349** (threshold: 0.3). Negative slope (-0.328) confirms directional consistency.

**After:**
> Pre-2019 DNSI predicts post-2019 gaps: R² = **0.349** (threshold: 0.3). Negative slope (-0.328) confirms directional consistency. However, leave-one-out cross-validation yields R² = -3.82, indicating high variance with n=4; the temporal signal requires validation on larger samples before deployment as a practical leading indicator.

**Rationale:** Disclosed LOO-CV failure that was previously buried.

---

### Discussion Section 6.1 (Line 228)

**Before:**
> The strong DNSI-gap correlation (R = -0.95) suggests that improvement entropy, normalized by task difficulty, captures fundamental benchmark evolution dynamics. The temporal prediction result (R² = 0.35) establishes DNSI as a leading indicator, enabling benchmark health assessment without held-out test sets.

**After:**
> The DNSI-gap correlation (R = -0.95) suggests that improvement entropy, normalized by task difficulty, may capture benchmark evolution dynamics. However, with n=4, this represents preliminary evidence. The temporal prediction result (R² = 0.35) suggests potential as a leading indicator, though LOO-CV instability (R² = -3.82) indicates the model does not yet generalize reliably — larger benchmark samples are needed before practical deployment.

**Rationale:** Full disclosure of limitations in main discussion.

---

### Conclusion (Line 248)

**Before:**
> We began by asking: which benchmarks are worth improving? Our work provides an answer. DNSI (Difficulty-Normalized Saturation Index) correlates strongly with generalization gaps (R = -0.95), functions as a leading indicator (R² = 0.35), and generalizes across vision and NLP domains.

**After:**
> We began by asking: which benchmarks are worth improving? Our pilot study suggests DNSI (Difficulty-Normalized Saturation Index) as a candidate answer. DNSI correlates with generalization gaps (R = -0.95, n=4) and shows consistent direction across vision and NLP domains, though larger-scale validation is needed before deployment.

**Rationale:** Tempered conclusion to match pilot study framing.

---

## Round 2 Changes

### Introduction Contribution 2 (Line 27)

**Before:**
> We demonstrate that DNSI correlates strongly with known generalization gaps (Pearson R = -0.950, p = 0.050)

**After:**
> We demonstrate that DNSI correlates with known generalization gaps (Pearson R = -0.950, p = 0.050, n=4)

**Rationale:** Removed "strongly", added sample size for consistency.

---

### Related Work Section 2.4 (Line 65)

**Before:**
> correlates strongly with measured generalization gaps (R = -0.95)

**After:**
> correlates with measured generalization gaps (R = -0.95, n=4)

**Rationale:** Consistency with rest of paper.

---

## Summary

| Round | Changes | Type |
|-------|---------|------|
| R1 | 6 | Language tempering, LOO-CV disclosure |
| R2 | 2 | Consistency fixes |
| **Total** | **8** | |
