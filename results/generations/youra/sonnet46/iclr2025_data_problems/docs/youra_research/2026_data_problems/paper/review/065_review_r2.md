# Adversarial Review - Round 2

**Paper:** Quality Filters as Demographic Reweighting: Auditable Corpus-Level Fairness Signals in Pretraining Data Curation
**Reviewed:** 2026-03-15T14:30:00
**Round:** R2 - Verification and Credibility
**Reviewer Version:** Adversary Agent v2.0
**Previous Round:** R1 (1 FATAL + 6 MAJOR → all fixed per revision notes in 06_paper_r1.md)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 2 | CONCERNS — p-value unit mismatch persists; configuration count inconsistency |
| Credibility | 0 | 1 | CONCERN — WinoBias limitations undisclosed; DoReMi comparison framing marginal |
| **TOTAL** | **0** | **3** | **CONDITIONAL PASS — fixes required before submission** |

**Recommendation:** Conditional Accept pending three MAJOR fixes. The paper's core findings are solid and the R1 revisions landed correctly. No FATAL issues found in R2. Three MAJOR issues remain that carry meaningful reviewer-rejection risk: (1) a statistical unit-of-analysis ambiguity in the p-value reporting that was flagged in R1 but not fully resolved, (2) a configuration count inconsistency (abstract says "seven corpus configurations" but 8 are listed), and (3) missing disclosure of WinoBias demographic lexicon limitations.

---

## R1 Fix Verification

Did R1 fixes land correctly?

- [x] **Table 2 entropy values corrected** — All seven values in the R1 paper exactly match ground truth (C0=3.3159, C1=3.2702, C2=3.1847, C3=3.0621, C4=2.8934, C5=2.5374, C6=3.0541). VERIFIED.
- [x] **H-M2 proxy training disclosed** — Section 3.6 and 4.2 both explicitly state "proxy model — a compact 512-hidden-dimension decoder trained with hf_trainer_fallback as an approximation of the intended Pythia-1B." Table 4 header reads "Logit Margins per Configuration (H-M2 Proxy Model)." VERIFIED.
- [x] **C4 reframed as preliminary finding** — Introduction no longer lists a numbered Contribution C4. Instead, a "Preliminary Finding" block appears after C1-C3, explicitly labeled "not a contribution." Results 5.3 is titled "Preliminary Pilot." VERIFIED.
- [x] **Overclaiming language removed** — "establishes" no longer appears in abstract, introduction, or conclusion. Replaced with "demonstrate at quick-run scale," "provide strong preliminary evidence." VERIFIED.
- [x] **ρ=1.0 statistical context added** — Section 5.2 includes a note: "ρ=1.0 reflects perfect rank monotonicity across 5 discrete, ordered filter configurations; the p-value is computed at the pair level (n=1800 demographic-occupation pairs pooled across configurations)... ρ=1.0 across 5 ordered points confirms the absence of any reversal in the trend, but a continuous sweep (e.g., 20 percentile levels) would provide a stronger statistical basis." VERIFIED. (See MAJOR-A2 below for residual issue with this note.)

All five R1 fixes confirmed present.

---

## Part 1: Numerical Verification (Accuracy Checker)

### Mathematical Validity Checks

**Entropy formula.** Section 3.4 states: `H(occupation|demographic) = -Σ_{d,o} P(d,o) log₂ P(o|d)`. This is the standard conditional entropy formula written correctly. The P(d,o) weighting and P(o|d) inside the logarithm are internally consistent. No error found.

**Log-odds formula.** Section 3.5 states: `log-odds(d,o) = log[P(o|d) / (1 − P(o|d))]` with a clarifying note that "log denotes the natural logarithm (entropy uses log₂; log-odds use natural log — both are internally consistent within their respective analyses)." This note was added in R1 to address Human Review Note 7. Formula is correct and base is now disclosed. No error found.

