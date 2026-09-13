# Human Review Notes - Phase 6.5 Adversarial Review

**Generated:** 2026-08-19  
**Paper:** 06_paper.md  
**Status:** MINOR issues for human review (not auto-fixed)

---

## Round 1 MINOR Issues

### 1. AUROC Value Clarity (Line 219-220)
- **Location:** Results Section, H-M3 Fusion Table
- **Issue:** Table shows entropy-only AUROC=0.675, but abstract/results report 0.65. These values come from different sample sizes (N=20 for fusion table, N=100 for H-M1).
- **Recommendation:** Consider adding table caption clarifying "Values computed on N=20 subset used for fusion experiments"
- **Type:** clarity

### 2. Embedding Model Choice (Line 126)
- **Location:** Methodology Section
- **Issue:** Uses "all-MiniLM-L6-v2" embedding model without discussion of why this choice or how different embedding models might affect results.
- **Recommendation:** Consider brief justification or noting as limitation
- **Type:** clarity

### 3. Temperature Choice (Line 111)
- **Location:** Methodology Section
- **Issue:** Temperature 0.7 stated but not justified. Different temperatures would affect response diversity and thus consistency scores.
- **Recommendation:** Consider brief justification ("standard value for diverse sampling") or noting as future work to test sensitivity
- **Type:** clarity

---

## Summary

| Type | Count |
|------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 3 |
| Formatting | 0 |

**Total MINOR issues:** 3

---

*These issues were collected during adversarial review but NOT auto-fixed. They are flagged for human review before final publication.*
