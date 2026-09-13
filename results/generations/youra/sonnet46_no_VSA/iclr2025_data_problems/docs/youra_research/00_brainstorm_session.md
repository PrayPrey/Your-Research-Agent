---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Language-Adaptive Perplexity Thresholds in FM Pretraining Corpora"
pipeline_project_id: "811d00b3-1493-4fd6-b49b-009a67c9b445"
---

# Research Brainstorm Session Results

**Session Date:** 2026-07-30
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Investigating whether language-adaptive (per-language-calibrated) perplexity thresholds in FM pretraining corpus curation produce a more equitable document retention distribution across language groups compared to global perplexity thresholds — testable on RedPajama-v2 quality signal metadata and existing multilingual benchmark performance data, with no API dependency, no model inference, and no GPU requirement.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode) — Seventh attempt after six prior failures (Attempts 1–3: infini-gram API blocked; Attempt 4: TRAK/DataInf gradient compute infeasible; Attempt 5: per-item Pythia lm-eval inference infeasible; Attempt 6: data curation bias direction inverted in h-m1 — perplexity filters exclude English, not low-resource languages, requiring directional redesign). This attempt applies the h-m1 empirical finding directly: global perplexity thresholds ARE biased (Cramér's V = 0.29–0.41, p ≈ 0) but the bias direction is that English is disproportionately excluded. The new question asks whether language-stratified (adaptive) thresholds correct this inverted bias — measurable using existing RedPajama-v2 quality signal Parquet files with no new data generation.

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Foundation models (FMs) have become central to modern machine learning, with data playing a crucial role in their development and sparking increased attention to data-related challenges such as curation and attribution. Adapting traditional data-centric methods to FMs is challenging due to the scale of both data and model architectures. The second DATA-FM workshop at ICLR 2025 addresses persistent and emerging data-related challenges in FM deployment, spanning data collection/curation, attribution, copyright, synthetic data, fairness, and benchmark evaluation.

**Source Type:** Workshop CFP / Structured Input (ICLR 2025 DATA-FM Workshop)

**Feasibility Constraints (Pipeline-Enforced):**
- REJECT: Ideas requiring new benchmarks, rubrics, or scoring frameworks
- REJECT: Ideas requiring synthetic/generated data or future follow-up data
- REJECT: Ideas requiring human evaluation, annotation, or subjective scoring
- ACCEPT ONLY: Hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Lessons from Previous Attempts

### Attempt 1–3: N-gram Contamination Detection via infini-gram API (h-e1, h-e2, h-e2-v2, h-e2-v3, h-c1) → FAIL / LIMITATION

**What was tried:** Measuring 13-gram overlap between benchmark items and Pile/C4/Dolma corpora using infini-gram HTTP API.

**Why it failed:** IP-level AWS WAF block (HTTP 403) after high query volume; full corpus indexing infeasible (825 GiB); streaming at max_docs < 1M gave near-zero match probability.

**Lesson for Attempt 7:** Zero HTTP API dependencies. Use only static pre-computed files from HuggingFace.

### Attempt 4: Gradient-based Data Attribution (TRAK/DataInf on Pythia) → ROUTE_TO_0

**What was tried:** Influence function methods on Pythia models against MMLU items.

**Why it failed:** CUDA kernel compilation risk; gradient computation over large corpora infeasible on CPU.

**Lesson for Attempt 7:** No GPU, no gradient computation, no CUDA. Pure statistical analysis on tabular metadata only.

### Attempt 5: Contamination Impact via DiD Panel Model (h-m1) → MUST_WORK_FAIL / SYNTHETIC_DATA_INVALID

**What was tried:** DiD panel: contamination × log(Pythia parameters) interaction on per-item MMLU accuracy.

**Why it failed:** 4/5 Pythia model sizes used synthetic accuracy values; real inference requires ~2–4 GPU-hours.

**Lesson for Attempt 7:** No model inference of any kind. All required data must exist as static pre-downloaded files.

### Attempt 6: Data Curation Bias via Global Perplexity Filter Retention Rates (h-m1 redesign) → MUST_WORK_FAIL / DIRECTION_INVERTED

**What was tried:** Testing whether global perplexity filters disproportionately exclude low-resource-language documents in RedPajama-v2 (208,263 rows, 5 model sizes).

**Why it failed:** Direction was empirically inverted — English has higher perplexity distribution in CommonCrawl web text than low-resource languages. Global perplexity thresholds disproportionately EXCLUDE English (retention 3.7%–36.5% at τ = 10th–50th percentile), while Italian (low-resource proxy) retains 18.2%–88.1%. The disparity IS real and strong (Cramér's V = 0.29–0.41, all Holm p ≈ 0), but the direction refutes the "low-resource languages hurt most" hypothesis.

**Critical empirical finding preserved from h-m1:**
- Disparity mechanism: CONFIRMED (Cramér's V = 0.29–0.41)
- Direction: English is MOST excluded by global perplexity thresholds in CommonCrawl web text
- Implication: Global perplexity calibration is language-biased, but the bias disadvantages high-resource languages at corpus-level, not low-resource ones
- Pipeline infrastructure: All correct, 27/27 tests passing, 6 figures generated — reusable

**Lesson for Attempt 7:** The h-m1 result is high-value: it CONFIRMS a real, strong disparity. The new hypothesis should BUILD on this finding rather than contradict it. The question "do language-adaptive thresholds correct this inverted bias?" is directly motivated by the h-m1 empirical result and testable on the same RedPajama-v2 metadata without new data.

### How THIS Direction (Attempt 7) Avoids ALL Prior Pitfalls

- **NO HTTP API:** Uses only RedPajama-v2 quality signal Parquet files (togethercomputer/RedPajama-Data-V2) — pre-computed static files, no rate-limit risk
- **NO model inference:** Per-language perplexity percentile computation is pure statistics on existing perplexity scores already distributed in RedPajama-v2 quality signals
- **NO GPU/CUDA:** Pandas + scipy.stats on CPU, minutes to run
- **NO corpus streaming at scale:** Works on quality-signal metadata Parquet files, not raw document text
- **NO synthetic data:** All perplexity scores and quality signals are real existing artifacts published by corpus authors
- **NO new benchmarks:** Uses existing RedPajama-v2 quality signal fields (already computed); retention rate comparison is a derived statistic, not a new rubric
- **NO human annotation:** All signals are automated
- **Builds on confirmed h-m1 finding:** The disparity existence (Cramér's V ≥ 0.29) is already established — this attempt asks "what threshold design corrects it?"
- **Direction specified correctly:** Hypothesis direction now matches empirical reality from h-m1: English is most excluded; language-adaptive threshold should REDUCE this English-exclusion bias while potentially changing retention rates for other language groups

---

## Session Plan

ROUTE_TO_0 recovery (7th attempt) — directional redesign building on h-m1 empirical finding. The core shift: Attempt 6 asked "does the current filter create language bias?" and found YES (strong signal). Attempt 7 asks "does a language-adaptive threshold design reduce this bias, and by how much?" This is a constructive follow-on: same RedPajama-v2 metadata, same statistical framework, but now simulating language-stratified perplexity calibration (compute per-language percentiles from existing perplexity scores, apply language-specific thresholds, compare resulting retention distributions) and testing whether the Cramér's V drops from ≥ 0.29 to near-zero.

**CFP Track Alignment:**
- Primary: "Data Collection and Curation for Foundation Models" — directly addresses "practical strategies for curating data (filtering, mixing, repairing) tailored to FM training stages" with a concrete algorithmic comparison (global vs. adaptive threshold)
- Secondary: "Data and Society (Safety, Privacy, Fairness)" — language-adaptive filtering directly addresses equitable corpus composition
- Tertiary: "Benchmarks and Evaluations" — retention distribution shifts affect what languages FMs are trained on, with downstream benchmark implications

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode (7th attempt). Research components extracted from ICLR 2025 DATA-FM Workshop CFP with six rounds of failure context applied.

**Failure-Filtered Directional Redesign from h-m1:**

| Preserved from h-m1 | How Attempt 7 Uses It |
|---------------------|----------------------|
| RedPajama-v2 quality signals confirmed accessible | Same dataset, same Parquet format |
| Perplexity scores per document available | Use raw perplexity field to compute per-language percentiles |
| Cramér's V = 0.29–0.41 (strong disparity confirmed) | Baseline comparison point: adaptive threshold should reduce this |
| English retention: 3.7%–36.5% (most excluded) | Adaptive threshold should equalize English retention to ≥ 50th percentile |
| Italian retention: 18.2%–88.1% (least excluded) | Adaptive threshold may slightly reduce Italian retention |
| 208,263 rows pipeline ran correctly | Reuse same data loading and statistical test code |
| Statistical test infrastructure correct | Reuse chi-square + Cramér's V framework |

**Simulation Design (no new data required):**
- **Input:** RedPajama-v2 quality signal Parquet files (existing, pre-computed)
- **Global threshold baseline:** Apply τ = 10th/20th/30th/40th/50th percentile of FULL corpus perplexity distribution → compute per-language retention rates → Cramér's V (this is h-m1 result, already known)
- **Adaptive threshold comparison:** Compute τ_lang = k-th percentile of per-LANGUAGE perplexity distribution for each language group → apply language-specific threshold → compute resulting per-language retention rates → Cramér's V
- **Test:** Does Cramér's V decrease significantly (Δ ≥ 0.1) when switching from global to adaptive threshold? Does the English-exclusion gap close?
- **No new data generated:** Both conditions use the same existing perplexity scores — only the threshold computation method differs

---

## Research Question Development

### Initial Question

Given that global perplexity thresholds in FM pretraining corpus curation demonstrably create strong language-group retention disparities (Cramér's V = 0.29–0.41, confirmed in h-m1 on RedPajama-v2), does replacing the global threshold with a per-language percentile-calibrated threshold substantially reduce the retention disparity across language groups?

### Refined Question

**In RedPajama-v2 CommonCrawl quality signal metadata, does applying a language-adaptive perplexity threshold (τ_lang = k-th percentile of per-language perplexity distribution, for k ∈ {10, 20, 30, 40, 50}) produce a statistically significantly lower language-group retention disparity (Cramér's V) compared to the global perplexity threshold baseline — specifically, does ΔCramér's V ≥ 0.1 for at least 3 of 5 k values, with all group-level retention rates falling within [40%, 60%] of each other under the adaptive threshold?**

This question is:
- **Immediately testable:** RedPajama-v2 quality signal Parquet files are public static downloads with perplexity scores already computed; language ID is a pre-computed field — no new computation needed beyond sorting and percentile computation
- **Builds on confirmed h-m1 result:** Baseline Cramér's V (0.29–0.41) is already established — no need to re-measure the problem, only the solution
- **No new benchmarks:** Cramér's V and chi-square are standard statistics; retention rate is a pre-existing concept applied to existing fields
- **No synthetic data:** All perplexity scores and language IDs are real existing artifacts from corpus release
- **No human annotation:** All signals are automated pre-computed fields
- **No API dependency:** HuggingFace datasets library for static Parquet download only — no rate-limit risk
- **Feasible compute:** Load Parquet → group by language → compute per-language percentile → apply threshold → chi-square → Cramér's V. Minutes on CPU.
- **Avoids ALL prior failure modes:** No infini-gram, no corpus text streaming, no model inference, no gradient computation, no GPU, no inverted-direction trap (direction now matches empirical h-m1 reality)

### Detailed Sub-Questions

1. **Adaptive threshold effectiveness:** For each k ∈ {10, 20, 30, 40, 50}, does language-adaptive perplexity thresholding produce a Cramér's V ≤ 0.10 for the language-group × retained/removed contingency table — compared to the global threshold baseline of Cramér's V = 0.29–0.41?

2. **English retention correction:** Under the adaptive threshold (any k), does English retention rate rise from the baseline 3.7%–36.5% to ≥ 40% — correcting the disproportionate English exclusion identified in h-m1?

3. **Low-resource language trade-off:** Does applying language-adaptive thresholds reduce retention rates for previously over-retained language groups (Italian: 18.2%–88.1% under global threshold) to within 20pp of English retention rates — and is this reduction statistically significant (chi-square p < 0.01)?

4. **k sensitivity:** Is the disparity-reduction effect of adaptive thresholding robust across k values (consistent ΔCramér's V ≥ 0.1 for ≥ 3/5 k values), or does it only appear at specific threshold levels — indicating that threshold calibration method matters more than the specific percentile?

5. **Cross-language consistency:** Do all language groups (English, Spanish, French, German, Italian, and any other groups with n ≥ 1,000 in the RedPajama-v2 sample) show convergence toward a common retention rate band under adaptive thresholds, or do some language groups remain outliers — identifying languages that require additional calibration beyond simple percentile matching?

---

## Reference Papers

Not provided - will discover in Phase 1

*(Key candidate papers based on failure context + h-m1 empirical finding:*
- *Soldaini et al. 2024 "Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research" — filter pipeline details*
- *Weber et al. 2024 "RedPajama: an Open Dataset for Training Large Language Models" — quality signal documentation*
- *Wenzek et al. 2020 "CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data" — perplexity filtering methodology, language model used for perplexity scoring*
- *Kreutzer et al. 2022 "Quality at a Glance: An Audit of Web-Crawled Multilingual Datasets" — multilingual corpus quality bias analysis*
- *Raffel et al. 2020 "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" — C4 filter pipeline*
- *Dodge et al. 2021 "Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus" — C4 content bias*
- *Xue et al. 2021 "mC4 and mT5: A Multilingual Version of C4 and T5" — multilingual filtering considerations*
- *Bender et al. 2021 "On the Dangers of Stochastic Parrots" — data bias in language models)*

---

## Validation Results

### So What Test

**Why does this matter?**

The h-m1 experiment confirmed that global perplexity thresholds create strong, statistically significant language-group retention disparities in CommonCrawl-based corpora (Cramér's V = 0.29–0.41). This is an empirically established fact — not a hypothesis. What remains open is: **can a simple algorithmic fix (per-language percentile calibration) correct this disparity at the same threshold percentile?**

This matters because:
- Language-adaptive perplexity thresholds are a low-cost, practical modification to existing corpus curation pipelines — if they work, corpus curators can implement them today with minimal code change
- The ICLR DATA-FM CFP specifically calls for "practical strategies for curating data (filtering, mixing, repairing) tailored to FM training stages" and "addressing the side effects of data curation on fairness and ethics in FMs" — this addresses both
- The h-m1 empirical finding (English disproportionately excluded by global perplexity) is a counterintuitive result that requires follow-up: documenting the problem without proposing a solution would be an incomplete contribution
- If adaptive thresholds reduce Cramér's V from ≥ 0.29 to ≤ 0.10, this is a concrete, actionable finding with immediate practical value for corpus curation pipeline design
- If adaptive thresholds do NOT reduce the disparity, this is equally important: it would imply that the bias is not attributable to threshold calibration alone, pointing to deeper structural causes in the perplexity model (e.g., language model used for perplexity scoring is itself language-biased)

**Impact:** High — builds on confirmed empirical finding (h-m1), proposes and tests a practical solution, directly addresses DATA-FM CFP tracks on data curation and fairness; publishable at the intersection of "does the fix work?" research.

### Feasibility Check

**✅ PASSES all mandatory constraints:**
- Uses existing real datasets: RedPajama-v2 (togethercomputer/RedPajama-Data-V2 on HuggingFace) — publicly available static Parquet files with pre-computed perplexity scores and language IDs
- Uses existing quality-filter labels: RedPajama-v2 quality signals (perplexity score, language ID, dedup signal) are published pre-computed fields — no new filtering computation needed
- No new benchmarks or scoring rubrics: Cramér's V and chi-square test are standard existing statistics; language-adaptive threshold is a simple percentile computation on existing data
- No synthetic data: All perplexity scores and language IDs are real existing artifacts from RedPajama-v2 release
- No human annotation: All signals are automated pre-computed fields from corpus authors
- No model inference: Per-language percentile computation is pure arithmetic on tabular data — no model loading

**Avoids ALL prior failure modes:**
- ✅ No infini-gram API (Attempts 1–3)
- ✅ No GPU / CUDA / gradient computation (Attempts 4–5)
- ✅ No model inference of any kind (Attempt 5)
- ✅ No inverted-direction trap (Attempt 6): direction specified correctly — English is most excluded under global threshold; adaptive threshold should INCREASE English retention and DECREASE outlier retention
- ✅ No large local index build (> 10 GB)
- ✅ No live HTTP API dependency
- ✅ Baseline Cramér's V already established (h-m1): no need to re-run the baseline measurement from scratch — use h-m1 results as confirmed baseline, only need to run adaptive threshold simulation

**Testable immediately:** Yes — same RedPajama-v2 data loading pipeline from h-m1 (208,263 rows, 5 language groups) can be reused with minor modification: add per-language percentile computation step before threshold application. Estimated additional code: ~20 lines. Runtime: minutes on CPU.

---

## Phase 1 Input Package

<phase1-input>

### research_question
In RedPajama-v2 CommonCrawl quality signal metadata, does applying a language-adaptive perplexity threshold (τ_lang = k-th percentile of per-language perplexity distribution, for k ∈ {10, 20, 30, 40, 50}) produce a statistically significantly lower language-group retention disparity (Cramér's V) compared to the global perplexity threshold baseline — specifically, does ΔCramér's V ≥ 0.1 for at least 3 of 5 k values, with all group-level retention rates falling within [40%, 60%] of each other under the adaptive threshold?

### detailed_question
1. For each k ∈ {10, 20, 30, 40, 50}, does language-adaptive perplexity thresholding produce a Cramér's V ≤ 0.10 for the language-group × retained/removed contingency table — compared to the global threshold baseline of Cramér's V = 0.29–0.41 (h-m1 confirmed)?
2. Under the adaptive threshold (any k), does English retention rate rise from the baseline 3.7%–36.5% to ≥ 40% — correcting the disproportionate English exclusion identified in h-m1?
3. Does applying language-adaptive thresholds reduce retention rates for previously over-retained language groups (Italian: 18.2%–88.1% under global threshold) to within 20pp of English retention rates, and is this reduction statistically significant (chi-square p < 0.01)?
4. Is the disparity-reduction effect of adaptive thresholding robust across k values (consistent ΔCramér's V ≥ 0.1 for ≥ 3/5 k values), or does it only appear at specific threshold levels?
5. Do all language groups with n ≥ 1,000 in the RedPajama-v2 sample show convergence toward a common retention rate band under adaptive thresholds, or do some language groups remain outliers?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- The h-m1 result is not a failure to be discarded — it is a high-value empirical finding (Cramér's V = 0.29–0.41, p ≈ 0 for all thresholds) that establishes the existence and magnitude of global perplexity threshold bias in CommonCrawl-based corpora. Attempt 7 frames this as the motivating result and asks the next natural question: can a simple algorithmic fix (per-language calibration) correct it?
- The direction of the bias (English most excluded, not low-resource languages) is counterintuitive but explainable: English web text has higher perplexity variance (more diverse writing styles, slang, code-switching) than template-heavy or formal-register low-resource language content, causing more English documents to exceed global perplexity thresholds.
- Language-adaptive thresholding is a zero-cost simulation: no new data needed, no new model needed — just compute percentiles within each language group using the existing perplexity scores in the RedPajama-v2 quality signal files. The h-m1 pipeline already loads and groups by language; the modification is ~20 lines of code.
- The baseline Cramér's V values from h-m1 serve as the comparison point — no need to re-run the global threshold experiment from scratch, only the adaptive threshold experiment is new.
- If the adaptive threshold works (ΔCramér's V ≥ 0.1): concrete actionable recommendation for corpus curation pipelines — directly publishable at DATA-FM.
- If the adaptive threshold does NOT work: equally important negative result — implies that the perplexity language model itself (CCNet LM, trained primarily on Wikipedia) is the source of bias, not the threshold calibration method.

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (7th attempt) — failure context extraction from Serena Memory (7 records: failure_h-e1_run1, failure_h-m1_run1, limitation_h-c1_run1, limitation_h-e2-v3_run1, pivot_h-e2_h-e2-v2, snapshot_h-e1_2026-07-29, superseded_h-m1), hard infrastructure constraint filter (eliminate all HTTP API dependencies AND all model inference AND all large local index builds AND inverted-direction hypotheses), empirical finding preservation (h-m1 Cramér's V result used as baseline, not discarded), constructive follow-on design (test algorithmic solution to confirmed problem).

### Areas for Further Exploration

- **Perplexity model bias:** If adaptive thresholds don't reduce Cramér's V, investigate whether the KenLM or CCNet language model used for perplexity scoring is itself language-biased (trained on Wikipedia, which has English-heavy content) — a deeper source of bias than threshold design
- **Deduplication interaction:** Does minhash deduplication interact with language-adaptive perplexity thresholding (e.g., after adaptive threshold, are remaining non-English documents still deduplicated at higher rates)?
- **Domain within language:** Within each language group, do documents from different domain types (news vs. forum vs. government) show different retention rates under adaptive thresholds?
- **Threshold method comparison:** Beyond percentile-based adaptive thresholds, do z-score normalization (subtract per-language mean, divide by per-language std) or rank-based thresholds produce further bias reduction?
- **Downstream FM impact:** A natural Phase 2 follow-on — if adaptive threshold changes retention distribution, does training on the rebalanced corpus improve multilingual benchmark performance (XCOPA, XNLI)?

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

**Phase 1 Research Priorities (ROUTE_TO_0 Informed — 7th Attempt, Language-Adaptive Threshold Track):**
1. Confirm RedPajama-v2 quality signal Parquet field names for perplexity score and language ID — verify they match what h-m1 used (fields: `ccnet_perplexity`, `language` or equivalent)
2. Retrieve exact h-m1 baseline Cramér's V values per threshold k — confirm they are stable across the 208,263-row sample and usable as reference baseline without re-running
3. Survey CCNet / Wenzek et al. 2020 — identify which language model was used to compute perplexity scores in RedPajama-v2; confirm it is the same KenLM trained on Wikipedia paragraphs (critical for interpreting results)
4. Survey prior work on language-adaptive perplexity filtering — confirm no prior study has directly compared global vs. per-language percentile thresholds on Cramér's V metric for language-group retention equity in RedPajama-v2
5. Identify minimum viable sample size — confirm that the 208,263-row h-m1 dataset has sufficient per-language group counts (n ≥ 1,000) to produce stable Cramér's V estimates for 5 threshold levels
6. Confirm statistical test for comparing two Cramér's V values — identify appropriate test (bootstrap CI on ΔCramér's V, permutation test, or jackknife) since standard chi-square does not directly compare two Cramér's V values from the same dataset
7. Survey Dolma perplexity metadata availability — confirm whether Dolma v1.7 also provides raw perplexity scores (enabling cross-corpus replication) or only binary filter pass/fail flags

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
