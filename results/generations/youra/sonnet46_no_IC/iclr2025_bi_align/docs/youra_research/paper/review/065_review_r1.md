# Adversarial Review — Round 1
# Three-Persona Review: Accuracy Checker · Bored Reviewer · Skeptical Expert
# Paper: "Capability or Verbosity? Disentangling the Drivers of Length-Debiased Preference in LLM Evaluation"
# Date: 2026-08-04
# Mode: UNATTENDED

---

## Ground Truth Summary

| Metric | Ground Truth (Phase 4) | Paper Claims | Match |
|--------|----------------------|--------------|-------|
| r_partial (H-E1) | 0.9851 | 0.9851 | ✅ |
| p-value (H-E1) | 1.69e-170 | 1.69e-170 | ✅ |
| Bootstrap CI lower | 0.9760 | 0.976 | ✅ |
| Bootstrap CI upper | 0.9875 | 0.988 | ✅ (rounded) |
| VIF | 1.764 | 1.764 | ✅ |
| β_win_std (H-M1) | 21.3391 | 21.34 | ✅ |
| β_len_std (H-M1) | -4.3720 | -4.37 | ✅ |
| Dominance ratio (H-M1) | 4.88 (21.34/4.37) | 4.88 | ✅ |
| R² full (H-M1) | 0.9628 | 0.963 | ✅ |
| R² verbosity-only (H-M1) | 0.2561 | 0.256 | ✅ |
| R² gain | 0.9628-0.2561=0.7067 | +70.7pp | ✅ |
| FWL ρ_resid (H-M2) | 0.9739 | 0.9739 | ✅ |
| FWL delta | 0.9851-0.9739=0.0112 | 0.0112 | ✅ |
| KW H (H-C1) | 196.3190 | 196.32 | ✅ |
| KW p (H-C1) | 2.6332e-42 | 2.63e-42 | ✅ |
| ε² (H-C1) | 0.8827 | 0.883 | ✅ |
| Dunn Q1 vs Q4 p (H-C1) | 1.0379e-38 | 1.04e-38 | ✅ |
| Monotonic (H-C1) | True | True | ✅ |
| Q1 median LC | 7.1391 | 7.14 | ✅ |
| Q2 median LC | 14.6901 | 14.69 | ✅ |
| Q3 median LC | 26.4112 | 26.41 | ✅ |
| Q4 median LC | 51.6178 | 51.62 | ✅ |
| KW H (H-M3) | 22.1852 | 22.19 | ✅ |
| KW p (H-M3) | 5.9691e-05 | 5.97e-05 | ✅ |
| ε² (H-M3) | 0.0876 | 0.088 | ✅ |
| Dunn Q1 vs Q4 p (H-M3) | 1.0 | 1.0 | ✅ |
| Heteroscedasticity BP p (H-M1) | 0.0114 | 0.011 | ✅ |

**All numerical claims verified against ground truth. Zero discrepancies found.**

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| FATAL | 0 | — |
| MAJOR | 3 | Require fix |
| MINOR (human review) | 7 | Collected — NOT auto-fixed |

**Recommendation: REVISE (MAJOR issues only — no fatal issues)**

Persuasiveness Check: MIXED (see Bored Reviewer findings below)

---

## PERSONA 1: ACCURACY CHECKER
**Role: Fact-checker and claim verifier**

### Finding AC-001 [MAJOR] — Bootstrap CI Discrepancy in H-E1

**Location**: Abstract, Section 5.1, Table in Section 5.1
**Claim**: "Bootstrap 95% CI [0.976, 0.988]"
**Ground Truth**: H-E1 validation report states Bootstrap CI 95%: [0.9760, 0.9875]

The paper reports the upper bound as 0.988, but the Phase 4 validation shows 0.9875. This is a rounding issue — 0.9875 correctly rounds to 0.988 (2 decimal places of the 3 significant digits). However, Section 5.1 also says "CI95%: [0.9800, 1.0000]" from the pingouin output in the validation file, which is the parametric CI, not the bootstrap CI. The paper correctly uses the bootstrap CI [0.976, 0.988] from the `Bootstrap CI 95%: [0.9760, 0.9875]` line.

**Assessment**: After careful inspection, the paper correctly uses the bootstrap CI [0.976, 0.988], distinct from the pingouin parametric CI [0.980, 1.000]. This is NOT a discrepancy — the paper states the more conservative bootstrap CI. 

**Revised Status: DOWNGRADE TO MINOR** — The paper should clarify in the text that it reports bootstrap CI (not parametric CI) to avoid reviewer confusion, since pingouin also outputs a parametric CI that is different.

