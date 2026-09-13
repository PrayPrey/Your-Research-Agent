# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.  
> **v2.0 Protocol:** These issues are NOT auto-fixed by AI to preserve author voice and style preferences.

**Generated**: 2026-04-20T10:45:00+00:00  
**Rounds Completed**: 2 (R1, R2)  
**Total Issues**: 4

---

## Summary by Category

| Category | Count |
|----------|-------|
| Grammar  | 1     |
| Style    | 1     |
| Clarity  | 1     |
| Formatting | 1   |

---

## Round 1 Issues

### Grammar

**MINOR-R1-G1**: Terminology consistency
- **Location**: Section 2.1 (Related Work), paragraph 2
- **Current**: "These approaches focus primarily on **what tactic to suggest next** (the forward inference problem) rather than **when to terminate a search** (the meta-reasoning problem)."
- **Issue**: In first sentence of this paragraph, uses "signal" instead of "tactic" - consider consistent terminology
- **Suggested**: Verify "what signal to suggest next" vs "what tactic to suggest next" - both appear in paper
- **Priority**: Low (meaning is clear from context)

### Style

**MINOR-R1-S1**: Wordiness in Related Work comparisons
- **Location**: Section 2.2-2.3, multiple paragraphs
- **Issue**: Some sentences in Related Work could be more concise
- **Example**: "While effective for symbolic reasoning where state spaces have clearer structure, these heuristics fail to leverage the rich semantic information available in neural provers."
- **Could be**: "While effective for symbolic reasoning, these heuristics cannot leverage neural provers' rich semantic information."
- **Priority**: Low (current style is acceptable, just verbose)

### Clarity

**MINOR-R1-C1**: Forward reference to Figure 5
- **Location**: Section 5.1 (Results), early paragraphs
- **Issue**: Ablation results discussed in text before Figure 5 is mentioned
- **Suggested**: Add forward reference: "We present comprehensive ablation results in Figure 5 (Section 5.3)."
- **Priority**: Low (readers will find Figure 5 when reaching Section 5.3)

### Formatting

**MINOR-R1-F1**: Table 2 visual organization
- **Location**: Section 5.3, Table 2 (Ablation Results)
- **Issue**: Table lists 7 detectors without visual separator between categories (single/pairwise/hybrid)
- **Suggested**: Consider adding horizontal rules or spacing between:
  - Single-signal models (confidence_only, symbolic_only, search_only)
  - Pairwise models (conf_symb, conf_search, symb_search)
  - Hybrid model (hybrid_all)
- **Priority**: Low (current table is readable, just could be more scannable)

---

## Round 2 Issues

**No MINOR issues identified in Round 2.**

R2 focused exclusively on numerical verification and found 3 FATAL discrepancies (all corrected).

---

## Recommended Priority

### Fix First: High-Visibility Sections
None of the MINOR issues appear in high-visibility sections (Abstract, Introduction, Conclusion).

### Fix Second: Grammar
- MINOR-R1-G1 (terminology consistency) - Quick fix if desired

### Consider: Style Improvements
- MINOR-R1-S1 (wordiness) - Subjective, author preference

### Optional: Formatting Tweaks
- MINOR-R1-F1 (table separator)
- MINOR-R1-C1 (forward reference)

---

## Notes for Human Reviewer

1. **Author Voice Preserved**: The AI deliberately did NOT auto-fix these issues to preserve your writing style and voice.

2. **Scientific Validity Unaffected**: All FATAL and MAJOR issues (0+13 in R1, 3 in R2) were resolved. These MINOR issues do not affect scientific accuracy or credibility.

3. **Subjective Nature**: Style and formatting preferences vary by author and venue. What seems "wordy" to one reviewer may be "thorough" to another.

4. **Time Investment**: Estimated 15-30 minutes to address all 4 issues if desired.

5. **Publication Ready Without Fixes**: The paper is publication-ready even without addressing these MINOR issues. They are polish items, not blockers.

---

## v2.0 Protocol Rationale

**Why NOT auto-fix MINOR issues?**

1. **Preserve Author Voice**: Writing style is personal; AI shouldn't impose generic "fixes"
2. **Avoid Over-Polishing**: Papers with too-perfect prose can sound robotic
3. **Subjective Judgments**: Grammar/style preferences vary; human judgment better for these
4. **Trust Authors**: Minor issues are noticed by authors during final read-through anyway
5. **Focus AI on What Matters**: AI should fix objective errors (wrong numbers, contradictions), not subjective style

**Result**: Paper maintains authentic authorial voice while achieving scientific rigor.

---

*These notes are advisory only. The final decision on whether and how to address these issues rests with the human author.*
