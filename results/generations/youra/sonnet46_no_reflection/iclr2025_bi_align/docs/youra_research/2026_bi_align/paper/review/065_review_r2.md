# Phase 6.5 Adversarial Review — Round 2
# Focus: Numerical Verification and Credibility
# Paper: Can Existing RLHF Preference Corpora Reveal Human-to-AI Stylistic Adaptation?
# Revision reviewed: 06_paper_r1.md
# Review Date: 2026-05-12
# Personas: Accuracy Checker + Skeptical Expert

---

## Ground Truth Verification Table

| Claim | Paper (r1) Location | Paper Value | Ground Truth | Match | Notes |
|-------|--------------------|----|---|---|---|
| β₄ coefficient | Abstract, Intro, Results 5.3, Conclusion | −0.0016308 | −0.0016308 | EXACT | |
| β₄ OR | Abstract, Results 5.3 | 0.9984 | 0.9983705 | ACCEPTABLE | Rounded to 4 dp |
| β₄ OR (abstract) | Abstract | 0.998 | 0.9983705 | ACCEPTABLE | Rounded to 3 dp |
| CI lower | Results 5.3, Conclusion | 0.9861 | 0.9861 | EXACT | |
| CI upper | Results 5.3, Conclusion | 1.0108 | 1.0108 | EXACT | |
| CI width | Results 5.4 | "approximately 0.025" | 0.0247 | MINOR DISCREPANCY | Actual = 0.0247; rounding to 0.025 is acceptable but imprecise |
| "rules out OR ≥ 1.011" | Results 5.4 | ≥ 1.011 | CI upper = 1.0108 | BORDERLINE | CI upper = 1.0108 < 1.011, so claim technically holds, but imprecise; correct value is ≥ 1.0108 |
| Wald p-value | Results 5.3 | 0.7958 | 0.7958274 | ACCEPTABLE | Rounded to 4 dp |
| LRT statistic | Results 5.3 | 0.067 | 0.0670215 | ACCEPTABLE | Rounded to 3 dp |
| LRT p-value | Results 5.3 | 0.7957 | 0.7957239 | ACCEPTABLE | Rounded to 4 dp |
| β₁ (abstract/intro) | Abstract, Intro, Conclusion | 0.025 | 0.0246 | MINOR DISCREPANCY | Rounded from 0.0246; inconsistent with Table 1 (0.0246) |
| β₁ (Table 1) | Results 5.2 Table 1 | +0.0246 | 0.0246 | EXACT | |
| β₁ OR | Results 5.2 Table 1 | 1.0249 | 1.0249 (exp(0.0246)) | EXACT | |
| β₂ | Results 5.2 Table 1 | +0.0008 | 0.0008 | EXACT | |
| Preference pairs | Throughout | 80,342 | 80,342 | EXACT | |
| Semantic clusters | Throughout | 27,034 | 27,034 | EXACT | |
| Median cluster size | Section 3.2, 4.5 | 2.8 | 2.8 | EXACT | |
| Newton iterations | Section 3.4, 4.5, 5.6 | 14 | 14 | EXACT | |
| Gradient norm | Section 3.4, 5.6 | 3.2 × 10⁻⁸ | 3.2e-8 | EXACT | |
| Runtime | Section 4.5 | 2037.7s (~34 min) | 2037.7s (33.96 min) | EXACT | |
| Mechanism checks | Results 5.5 | 5/5 PASS | 5/5 PASS | EXACT | |
| Helpful-base total rows | Section 4.2 | 43,835 | 43,835 | EXACT | |
| Helpful-base retained | Section 4.2 | 20,108 | 20,108 | EXACT | |
| Helpful-online total rows | Section 4.2 | 22,007 | 22,007 | EXACT | |
| Helpful-online retained | Section 4.2 | 20,063 | 20,063 | EXACT | |
| Safety preface lexicon size | Section 3.1 | 14 | 14 | EXACT | |
| Baseline comparison | Not mentioned | — | SKIPPED (skip_baseline_comparison=true) | N/A | Correctly absent from paper |

---

## Executive Summary

**FATAL Issues: 0**
**MAJOR Issues: 2**
**MINOR Issues: 4**

