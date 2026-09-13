# Human Review Notes
> **Purpose:** Minor issues collected during adversarial review for human review. These were NOT auto-fixed.

**Date:** 2026-08-25  
**Rounds Completed:** R1 (R2 pending)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 |
| Clarity | 1 |
| Formatting | 0 |
| **Total** | **4** |

---

## Round 1 Issues

### Style
1. **Section 5.4, Table 4** — "*Note on SE orientation*" placed mid-table interrupts reading flow. Consider moving to a footnote below the table for smoother reading. (BORED-MINOR-001)

2. **Section 5.5, Table 5** — "~47%" for empirical accuracy could be "46.9%" for precision consistency with other metrics reported to 3 decimal places. (SKEP-MINOR-002)

3. **Sections 5.1–5.5** — Figure references ("Figure 1 shows..., Figure 2 confirms..., Figure 3's violin...") assume inline figures. In final camera-ready, verify figure placement near first reference. (BORED-MINOR-002)

### Clarity
1. **Section 5.4** — The dual delta values (0.092 raw vs 0.336 corrected) are now both reported after R1 fix, but the rationale for preferring the corrected value over the raw value for the headline claim could be made even more explicit with one additional sentence explaining that the corrected orientation is the one consistent with the defined AUROC convention in Section 3.2. (SKEP-MINOR-001 — partially addressed in R1-FIX-003, residual clarity gap)

---

## Recommended Priority

1. **Fix First:** Move Section 5.4 sign convention note to a footnote (Style #1) — affects readability at key section
2. **Consider:** Clarify corrected vs. raw delta rationale (Clarity #1) — supports reviewer trust
3. **Optional:** Precision consistency in Table 5 (Style #2)
4. **Optional:** Camera-ready figure placement check (Style #3)

---

## Round 2 Issues

### Clarity
1. **Introduction, Contribution 4** — Uses corrected delta 0.336 in the contribution statement. After reading Section 5.4, this is justified, but a reader scanning only the Introduction may be confused about why the gate is 0.03 and the delta is 0.336 vs 0.092. One additional phrase "(using corrected SE orientation; see §5.4)" would resolve the potential confusion. (R2-MINOR-001)

2. **Section 5.2, final paragraph** — Values "10.1 nats²" and "3.4 nats²" (low vs high uncertainty sub-group variance) are not sourced in the text. Add "(from Figure 6 sub-group analysis)" to allow verification. (R2-MINOR-003)

---

## Updated Summary by Category

| Category | R1 | R2 | Total |
|----------|----|----|-------|
| Typo | 0 | 0 | 0 |
| Grammar | 0 | 0 | 0 |
| Style | 3 | 0 | 3 |
| Clarity | 1 | 2 | 3 |
| Formatting | 0 | 0 | 0 |
| **Total** | **4** | **2** | **6** |

---

## Recommended Priority

1. **Fix First:** Move Section 5.4 sign convention note to a footnote (Style #1) — affects readability at key section
2. **Fix Second:** Add "(see §5.4)" in Introduction Contribution 4 (Clarity R2 #1)
3. **Consider:** Add figure reference for sub-group variance values (Clarity R2 #2)
4. **Consider:** Clarify corrected vs. raw delta rationale (Clarity #1 from R1)
5. **Optional:** Precision consistency in Table 5 (Style #2)
6. **Optional:** Camera-ready figure placement check (Style #3)

---

*Note: These issues do not block paper acceptance but improve overall quality.*
