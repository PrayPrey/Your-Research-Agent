# Adversarial Review Report — Round 1

**Paper:** When Consistency Is Not Uncertainty: Sampling-Based Hallucination Detection Fails Under Systematic Confabulation in Instruction-Tuned LLMs
**Round:** R1 — Accuracy and Engagement
**Date:** 2026-08-31
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Summary (from 065_ground_truth.yaml + 04_validation.md)

| Metric | Ground Truth | Paper Claims | Match |
|--------|-------------|--------------|-------|
| SMC-NLI AUROC | 0.4933 | 0.4933 | ✅ |
| SMC-Embed AUROC | 0.4859 | 0.4859 | ✅ |
| Mean SMC-NLI (correct) | 0.6236 | 0.6236 | ✅ |
| Mean SMC-NLI (hallucinated) | 0.6299 | 0.6299 | ✅ |
| Gap | 0.006 | 0.006 | ✅ |
| SMC-NLI std | 0.3388 | 0.3388 | ✅ |
| N questions | 1000 | 1000 | ✅ |
| N samples total | 10,000 | 10,000 | ✅ |
| NLI pairs | 45,000 | 45,000 | ✅ |
| Unit tests | 14/14 | 14/14 | ✅ |
| Tasks completed | 15/15 | 15/15 | ✅ |

**Pre-computed discrepancies: 0. All numerical claims match ground truth exactly.**

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| FATAL | 0 | — |
| MAJOR | 3 | Must fix |
| MINOR (human review) | 7 | Collected for human review |

**Recommendation:** MAJOR_REVISION (fixable without new experiments)

---

## PERSONA 1: ACCURACY CHECKER

*Role: Fact-checker and claim verifier. Focus: numerical consistency, methodology accuracy, baseline fairness.*

### AC-FINDINGS

**All quantitative claims verified against ground truth — no numerical discrepancies found.**

However, the following claim-evidence issues require attention:

#### MAJOR-AC-001: Figure 1 Caption/Content Mismatch

**Location:** Section 5 (Results), line "Figure 1 (smc_nli_distribution.png)"

**Issue:** Section 3 (Methodology Overview) introduces "Figure 1" as `smc_nli_distribution.png` ("Distribution of SMC-NLI scores split by label"). Section 5 (Results, Primary Result) introduces "Figure 1" as `auroc_comparison.png` ("AUROC comparison across SMC-NLI, SMC-Embed, and the random baseline"). Two different figures are both labeled "Figure 1."

**Evidence:**
- Section 3: "**Figure 1** (smc_nli_distribution.png): Distribution of SMC-NLI scores split by label..."
- Section 5: "**Figure 1** (auroc_comparison.png) shows the AUROC comparison..."

**Impact:** A reviewer cannot determine which figure is actually Figure 1. This is a concrete internal contradiction that will cause rejection if uncorrected.

**Required fix:** Assign distinct figure numbers. Logical order: Figure 1 = auroc_comparison.png (primary result), Figure 2 = roc_curves.png, Figure 3 = smc_nli_distribution.png, Figure 4 = nli_vs_embed_scatter.png. Update all in-text references accordingly.

**Severity: MAJOR** — direct contradiction in figure numbering across sections.

---

#### MAJOR-AC-002: "First Direct Empirical Evidence" Overclaim Without Citation Search

**Location:** Section 2 (Related Work), final paragraph: "Our work provides the *first direct empirical evidence* of this effect..."

**Issue:** The claim "first direct empirical evidence" is made without a thorough citation search. Ground truth notes: `citations_verified: 0 — all INFERRED` and explicitly flags `[CITATION NEEDED: any paper discussing RLHF effects on UQ]`. If any paper exists showing RLHF models produce more consistent outputs (even as a side observation), the "first" claim is false.

**Evidence from ground truth:**
```yaml
unverified:
  - claim: "Any paper explicitly discussing RLHF effects on UQ — marked [CITATION NEEDED] in Related Work"
    status: "CITATION_NEEDED"
```

The paper itself contains `[CITATION NEEDED]` in the text (Section 2, positioning paragraph), which is a direct admission that the "first" claim may not hold.

**Impact:** A skeptical reviewer will immediately search for this paper. If found, the novelty claim collapses. If not found, the [CITATION NEEDED] in the submitted text is a submission error that triggers rejection on its own.

