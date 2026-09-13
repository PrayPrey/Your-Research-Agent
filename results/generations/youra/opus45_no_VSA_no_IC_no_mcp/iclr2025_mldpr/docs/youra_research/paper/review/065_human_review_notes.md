# Human Review Notes

**Generated:** 2026-08-28
**Purpose:** Minor issues collected for human review (NOT auto-fixed)

---

## Round 1 Notes

### Note 1: Rounding Inconsistency (MINOR)

**Location:** Abstract vs Section 5.2
**Issue:** Abstract says "R² = 0.35", body says "R² = 0.349"
**Recommendation:** Choose consistent precision (suggest 0.35 throughout for readability)
**Category:** formatting

### Note 2: Cross-Hypothesis DNSI Values (MINOR)

**Location:** Table 1 vs h-c1 validation data
**Issue:** h-c1 uses CIFAR-10 DNSI=0.85, paper uses 0.790 (from h-m1)
**Recommendation:** Add footnote explaining methodology variations between hypothesis validations, or use single consistent dataset
**Category:** clarity

### Note 3: Missing Figure References (MINOR)

**Location:** Throughout
**Issue:** Paper references "Table 1" but methodology paper lacks actual embedded figures
**Recommendation:** Consider adding figure placeholders or clarifying this is text-only version
**Category:** formatting

---

## Summary

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 1 |
| Formatting | 2 |
| **Total** | **3** |
