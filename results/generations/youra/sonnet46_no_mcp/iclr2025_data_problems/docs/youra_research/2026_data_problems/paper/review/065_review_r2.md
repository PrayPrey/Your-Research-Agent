# Round 2 Adversarial Review: Numerical Verification and Credibility

**Round:** R2  
**Focus:** Numerical Verification, Mathematical Validity, Baseline Fairness, R1 Fix Confirmation  
**Date:** 2026-05-04  
**Reviewer:** Adversary Agent (R2)  
**Paper:** 06_paper_r1.md — "A Cross-Corpus Contamination Atlas"

---

## Executive Summary

| Category | Count |
|----------|-------|
| FATAL issues | 0 |
| MAJOR issues | 2 |
| MINOR issues | 4 |
| R1 fixes verified | True (all 5 fixes confirmed) |
| Numerical checks performed | 12 |

**Recommendation:** CONDITIONAL_ACCEPT — Two MAJOR issues require targeted fixes before submission. No fatal mathematical errors found. R1 revisions were applied correctly and consistently.

---

## Numerical Verification Table

| Check | Claim in Paper | Ground Truth | Result |
|-------|----------------|--------------|--------|
| 1A: 43x ratio | "43× the rate" | 17.3/0.4 = 43.25x | PASS (correct) |
| 1A: 40x in Abstract | "40× contamination differentials" | Max diff is 43.25x | MINOR (see below) |
| 1B: 38% C4 reduction | (6.53−4.05)/6.53 = 37.98% | Rounds to 38% | PASS |
| 1B: Mixed-source comparison | Pile=WIMBD published; C4=10% sample | Not same measurement basis | MAJOR |
| 1C: KW H=22.08 group balance | 6 groups, n=57 vs n=2 | Extreme imbalance not noted | MAJOR |
| 1D: Pile-RP equivalence language | "statistically indistinguishable" | p=0.810 = fail to reject null | PASS (correct phrasing) |
| 1E: Scaling factor direction | C4 ×0.62 scales UP more than RP ×0.88 | C4 is still lowest after scaling | PASS (consistent) |
| 1F: Format sensitivity scope | ρ=0.74 (h-e1 only) | Only computed for Pile | MINOR (overclaim risk) |
| KW H=590.82 | Exact | Verified ✓ | PASS |
| KW p=2.73e-89 | Exact | Verified ✓ | PASS |
| Max pair diff 16.9pp | 17.3−0.4=16.9pp | Verified ✓ | PASS |
| Sensitivity rho 0.7375 | Paper says 0.74 | Rounds correctly ✓ | PASS |
| h-m1 KW H=17.506 | Paper says 17.51 | Rounds correctly ✓ | PASS |
| h-m1 KW p=1.5794e-4 | Paper says 1.58e-4 | Rounds correctly ✓ | PASS |
| Dunn C4 vs RP p=0.00973 | Paper says 0.0097 | Rounds correctly ✓ | PASS |
| h-m2 KW H=22.079 | Paper says 22.08 | Rounds correctly ✓ | PASS |
| Cohen's d=0.853 | Paper says 0.85 | Rounds correctly ✓ | PASS |
| 1.860 ratio | Paper says "~1.9x" | 6.64/3.57=1.860; R1 fix applied ✓ | PASS |

---

## Mathematical Validity Analysis

### Check 1A: 40x vs 43x Consistency

The paper correctly states "professional medicine questions appear in The Pile v1 at 43 times the rate" in the Introduction and Result sections. The actual ratio is 17.3%/0.4% = 43.25x — "43x" is accurate.

However, both the Abstract and Conclusion use "40× contamination differentials." This creates a numerical inconsistency within the same paper: Section 5.1 says the finding is 40× (the sub-task variance RQ1 finding), yet Section 1 and Table 1 anchor on 43×. The 40× framing may be intended as a rounded figure from Figure 2's visual impression (top-10 range), but the actual measured differential is 43x. Using 40x in the Abstract while anchoring on 43x elsewhere is internally inconsistent. Readers will notice the discrepancy.

**Verdict: MINOR** — 40x is not wrong (it is a conservative rounded figure), but the internal inconsistency between 40x (Abstract/Conclusion) and 43x (Introduction/Results) undermines numerical precision. Should be harmonized to "43x" or "more than 40x" throughout.

