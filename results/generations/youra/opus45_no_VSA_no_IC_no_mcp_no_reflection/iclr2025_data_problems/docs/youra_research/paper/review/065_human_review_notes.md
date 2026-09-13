# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.

**Date:** 2026-08-28
**Rounds Completed:** 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 2 |
| Formatting | 0 |
| **Total** | **2** |

---

## Round 1 Issues

### Clarity

1. **Section 5.2, Statistical Analysis:**
   - Issue: "p-value: < 0.001" could be more precise
   - Suggestion: Consider "p << 0.001" or "p = 0.0 (to machine precision)"
   - Impact: Low (current phrasing is technically correct)

2. **Figure 1 caption:**
   - Current: "EDMP similarity scores for 8 domains. Domains are ordered by score."
   - Suggestion: Add what bar heights represent and mention the variance threshold
   - Example: "EDMP similarity scores for 8 domains, sorted by score. Higher scores indicate greater semantic similarity to MMLU task exemplars. The low variance (std=0.0069) across domains reflects synthetic data limitations."
   - Impact: Medium (improves accessibility)

---

## Round 2 Issues

None. All numerical claims verified.

---

## Recommended Priority

1. **Fix First:** Figure 1 caption expansion (improves figure accessibility)
2. **Consider:** p-value precision in Section 5.2 (optional)

---

## Status

These issues do not block paper acceptance but may improve overall clarity for readers.

*Note: MINOR issues are collected for human review per workflow specification. Auto-fixing is reserved for FATAL and MAJOR issues only.*