The R1 revision has successfully resolved all four MAJOR issues from Round 1. The paper is numerically accurate on essentially all quantitative claims. Two new MAJOR issues are identified in this round: (1) a precision mismatch in the "rules out OR ≥ 1.011" claim vs. the actual CI upper bound of 1.0108, which while technically defensible is internally inconsistent with other figures; and (2) the abstract's rounded β₁ = 0.025 is inconsistently applied relative to the precise Table 1 value of 0.0246, creating ambiguity in a visible claim. Additionally, five [UNVERIFIED] citations remain and constitute an ongoing credibility risk. The paper's core argument is sound, the null result is credible, and the four contributions are defensible given appropriate hedging already present in the text.

---

## FATAL Issues

*None found.*

---

## MAJOR Issues

### MAJOR-R2-001: "Rules Out OR ≥ 1.011" — Imprecise Threshold Inconsistent with Reported CI

**Persona:** Accuracy Checker
**Location:** Results, Section 5.4 (Power and Precision Analysis)
**Severity:** MAJOR

**Issue:**

Section 5.4 states: *"The upper bound of 1.0108 rules out any OR ≥ 1.011 at the 95% confidence level."*

The CI upper bound is reported as 1.0108. The claim that this rules out OR ≥ 1.011 is technically true (1.0108 < 1.011), but it is misleading and inconsistent:

- The correct statement is that the CI rules out OR ≥ 1.0108, not OR ≥ 1.011.
- Writing "rules out OR ≥ 1.011" when the upper bound is 1.0108 implies the threshold of 1.011 was derived from the CI, when in fact 1.011 is slightly *above* the CI upper bound. This creates a numerically confusing sentence: a reader who checks the arithmetic will find that 1.0108 ≠ 1.011.
- The ground truth YAML (`065_ground_truth.yaml`, `adversarial_review_targets`) states: *"CI width = 0.0247, upper bound 1.0108, rules out OR ≥ 1.015"* — an even more conservative (and more honest) threshold.
- A reviewer performing spot-checking will flag this as a rounding error or attempt to overstate precision.

The correct formulation is either:
  - "The CI upper bound of 1.0108 rules out OR ≥ 1.011 at the 95% confidence level" → technically true but should be stated as "rules out OR ≥ 1.0108" for accuracy.
  - Or simply: "The upper bound of 1.0108 rules out effects of OR ≥ 1.011, and effects as large as OR = 1.10 lie far outside the CI" — keeping both statements but distinguishing them.

**Required Fix:** Replace "rules out any OR ≥ 1.011" with "rules out any OR ≥ 1.0108" to match the reported CI upper bound exactly. Then add the separate interpretive statement that OR = 1.10 (the practical threshold) lies far outside the CI.

Corrected sentence: *"The upper bound of 1.0108 rules out OR ≥ 1.0108 at the 95% confidence level; effects as large as OR = 1.10, the minimum practical threshold set a priori, lie far outside the CI."*

---

### MAJOR-R2-002: β₁ Rounding Inconsistency — Abstract/Introduction/Conclusion Report 0.025 While Table 1 Reports 0.0246

**Persona:** Accuracy Checker
**Location:** Abstract, Introduction (para. "The findings"), Results 5.2, Discussion 6.2, Conclusion
**Severity:** MAJOR

**Issue:**

The paper reports β₁ inconsistently across locations:
- **Abstract:** "β₁ = 0.025, p < 0.001" (rounded to 3 sig. fig.)
- **Introduction (para. "The findings"):** "β₁ = +0.025 (p < 0.001)"
- **Results 5.2, Table 1:** "β₁ = +0.0246" (4 sig. fig.)
- **Results 5.2 text:** "β₁ = **+0.0246** (p < 0.001, ***)"
- **Discussion 6.2:** "β₁ = +0.0246"
- **Conclusion:** "β₁ = +0.025 (p < 0.001)"

The actual value from ground truth is 0.0246. Rounding to 0.025 is acceptable in isolation for abstract/conclusion brevity. However, having both 0.025 and 0.0246 in the same paper without explicitly noting "β₁ = 0.0246 (≈ 0.025)" creates an ambiguity that a careful reviewer will flag — particularly because 0.025 is also the CI width, making the coincidence confusing.

The specific risk: a reviewer reading the abstract (β₁ = 0.025) and then Table 1 (β₁ = +0.0246) will wonder if these are the same number or whether a different specification is being cited. This ambiguity is avoidable.

**Required Fix:** Standardize to 0.0246 everywhere (the 4-significant-figure value from Table 1), or explicitly note in the first instance of rounded usage (e.g., abstract) that β₁ = 0.0246 is reported as ≈ 0.025 for readability. The conclusion should use the same precision as the abstract. Recommend: use 0.0246 in abstract and conclusion, consistent with Table 1.

