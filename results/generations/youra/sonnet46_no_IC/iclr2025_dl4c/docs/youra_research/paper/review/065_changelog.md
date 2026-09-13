# Revision Log - Round 1

**Date**: 2026-08-04T20:05:00Z
**Input Paper**: paper/06_paper.md
**Review File**: paper/review/065_review_r1.md
**Output Paper**: paper/06_paper_r1.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-A1 | 30× vs 31× inconsistency | ACCEPT | Fixed "30×" → "31×" in Section 5.1 Figure 1 description paragraph |
| MAJOR-E1 | Scope mismatch — speculative 2-5pp outcome | ACCEPT | Replaced speculative "Expected outcome" sentence in Section 5.2 with explicit statement that H-E1 is future work, outcome empirically TBD, and marginal benefit over heuristic filters may be small |
| MAJOR-C1 | "First" novelty claim fragile | ACCEPT | Replaced "First empirical characterization of Python doctest executability at corpus scale" with "First systematic measurement of the gap between `>>>` pattern prevalence and subprocess executability in a curated Python code corpus used for LLM training" in Section 1.4 Contribution 1 |
| MAJOR-C2 | Compile-only benefit overclaim | ACCEPT | (a) Section 6.1: Replaced "The practical recommendation is clear: use compile() as the primary execution-quality gate" with "Compile-only filtering is feasible at scale and avoids the import isolation problem" and added caveat that SFT benefit remains to be confirmed by H-E1; (b) Section 6.3: Replaced "production-ready" with "pipeline-ready as a syntax-validity quality gate; its SFT quality benefit will be confirmed by H-E1" |

---

## Sections Modified

| Section | Change |
|---------|--------|
| Section 1.4 Contribution 1 | Scoped novelty claim from "First empirical characterization" to "First systematic measurement of the gap" |
| Section 5.1 (Figure 1 description) | Fixed "30×" → "31×" |
| Section 5.2 | Replaced speculative 2-5pp expected outcome with explicit future-work framing and marginal-benefit caveat |
| Section 6.1 | Replaced "The practical recommendation is clear" block with feasibility framing + H-E1 caveat |
| Section 6.3 | Replaced "production-ready" with "pipeline-ready" + SFT benefit caveat |

---

## Word Count Changes

Approximately +30 words net (Section 5.2 replacement added context; other sections were near-even swaps).

---

## Minor Issues

All MINOR issues collected in 065_human_review_notes.md — not fixed in paper per instructions.

---

# Revision Log - Round 2

**Date**: 2026-08-04T21:00:00Z
**Input Paper**: paper/06_paper_r1.md
**Review File**: paper/review/065_review_r2.md
**Output Paper**: paper/06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-N1 | Figure 2 breakdown arithmetic error (2.1% → 1.1%) | ACCEPT | Fixed "2.1%" → "1.1%" in Section 5.1 body text (line 318). Figure 2 caption did not contain the error. Verified four-category sum: 96.9% + 1.1% + 1.9% + 0.1% = 100.0% ✓ |

---

## Sections Modified

| Section | Change |
|---------|--------|
| Section 5.1 (Figure 2 description) | Fixed arithmetic error: "2.1%" → "1.1%" (106/10000 = 1.06% ≈ 1.1%) |

---

## Word Count Changes

0 words net (single number corrected).

---

## Minor Issues

Two new minor issues collected in 065_human_review_notes.md — not fixed in paper per instructions.

---

## Final Summary

**Total Revisions Made**: 5 MAJOR issues resolved across 2 rounds
**Sections Modified**: Section 1.4, 5.1, 5.2, 6.1, 6.3
**Word Count Change**: ~+30 words net (R1: +30, R2: 0)

**Review Process**:
- Started: 2026-08-04T20:00:00Z
- Completed: 2026-08-04T20:20:00Z
- Rounds: 2 (R1: structural/framing, R2: numerical verification)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (9 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)
- 06_paper_r1.md (paper after R1 revision)
- 06_paper_r2.md (paper after R2 revision)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
