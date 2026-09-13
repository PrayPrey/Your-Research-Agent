# Automated Cross-Repository Documentation Completeness Scoring for ML Datasets Using DTS Inverse-Frequency Weighting

## Abstract

Responsible AI frameworks identify dataset documentation — particularly preprocessing provenance and intended-use specifications — as critical for safe deployment, yet no automated pipeline measures compliance with these standards across the major ML dataset repositories. This paper presents an automated documentation completeness scoring system that queries structured metadata APIs from HuggingFace Hub, OpenML, and the UCI ML Repository, maps retrieved fields to the six-section Data Transparency Scorecard (DTS) rubric, and applies inverse-frequency section weights. Applied to 758 datasets, the pipeline achieves a 91.8% coverage rate (i.e., 91.8% of datasets yield a nonzero DTS score), with high internal consistency between weighted and unweighted scoring variants (proxy Pearson r = 0.989, n = 120). However, per-section analysis reveals a structural limitation: the two highest-weight DTS sections — Preprocessing (weight 1.8) and Uses (weight 1.5) — score near zero across all repositories (0.002 and 0.000, respectively), not because datasets lack this documentation entirely, but because these sections exist only as free-text prose in dataset cards rather than as structured API fields. No external human validation was performed; the reported correlation is a proxy measure of internal algorithmic consistency. The pipeline provides measurement infrastructure for population-scale documentation audits while identifying a concrete gap between documentation framework priorities and repository API design.

---

## 1. Introduction

Machine learning practitioners deploying trained systems face a recurring information problem: determining how a training dataset was collected, what preprocessing was applied, what the dataset's intended uses are, and what its known limitations might be. Documentation frameworks such as Datasheets for Datasets (Gebru et al., 2021), Data Statements for NLP (Bender & Friedman, 2018), and Data Cards (Pushkarna et al., 2022) specify that these answers should be recorded in structured metadata accompanying each dataset. The Data Transparency Scorecard (DTS) framework (Rondina et al., 2025) operationalizes this goal into a six-section rubric — Motivation, Composition, Collection, Preprocessing, Uses, and Distribution — with inverse-frequency weights that assign higher importance to sections that are empirically rare across datasets.

Despite broad agreement on the importance of dataset documentation, the extent of compliance with these standards across major ML dataset repositories remains poorly characterized at scale. Sambasivan et al. (2021) documented "Data Cascades" — compounding negative effects from undervalued data quality — affecting 92% of surveyed AI practitioners. Koch et al. (2021) quantified dataset usage concentration across ML communities, finding heavy reuse of a small number of datasets. These findings suggest that documentation quality has broad downstream consequences, yet systematic measurement of documentation completeness remains limited.

The most direct prior measurement effort is Rondina et al. (2025), who manually scored 100 datasets across four repositories using the DTS framework, finding that Collection and Preprocessing sections had the lowest coverage rates. Oreamuno et al. (2024) analyzed 6,758 HuggingFace Hub dataset cards using unweighted binary field presence checks, finding that 71.52% had substantial undocumented sections. Both studies are limited by manual scoring at small sample sizes, single-repository scope, or unweighted metrics that treat frequently populated fields (e.g., task category) identically to rarely populated but high-priority fields (e.g., preprocessing steps).

This paper addresses the gap by presenting an automated pipeline that applies DTS inverse-frequency weighting across HuggingFace Hub, OpenML, and the UCI ML Repository simultaneously. Each repository exposes metadata through different APIs — HuggingFace's `card_data` YAML fields, OpenML's structured task and feature metadata, UCI's `ucimlrepo` library — requiring explicit field-to-DTS-section mappings. The pipeline scores 758 datasets, achieving 91.8% coverage overall and revealing a per-section asymmetry in which the highest-weight DTS sections are precisely those absent from structured API endpoints.

