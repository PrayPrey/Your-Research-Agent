# Revision Log - Round 1

**Date**: 2026-07-30
**Input Paper**: paper/06_paper.md
**Review File**: paper/review/065_review_r1.md
**Output Paper**: paper/06_paper_r1.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| ACC-MAJOR-001 | N=299 in section file | ACCEPT | Fixed sections/04_experiments.md Section 4.2: "N=299 matched models" → "N=297 matched models" (compiled paper already correct) |
| ACC-MAJOR-002 | Fisher z formula notation | ACCEPT | Fixed formula in Section 3.1 to show separate denominators: √(1/(N−3) + 1/(N−4)); added clarifying text explaining N−4 accounts for one covariate (k=1) |
| CRED-MAJOR-001 | Conclusion drops "to our knowledge" | ACCEPT | Added hedge to Section 7: "Our work provides, to our knowledge, the first direct application..." Also fixed in sections/07_conclusion.md |

---

## Issues NOT Addressed (MINOR → human_review_notes)

| ID | Title | Location |
|----|-------|----------|
| MINOR-1 | Contribution (4) header framing too strong for null result | Style note in 065_human_review_notes.md |
| MINOR-2 | Rounding inconsistency 49%/76% vs 49.3%/76.3% | Style note in 065_human_review_notes.md |
| MINOR-3 | clawrxiv citation format needs verification | Style note in 065_human_review_notes.md |
| MINOR-4 | N=321 vs N=300 unexplained across sections | Clarity note in 065_human_review_notes.md |
| MINOR-5 | BBQ forward reference missing in Section 2.1 | Clarity note in 065_human_review_notes.md |
| MINOR-6 | Tu et al. 2024 in section file but not compiled paper | Clarity note in 065_human_review_notes.md |

---

## Sections Modified

- **Section 3.1** (compiled paper + section file implicitly): Fisher z formula clarified with separate N−3 / N−4 denominators and explanatory text
- **Section 7** (compiled paper): "to our knowledge" added to first-application claim
- **sections/04_experiments.md**: N=297 corrected (was N=299)
- **sections/07_conclusion.md**: "to our knowledge" added (mirrors compiled paper fix)

---

## Word Count Changes

| Section | Change |
|---------|--------|
| Section 3.1 | +~20 words (formula note + explanatory text for N−3/N−4) |
| Section 7 | +4 words ("to our knowledge") |
| Total | ~+24 words |

---

# Revision Log - Round 2

**Date**: 2026-07-30
**Input Paper**: paper/06_paper_r1.md
**Review File**: paper/review/065_review_r2.md
**Output Paper**: paper/06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MATH-MAJOR-001 | Fisher z formula mismatch | ACCEPT | Changed formula from independent-samples √(1/(N−3)+1/(N−4)) to same-sample √(2/(N−3)); added Steiger (1980) citation and justification |

### MINOR Issues

Not auto-fixed; carried to human_review_notes.

---

## Sections Modified

- Section 3.1: Fisher z formula corrected to same-sample form
- References: Added Steiger (1980)

## Word Count Changes

| Section | Change |
|---------|--------|
| Section 3.1 | ~+30 words (formula + justification text) |
| References | +1 entry (~20 words) |
| Total | ~+50 words |

---

## Final Summary

**Total Revisions Made:** 4 MAJOR issues fixed across 2 rounds
**Sections Modified:** Section 3.1, Section 7, References, sections/04_experiments.md, sections/07_conclusion.md
**Word Count Change:** ~+74 words total

**Review Process:**
- Started: 2026-07-30
- Completed: 2026-07-30
- Rounds: 2 (R1, R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper)
- paper/review/065_review_summary.md (review summary)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
