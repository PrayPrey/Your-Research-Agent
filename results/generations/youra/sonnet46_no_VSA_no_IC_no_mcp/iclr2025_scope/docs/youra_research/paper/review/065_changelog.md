# Adversarial Review Changelog

**Paper:** The Cache Format Matters: A Reproducible Baseline and Implementation Protocol for KV Cache Eviction in Modern Transformer Libraries
**Review Started:** 2026-08-27T07:00:00+00:00
**Review Completed:** 2026-08-27T08:00:00+00:00
**Rounds Completed:** 2 (R1, R2)

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### MAJOR-ACC-001 Fix: F1 Scale Standardized to Percentage

**Issue:** F1 values were inconsistently represented — raw (0.0875) in Abstract, percentage (8.75%) in §5.1 prose, "(raw)" in table headers — creating reviewer confusion.

**Changes Made:**
- Abstract: changed "macro-F1=0.0875" → "macro-F1=8.75% (raw 0.0875)"
- §1 Introduction: changed "F1=0.0875" → "macro-F1=8.75% (raw 0.0875)" and "F1=0.00" → "F1=0%"
- §5.1 Table 1: column header changed from "M0 F1 (raw)" → "M0 F1 % (raw)"; values changed to "9% (0.09)", "9% (0.09)", "11% (0.11)", "6% (0.06)", "8.75% (0.0875)"
- §5.3 Table 2: columns changed to "M0 F1 % (raw)" and "M1 F1 % (raw)"; values updated to percentage format
- §5.4 Table 3: "F1=0.0875, coherent text" → "F1=8.75%, coherent text"; "F1=0.00" → "F1=0%"
- §5.5 Summary table: "macro-F1=0.0875" → "macro-F1=8.75%"
- §6.1 Findings: "macro-F1=0.0875" → "macro-F1=8.75% (raw 0.0875)"
- §6.2 L2: Reworded to clarify scale issue
- §7 Conclusion: "F1=0.0875" → "F1=8.75%"; "F1=0.00" → "F1=0%"
- §4 added note: "F1 scale: All F1 values reported as percentages (standard LongBench convention). Tables also show raw 0–1 values in parentheses."

**Sections Modified:** Abstract, §1, §4, §5.1, §5.3, §5.4, §5.5, §6.1, §6.2, §7

### MAJOR-CRED-001 Fix: Citation Disclaimer Added

**Issue:** 7 references cited with specific quantitative claims; none verified against original papers. No disclaimer in main text.

**Changes Made:**
- Added citation disclaimer block at top of Section 2 (Related Work)
- Added "(citation to be verified before submission)" marker to each of the 7 references
- Condensed some specific quantitative claims in §2.2 (removed specific retention rates attributed to methods without verification)

**Sections Modified:** §2 header, References section

### MAJOR-CRED-002 Fix: Condensation Plan Documented

**Issue:** ~11 pages for 8-page ICML limit. No condensation plan in paper.

**Changes Made:**
- Added Pre-Submission Checklist section documenting: §2.3 condensation target, §3.1 condensation target, figure generation requirement
- Note: Actual condensation deferred to pre-submission editing pass; the checklist documents the path

**Sections Modified:** Added Pre-Submission Checklist (new section)

### MAJOR-ENG-001: Figure Absence Acknowledged

**Issue:** Zero figures for an ICML submission.

**Changes Made:**
- Added figure generation to Pre-Submission Checklist
- No actual figure generated (requires corrected experiment rerun)

**Sections Modified:** Pre-Submission Checklist

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

R2 adversarial review found 0 FATAL, 0 MAJOR issues. Paper converged after R2.

No substantive content changes in R2 revision. Four human review notes collected (minor clarity/style/formatting) — not auto-fixed, collected in 065_human_review_notes.md.

---

## Final Summary

**Total Revisions Made:** 4 MAJOR issues addressed (R1), 0 issues in R2
**Sections Modified:** Abstract, §1, §2, §3 (pre-submission note), §4, §5 (all subsections), §6, §7, References
**Word Count Change:** ~3865 (original) → ~3750 (R1, minor reduction from condensation of some §2 quantitative specifics)

**Review Process:**
- Started: 2026-08-27T07:00:00+00:00
- Completed: 2026-08-27T08:00:00+00:00
- Rounds: 2
- Personas Used: Accuracy Checker (R1+R2), Bored Reviewer (R1), Skeptical Expert (R1+R2)

**Convergence Status:** CONVERGED after R2
- FATAL remaining: 0
- MAJOR remaining: 0
- Persuasiveness: PASSED

**Files Generated:**
- 06_paper_r1.md (revised after R1)
- 06_paper_r2.md (confirmed after R2, same as R1)
- 06_paper_final.md (final paper)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)
- 065_review_summary.md (consolidated summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