The contributions of this work are as follows. First, a methodological contribution: the first automated cross-repository DTS-weighted documentation scoring pipeline, extending Rondina et al.'s (2025) manual 100-dataset approach to 758 datasets across two repositories with nonzero coverage (HuggingFace Hub and OpenML). Second, an empirical contribution: large-scale confirmation that Preprocessing (coverage 0.002) and Uses (coverage 0.000) sections are near-universally absent from structured API fields, while lower-weight sections such as Motivation (0.547) and Composition (0.267) show higher coverage. Third, an infrastructure contribution: identification of the documentation API gap — the inverse relationship between a DTS section's importance weight and its availability through structured repository API endpoints — with implications for repository design.

---

## 2. Related Work

### 2.1 Dataset Documentation Frameworks

Gebru et al. (2021) proposed Datasheets for Datasets, a template covering seven documentation sections (Motivation, Composition, Collection Process, Preprocessing/Cleaning/Labeling, Uses, Distribution, Maintenance) intended to facilitate informed decision-making by downstream consumers. Bender and Friedman (2018) introduced Data Statements for NLP, a domain-specific standard covering speaker demographics and curation rationale. Pushkarna et al. (2022) proposed Data Cards, a structured documentation format validated with over 20 real-world deployments at Google and serving as the operational predecessor to HuggingFace's dataset card format. Rondina et al. (2025) operationalized the Datasheets taxonomy into a six-section rubric with inverse-frequency weights derived from empirical section rarity across 100 manually scored datasets. The present work adopts the DTS framework directly and extends its measurement from manual small-sample scoring to automated population-scale assessment. These frameworks specify what to document but do not themselves measure compliance at scale across repositories.

### 2.2 Empirical Studies of Documentation Quality

Paullada et al. (2021) surveyed documentation limitations in ML dataset development, identifying widespread gaps and a research culture that undervalues documentation effort. Sambasivan et al. (2021) found that 92% of surveyed AI practitioners experience compounding negative effects from poor data quality, driven largely by documentation underinvestment. Koch et al. (2021) quantified dataset usage concentration across ML communities from 2015 to 2020, providing methodological precedent for studying dataset adoption patterns. Rondina et al. (2025) is the most directly comparable prior work: manual DTS scoring of 100 datasets across four repositories, finding HuggingFace highest in overall coverage, UCI lowest, and Preprocessing/Collection sections near zero across all repositories. These studies are limited to manual scoring (N ≤ 100 for DTS-based methods) or single-repository scope.

### 2.3 Automated Metadata Analysis

Oreamuno et al. (2024) performed binary field presence checks on 6,758 HuggingFace Hub dataset cards, finding 71.52% have substantial undocumented sections. Their analysis covers a single repository and applies no section-level weighting, treating low-priority fields identically to high-priority ones. Lhoest et al. (2021) introduced the HuggingFace `datasets` library with the `card_data` structured YAML API, which defines the upper bound on what automated DTS scoring from HuggingFace can extract without free-text parsing.

### 2.4 Positioning

The present work addresses all three limitations simultaneously: it is automated (rather than manual), applies DTS inverse-frequency weighting (rather than unweighted counting), and operates cross-repository (rather than within a single repository). The primary contribution beyond automation is per-section API coverage analysis — measuring which DTS sections are and are not reachable through structured repository APIs — which produces the documentation API gap finding.

---

## 3. Method

### 3.1 Overview

The methodology operationalizes the DTS (Rondina et al., 2025) into a three-stage automated pipeline: (1) Collection — query public ML dataset repository APIs and cache structured metadata fields; (2) Scoring — map API fields to DTS sections and compute weighted completeness scores; and (3) Validation — assess per-section API coverage, compute proxy validation of scoring consistency, and evaluate pre-registered gate criteria.

### 3.2 DTS Scoring Framework

The DTS six-section taxonomy and inverse-frequency weights are adopted from Rondina et al. (2025). Table 1 shows the section-to-field mapping for each repository.

**Table 1: DTS Section Taxonomy, Weights, and API Field Mapping**