### Check 1B: Mixed-Source Comparison Validity (38% reduction)

The 38% claim computes: (6.53 − 4.05) / 6.53 = 37.98% ≈ 38%. The arithmetic is correct.

However, the two values being compared come from fundamentally different measurement sources:
- Pile rate (6.53%): WIMBD published rates — NOT independently measured by this pipeline.
- C4 rate (4.05%): 10% streaming sample with ×0.62 scaling — independently measured.

This is not a like-for-like comparison. The Pile rate is a published external benchmark; the C4 rate is an independent measurement with propagated uncertainty. The paper does disclose the scaling uncertainty (±4–8 pp) in Section 3.3 and Limitation L2. But nowhere does the paper explicitly state that the 38% reduction compares a WIMBD-published figure (Pile) against an independently computed figure (C4), which is a methodological asymmetry beyond just scaling uncertainty.

The issue: if the Pile rate had been independently measured by this pipeline using the same 10% sampling + scaling approach (rather than using WIMBD published rates), the Pile figure might differ. The cross-source comparison introduces an unmeasured source of bias.

**Verdict: MAJOR** — The paper must add a sentence in Section 5.2 or Limitation L1/L2 explicitly acknowledging that the 38% reduction compares a WIMBD-published Pile rate against a pipeline-computed C4 rate, and that this cross-source comparison limits the precision of the absolute reduction figure beyond the already-noted scaling uncertainty.

### Check 1C: KW Interaction with Extreme Group Size Imbalance (H=22.08)

The interaction KW test uses 6 groups: academic (n=57) × 3 corpora + commonsense (n=2) × 3 corpora. The academic groups have n=57 each; the commonsense groups have n=2 each.

This extreme imbalance (57:2 ratio) means the KW statistic is dominated by the within-academic-group variance across corpora. The H=22.08, p=0.0005 result primarily reflects that MMLU sub-tasks have heterogeneous rates across corpora — which h-m1 already established. The new information from the 6-group interaction test is limited by the n=2 commonsense groups having essentially no within-group variance to contribute meaningfully to the test statistic.

The paper correctly notes the n=2 limitation for Mann-Whitney but does NOT note the same issue for the KW interaction test. A reader might interpret H=22.08, p=0.0005 as strong evidence of the domain × corpus interaction, when the test may be primarily powered by the 57-cell academic variation rather than the 2-cell commonsense groups.

**Verdict: MAJOR** — The paper should add a qualification to the KW interaction result noting that with n=2 commonsense groups, the interaction test is heavily weighted toward the academic-side variance and should be interpreted accordingly. The KW interaction result p=0.0005 confirms group differences exist but cannot cleanly separate domain vs corpus main effects when group sizes are this imbalanced.

### Check 1D: Pile-RedPajama Equivalence Language

The paper consistently uses "statistically indistinguishable" (not "equivalent" or "same") when describing the Pile-RP p=0.810 result. Section 6.1 correctly frames this as a structural finding grounded in shared CommonCrawl ancestry rather than claiming statistical proof of equivalence. The language "fail to reject null" is implied correctly throughout. No overclaim detected.

**Verdict: PASS** — Phrasing is appropriately conservative. No changes needed.

### Check 1E: Scaling Factor Internal Consistency

The scaling factors (C4 ×0.62; RP ×0.88) mean that for the same raw 10% sample rate X:
- C4 full-corpus estimate = X / 0.62 ≈ 1.613X
- RP full-corpus estimate = X / 0.88 ≈ 1.136X

This means C4's raw rates are scaled up more aggressively than RP's. Despite this upward scaling, C4 remains the lowest contamination corpus (4.05% vs RP 5.75%). This actually strengthens the conclusion: C4 is lowest even after aggressive upward scaling. The directional ordering is therefore conservative with respect to C4. This is consistent with the paper's claim.

**Verdict: PASS** — The scaling directional effect actually reinforces the C4 finding. No issue.

### Check 1F: Format Sensitivity Scope

Section 3.5 states: "Text format sensitivity: ρ=0.74 (question+choices vs question-only). Sampling sensitivity: ρ>0.995 across independent 10% samples. Both confirm rank-based conclusions are methodologically robust."

