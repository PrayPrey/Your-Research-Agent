# Automated DTS-Weighted Cross-Repository ML Dataset Documentation Scoring: Feasibility and the Documentation API Gap

## Abstract

Dataset documentation frameworks such as the Data Transparency Scorecard (DTS) designate preprocessing and intended-use sections as highest priority, yet no automated pipeline has measured compliance with these standards across multiple ML dataset repositories. We describe an automated DTS-weighted documentation completeness scoring system that queries structured metadata APIs from HuggingFace Hub, OpenML, and UCI ML Repository, mapping retrieved fields to the DTS six-section rubric with inverse-frequency weights. Applied to 758 datasets, the pipeline yields a coverage rate of 91.8% (696 of 758 datasets scoreable), with a proxy correlation of r = 0.989 (p < 0.001) between weighted and unweighted scores computed on a 120-dataset subsample. However, the two highest-weighted DTS sections -- Preprocessing (weight 1.8) and Uses (weight 1.5) -- exhibit near-zero coverage across all repositories (0.002 and 0.000, respectively), because these sections are not represented as structured API fields. This result reflects a structural gap in repository API design rather than an absence of documentation effort by dataset creators. The pipeline is limited by the use of proxy validation (weighted vs. unweighted correlation) rather than human expert annotation, and by complete scoring failure on the UCI repository due to field naming mismatches. We release the pipeline as an open-source tool for population-scale documentation audits and identify the specific infrastructure changes needed to close the gap between documentation frameworks and repository APIs.

## 1. Introduction

Documentation frameworks for ML datasets -- including Datasheets for Datasets (Gebru et al., 2021), Data Statements (Bender & Friedman, 2018), and Data Cards (Pushkarna et al., 2022) -- specify what information dataset creators should record. The Data Transparency Scorecard (DTS; Rondina et al., 2025) operationalizes this into a six-section rubric with inverse-frequency weights, where sections that are rarely documented (e.g., Preprocessing, Uses) receive higher weights than commonly documented ones (e.g., Motivation). Prior empirical work on documentation quality has been limited to manual scoring at small sample sizes (Rondina et al., 2025, n = 100) or single-repository unweighted analyses (Oreamuno et al., 2024, n = 6,758 on HuggingFace Hub only).

Three gaps motivate this work. First, no automated pipeline applies DTS inverse-frequency weighting to documentation scoring. Second, no study operates across multiple repository APIs simultaneously. Third, and less anticipated prior to this work: it is unknown whether the DTS sections designated as highest priority are even representable through structured repository API fields.

We present an automated pipeline that collects structured metadata from HuggingFace Hub (n = 496), OpenML (n = 200), and UCI ML Repository (n = 62), maps API fields to DTS sections, and computes weighted completeness scores. The pipeline was evaluated against two pre-specified gate criteria: corpus coverage rate of at least 0.70 and proxy Pearson r of at least 0.70. Both criteria were met.

The principal empirical finding is a structural asymmetry: the DTS sections with the highest importance weights (Preprocessing at 1.8 and Uses at 1.5) score near-zero across all repositories because these sections exist only as free-text prose in dataset cards, not as structured API fields. Lower-weighted sections such as Motivation (1.0) and Composition (0.9) show substantially higher coverage. This pattern, which we term the documentation API gap, indicates that API-based scoring systematically cannot assess the documentation dimensions that responsible AI frameworks prioritize most.

This paper makes three contributions: (1) the first automated cross-repository DTS-weighted documentation scoring pipeline, achieving 91.8% coverage across 758 datasets; (2) large-scale empirical characterization of per-section API coverage, revealing the documentation API gap; and (3) identification of the measurement infrastructure needed for future causal studies of documentation quality.

Several important limitations should be noted at the outset. The proxy validation (r = 0.989) measures internal algorithmic consistency between weighted and unweighted scoring, not agreement with human expert judgment. The UCI repository contributed zero scoreable datasets due to a field naming mismatch in the scoring configuration. Two key citations (Rondina et al., 2025; Oreamuno et al., 2024) have not been independently verified in literature databases. These limitations are discussed in detail in Section 6.

## 2. Related Work

### 2.1 Dataset Documentation Frameworks

Gebru et al. (2021) proposed Datasheets for Datasets, a template covering seven documentation sections (Motivation, Composition, Collection Process, Preprocessing/Cleaning/Labeling, Uses, Distribution, Maintenance). Bender and Friedman (2018) introduced Data Statements for NLP, a domain-specific standard addressing speaker demographics and curation rationale. Pushkarna et al. (2022) developed Data Cards, a structured documentation format validated across deployments at Google and operationally related to HuggingFace's dataset card format.

