# Human Review Notes - Phase 6.5

**Generated:** 2026-08-28
**Purpose:** Minor issues collected for human review (not auto-fixed)

---

## Summary

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 1 |
| Formatting | 0 |
| **Total** | **1** |

---

## Notes

### R1-M1: Gradient Norm Aggregation Clarification

**Round:** R1
**Category:** clarity
**Location:** Section 6.4 (Limitations)
**Severity:** MINOR

**Issue:**
Paper mentions "Layer4 gradients only" but does not explicitly note potential sensitivity to gradient norm aggregation method (L2 vs L1 vs Frobenius).

**Context:**
Ground truth shows L2 norm was used. Results could theoretically differ with other aggregation methods.

**Suggested Fix:**
Add clarifying sentence: "We use L2 gradient norms; other aggregation methods (L1, Frobenius) may yield different ratios but directional findings should hold."

**Action Required:** Human decision - add or decline

---

## Review Status

- [x] R1 MINOR issues collected
- [ ] R2 MINOR issues collected (pending)

---

*These issues are NOT auto-fixed to preserve author judgment on stylistic choices.*
