# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.

**Date**: 2026-08-24
**Rounds Completed**: 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Precision | 2 |
| Consistency | 2 |
| Completeness | 2 |
| Statistical | 2 |
| Formatting | 2 |

---

## Round 1 Issues

### Precision
1. **Abstract**: "75% of adaptation capacity" claim was unsupported — *addressed in revision*

### Consistency
1. **Sec 3.2 vs Abstract**: h-e1 predicted α in (0.3, 0.7), abstract said (0.3, 0.8) — *addressed by changing gate to α < 1*

### Completeness
1. **Sec 5.4 Table 4**: No 12B entropy value shown (entropy measured at 6.9B) — entropy analysis covers 1B-6.9B, consistent with validation files
2. **Sec 6.3**: Missing limitation about synthetic validation — *added*

### Formatting
1. **Sec 2.4**: "1B-12B" could imply inclusive range; explicit list "1B, 2.8B, 6.9B, 12B" clearer — *addressed*

---

## Round 2 Issues

### Precision
1. **p-value rounding**: h-m1 reports p=0.0102, paper uses 0.010. Minor precision loss, acceptable.

### Consistency
1. **Formula range**: Core claim states α ∈ (0.3, 0.8) but observed α=0.82 slightly exceeds. Consider "α < 1" to avoid confusion. — *addressed in gate criterion, intro updated*

### Statistical
1. **n=3 for entropy correlation**: Acknowledged in limitations but could be more prominent
2. **Bootstrap with 3 seeds**: Wide CI reflects this, appropriately reported

### Formatting
1. **Figures not inline**: Filenames added but full LaTeX embedding deferred to Phase 6.5.1

---

## Recommended Priority

1. **Already Fixed**: M1-M4 from R1 addressed in revision
2. **Deferred to LaTeX**: Figure embedding with captions
3. **Optional**: Statistical power note could be expanded

---

*Note: These issues do not block paper acceptance but improve overall quality.*
