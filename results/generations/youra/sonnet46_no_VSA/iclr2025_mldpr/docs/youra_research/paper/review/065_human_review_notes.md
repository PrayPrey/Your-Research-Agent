# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> These issues do NOT block paper acceptance and were NOT auto-fixed.
> Address before final submission.

**Date**: 2026-08-03  
**Rounds Completed**: 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 2 |
| Style | 3 |
| Clarity | 2 |
| References (HIGH priority) | 1 bundle (4 refs) |
| Missing data | 1 |

---

## Round 1 Issues

### Grammar

**M2-G1** — Section 2.1, two consecutive sentences begin with "Koch et al."

> Current: "Koch et al. establish a 87-task taxonomy... Their methodology provides the h-e2 panel... Where Koch et al. characterize concentration trends..."

Suggested: Vary the subject. E.g., "Their taxonomy provides..." for the second sentence, keeping "Koch et al." for the first introduction only.

---

**M3-G2** — Abstract: "plurality benchmark displacement" is undefined on first use in the abstract.

Readers unfamiliar with the papers-with-code ecosystem may not understand "plurality" immediately. The term is defined in Section 1 but not in the Abstract.

Suggested: Add brief parenthetical in Abstract, e.g., "plurality benchmark displacement (where a benchmark loses its status as the highest-performing benchmark for a task)" — or trust that the venue target audience knows the term.

---

### Style

**M1-S1** — Section 6.5 "On the Value of Principled Nulls" could be a forward hook rather than a terminal observation.

The insight "A null under poor measurement is uninformative. A null under validated measurement... definitively rules out a predictor class" is compelling enough to appear earlier (e.g., as the final paragraph of Introduction or the opening of Discussion). As the last Discussion section it reads as an afterthought.

Suggested: Consider moving the first two sentences of 6.5 to the end of the Introduction or as a bridge into Discussion.

---

**M4-S2** — "h-e2 panel" introduced in Abstract without expansion.

The term appears in the abstract: "258 complete-case rows from the h-e2 panel." The expansion only appears in Section 3.1. For venue readers unfamiliar with the pipeline, this may read as jargon.

Suggested: Either expand once in abstract ("h-e2 panel (87-task Papers With Code dataset)") or replace "h-e2 panel" with "our dataset" in the Abstract only.

---

**M5-S3** — Section 6.2 explanation order (E1 before E2) may benefit from reordering.

E2 (construct validity gap — paper_url is paper-level, not institution-level) is arguably the most important explanation and directly motivates future work. E1 (different predictor) is also important but is essentially a framing point already made in Section 5.4. Putting E2 first would emphasize the construct validity argument more prominently.

Suggested: Swap E1 and E2 order, with a bridging sentence. Optional — purely rhetorical preference.

---

### Clarity

**M6-C1** — P3 Kaplan-Meier: no numeric log-rank p-value reported.

Section 5.3 describes Q1 vs Q4 KM curves as "no meaningful separation" and relies on "visual inspection." For a quantitative paper, including the log-rank test p-value would strengthen P3 evidence considerably. The p-value may be available in `experiment.log` or can be extracted from lifelines.

Action: Extract log-rank p-value from `h-m1/code/experiment.log` or rerun `lifelines.statistics.logrank_test(Q1_durations, Q4_durations, Q1_events, Q4_events)`. Add as a one-line sentence: "Log-rank test: p = X.XX (Q1 vs Q4)."

---

**M7-C2** — EPV ≈ 86 is stated but event count is not explicitly reported.

The paper states "EPV ≈ 86" in several places. EPV = events / predictors_in_M1 = N_events / 1 implies N_events ≈ 86. But the exact event count (number of displacement events in 258 rows) is never stated explicitly. A reviewer may ask "How many displacements were actually observed?"

Suggested: Add one line in Section 3.1 or Table 2: "Of 258 complete-case rows, N_events = [exact count] displacement events (EPV = N_events / 1 ≈ 86)."

---

## Round 2 Issues

### References (HIGH PRIORITY — Must Fix Before Submission)

**M-REF-1** (HIGH) — Four references unverified via Semantic Scholar during pipeline:

1. **`ott2022benchmark`**: Cited as "Ott et al. 2022 (Nature Communications, 3765 benchmarks, breadth→saturation)." Multiple Semantic Scholar queries returned 0 results. Needs manual verification of exact title, authors, DOI, volume/page. If it does not exist as cited, the Related Work claim must be removed or replaced.

2. **`paullada2021data`**: Cited as "Paullada et al. 2021 (671 citations, dataset lifecycle governance)." Multiple queries returned 0 results. Likely published in *Patterns* (Cell Press) or NeurIPS Datasets & Benchmarks track. Verify full citation.

3. **`rogers2003diffusion`**: Classic book — "Diffusion of Innovations" by Everett M. Rogers. Not in Semantic Scholar (books often absent). Verify: edition (5th, 2003 is standard), publisher (Free Press), ISBN. Standard citation is correct but should be confirmed.

4. **`iclr2025benchmarking`**: Cited as "ICLR 2025 workshop on benchmarking." Workshop proceedings may not have a stable DOI or URL. Verify exact workshop name, date, and URL. If proceedings are not formally published, cite as a URL-only reference.

**Action required**: Manual web search for each reference before submission. Confirm title, authors, year, venue. Update `06_references.bib` accordingly.

---

## Recommended Priority

1. **Fix First** (HIGH): Unverified references (M-REF-1) — could invalidate Related Work claims if references are incorrect
2. **Fix Second** (MEDIUM): Log-rank p-value for KM Q1 vs Q4 (M6-C1) — strengthens P3 evidence
3. **Fix Third** (MEDIUM): Explicit event count for EPV calculation (M7-C2) — common reviewer question
4. **Consider** (LOW): Grammar issues M2-G1, M3-G2 — improve readability
5. **Optional** (LOW): Style issues M1-S1, M4-S2, M5-S3 — rhetorical preference

---

*These issues do not block paper acceptance but improve overall quality and reduce reviewer attack surfaces.*
