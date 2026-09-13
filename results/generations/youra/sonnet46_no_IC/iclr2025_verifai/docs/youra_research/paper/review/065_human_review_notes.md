# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> These are NOT auto-fixed by the Revision Agent.

**Date**: 2026-08-05
**Rounds Completed**: 2 (R1 initial, updated after R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 2 |
| Formatting | 1 |
| **Total** | **5** |

---

## Round 1 Issues

### Style

1. **§3, Table "Model and Infrastructure"**: Parenthetical "(effectively 1 at B=1000)" is correct but informal in a table cell. Consider moving to a table footnote or §5.4 prose only.

2. **§2, last paragraph**: "Our study differs from prior work in three ways: (1)... (2)... (3)..." — numbered list fragments what could be flowing prose. Consider: "Our study fills this gap in three ways: first... second... third..." for smoother reading.

### Clarity

3. **Abstract**: "using feedback signals to guide LLM re-generation on failing problems" — slightly abstract. Introduction's version "generating code, receiving feedback on failures, and re-generating to fix them" is clearer. Consider aligning Abstract phrasing.

4. **§5.1**: "more than doubling the baseline success rate" — colloquial but not inaccurate (33.1% → 73.3% = 2.21× improvement). Acceptable as-is; alternatively "increasing pass@1 by 2.21×" is more precise.

### Formatting

5. **References section**: Austin et al. 2021 entry contains "[UNVERIFIED via Scholar]" annotation: `arXiv:2108.07732*. [UNVERIFIED via Scholar]`. This internal annotation must be removed before submission. Manual citation verification recommended before final submission.

---

## Recommended Priority

1. **Fix First**: Remove "[UNVERIFIED via Scholar]" from References before submission (mandatory)
2. **Fix Second**: Align Abstract phrasing with Introduction for consistency
3. **Consider**: Style improvements in §2 and §3 table (subjective)
4. **Optional**: §5.1 colloquial phrasing

---

*Note: These issues do not block paper acceptance but improve overall quality.*