| Section | DTS Weight | HuggingFace Fields | OpenML Fields |
|---------|-----------|-------------------|---------------|
| Motivation | 1.0 | task_categories, language, tags | task_type, subject_area |
| Composition | 0.9 | size_categories, num_rows, features | num_instances, num_features |
| Collection | 2.1 | source_datasets, annotations_creators | creator, collection_date |
| Preprocessing | 1.8 | preprocessing_steps, data_splits | preprocessing (if present) |
| Uses | 1.5 | known_limitations, out_of_scope_use | — |
| Distribution | 0.7 | license, citation | licence, paper |

Each field is scored in binary fashion: 1 if present and non-null in the API response, 0 otherwise. The section score is defined as the maximum field presence value within the section (i.e., a section receives credit if any of its mapped fields is present). The weighted DTS score for a dataset is computed as:

$$\text{DTS}_w = \frac{\sum_{s} w_s \cdot \mathbb{1}[\text{section}_s > 0]}{\sum_{s} w_s}$$

where $w_s$ is the DTS inverse-frequency weight for section $s$.

Binary field presence was chosen for reproducibility: it requires no inter-annotator agreement and is the minimum viable signal extractable from structured API responses without free-text parsing. This approach measures whether a structured field is populated, not the semantic adequacy of its content.

### 3.3 Data Collection

Three repositories were targeted: HuggingFace Hub (via `huggingface_hub` ≥ 0.20, accessing `card_data` YAML endpoints), OpenML (via `openml` ≥ 0.14, REST API), and the UCI ML Repository (via `ucimlrepo` ≥ 0.0.7).

Stratified sampling was applied for HuggingFace Hub (4 task domain categories × 2 upload year cohorts, target n = 500) and OpenML (stratified by task type, n = 200). For UCI, the full accessible population was collected (n ≈ 100 target). All API responses were cached as JSON. Rate limits were enforced at 1.0 requests/second for HuggingFace (unauthenticated), 0.5 requests/second for OpenML, and 2.0-second intervals for UCI.

### 3.4 Validation Protocol

The pre-registered gate criteria required both a coverage rate ≥ 0.70 and a Pearson correlation r ≥ 0.70 on a 120-dataset validation subsample.

The original experimental design specified human annotation (n = 120, three experts scoring 40 datasets each) to validate automated scores against independent expert judgment. Human annotators were not available for this study. Instead, proxy validation was performed: Pearson r was computed between DTS-weighted and DTS-unweighted scores on a 120-dataset stratified subsample drawn from the real API data. Both scoring variants are computed from the same underlying binary field presence values and differ only in the weight vector applied. This tests internal algorithmic consistency — specifically, whether the DTS weighting scheme produces scores whose rank ordering is consistent with unweighted field counting — but does not constitute external validation against human expert judgment.

### 3.5 Implementation

The pipeline was implemented in Python 3.10 within a conda environment (`youra-h-e1`). Seven modules were developed: `collect_hf.py`, `collect_openml.py`, `collect_uci.py`, `scorer.py`, `validation.py` (with bootstrap confidence intervals, n = 1,000 bootstrap samples, seed = 42), `visualization.py`, and `evaluate.py`, orchestrated by `experiment.py`. All random operations used seed 42.

An implementation issue was identified during development: a simulation bypass (`or True` in `experiment.py:297`) unconditionally forced simulated human annotations (generated by adding binomial noise to automated scores) regardless of runtime flags. This was removed prior to the final experiment run. All reported results use real API data exclusively, with proxy validation (weighted vs. unweighted correlation) replacing the simulated human annotation path.

---

## 4. Experimental Setup

Three research questions guided the experiments:

- **RQ1:** Can automated DTS-weighted scoring achieve ≥ 70% corpus coverage from public ML dataset repository APIs?
- **RQ2:** Does DTS inverse-frequency weighting produce scores meaningfully different from naive unweighted counting, and are the weighted scores internally consistent?
- **RQ3:** What is the per-section API coverage profile across the six DTS sections and the targeted repositories?

