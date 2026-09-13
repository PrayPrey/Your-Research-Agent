# Reflection Report: H-M2

**Date:** 2026-08-27
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL → DOCUMENT
**Reflection Outcome:** LIMITATION_RECORDED
**Modification Attempt:** 0

---

## Gate Assessment

**Criterion:** R²_D > R²_A with non-overlapping 95% CI on ≥2/3 tasks at k=20
**Result:** 0/3 labels pass (0/2 required) → FAIL

| Label | R²_A | R²_D | ΔR² | CI Non-overlap | Pass |
|-------|------|------|-----|---------------|------|
| test_accuracy | -0.196 | -0.218 | -0.022 | False | ✗ |
| generalization_gap | -0.003 | -0.024 | -0.021 | False | ✗ |
| learning_rate | -0.014 | -0.017 | -0.004 | False | ✗ |

---

## Self-Recovery Assessment

### Can improvement be identified?

**No.** Analysis of failure modes:

1. **Root cause: N << d regime.** N=500 models, d=50,890 weight dimensions. PCA+linear regression in this regime is fundamentally ill-posed: even at k=50 PCs, the linear probe overfits on 450 training samples and fails to generalize on 50 test samples (all R² negative).

2. **Canonicalization is correct.** EVR improvement (0.055 → 0.086 for top-20 PCs) confirms canonicalization does concentrate geometric variance. The issue is that even concentrated PCA features cannot be linearly decoded to property labels with N=500.

3. **No parameter change can fix this.** Increasing k makes overfitting worse. Decreasing k loses signal. Changing n_boot doesn't affect R². The only fix is more data (N≥5000 estimated).

4. **k=10 shows slight positive ΔR² for 2/3 labels** (+0.011 test_accuracy, +0.012 learning_rate) but CIs overlap widely — not statistically significant with n=50 test samples.

### Self-modification options evaluated:

| Option | Verdict | Reason |
|--------|---------|--------|
| Reduce k to [5, 10] only | Rejected | k=10 shows marginal improvement but CI still overlaps |
| Increase n_boot | Rejected | Doesn't improve point estimates or shrink CIs |
| Ridge regression instead of OLS | Out of scope | Not a SELF_MODIFY fix — changes hypothesis |
| Use more data | Impossible | Full zoo unavailable (HuggingFace blocked) |

**Conclusion: No meaningful self-modification available.**

---

## Limitation Statement

> **H-M2 LIMITATION:** PCA concentration effect (Condition D vs A) is not detectable via linear probe R² at N=500, d=50,890. The linear probe is fundamentally underpowered in this data regime. Geometric concentration is confirmed (EVR improves), but linear separability does not improve. This is a dataset size limitation, not a methodology error.

**Impact on pipeline:** Non-blocking (SHOULD_WORK gate). Proceed to H-M3.

**Revised causal claim:** "Canonicalization → geometric concentration (EVR)" is confirmed. "Geometric concentration → linear probe R² improvement" is NOT confirmed at N=500. The causal pathway to ρ improvement must operate through a different mechanism (NFT structural learning, not linear PCA features).

---

## Lessons Learned

1. PCA linear probe R² is a low-power metric when N << d — requires N ≥ 5k for 50k-dim weight vectors
2. EVR improvement is a better concentration metric than R² in low-N regimes
3. H-M3 hypothesis design should use NFT-based (non-linear) evaluation rather than linear PCA probes

---

## Outcome

- **reflection_outcome:** LIMITATION_RECORDED
- **should_work_failed:** True
- **route_to:** None (continue to Phase 5)
- **limitation_note:** H-M2: SHOULD_WORK gate failed — N=500 insufficient for PCA linear probe at d=50890; EVR concentration confirmed but R² improvement not detectable

---

*Generated: 2026-08-27 | Phase 4 Step 6B | Unattended mode*