**Bootstrap CI arithmetic check.** H(C5) − H(C1) = 2.5374 − 3.2702 = −0.7328 bits. The reported Bootstrap 95% CI is [−1.154, −0.330]. Sanity check: the point estimate (−0.7328) falls within the reported CI (−1.154 < −0.7328 < −0.330). The CI is asymmetric around the point estimate (lower half: |−1.154 − (−0.7328)| = 0.421; upper half: |−0.330 − (−0.7328)| = 0.403), which is consistent with bootstrap resampling producing a slightly non-symmetric distribution. The CI width of 0.824 bits is plausible for n=1000 bootstrap samples on a ~50k document corpus. No arithmetic error detected; CI is internally coherent.

**Table 2 values vs. ground truth.** All seven values match 065_ground_truth.yaml exactly. Relative changes are correctly computed:
- C2 vs C1: (3.1847 − 3.2702) / 3.2702 = −2.61% ✓ (paper says −2.61%)
- C3 vs C1: (3.0621 − 3.2702) / 3.2702 = −6.36% ✓ (paper says −6.35%, rounding acceptable)
- C4 vs C1: (2.8934 − 3.2702) / 3.2702 = −11.52% ✓ (paper says −11.52%)
- C5 vs C1: (2.5374 − 3.2702) / 3.2702 = −22.41% ✓ (paper says −22.41%)

All relative change values verified against ground truth. PASS.

**Spearman p-values: both H-E1 and H-M1 report p=1.4×10⁻²⁴.** See MAJOR-A2 below.

**Negative control value.** Ground truth records |C7 − C0| = 0.4953. Paper reports 0.495. Rounding is correct and the comparison to threshold 0.01 is unambiguous (0.495 >> 0.01). PASS.

---

### FATAL Issues

None found in R2.

---

### MAJOR Issues

#### MAJOR-A1: Configuration Count Inconsistency — Abstract Says "Seven" but Eight Configurations Exist

**Location:** Abstract (sentence 4); Table 1 (Section 3.2); Section 4.1

**Issue:** The abstract reads: "These effects hold robustly across seven corpus configurations on DCLM-POOL at ~50k document quick-run scale." Table 1 lists eight configurations: C0, C1, C2, C3, C4, C5, C6, C7. Section 4.1 states: "8 configurations total = 400k documents processed."

The number "seven" in the abstract appears to refer to the fastText sweep + DoReMi configurations (C0–C6 = 7), excluding C7 (the shuffled-demographic negative control), on the basis that C7 is a methodological control rather than a corpus configuration in the fairness audit sense. However, this logic is never stated, and "seven corpus configurations" directly contradicts the "8 configurations" count in Section 4.1 and the eight-row Table 1.

A reviewer who counts Table 1 rows will immediately notice this discrepancy. It introduces doubt about whether the authors have their own experimental setup correctly described.

**Required action:** Either (a) change "seven corpus configurations" in the abstract to "eight corpus configurations (including a shuffled-demographic negative control)" or (b) add a parenthetical in the abstract: "seven primary corpus configurations plus a shuffled-demographic negative control (C7)." The Section 4.1 "8 configurations total" language already uses eight; the abstract must be consistent.

---

#### MAJOR-A2: p-Value Unit Ambiguity Not Fully Resolved — H-E1 and H-M1 Identical p=1.4×10⁻²⁴

**Location:** Section 5.1 (H-E1), Section 5.2 (H-M1), Abstract, Introduction

**Issue:** R1 added a clarifying note in Section 5.2 explaining that the H-M1 p-value is "computed at the pair level (n=1800 demographic-occupation pairs pooled across configurations)." This partially addresses R1 MAJOR-C3. However, the problem now has an additional dimension visible only when both sections are read together:

Both H-E1 (entropy Spearman ρ=−1.0) and H-M1 (log-odds Spearman ρ=1.0) report the **exact same p-value: p=1.4×10⁻²⁴**. These are two different statistical tests on two different variables (entropy per configuration vs. log-odds per pair) run at different units of analysis. The probability of two independent statistical tests producing bit-for-bit identical p-values at this level of precision is negligible unless both p-values were computed using the same input (i.e., both are pair-level, n=1800, and both happen to produce perfect rank correlation).

