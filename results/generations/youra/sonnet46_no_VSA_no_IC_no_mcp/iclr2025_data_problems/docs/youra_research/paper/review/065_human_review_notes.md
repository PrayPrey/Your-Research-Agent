# Human Review Notes
> **Purpose:** Minor issues collected during adversarial review for human review. NOT auto-fixed.

**Date:** 2026-08-25T20:30:00+00:00
**Rounds Completed:** R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 1 |
| Formatting | 0 |
| Citation | 1 |

---

## Round 1 Issues

### Style

1. **Section 5.3** — "a 17% relative improvement in contamination signal recovery": The relative framing (17%) may be perceived as overclaiming relative to the absolute gain of Δr=+0.093. Consider also stating the absolute: "a Δr=+0.093 (17% relative) improvement." Both framings are mathematically correct; adding the absolute makes the claim more defensible.

2. **Section 1 (Abstract)** — The phrase "Our findings reframe deduplication's benchmark effects from a uniform quality improvement to a selective contamination correction" is accurate and compelling but could be tightened to "reframe deduplication as a selective contamination corrector, not a uniform quality booster."

### Clarity

1. **ACC-MINOR-001** — Section 5.2 presents n=16 as the observations count in the Results table, but the Methodology section (after R1 fix) now discloses n=4 non-significance. The Results section should add a brief parenthetical "(see Section 3 for discussion of n=4 benchmark-level analysis)" to cross-reference the disclosure.

### Citation

1. **SKP-MINOR-001** — Golchin & Surdeanu (2023) reference: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models. arXiv preprint." — arXiv ID is missing. Full citation should include arXiv:2308.08493 (based on the paper's known identifier). Verify before camera-ready.

---

## Recommended Priority

1. **Citation**: Fix Golchin & Surdeanu arXiv ID (required for publication)
2. **Clarity**: Add cross-reference in Section 5.2 to methodology n=4 discussion
3. **Style**: Consider adding absolute Δr alongside relative % in Section 5.3

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience.*