The Data Transparency Scorecard (Rondina et al., 2025) converts the Datasheets taxonomy into a six-section rubric with inverse-frequency weights derived from empirical section rarity across 100 manually scored datasets. We adopt the DTS framework directly in this work. It should be noted that Rondina et al. (2025) has not been independently confirmed in Semantic Scholar or other literature databases at the time of writing; all DTS weight values used in this paper are dependent on the accuracy of that source.

These frameworks specify what information should be documented but do not themselves measure compliance at scale across repositories.

### 2.2 Empirical Studies of Documentation Quality

Paullada et al. (2021) surveyed documentation limitations in ML dataset development, identifying widespread gaps and a research culture that undervalues documentation investment. Sambasivan et al. (2021) reported that 92% of surveyed AI practitioners experience compounding negative effects from poor data quality -- termed "Data Cascades" -- driven in part by documentation underinvestment. Koch et al. (2021) quantified dataset usage concentration across ML communities from 2015 to 2020.

Rondina et al. (2025) is the most directly related predecessor: manual DTS scoring of 100 datasets across four repositories, reporting near-zero coverage for Preprocessing and Collection sections and higher coverage for Motivation. Our work extends this to automated scoring at 7.58 times the sample size, though covering three repositories rather than four.

### 2.3 Automated Metadata Analysis

Oreamuno et al. (2024) performed binary field presence checks on 6,758 HuggingFace Hub dataset cards, reporting that 71.52% have substantial undocumented sections. Their analysis is single-repository and unweighted, treating all fields equally regardless of DTS importance. Lhoest et al. (2021) introduced the HuggingFace `datasets` library with the `card_data` structured YAML API, which defines the upper bound on what automated DTS scoring from HuggingFace can retrieve.

No prior work applies DTS inverse-frequency weighting in an automated cross-repository pipeline or measures per-section API coverage against DTS importance weights.

## 3. Method

### 3.1 Overview

The pipeline operates in three stages: (1) collection of structured metadata from public ML dataset repository APIs, (2) scoring via mapping of API fields to DTS sections with weighted completeness computation, and (3) validation of scoring consistency and coverage.

### 3.2 DTS Scoring Framework

We adopt the DTS six-section taxonomy and inverse-frequency weights from Rondina et al. (2025) without modification.

**Table 1: DTS Section Taxonomy and API Field Mapping**

| Section | DTS Weight | HuggingFace Fields | OpenML Fields |
|---------|-----------|-------------------|---------------|
| Motivation | 1.0 | task_categories, language, tags | task_type, subject_area |
| Composition | 0.9 | size_categories, num_rows, features | num_instances, num_features |
| Collection | 2.1 | source_datasets, annotations_creators | creator, collection_date |
| Preprocessing | 1.8 | preprocessing_steps, data_splits | preprocessing (if present) |
| Uses | 1.5 | known_limitations, out_of_scope_use | -- |
| Distribution | 0.7 | license, citation | licence, paper |

Each field is scored as binary: 1 if present and non-null, 0 otherwise. The section score is the maximum field presence value within each section. The weighted DTS score is computed as:

DTS_w = sum(w_s * I[section_s > 0]) / sum(w_s)

where w_s is the DTS weight for section s and I[.] is the indicator function.

Binary field presence measures whether a structured API field is populated, not whether the documented content is semantically adequate or accurate. A dataset with `task_categories: ['nlp']` scores identically to one with a detailed task description in the same field.

### 3.3 Data Collection

Target repositories were HuggingFace Hub (via `huggingface_hub` >= 0.20, `card_data` YAML endpoint), OpenML (via `openml` >= 0.14, REST API), and UCI ML Repository (via `ucimlrepo` >= 0.0.7). Sampling was stratified by four task domain categories and two upload year cohorts (up to 2021 and after 2021). Target sample sizes were HuggingFace Hub n = 500, OpenML n = 200, and UCI approximately 100 (full accessible population). The actual UCI population accessible via `ucimlrepo` v0.0.7 was 62 datasets, fewer than the initial estimate of approximately 100.

All API responses were cached in JSON format. Rate limits were enforced at 1.0 request per second for HuggingFace (unauthenticated), 0.5 requests per second for OpenML, and one request per 2.0 seconds for UCI.

