# Human Review Notes

**Paper:** BiDPO: Learning Agency-Preserving Signals in Preference Data (A Negative Result)
**Generated:** 2026-08-18
**Purpose:** Minor issues NOT auto-fixed - collected for human author review

---

## Summary

| Type | Count |
|------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 2 |
| Formatting | 1 |
| **Total** | **3** |

---

## Issues

### M1: Clarity - Discussion Redundancy

**Location:** Section 6 Discussion, paragraph 1-2
**Description:** "The Training-Generation Gap" section repeats the p=0.247, d=0.016 finding already stated in Results. Consider condensing.
**Suggestion:** Focus Discussion on the "why" rather than restating the "what."

---

### M2: Clarity - Lambda Choice

**Location:** Section 3 Methodology, Training Configuration
**Description:** λ=0.5 is used but not justified. Why this value vs others?
**Suggestion:** Add brief note: "We set λ=0.5 as a balanced starting point; systematic λ sweeps are left for future work."

---

### M3: Formatting - Reference Style

**Location:** Section 7 References
**Description:** "See `06_references.bib` for full citations" is non-standard for academic papers.
**Suggestion:** Replace with proper inline citations or full bibliography.

---

## Notes for Human Author

These issues are cosmetic/clarity improvements that do not affect the scientific claims. The paper is publication-ready from a scientific accuracy standpoint.

Priority order for fixing:
1. M3 (Formatting) - most visible to reviewers
2. M2 (Clarity) - addresses potential reviewer question
3. M1 (Clarity) - nice-to-have polish