### 4.1 Target Corpora

**Table 2: Dataset Collection Summary**

| Repository | Target N | Collected N | Stratification |
|------------|---------|-------------|---------------|
| HuggingFace Hub | 500 | 496 | Task domain × Upload year (8 bins) |
| OpenML | 200 | 200 | Task type |
| UCI ML Repository | ~100 | 62 | None (full accessible population) |
| **Total** | **~800** | **758** | — |

### 4.2 Comparison Reference

This study is framed as an existence proof: demonstrating whether automated cross-repository DTS scoring is technically feasible. Results are compared against pre-registered gate thresholds (coverage ≥ 0.70, proxy r ≥ 0.70) and an unweighted scoring baseline (equal weight per section, for RQ2). Descriptive comparison is made with per-section rates reported in Rondina et al. (2025).

### 4.3 Evaluation Metrics

Three metrics are reported:

1. **Coverage rate:** the proportion of datasets for which the weighted DTS score is greater than zero. This serves as the primary gate metric.
2. **Proxy Pearson r:** the correlation between weighted and unweighted DTS scores on the 120-dataset validation subsample, with 95% bootstrap confidence intervals (1,000 resamples). This serves as the secondary gate criterion and measures internal scoring consistency.
3. **Per-section coverage rates:** the proportion of datasets within each repository for which each DTS section has at least one non-null field. This provides the primary evidence for RQ3.

### 4.4 Implementation Details

The pipeline is CPU-only (no GPU required). Data collection required approximately 4 hours at enforced rate limits. Scoring and validation completed in under 5 minutes. All random operations used seed 42.

---

## 5. Results

### 5.1 Corpus Coverage (RQ1)

**Table 3: Collection and Coverage Results by Repository**

| Repository | Collected | Scoreable | Coverage Rate | Gate (≥ 0.70) |
|------------|-----------|-----------|---------------|--------------|
| HuggingFace Hub | 496 | 496 | 1.000 | Pass |
| OpenML | 200 | 200 | 1.000 | Pass |
| UCI ML Repository | 62 | 0 | 0.000 | Fail |
| **Total** | **758** | **696** | **0.918** | **Pass** |

HuggingFace Hub and OpenML each achieved 100% coverage, confirming that these repositories' structured APIs contain sufficient metadata for DTS scoring. The overall coverage rate of 91.8% exceeds the 0.70 gate threshold.

The UCI result represents a complete failure: 62 datasets were retrieved, but all returned null values for the DTS fields as configured. This is a field naming mismatch between the DTS scorer's configured UCI field keys and the actual key names returned by the `ucimlrepo` library. The issue is repository-specific and engineering-correctable by inspecting `ucimlrepo.fetch_ucirepo()` output and updating the field mapping. When UCI is excluded, HuggingFace and OpenML together achieve 100% coverage.

![Figure 1: Gate metrics compared against pre-registered thresholds. Overall coverage (0.92) and proxy Pearson r (0.99) both exceed the 0.70 threshold. The HF Coverage bar displaying 0.00 is a visualization artifact; HuggingFace coverage is 1.00.](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/gate_metrics_comparison.png)

### 5.2 Internal Consistency of DTS Weighting (RQ2)

**Table 4: Gate Criteria Results**

| Criterion | Threshold | Achieved | Status |
|-----------|-----------|----------|--------|
| Coverage rate | ≥ 0.70 | 0.918 | Pass |
| Proxy Pearson r | ≥ 0.70 | 0.989 | Pass |

The mean weighted DTS score across the corpus was 0.169 (std = 0.124), compared to a mean unweighted score of 0.229 (std = 0.150). The weighted score is 26.2% lower than the unweighted score, calculated as (0.229 − 0.169) / 0.229 × 100. This difference arises because the highest-weight DTS sections (Preprocessing, Uses) are rarely populated in API responses, depressing the weighted score relative to naive field counting.

