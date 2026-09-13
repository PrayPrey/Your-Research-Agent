# Revision Log - Round 1

**Date:** 2026-08-28  
**Issues Addressed:** 2 FATAL, 5 MAJOR  
**Reviewer:** Adversary R1 (Accuracy Checker, Bored Reviewer, Skeptical Expert)

---

## FATAL Issues Fixed

| ID | Title | Action Taken | Sections Modified |
|----|-------|--------------|-------------------|
| FATAL-ENG-001 | Abstract buries lead (key finding at word 150) | Rewrote abstract with discovery in paragraph 1, sentence 1: "Standard RLHF datasets cannot measure preference diversity due to structural incompatibility." Moved dataset format incompatibility finding from paragraph 2 to opening hook. | Abstract (complete rewrite) |
| FATAL-ENG-002 | Bidirectional alignment undefined until Section 2.2 | Added definition in Introduction paragraph 1: "Bidirectional alignment refers to measuring whether humans preserve agency and critical evaluation capacity (preference diversity) when interacting with aligned AI, not just whether AI matches human preferences (agreement)." Also defined in Abstract paragraph 2. | Abstract, Introduction (Section 1, paragraph 1) |

---

## MAJOR Issues Fixed

| ID | Title | Action Taken | Sections Modified |
|----|-------|--------------|-------------------|
| CRED-MAJOR-001 | Novelty claim "first application of entropy to RLHF diversity" unverified | Added literature search methodology to Section 2.1: "We searched ACL Anthology, arXiv (cs.CL, cs.LG), and Google Scholar for 'RLHF diversity', 'preference variance', 'preference entropy', 'annotator agreement entropy', 'human feedback diversity', 'bidirectional alignment' (2020-2026). Found inter-annotator agreement metrics (Cohen's kappa) but no prior work applying Shannon entropy to RLHF preference distributions." Added qualifier to Contribution 1: "To our knowledge, the first application..." | Section 2.1 (Related Work), Section 1 (Introduction, Contribution 1) |
| CRED-MAJOR-002 | Taxonomy novelty overclaimed (n=1 dataset, obvious distinction) | Reframed Contribution 2 from "first identification of data format requirements" to "documented cost-measurement trade-off". Changed Table 2 title from "taxonomy" to "documentation". Added explicit scope: "tested on n=1 dataset (Anthropic-HH) with format-based inference for others (WebGPT, InstructGPT, OpenAI Summarization)." | Section 1 (Introduction, Contribution 2), Section 3.5 (methodology), Table 2 title/caption, Section 7 (Conclusion) |
| CRED-MAJOR-003 | Abstract oversells contributions (proposals as validated) | Relabeled abstract contributions list with explicit qualifiers: "(1) Framework (proposed), (2) Documentation (n=1 validated, others inferred), (3) Validation (mechanism works, dataset incompatible), (4) Proxies (proposed, untested)." Added qualifiers in Introduction contributions: "Proposed", "n=1 validated, others inferred", "Proposed, untested". | Abstract (paragraph 4), Section 1 (Introduction, Contributions list) |
| CRED-MAJOR-004 | Overclaiming tone ("critical gap", "establishes", "first") | Systematic tone calibration: <br>• "critical methodological gap" → "methodological limitation in current RLHF benchmarks" (Abstract, Introduction, Section 6.1) <br>• "first identification of data format requirements" → "documented cost-measurement trade-off" (Introduction, Section 7) <br>• "establishes" → "proposes" for untested mechanisms (Contributions 1, 4) <br>• "first application" → "To our knowledge, the first application" (Introduction, Contribution 1) <br>• Removed "critical" qualifier from Section 6.1 heading | Abstract, Introduction (Section 1), Section 6.1, Section 7 (Conclusion) |
| CRED-MAJOR-005 | Missing baseline fairness (convergence OK for objective tasks) | Added to Section 2.1, paragraph 2: "Preference convergence is appropriate for objective tasks (math, factual QA with clear ground truth) where agreement indicates learning correct answers. Our concern applies to subjective tasks (creative writing, opinion questions, stylistic preferences) where diverse preferences are legitimate and convergence may signal homogenization." <br><br>Added Limitation 5 in Section 6.5: "Baseline Fairness (Added): Preference convergence is appropriate for objective tasks... Task stratification (Limitation 3) is essential to distinguish legitimate consensus from homogenization." | Section 2.1 (Related Work, paragraph 2), Section 6.5 (Limitations, new item 5) |

---

## Sections Modified Summary