If both are pair-level Spearman tests, then: for H-E1, the correlation is between (config rank, entropy value) for 5 configurations; for H-M1, the correlation is between (config rank, log-odds value) across 1800 pairs. These are structurally different tests. The identical p-value raises the question of whether one p-value was copied from the other, or whether both were derived from the same n=1800 pair-level computation applied to a different aggregation of the same data.

The clarifying note in Section 5.2 addresses the H-M1 unit of analysis but does not explain why H-E1 — which has only 5 configuration-level entropy values — produces the same p-value as H-M1. For H-E1, a Spearman test with n=5 and ρ=−1.0 cannot produce p=1.4×10⁻²⁴. The minimum attainable p-value for a two-tailed Spearman test with n=5 and ρ=1.0 is approximately p=0.083 (one-tailed: p=0.042). If the H-E1 p-value is pair-level (n=1800), the abstract and Section 5.1 must say so explicitly. If it is configuration-level (n=5), the value p=1.4×10⁻²⁴ is arithmetically impossible and constitutes a reported statistical error.

**Required action:** Clarify in Section 5.1 what the unit of analysis is for the H-E1 Spearman test (configuration-level n=5 or pair-level n=1800), and explain why both H-E1 and H-M1 produce the same p-value. If both are pair-level tests, state this explicitly in both sections. If the H-E1 p-value is a configuration-level result, the value must be corrected. This is the most technically damaging open issue in the paper.

---

## Part 2: Credibility Verification (Skeptical Expert)

### Missing Limitations Check

**English-only / Western-centric scope.** Section 2.1 quotes Dolma as "primarily English, Western-centric" and uses this as a comparison point. Section 6.2 limitations do not explicitly state that the current study is also English-only and limited to a Western-centric lexicon. A reviewer from a multilingual NLP background will notice the asymmetry: citing this limitation in related work but not acknowledging it as a limitation of the present study.

This is partially addressed: the paper notes "seven corpus configurations" with the DCLM-POOL (CommonCrawl-derived, English-heavy), and the WinoBias lexicon is English-only. However, the limitations section (L1-L4) does not include a limitation on language scope or geographic/cultural generalizability of findings. See MAJOR-C1 below.

**20 occupations only.** Section 3.3 correctly states "20 occupations paired with gender-indicating pronouns and modifiers." This is a known WinoBias constraint. The limitations section does not mention coverage limitations of the 20-occupation lexicon (e.g., missing non-binary gender categories, missing racial/ethnic demographic dimensions beyond the WinoBias scope). See MAJOR-C1 below.

**WinoBias lexicon limitations.** WinoBias [Zhao et al., 2018] is cited as the demographic lexicon source (Section 3.3, 3.6). WinoBias is known to have specific limitations: it covers only binary gender, 20 occupations drawn from U.S. Bureau of Labor Statistics data, and is English-only. The paper does not mention any of these known limitations of the lexicon it uses as the measurement instrument. A fairness reviewer familiar with the literature will flag this immediately.

**ρ=1.0 discrete-configuration interpretation.** The R1-added note is present in Section 5.2 and is substantively correct. It reads: "ρ=1.0 across 5 ordered points confirms the absence of any reversal in the trend, but a continuous sweep... would provide a stronger statistical basis." This adequately frames the limitation. The phrase "near-perfect statistical regularity" in the abstract is marginally acceptable because it is paired with "(Spearman ρ=1.0, p≈0 across 5 filter configurations)" which specifies the 5-configuration scope. This is acceptable as written.

**H-M2 proxy model framing.** The disclosure is comprehensive and appears in Sections 3.6, 4.2, 5.3, the "Preliminary Finding" block in the Introduction, and Limitation L1. The "Preliminary Finding" label in the Introduction is appropriate. The paper does not overclaim corpus-to-model propagation. This is satisfactory.

### Baseline Fairness Check