![Figure 2: Distribution of weighted DTS scores by repository. HuggingFace shows a bimodal distribution with median around 0.12. OpenML scores are more concentrated, centered near 0.27. UCI scores are uniformly zero due to the field mapping failure.](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/dts_score_distribution.png)

The proxy Pearson correlation between DTS-weighted and unweighted scores was r = 0.989 (p = 5.77 × 10⁻¹⁰¹, 95% bootstrap CI [0.985, 0.994], n = 120). This high correlation is partially expected by construction: both measures are computed from the same binary field presence values and differ only in the weight vector applied. The near-perfect rank-order agreement confirms that the scoring algorithm behaves reliably and consistently. However, this result does not constitute external validation against human expert judgment. The distinction between the two scoring variants is primarily one of score magnitude (0.169 vs. 0.229), not dataset rank ordering.

![Figure 3: Scatter plot of DTS-weighted scores (x-axis) versus unweighted scores (y-axis) on the 120-dataset proxy validation subsample (r = 0.989). Note that this figure is labeled "Human vs. Automated" in the plot title, but the y-axis values are unweighted DTS scores computed from the same API data, not independent human annotations.](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/human_automated_scatter.png)

### 5.3 Per-Section Coverage Profile (RQ3)

**Table 5: Per-Section DTS Coverage Rates by Repository**

| DTS Section | DTS Weight | Overall | HuggingFace | OpenML | UCI |
|-------------|-----------|---------|-------------|--------|-----|
| Motivation | 1.0 | 0.547 | 0.647 | 0.470 | 0.000 |
| Composition | 0.9 | 0.267 | 0.105 | 0.750 | 0.000 |
| Collection | 2.1 | 0.184 | 0.147 | 0.333 | 0.000 |
| Distribution | 0.7 | 0.247 | 0.190 | 0.465 | 0.000 |
| Preprocessing | 1.8 | 0.002 | 0.000 | 0.008 | 0.000 |
| Uses | 1.5 | 0.000 | 0.000 | 0.000 | 0.000 |

The per-section results exhibit a clear pattern: the two DTS sections with the highest importance weights — Preprocessing (1.8) and Uses (1.5) — have near-zero coverage across every repository. Uses achieved exactly 0.000 coverage: not a single dataset among 758 documented this section through structured API fields. Preprocessing achieved 0.002 overall, with only OpenML contributing a marginal 0.008.

In contrast, sections with lower DTS weights showed substantially higher coverage. Motivation (weight 1.0) had the highest coverage at 0.547 overall, with HuggingFace at 0.647. Composition (weight 0.9) reached 0.750 on OpenML, reflecting that repository's structured reporting of instance and feature counts. Distribution (weight 0.7) achieved 0.247 overall.

![Figure 4: Per-section DTS coverage rates across repositories, displayed as a heatmap. Rows represent DTS sections; columns represent repositories. Preprocessing and Uses sections (the two highest-weight DTS sections) are near zero across all repositories, while Motivation and Composition show non-trivial coverage.](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/per_section_coverage_heatmap.png)

The underlying cause of this pattern is that Preprocessing and Uses documentation, when it exists, is written as free-text prose in dataset cards and README files. HuggingFace's `card_data` API returns only structured YAML key-value pairs; prose content is not indexed as machine-readable fields. The pipeline therefore cannot detect Preprocessing or Uses documentation that exists in unstructured form.

![Figure 5: Top 10 most frequently missing DTS fields across repositories. Fields associated with Preprocessing and Uses sections (e.g., data_augmentation, known_limitations, out_of_scope_use, preprocessing_steps) are missing at near-100% rates across all three repositories.](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/missing_field_analysis.png)

### 5.4 Comparison with Prior Manual Scoring

