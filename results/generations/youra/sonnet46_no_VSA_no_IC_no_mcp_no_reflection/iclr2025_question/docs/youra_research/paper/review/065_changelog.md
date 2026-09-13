# Adversarial Review Changelog

**Paper:** When Consistency Is Not Uncertainty...
**Review started:** 2026-08-31T07:00:00+00:00

---

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

### MAJOR-AC-001: Figure Numbering Conflict — FIXED

**Issue:** Two distinct figures were both labeled "Figure 1" — `smc_nli_distribution.png` in Section 3 and `auroc_comparison.png` in Section 5.

**Fix applied:**
- Section 3 Overview: `smc_nli_distribution.png` → **Figure 3**
- Section 5 Primary Result: `auroc_comparison.png` → **Figure 1** (no change)
- Section 5 ROC Curve: `roc_curves.png` → **Figure 2** (no change; was already Figure 2)
- Section 5 Mechanism Analysis: `smc_nli_distribution.png` → **Figure 3** (clarified with "corresponding to Section 3")
- Section 5 Dual-Metric: `nli_vs_embed_scatter.png` → **Figure 4** (added "confirming the shared failure mode")

Final figure assignment:
- Figure 1: auroc_comparison.png (AUROC bar chart — primary result)
- Figure 2: roc_curves.png (ROC curves)
- Figure 3: smc_nli_distribution.png (SMC-NLI score distribution by label)
- Figure 4: nli_vs_embed_scatter.png (SMC-NLI vs SMC-Embed scatter)

**Sections modified:** Section 3 (Overview), Section 5 (all figure references)

---

### MAJOR-AC-002: [CITATION NEEDED] Placeholder Removed + Novelty Claim Softened — FIXED

**Issue:** 
1. `[CITATION NEEDED: any paper discussing RLHF effects on UQ]` placeholder present in submitted text.
2. "first direct empirical evidence" claim without verified citation support.

**Fix applied:**
- Positioning paragraph (Section 2): Replaced `[CITATION NEEDED...]` sentence with: "To our knowledge, no prior work has explicitly characterized the stochastic hallucination vs. systematic confabulation distinction as a necessary regime prerequisite for sampling-based hallucination detection, or provided empirical evidence of this distinction via dual-metric (NLI + embedding) evaluation with independently verified implementation correctness. While related work discusses RLHF effects on output distributions [Ouyang et al., 2022; Bai et al., 2022], the downstream implication for sampling-based uncertainty quantification has not been systematically investigated."
- Related Work, RLHF subsection final sentence: "Our work provides the first direct empirical evidence" → "To our knowledge, our work provides the first direct empirical evidence in the context of hallucination detection"

**Sections modified:** Section 2 (Related Work — Positioning, RLHF subsection)

---

### MAJOR-BR-001: Section 4 Redundancy Reduced — FIXED

**Issue:** Section 4 (Experimental Setup) duplicated content from Section 3 (Methodology): dataset description, sampling parameters, implementation validation details.

**Fix applied:** Restructured Section 4 to:
- Keep the 4 nested questions (Q1-Q4) — the organizing logic of the section
- Replace duplicated methodology with a forward reference: "Full methodology and implementation details are described in Section 3."
- Keep hardware spec (5× H100) — not in Section 3
- Keep Evaluation Protocol and Baselines — metric framing specifics not duplicated in Section 3
- Remove: redundant dataset subsection, redundant sampling params, redundant Implementation Validation subsection

**Estimated word reduction:** ~180 words removed from Section 4.

**Sections modified:** Section 4 (Experimental Setup)

---

## MINOR Issues (collected — NOT auto-fixed)

See 065_human_review_notes.md for 7 MINOR issues collected from R1.

---

## Round 2 Revisions (06_paper_r1.md → 06_paper_r2.md)

**No FATAL or MAJOR issues found in R2.** Paper content unchanged from R1.

06_paper_r2.md = 06_paper_r1.md (identical — R2 revision is a no-op).

R2 confirmed all numerical claims verified: 0 discrepancies, 0 mathematical impossibilities, 0 baseline fairness issues.

2 additional MINOR items collected (see 065_human_review_notes.md, Round 2 section).

---

## Final Summary

**Total Revisions Made:** 3 MAJOR fixes (R1)
**Sections Modified:** Section 2 (Related Work), Section 3 (Overview figure ref), Section 4 (Experimental Setup), Section 5 (all figure refs)
**Word Count Change:** ~180 words removed (Section 4 deduplication)

**Review Process:**
- Started: 2026-08-31T07:00:00+00:00
- Completed: 2026-08-31T07:45:00+00:00
- Rounds: 2 (R1 + R2)
- Personas: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_r1.md (R1 revision)
- 06_paper_r2.md (R2 revision — identical to R1, no MAJOR issues)
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (9 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md, 065_review_r2.md (adversary reports)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
