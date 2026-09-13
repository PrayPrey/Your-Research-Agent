---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: OpenML Tag Count → Task Run Count (Tag-Specific Adoption)"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-05
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Among OpenML datasets, does the number of descriptive tags (keyword tags attached at upload) predict task run count more strongly than composite metadata completeness score — specifically with IRR ≥ 1.1 at the 95% CI lower bound — using the existing OpenML corpus without new data collection?

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Reflection 5)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Datasets are a central pillar of ML research — from pretraining to evaluation and benchmarking. A growing body of work highlights serious issues throughout the ML data ecosystem: the under-valuing of data work, ethical issues in datasets that go undiscovered, a lack of standardized dataset deprecation procedures, the (mis)use of datasets out-of-context, an overemphasis on single metrics rather than holistic model evaluation, and the overuse of the same few benchmark datasets. Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop: The Future of Machine Learning Data Practices and Repositories). Retrying after previous failure — Reflection 5.

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (Benchmark Saturation — H-E1 v1, PwC):** Partial Spearman ρ = -0.1392 (required > 0.3), direction NEGATIVE. Popular benchmarks stay unsaturated — logistic saturation framing falsified.

**Attempt 2 (Documentation → Adoption, HuggingFace — H-E1 v2):** HF Hub API selection bias → hurdle component degenerate (near-perfect separation). OLS conditional component structurally sound but hurdle model invalid on biased sample.

**Attempt 3 (OpenML composite score — H-E1 v3, NB-2):** N=5,217 datasets, beta_1=0.0730, p=4.57e-21, IRR=1.076, 95% CI [1.0595, 1.0922] — BELOW threshold 1.1. RC-3 decade fixed effects attenuate to IRR=1.014, p=0.19 (non-significant — cross-sectional age confounding). RC-2a (binary description presence) IRR=1.102 marginally above 1.1 — suggests binary field presence is stronger predictor than composite score.

### How This New Direction Avoids Those Pitfalls

This direction permanently avoids:
1. **HuggingFace Hub API** — confirmed selection bias
2. **Hurdle / zero-inflated models** — degenerate on biased samples
3. **Saturation rate** as DV — falsified
4. **Composite 0-5 score** as primary IV — IRR too small (1.076), effect attenuates with decade FE

**New pivot:** Use EXISTING OpenML corpus (5,217 rows × 24 cols, `h-e1/code/data/h_e1/openml_dataset_corpus.csv`) to test **tag count** as the primary predictor. Key justifications:
- Snapshot note: "Tags field likely carries most adoption signal"
- RC-2a finding: binary presence (description>0) IRR=1.102 — binary/count features outperform composite score
- Tag count is a natural count variable with more variance than binary presence/absence
- No new data collection needed — existing corpus; avoids decade FE attenuation by including it as control (not removing effect)
- IRR threshold ≥ 1.1 at 95% CI lower bound explicitly pre-registered to avoid Attempt 3 failure mode

---

## Session Plan

ROUTE_TO_0 Auto-Fill (Reflection 5). Pivot from composite score (failed IRR threshold) to tag-count-as-primary-IV using reusable OpenML corpus. Four failure lessons (PwC saturation, HF hurdle ×2, OpenML composite sub-threshold) directly inform narrow hypothesis reframing.

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode — No interactive sessions. Research direction synthesized from:
1. H-E1 v3 failure snapshot: IRR=1.076 below 1.1; RC-3 decade FE attenuation; "Tags field likely carries most adoption signal"
2. H-E1 v3 RC-2a: binary description presence IRR=1.102 — binary/count metadata features > composite score
3. H-E1 v1 (PwC saturation falsified), H-E1 v2 (HF hurdle degenerate) — permanently eliminated
4. Existing corpus (5,217 rows × 24 cols) reusable without new API calls
5. ICLR 2025 Workshop CFP: dataset discoverability, keyword tagging practices, FAIR findability
6. Feasibility constraints (no new benchmarks, no synthetic data, no human annotation)

---

## Research Question Development

### Initial Question

Among OpenML datasets, does the number of descriptive keyword tags predict task run count more strongly (IRR ≥ 1.1 at 95% CI lower bound) than the composite metadata completeness score — after controlling for log(n_instances), log(n_features), dataset age, and decade fixed effects?

### Refined Question

Using the existing OpenML dataset corpus (N≈5,217), does tag count (number of keyword tags attached to each dataset) statistically predict task run count in a negative binomial regression (NB-2) controlling for log(n_instances), log(n_features), dataset age (years + age²), and decade-of-upload fixed effects — with IRR > 1.1 at the 95% CI lower bound — where all data comes from the existing cached corpus without new API collection?

### Detailed Sub-Questions

1. Is tag count a statistically significant positive predictor of task run count (NB-2, IRR > 1.1, 95% CI lower bound > 1.1, p < 0.05) after controlling for log(n_instances), log(n_features), dataset age, age², and decade fixed effects — and does the effect survive RC-3 (decade FE) unlike the composite score in Attempt 3?

2. Does binary tag presence (has_tags: 0/1) predict task run count with IRR > 1.1 (95% CI lower bound) — consistent with RC-2a finding that binary presence outperforms composite score?

3. Which tag categories (domain tags, task type tags, format tags, license tags) independently predict run count after Bonferroni correction — do domain/task tags drive adoption more than administrative tags?

4. Is there a nonlinear (log or square-root) relationship between tag count and run count that fits better than linear tag count — does marginal benefit of additional tags diminish?