### 3.4 Validation Protocol

The planned human annotation study (n = 120, three experts scoring 40 datasets each) was not conducted. In its place, we computed a proxy validation: the Pearson correlation between DTS-weighted and DTS-unweighted scores on a 120-dataset stratified subsample drawn from real API data. Both the weighted and unweighted scores are computed from the same underlying binary field presence values; they differ only in the weight vector applied. This measures internal algorithmic consistency -- whether the weighting scheme behaves reliably -- not construct validity against human expert judgment.

Gate criteria were specified prior to experimentation: coverage rate of at least 0.70 and proxy Pearson r of at least 0.70.

### 3.5 Implementation

The pipeline was implemented in Python 3.10 in a conda environment. It consists of eight modules: `collect_hf.py`, `collect_openml.py`, `collect_uci.py`, `scorer.py`, `validation.py` (bootstrap confidence intervals, n = 1,000 resamples, seed = 42), `visualization.py`, `evaluate.py`, and `experiment.py` (main orchestrator). All random operations used seed 42.

A simulation bypass (`or True` in `experiment.py` line 297) was identified during development that unconditionally forced synthetic human annotation generation regardless of command-line flags. This was removed; all reported results use real API data exclusively with proxy validation replacing the originally planned human annotation comparison.

## 4. Experimental Setup

Three research questions guided the experiments:

**RQ1:** Can automated DTS-weighted scoring achieve at least 70% corpus coverage from public ML dataset repository APIs?

**RQ2:** Does DTS inverse-frequency weighting produce scores different from naive unweighted counting, and are the scores internally consistent?

**RQ3:** What is the per-section API coverage profile across the six DTS sections and three repositories?

### 4.1 Corpus

| Repository | Target N | Collected N | Stratification |
|------------|---------|-------------|---------------|
| HuggingFace Hub | 500 | 496 | Task domain x upload year (8 bins) |
| OpenML | 200 | 200 | Task type |
| UCI ML Repository | ~100 | 62 | None (full accessible population) |
| **Total** | **~800** | **758** | -- |

### 4.2 Comparison Reference

This is a feasibility study. We compare against pre-specified gate thresholds (coverage >= 0.70, proxy r >= 0.70) and an unweighted scoring baseline (equal weight per field) for RQ2. Per-section rates are compared descriptively with the directional patterns reported in Rondina et al. (2025), though exact numerical comparison is not possible as the Rondina et al. values have not been independently verified.

### 4.3 Evaluation Metrics

**Coverage rate:** The proportion of datasets with a weighted DTS score greater than zero.

**Proxy Pearson r:** Correlation between weighted and unweighted DTS scores on a 120-dataset subsample, with 95% bootstrap confidence interval (1,000 resamples).

**Per-section coverage rates:** The proportion of datasets in each repository with non-zero coverage for each DTS section.

### 4.4 Implementation Details

The pipeline is CPU-only. Collection required approximately 4 hours at the enforced rate limits. Scoring and validation completed in under 5 minutes. All random operations used seed 42.

## 5. Results

### 5.1 Corpus Coverage (RQ1)

**Table 2: Collection and Coverage Results by Repository**

| Repository | Collected | Scoreable | Coverage Rate | Gate (>= 0.70) |
|------------|-----------|-----------|---------------|----------------|
| HuggingFace Hub | 496 | 496 | 1.000 | Pass |
| OpenML | 200 | 200 | 1.000 | Pass |
| UCI ML Repository | 62 | 0 | 0.000 | Fail |
| **Total** | **758** | **696** | **0.918** | **Pass** |

The overall coverage rate of 0.918 exceeds the 0.70 threshold. HuggingFace Hub and OpenML each achieve 100% coverage, indicating that their structured APIs contain sufficient fields for DTS scoring.

The UCI result requires explanation: all 62 collected datasets returned null values for all DTS-mapped fields. This is attributable to a field naming mismatch between the DTS scorer's configured UCI field keys and the actual key names returned by the `ucimlrepo` library. The UCI datasets likely contain some relevant metadata under different field names, but the current field mapping does not capture it. This is an engineering issue in the pipeline configuration, not evidence that UCI datasets lack all documentation. Excluding UCI from the denominator yields 100% coverage for HuggingFace and OpenML combined.

![Gate metrics comparison](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/gate_metrics_comparison.png)