---

## MINOR Issues (Collected for Human Review — NOT Auto-Fixed)

### MINOR-R2-001: OR = 0.9984 vs. exact 0.9983705 — abstract uses 0.998

**Location:** Abstract
**Type:** precision / clarity
**Note:** Abstract reports "OR = 0.998" (3 dp). Introduction and Results report "OR = 0.9984" (4 dp). The exact value is 0.9983705. All are acceptable roundings individually, but mixing 3 dp and 4 dp across abstract/body is inconsistent. Recommend 0.9984 throughout for uniformity, or note in abstract that 0.9984 is rounded.

### MINOR-R2-002: CI precision — abstract vs. body

**Location:** Abstract vs. Section 5.3
**Type:** precision / clarity
**Note:** Carried forward from R1 MINOR-001 (not yet resolved per paper text). Abstract reports "[0.986, 1.011]" (3 dp); body reports "[0.9861, 1.0108]" (4 dp). This remains inconsistent. Recommend 4 dp throughout, or acknowledge abstract uses rounded values.

### MINOR-R2-003: "~34 minutes" runtime — minor precision note

**Location:** Section 4.5
**Type:** minor precision
**Note:** 2037.7 seconds = 33.96 minutes. The paper says "~34 minutes" which is an acceptable rounding. No change needed, but note that "approximately 34 minutes" is the cleaner phrasing vs. "~34 minutes" in formal text.

### MINOR-R2-004: [UNVERIFIED] citations remain — 5 of 10

**Location:** References section
**Type:** citation credibility
**Note:** Five references carry [UNVERIFIED] tags: Bai et al. 2022, Ji et al. 2023, McFadden 1974, Shen et al. 2024, Vishwarupe et al. 2026. In a submitted paper, these tags must be removed — either after verification or with a note that they are preprints/working papers. McFadden 1974 is a classic econometrics textbook chapter and should be trivially verifiable. Bai et al. 2022 is a widely-cited arXiv paper. Vishwarupe et al. 2026 has a future date (2026) and may not yet be published; if it is a preprint or forthcoming work, this should be stated explicitly rather than citing as a 2026 paper without qualification. This is not auto-fixable but must be resolved before submission.

---

## R1 Fix Verification

| Issue | R1 Description | Status in r1 Paper | Verdict |
|-------|---------------|-------------------|---------|
| MAJOR-001 | Incomplete perplexity coefficient in Table 1 ("pending final run" placeholder) | Table 1 no longer contains a perplexity row. Section 3.3 note added: "perplexity was applied as a data quality filter during preprocessing rather than as a model covariate." Section 5.2 table note confirms. | RESOLVED |
| MAJOR-002 | BFGS failure cause misattributed to large n rather than Hessian ill-conditioning from many small clusters | Section 5.6 now correctly states: "BFGS fails... because the Hessian is ill-conditioned due to the large number of small-sized cluster fixed effects (27,034 clusters, median size 2.8 pairs)... This is a structural issue inherent to the fixed-effects parameterization with many sparse groups." | RESOLVED |
| MAJOR-003 | Missing discussion of effective degrees of freedom / cluster-level precision | Section 5.4 now contains: "This precision is derived from the conditional likelihood, which appropriately accounts for the cluster fixed-effect structure: the effective precision is determined by 27,034 cluster-level strata rather than 80,342 nominally independent pairs." | RESOLVED |
| MAJOR-004 | Scope overclaim on "minimum infrastructure" conclusion | Abstract, Section 6.4, and Conclusion now use: "illustrates a key infrastructure constraint," "motivates a new generation of annotator-linked... preference corpora," and "This falsification illustrates a key data infrastructure constraint." The phrase "defines minimum requirements" has been replaced with "outlines a feasible annotation protocol." | RESOLVED |

All four R1 MAJOR issues are properly resolved in the r1 revision.

---

## Persuasiveness Assessment

### Four Contributions — Are They Defensible?

