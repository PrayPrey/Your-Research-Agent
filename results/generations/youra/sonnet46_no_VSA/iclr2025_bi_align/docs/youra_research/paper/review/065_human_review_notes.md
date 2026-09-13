# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.

**Date**: 2026-07-30
**Rounds Completed**: 1

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 |
| Clarity | 3 |
| Formatting | 0 |

---

## Round 1 Issues

### Style

1. **Contribution (4) header framing**: Introduction contribution (4) says "Evidence for asymmetric RLHF alignment effects" — this is slightly aggressive framing for a null result. The body text (Sections 5.5, 6.2) is more careful ("suggests potential asymmetry," "hypothesis-generating finding"). Consider softening to "Null result suggesting potential asymmetry in RLHF alignment targets" to match body text framing.

2. **Rounding inconsistency**: Abstract uses "49%/76%" while Introduction uses "49.3%/76.3%". These are the same numbers rounded differently. Standardize across sections (either always 49%/76% or always 49.3%/76.3%).

3. **`clawrxiv:2603.00394` citation format**: This uses an unusual citation format. Verify that "clawrxiv" is a real preprint server (not a placeholder). Format citation consistently with other preprint citations for ICML submission.

### Clarity

1. **N=321 vs N=300 unexplained**: TruthfulQA RLHF analysis used N=321 base/chat pairs while BBQ sign test used N=300 pairs. A quick reader may wonder if these should match. Add one sentence (e.g., in Section 2.3 or 5.5) clarifying these came from different pipeline iterations.

2. **BBQ forward reference in Section 2.1**: Section 2.1 describes the real BBQ benchmark without the proxy caveat; proxy disclosure comes three sections later in Section 3.2. Consider adding a forward reference "(see Section 3.2 for proxy substitution details)" at first BBQ mention in 2.1 to orient the reader earlier.

3. **Tu et al. 2024 citation discrepancy**: The section file `02_related_work.md` (Section 2.4) cites `(Liu et al., 2017; Tu et al., 2024)` but the compiled paper `06_paper.md` only has `(Liu et al., 2017)`. If Tu et al. 2024 is a real citation, it should appear in the compiled paper and reference list. If it was dropped intentionally, remove it from the section file too. Resolve in one direction before submission.

---

## Recommended Priority

1. **Fix First**: Clarity item 3 (Tu et al. 2024 — resolve intentionally in section file and compiled paper)
2. **Fix Second**: Style item 2 (rounding consistency 49%/76% vs 49.3%/76.3%)
3. **Fix Third**: Clarity item 1 (N=321 vs N=300 explanation)
4. **Consider**: Style items 1 and 3, Clarity item 2

---

*Note: These issues do not block paper acceptance but improve overall quality.*

---

## Round 2 Issues

### Style
1. The Steiger (1980) reference added in R2 may need DOI verification and consistent formatting with other references in the bibliography.

### Clarity  
1. R2 verified all 24 primary numerical claims against Phase 4 JSON result files — no clarity issues found.