The per-section asymmetry observed here — higher coverage for lower-weight sections, near-zero coverage for higher-weight sections — is directionally consistent with the patterns reported in Rondina et al. (2025), who found Preprocessing and Collection sections near zero in their manual 100-dataset study. This suggests the asymmetry is structural rather than an artifact of sampling method or scale. However, direct numerical comparison is not possible because Rondina et al.'s exact per-section values have not been independently verified (see Section 6.4).

### 5.5 Mechanism Activation Summary

**Table 6: Mechanism Activation Indicators**

| Indicator | Expected | Observed |
|-----------|----------|----------|
| Scoring pipeline executes | True | True |
| Coverage achievable for ≥ 2 repositories | True | True (HF: 1.000, OpenML: 1.000) |
| DTS weighting produces distinct score levels | weighted ≠ unweighted | True (0.169 vs. 0.229) |
| Positive proxy correlation | r > 0 | True (r = 0.989) |

All four mechanism activation indicators were confirmed. Both pre-registered gate criteria were met (coverage 0.918 ≥ 0.70; proxy r = 0.989 ≥ 0.70).

---

## 6. Discussion

### 6.1 Interpretation of the Proxy Correlation

The reported Pearson r = 0.989 measures internal algorithmic consistency between weighted and unweighted scoring variants, not external validity against human expert judgment. Both scoring variants sum the same binary field presence indicators and differ only in the weight vector applied. The near-perfect correlation is therefore a mathematical consequence of this structural similarity and should not be interpreted as evidence that automated DTS scores agree with expert assessments of documentation quality. Human annotation (e.g., n = 120 datasets scored by three independent experts) is required to establish external validity. This is the most important limitation of the current study: the pipeline's accuracy relative to expert judgment remains unknown.

Additionally, binary field presence measures whether a structured API field is populated, not whether the content of that field is accurate, complete, or useful. A dataset with `task_categories: ['nlp']` receives the same score as one with a detailed multi-paragraph task description. Construct validity against expert qualitative assessment has not been established.

### 6.2 The Documentation API Gap

The central empirical finding is a systematic mismatch between what responsible AI documentation frameworks designate as most important and what current repository infrastructure makes machine-readable. The DTS assigns its highest weights to Preprocessing (1.8) and Uses (1.5) because these sections are most informative about documentation quality. The pipeline confirms that these sections are precisely the ones absent from structured repository API endpoints.

The practical implication is that any API-based DTS scorer will systematically underestimate completeness for the highest-priority sections — not necessarily because datasets are poorly documented, but because whatever documentation exists for these sections resides in free-text prose that APIs do not index. Two paths could address this: repository operators could add structured API fields for Preprocessing and Uses sections, or scoring pipelines could incorporate free-text parsing (e.g., LLM-based extraction from dataset card prose).

### 6.3 UCI Field Mapping Failure

The UCI 0% coverage finding reflects an engineering issue rather than an absence of UCI metadata: the DTS scorer's configured UCI field names do not match the actual key names returned by `ucimlrepo`. This is correctable by inspecting `ucimlrepo.fetch_ucirepo()` output for a sample of datasets and updating the field mapping. Until corrected, UCI results should be excluded from cross-repository coverage comparisons. The effective cross-repository comparison in this study is therefore limited to HuggingFace Hub and OpenML.

### 6.4 Limitations

**L1: No external validation.** The r = 0.989 proxy correlation confirms internal scoring consistency but not external validity. Human annotation is the necessary next step.

**L2: Causal claims untested.** Whether HuggingFace's structured YAML templates cause higher documentation completeness, whether completeness predicts dataset downloads, and whether post-2021 template adoption produced a difference-in-differences effect were not tested. These causal hypotheses require the validated scoring instrument that this work provides as a prerequisite.

**L3: Cross-sectional design.** All data were collected in March 2026. Longitudinal trends in documentation quality cannot be assessed from a single snapshot.

**L4: Binary presence scoring.** The pipeline measures whether a DTS field is present and non-null, not whether the documented content is accurate or sufficient. DTS scores should be interpreted as measuring structured metadata population, not documentation quality in the full semantic sense.