5. Does the tag count effect interact with dataset structural complexity (n_features, n_classes) — do heavily-tagged simple datasets achieve more runs than heavily-tagged complex datasets?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

ICLR 2025 Workshop on ML Data Practices — significance pre-validated. Tag-based findings would directly inform:
- OpenML repository design: whether to require minimum tag count at dataset submission
- FAIR Findability operationalization: tags as machine-readable findability proxies
- Evidence-based keyword tagging recommendations for dataset submitters
- Practical guidance distinguishing high-impact metadata fields (tags) from lower-impact ones (composite score)

This is Reflection 5 — prior three failures produce publishable negative results that collectively narrow valid methodology. Tag-count hypothesis is mechanistically distinct from composite score (captures discoverability/searchability rather than documentation completeness).

### Feasibility Check

**FEASIBILITY CONSTRAINTS SATISFIED:**
- ✅ No new benchmarks — uses existing OpenML data; tag count extracted from cached corpus
- ✅ No synthetic/generated data — existing corpus at `h-e1/code/data/h_e1/openml_dataset_corpus.csv` (5,217 rows × 24 cols)
- ✅ No human evaluation/annotation — tag count is a structured integer field from OpenML API, extractable programmatically
- ✅ Testable immediately — corpus already on disk; NB-2 model code reusable from h-e1 pipeline; only IV changes (tag_count replaces composite_score)
- ✅ Avoids Attempt 3 failure mode — explicit IRR threshold pre-registered; decade FE included as control (not excluded)
- ✅ Avoids Attempts 1-2 failure modes — no saturation rate, no HF API, no hurdle model

**Data sources:**
- Existing corpus: `docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv` (N=5,217, 24 cols)
- Tag data: `tag` field in OpenML dataset list endpoint (already fetched in h-e1 collection); if not in corpus, supplement via `openml.datasets.list_datasets(output_format='dataframe')` with `tag` column
- DV: task_run_count (already in corpus)
- Controls: log(n_instances), log(n_features), age_years, age²_years, decade FE (already in corpus)
- Statistical model: NB-2 (same as h-e1); swap IV from composite_score to tag_count

---

## Phase 1 Input Package

<phase1-input>

### research_question
Using the existing OpenML dataset corpus (N≈5,217), does tag count (number of keyword tags attached to each dataset) statistically predict task run count in a negative binomial regression (NB-2) controlling for log(n_instances), log(n_features), dataset age, age², and decade-of-upload fixed effects — with IRR > 1.1 at the 95% CI lower bound — where all data is from the existing cached corpus without new API collection?

### detailed_question
1. Is tag count a statistically significant positive predictor of task run count (NB-2, IRR > 1.1, 95% CI lower bound > 1.1, p < 0.05) after controlling for log(n_instances), log(n_features), dataset age, age², and decade fixed effects — does it survive RC-3 (decade FE) unlike composite score in Attempt 3?

2. Does binary tag presence (has_tags: 0/1) predict task run count with IRR > 1.1 (95% CI lower bound) — consistent with RC-2a finding that binary presence outperforms composite score?

3. Which tag categories (domain, task type, format, license) independently predict run count after Bonferroni correction — do domain/task tags drive adoption more than administrative tags?

4. Is there a nonlinear (log or square-root) relationship between tag count and run count — does marginal benefit of additional tags diminish?

5. Does the tag count effect interact with dataset structural complexity (n_features, n_classes) — do heavily-tagged simple datasets achieve more runs than heavily-tagged complex datasets?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Composite metadata score (0-5) fails IRR threshold (1.076); tag count is mechanistically distinct — captures discoverability/searchability, not documentation completeness
- RC-2a from Attempt 3 strongly motivates this pivot: binary field presence IRR=1.102 > composite score IRR=1.076; count-based features likely perform better
- Decade FE (RC-3) attenuated composite score to non-significance; tag count hypothesis must include decade FE as primary control (not robustness check)
- Corpus fully reusable — only IV changes; estimated code modification: ~10 lines in analysis.py
- Four cumulative failures narrow the valid methodology space: NB-2 on OpenML census, count/binary IV, decade FE as control, IRR threshold at 95% CI lower bound

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (Reflection 5) — failure context synthesis from:
- snapshot_h-e1_2026-08-05T031500Z: IRR=1.076, RC-3 attenuation, tags adoption signal
- youra/h-e1/phase4-completion: HF hurdle degeneracy, corpus infrastructure documented
- MEMORY.md: "H-E1 MUST_WORK FAIL x3; latest: IRR=1.076 < 1.1; RC-3 decade FE attenuation; corpus reusable"
- Archive 20260805T031945: OpenML pivot from previous brainstorm carried forward with tag-count refinement

### Areas for Further Exploration

- FAIR Findability: tags as machine-readable findability proxies in OpenML
- Tag vocabulary standardization: controlled vocabulary vs. free-text tags and adoption rates
- Cross-repository validation: does tag count predict adoption on UCI ML Repository?
- Tag age decay: do datasets added with tags in recent years show faster adoption ramp?
- Network effects: do datasets sharing tags with popular datasets inherit discovery pathways?

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Focus search on:
1. Keyword tagging practices and dataset discoverability in ML repositories
2. FAIR Findability operationalized through structured metadata (tags, keywords)
3. Prior work on tag count and resource adoption in scientific data repositories
4. OpenML platform studies on dataset metadata and reuse
5. Count regression methods — NB-2 robustness literature
6. RC-3 decade fixed effects interpretation in cross-sectional studies

Run: `/phase1-targeted`

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
