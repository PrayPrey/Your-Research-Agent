# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.

**Date**: 2026-08-29T14:30:00Z
**Rounds Completed**: 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 3 |
| Formatting | 0 |

---

## Round 1 Issues

### Clarity

1. **Section 5 (Results)**: Consider adding confidence intervals for AUROC values given 50-sample PoC size. Example: "AUROC = 0.81 (95% CI: 0.68-0.91)"

2. **Section 6.2 (Limitations)**: Temperature sensitivity (0.7) for semantic entropy sampling not explicitly discussed. May affect reproducibility concerns.

3. **Section 6.2 (Limitations)**: NLI threshold sensitivity (0.7) not acknowledged. Different thresholds may yield different clustering behavior.

---

## Round 2 Issues

No additional MINOR issues found in Round 2 numerical verification.

---

## Recommended Priority

1. **Fix First**: Item 1 (confidence intervals) - Adds statistical rigor for PoC claims
2. **Consider**: Items 2-3 (sensitivity acknowledgments) - Strengthen reproducibility section
3. **Optional**: None

---

*Note: These issues do not block paper acceptance but improve overall quality.*
*All FATAL (0) and MAJOR (0) issues resolved. Paper converged after 2 rounds.*