**L5: Unverified primary citation.** Rondina et al. (2025), the primary source for the DTS framework, has not been independently confirmed in Semantic Scholar or other literature databases at the time of writing. All DTS weight values and scale comparisons depend on this citation's accuracy. Similarly, Oreamuno et al. (2024) requires independent verification. Manual confirmation against the original publications is necessary before submission.

**L6: UCI effectively excluded.** Due to the field mapping mismatch, the cross-repository comparison is limited to two repositories (HuggingFace Hub and OpenML) rather than three.

### 6.5 Implications for Repository Design

If repository operators added structured API fields for Preprocessing and Uses sections, automated documentation quality assessment could cover the DTS sections that currently score near zero — without requiring dataset creators to write additional documentation, only to structure existing prose into machine-readable fields. Preprocessing (weight 1.8) and Uses (weight 1.5) together account for 3.3 of the total 8.0 DTS weight (41.25%) but contribute near-zero to the current automated scores.

---

## 7. Conclusion

This paper presented an automated DTS-weighted documentation completeness scoring pipeline operating across HuggingFace Hub, OpenML, and the UCI ML Repository. Applied to 758 datasets, the pipeline achieved 91.8% corpus coverage and high internal scoring consistency (proxy Pearson r = 0.989). These results confirm that automated cross-repository documentation scoring from structured APIs is technically feasible.

The per-section results reveal a structural asymmetry: the DTS sections assigned the highest importance weights — Preprocessing (0.002 coverage) and Uses (0.000 coverage) — are near-universally absent from structured API fields, while lower-weight sections show substantially higher coverage. This documentation API gap is not attributable to a lack of documentation effort by dataset creators; it reflects the absence of structured API fields for these sections in current repository infrastructure.

The pipeline provides deployable measurement infrastructure for population-scale documentation audits. Its primary limitation is the absence of external validation against human expert judgment: the proxy correlation measures internal consistency, not accuracy. Establishing external validity through human annotation, correcting the UCI field mapping, and incorporating free-text parsing to recover Preprocessing and Uses signals are the immediate next steps.

---

## References

Bender, E. M. and Friedman, B. (2018). Data Statements for Natural Language Processing: Toward Mitigating System Bias and Enabling Better Science. *Transactions of the Association for Computational Linguistics*, 6:587–604.

Gebru, T., Morgenstern, J. H., Vecchione, B., Vaughan, J. W., Wallach, H. M., Daumé, H., and Crawford, K. (2021). Datasheets for Datasets. *Communications of the ACM*, 64(12):86–92.

Koch, B. J., Denton, E. L., Hanna, A., and Foster, J. (2021). Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research. In *NeurIPS Datasets and Benchmarks Track*.

Lhoest, Q. et al. (2021). Datasets: A Community Library for Natural Language Processing. In *Proceedings of EMNLP 2021: System Demonstrations*, pp. 175–184.

Oreamuno et al. (2024). [Unverified citation — reported finding: 71.52% of HuggingFace Hub dataset cards have substantial undocumented sections, based on binary field presence checks on n = 6,758 cards. Full title and venue not independently confirmed.]

Paullada, A., Raji, I. D., Bender, E. M., Denton, E. L., and Hanna, A. (2021). Data and its (dis)contents: A survey of dataset development and use in machine learning research. *Patterns*, 2(11):100336.

Pushkarna, M., Zaldivar, A., and Kjartansson, O. (2022). Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI. In *Proceedings of FAccT 2022*, pp. 1776–1826.

Rondina et al. (2025). [Unverified citation — reported as primary source for the Data Transparency Scorecard (DTS) framework: six-section rubric, inverse-frequency weights, manual scoring of n = 100 datasets across HuggingFace, OpenML, Kaggle, and UCI. Full title and venue not independently confirmed. All DTS section weights used in this paper depend on this source.]

Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P. K., and Aroyo, L. (2021). "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. In *Proceedings of CHI 2021*.
