# Human Review Notes
> Purpose: Minor issues collected during adversarial review for human review.
> v2.0: These issues are NOT auto-fixed by AI.

Generated: 2026-05-04
Rounds Completed: 1

## Summary by Category
| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 4 |
| Clarity | 2 |
| Formatting | 0 |

## Round 1 Issues

### N1 [Style] — "40×" in abstract vs "43×" in results — inconsistent rounding
- **Location:** Abstract final sentence ("conceal 40× contamination differentials") vs. Abstract opening / Section 5.1 ("43× the rate")
- **Issue:** The abstract uses both figures — "43×" for the medicine/mathematics ratio and "40×" for the general sub-task differential — but without clear labeling. Readers may perceive inconsistency. The 40× is the full-range ratio (17.3% / 0.4% = 43.25×, rounded down to 40×); the 43× is the same underlying comparison but rounded differently in different locations.
- **Recommended action:** Decide on one rounding convention and apply consistently, OR add a brief clarifying parenthetical in the abstract distinguishing the two figures. For example: "conceal >40× contamination differentials (up to 43× between top and bottom sub-tasks)."
- **Priority:** Medium

### N2 [Style] — Format sensitivity ρ=0.74 vs unrounded 0.7375 — state rounding convention
- **Location:** Section 3.5, Section 5.1 WIMBD validation note (both cite ρ=0.74)
- **Issue:** The text states Spearman ρ=0.74 for both the WIMBD pipeline validation and the format sensitivity analysis. If these are two distinct correlations that happen to round to the same value, this should be made explicit. If ρ=0.74 is the same number reused for two different analyses, a note confirming they refer to the same measurement is needed. The unrounded value (e.g., 0.7375 or 0.7421) should be stated or a rounding note added.
- **Recommended action:** Report two decimal places consistently (e.g., ρ=0.74) and confirm whether the WIMBD ρ=0.74 (Section 5.1) and format sensitivity ρ=0.74 (Section 3.5 / Figure 6) are distinct values or the same. Add "(rounded to 2 d.p.)" or report 3 significant figures.
- **Priority:** Low

### N3 [Clarity] — 13-gram contamination does not distinguish question vs answer leakage — missing limitation
- **Location:** Section 6.2 Limitations (not currently listed)
- **Issue:** The 13-gram containment method measures overlap of the full concatenated text unit (question + all answer choices) against the corpus. This does not distinguish between: (a) the question stem appearing in training data, (b) the correct answer appearing in training data, or (c) all answer choices appearing together. The contamination severity differs substantially between these cases — question leakage is less directly harmful than answer leakage. This is a methodological limitation not currently disclosed.
- **Recommended action:** Add as L5 in Section 6.2: "Our 13-gram containment measure does not distinguish between question-stem leakage and answer-leakage; the former is less harmful to evaluation validity than the latter. Future work should apply answer-aware contamination metrics."
- **Priority:** Medium

### N4 [Style] — Scaling factor source citation and uncertainty — cite source more precisely
- **Location:** Section 3.3 Corpus Indexing ("literature-calibrated scaling factors (C4: ×0.62 [Dodge et al., 2021]; RedPajama: ×0.88 [TogetherComputer, 2023])")
- **Issue:** The scaling factors ×0.62 and ×0.88 are cited to the corpus documentation papers, but these papers may not explicitly state these factors — they may be derived values. If the factors are derived from sampling experiments reported in those papers, the derivation should be briefly described. If they are directly stated in the cited papers, the specific table or section should be noted. Additionally, the M5 fix adds uncertainty language (±10–20%), but the source of this uncertainty estimate is not cited.
- **Recommended action:** Either (a) add a brief footnote or parenthetical explaining how ×0.62 and ×0.88 were derived from the cited literature, or (b) add a supplementary appendix with the derivation. The ±10–20% uncertainty estimate should similarly be sourced or described as "estimated from reported sampling variance."
- **Priority:** Medium

### N5 [Clarity] — BBH treated as single aggregate vs MMLU 57-way split — add methodological note
- **Location:** Section 3.2 Benchmark Sub-tasks, Section 4.1 Benchmarks table, Section 5.3 RQ3 (n=2 commonsense)
- **Issue:** MMLU is analyzed at 57-sub-task granularity, while BIG-Bench Hard is treated as a single aggregate unit. This asymmetry directly caused the h-m2 underpowering (n=2 commonsense rather than n=24+). The current text mentions BBH has 27 sub-tasks (referenced in Section 6.2 L3 as "n=24 commonsense") but does not explain why BBH was not split to sub-task granularity in the main analysis. The methodological rationale for this asymmetric treatment is absent.
- **Recommended action:** Add a sentence to Section 3.2 or 4.1 explaining why BBH was aggregated (e.g., "BIG-Bench Hard is treated as a single aggregate in the main analysis due to [reason]; sub-task-level analysis is left for future work and would increase commonsense category power from n=2 to n≥24."). This also helps readers understand that the underpowering was a deliberate methodological choice, not an oversight.
- **Priority:** High (directly affects interpretability of h-m2 result)

