# 3. Methodology

## 3.1 Overview

Building on the observation that CCNet's per-language KenLM models produce structurally incomparable perplexity scales across language families, we design a measurement methodology to quantify the language-group retention disparity produced by the practitioner-common operation: applying a single global k-th percentile threshold to pre-computed ccnet_perplexity scores across all languages simultaneously.

Our approach simulates the filtering operation directly on the pre-computed quality signal metadata from RedPajama-V2, without requiring access to the original text, LM retraining, or GPU infrastructure. This design choice is motivated by practicality: the ccnet_perplexity signal is pre-computed and available as a Parquet file, enabling any practitioner to replicate the measurement. It also ensures the measurement captures exactly what practitioners experience when applying this filter.

## 3.2 Dataset and Quality Signal

**RedPajama-V2 Quality Signal Sample.** We analyze the ccnet_perplexity field from the RedPajama-V2 quality signal metadata for a stratified subsample of 208,262 documents spanning five languages: English (en), German (de), French (fr), Spanish (es), and Italian (it). The subsample covers the head and middle partitions of the CommonCrawl-derived dataset. The ccnet_perplexity field contains perplexity scores computed using CCNet's pipeline: per-language KenLM n-gram models trained on language-specific Wikipedia, applied to CommonCrawl web documents after language identification.

**Why these five languages.** This is the exact five-language subset for which ccnet_perplexity is pre-computed in the RedPajama-V2 quality signal Parquet files. It covers two language families — Romance (es, fr, it) and Germanic (en, de) — enabling a direct test of whether the disparity aligns with family-level KenLM training corpus differences.

The perplexity distributions across languages show structurally divergent shapes (Figure 3). Germanic languages cluster at lower absolute perplexity values than Romance languages, consistent with the hypothesis that larger, more formal Germanic Wikipedias produce KenLM models that assign lower perplexity to Germanic web text.

## 3.3 Global k-th Percentile Thresholding

For each threshold level k ∈ {10, 20, 30, 40, 50}, we apply the following filtering rule:

```
retain document d if ccnet_perplexity(d) < P_k(all documents)
```

where P_k denotes the k-th percentile of the ccnet_perplexity distribution computed across all documents in the sample, regardless of language. This is the global threshold operation.

We evaluate five threshold levels to cover the full practical range from aggressive (k=10, retaining only 10% of documents with lowest perplexity) to permissive (k=50, retaining half). Each threshold level produces a binary retention indicator for each document.

**Rationale for k ∈ {10, 20, 30, 40, 50}.** These cover the range typically used in practice: very aggressive filtering (k=10) for high-quality focused corpora, moderate filtering (k=30) for balanced quality-quantity tradeoff, and permissive filtering (k=50) for large-scale pretraining. Assessing consistency of V across this range tests whether the disparity is structural (present throughout) or threshold-specific.

## 3.4 Measuring Language-Group Retention Disparity

For each threshold level k, we construct a 2×5 contingency table:

| | Retained | Removed |
|---|---|---|
| de | count | count |
| en | count | count |
| es | count | count |
| fr | count | count |
| it | count | count |

We measure language-group retention disparity using Cramér's V, computed as:

```
V = sqrt(chi² / (n * (min(r, c) - 1)))
```

where chi² is the Pearson chi-square statistic, n is the total document count, r is the number of rows (5 languages), and c is the number of columns (2: retained/removed). Cramér's V ranges from 0 (no association) to 1 (perfect association), with V > 0.5 conventionally classified as "large" by Cohen's criteria.

**Rationale for Cramér's V over alternatives.** Per-language retention rate differences are sensitive to the direction of comparison (which languages to subtract) and do not provide a single scalar measuring overall association strength. Cramér's V is symmetric, normalized, and standard for measuring association in r×c contingency tables — enabling direct comparison across threshold levels and future correction strategies.

## 3.5 Multiple Testing Correction

We apply Holm-Bonferroni correction across the five threshold levels, treating the null hypothesis H₀: V = 0 (no language-retention association) independently for each k. This controls the familywise error rate at α = 0.05 while being less conservative than Bonferroni correction for independent tests. We implement the correction using `statsmodels.stats.multitest.multipletests`.

## 3.6 Implementation

The measurement pipeline is implemented in Python using pandas (groupby operations and contingency tables), scipy.stats (chi-square computation, Cramér's V), and statsmodels (Holm correction). Total runtime is approximately 35 seconds on a standard CPU. The pipeline reads from a cached Parquet file containing pre-computed ccnet_perplexity values and language IDs, performing no model inference, HTTP API calls, or GPU computation.

We validate reproducibility through three independent runs on the same sample, confirming identical V values across runs (V = 0.4021–0.5696 for k=10–k=40, V = 0.5293 for k=50). The consistent results across runs confirm that the measurement is not sensitive to random seed or numerical precision.

**Stratification.** The 208,262-document sample is stratified to ensure adequate per-language representation (~42k documents per language), minimizing sampling composition artifacts. NaN rates in ccnet_perplexity are below 0.01%, with negligible impact on results.
