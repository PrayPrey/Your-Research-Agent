# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review (NOT auto-fixed).
> These do not block paper acceptance but improve overall quality.

**Date:** 2026-08-31T11:30:00+00:00
**Rounds Completed:** 2 (R1, R2)
**Total Minor Issues:** 4

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 2 |
| Formatting | 1 |

---

## Round 1 Issues

### Clarity

**ACCR-MINOR-001** — FlatMLP Gap CI Omitted from Table 1
- **Location:** Table 1, Results §5.1
- **Original:** FlatMLP gap CI shown as "—"
- **Status:** Partially addressed — R1 revision added FlatMLP CI [0.4850, 0.5801] from h-m1 and full footnote. Consider whether to also report DWSNet gap CI (h-m1 shows [0.4377, 0.5325]) in Table 1 for completeness.
- **Action:** Optional — add DWSNet gap CI to Table 1 for symmetry.

### Formatting

**BORE-MINOR-001** — Citation Verification Status Not Disclosed
- **Location:** References section / paper metadata
- **Issue:** All 11 citations are unverified via Semantic Scholar MCP (per ground truth: `citations_verified_mcp: 0`). ArXiv IDs sourced from pipeline artifacts appear correct but were not cross-checked against live databases.
- **Action:** Consider adding a note: "References verified by arXiv ID from pipeline artifacts; cross-checking with Semantic Scholar MCP recommended before submission."
- **Priority:** Low — does not affect scientific claims.

---

## Round 2 Issues

### Clarity

**ACCR2-MINOR-001** — Partial Spearman vs. Direct Spearman Informal Comparison
- **Location:** §5.3, point 1: "Stronger than the direct Spearman (0.73 > 0.57)"
- **Issue:** Comparing partial Spearman (on rank residuals) to direct Spearman (on raw ranks) is informal. Both are valid effect-size descriptors but not directly statistically comparable.
- **Suggested revision:** "The partial correlation (r=0.73) exceeds the direct Spearman (r=0.57), suggesting the gap-specific component of NFT's predictions is stronger than the combined signal — though partial and direct Spearman measure different quantities and should not be directly compared as if equivalent."
- **Priority:** Medium — reviewers familiar with partial correlation may flag this.

### Style

**SKEP2-MINOR-001** — Closing Metaphor Precision
- **Location:** Final sentence of Conclusion Closing: "The harder prediction problem, it turns out, is the one weight space was built for."
- **Issue:** "weight space was built for" implies intent — weight-space representations were developed for test accuracy prediction, not gap. The metaphor is literary but imprecise.
- **Suggested revision:** "The harder prediction problem, it turns out, is the one where weight space's structural information proves most accessible."
- **Priority:** Low — literary closing, acceptable as-is.

---

## Recommended Priority

1. **Fix First:** ACCR2-MINOR-001 (partial vs. direct Spearman) — methodological clarity, may draw reviewer attention
2. **Fix Second:** BORE-MINOR-001 (citation verification note) — transparency
3. **Consider:** ACCR-MINOR-001 (DWSNet CI addition) — completeness
4. **Optional:** SKEP2-MINOR-001 (closing metaphor) — stylistic

---

*These issues do not block paper acceptance. FATAL and MAJOR issues were resolved in R1 revision.*