The Contribution 4 in the Introduction states: "Demonstration that rank-based contamination analysis is robust to text format variations (ρ=0.74) and corpus sampling fractions (ρ>0.995)."

The ground truth specifies that format sensitivity ρ=0.7375 was computed for h-e1 (The Pile) only. The sampling sensitivity ρ>0.995 was computed for all three corpora. However, the paper does not clarify that format sensitivity was only computed for The Pile. A reader could reasonably infer that ρ=0.74 applies to all three corpora (since "methodologically robust" is a general claim), creating a potential overclaim.

**Verdict: MINOR** — Add a parenthetical "(computed for The Pile; assumed portable to C4/RedPajama given consistent MinHash methodology)" or restrict the claim to "for The Pile analysis."

---

## Baseline Fairness Assessment

**WIMBD validation comparison:** The paper correctly reports all five checked sub-tasks within ±5pp:
- professional_medicine: 17.3% vs WIMBD 12.5% → 4.8pp (within ±5pp) ✓
- professional_law: 13.2% vs WIMBD 13.5% → 0.3pp ✓
- abstract_algebra: 1.0% vs WIMBD 2.0% → 1.0pp ✓
- formal_logic: 1.6% vs WIMBD 1.5% → 0.1pp ✓
- global_facts: 13.0% vs WIMBD 13.0% → exact ✓