| Contribution | Defensibility | Assessment |
|---|---|---|
| 1. AIFS construct introduction and validation | YES | β₁ = +0.0246, p < 0.001 on 80,342 pairs is solid construct validation. The construct is explicitly transferable. The regex operationalization is a defensible methodological choice with clear rationale. |
| 2. Conditional logit supply-control pipeline with Newton optimizer | YES | BFGS failure and Newton resolution are documented with precise metrics (14 iterations, gradient norm 3.2e-8). The contribution is practical and replicable. |
| 3. First empirical falsification of split-based adaptation proxies | MOSTLY DEFENSIBLE | The "to our knowledge" hedge is present in Section 3. The quantitative precision (CI width 0.0247) makes the falsification credible. However, the paper cannot exclude other HH-RLHF analyses that may have incidentally tested this. |
| 4. Data infrastructure constraint illustration | DEFENSIBLE (with appropriate hedging) | R1 correctly softened from "defines minimum requirements" to "illustrates a key constraint." This contribution is now proportionate to what the single null result can support. |

### Perplexity-as-Filter Explanation — Is It Credible?

The paper now consistently states that "perplexity was applied as a data quality filter during preprocessing rather than as a model covariate" (Section 3.3 note, Table 1 note). This explanation is credible and internally consistent. The sensitivity analysis (Figure 2, four specifications) confirms stability of β₁ and β₄. The absence of a perplexity covariate is no longer a credibility concern.

### "Precision Null" Claim — Is It Overclaiming?

The claim that the null is a "precision null" rather than an underpowered null is well-supported:
- CI width 0.0247 (reported as ~0.025) is narrow relative to the practical threshold of OR = 1.10.
- The effective sample for precision is 27,034 cluster-level strata, correctly acknowledged in Section 5.4.
- The OR = 1.10 practical threshold lies far outside the CI (1.10 vs. CI upper 1.0108), providing a clear magnitude argument.
- The "precision null" framing is appropriate given these numbers. No overclaiming found here.

### Unverified Citations — Are They a Problem?

Yes, to a moderate degree. Five [UNVERIFIED] tags in a 10-citation paper (50% verification rate) is notable. Key risks:
- **Vishwarupe et al. 2026**: A 2026 date in a paper dated 2026-05-12 suggests a very recent or forthcoming paper. A reviewer may not be able to access this, and the paper makes substantive claims about it ("audit 16 major alignment benchmarks"). If this does not exist or is a preprint, the framing of Section 2.1 is overstated.
- **Shen et al. 2024**: Cited as "most comprehensive review" and "conceptually decisive." If this is a non-peer-reviewed preprint or has been retracted, this could weaken the positioning of the Related Work.
- **McFadden 1974**: This is a canonical reference and near-certainly exists. The [UNVERIFIED] tag is a paperwork issue only.
- **Bai et al. 2022 and Ji et al. 2023**: Both are widely-cited arXiv papers. Low risk.

**Overall:** The [UNVERIFIED] tags themselves are metadata artifacts that must not appear in a submitted manuscript. The underlying citation existence risk is low for most, but Vishwarupe et al. 2026 warrants scrutiny.

### Is the Conclusion's Future-Work Section Overconfident?

Section 7 (Conclusion) identifies four specific future-work directions: annotator-linked datasets (UltraFeedback, LMSYS-Chat-1M), longitudinal within-annotator design, AIFS pipeline validation against pre-LLM baselines, and a "schema bidirectionality index audit" across HH-RLHF, BeaverTails, PKU-SafeRLHF. This is specific and grounded. The named datasets (UltraFeedback, LMSYS-Chat-1M) are real and publicly available. The framing is "redirected" rather than "blocked," which is accurate. No overconfidence found in the future-work section.

---

## Summary

**Round 2 verdict: REVISE (minor revision)**

The paper is in substantially better shape after R1 fixes. The numerical accuracy is high; the core null result is credible; the four contributions are appropriately hedged; the precision null framing is justified. Two MAJOR issues remain:

1. **MAJOR-R2-001** (Accuracy): "rules out OR ≥ 1.011" should be "rules out OR ≥ 1.0108" — the current phrasing is technically correct but imprecise relative to the reported CI upper bound and will invite reviewer scrutiny.

2. **MAJOR-R2-002** (Consistency): β₁ rounding (0.025 vs. 0.0246) is inconsistent across abstract/introduction/conclusion vs. Table 1. Standardize to 0.0246 throughout.

Both MAJOR issues are cosmetic-to-minor in scientific significance but are the kind of numerical inconsistencies that adversarial reviewers flag immediately. Fixing them requires editing approximately 6 sentences. Once resolved, the paper has no remaining precision or credibility gaps detectable from the ground truth data.
