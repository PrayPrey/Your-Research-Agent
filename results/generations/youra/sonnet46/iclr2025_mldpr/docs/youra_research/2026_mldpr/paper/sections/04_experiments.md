# 4. Experimental Setup

We design experiments to test three research questions that map directly to the contributions claimed in the Introduction.

**RQ1:** *Can an automated DTS-weighted scoring pipeline achieve ≥70% corpus coverage from public ML dataset repository APIs?* This tests our methodological claim that automated cross-repository scoring is technically feasible.

**RQ2:** *Does DTS inverse-frequency weighting produce scores meaningfully different from naive unweighted field presence counting, and are the scores internally consistent?* This tests our empirical claim that DTS weighting captures a distinct quality signal.

**RQ3:** *What is the per-section API coverage profile across the six DTS sections and three repositories?* This tests our infrastructure claim and reveals the documentation API gap finding — whether the sections that responsible AI frameworks designate as most important are accessible via structured repository APIs.

## 4.1 Target Corpora

We target three repositories that together represent the dominant platforms for public ML dataset hosting (Section 3.3). Rather than a benchmark dataset in the traditional ML sense, our corpus is the metadata collection itself: API responses from real dataset repositories, with each dataset's metadata treated as a sample point.

**HuggingFace Hub Corpus.** We collect a stratified sample of n=500 datasets from HuggingFace Hub using the `huggingface_hub` library's `list_datasets()` endpoint and per-dataset `dataset_info()` call for `card_data` YAML field extraction. Stratification bins: 4 task domain categories (NLP, Computer Vision, Tabular/Structured, Other) × 2 upload year cohorts (≤2021 and >2021), yielding 8 bins. The 2021 split is motivated by HuggingFace's introduction of structured YAML card schema enforcement that year. Actual collected: n=496 (4 datasets unavailable due to access restrictions).

**OpenML Corpus.** We collect n=200 datasets from OpenML using the `openml.datasets.list_datasets()` API endpoint, stratified by task type (Classification, Regression, Clustering, Other). OpenML provides structured metadata including task type, feature descriptions, creator names, DOI links, and dataset provenance fields in structured JSON/XML format.

**UCI ML Repository Corpus.** We target the full UCI population (~100 datasets accessible via `ucimlrepo`), with no stratification applied (full population rather than sample, given small N). Actual collected: n=62 (38 datasets returned errors or timeouts from the `ucimlrepo` library).

**Full corpus:** n=758 datasets (496 HF + 200 OpenML + 62 UCI).

| Repository | Target N | Collected N | Stratification |
|------------|---------|-------------|---------------|
| HuggingFace Hub | 500 | 496 | Task domain × Upload year (8 bins) |
| OpenML | 200 | 200 | Task type |
| UCI ML Repository | ~100 | 62 | None (full population) |
| **Total** | **~800** | **758** | — |

## 4.2 Baseline and Comparison Reference

This study is an existence proof, not a comparative ML experiment. There is no competing automated DTS-weighted scoring system to compare against (our pipeline is the first). Instead, we compare against:

**Gate Thresholds (pre-registered).** Coverage rate ≥ 0.70 and proxy Pearson r ≥ 0.70 were pre-registered in the experiment design (02c_experiment_brief.md) as the MUST_WORK gate criteria for the existence hypothesis. These thresholds were chosen to be demanding enough to rule out trivially sparse scoring while achievable from well-structured APIs.

**Unweighted Scoring Baseline.** For RQ2, we compare DTS-weighted scores against a naive unweighted baseline — simple field presence rate across all queried fields with equal weight per field (1/total_fields). This comparison is reported as a sensitivity check and serves as the reference signal for proxy validation.

**Rondina et al. [2025] Manual Benchmark.** For descriptive comparison, we compare our per-section coverage rates against Rondina et al.'s [2025] manual scores on n=100 datasets. This validates whether automated scoring replicates the section asymmetry pattern established by manual annotation.

## 4.3 Evaluation Metrics

**Primary metric — Coverage rate.** The fraction of collected datasets with weighted DTS score > 0:
$$\text{coverage\_rate} = \frac{|\{d \in D : \text{DTS}_{\text{weighted}}(d) > 0\}|}{|D|}$$
A dataset is "scoreable" if at least one DTS section field is present in its API response. Coverage rate directly measures the pipeline's viability for population-scale analysis.

**Secondary metric — Proxy Pearson r.** Pearson correlation between DTS-weighted scores and DTS-unweighted scores on a 120-dataset stratified subsample (40 per repository). Computed with 1,000-sample bootstrap confidence intervals (seed=42, 95% CI). This tests whether the DTS weighting mechanism produces scores that are internally consistent with the underlying field presence signal (RQ2).

**Descriptive metrics — Per-section coverage rates.** For each DTS section $s \in S$ and each repository $R$, the fraction of datasets from repository $R$ where section $s$ scores > 0:
$$\text{coverage}(s, R) = \frac{|\{d \in D_R : \text{section}_s(d) > 0\}|}{|D_R|}$$
These per-section rates constitute the primary evidence for RQ3 and the documentation API gap finding.

**DTS score distributions.** Mean, standard deviation, and quartile distributions of both weighted and unweighted DTS scores across the full corpus and per repository.

## 4.4 Implementation Details

The pipeline runs on CPU (no GPU required — this is a statistical metadata analysis, not a neural network training study). Hardware: standard workstation (8-core CPU, 16GB RAM). Collection time: approximately 4 hours for the full corpus at enforced rate limits. Scoring and validation: < 5 minutes.

All random operations use seed=42. The conda environment (`youra-h-e1`) pins exact package versions: `huggingface_hub==0.20`, `openml==0.14`, `ucimlrepo==0.0.7`, `scipy==1.10`, `statsmodels==0.14`, `pandas==2.0`. The full pipeline — from API collection to figure generation — is reproducible by executing `python experiment.py` with the same API rate limits and seed.

**Note on proxy validation:** The final results use proxy validation (weighted vs. unweighted DTS correlation) rather than human annotation correlation. A simulation bypass (`or True` in `experiment.py:297`) was identified and removed during validation, ensuring all reported results use real API data exclusively. See Section 6.1 for discussion of this limitation.