**Required fix:** Either (a) find and cite the relevant paper and soften the novelty claim to "to our knowledge, no prior work has systematically characterized..." or (b) remove the [CITATION NEEDED] placeholder and use appropriately hedged language. The [CITATION NEEDED] text **must not appear in the submitted paper**.

**Severity: MAJOR** — submission-blocking placeholder text present; novelty claim potentially unsupported.

---

#### MINOR-AC-003: Binom(10,2) = 45 — Confirm Explicit

**Location:** Section 3 (SMC-NLI Scoring), formula

**Issue:** The formula uses $\binom{N}{2} = 45$ for N=10. This is correct (10×9/2 = 45). No error, but worth confirming the claim "45,000 NLI pairs" = 1000 questions × 45 pairs is explicitly stated and consistent. It is stated in Section 4, consistent. Mark as PASS — no action needed.

*Collected for completeness. No action required.*

---

#### MINOR-AC-004: Temperature Citation Consistency

**Location:** Section 3 (LLM Sampling), "Temperature=0.7 matches the setting used in SelfCheckGPT [Manakul et al., 2023]"

**Issue:** SelfCheckGPT (arXiv:2303.08896) uses temperature=1.0, not 0.7, in their main experiments. The claim that T=0.7 "matches" Manakul et al. may be inaccurate. This is worth verifying against the actual paper.

**Impact if wrong:** Minor credibility issue — the design rationale for T=0.7 loses its citation support.

**Required fix (human review):** Verify what temperature Manakul et al. 2023 actually use. If T=1.0, change to "We use temperature=0.7, within the sampling regime used by prior work, to balance diversity and coherence."

*Collected as MINOR — requires human verification.*

---

## PERSONA 2: BORED REVIEWER

*Role: Busy NeurIPS reviewer with 5 papers today. Focus: engagement, clarity, hook quality, attention.*

### BR-FINDINGS

**Engagement Assessment:**
- Would I continue reading after abstract? **YES** — the abstract is unusually direct and leads with a concrete result (AUROC=0.4933).
- Problem clear in 1 minute? **YES** — the opening paragraph of Introduction is excellent. The "detector that passes every check / AUROC=0.4933" hook is memorable and specific.
- Novelty clear in 2 minutes? **PARTIAL** — the regime distinction (stochastic hallucination vs systematic confabulation) is clear, but the novelty claim is muddied by [CITATION NEEDED] in the Related Work section, which a reader sees.
- Figure 1 self-explanatory? **CANNOT ASSESS** — two different files are called Figure 1 (MAJOR-AC-001 above). This needs resolution before this check can pass.
- Would I continue reading? **YES**
- Attention lost at? **Section 4 (Experimental Setup)** — the setup section partially repeats content from Section 3 (Methodology). The subsections "Model and Setup," "Dataset," "Implementation Validation" all re-cover ground already covered in Section 3. This is a common paper structure problem that signals padding.

#### MAJOR-BR-001: Section 4 Redundancy Weakens Paper

**Location:** Section 4 (Experimental Setup) — particularly subsections "Model and Setup," "Dataset," "Implementation Validation"

**Issue:** Section 4 largely repeats content from Section 3. Examples:
- Section 3 Dataset: "N=1000 questions (500 correct, 500 hallucinated), drawn with seed=42"
- Section 4 Dataset: "We draw a stratified sample of N_eval=1000 questions (500 correct, 500 hallucinated) using sklearn...with seed=42"
- Section 3 Implementation: "14 unit tests covering..."
- Section 4 Implementation: "Unit tests (14/14): All tests covering...pass"

**Impact:** For a bored reviewer, 1.5 pages of repeated setup signals the paper is artificially inflated. It reduces trust and causes skimming, which means important content in later sections gets missed.

**Required fix:** Section 4 should contain only what is NOT in Section 3 — specifically, the four nested experimental questions (Q1-Q4) and the hardware spec (5× H100). The full sampling/dataset/implementation details belong exclusively in Section 3. This would cut ~0.5 pages from Section 4 and tighten the paper.

**Severity: MAJOR** — structure inefficiency signals low quality to reviewers and causes attention loss.

---

#### MINOR-BR-002: Abstract Length

**Location:** Abstract

**Issue:** The abstract is 220+ words. ICML 2025 typically expects abstracts ~150-180 words. The current abstract is dense but could be trimmed. The last two sentences about infrastructure (C4) can be shortened.

*Collected as MINOR for human review.*

---