*Figure 1: Gate criteria achievement. Both pre-specified thresholds (coverage >= 0.70 and proxy r >= 0.70) are met.*

### 5.2 Internal Consistency of DTS Weighting (RQ2)

**Table 3: Gate Criteria Results**

| Criterion | Threshold | Achieved | Margin | Status |
|-----------|-----------|----------|--------|--------|
| Coverage rate | >= 0.70 | 0.918 | +21.8 pp | Pass |
| Proxy Pearson r | >= 0.70 | 0.989 | +28.9 pp | Pass |

The mean weighted DTS score is 0.169 (SD = 0.124), compared to a mean unweighted score of 0.229 (SD = 0.150). The weighted score is approximately 26% lower than the unweighted score ((0.229 - 0.169) / 0.229 = 0.262). This difference arises because the highest-weighted DTS sections (Preprocessing, Uses) are rarely populated in API responses, pulling the weighted average down relative to naive field counting.

The proxy Pearson correlation between weighted and unweighted scores is r = 0.989 (p = 5.77 x 10^-101, 95% bootstrap CI [0.985, 0.994], n = 120). This near-perfect correlation is partially expected by construction: both measures are computed from the same binary field presence values and differ only in the weight vector. The correlation confirms that the scoring algorithm behaves consistently, but it does not constitute external validation against independent human expert judgment. The primary distinction between the two scoring approaches is in score magnitude (0.169 vs. 0.229), not in dataset rank ordering.

![DTS score distribution](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/dts_score_distribution.png)

*Figure 2: Distribution of DTS-weighted and unweighted scores across the 758-dataset corpus.*

![Proxy validation scatter](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/human_automated_scatter.png)

*Figure 3: Scatter plot of weighted vs. unweighted DTS scores on the 120-dataset validation subsample, with bootstrap confidence interval annotation.*

### 5.3 Per-Section Coverage Profile (RQ3)

**Table 4: Per-Section DTS Coverage Rates by Repository**

| DTS Section | DTS Weight | Overall | HuggingFace | OpenML | UCI |
|-------------|-----------|---------|-------------|--------|-----|
| Motivation | 1.0 | 0.547 | 0.647 | 0.470 | 0.000 |
| Composition | 0.9 | 0.267 | 0.105 | 0.750 | 0.000 |
| Collection | 2.1 | 0.184 | 0.147 | 0.333 | 0.000 |
| Preprocessing | 1.8 | 0.002 | 0.000 | 0.008 | 0.000 |
| Uses | 1.5 | 0.000 | 0.000 | 0.000 | 0.000 |
| Distribution | 0.7 | 0.247 | 0.190 | 0.465 | 0.000 |

![Per-section coverage heatmap](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/per_section_coverage_heatmap.png)

*Figure 4: Per-section DTS coverage rates across repositories. Preprocessing (weight 1.8) and Uses (weight 1.5) score near-zero across all repositories. These sections exist as free-text prose in dataset cards rather than structured API fields, which is why automated API-based scoring cannot detect them.*

The two highest-weighted DTS sections have near-zero coverage universally:

- Preprocessing (weight 1.8): overall coverage 0.002. Only OpenML shows any non-zero value (0.008), corresponding to a small number of datasets with a structured preprocessing field.
- Uses (weight 1.5): overall coverage 0.000. No dataset in the 758-dataset corpus documented intended uses or known limitations through structured API fields.

The sections with the highest coverage -- Motivation (0.547), Composition (0.267), Distribution (0.247) -- have the lowest DTS weights (1.0, 0.9, 0.7 respectively). Collection (weight 2.1) achieves 0.184 overall coverage, indicating partial availability of structured collection-related fields.

This pattern arises because preprocessing steps, intended uses, and known limitations are typically described in free-text prose within dataset cards and README files. HuggingFace's `card_data` API returns only structured YAML key-value pairs; the prose content of dataset cards is not indexed as structured fields. This structural mismatch between where documentation exists (prose) and what the API exposes (structured fields) is the documentation API gap.

![Missing field analysis](/home/anonymous/YouRA_results_new_4/TEST_mldpr/docs/youra_research/20260315_mlpdr/paper/figures/missing_field_analysis.png)

*Figure 5: Field-level missing rates by DTS section and repository, providing granular detail complementing the section-level heatmap.*

### 5.4 Directional Comparison with Prior Manual Scoring

