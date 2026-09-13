# Phase 6.5 Changelog

## Round 1 Revisions

### MAJOR-1: Decimal precision
- Changed: H-E1 results table (lines 246-249 in original)
- Before: r=0.578, CI [0.357, 0.738]; r=0.424, CI [0.165, 0.628]; r=0.444, CI [0.189, 0.643]
- After: r=0.58, CI [0.36, 0.74]; r=0.42, CI [0.17, 0.63]; r=0.44, CI [0.19, 0.64]
- Also standardized H-M2 subtask r values to 2 decimals (0.153->0.15, 0.148->0.15, 0.222->0.22)
- Also standardized H-M3 r values to 2 decimals (-0.005->-0.01, -0.147->-0.15)
- Reason: Consistency in decimal precision throughout paper

### MAJOR-2: Missing CI for H-M1
- Added: CI and p-value columns to H-M1 results table
- Location: Results Section H-M1
- Content: r(TruthfulQA, MMLU) = 0.19, 95% CI [−0.09, 0.44], p=0.19
- Reason: Match rigor of H-E1 reporting

### MAJOR-3: H-M2 p-value disclosure
- Added: Explicit statement about non-significant p-value
- Location: Results Section H-M2, after the main table
- Content: "While this correlation is not statistically significant (p=0.26), the low magnitude (r=0.16) supports our interpretation of near-orthogonality. The gate condition (r < 0.7) is satisfied regardless of statistical significance—the correlation's magnitude, not its p-value, determines whether the dimensions are distinct."
- Also added p-value column to H-M2 table showing p=0.26
- Reason: Honesty about statistical significance; prevents misleading readers

## Round 2 Verification

No revisions required. All R1 fixes verified correct. Deep numerical cross-check confirmed all paper values match Phase 4 sources.

---

## Final Summary

**Total Revisions Made**: 3 MAJOR fixes
**Sections Modified**: Results (H-E1, H-M1, H-M2, H-M3)
**Word Count Change**: +47 words

**Review Process**:
- Started: 2026-08-24
- Completed: 2026-08-24
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