**±5pp tolerance justification:** The paper states "within ±5pp" but does not explicitly justify why ±5pp is the chosen threshold. The professional_medicine discrepancy at 4.8pp is the tightest pass — any slightly different threshold (e.g., ±4pp) would cause a failure. The paper should briefly note why ±5pp is an appropriate tolerance (e.g., consistent with the ±4–8pp scaling uncertainty described in L2, or matching WIMBD's own reported methodology tolerances).

**Citation verifiability for scaling factors:** The paper cites Dodge et al. (2021) for C4 ×0.62 and TogetherComputer (2023) for RP ×0.88. These are plausible sources (Dodge et al. documents C4 properties; TogetherComputer documents RP construction). However, the specific scaling factor values (0.62, 0.88) are not obviously derivable from the abstract content of these papers — they appear to be literature-calibrated estimates rather than directly cited figures. The paper uses the phrase "literature-calibrated" which appropriately hedges this. No fabrication concern, but the basis for these specific numerical values should ideally be clarified (e.g., "estimated from token-level document retention rates reported in...").

**WIMBD Spearman ρ claim:** The paper reports ρ=0.721 for WIMBD consistency (h-m1 result) and ρ=0.74 in Section 5.1 (h-e1 WIMBD validation). These are different correlations — one is cross-corpus methodology validation (ρ=0.721), the other is format sensitivity (ρ=0.74). The distinction is clear in context, but these numbers appearing close together could cause confusion. No error, but worth noting for clarity.

---

## R1 Fix Verification

All five R1 fixes were systematically verified:

**M1: "2-3x" → "approximately 1.9x"** — VERIFIED. The paper consistently says "approximately 1.9×" in Abstract, Contribution 3, Section 5.3, and Conclusion. The computed ratio is 6.64/3.57 = 1.860, which rounds to ~1.9x. Section 5.3 also explicitly states "approximately 1.86x" for the Pile column. No residual "2-3x" language found.

**M2: h-m2 gate failure qualifier** — VERIFIED. Abstract contains "supported by an interaction test (H=22.08, p=0.0005) but not confirmed by a pre-registered directional test due to insufficient category granularity (n=2 commonsense sub-tasks)." Contribution 3 contains identical qualifier. Section 5.3 and Conclusion both repeat the exploratory caveat. Consistent and thorough.

**M3: Novelty differentiated from WIMBD** — VERIFIED. Section 2.4 explicitly states what WIMBD does vs what this paper does. Contribution 1 clearly delineates the WIMBD limitation (The Pile only, individual datasets in isolation) vs this paper's contribution (59 sub-tasks × 3 corpora unified matrix). No overclaim of novelty beyond what is substantiated.

**M4: Causal language softened** — VERIFIED. Throughout the paper, "is associated with" replaces causal framing. Searched for "determines," "causes," "not scale" — none found. Section 3 says "corpus source composition — not merely corpus scale — should predict" (hypothetical framing, acceptable). The key insight box says "is associated with." Consistent.

**M5: 38% uncertainty caveat** — VERIFIED. Every instance of the 38% claim includes the qualifier "assuming literature-calibrated scaling factors; directional ordering robust to ρ>0.995 sensitivity analysis." This qualifier appears in: Abstract, Contribution 2, Section 5.2, and Conclusion. Four consistent appearances.

**R1 Fix Verdict: ALL 5 FIXES CORRECTLY AND CONSISTENTLY APPLIED.**

---

## Remaining Limitations Check

**L-R1: Format sensitivity scope (ρ=0.74 computed only for The Pile)**
The paper does not disclose that format sensitivity was only tested for The Pile. Contribution 4 implies general robustness. This is a missing limitation. **MINOR** (noted above under Check 1F).

**L-R2: MMLU-heavy analysis structure**
The 59-sub-task analysis includes HellaSwag (1 entry) and BBH (1 aggregate entry) as single data points, making it an effectively 57-MMLU-dominated analysis. Section 3.2 correctly notes this (57 MMLU + 1 HellaSwag + 1 BBH aggregate), and Limitation L3 notes the n=2 commonsense consequence. The paper is adequately transparent about this structure. **PASS — adequately disclosed.**

**L-R3: Temporal aspects (Pile v1 from 2021)**
The paper does not discuss that The Pile v1 was assembled in 2021, and some benchmark test sets (HellaSwag: 2019, MMLU: 2021, BBH: 2022) may have been created after Pile assembly. This temporal ordering is relevant: if benchmark test sets were created after training data assembly, the contamination pathway is plausible. If the opposite, it is less concerning. A brief note on temporal ordering would strengthen credibility. **MINOR** — not a fatal flaw but a standard limitation for contamination work.

**L-R4: Model-level vs corpus-level contamination**
The paper does not address whether models actually train on the full corpus or a filtered version, meaning corpus-level contamination rates may overstate model-level contamination. This is an important caveat for the "practitioners choosing training corpora" claim in the Abstract. Not unique to this paper (it is a limitation of all corpus-level contamination studies), but should be acknowledged. **MINOR** — standard limitation in the field, brief acknowledgment would be appropriate.

**L-R5: KW interaction test power imbalance (n=57 vs n=2)**
Not disclosed. **MAJOR** (noted above under Check 1C).

**L-R6: Cross-source comparison for 38% reduction**
Not explicitly disclosed as a distinct issue from scaling uncertainty. **MAJOR** (noted above under Check 1B).

---

## FATAL Issues

**None.** All numerical claims are mathematically verified. All major statistics are correctly reported from ground truth. No fabricated data found.

---

## MAJOR Issues

### MAJOR-1: Cross-Source Measurement Asymmetry in 38% Reduction Claim

**Location:** Section 5.2, Section 3.3, Limitation L2  
**Issue:** The 38% C4 reduction compares a WIMBD-published Pile rate (6.53%, external source) against a pipeline-computed C4 rate (4.05%, 10% sample + ×0.62 scaling). This is not disclosed as a distinct methodological limitation beyond the scaling uncertainty. The cross-source nature means the Pile baseline itself may carry unknown uncertainty from WIMBD's methodology (different MinHash parameters, document coverage, etc.) that the paper does not address.  
**Fix:** Add one sentence to Limitation L1 or L2: "Additionally, the 38% reduction figure compares a WIMBD-published Pile rate against a pipeline-computed C4 rate; cross-source comparison introduces methodological asymmetry beyond the stated scaling uncertainty, and the figure should be treated as directionally indicative rather than precisely calibrated."  
**Severity:** MAJOR — central quantitative claim requires explicit methodological qualification.

### MAJOR-2: KW Interaction Test Power Imbalance Not Disclosed

**Location:** Section 5.3, Abstract, Contribution 3  
**Issue:** The KW interaction test (H=22.08, p=0.0005) uses 6 groups with n=57 (academic) vs n=2 (commonsense) per corpus. This extreme imbalance means the test is dominated by academic-side variance and does not cleanly test the domain × corpus interaction. The paper acknowledges n=2 limits Mann-Whitney but does not apply the same caveat to the KW interaction test — creating an inconsistency where the KW interaction is cited more strongly than warranted.  
**Fix:** Add a parenthetical to the KW interaction result in Section 5.3: "(noting that with n=2 commonsense groups, this test is predominantly powered by academic sub-task variance across corpora; the interaction interpretation is exploratory)." Apply same caveat in Abstract and Contribution 3 where the KW interaction is cited.  
**Severity:** MAJOR — the KW interaction result is cited in Abstract and contributions as key supporting evidence; the power imbalance caveat is essential for accurate interpretation.

---

## MINOR Issues → human_review_notes

### MINOR-1: Internal 40x/43x Inconsistency

Abstract and Conclusion: "40× contamination differentials"  
Introduction, Results, Figures: "43×"  
The actual differential is 43.25x. "40x" appears to be a rounded conservative figure used in summary contexts. While not factually wrong, the inconsistency may confuse reviewers. **Suggested fix:** Replace "40×" with "43×" in Abstract and Conclusion, or use "more than 40×" consistently and note "specifically 43× for the professional_medicine/high_school_mathematics pair."

### MINOR-2: Format Sensitivity Scope Not Disclosed

ρ=0.74 format sensitivity was computed only for The Pile (h-e1). Contribution 4 and Section 3.5 imply general robustness without restricting to The Pile. **Suggested fix:** Add "(computed for The Pile)" to the ρ=0.74 citation in Contribution 4 and Section 3.5.

### MINOR-3: ±5pp WIMBD Tolerance Not Justified

The ±5pp threshold for WIMBD validation is not explicitly justified. With professional_medicine at 4.8pp — the closest pass — the threshold choice affects whether validation is declared successful. **Suggested fix:** Add one sentence: "We adopt ±5pp as the validation tolerance, consistent with the ±4–8pp scaling uncertainty estimated for the C4/RP measurements."

### MINOR-4: Temporal Limitation Not Discussed

Corpus and benchmark temporal ordering (Pile v1: 2021; MMLU: 2021; BBH: 2022) not mentioned. **Suggested fix:** Add "L5: Temporal ordering" to Limitations section: "The Pile v1 was assembled in 2020–2021. Some benchmark test sets (BBH: 2022) post-date Pile assembly, limiting contamination pathways for those sub-tasks. Future work should account for temporal ordering in contamination attribution."

---

## Summary for Revision Agent

**R2 Review Status:** CONDITIONAL_ACCEPT pending 2 MAJOR fixes and 4 MINOR improvements.

**Priority fixes required:**

1. **Section 5.2 / Limitation L1 or L2 (MAJOR-1):** Add explicit disclosure that the 38% reduction compares WIMBD-published Pile rates against pipeline-computed C4 rates (cross-source methodological asymmetry, beyond already-noted scaling uncertainty).

2. **Section 5.3, Abstract, Contribution 3 (MAJOR-2):** Add caveat that KW interaction H=22.08 is predominantly powered by the n=57 academic groups (not the n=2 commonsense groups), limiting the interaction interpretation.

**Secondary improvements (MINOR):**

3. Harmonize 40x → 43x (or "more than 40x") in Abstract and Conclusion.
4. Restrict ρ=0.74 format sensitivity claim to "for The Pile" in Contribution 4 and Section 3.5.
5. Justify ±5pp WIMBD validation tolerance (1 sentence in Section 5.1).
6. Add L5 temporal limitation (1 sentence in Section 6.2).

**What is working well:**
- All 5 R1 fixes correctly applied and consistent throughout
- All key statistics accurately reported with appropriate rounding
- Scaling uncertainty caveat for 38% is thorough and appears 4 times
- h-m2 gate failure qualifier appears consistently in all expected locations
- "~1.9x" replaces "2-3x" correctly with supporting arithmetic
- WIMBD comparison figures all verified correct
- "Statistically indistinguishable" correctly used for Pile-RP p=0.810
- No causal overclaims found; "associated with" framing consistent
- Limitations section is substantive and honest

---

*R2 Review completed: 2026-05-04 | Adversary Agent | 12 numerical checks performed*
