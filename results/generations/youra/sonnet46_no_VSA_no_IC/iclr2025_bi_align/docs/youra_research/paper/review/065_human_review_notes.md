# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review (Phase 6.5) for human review during final polish. These were NOT auto-fixed by the Revision Agent.

**Date:** 2026-08-21
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
| **Total** | **4** |

---

## Round 1 Issues

### Style

1. **Abstract, sentence 2:** "Whether these communities actually cite each other's alignment work — and symmetrically — is an open empirical question" — the em-dash construction "— and symmetrically —" is slightly awkward. Consider: "Whether these communities actually cite each other's alignment work symmetrically is an open empirical question."

### Clarity

1. **Section 5.3:** The parenthetical "(h-e1-v2)" may confuse readers unfamiliar with internal pipeline naming conventions. Consider adding a brief gloss: "(h-e1-v2, the planned corpus augmentation step described in Limitation 1)" or moving the label to a footnote.

2. **Section 6.2 Limitation 4:** Even after R1 fix, the opening "Findings apply specifically to the alignment community as operationalized by Shen et al. [2024]" could be strengthened by leading with the implication: "Corpus selection bias limits generalizability: findings apply specifically to papers in the alignment community as operationalized by Shen et al. [2024]."

### Formatting

1. **Section 3.4:** The displayed math formula for $r$ renders as a LaTeX display equation. In ICML2025 format, verify that `$$...$$` produces a display equation (not inline) in the final PDF. Consider using `\begin{equation}...\end{equation}` for numbered equations if the venue requires equation numbering.

---

## Round 2 Issues

None additional.

---

## Recommended Priority

1. **Fix First:** Style issue in Abstract (high visibility, easy fix)
2. **Consider:** Clarity issues in Section 5.3 (h-e1-v2 parenthetical) and Section 6.2 (Limitation 4 opener)
3. **Verify:** LaTeX equation formatting in final PDF compilation

---

*Note: These issues do not block paper acceptance but improve overall quality.*
