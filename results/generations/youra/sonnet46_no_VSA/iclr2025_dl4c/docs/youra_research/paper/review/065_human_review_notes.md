# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> These issues do NOT block paper acceptance but improve overall quality.
> They were NOT auto-fixed — review and apply at your discretion.

**Date**: 2026-08-03  
**Rounds Completed**: 2  

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 2 |
| Clarity | 2 |
| Formatting | 1 |
| **Total** | **5** |

---

## Round 1 Issues

### Style

1. **Section 1 (Introduction)**: "This effect substantially exceeds most reported architectural improvements" — this comparative claim lacks citation. Either add a citation to a survey/comparison, or soften to "This effect exceeds typical single-technique improvements reported in the code SFT literature."
   - *Original (before R1 fix)*: "dwarfs most reported architectural improvements"
   - *R1 fix*: changed "dwarfs" to "substantially exceeds" — still needs citation or softening.

2. **Section 1 (Introduction)**: Opening hook sentence ends with "— by up to 1.5 percentage points, consistently across all three random seeds." The phrase "by up to 1.5 percentage points" undersells the finding relative to the Abstract's framing of the same phenomenon. Consider aligning the hook's quantitative framing with the Abstract.

### Clarity

3. **Section 3.2 (Table)**: The "Conditions" table shows "Equal-mix | Equal proportions from all three | —" — the "—" for problem count is unexplained. Add a note: "~360 problems total (120 from each source)" or note it's token-budget equalized to match others.

4. **Section 5.1**: The note "Critically, Equal-mix achieves only 10.2% — below both HumanEval-only (35.0%) and MBPP-only (27.6%)" is accurate but could be strengthened by noting this is *also below the base model's zero-shot performance* — if the base model zero-shot is reported. If not available, skip this suggestion.

### Formatting

5. **Section 5.4, Table 4**: "Seed variance" column header and values use "σ²≈0.00000" which rounds to exactly zero — this could be interpreted as literally zero. Consider using scientific notation or "< 0.001" to be precise.

---

## Round 2 Issues

### Formatting

*(The MINOR-R2-001 notation issue — "0.055pp vs 0.319pp" → "5.5pp vs 31.9pp" — was auto-fixed in R2 revision as it affected numerical clarity. Not listed here.)*

No additional MINOR issues found in R2.

---

## Recommended Priority

1. **Fix First**: Item 1 (citation for comparative claim in Introduction — visible to reviewers)
2. **Fix Second**: Item 5 (σ² notation — could confuse readers)
3. **Consider**: Items 2, 3, 4 (framing/clarity improvements)

---

*Note: These issues do not block paper acceptance but improve overall quality.*
