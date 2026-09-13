# Human Review Notes
> **Purpose**: Minor issues collected during adversarial review for human review. NOT auto-fixed.

**Date**: 2026-07-30
**Rounds Completed**: 2 (R1 + R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 3 |
| Citation/Reference | 2 |
| **Total** | **7** |

---

## Round 1 Issues

### Style

**HRN-001** (ACC-MINOR-001 / BR-MINOR-002): Section 5.5 — Pipeline versioning IDs
- **Location**: Results Section 5.5, paragraph 2
- **Current text**: "This recalibration required three gate iterations during the research pipeline (h-e1 predicted V ∈ [0.29, 0.41], observed V partially outside range; h-e1-v3 used the same gate and obtained the same result; h-e1-v3-v4 updated the gate to the empirically observed range V ∈ [0.40, 0.57] and achieved all five indicators passing)."
- **Issue**: Internal pipeline hypothesis IDs (h-e1, h-e1-v3, h-e1-v3-v4) are inappropriate in a submitted paper — readers cannot interpret them and they break the narrative.
- **Suggested replacement**: "This recalibration required three experimental iterations: initial gate bounds predicted V ∈ [0.29, 0.41], but two successive runs confirmed empirical results fell above the predicted ceiling. The gate bounds were updated to the empirically observed range V ∈ [0.40, 0.57], at which point all five threshold levels passed."
- **Priority**: HIGH — should fix before submission

**HRN-002** (BR-MINOR-001): Discussion section ordering
- **Location**: Section 6 header structure
- **Issue**: "6.2 Connection to Prior Work" is an unusual placement for prior work discussion (typically in Introduction/Related Work). In Discussion, readers expect Interpretation → Limitations → Future Work. Minor reorganization could strengthen the Discussion.
- **Suggested fix**: Consider merging 6.2 into 6.1 or retitling as "6.2 Implications for Prior Estimates and Future Work"
- **Priority**: LOW — acceptable as-is for most venues

### Clarity

**HRN-003** (SE-MINOR-001): Reproducibility parenthetical in Section 3.6
- **Location**: Methodology Section 3.6
- **Current text**: "confirming identical V values across runs (V = 0.4021–0.5696 for k=10–k=40, V = 0.5293 for k=50)"
- **Issue**: The parenthetical implies V=0.5293 is outside the range 0.4021–0.5696, but it isn't. Confusing to readers.
- **Suggested replacement**: "confirming identical V values across runs (V ranges from 0.4021 at k=10 to 0.5696 at k=40, declining slightly to 0.5293 at k=50 due to Spanish saturation)"
- **Priority**: MEDIUM

**HRN-004** (R2 additional): Introduction — "Cramér's V reaches 0.57 at k=40"
- **Location**: Introduction paragraph 2
- **Current text**: "Cramér's V — a standard measure of association magnitude in contingency tables — reaches 0.57 at k=40"
- **Note**: Actual V at k=40 is 0.5696, which rounds to 0.57. This is acceptable rounding for the introduction's informal framing, but the exact value 0.5696 appears in Table 1. No correction needed, but a reader comparing Intro to Table 1 might notice. Consider saying "V ≈ 0.57 at k=40" or "V = 0.5696 at k=40" for precision.
- **Priority**: LOW

**HRN-005**: Figure caption for Figure 4
- **Location**: Figure Captions section
- **Current text**: "The gap peaks at 72.7pp at k=30 and remains above 60pp across the full practical range."
- **Issue**: The paper text (Section 5.4) says "remains above 71pp through k=50" but the caption says "above 60pp". The actual gap at k=50 is es=100% − de=28.9% = 71.1pp. Both are technically true (71pp > 60pp), but the caption understates the finding. Consider updating caption to "remains above 71pp" for consistency with Section 5.4.
- **Priority**: MEDIUM — minor inconsistency between text and caption

### Citation / Reference

**HRN-006** (SE-MINOR-003): Singh et al. 2026 missing from References
- **Location**: Related Work Section 2.3 cites "Singh et al. [2026]" but no such entry appears in the references section at the end of 06_paper.md or 06_references.bib
- **Also noted**: The Related Work section in 02_related_work.md cites "Singh et al. [2024] (Repetition over Diversity)" — note the year change from 2024 to 2026 across sections
- **Required action**: Verify correct year and add to References/BibTeX
- **Priority**: HIGH — missing citation is a rejection reason

**HRN-007** (SE-MINOR-002): Jansen et al. 2022 citation accuracy
- **Location**: Section 2.3: "Jansen et al. [2022] find that standard perplexity filtering breaks down on multilingual heterogeneous data."
- **Issue**: The actual Jansen et al. 2022 paper ("Perplexed by Quality: A Perplexity-based Method for Adult and Harmful Content Detection in Multilingual Heterogeneous Web Data") focuses on harmful content detection, not quality filter retention bias. The characterized finding may be an overgeneralization.
- **Required action**: Verify the actual claim made in Jansen et al. 2022 and either adjust the summary or replace with a more appropriate citation.
- **Priority**: HIGH — incorrect citation characterization is a rejection reason

---

## Recommended Priority

1. **Fix First** (before submission):
   - HRN-001: Remove pipeline IDs from Section 5.5
   - HRN-006: Add missing Singh et al. citation to References
   - HRN-007: Verify Jansen et al. 2022 characterization

2. **Fix Second** (improves clarity):
   - HRN-003: Reproducibility parenthetical
   - HRN-005: Figure 4 caption consistency

3. **Optional** (stylistic):
   - HRN-002: Discussion section ordering
   - HRN-004: Introduction V rounding

---

*Note: MAJOR issues (BR-MAJOR-001, SE-MAJOR-001) were auto-fixed in 06_paper_r1.md and are NOT included here. These notes cover only issues NOT auto-fixed.*