#### MINOR-BR-003: "Confidently Consistent" Not Defined Before Use

**Location:** Section 5 (Mechanism Analysis): "The model is 'confidently consistent' regardless of factual accuracy."

**Issue:** The phrase appears here without prior definition. The formal terms "stochastic hallucination" and "systematic confabulation" are defined in Section 1; "confidently consistent" is a third informal term that adds confusion. Should be replaced with "systematically confabulating."

*Collected as MINOR for human review.*

---

#### MINOR-BR-004: Discussion Section 6 Organization

**Location:** Section 6 (Discussion)

**Issue:** Discussion has 5 subsections but no clear hierarchy. "The Systematic Confabulation Regime" and "Alternative Explanation" are both interpretive — they could be combined under one heading "Interpreting the Failure." "Broader Impact" is very short (2 paragraphs) and could be merged with Conclusion.

*Collected as MINOR for human review — structural suggestion.*

---

### Persuasiveness Checks

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Leads with specific numbers and a concrete setup |
| Problem clear in 1 minute? | PASS | Opening paragraph is excellent |
| Novelty clear in 2 minutes? | PARTIAL FAIL | [CITATION NEEDED] placeholder undermines novelty claim |
| Figure 1 self-explanatory? | CANNOT ASSESS | Figure numbering conflict (MAJOR-AC-001) |
| Would continue reading? | YES | |
| Attention lost at? | Section 4 | Repetition of Section 3 content |
| False novelty claims? | 1 | "first direct empirical evidence" + [CITATION NEEDED] |
| Unfair baseline comparisons? | 0 | |
| Overclaims? | 0 | Negative result paper — if anything, appropriately hedged |
| Missing limitations? | NO | L1-L4 are well articulated |
| Tone overclaiming? | 0 | |

**Persuasiveness: PARTIAL FAIL** — blocked by figure numbering issue and [CITATION NEEDED] placeholder.

---

## PERSONA 3: SKEPTICAL EXPERT

*Role: Domain expert looking for holes. Focus: novelty, baseline fairness, missing limitations.*

### SE-FINDINGS

**Initial Assessment:** This is a well-executed negative result paper. The dual-metric design and mechanism verification are genuine methodological strengths. However, there are credibility issues to address.

#### MINOR-SE-001: "Systematic Confabulation" — Prior Use?

**Location:** Section 1 and throughout

**Issue:** The term "systematic confabulation" is used as if coined by this paper. However, "confabulation" in the LLM context has appeared in prior literature (e.g., Ji et al. 2023 Survey on Hallucination). While the specific regime framing may be novel, the term itself is not coined here. A careful reviewer will check.

**Required consideration (human review):** Add a footnote or sentence: "We use 'systematic confabulation' to describe..." and acknowledge if the term has prior usage in adjacent contexts.

*Collected as MINOR — terminology credit issue.*

---

#### MINOR-SE-002: Missing Statistical Test

**Location:** Section 5 (Primary Result), AUROC values

**Issue:** The paper reports AUROC=0.4933 and 0.4859 without a significance test against 0.50. For a negative result paper, showing these are not significantly different from chance strengthens the claim. The standard approach is a DeLong test or bootstrap CI.

**Required consideration (human review):** Add bootstrap 95% confidence intervals around both AUROC values. Expected to confirm they span 0.50, confirming chance performance. This is minor because the values are so close to 0.50 (within 0.01) that significance is obvious, but reviewers may ask.

*Collected as MINOR — statistical rigor suggestion.*

---

#### MINOR-SE-003: N=10 Samples — Sensitivity Analysis Missing

**Location:** Section 3 (LLM Sampling): "N=10 stochastic samples per question"

**Issue:** The paper follows Kuhn et al. (N=10) but does not ablate N. With systematic confabulation, is N=10 enough to observe the high-consistency pattern, or would N=20 reduce variance and perhaps reveal a small signal? A brief ablation (N=5, N=10, N=20) would strengthen the claim that the null result is robust to this hyperparameter.

**Required consideration (human review):** Given this is a negative result, a sensitivity analysis on N strengthens the claim. However, this requires new experiments — classify as future work if out of scope.

*Collected as MINOR — suggests future work note is already present.*

---

#### MINOR-SE-004: Lin et al. 2024 Citation Detail

**Location:** Section 2 (Related Work): "Lin et al. [2024] conducted a systematic comparison..."