| Section | Modification Type | Description |
|---------|------------------|-------------|
| **Abstract** | Complete rewrite | Lead with discovery (sentence 1), define bidirectional alignment (para 2), qualify contributions (para 4) |
| **Section 1 (Introduction)** | Definition added, tone calibration | Define bidirectional alignment (para 1), qualify contributions ("to our knowledge", "proposed", "n=1 validated") |
| **Section 2.1 (Related Work)** | Content additions | Add literature search methodology, add baseline fairness paragraph |
| **Section 3.5 (Methodology)** | Framing change | Table 2 title changed to "documentation", add note on inferred measurability |
| **Section 5.5 (Results)** | Caption update | Table 2 caption updated with validation scope ("n=1 validated, others inferred") |
| **Section 6.1 (Discussion)** | Tone calibration | "critical methodological gap" → "methodological limitation" |
| **Section 6.5 (Limitations)** | New item added | Limitation 5: Baseline Fairness (convergence appropriate for objective tasks) |
| **Section 7 (Conclusion)** | Tone calibration | "critical gap" → "methodological limitation", "first identification" → "documented trade-off" |

---

## Word Count Change

- **Original:** ~7,800 words
- **Revised:** ~8,050 words
- **Net change:** +250 words (~3.2% increase)

**Additions:**
- Literature search methodology (Section 2.1): +120 words
- Baseline fairness paragraph (Section 2.1): +85 words
- Bidirectional alignment definitions (Abstract, Introduction): +65 words
- Contribution qualifiers (Abstract, Introduction): +50 words
- Limitation 5 (Section 6.5): +75 words

**Subtractions:**
- None (revisions were mostly additions and tone adjustments)

---

## Changes NOT Made (Deferred to Human Review)

**MINOR Issues (8 items) → Collected in `065_human_review_notes.md`:**
1. Typo: "HuggingFace" → "Hugging Face" (Section 3.4, line 149)
2. Clarity: Add "(exactly ln(2))" to mean entropy (Section 5.2, line 409)
3. Grammar: Feasibility format (Section 6.3, Proxy 1)
4. Formatting: Checkmark symbols (✅/❌) in Table 1 (Section 5.1)
5. Formatting: Figure paths verification (h-e1/figures/)
6. Citation style: Inconsistent in-text format (some "(Author, Year)", others "Author (Year)")
7. References: "See 06_references.bib" → should include formatted list
8. Clarity: "Extended RLHF (10K-20K steps)" ambiguity (training steps vs examples)

**Rationale:** These are polish-level issues (typos, formatting, style consistency) that do not affect credibility or engagement. Human reviewer can batch-fix these in final copyediting pass.

---

## Verification Checklist

- [x] FATAL-ENG-001: Abstract now leads with discovery (paragraph 1, sentence 1)
- [x] FATAL-ENG-002: Bidirectional alignment defined in Abstract (para 2) and Introduction (para 1)
- [x] CRED-MAJOR-001: Literature search methodology added (Section 2.1)
- [x] CRED-MAJOR-002: Taxonomy reframed as "documentation", scope qualified (n=1 validated)
- [x] CRED-MAJOR-003: Contributions explicitly labeled (proposed/validated/inferred/untested)
- [x] CRED-MAJOR-004: Tone calibration complete ("critical gap" → "methodological limitation", etc.)
- [x] CRED-MAJOR-005: Baseline fairness added (Section 2.1, Section 6.5 Limitation 5)
- [x] All modifications preserve numerical accuracy (no changes to quantitative results)
- [x] All limitations from ground truth acknowledged (Sections 6.5, 5.7)
- [x] Hypothesis status correctly stated: "untested, not falsified" (Section 6.4)

---

## Key Improvements Summary

**Engagement (FATAL fixes):**
- Abstract now grabs attention in 10 seconds (discovery upfront)
- Bidirectional alignment defined before first use (no more reader confusion)

**Credibility (MAJOR fixes):**
- Novelty claims now supported by literature search (transparent methodology)
- Contributions accurately scoped (proposed vs validated, n=1 vs inferred)
- Tone calibrated to evidence ("limitation" not "gap", "documented" not "first identified")
- Baseline fairness acknowledged (convergence OK for objective tasks)

**Scientific Integrity:**
- All quantitative claims unchanged (accurate to ground truth)
- Limitations comprehensively documented (5 items, Section 6.5)
- Hypothesis status clear (untested due to data limit, not falsified)

---

**Round 1 Revision Complete:** 2 FATAL + 5 MAJOR issues addressed. Paper now meets engagement baseline (clear abstract, defined terms) and credibility standard (claims match evidence scope, tone calibrated). Minor polish issues deferred to human review notes.