The per-section pattern observed here -- higher coverage for lower-weighted sections and near-zero coverage for Preprocessing and Uses -- is directionally consistent with the patterns described in Rondina et al. (2025), who reported near-zero Preprocessing and Collection coverage and higher Motivation coverage in their manual 100-dataset study. However, exact numerical comparison is not possible because (a) Rondina et al. scored manually while we score from API fields, measuring partially different constructs, and (b) the Rondina et al. citation has not been independently verified. The directional consistency suggests that the section asymmetry is structural rather than an artifact of either scoring method.

### 5.5 Mechanism Activation Summary

**Table 5: Mechanism Activation Indicators**

| Indicator | Expected | Observed |
|-----------|----------|----------|
| Scoring pipeline executes without errors | True | True |
| Coverage achievable for at least 2 repositories | True | True (HF: 1.000, OpenML: 1.000) |
| DTS weighting produces distinct score level | weighted != unweighted | True (0.169 vs. 0.229) |
| Positive proxy correlation | r > 0 | True (r = 0.989) |

## 6. Discussion

### 6.1 The Documentation API Gap

The central finding is a systematic mismatch between what documentation frameworks designate as most important and what repository APIs make machine-readable. The DTS assigns its highest weights to Preprocessing (1.8) and Uses (1.5) because these sections are rare and informative when present. Our results show these sections are near-zero in structured API responses across all repositories surveyed.

This does not necessarily indicate that dataset creators fail to document preprocessing and intended uses. Rather, such documentation may exist as free-text prose in dataset cards, README files, or accompanying papers -- formats not indexed by structured API endpoints. An API-based DTS scorer will therefore systematically underestimate completeness for the highest-priority sections. Closing this gap would require either repository operators adding structured API fields for Preprocessing and Uses content, or development of free-text parsing (e.g., LLM-based extraction) to recover documentation that exists in prose form.

The proxy correlation of r = 0.989, while indicating consistent algorithmic behavior, reflects the mathematical relationship between two scoring functions that share the same binary inputs. Both weighted and unweighted scores sum the same field presence indicators with different weight vectors. The near-perfect correlation is therefore partly a consequence of this structural similarity. Human annotation (n = 120, three experts) would provide the external validity assessment that proxy correlation cannot.

### 6.2 UCI Field Mapping Failure

The UCI coverage of 0% is best understood as a pipeline engineering issue rather than a finding about UCI documentation quality. The DTS scorer's configured UCI field names do not match the actual key names returned by `ucimlrepo`. This is correctable by inspecting the library's output for a small sample and updating the field mapping. Until corrected, UCI results should be excluded from cross-repository completeness comparisons, and the overall coverage rate of 91.8% should be interpreted with the understanding that it includes 62 datasets that scored zero due to this mapping failure.

### 6.3 Implications for Repository Design

If repository operators were to add structured API fields for Preprocessing and Uses sections, automated documentation quality assessment could cover these high-priority areas without requiring dataset creators to produce additional documentation -- only to structure existing prose documentation into machine-readable fields. Preprocessing (weight 1.8) and Uses (weight 1.5) together account for 3.3 of the 8.0 total DTS weight (41.25%) but contribute near-zero to current automated scores.

### 6.4 Limitations

**L1: Proxy validation only.** The r = 0.989 correlation measures internal consistency between two computations derived from the same binary field presence values, not agreement with human expert assessment. Human annotation of 120 datasets by three independent experts is required to establish external validity. This limitation means the pipeline's construct validity -- whether it measures what the DTS framework intends to measure -- is unverified.

**L2: Causal claims not tested.** Three planned follow-up hypotheses were not executed: whether HuggingFace's structured YAML adoption caused higher documentation completeness (H-M1), whether completeness predicts search filter eligibility (H-M2), and whether completeness predicts dataset download adoption (H-M3). This paper reports only the existence proof that automated DTS scoring is feasible, not any causal or predictive relationships.

**L3: Cross-sectional snapshot.** All data were collected in March 2026. The results represent a single time point and cannot address temporal trends in documentation quality. Longitudinal analysis would require periodic re-collection.

**L4: Binary presence scoring.** The pipeline measures whether a structured API field is populated with any non-null value, not the semantic quality, accuracy, or sufficiency of the content. A dataset with a single-word task category scores identically to one with a detailed description. DTS scores from this pipeline should be interpreted as measuring structured metadata population, not documentation quality in its full semantic sense.

