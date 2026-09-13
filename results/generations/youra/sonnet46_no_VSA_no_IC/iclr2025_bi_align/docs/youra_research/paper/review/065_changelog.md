# Revision Log — Adversarial Review Phase 6.5

---

# Revision Log — Round 1

**Date:** 2026-08-21
**Input Paper:** paper/06_paper.md
**Review File:** paper/review/065_review_r1.md
**Output Paper:** paper/06_paper_r1.md

---

## Issues Addressed

### FATAL Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| FATAL-ACC-001 | Scheme 3 ML_NLP/HCI classification count mismatch | ACCEPT | Corrected Section 5.2 table: ML_NLP 27→28, HCI 6→5. Updated "N=6 HCI papers" in Section 5.3 Unexpected Finding to "N=5 HCI papers" for consistency. |

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ENG-001 | Conclusion says "three things" but paper has four contributions | ACCEPT | Changed "We contribute three things" to "We contribute four things" in Section 7; added C4 explicitly. |
| MAJOR-CRED-001 | Overclaiming tone — "striking" used 3x for N=9 result | PARTIAL | Changed Introduction "striking story" to "notable story". Changed Section 5.3 "The directional signal is striking" to "directionally consistent with H-CitAsym". |
| MAJOR-CRED-002 | N=4 HCI denominator not made explicit in ratio discussion | ACCEPT | Added clarification in Section 5.3 Interpretation noting HCI papers with outgoing within-corpus citations. |

---

## Issues NOT Addressed

None.

---

## Sections Modified

- Section 5.2: Corrected Scheme 3 ML_NLP (27→28) and HCI (6→5) counts
- Section 5.3: Tone change, N denominator clarification, N=5 HCI correction
- Section 6.2 Limitation 4: More specific framing
- Section 7: "three" → "four", C4 added explicitly
- Introduction para 1: "striking" → "notable"

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Overall | 6,039 | ~6,129 | +90 |

---

# Revision Log — Round 2

**Date:** 2026-08-21
**Input Paper:** paper/06_paper_r1.md
**Review File:** paper/review/065_review_r2.md
**Output Paper:** paper/06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-MATH-001 | "89.4%" arithmetic not explicit in prose | ACCEPT | Changed "ML/NLP alignment papers allocate 89.4% of within-corpus outgoing citations" to "ML/NLP alignment papers allocate 42 of 47 within-corpus outgoing citations (89.4%)" in Section 5.3 Interpretation. |

---

## Issues NOT Addressed

None.

---

## Sections Modified

- Section 5.3 Interpretation: Made 42/47 arithmetic explicit for 89.4% figure

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Overall | ~6,129 | ~6,135 | +6 |

---

## Final Summary

**Total Revisions Made:** 6 (1 FATAL, 4 MAJOR from R1; 1 MAJOR from R2)
**Sections Modified:** Introduction, 5.2, 5.3, 6.2, 7
**Word Count Change:** 6,039 → ~6,135 (+96)

**Review Process:**
- Started: 2026-08-21
- Completed: 2026-08-21
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert (R1); accuracy_checker, skeptical_expert (R2)
- Convergence: CONVERGED after R2

**Files Generated:**
- paper/06_paper_r1.md (R1 revised paper)
- paper/06_paper_r2.md (R2 revised paper)
- paper/06_paper_final.md (final paper = R2)
- paper/review/065_review_r1.md (R1 adversary report)
- paper/review/065_review_r2.md (R2 adversary report)
- paper/review/065_review_summary.md (consolidated review)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
