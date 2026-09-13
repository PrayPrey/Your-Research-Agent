# Phase 6.5 Adversarial Review Changelog

## Round 1 Revisions

**Date**: 2026-08-26
**Source review**: 065_review_r1.md
**Input paper**: 06_paper.md
**Output paper**: 06_paper_r1.md

---

### MAJOR-1 Fix: Gao checkpoint count clarification

- **Location**: Section 5.1 body text; Section 5.5 (new note); Appendix B
- **Issue**: Section 5.1 stated "11 checkpoints" for Gao; datasets table and H-M4 regression use n=10. The discrepancy was unexplained, leaving reviewers to wonder why one checkpoint was dropped.
- **Change**:
  - Section 5.1: Replaced "across 11 checkpoints" with "across 11 KL levels available for signal characterization" and added a parenthetical explaining that the KL=0 boundary point is included for variance estimation (H-E1) but excluded from regression (H-M4), yielding n=10 paired observations.
  - Section 5.5: Added a "Note on Gao checkpoint count" paragraph explicitly reconciling the 11-level plot (Appendix B) with the 10-observation regression (H-M4), citing the KL=0 boundary exclusion rationale and the datasets table.
  - Appendix B: Updated description to clarify "11 KL checkpoints (all available levels, including the KL=0 boundary point used for signal characterization in H-E1)" and added a cross-reference explaining the n=10 regression exclusion.

---

### MAJOR-2 Fix: Section 5.5 heading numbering

- **Location**: Section 5.5 heading; Section 3.5 step list
- **Issue**: Section 5.5 heading read "Step 5: Cross-Dataset Replication (H-M4 — Replication)" but the framework (Section 3.5) defines exactly four steps, with H-M4 listed under Step 4. A "Step 5" does not exist in the defined framework.
- **Change**:
  - Section 5.5 heading changed from "## 5.5 Step 5: Cross-Dataset Replication (H-M4 — Replication)" to "## 5.5 Step 4 (Replication): Cross-Dataset Replication (H-M4 — Replication)".
  - Section 3.5: Converted the bullet list of steps to a numbered list (1–4) to make the step count explicit and prevent future proofreading drift.

---

### MAJOR-3 Fix: Novelty claim narrowing and "strong evidence" softening

- **Location**: Abstract (paragraph 3); Introduction (Contribution 1 and Contribution 3); Section 2.1 (last sentence)
- **Issue**: "The first quantitative, replicated regression characterization" is vulnerable to challenge because Gao et al. [2023] — titled "Scaling Laws for Reward Model Overoptimization" — likely contains regression analysis of overoptimization curves. The broader "first quantitative characterization" claim can fail if any slope appears in either source paper. Additionally, "strong evidence" from n=2 datasets in Contribution 3 is an overclaim relative to the Discussion's correctly hedged language.
- **Change**:
  - Abstract: Changed "the first quantitative, replicated regression characterization of how RLHF optimization degrades evaluation calibration to human judgment" to "the first regression characterization of the *normalized divergence gap* (RM_norm − gold_preference) as a function of KL budget with cross-dataset slope comparison". This claim is defensible regardless of what regression Gao et al. perform internally, because the normalized construct and cross-dataset comparison are unambiguously novel.
  - Introduction Contribution 1: Changed "the first quantitative regression characterization of proxy-gold divergence as a function of KL optimization budget" to "the first regression characterization of the normalized divergence gap (RM_norm − gold_preference) as a function of KL optimization budget with cross-dataset slope comparison".
  - Introduction Contribution 3: Changed "strong evidence this is not a model-family artifact" to "consistent evidence (n=2 datasets; further replication required to establish universality) that this is not a model-family artifact".
  - Section 2.1: Changed "enabling the first quantitative, replicated characterization of the calibration-alignment divergence curve" to "enabling the first cross-dataset characterization of the calibration-alignment divergence curve slope" — consistent narrowing.
  - Section 6.1 Finding 2: Added "(n=2 datasets; further replication required to establish universality)" parenthetical after the model-family-independent mechanism claim.

## Round 2 Revisions

**Date**: 2026-08-26
**Source review**: 065_review_r2.md
**Input paper**: 06_paper_r1.md
**Output paper**: 06_paper_r2.md

---

### MAJOR-R2-1 Fix: Durbin-Watson autocorrelation disclosure
- **Location**: Section 6.3 (Limitations)
- **Issue**: DW=0.411 shown in Appendix C but never discussed; OLS parametric CIs assume i.i.d. residuals and may be anti-conservative under autocorrelation. A methodologically trained reviewer would immediately flag this.
- **Change**: Added L5 sentence acknowledging DW=0.411 indicates positive residual autocorrelation, noting OLS parametric CI may be anti-conservative, and stating that the bootstrap CI [0.117, 0.177] (no i.i.d. assumption) independently confirms the strictly positive slope and serves as the autocorrelation-robust robustness check.

---

## Final Summary

**Total Revisions Made**: 4 MAJOR issues fixed (3 in R1, 1 in R2)
**Sections Modified**: Abstract, Introduction (Contributions 1, 3), Related Work 2.1, Methodology 3.5, Results 5.1, Results 5.5 (heading + body), Discussion 6.1, Discussion 6.3 (L5 added), Appendix B
**Human Review Notes**: 11 MINOR issues collected (not auto-fixed) — see 065_human_review_notes.md

**Review Process**:
- Started: 2026-08-26T04:00:00Z
- Completed: 2026-08-26T04:35:00Z
- Rounds: 2 (R1, R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- paper/review/065_review_summary.md (review summary)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)
- paper/review/065_review_r1.md (R1 adversary report)
- paper/review/065_review_r2.md (R2 adversary report)
- paper/review/065_review_checkpoint.yaml (final state: COMPLETED, CONDITIONAL_ACCEPT)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
