# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review. These were NOT auto-fixed.

**Date:** 2026-08-24
**Rounds Completed:** 2

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
1. **MINOR-003** — Abstract vs. tables: Abstract uses "8.6%", "81.9%", "73.4 pp"; Table 1 uses "8.57%", "81.93%", "73.36 pp". The R1 revision standardized prose to "8.57%" and "73.4 pp (73.36 pp exact)" on first mention. Author may wish to review for remaining style inconsistencies in final proofread.

### Clarity
2. **MINOR-002** — Section 2.3: The spectral regularization paper was [CITATION NEEDED] in R1 and is now filled in as Chen et al. 2025 (chen2025spectral placeholder). Author must verify exact citation before submission. Mark for manual check.

### Formatting
3. **MINOR-001** — Section 6.1 Finding 3: Pre-revision, reviewer noted potential "unmotivated" typo. Post-check confirmed the text read "unverified but well-motivated" — no change needed. Flagged as a false positive.

---

## Round 2 Issues

### Clarity
4. **ACC-R2-MINOR-001** — Section 5.2 (Training Dynamics): The supervised model's val WGA dips below 80% at epochs 23, 30, 33, 36-37, 55, 59, 79 per the archive JSON. The R2 revision changed to "generally above 80% after epoch 10, consistently above 70% throughout." Author should verify this phrasing is accurate for the final figure. If Figure 2 shows the training dynamics curve, caption wording should match.

---

## Recommended Priority

1. **Resolve first**: chen2025spectral author verification (submission-blocking)
2. **Resolve before submission**: All 8 UNVERIFIED references in references section
3. **Consider**: Style consistency between prose (rounded) and tables (exact) — personal preference, both styles are used in ML papers
4. **Optional**: Figure 2 caption alignment with §5.2 training dynamics description

---

*Note: These issues do not block the adversarial review from converging, but require author attention before submission to ICML 2026.*
