# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-05-11T16:00:00+00:00
**Rounds Completed**: 2 (R1 + R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 1 |
| Style | 3 |
| Clarity | 3 |
| Formatting | 1 |
| **Total** | **8** |

---

## Round 1 Issues

### Grammar
1. **§5.3 Pairwise table**: "Qualifies" column uses ✓ and — symbols inconsistently — consider "Yes"/"No" or uniform symbol convention for camera-ready formatting.

### Style
1. **Abstract**: Word count ~173 words exceeds ICML 150-word convention. Consider trimming the last sentence ("These findings establish concrete domain boundaries...") or merging with the SelfCheckGPT sentence.
2. **§1 Introduction opening**: "We deployed three state-of-the-art..." — "state-of-the-art" is a cliché that adds no information. Consider: "We applied three widely-used uncertainty quantification methods..."
3. **§6 Discussion**: "Finding 1/2/3" headers are informal for ICML. Consider using subsection titles that name the finding directly (e.g., "NLI Domain Mismatch Causes SE Degeneracy").

### Clarity
1. **§3 Methodology, H-M2 definition**: "Gate: ≥0.50 (PASS); < 0.30 CI lower (PIVOT)" — the dual threshold is not explained inline. A brief parenthetical "(i.e., CI lower bound below 0.30 triggers PIVOT)" would help readers unfamiliar with the gate framework.
2. **§5.1 Table caption**: The table has no explicit caption in the markdown — just a header row. Consider adding "Table 1:" label for cross-referencing in camera-ready.
3. **§4 Experimental Setup table**: "Min AUROC gap (gate)" row — "gate" is pipeline-internal terminology. Consider "Min significant AUROC gap" for external readers.

### Formatting
1. **Figure List at end of paper**: ICML papers embed figure captions inline with figures, not in a separate list. The Figure List section should be removed or converted to inline captions for camera-ready submission.

---

## Round 2 Issues

*(No additional MINOR issues identified in R2 — R2 focused on numerical verification and credibility, which produced only MAJOR-level findings that were addressed.)*

---

## Recommended Priority

1. **Fix First**: Abstract word count (high visibility, affects first impression)
2. **Fix Second**: Figure List → inline captions (required for camera-ready ICML format)
3. **Consider**: "state-of-the-art" → "widely-used" in §1 opening
4. **Consider**: §6 Discussion heading style
5. **Optional**: §3 H-M2 gate explanation, §4 table row label, §5.1 table caption label

---

*Note: These issues do not block paper acceptance but improve overall quality and ICML format compliance.*