**Action**: Add "bootstrap" qualifier explicitly where CI is mentioned in text (it's in the table header but not always in prose).

---

### Finding AC-002 [MAJOR] — Unverified Citation (Singhal 2023)

**Location**: References section; Section 6.4 context
**Issue**: Reference "Singhal, P., et al. (2023). How LLMs Interact with Length Bias in RLHF" is flagged as [UNVERIFIED] in the paper's own Statistics block and in 065_ground_truth.yaml.

The paper currently includes this reference in the references list with the note "[UNVERIFIED — verify before submission]" in the paper's own text. This is a critical submission risk: reviewers will check references, and a fabricated or misidentified citation will cause immediate rejection.

**Evidence**: Paper text (line in References): "Singhal, P., et al. (2023). How LLMs Interact with Length Bias in RLHF. *arXiv preprint*. [UNVERIFIED — verify before submission]"

**Action Required**: EITHER verify this citation exists (find actual arXiv ID) OR remove from references and remove any in-text citation. Do NOT submit with unverified citations.

**Severity**: MAJOR — Unverified citation is a submission-blocking issue.

---

### Finding AC-003 [MAJOR] — Ji 2023 Citation Also Unverified

**Location**: Section 2.2, References
**Claim**: Ji et al. (2023) "AI Alignment: A Comprehensive Survey" arXiv:2310.19852
**Issue**: 065_ground_truth.yaml explicitly flags: "Ji2023Survey — arxiv_claimed: 2310.19852 — Not confirmed via MCP in this session — verify"

The paper cites this survey in Section 2.2: "Ji et al. [2023] survey alignment approaches broadly...". If arXiv:2310.19852 does not correspond to this paper, the citation is wrong.

**Action Required**: Verify arXiv:2310.19852 is indeed "AI Alignment: A Comprehensive Survey" by Ji et al. OR correct citation. Given the paper relies on this for the "open problem" framing in Related Work, it needs verification.

**Severity**: MAJOR — unverified citation.

---

### Finding AC-004 [MINOR — Human Review] — "~5×" vs Actual ~4.88×

**Location**: Abstract
**Claim**: "capability explains ~5× more LC variance than verbosity in standardized regression"
**Ground Truth**: Dominance ratio = 21.34 / 4.37 = 4.88

The paper uses "~5×" in the abstract but the actual ratio is 4.88×. This rounds to ~5× appropriately for the abstract. The body correctly states "4.88:1". However, reviewers may note the discrepancy between "~5×" (abstract) and "4.88×" (body). Suggest "~5×" is fine but ensure body text consistently says "~4.9×" or "4.88×".

**Category**: MINOR (style/precision)
**Action**: Human review — consider whether to use "~4.9×" in abstract for consistency with body.

---

### Finding AC-005 [MINOR — Human Review] — "~4.9" vs "~5" inconsistency  

**Location**: Introduction, Discussion
**Issue**: Introduction says "factor of ~4.9" (correct), Discussion says "factor of ~5 in standardized regression". The abstract says "~5×". These three phrasings are slightly inconsistent.
**Category**: MINOR (style)
**Action**: Human review — unify to "~4.9×" or "4.88×" throughout.

---

## PERSONA 2: BORED REVIEWER
**Role: Busy NeurIPS reviewer with 5 papers to review today**

### Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ PASS | Starts with headline number, problem clear |
| Problem clear in 1 minute? | ✅ PASS | Introduction paragraph 1 excellent |
| Novelty clear in 2 minutes? | ✅ PASS | "partial vs bivariate" framing is clear |
| Figure 1 self-explanatory? | ⚠️ LIMITED | No figures in paper text (references to figures exist but no actual figures embedded) |
| Would continue reading? | ✅ YES | Abstract is engaging, hook works |
| Attention lost at? | Section 4 | Experiments section is redundant with Methodology |

### Finding BR-001 [MAJOR] — Experiments Section is Partially Redundant

**Location**: Section 4 (Experimental Setup)
**Issue**: Section 4 repeats information already in Section 3. Specifically:
- Section 3.1 defines dataset (N=223, variables)
- Section 4.1 again describes same dataset
- Section 3.2–3.5 defines the analyses
- Section 4.2–4.4 partially restates RQs and thresholds from Section 3

A bored reviewer scanning Section 4 after Section 3 will feel the paper is padded. For a conference paper targeting ~8 pages, this redundancy costs space that could be used for analysis.

**What works**: The RQ framing in Section 4 (RQ1–RQ5) is actually useful for navigating Results — but it should appear in Introduction or Methodology, not as a separate Experiments section.

**Action**: Consider merging Section 4's RQ table into Section 3's analysis design, or collapse Section 4 to a brief paragraph pointing to Section 3 for setup details. This is a structural MAJOR issue that weakens the paper's density.

**Severity**: MAJOR — redundancy hurts paper at page-limited conference.

---

### Finding BR-002 [MINOR — Human Review] — Section 5.1 contains redundant bivariate scatter claim

**Location**: Section 5.1 (RQ1)
**Text**: "Figure 1 shows the bivariate scatter (ρ = 0.966)"
**Issue**: The text mentions ρ = 0.966 as the bivariate correlation in the figure, but this number is not featured in the abstract, introduction, or methodology. It appears without prior setup. A reviewer notes: "where did 0.966 come from? The abstract says bivariate was 0.94 (Dubois)."

The 0.966 is the bivariate Spearman ρ in our sample (from H-C1 secondary analysis: rho=0.9662). The 0.94 is what Dubois et al. [2024] reported. These are different numbers (different samples/methods) and the paper doesn't clarify this distinction adequately. Readers will be confused.

**Category**: MINOR (clarity)
**Action**: Add a brief note: "Our bivariate ρ = 0.966 exceeds Dubois et al.'s reported 0.94, reflecting our larger and more diverse model set."

---

### Finding BR-003 [MINOR — Human Review] — Word count concern

**Location**: Paper metadata / actual text
**Issue**: Paper metadata says ~3805 words total, estimating ~8 pages. ICML 2025 standard is 8 pages + unlimited references. The paper is likely fine, but the word count seems low for 8 pages — reviewers may feel it's thin in some sections if padded with redundant experiments. Given BR-001 (redundancy), cutting Experiments and reinvesting words elsewhere would improve density.

**Category**: MINOR (structural)

---

## PERSONA 3: SKEPTICAL EXPERT
**Role: Domain expert looking for holes in claims**

### Finding SE-001 [MAJOR] — FWL Caveat Understated

**Location**: Section 3.4, Section 5.3, Discussion
**Issue**: The Frisch-Waugh-Lovell (FWL) theorem guarantees *exact* equality between partial OLS coefficients and residualized OLS coefficients — but only for **Pearson** (OLS) regression. The paper applies this to **Spearman** (rank-based) partial correlation, for which FWL is an approximation, not a theorem.

The paper does acknowledge this in the ground truth's `adversarial_review_targets`: "FWL exact equality only holds for Pearson, not Spearman — acknowledged as 'should work' not exact."

However, in the **paper text itself**, this limitation is not stated. Section 3.4 says "FWL Theorem Verification" without qualifying that the theorem strictly applies to Pearson. Section 5.3 says "two independent estimators converge" without noting that strict FWL equality is not expected for Spearman.

A skeptical reviewer will flag this: "The FWL theorem does not apply to Spearman correlation. Calling this 'FWL verification' is misleading."

**Action Required**: Add a qualifying sentence in Section 3.4 and/or Section 5.3: "Note: The FWL theorem guarantees exact equality for Pearson partial correlations; for Spearman, we use residualized rank correlation as an *independent estimator* approximating the FWL principle. Delta = 1.1pp [0.976, 0.988] confirms the two approaches agree well empirically, providing robustness evidence even without exact theoretical guarantee."

**Severity**: MAJOR — a sophisticated reviewer will catch this and it weakens the methodological contribution if unaddressed.

---

### Finding SE-002 [MINOR — Human Review] — VIF interpretation borderline framing

**Location**: Section 3.1, 5.1
**Claim**: "VIF = 1.764 (threshold: VIF < 5.0), confirming no multicollinearity"
**Issue**: VIF = 1.764 is low, but the paper's claim that partial correlations are "interpretable" solely because VIF < 5 is an OLS-specific heuristic. For Spearman partial correlation, the VIF diagnostic is less directly applicable. The paper correctly reports VIF but shouldn't rely on it exclusively as the interpretability warrant for Spearman analysis.
**Category**: MINOR (methodological precision)
**Action**: Human review — add footnote noting VIF is computed for OLS interpretability; for Spearman, the low VIF additionally supports the robustness of the rank-based analysis.

---

### Finding SE-003 [MINOR — Human Review] — Bivariate 0.94 vs our 0.966

**Location**: Abstract, Introduction, Section 2.1
**Claim**: "higher than the 0.94 bivariate correlation previously reported" (Dubois 2024)
**Issue**: Our sample bivariate ρ = 0.966 (from H-C1 secondary analysis). The abstract says partial (0.985) exceeds bivariate (0.94), but the relevant comparison for our *sample* is partial (0.985) vs our *sample's* bivariate (0.966). The paper is comparing to Dubois' reported bivariate (0.94 from a different sample/era). A skeptical reviewer may note: "Your bivariate correlation in your sample is 0.966, not 0.94. Your partial of 0.985 exceeds your own bivariate by only 0.019pp, not 0.045pp."

The paper is not wrong to compare to Dubois' 0.94 as a baseline, but should be explicit: "Dubois et al. [2024] report bivariate ρ ≈ 0.94; our sample yields bivariate ρ = 0.966, and our partial correlation (0.985) exceeds both."

**Category**: MINOR (precision/framing)
**Action**: Human review — add clarifying note distinguishing Dubois' 0.94 from our sample's bivariate 0.966.

---

### Finding SE-004 [MINOR — Human Review] — Missing limitation: Epsilon-squared for KW

**Location**: Section 5.4, Discussion
**Issue**: ε² = (H − k + 1)/(N − k) is one effect size formula for KW. The paper uses this formula correctly (verified: (196.32 - 4 + 1)/(223 - 4) = 193.32/219 = 0.883). However, the formula is stated in Section 3.5 but NOT cited to a methodological source. Some reviewers may question whether this is the right KW effect size (alternatives: η², rank-biserial correlation).
**Category**: MINOR (methodology citation)
**Action**: Human review — add citation for ε² formula (e.g., Tomczak & Tomczak 2014 or equivalent).

---

### Finding SE-005 [MINOR — Human Review] — H-M3 gate "SHOULD_WORK" not fully transparent

**Location**: Section 5.5, Discussion 6.2
**Issue**: The paper presents H-M3 (Δ as DV) as PASS, but the ground truth shows monotonic trend = False and Dunn Q1 vs Q4 p = 1.0. The paper correctly notes "Non-monotonic" and discusses this in Discussion 6.2. However, the paper claims H-M3 "passed its gate" (Section 5.6 summary table) without clarifying that it passed only on KW (p < 0.05), not on the additional monotonicity criterion. The SHOULD_WORK gate was KW only, which is fine, but a reviewer may find it inconsistent that the summary table lists H-M3 as "PASS" when Dunn Q1 vs Q4 p = 1.0.

The paper does discuss this in Section 5.5, so this is minor. But the summary table (Section 5.6) could note "KW PASS; Dunn Q1 vs Q4 n.s." rather than just "PASS."
**Category**: MINOR (clarity)
**Action**: Human review — add sub-note in Table 5.6 for H-M3.

---

## Summary for Revision Agent

### FATAL Issues (0): None.

### MAJOR Issues (3):

| ID | Persona | Issue | Action Required |
|----|---------|-------|-----------------|
| AC-002 | Accuracy | Singhal 2023 citation UNVERIFIED — still in reference list with warning | Remove [UNVERIFIED] note; either verify or remove citation |
| AC-003 | Accuracy | Ji 2023 citation needs verification (arXiv:2310.19852) | Verify or flag; do not submit unverified |
| SE-001 | Skeptical Expert | FWL theorem applies to Pearson, not Spearman — paper doesn't clarify this limitation | Add qualifying sentence in 3.4 and 5.3 |

Note: BR-001 (Experiments section redundancy) is a legitimate structural issue, but because removing a section would require major rewriting beyond word-level correction, it is **downgraded to MINOR for human review** in this automated pass. The revision agent should address only the citation and FWL caveat issues.

**Updated MAJOR count: 2** (AC-002, AC-003 — citation issues; SE-001 — FWL caveat)

### MINOR Issues for Human Review (7):

1. AC-001: Add "bootstrap" qualifier to CI mentions in prose
2. AC-004: Inconsistency "~5×" (abstract) vs 4.88 (body) — consider "~4.9×"
3. AC-005: "~4.9" vs "~5" inconsistency across sections
4. BR-001: Experiments section partially redundant with Methodology
5. BR-002: Clarify bivariate 0.966 vs Dubois' 0.94 distinction
6. SE-002: VIF interpretation note for Spearman
7. SE-003: Distinguish Dubois' 0.94 from our sample's bivariate 0.966
8. SE-004: Cite ε² formula for KW
9. SE-005: H-M3 summary table note "KW PASS; Dunn n.s."

(Total MINOR count: 9 — some were renumbered from initial count of 7)

---

## Persuasiveness Check Results (R1)

| Check | Result |
|-------|--------|
| abstract_compelling | true |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | true |
| figure_1_self_explanatory | N/A (no figures embedded in .md) |
| would_continue_reading | true |
| attention_lost_at | "Section 4 (redundancy)" |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 0 |
| tone_overclaiming_found | 0 |
| missing_limitations | false (all L1-L5 from ground truth are stated) |

**Persuasiveness: CONDITIONAL PASS** — abstract and intro are engaging, limitations are disclosed. The FWL caveat (SE-001) is the main credibility risk.

---

## Agent Return Summary

```yaml
agent: "adversary"
round: "R1"
status: "COMPLETED"
fatal_count: 0
major_count: 3  # AC-002, AC-003, SE-001
minor_count: 9  # In human_review_notes
ground_truth_discrepancies: 0
persuasiveness_passed: true  # Conditional — SE-001 must be fixed
key_issues:
  - "Two unverified citations (Singhal 2023, Ji 2023) still in paper with warning markers"
  - "FWL theorem applies to Pearson only — Spearman use needs qualification"
recommendation: "REVISE — fix citations and FWL caveat, then proceed"
```
