# Adversarial Review — Round 2
**Paper:** Deduplication Produces a Contamination-Correction Benchmark Accuracy Signature
**Date:** 2026-08-25
**Round:** R2 — Numerical Verification and Credibility
**Personas:** Accuracy Checker, Skeptical Expert
**Input:** 06_paper_r1.md (post-R1 revision)

---

## Numerical Verification Log

### Search 1: Primary Correlation (H-M3)

**Paper claims:** r=0.632, p=0.0086, Spearman ρ=0.618, p=0.0107, Bootstrap CI [0.297, 0.858]

**Source verification (h-m3/04_validation.md):**
- Pearson r: 0.6323 ✅ (paper rounds to 0.632)
- Pearson p: 0.0086 ✅ (exact match)
- Spearman ρ: 0.6185 ✅ (paper rounds to 0.618)
- Spearman p: 0.0107 ✅ (exact match)
- Bootstrap CI: [0.2970, 0.8581] ✅ (paper rounds to [0.297, 0.858])
- n observations: 16 ✅

**Verdict: VERIFIED ✅**

### Search 2: MMLU t-test (H-E1)

**Paper claims:** t=-5.574, p=0.0114, mean Δ=-0.0071, Bonferroni significant

**Source verification (h-e1/04_validation.md):**
- t=-5.574 ✅ (exact match)
- p=0.0114 ✅ (exact match)
- mean Δ=-0.0071 ✅ (exact match)
- Bonferroni corrected α=0.0125 ✅

**Verdict: VERIFIED ✅**

### Search 3: HellaSwag, ARC-Challenge, WinoGrande results (H-E1)

**Paper claims (Table 1):**
- HellaSwag: t=+3.283, p=0.0463, Δ=+0.0159
- ARC-Challenge: t=+5.362, p=0.0127, Δ=+0.0122
- WinoGrande: t=+0.038, p=0.9722, Δ=+0.0002

**Source verification (h-e1/04_validation.md):**
- HellaSwag: t=3.283, p=0.0463, mean Δ=+0.0159 ✅
- ARC-Challenge: t=5.362, p=0.0127, mean Δ=+0.0122 ✅
- WinoGrande: t=0.038, p=0.9722, mean Δ=+0.0002 ✅

**Verdict: VERIFIED ✅**

### Search 4: Token-Count Matching (H-M4)

**Paper claims:** r_token=0.632, r_step=0.539, Δr=+0.093, bias_delta=-0.004, Pile step 99K, <0.30% mismatch

**Source verification (h-m4/04_validation.md):**
- r_token=0.6323 ✅ (rounds to 0.632)
- r_step=0.5393 ✅ (rounds to 0.539)
- Δr=+0.0930 ✅ (rounds to +0.093)
- bias_delta=-0.00418 ✅ (paper says "-0.004", acceptable rounding)

**Pile step reconciliation (VERIFIED CONSISTENT):**
- h-e1/04_validation.md: Pile step 99,000 used for primary analysis ✅
- h-m4/04_validation.md: Pile step 128,000 used for H-M4's step-matched simulation
- The two use different checkpoints for different purposes; R1 footnote clarifies this ✅
- Paper's claim of Pile step 99K with <0.30% mismatch matches h-e1 verification table ✅

**Verdict: VERIFIED ✅ (after R1 footnote clarification)**

### Search 5: Per-model-size correlations

**Paper claims (Section 5.2):** 160M r=0.631, 410M r=0.799, 1B r=0.539, 6.9B r=0.856

**Source verification (h-m3/04_validation.md, Ablation 4):**
- 160m: 0.6307 ✅ (rounds to 0.631)
- 410m: 0.7988 ✅ (rounds to 0.799)
- 1b: 0.5391 ✅ (rounds to 0.539)
- 6.9b: 0.8562 ✅ (rounds to 0.856)

**Note:** h-m3/04_validation.md reports per-size p-values: 160m p=0.3693, 410m p=0.2012, 1b p=0.4609, 6.9b p=0.1438 — all non-significant at n=4. Paper correctly shows these without individual p-values. ✅

**Verdict: VERIFIED ✅**

### Search 6: H-M2 Direction Reversal

**Paper claims (Section 5.5):**
- MMLU: -0.104 (dedup higher)
- HellaSwag: -0.092 (dedup higher)
- ARC-Challenge: -0.077 (dedup higher)
- WinoGrande: -0.160 (dedup higher)
- Dual estimator: 13-gram r=+0.632 vs min-k% r=-0.713

**Source verification (h-m2/04_validation.md):**
- MMLU min-k% delta: -0.104 ✅
- HellaSwag: -0.092 ✅
- ARC-Challenge: -0.077 ✅
- WinoGrande: -0.160 ✅
- min-k% r=-0.7125 (h-m3 ablation) ✅ (paper rounds to -0.713)
- n_tests=22, 0 significant in expected direction ✅

**Verdict: VERIFIED ✅**

### Search 7: H-M1 Dry-Run Results

**Paper claims:** 2/4 benchmarks significant p<0.0125, Spearman ρ=1.0, n=200

**Source verification (h-m1/04_validation.md):**
- n_removed=200, n_retained=200 ✅
- n_significant=2/4 ✅
- gate_pass=TRUE ✅
- Spearman ρ=1.0 ✅

**Verdict: VERIFIED ✅**

### Search 8: Contamination Estimates

