# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review (NOT auto-fixed).

**Date**: 2026-08-04
**Rounds Completed**: 2 (updated after R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 2 |
| Formatting | 0 |
| **Total** | **4** |

---

## Round 1 Issues

### Style
1. **MINOR-001** — Section Abstract: "0.88" appears in Introduction hook as "mean AUROC 0.885" after fix — consider whether the abstract summary number (now removed from intro hook) needs a parenthetical "(mean of passing seeds)" for absolute clarity.
2. **MINOR-002** — Section 2.3: EVaLS cited as "[sharif-ml-lab]" without formal author/year/title. This reference is non-standard and will fail any BibTeX bibliography. Replace with proper citation: search for "EVaLS spurious correlations" to find the correct paper reference.

### Clarity
3. **MINOR-003** — Section 6.4 (Limitations): Compute cost is mentioned per-checkpoint in Section 4.3 ("approximately 8 minutes on a single A100 GPU") but not discussed as a scalability limitation in Section 6.4. Consider adding: "Per-checkpoint trace computation takes ~8 minutes on an A100 for 4795 samples with K=50; scaling to datasets with >100K samples or architectures with larger last-fc layers would require further engineering."
4. **MINOR-004** — Section 3.6: The gate threshold language appears in multiple forms across paragraphs (once for H-E3, once for H-M1). After R1 fix, verify both paragraphs read consistently.

---

## Recommended Priority

1. **Fix First**: MINOR-002 (EVaLS citation — will block submission with missing reference)
2. **Fix Second**: MINOR-003 (scalability limitation — strengthens paper's self-awareness)
3. **Consider**: MINOR-001 and MINOR-004 (minor style/clarity — subjective)

---

*Note: These issues do not block paper acceptance but improve overall quality.*
