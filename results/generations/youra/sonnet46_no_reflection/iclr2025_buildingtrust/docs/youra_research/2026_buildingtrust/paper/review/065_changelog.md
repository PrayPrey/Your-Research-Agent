# Phase 6.5 Adversarial Review — Changelog

**Paper:** Adversarial Fragility and Calibration Are Anticorrelated After Capability Control
**Review Version:** v2.0 (Three-Persona)
**Started:** 2026-05-12T17:00:00

---

# Revision Log — Round 1

**Date:** 2026-05-12T17:15:00
**Input Paper:** paper/06_paper.md
**Review File:** paper/review/065_review_r1.md
**Output Paper:** paper/06_paper_r1.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-CRED-001 | Abstract/conclusion overgeneralize to "trust failure modes" | ACCEPT | Narrowed abstract final sentence to "adversarial fragility and calibration are positively coupled after capability control"; narrowed Section 2.4 positioning; scoped conclusion to RI-ECE dimension throughout |
| MAJOR-CRED-002 | Conclusion tone overclaims ("precondition for alignment design") | ACCEPT | Replaced with "motivates empirical testing of cross-dimension relationships as a complement to alignment method development" |
| MAJOR-CRED-003 | arc_challenge circularity unacknowledged | ACCEPT | Added L7 to Section 6.2; added forward reference in Section 3.3 |
| MAJOR-ENG-001 | Figure 1 doesn't convey key finding | PARTIAL | Added caption note in Section 3.4: "Figure 1 shows the RI distribution; the central finding (RI–ECE anticorrelation) is visualized in Figure 4" — full figure restructure deferred to human review |
| MAJOR-ENG-002 | Section 5.2 Key Observation 2 undermines contribution | ACCEPT | Reframed: similarity to PC1 confirms robust anticorrelation pattern and motivates training-regime interpretation; removed "largely capability-mediated" framing |
| MAJOR-ACC-001 | Mistral p-value ambiguity | ACCEPT | Added raw p-value column to Section 5.3 table; added prose clarification "raw p=0.173, Holm p=0.519; exploratory only" |

### MINOR Issues → Human Review Notes

| ID | Title | Action |
|----|-------|--------|
| HRN-001 | Bold markdown in abstract | Collected in human_review_notes.md |
| HRN-002 | Small-n families listed alongside major ones (style) | Collected in human_review_notes.md |
| HRN-003 | "visually confirms" passive phrasing | Collected in human_review_notes.md — changed to "provides visual confirmation" during revision |

---

## Sections Modified

| Section | Change |
|---------|--------|
| Abstract | Narrowed scope claim (CRED-001) |
| Section 2.4 | Narrowed positioning claim (CRED-001) |
| Section 3.3 | Added arc_challenge circularity note + L7 forward reference (CRED-003) |
| Section 3.4 | Added Figure 1 vs Figure 4 caption note (ENG-001) |
| Section 5.2 | Reframed Key Observation 2 (ENG-002) |
| Section 5.3 | Added raw p-value column + Mistral clarification prose (ACC-001) |
| Section 6.2 | Added L7 — ARC-Challenge Circularity (CRED-003) |
| Section 6.3 | Narrowed broader impact scope (CRED-001) |
| Section 7 | Softened "precondition" language; scoped to RI-ECE (CRED-002) |

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | ~150 | ~160 | +10 |
| Methodology | ~520 | ~560 | +40 |
| Results | ~580 | ~620 | +40 |
| Discussion | ~520 | ~560 | +40 |
| Conclusion | ~370 | ~390 | +20 |
| **Total** | ~3820 | ~4010 | **+190** |

---

## Issues NOT Addressed

*None — all 6 MAJOR issues addressed (5 accepted, 1 partial).*

---

# Revision Log — Round 2

**Date:** 2026-05-12T17:35:00
**Input Paper:** paper/06_paper_r1.md
**Review File:** paper/review/065_review_r2.md
**Output Paper:** paper/06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

*None found in R2 — paper_r2 is identical to paper_r1.*

### MINOR Issues → Human Review Notes

| ID | Note | Action |
|----|------|--------|
| HRN-004 | ARC-Challenge capitalization inconsistency | Collected in human_review_notes.md |
| HRN-005 | Partial correlation notation inconsistency | Collected in human_review_notes.md |

---

## Sections Modified

*None — R2 numerical verification found zero discrepancies. No changes required.*

---

## Word Count Changes

*Unchanged from R1: ~4010 words.*

---

## R2 Numerical Verification Summary

- 21 numerical claims verified against Phase 4/5 source files
- Zero discrepancies found
- All R1 fixes confirmed correctly applied

---

## Final Summary (v2.0)

**Total Revisions Made:** 9 section modifications (all in R1)
**Sections Modified:** Abstract, Sections 2.4, 3.3, 3.4, 5.2, 5.3, 6.2, 6.3, 7
**Word Count Change:** ~3820 → ~4010 (+190)

**Review Process:**
- Started: 2026-05-12T17:00:00
- Completed: 2026-05-12T17:45:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review — 5 items)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)

---