**Issue:** Lin et al. 2024 is referenced in the body but the BibTeX key `Lin2024Generating` is listed in References section — verify this matches the correct paper (arXiv:2305.19187). The paper title in References ("Generating with Confidence") matches the citation context. This appears correct.

*No action needed — verified consistent.*

---

**Overall Novelty Assessment:** The regime distinction is genuine and useful. The negative result is clean and well-attributed. The main novelty concerns are (1) the [CITATION NEEDED] placeholder that directly admits potential prior work on RLHF+UQ, and (2) the figure numbering inconsistency that signals careless preparation. Neither undermines the scientific contribution, but both signal to reviewers that the paper wasn't carefully proofread before submission.

---

## Summary of Issues

### FATAL Issues: 0

None found. All quantitative claims match ground truth. Core scientific contribution is sound.

### MAJOR Issues: 3

| ID | Location | Issue | Required Action |
|----|----------|-------|----------------|
| MAJOR-AC-001 | Sections 3 & 5 | Two figures both labeled "Figure 1" | Renumber all figures consistently |
| MAJOR-AC-002 | Section 2, Related Work | [CITATION NEEDED] placeholder in submitted text + "first direct empirical evidence" overclaim | Remove placeholder, soften novelty claim |
| MAJOR-BR-001 | Section 4 | Section 4 duplicates Section 3 content | Restructure Section 4 to remove redundancy |

### MINOR Issues (collected for human review): 7

| ID | Category | Location | Issue |
|----|----------|----------|-------|
| MINOR-AC-004 | clarity | Section 3 | T=0.7 "matches" Manakul — verify actual temperature used |
| MINOR-BR-002 | formatting | Abstract | ~220 words — consider trimming to ICML norm |
| MINOR-BR-003 | style | Section 5 | "confidently consistent" — undefined third term |
| MINOR-BR-004 | style | Section 6 | Discussion subsection organization could be tightened |
| MINOR-SE-001 | clarity | Throughout | "systematic confabulation" — add prior usage acknowledgment |
| MINOR-SE-002 | clarity | Section 5 | Bootstrap CIs on AUROC values would strengthen negative result |
| MINOR-SE-003 | clarity | Section 3 | N=10 sensitivity analysis missing — note as future work |

---

## Ground Truth Verification Log

All claims cross-checked against `h-e1/04_validation.md` and `paper/065_ground_truth.yaml`:
- ✅ AUROC values: exact match
- ✅ Mean SMC scores per label: exact match
- ✅ Gap value: exact match
- ✅ SMC-NLI std: exact match
- ✅ Sample counts: exact match
- ✅ Test counts: exact match
- ✅ Infrastructure counts (10,000 samples, 45,000 pairs): exact match

**No numerical discrepancies found.**

---

## Summary for Revision Agent

**Priority 1 (FATAL — none):** No fatal issues to fix.

**Priority 2 (MAJOR — fix all):**
1. **Figure numbering:** Assign unique numbers to all 4 figures. Figure 1=auroc_comparison.png, Figure 2=roc_curves.png, Figure 3=smc_nli_distribution.png, Figure 4=nli_vs_embed_scatter.png. Fix all in-text references across Sections 3, 5.
2. **[CITATION NEEDED] placeholder:** Remove from Related Work. Replace the positioning paragraph with hedged language: "To our knowledge, no prior work has explicitly characterized the stochastic hallucination vs. systematic confabulation distinction as a regime prerequisite for sampling-based detection, or provided empirical evidence via dual-metric evaluation with implementation correctness verification."
3. **Section 4 redundancy:** Remove from Section 4 any content already in Section 3 (dataset description, implementation validation details). Keep only: the 4 nested questions (Q1-Q4), hardware spec, and evaluation protocol specifics not in Section 3.

**Priority 3 (MINOR — collect in human_review_notes.md):**
- All 7 MINOR items above — do NOT auto-fix.

**Return summary:**
```yaml
agent: adversary_r1_inline
round: R1
status: COMPLETED
fatal_count: 0
major_count: 3
minor_count: 7
ground_truth_discrepancies: 0
persuasiveness_passed: false  # blocked by figure numbering and [CITATION NEEDED]
recommendation: MAJOR_REVISION
key_blockers:
  - "Figure 1 numbering conflict (Sections 3 and 5)"
  - "[CITATION NEEDED] placeholder present in submitted text"
  - "Section 4 redundancy with Section 3"
```