**DoReMi comparison.** DoReMi (Section 5.1, Table 2; Section 5.2, Table 3) is compared as an "alternative curation path." The paper reports C6 (DoReMi) entropy at 3.0541 bits, comparable to C3 fastText (3.0621 bits), and states: "the DoReMi alternative (C6: 3.0541 bits) achieves an entropy level comparable to C3, suggesting domain reweighting produces similar demographic concentration effects to median fastText filtering." This is a fair, appropriately hedged comparison. The paper does not claim DoReMi is worse or better on downstream performance — only that the demographic entropy effect is comparable to mid-level fastText. This framing is credible. No baseline unfairness detected.

**The paper notes in Section 2.1:** "DoReMi demonstrates that domain composition is a powerful lever — but measures only performance outcomes of domain reweighting, not demographic structure changes." This is accurate and fair. No issues.

---

### FATAL Issues

None found in R2.

---

### MAJOR Issues

#### MAJOR-C1: Missing Scope Limitations — WinoBias Lexicon Constraints and Language/Cultural Generalizability

**Location:** Section 6.2 Limitations; Section 3.3 Methodology

**Issue:** The Limitations section (L1-L4) covers training scale, missing H-M3, quick-run corpus scale, and single model family. It does not address three limitations that a fairness-specialized reviewer will consider essential:

1. **Binary gender only.** WinoBias covers male/female pronoun-based demographic categories. Non-binary and gender-neutral pronouns are absent. The demographic-occupation association entropy H(occupation|demographic) is therefore measuring a specific and narrow slice of the demographic space. The paper's claim that fastText functions as a "demographic reweighting mechanism" is accurate but must be scoped to this binary-gender occupational context.

2. **20-occupation coverage.** WinoBias occupations are drawn from U.S. Bureau of Labor Statistics data circa 2018 and represent a culturally specific sample. Other occupational taxonomies (e.g., ISCO-08 international classification) would produce different results. The 22.41% entropy reduction is specific to this occupation set.

3. **English-only, U.S.-centric lexicon.** Findings may not generalize to multilingual corpora or non-Western demographic-occupation association patterns. The DCLM-POOL is multilingual in principle (CommonCrawl) but the WinoBias lexicon is English-specific, meaning non-English documents are effectively excluded from the co-occurrence analysis.

None of these are disqualifying — they are the expected limitations of using WinoBias as a measurement instrument. But a paper making claims about demographic fairness implications for practitioners must disclose that the measurement instrument is gender-binary, occupation-limited, and English/U.S.-centric. Absence of this disclosure will draw reviewer criticism disproportionate to the actual severity.

**Required action:** Add a Limitation L5 in Section 6.2: "L5: WinoBias lexicon scope. The demographic-occupation lexicon is gender-binary (male/female pronouns only), covers 20 U.S.-centric occupations from BLS data, and is English-specific. Findings characterize fastText's effect on gender-binary, English-language occupation associations and may not generalize to non-binary gender categories, other demographic dimensions (race, age, nationality), or multilingual corpora." This addition does not weaken the core contribution; it demonstrates methodological self-awareness expected in fairness research.

---

## Human Review Notes

The following are minor/style issues that do not block convergence but should be addressed before final submission.

**HRN-1: C7 base configuration motivation (Table 1, Section 3.2).** R1 Human Review Note 2 flagged the absence of motivation for why C7 uses C3 as its base rather than C0 or C5. The R1 paper added the phrase "median entropy level, preserves overall frequency while destroying conditional associations" to the Table 1 C7 row. This is present and adequate. No further action needed.

**HRN-2: Log base clarification (Section 3.5).** R1 Human Review Note 7 requested explicit log-base statement for log-odds. R1 paper added: "log denotes the natural logarithm (entropy uses log₂; log-odds use natural log — both are internally consistent within their respective analyses)." This is present and satisfactory.

**HRN-3: GPU device ID removed.** R1 Human Review Note 3 requested removal of "CUDA_VISIBLE_DEVICES=1" from Section 4.2. The R1 paper does not contain this line. RESOLVED.

**HRN-4: Unverified citations.** Paper statistics block notes 2 unverified citations (84.6% verification rate). The paper identifies these as "Gebru et al. 2018 (conference vs. journal version)" and "Biderman et al. 2023 (Pythia ICML)." Both citations appear in text (References section). Verify before submission: Gebru et al. was originally a workshop paper and later published in Communications of the ACM 2021; the ICML 2023 Pythia paper by Biderman et al. is verifiable at arXiv:2304.01373. Use the correct venue designation.

