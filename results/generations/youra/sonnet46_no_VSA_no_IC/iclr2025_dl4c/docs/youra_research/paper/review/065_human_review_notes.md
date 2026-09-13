# Human Review Notes
> **Purpose:** Minor issues collected during adversarial review for human review. NOT auto-fixed.

**Date:** 2026-08-21
**Rounds Completed:** 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Factual correction (applied) | 1 |
| Clarity | 3 |
| Style | 1 |
| Formatting | 0 |
| Typo | 0 |
| Grammar | 0 |

---

## Round 1 Issues

### Clarity

1. **Section 5.1, Table 1 header:** "k=4, max_new_tokens=128" — consider adding "(profiling only; training uses max_completion_length=512)" to immediately signal the mismatch to readers scanning tables.

2. **Section 3.2, parameter note:** The paragraph explaining k=4 vs k=8 reduction is accurate but dense. Consider a bullet-list format for clarity: (1) design spec, (2) actual parameters, (3) reason for change, (4) implication.

3. **Section 6.2, root cause enumeration:** Four ranked candidates are listed but without explicit probability weights (e.g., "most likely" vs "possible" vs "less likely"). Consider a simple 3-tier label (HIGH/MEDIUM/LOW) for each candidate to guide readers.

### Style

1. **AC-4 (k=4 vs k=8 coarseness):** The paper explains k was reduced but does not quantify how k=4 affects the variance distribution's resolution. A one-paragraph analysis showing how k=8 would produce 7 distinct variance values (vs. 3 under k=4) would help readers assess generalizability.

---

## Round 2 Issues

### Clarity

1. **R2-MINOR-2:** The "to our knowledge" hedge on "first empirical characterization" is present but unsupported by explicit comparison to prior GRPO-on-MBPP work. Consider adding a footnote: "Gehring et al. [2024] and Nie et al. [2026] report aggregate reward statistics but not per-problem variance distributions."

---

## Factual Correction Applied in Revision

**"40,000+" corrected to "50,000+"** (R1 revision, treated as factual not stylistic):
- Original: "40,000+ generation attempts"
- Correct: 10,000 (h-m2) + 40,000 (h-m3) = 50,000 total
- Changed to "50,000+" throughout paper R1

---

## Recommended Priority for Human Review

1. **Address first:** Clarity items 1 and 3 (Table 1 header annotation, root cause probability labeling)
2. **Consider:** Style item 1 (k=4 coarseness analysis paragraph)
3. **Optional:** R2-MINOR-2 footnote on prior work comparison

---

*These issues do not block paper acceptance but improve overall quality and reduce reviewer attack surface.*
