# Human Review Notes — R1

**Paper:** Generation-Free Hallucination Detection via NLI Contradiction Scoring
**Source review:** 065_review_r1.md
**Revision:** R1 (2026-03-16)
**Status:** Collected for human review; NOT applied to paper

These items were identified in the adversarial review as style, clarity, or structural issues that do not rise to Major severity or require human editorial judgment to resolve. They are collected here for a human reviewer to address before final submission.

---

## HR-1 (Style) — "Three Levels Deep" subheading reads as template artifact

**Location:** Section 1.1, subheading "The Problem: Three Levels Deep"

**Issue:** The "three levels deep" framing in the subheading reads as a template-driven construct. A reviewer who has seen many papers will recognize it as structural scaffolding rather than organic framing.

**Suggested action:** Consider removing the "three levels deep" label from the subheading (e.g., rename to "The Problem" or "The Gap") and letting the escalating three-paragraph structure speak for itself. The content is effective; the label slightly undercuts it.

---

## HR-2 (Style) — "Discriminative signal in NLI pre-training" is imprecise

**Location:** Section 6.1, sentence: "Post-hoc NLI scoring bypasses sampling dependency entirely, operating on the discriminative signal in NLI pre-training."

**Issue:** "The discriminative signal in NLI pre-training" is ambiguous — it could refer to general discriminative features or specifically the contradiction-detection capability. The paper's contribution is applying the latter to hallucination detection.

**Suggested action:** Revise to: "...operating on the contradiction-detection signal encoded during NLI pre-training." This makes the mechanism explicit and accurate.

---

## HR-3 (Clarity) — Structural ceiling derivation (p_contradictory = 0.04 → max AUROC ≈ 0.52) not shown

**Location:** Section 5.3, sentence: "The structural ceiling analysis shows the theoretical maximum AUROC for contradiction-based detection on summarization is approximately 0.52 given the proportion of summarization hallucinations that manifest as contradictions (p_contradictory ≈ 0.04 per example)."

**Issue:** The derivation linking p_contradictory = 0.04 to theoretical max AUROC ≈ 0.52 is asserted but not explained. A reviewer may question the 0.52 claim without the supporting logic.

**Suggested action:** Add a one-sentence explanation, e.g.: "If only ~4% of hallucinated examples produce contradiction signals, a detector that perfectly identifies those achieves an expected AUROC of ~0.52 over the full balanced dataset — consistent with the observed 0.530." Alternatively, place the derivation in a footnote or appendix.

---

## HR-4 (Structure) — Conclusion partially duplicates Discussion (Section 6.1)

**Location:** Section 7 (Conclusion), second paragraph beginning: "Generation-free NLI contradiction scoring achieves AUROC = 0.709..."

**Issue:** This paragraph re-states results already fully narrated in Section 5 and discussed in Section 6.1. Given the paper already exceeds the 8-page ICML limit by ~87%, this duplication is a prime trimming target.

**Suggested action:** Trim the Conclusion's result re-statement to 1-2 sentences and foreground the forward-looking takeaways (future directions, the map metaphor). The three future directions paragraph and the final "map" paragraph are the most distinctive content in Section 7 — preserve those.

---

## HR-5 (Citation) — DeBERTaV3 citation year inconsistency

**Location:** References section, entry: "[He et al., 2021] He, P., Gao, J., and Chen, W. DeBERTaV3... In *ICLR*, 2023."

**Issue:** The citation key uses year 2021 (arXiv posting date) but the venue entry reads "ICLR, 2023" (publication year). This inconsistency will cause formatting issues in any bibliography system.

**Suggested action:** Standardize to one year. Recommended: update key to [He et al., 2023] to match the publication venue (ICLR 2023), and ensure all in-text citations referencing He et al. are updated consistently (currently appears as "[He et al., 2021]" in Section 3.2).

---

## HR-6 (Minor Number) — Consider footnote on AUROC rounding

**Location:** Abstract and throughout paper (AUROC values: 0.709, 0.644)

**Issue:** Ground truth values are 0.7094 and 0.6437, rounded to 0.709 and 0.644 (3 significant figures). Rounding is correct and standard; no error. However, if a reviewer runs the numbers independently and finds 0.7094, the slight discrepancy could prompt a question.

**Suggested action:** Optional — add a footnote on first AUROC appearance: "Values rounded to 3 significant figures; ground truth: dialogue 0.7094, QA 0.6437." This is low priority but adds transparency at no cost.

---

## HR-7 (Transparency) — h-m1 gate failure not disclosed in mechanism analysis

**Location:** Section 5.2 (QA KL paradox discussion)