**HRN-5: Introduction p≈0 vs. p=1.4×10⁻²⁴ inconsistency.** The abstract and Introduction both use "p≈0" for the H-M1 Spearman result, while Results 5.2 gives the exact value "p=1.4×10⁻²⁴." This inconsistency is stylistically acceptable (abstract space constraints) but a reviewer may ask why the abstract uses p≈0 rather than the exact value. Consider replacing "p≈0" with "p=1.4×10⁻²⁴" in the abstract for precision, or adding a footnote that "p≈0 denotes p=1.4×10⁻²⁴."

**HRN-6: Section 5.1 narrative is now accurate post-R1 Table 2 fix.** The paper correctly notes: "C3 (fastText ≥ 50%) shows a −6.3% reduction relative to C1, and C4 (fastText ≥ 70%) shows a −11.6% reduction. The largest single-step drop concentrates at C4→C5 (2.8934→2.5374 bits, −7.7 percentage points)." With ground-truth values: C4→C5 = 2.8934 − 2.5374 = 0.356 bits; C3→C4 = 3.0621 − 2.8934 = 0.169 bits. The narrative correctly identifies C4→C5 as the largest single-step drop. Verified accurate.

**HRN-7: H-M2 rho discrepancy transparency.** Section 5.3 includes a "Note on rho provenance" disclosing the discrepancy between h-m2/04_validation.md (ρ=0.357) and verification_state.yaml (ρ=−0.2143). This disclosure is present and appropriate. The paper correctly uses 0.357 from the primary record (h-m2/04_validation.md) and flags reconciliation as future work. This is adequate for submission; a reviewer may ask for more but the disclosure is substantively honest.

**HRN-8: "near-perfect regularity" language in abstract.** The abstract reads: "amplifying conditional log-odds across 1800 demographic-occupation pairs with near-perfect regularity (Spearman ρ=1.0, p≈0 across 5 filter configurations)." The parenthetical "(across 5 filter configurations)" now scopes the claim appropriately following the R1 fix. This is acceptable.

---

## Summary

| Round | FATAL | MAJOR | Outcome |
|-------|-------|-------|---------|
| R1 | 1 | 6 | All fixed in 06_paper_r1.md |
| R2 | 0 | 3 | Fix required before submission |

**R2 MAJOR issues requiring action before submission:**

1. **MAJOR-A1 (Configuration count):** Abstract says "seven corpus configurations" but 8 are defined and counted in Table 1 and Section 4.1. Fix by adding "(plus shuffled-demographic negative control)" or changing to "eight."

2. **MAJOR-A2 (p-value unit ambiguity):** H-E1 and H-M1 both report p=1.4×10⁻²⁴. For H-E1 with ρ=−1.0 across n=5 configurations, this p-value is arithmetically impossible at the configuration level. Must clarify whether H-E1 p-value is pair-level (n=1800) or configuration-level (n=5), and correct or explain the identical p-values. This is the highest-risk remaining issue for a statistically careful reviewer.

3. **MAJOR-C1 (WinoBias scope limitation):** The Limitations section omits WinoBias's binary-gender-only coverage, 20-occupation U.S.-centric scope, and English-only constraint. Add Limitation L5 disclosing these known instrument limitations.

**What is solid and should not change:**
- All Table 2 entropy values (verified against ground truth)
- All Table 3 log-odds values (verified against ground truth)
- Bootstrap CI [−1.154, −0.330] (arithmetically coherent, excludes zero)
- H-M2 proxy model framing (comprehensive disclosure throughout)
- C4 demotion to "Preliminary Finding" (correctly removed from numbered contributions)
- Overclaiming language removal (all "establishes" replaced)
- ρ=1.0 statistical context note in Section 5.2
- DoReMi comparison framing (fair and appropriately hedged)
- Limitations L1-L4 (complete and honest)
- Related work framing (accurate and well-positioned)