### N6 [Style] — Figure 1 caption self-explanatory status — verify visually during revision
- **Location:** Appendix Figure Captions, Figure 1
- **Issue:** The Figure 1 caption states "The distribution spans 0.4%–17.3%, confirming highly non-uniform contamination" — this is adequately self-explanatory. However, during any final revision pass, a human reviewer should visually confirm that the actual figure file (contamination_rates_barplot.png) matches the caption description, particularly: (a) the sort order is descending, (b) all 59 sub-tasks are visible or the axis labels are legible, and (c) the y-axis range covers 0–17.3%. This cannot be verified by text-based AI review.
- **Recommended action:** During final human revision, open figures/contamination_rates_barplot.png and verify caption accuracy. No text change required if figure matches.
- **Priority:** Low (visual verification only)

## Recommended Priority

| Priority | Issue | Action Required |
|----------|-------|----------------|
| High | N5: BBH aggregation rationale | Add methodological note in Section 3.2/4.1 |
| Medium | N1: 40× vs 43× rounding | Clarify or unify rounding in abstract |
| Medium | N3: Question vs answer leakage | Add as L5 in Section 6.2 Limitations |
| Medium | N4: Scaling factor derivation | Add footnote or appendix for ×0.62, ×0.88 |
| Low | N2: ρ=0.74 rounding convention | Confirm distinctness; add rounding note |
| Low | N6: Figure 1 visual verification | Human visual check of figure file |

---

## Round 2 Issues

### R2-N1 [Style] — "40×" in abstract/conclusion vs "43×" in Introduction/Results — recommend standardizing to "43×"
- **Location:** Abstract final sentence ("conceal 40× contamination differentials"); Conclusion item (1) ("varies by 40×") vs. Introduction opening ("43 times the rate") and Section 5.1 ("vary by 40×" in finding, but "43×" in Table 1 row context)
- **Issue:** The actual measured differential is 43.25× (17.3% / 0.4%). "40×" appears in abstract/conclusion summary contexts as a rounded figure, while "43×" is used in introduction and results. This internal inconsistency may confuse reviewers who notice the discrepancy between abstract and results.
- **Recommended action:** Standardize to "43×" throughout (the actual 43.25× value), or use "more than 40×" consistently and add a parenthetical "(specifically 43× for the professional_medicine/high_school_mathematics pair)" where precision matters.
- **Priority:** Medium

### R2-N2 [Clarity] — Format sensitivity rho=0.74 only computed for The Pile (h-e1); presented as general methodological robustness
- **Location:** Section 3.5 Sensitivity Analysis; Contribution 4 in Introduction
- **Issue:** The format sensitivity ρ=0.74 (question+choices vs question-only) was computed for The Pile analysis only (h-e1). Contribution 4 states "rank-based contamination analysis is robust to text format variations (ρ=0.74)" without restricting this to The Pile, implying general robustness across all three corpora.
- **Recommended action:** Add a per-corpus scope note: "(computed for The Pile; assumed portable to C4/RedPajama given consistent MinHash methodology)" in Contribution 4 and Section 3.5, or explicitly restrict the claim to "for The Pile analysis."
- **Priority:** Medium

### R2-N3 [Clarity] — ±5pp WIMBD validation tolerance threshold not explicitly justified; professional_medicine passes at 4.8pp (very close to boundary)
- **Location:** Section 5.1 WIMBD validation note
- **Issue:** The paper states all five checked sub-tasks are "within ±5 pp of published values" but does not justify why ±5pp is the chosen threshold. The professional_medicine comparison (pipeline: 17.3%, WIMBD: 12.5%) yields a 4.8pp discrepancy — passing the threshold by only 0.2pp. Any slightly stricter threshold would cause a validation failure, yet no justification for the ±5pp choice is provided.
- **Recommended action:** Add one sentence justifying the threshold: "We adopt ±5pp as the validation tolerance, consistent with the ±4–8pp scaling uncertainty estimated for the C4/RP measurements in Section 3.3." This grounds the validation threshold in the pipeline's own uncertainty estimates.
- **Priority:** Medium

### R2-N4 [Clarity] — No temporal limitation noted; The Pile v1 dates from 2021, BIG-Bench Hard from 2022/2023; some test set items may postdate corpus creation
- **Location:** Section 6.2 Limitations (not currently listed)
- **Issue:** The Pile v1 was assembled in 2020–2021. BIG-Bench Hard was released in 2022/2023, meaning some BBH test items postdate The Pile's assembly. For these items, contamination via corpus memorization is temporally impossible — the test items did not exist when the corpus was built. This temporal asymmetry is not discussed and is relevant to the contamination pathway interpretation.
- **Recommended action:** Add as optional L5 in Section 6.2: "The Pile v1 was assembled in 2020–2021; BIG-Bench Hard (2022/2023) and some MMLU sub-tasks postdate Pile assembly, limiting the contamination pathway for those items. Future work should account for temporal ordering in contamination attribution."
- **Priority:** Low (does not affect MMLU-dominated results; BBH is a single aggregate data point)
