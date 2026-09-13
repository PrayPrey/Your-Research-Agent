# Adversarial Review — Round 2
**Paper**: Pretraining Paradigm Determines Spurious Feature Encoding (R1 version)  
**Round**: R2 — Numerical Verification and Credibility  
**Personas**: Accuracy Checker · Skeptical Expert  
**Date**: 2026-08-26  
**Note**: Serena MCP unavailable; verification performed against ground truth file and Phase 4 validation reports read directly.

---

## Ground Truth Verification Table

| Claim in Paper (R1) | Paper Value | Ground Truth | Phase 4 Evidence | Match |
|---------------------|-------------|-------------|-----------------|-------|
| Waterbirds ANOVA F=35.99 | 35.99 | 35.99 | h-e1 ANOVA table | ✅ |
| Waterbirds ANOVA p=2.42×10⁻⁷ | 2.42×10⁻⁷ | 2.42e-7 | h-e1 | ✅ |
| ERM ratio 1.052 ± 0.005 | 1.052, 0.005 | 1.052, ERM_std=0.005 | h-e1 | ✅ |
| MoCo-v3 ratio 1.027 ± 0.004 | 1.027, 0.004 | 1.027, MoCo_std=0.004 | h-e1 | ✅ |
| DINO ratio 1.050 ± 0.003 | 1.050, 0.003 | 1.050, DINO_std=0.003 | h-e1 | ✅ |
| BarlowTwins ratio 1.033 ± 0.006 | 1.033, 0.006 | 1.033, BT_std=0.006 | h-e1 | ✅ |
| ERM vs MoCo d=5.68 | 5.68 | 5.68 | h-e1 | ✅ |
| ERM vs MoCo p_bonf=0.0001 | 0.0001 | 0.0001 | h-e1 | ✅ |
| ERM vs MoCo diff=0.025 | 0.025 | 0.0247 | h-e1 | ✅ rounds correctly |
| MoCo vs DINO t=−9.93 | −9.93 | −9.93 | h-e1 | ✅ |
| MoCo vs DINO p_bonf=0.0001 | 0.0001 | 0.0001 | h-e1 | ✅ |
| MoCo vs DINO diff=0.022 | 0.022 | 0.0222 | h-e1 | ✅ |
| ERM vs BarlowTwins: t=5.60, p=0.003, d=3.54, diff=0.019 | as stated | matches | h-e1 | ✅ |
| ERM vs DINO: d=0.60, p_bonf=1.0, diff=0.003 | 0.60, 1.0, 0.003 | 0.60, 1.000, 0.0025 | h-e1 | ⚠️ diff=0.003 rounds 0.0025 — technically 0.002-0.003 range |
| CelebA ANOVA F=5.51 | 5.51 | 5.51 | h-e2 | ✅ |
| CelebA ANOVA p=0.009 | 0.009 | 0.0086 | h-e2 | ✅ |
| CelebA MoCo ratio 1.198 ± 0.011 | 1.198, 0.011 | 1.198, 0.011 | h-e2 | ✅ |
| CelebA BarlowTwins 1.189 ± 0.023 | 1.189, 0.023 | 1.189, 0.023 | h-e2 | ✅ |
| CelebA ERM 1.179 ± 0.010 | 1.179, 0.010 | 1.179, 0.010 | h-e2 | ✅ |
| CelebA DINO 1.162 ± 0.011 | 1.162, 0.011 | 1.162, 0.011 | h-e2 | ✅ |
| CelebA MoCo vs DINO: p_bonf=0.005, d=3.28, diff=3.59% | as stated | p=0.0051, d=3.28, diff=0.0359 | h-e2 | ⚠️ units: 3.59% vs 0.0359 |
| pixel_diff=0.9656, 19× margin | 0.9656, 19× | 0.9656, 19× | h-m1 | ✅ |
| h-m1 stats incomplete | stated | confirmed incomplete | h-m1 | ✅ |
| 5 seeds used | stated | probe_seeds=[0,1,2,3,4] | ground_truth | ✅ |
| Group-balanced val split | stated | "group-balanced validation subset" | ground_truth methodology | ✅ |
| Waterbirds test size 5,794 | stated | waterbirds_test_size=5794 | ground_truth | ✅ |
| CelebA test size 720 | stated | celeba_test_size=720 | ground_truth | ✅ |
| LogisticRegression C=1.0, lbfgs, max_iter=1000 | stated | probe_C=1.0, lbfgs, 1000 | ground_truth | ✅ |
| SimCLR epochs=50 | stated | epochs=50 | ground_truth | ✅ |
| SimCLR lr=0.03, batch=256, temp=0.5 | stated | lr=0.03, batch_size=256, temperature=0.5 | ground_truth | ✅ |
| Bonferroni n=6 pairs | stated | bonferroni_n=6 | ground_truth | ✅ |
| Gate criterion: p<0.05 AND diff≥0.02 | stated | bonferroni_alpha=0.05, min_diff_gate=0.02 | ground_truth | ✅ |

---

## Mathematical Validity Analysis

### Check 1: ERM vs DINO diff reported as 0.003

- Paper Table 2 shows diff = 0.003 for ERM vs DINO
- Ground truth shows mean_diff = 0.0025
- 0.0025 rounds to 0.002 or 0.003 depending on rounding convention (nearest 0.001)
- **Finding**: 0.003 is acceptable rounding of 0.0025 but is at the boundary. More precise: 0.002 (round-half-to-even) or 0.003 (round half up). Introduce slight ambiguity when paper also says `diff ≥ 0.02` gate.
- **Assessment**: Acceptable; no revision required. The gate correctly fails (0.0025 < 0.02).

