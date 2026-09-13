# 4. Experimental Setup

## 4.1 Research Questions

We design our experiment to answer three specific questions corresponding to the existence claim:

**RQ1:** Does global k-th percentile thresholding on ccnet_perplexity produce statistically significant language-group retention disparity (Cramér's V > 0.10 with Holm p < 0.05)?

**RQ2:** Is the disparity consistent across the full practical range of threshold aggressiveness (k ∈ {10, 20, 30, 40, 50}), or does it only appear at specific threshold levels?

**RQ3:** Does the retention ordering align with the CCNet KenLM mechanism prediction — specifically, do Germanic languages (en, de) show consistently lower retention than Romance languages (es, fr, it)?

These questions are not independent: RQ1 establishes the existence of the bias; RQ2 tests its structural consistency; RQ3 connects the measurement to the proposed mechanistic explanation, providing evidence that the disparity reflects language-family KenLM training corpus differences rather than random sample variation.

## 4.2 Dataset

**RedPajama-V2 Quality Signal Parquet (208,262 documents).** We use the ccnet_perplexity field from the RedPajama-V2 quality signal metadata, available as pre-computed Parquet files from the HuggingFace repository. Our analysis covers the head and middle partitions, stratified to yield approximately 41,600 documents per language across five languages: en, de, es, fr, it.

| Language | Family | Documents | NaN rate |
|----------|--------|-----------|----------|
| de | Germanic | ~41,600 | < 0.01% |
| en | Germanic | ~41,600 | < 0.01% |
| es | Romance | ~41,600 | < 0.01% |
| fr | Romance | ~41,600 | < 0.01% |
| it | Romance | ~41,600 | < 0.01% |
| **Total** | | **208,262** | **< 0.01%** |

**Why this dataset.** RedPajama-V2 is one of the largest publicly available multilingual pretraining datasets with pre-computed CCNet-style quality signals. It provides ccnet_perplexity for the exact five-language set (en/de/es/fr/it) that spans the Romance–Germanic language family divide, making it the natural testbed for the measurement hypothesis. The pre-computed nature of the signal allows CPU-only analysis without requiring LM retraining.

## 4.3 Thresholds Evaluated

We evaluate five threshold levels k ∈ {10, 20, 30, 40, 50}, where the global k-th percentile threshold retains documents with ccnet_perplexity below the k-th percentile of the combined distribution across all five languages. This directly simulates the practitioner operation.

| k | Threshold (PPL) | Filtering Description |
|---|----------------|----------------------|
| 10 | 175.0 | Very aggressive: retain 10% lowest-PPL documents |
| 20 | 224.0 | Aggressive: retain 20% |
| 30 | 261.7 | Moderate: retain 30% |
| 40 | 295.1 | Permissive: retain 40% |
| 50 | 328.9 | Very permissive: retain 50% |

Thresholds are computed on the combined sample distribution. The key point is that these are global thresholds — they do not account for the different per-language perplexity distributions.

## 4.4 Evaluation Metrics

**Cramér's V.** Primary metric for measuring language-group retention disparity. Computed from the 5×2 contingency table (language × retained/removed) using `scipy.stats.contingency.association(method='cramer')`.

**Per-language retention rates.** For each k and language l: retention_rate(l, k) = |{retained documents in language l}| / |{total documents in language l}|. These provide the human-interpretable view of which languages are over- or under-retained.

**Max–min retention gap.** max_l(retention_rate(l, k)) − min_l(retention_rate(l, k)), computed per k. A concise scalar measuring the worst-case disparity between any two language groups.

**Statistical significance.** Chi-square p-value with Holm-Bonferroni correction across the 5 threshold levels. We report corrected p-values; all uncorrected p-values are effectively 0 (machine epsilon) given n = 208,262.

## 4.5 Implementation Details

All computation is performed in Python on standard CPU hardware. Key libraries:

- `pandas` (1.5+): Parquet loading, contingency table construction, groupby operations
- `scipy.stats` (1.9+): Chi-square computation, Cramér's V via `contingency.association`
- `statsmodels.stats.multitest`: Holm-Bonferroni correction via `multipletests`

**Reproducibility:** We use `random_state=42` for stratified subsampling. The data is cached as a local Parquet file (`redpajama_sample.parquet`). Total runtime: approximately 35 seconds on standard CPU hardware. No GPU, model inference, or network access required during experiment execution.

The full implementation is in `h-e1-v3-v4/code/run_experiment.py`. The core computation is:

```python
# Global k-th percentile threshold
threshold = df['ccnet_perplexity'].quantile(k / 100)
retained = df['ccnet_perplexity'] < threshold

# Contingency table: language × retained/removed
ct = pd.crosstab(df['language'], retained)

# Cramér's V
V = scipy.stats.contingency.association(ct, method='cramer')

# Holm-Bonferroni across k values
_, pvals_corrected, _, _ = multipletests(pvals_raw, method='holm')
```