**Issue:** Section 5.2 presents the KL divergence paradox for QA as an analysis finding, but does not disclose that this arose from a pre-specified gate failure (h-m1: KL > 0.05 required on all tasks; QA failed with KL = 0.035). The Wilcoxon + Cohen's d indicators were used as primary mechanism confirmation after this failure. A fully transparent paper would note the original criterion was revised.

**Suggested action:** Add a footnote or parenthetical, e.g.: "The original mechanism verification criterion required KL > 0.05 on all tasks; QA failed this threshold (KL = 0.035). Wilcoxon rank-sum and Cohen's d are used as primary confirmation, with KL treated as supplementary for short-context tasks."

---

## HR-8 (Page Length) — Reduction targets for ICML submission

**Location:** Entire paper

**Issue:** The paper is approximately 15 pages against an 8-page ICML limit (~87% over). Substantial trimming is required before submission.

**Estimated reduction targets:**

| Section | Current state | Action | Est. savings |
|---------|--------------|--------|--------------|
| Section 5 (Results) | 4 figures for mechanism (Figs 5-8) | Consolidate into 1-2 panels | ~0.75 page |
| Section 6 (Discussion) | Re-states Section 5 results | Cut result re-statement; keep framework and implications | ~0.5 page |
| Section 7 (Conclusion) | Duplicates Section 6.1 | Trim to 2 focused paragraphs (per HR-4) | ~0.3 page |
| Appendix (Figure captions) | 8 standalone captions | Integrate captions into main figures; cut appendix | ~0.5 page |
| Section 1 (Introduction) | Three sub-sections with overlap | Consolidate 1.2 and 1.3 into one section | ~0.3 page |

**Target:** 8 main pages + up to 2 appendix pages. A 10-page total is achievable with moderate editing while preserving all core findings, all tables, and the key figures (Figs 1-4).

**Note:** The page estimate in the front matter has been updated in R1 to flag submission-readiness status.

---

*Collected by Revision Agent R1 | 2026-03-16*
*Source: Adversarial Review 065_review_r1.md, Part 4 (Human Review Notes)*

---

# Human Review Notes — R2

**Paper:** Generation-Free Hallucination Detection via NLI Contradiction Scoring
**Source review:** 065_review_r2.md
**Revision:** R2 (2026-03-16)
**Status:** Collected for human review; NOT applied to paper

---

## HR-R2-1 (Minor) — C2 partial hedges: two instances fixed in R2, no remaining unhedged "first" claims

**Location:** Sections 2.4 and 6.2

**Status:** Both instances were fixed in R2 (hedge "to our knowledge" inserted). No further action required on C2 unless a reviewer identifies additional unhedged novelty claims elsewhere in the paper. The fix is complete as of R2.

---

## HR-R2-2 (Editorial) — E1 front matter inconsistency: page_estimate vs. R1 fix list

**Location:** YAML front matter, `page_estimate` field; R1 changelog entry for E1

**Issue:** The `page_estimate` field reads "~15 pages (requires substantial trimming to meet 8-page ICML limit before submission; see human review notes)". The R1 changelog lists E1 as "fixed" — however, the underlying issue (actual page count vs. 8-page ICML limit) was not resolved, only the front matter language was updated. There is therefore a tension: E1 appears in the R1 "fixes applied" list, yet the paper remains substantially over the page limit.

**Suggested action for human editor:** Either (a) perform the structural trim described in HR-8 (page length reduction targets) and update the front matter to reflect a realistic post-trim page estimate, or (b) update the R1 changelog to clarify that E1 was a front matter wording fix only, not resolution of the underlying over-length issue. The current state is not an error but may confuse a reader who sees E1 as fully resolved.

---

## HR-R2-3 (Clarity) — Structural ceiling derivation still lacks explicit step in Section 5.3

**Location:** Section 5.3, sentence: "The structural ceiling analysis shows the theoretical maximum AUROC for contradiction-based detection on summarization is approximately 0.52 given the proportion of summarization hallucinations that manifest as contradictions (p_contradictory ≈ 0.04 per example)."

**Issue:** This note was originally raised as HR-3 in R1 and remains unaddressed. The derivation linking p_contradictory = 0.04 to theoretical max AUROC ≈ 0.52 is asserted without explanation. The R2 review re-flagged this as a transparency concern.

**Suggested action:** Add a one-sentence derivation, e.g.: "If only ~4% of hallucinated examples produce contradiction signals, a detector that perfectly identifies those achieves an expected AUROC of ~0.52 over the full balanced dataset — consistent with the observed 0.530." A footnote or appendix subsection is also acceptable. This is a medium-priority transparency issue that a reviewer may challenge.

---

*Collected by Revision Agent R2 | 2026-03-16*
*Source: Adversarial Review 065_review_r2.md*
