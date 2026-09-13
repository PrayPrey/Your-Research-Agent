# Adversarial Review Changelog
**Paper:** Deduplication Produces a Contamination-Correction Benchmark Accuracy Signature
**Review Started:** 2026-08-25T20:30:00+00:00

---

## Round 1 Changes

### MAJOR Issue Fixes

**[ACC-MAJOR-001] Pile step 99K/128K ambiguity — clarifying footnote added**
- Location: Section 3 (Token-Count Matching)
- Change: Added footnote clarifying that Pile step 99,000 is the primary token-count-matched comparison point used in H-E1 and H-M3; Pile step 128,000 is used internally in H-M4's analytical simulation of the step-matched condition only.
- Rationale: Prevents reader confusion from apparent discrepancy between h-e1/04_validation.md (step 99K) and h-m4/04_validation.md (step 128K).

**[ENG-MAJOR-001] Figure 3 filename corrected**
- Location: Section 3 (Token-Count Matching paragraph), Figure Reference Summary
- Change: `fig_04_bias_decomposition.png` → `fig_03_bias_decomposition.png` in two locations.
- Rationale: Filename contained "04" while the figure is labeled Figure 3, creating inconsistency. Corrected to align filename with figure number.

**[SKP-MAJOR-001] n=4 benchmark-level non-significance disclosure added to Methodology**
- Location: Section 3 (Contamination-Accuracy Correlation Analysis)
- Change: Expanded the description of n=16 analysis to explicitly state that the benchmark-level correlation (n=4, collapsing across model sizes) yields r=0.776 but is not independently significant (p=0.224). Added acknowledgment that treating model-size replications as independent observations inflates effective sample size.
- Rationale: This disclosure existed in sections/03_methodology.md but was absent from the assembled 06_paper.md. Restores the intellectual honesty of the methodology section.

**[SKP-MAJOR-002] L6 limitation added — No formal Phase 5 baseline comparison**
- Location: Section 6 (Limitations)
- Change: Added L6 disclosing that no formal structured baseline comparison against prior contamination-mitigation methods was completed; the framework is validated informally against Biderman et al. 2023.
- Rationale: Ground truth file explicitly flagged this missing limitation.

### Sections Modified
- Section 3 (Methodology): Token-Count Matching paragraph (footnote + figure filename), Contamination-Accuracy Correlation Analysis (n=4 disclosure)
- Section 6 (Limitations): Added L6
- Figure Reference Summary: fig_03_bias_decomposition.png filename fix

### Word Count Delta
- Added: ~120 words (footnote, n=4 disclosure paragraph, L6)
- Removed: 0 words
- Net: +120 words

---

## Round 2 Changes

### New Issues Found in R2: 0 FATAL, 0 MAJOR, 1 MINOR

All primary numerical claims verified against h-e1, h-m3, h-m4, h-m2, h-m1 validation files. No discrepancies found.

**[R2-MINOR-001] Per-model-size correlation non-significance noted**
- Location: Section 5.2 (Contamination Predicts the Signature Direction)
- Change: Added parenthetical "(all non-significant at n=4)" to per-model-size correlation list.
- Rationale: At n=4 per model size, individual per-size correlations are not independently significant. Acknowledging this proactively defends against a reviewer pointing it out.

### Sections Modified
- Section 5.2: Minor parenthetical added to per-model-size correlation sentence.

### Word Count Delta
- Added: ~5 words
- Removed: 0
- Net: +5 words

---

## Final Summary

**Total Revisions Made:** 5 (4 MAJOR fixes across R1; 1 minor addition in R2)
**Sections Modified:** Methodology (Sec 3), Results (Sec 5.2), Discussion/Limitations (Sec 6), Figure Reference Summary
**Word Count Change:** ~125 words added, 0 removed

**Review Process:**
- Started: 2026-08-25T20:30:00+00:00
- Completed: 2026-08-25T21:00:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert (R1); accuracy_checker, skeptical_expert (R2)

**Files Generated:**
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md, 065_review_r2.md (per-round adversary reports)
- 06_paper_r1.md, 06_paper_r2.md (intermediate revisions)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