**Paper claims:**
- MMLU: 5.5%
- HellaSwag: 20.0%
- ARC-Challenge: 8.5%
- WinoGrande: 2.5%

**Source verification (h-m3/04_validation.md, Contamination Estimates):**
- mmlu: 0.0550 (5.5%) ✅
- hellaswag: 0.2000 (20.0%) ✅
- arc_challenge: 0.0850 (8.5%) ✅
- winogrande: 0.0250 (2.5%) ✅

**Verdict: VERIFIED ✅**

### Search 9: 13-gram r vs min-k% r disagreement claim

**Paper claims:** "13-gram r=+0.632 vs min-k% r=-0.713"

**Source verification (h-m3/04_validation.md, Ablation 1):**
| Estimator | Pearson r | p-value |
| 13-gram overlap | 0.6323 | 0.0086 |
| min-k% differential | -0.7125 | 0.0020 |

Paper rounds correctly: +0.632 and -0.713 ✅

**Verdict: VERIFIED ✅**

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth | Serena/Source | Match |
|-------|-----------|--------------|---------------|-------|
| Pearson r=0.632 | 0.632 | 0.6323 (h-m3) | h-m3/04_validation.md | ✅ |
| p=0.0086 | 0.0086 | 0.0086 | h-m3 | ✅ |
| CI [0.297, 0.858] | [0.297, 0.858] | [0.2970, 0.8581] | h-m3 | ✅ |
| MMLU t=-5.574 | -5.574 | -5.574 | h-e1 | ✅ |
| Δr=+0.093 | +0.093 | +0.0930 | h-m4 | ✅ |
| Pile step 99K | 99,000 | 99,000 (h-e1) | h-e1 | ✅ |
| <0.30% mismatch | <0.30% | 0.30% | h-e1 | ✅ |
| bias_delta=-0.004 | -0.004 | -0.00418 | h-m4 | ✅ |
| min-k% r=-0.713 | -0.713 | -0.7125 | h-m3 ablation | ✅ |
| n=4 non-sig p=0.224 | p=0.224 | 0.2239 (h-m3 ablation 2) | h-m3 | ✅ |
| r_bench=0.776 | 0.776 | 0.7761 | h-m3 ablation 2 | ✅ |
| 13-gram sources correct | stated | Lee+GPT-4 TR | literature | ✅ |

---

## Mathematical Validity Analysis

### Check 1: n=16 statistical justification
Paper uses n=16 (4 benchmarks × 4 model sizes). Each benchmark contributes 4 data points (one per model size). The assumption of independence across model sizes is partially defensible: per-size correlations all exceed r=0.5 (Table, Section 5.2), suggesting the contamination signal is consistent across scale, not an artifact of one model size. The n=4 non-significance (p=0.224) is now properly disclosed in R1. **No mathematical invalidity — disclosed appropriately.**

### Check 2: Δr=+0.093 plausibility
r_token=0.632, r_step=0.539, Δr=0.093. Calculation: 0.632-0.539=0.093 ✅. Relative: 0.093/0.539=17.3% ✅. Both reported correctly.

### Check 3: Bonferroni threshold
α=0.05/4=0.0125. Applied to H-E1. MMLU p=0.0114 < 0.0125 ✅ (significant). ARC p=0.0127 > 0.0125 (correctly labeled "Near-sig.") ✅.

### Check 4: 207B token claim
dedup-Pile step 143,000 ≈ 207B tokens. Pile step 99,000 ≈ 207B tokens. Mismatch <0.30%. Confirmed by h-e1 checkpoint map. ✅

### Check 5: Bootstrap CI consistency
CI [0.297, 0.858] spans r=0.632 and excludes zero. Asymmetric around r=0.632 (lower width: 0.335, upper width: 0.226) — expected for r-to-z Fisher transformation bootstrap, slightly right-skewed. ✅

---

## Baseline Fairness Assessment

The paper compares token-count-matched vs step-matched results from the same Pythia model family. There is no external baseline comparison in the traditional sense. The comparison is internal:
- Token-count matching (our method) vs step-matching (prior practice)
- r=0.632 vs r=0.539

This is fair: both conditions use the same data; the difference is purely checkpoint selection. No unfair baseline manipulation detected.

The paper does not claim superiority over other contamination detection methods — it proposes a new framework. The only informal comparison is to Biderman et al. 2023 (who used step-matching without contamination-accuracy correlation analysis). This comparison is fair and accurately described.

**Verdict: Baseline comparison is fair ✅**

---

## Executive Summary — Round 2

| Severity | Found | Action |
|----------|-------|--------|
| FATAL | 0 | None |
| MAJOR | 0 | None (all R1 MAJORs resolved) |
| NEW MINOR | 1 | Per-size p-values not reported |

### New Minor Issue (R2):

**R2-MINOR-001: Per-model-size correlations lack p-values**
- Section 5.2 reports per-size r values but not p-values.
- At n=4 per size, all per-size correlations are non-significant (p ranges 0.14–0.46 per h-m3 ablation 4).
- Not reporting them is technically defensible (they're shown as "ablation," not primary results), but a skeptical reviewer may ask.
- **Recommendation for human review**: Add parenthetical "all non-significant at n=4" to the per-model-size table caption, or add to Limitations L3.

---

## R2 Verdict

**CONVERGE** — FATAL=0, MAJOR=0, persuasiveness PASSED, round 2 complete.

All primary claims verified against Phase 4 validation files. No numerical discrepancies found in the R1-revised paper. One new MINOR issue collected for human review.
