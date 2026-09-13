# Human Review Notes
> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-05-04T09:30:00Z
**Rounds Completed**: 1 (R1; R2 notes appended below)

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

### Style
1. **HR notation consistency** (Abstract/Introduction vs. Results): "3.16" used in Abstract and Introduction; "3.159" used in Results tables. Recommend standardizing to "3.16" throughout text and "3.159" in tables, or "3.159" everywhere for precision. Neither choice affects scientific validity.

### Clarity
1. **p-value notation** (Abstract vs. Results): Abstract says "p=0.005" (rounded), Results says "p=0.0053" (exact). Recommend using "p=0.0053" consistently, or "p<0.01" in Abstract with exact value in Results. Minor but can confuse careful readers.

2. **Age-FAIR correlation not quantified** (Methods 3.3): The suppressor confounding mechanism (high-FAIR = newer datasets) is stated but not demonstrated with a number. Adding one sentence with the Spearman correlation between FAIR score and dataset creation year would strengthen the methodological claim for skeptical reviewers. E.g., "High-FAIR datasets are systematically newer (ρ=X between FAIR score and creation year quartile), creating the suppressor..."

### Formatting
1. **Lv et al. (2022) spurious citation**: "Are We Really Achieving Progress in Heterogeneous Graph Neural Networks?" (arXiv:2112.14936) appears in the References section with no apparent connection to FAIR data principles, ML dataset repositories, or survival analysis. This appears to be a pipeline artifact from a different research topic. Should be removed or replaced with a relevant citation.

---

## Round 2 Issues

### Clarity
1. **p-value rounding in Introduction** (Introduction paragraph 1): "p=0.58" should be "p=0.583" to match the value used consistently in Abstract and Results. Minor but precision-conscious reviewers will notice the discrepancy between the hook sentence and the Results table.

---

## Recommended Priority

1. **Fix First**: Lv et al. 2022 spurious citation removal (formatting — affects credibility)
2. **Fix Second**: HR notation consistency (style — easy fix)
3. **Consider**: p-value notation standardization (clarity)
4. **Optional**: Add age-FAIR correlation quantification (clarity — strengthens argument)

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer perception.*