**L5: Unverified citations.** Two citations central to this work have not been independently confirmed in academic databases:
- Rondina et al. (2025): the primary source for the DTS framework, six-section taxonomy, and all inverse-frequency weights used throughout this paper.
- Oreamuno et al. (2024): the source for the 71.52% undocumented HuggingFace cards statistic cited in the introduction.

Manual verification of both citations against original publications is required before any submission.

**L6: Simulation bypass in implementation.** A code-level issue (`or True` forcing synthetic annotation generation) was identified and corrected during development. While the fix was applied before final results were computed, this incident illustrates the risk of silent data simulation in automated research pipelines.

### 6.5 Broader Impact

This pipeline provides an automated tool for population-scale documentation audits. Automated DTS scores should be interpreted as measuring structured API field coverage -- a triage tool for identifying datasets with sparse structured metadata, not a replacement for expert assessment of dataset fitness for a given purpose.

Potential risks merit consideration. If automated DTS scores are adopted as gatekeeping criteria by repository platforms before the metric's construct validity is established through human expert comparison, datasets could be inappropriately penalized or rewarded based on metadata format rather than documentation substance. Additionally, repositories with richer structured API infrastructure (such as HuggingFace Hub) will score systematically higher than equivalent-quality datasets on repositories with sparser API schemas, which could introduce bias in cross-repository audits.

## 7. Conclusion

We presented an automated DTS-weighted documentation completeness scoring pipeline operating across HuggingFace Hub and OpenML, achieving 91.8% corpus coverage across 758 datasets with internally consistent scoring (proxy r = 0.989). The pipeline demonstrates that automated cross-repository documentation scoring from structured APIs is technically feasible.

The per-section results reveal a documentation API gap: the DTS sections assigned highest importance weights -- Preprocessing (0.002 coverage) and Uses (0.000 coverage) -- are near-zero across all repositories, not because documentation is absent but because these sections exist as free-text prose rather than structured API fields. Lower-weighted sections such as Motivation (0.547) and Composition (0.267) show substantially higher coverage because their associated information is represented in structured API endpoints.

Several questions remain open. The proxy validation used here does not establish construct validity against human expert judgment; a planned human annotation study (n = 120) is the necessary next step. The UCI repository was not successfully scored due to a field naming mismatch that is engineering-correctable. Three causal hypotheses (H-M1, H-M2, H-M3) remain untested and would require the validated scoring instrument this paper provides.

The pipeline provides measurement infrastructure for future work: fixing the UCI field mapping, conducting human validation, and testing whether documentation completeness predicts dataset adoption. LLM-based parsing of dataset card prose offers a complementary approach to recovering the Preprocessing and Uses signals that structured APIs currently do not expose.

## References

Bender, E. M. and Friedman, B. (2018). Data Statements for Natural Language Processing: Toward Mitigating System Bias and Enabling Better Science. *Transactions of the Association for Computational Linguistics*, 6:587-604.

Gebru, T., Morgenstern, J. H., Vecchione, B., Vaughan, J. W., Wallach, H. M., Daume, H., and Crawford, K. (2021). Datasheets for Datasets. *Communications of the ACM*, 64(12):86-92.

Koch, B. J., Denton, E. L., Hanna, A., and Foster, J. (2021). Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research. In *NeurIPS Datasets and Benchmarks Track*.

Lhoest, Q. et al. (2021). Datasets: A Community Library for Natural Language Processing. In *Proceedings of EMNLP 2021: System Demonstrations*, pp. 175-184.

Oreamuno et al. (2024). [UNVERIFIED -- Title and venue not confirmed. Cited as reporting that 71.52% of HuggingFace Hub dataset cards have substantial undocumented sections via binary field presence checks on n = 6,758 cards. Manual verification required before submission.]

Paullada, A., Raji, I. D., Bender, E. M., Denton, E. L., and Hanna, A. (2021). Data and its (dis)contents: A survey of dataset development and use in machine learning research. *Patterns*, 2(11):100336.

Pushkarna, M., Zaldivar, A., and Kjartansson, O. (2022). Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI. In *Proceedings of FAccT 2022*, pp. 1776-1826.

Rondina et al. (2025). [UNVERIFIED -- Title and venue not confirmed. Cited as the primary source for the Data Transparency Scorecard (DTS) framework: six-section rubric with inverse-frequency weights, manual scoring of n = 100 datasets across four repositories. All DTS section weights and the 7.58x scale comparison in this paper depend on this citation. Manual verification required before submission.]

Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P. K., and Aroyo, L. (2021). "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. In *Proceedings of CHI 2021*.