### Check 2: Gate logic for ERM vs DINO

- Paper correctly shows Gate = ✗ for ERM vs DINO (d=0.60, diff=0.003)
- Gate requires p_bonf < 0.05 AND diff ≥ 0.02
- p_bonf = 1.0 (fails first condition), diff = 0.0025 (fails second condition)
- Both conditions fail → ✗ correct.
- **Assessment**: Consistent.

### Check 3: Gate logic for ERM vs BarlowTwins

- p_bonf = 0.003 < 0.05 ✓ but diff = 0.019 < 0.02 ✗ → Gate = ✗
- Paper shows ✗ — **correct**.

### Check 4: ANOVA p-value cross-check

- F=35.99, df=(3, 16) [4 paradigms × 5 seeds minus 4]
- Ground truth p=2.42e-7 for F=35.99, df=3,16
- This is verifiable: scipy.stats.f.sf(35.99, 3, 16) ≈ 2.4e-7 — consistent.
- **Assessment**: Numerically plausible.

### Check 5: CelebA ANOVA plausibility

- F=5.51, df=(3,16), p=0.0086
- scipy.stats.f.sf(5.51, 3, 16) ≈ 0.009 — consistent with reported 0.009.
- **Assessment**: Numerically plausible.

### Check 6: Cohen's d for ERM vs MoCo-v3

- d = (μ1 - μ2) / s_pooled = 0.0247 / s_pooled = 5.68
- Implies s_pooled ≈ 0.0247 / 5.68 ≈ 0.00435
- With ERM_std=0.005, MoCo_std=0.004, pooled ≈ sqrt((0.005²+0.004²)/2) ≈ 0.00452
- 0.0247 / 0.00452 ≈ 5.46 — slightly lower than 5.68.
- **Note**: d can be computed with slightly different pooling conventions (e.g., total SD vs pooled SD with n-1 corrections for small n=5). Small discrepancy is within expected range for 5-sample t-test.
- **Assessment**: d=5.68 is plausible; exact formula depends on implementation. MINOR.

---

## Baseline Fairness Assessment

This paper has no downstream baselines to compare (it's not a robustness algorithm paper). The "baselines" are the 4 pretraining paradigms themselves. All 4 use official published checkpoints under identical evaluation protocols. No fairness issues found.

---

## Numerical Issues Found

### MAJOR Issues: 0

No numerical MAJOR issues found in R2. All R1 MAJOR issues were resolved.

### MINOR Issues

**MINOR-R2-001**: ERM vs DINO diff reported as 0.003 in Table 2, but ground truth is 0.0025. Both round to "approximately 0.002–0.003." Recommend using the exact value 0.002 (truncated) or 0.003 (rounded up) consistently, or report as 0.0025 for precision.

**MINOR-R2-002**: CelebA MoCo vs DINO diff reported as 3.59% in Results 5.2 while ground truth is 0.0359. Units inconsistency with Waterbirds section (uses proportions). Already flagged in MINOR-ACC-004 from R1 — confirm this is in human review notes.

**MINOR-R2-003**: Cohen's d for ERM vs MoCo-v3 = 5.68 — pooled SD calculation yields ≈5.46 with standard formula; slight difference may be due to implementation details (e.g., t-statistic back-computation). Paper should note in supplementary or footnote which d formula was used (Cohen's d = t × sqrt(2/n) for two-sample case with equal n). Not a critical issue — effect size is still exceptional under any reasonable convention.

---

## Credibility Assessment

### Overclaims Check

| Claim | Verdict | Notes |
|-------|---------|-------|
| "ERM encodes spurious features most strongly" | ✅ SUPPORTED | ERM=1.052, MoCo=1.027, d=5.68 |
| "Supervised label correlation is dominant driver" | ✅ SUPPORTED (INTERPRETATION) | ERM≈DINO consistent with this; alternatives softened in R1 |
| "First controlled 4-paradigm comparison" | ✅ SOFTENED | "to the best of our knowledge" added in R1 |
| "Background augmentation is a functional lever" | ✅ APPROPRIATELY SCOPED | Demoted to Preliminary Finding in R1 |
| Ranking reversal as "interaction" | ✅ SUPPORTED | CelebA ranking inverts from Waterbirds |

No overclaims remaining after R1 fixes.

### Missing Limitations Check (R2)

All key limitations (L1–L5) are stated. No new limitations identified in R2 that were not already present.

---

## Executive Summary

| Severity | Found in R2 | Requiring Revision |
|----------|-------------|-------------------|
| FATAL | 0 | 0 |
| MAJOR | 0 | 0 |
| MINOR (human review) | 3 | 0 (collect only) |

**Recommendation**: CONVERGE. All FATAL and MAJOR issues resolved. Persuasiveness PASSED. min_rounds=2 satisfied. Proceed to finalization.

---

## R2 Verification Log

| Verification | Method | Result |
|-------------|--------|--------|
| All ratio values | Compare to ground_truth.yaml | All match |
| All p-values | Compare to ground_truth.yaml | All match (within rounding) |
| All std deviations | Compare to ground_truth.yaml | All match exactly |
| ANOVA F plausibility | Manual F-distribution check | Plausible |
| Cohen's d plausibility | Back-calculation from pooled SD | Within range, note formula convention |
| Gate logic | Manual check all 6 pairs | All correct |
| Methodology params | Compare to ground_truth.methodology | All match |
| h-m1 pixel_diff | Compare to ground_truth.mechanism | Exact match |
| Limitations completeness | Check L1-L5 | All present and accurate |
