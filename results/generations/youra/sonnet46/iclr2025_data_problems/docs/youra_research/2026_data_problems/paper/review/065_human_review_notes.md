# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-03-15T15:00:00
**Rounds Completed**: 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 4 |
| Formatting | 0 |
| Citation verification | 2 |
| **Total** | **8** |

---

## Round 1 Issues

### Clarity
1. **Section 5.1**: Original text claimed "intermediate configurations (C2-C4) show modest entropy reductions (0.5–4.9%)" — this was a FATAL issue and was FIXED in R1. Now correctly shows −6.3% (C3) and −11.5% (C4). RESOLVED.

2. **Section 3.6 / 4.2**: The distinction between "intended Pythia-1B architecture" and "actual proxy model used" should be clear on first encounter. RESOLVED in R1.

3. **Table 1 (C7)**: Motivation for using C3 as C7 base was missing. RESOLVED — added "median entropy level, preserves overall frequency while destroying conditional associations."

4. **Section 3.5**: Log base for log-odds formula was ambiguous. RESOLVED — added "(log denotes natural logarithm; entropy uses log₂)."

### Style
1. **Abstract**: Uses "p≈0" for H-M1 Spearman result while Results Section 5.2 gives exact "p=1.4×10⁻²⁴." Stylistically acceptable (abstract space constraints) but inconsistent. **Consider**: Replace "p≈0" with "p=1.4×10⁻²⁴" in abstract for precision, or add parenthetical "(p≈0 denotes p=1.4×10⁻²⁴)" somewhere in the paper.

2. **Section 2.3 (Related Work)**: The phrase "to our knowledge, novel as a curation-hyperparameter audit sweep in the pretraining data context" is somewhat convoluted. **Consider**: "to our knowledge, the first curation-hyperparameter audit sweep measuring H(occupation|demographic) across filtering configurations."

### Citation Verification
1. **Gebru et al. 2018**: Cited as "FAccT Workshop 2018" — original was a workshop paper, later published in Communications of the ACM 2021. Verify correct venue: use "FAccT Workshop 2018" if citing original, or "Communications of the ACM 64(12), 2021" if citing published version.

2. **Biderman et al. 2023**: Cited as "ICML 2023" — verify against arXiv:2304.01373. Biderman et al., "Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling," ICML 2023 is the correct citation.

---

## Round 2 Issues

### Clarity
1. **Section 5.3 (H-M2 rho note)**: "A discrepancy exists with a quick-run proxy state variable (ρ=−0.2143 in verification_state.yaml), which reflects mock-training proxy outputs rather than the primary validation run." The phrase "quick-run proxy state variable" may confuse readers unfamiliar with the pipeline. **Consider**: "verification_state.yaml records ρ=−0.2143, reflecting mock-training outputs from an earlier proxy run rather than the final experimental record in h-m2/04_validation.md."

2. **Appendix Figure 5 description**: "Mean log-odds across 1800 pairs vs. filtering intensity (5 filter levels C1–C5)" — correct. No action needed, just flagged for consistency check against actual figure.

3. **Section 6.2 L5**: "draws occupations from U.S. Bureau of Labor Statistics data circa 2018" — verify this is the correct WinoBias source. Zhao et al. 2018 describes the occupation list as drawn from BLS. This is accurate; no action needed.

---

## Recommended Priority

1. **Fix First**: Citation verification (Gebru et al. venue) — easy, high accuracy risk
2. **Fix Second**: Abstract p≈0 → p=1.4×10⁻²⁴ for precision consistency
3. **Consider**: Related Work 2.3 phrasing improvement
4. **Optional**: Section 5.3 rho discrepancy note phrasing

---

*Note: These issues do not block paper acceptance but improve overall quality.*
