# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-04-24T20:40:00Z
**Rounds Completed**: 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 5 |
| Clarity | 3 |
| Formatting | 1 |
| Incomplete | 1 |

**Total**: 10 minor issues

---

## Round 1 Issues

### Style (5 issues)

1. **Abstract, line 25**: "post-training without annotation costs" — awkward phrasing
   - Suggested: "post-training without requiring group annotations"

2. **Introduction, line 47**: "shifts the focus from 'how to fix'" — informal phrasing for academic paper
   - Suggested: "shifts focus from robustification methods to optimization foundations"

3. **Section 3.2, line 95**: "avoiding full eigendecomposition, which is O(M³)" — parenthetical breaks flow
   - Suggested: Remove parenthetical or move to footnote

4. **Throughout**: Inconsistent hyphenation: "worst-group" vs "worst group"
   - Suggested: Standardize to "worst-group" (hyphenated)

5. **Section 6.3, Limitation 4**: "estimated 20-30 hours" — inconsistent with other time estimates (uses hours, others use weeks)
   - Suggested: Convert to "estimated 1-2 days" for consistency

### Clarity (3 issues)

1. **Section 2.5, line 81**: "Positioning Our Contribution" — heading is meta-commentary, unusual for Related Work
   - Suggested: Change to "Summary" or "Our Approach"

2. **Section 5.1, Table 1**: Missing column header explanation (what does "Difference" row represent?)
   - Suggested: Add caption note: "Difference row shows ERM minus DRO values"

3. **Section 5.6.1, line 286**: "This failure has three potential explanations" — numbered list would be clearer
   - Suggested: Format as numbered list (1, 2, 3) instead of prose

### Formatting (1 issue)

1. **Figure references**: Figures 1-3 referenced in text but actual figure numbers don't match captions (fig2_spectra is called "Figure 1" in text)
   - Suggested: Renumber figures to match text references OR update text to match figure filenames

### Incomplete (1 issue)

1. **References section**: "See 06_references.bib" — placeholder text, needs actual formatted references
   - Suggested: Generate formatted bibliography from .bib file

---

## Round 2 Issues

**None identified** — R2 focused on verifying R1 fixes, found no new minor issues.

---

## Recommended Priority

1. **Fix First**: References section (incomplete - high visibility)
2. **Fix Second**: Figure numbering mismatch (affects readability)
3. **Fix Third**: Clarity improvements (Table 1 caption, Section 2.5 heading)
4. **Consider**: Style improvements (hyphenation, phrasing)
5. **Optional**: Minor formatting tweaks

---

## Notes

- These issues do not block paper acceptance but improve overall quality
- All substantive issues (FATAL/MAJOR) were resolved in R1
- Paper is ready for submission with these minor polish items outstanding
- Estimated time to address all: 1-2 hours of human editing

---

**Last Updated**: 2026-04-24T20:40:00Z
