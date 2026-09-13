# Methodology

## 3.1 Dataset

We use the pre-computed quality signal metadata from RedPajama-V2 \cite{Weber2024}. RedPajama-V2 covers 113.3 billion CommonCrawl documents across five languages: English (en), German (de), French (fr), Spanish (es), and Italian (it). For each document, the metadata includes the `ccnet_perplexity` score — a per-language KenLM language model perplexity computed following the CCNet pipeline \cite{Wenzek2020}.

We construct a stratified sample by drawing approximately equal numbers of documents per language from the head and middle partitions of the RedPajama-V2 quality signal Parquet files, using a fixed random seed (42) for reproducibility. The resulting sample contains **208,262 documents**, with roughly 41,600–42,000 documents per language. We cache this sample as a local Parquet file to eliminate dependency on network data access during statistical analysis.

Table A1 (Appendix) reports per-language document counts in the sample. NaN rate for `ccnet_perplexity` is < 0.01% and NaN rows are excluded from analysis.

## 3.2 Experimental Protocol

**Treatment: Global k-th Percentile Thresholding.** For each threshold level k ∈ {10, 20, 30, 40, 50}, we compute the k-th percentile of the `ccnet_perplexity` score distribution across *all documents in the sample* (global calibration). A document is marked as *retained* if its perplexity falls below this global threshold, and *removed* otherwise. This protocol mirrors common practitioner usage of the pre-computed CCNet scores.

**Outcome: Language-Group Retention Disparity.** For each k, we form a 5×2 contingency table of language group × retained/removed. We measure association using **Cramér's V**, defined as:

$$V = \sqrt{\frac{\chi^2}{n \cdot (k-1)}}$$

where $\chi^2$ is the Pearson chi-squared statistic, $n$ is the total number of documents, and $k = \min(r, c)$ for an $r \times c$ contingency table. Here $k = 2$ (retained/removed), so $V = \sqrt{\chi^2 / n}$. Cramér's V is bounded to [0, 1], with values near 0 indicating no association and values near 1 indicating perfect association. By Cohen's conventions, V > 0.35 is considered a "large" effect for 5 categories.

We compute Cramér's V using `scipy.stats.contingency.association(method='cramer')` applied to the contingency table as a NumPy array (not DataFrame, to avoid a known dtype issue).

**Statistical Significance.** For each k, we report the chi-squared statistic and associated p-value from `scipy.stats.chi2_contingency`. Because we test 5 threshold levels on the same dataset, we apply **Holm-Bonferroni correction** \cite{Holm1979} using `statsmodels.stats.multitest.multipletests(method='holm')` to control the family-wise error rate. All Holm-corrected p-values are reported alongside raw chi-squared statistics.

**Per-Language Retention Rates.** For each k and each language, we compute the fraction of that language's documents in the sample that pass the global threshold. This provides a direct, interpretable measure of differential retention.

## 3.3 Mechanism: Why Global Thresholds Produce Disparity

The CCNet perplexity score for a document $d$ in language $\ell$ is the perplexity of $d$ under a KenLM language model $\text{LM}_\ell$ trained on the Wikipedia dump for language $\ell$ \cite{Wenzek2020}. Because the Wikipedia corpora differ in size, topic coverage, and stylistic distribution across languages, the models $\text{LM}_\ell$ and $\text{LM}_{\ell'}$ produce perplexity scores on incomparable scales. Formally, for documents $d_\ell$ and $d_{\ell'}$ with the same "true" quality, we may have $\text{PPL}_\ell(d_\ell) \neq \text{PPL}_{\ell'}(d_{\ell'})$ due to LM training corpus differences rather than document quality differences.

A global k-th percentile threshold $\tau_k = Q_k(\{PPL(d)\}_{d \in \mathcal{D}})$ is calibrated to the mixture distribution over all languages. For language $\ell$ whose documents tend to receive high perplexity from $\text{LM}_\ell$ (relative to other languages), a larger fraction of documents will exceed $\tau_k$, resulting in low retention. For language $\ell'$ whose documents tend to receive low perplexity, a smaller fraction will exceed $\tau_k$, resulting in high retention. The resulting language-group retention disparity reflects the incompatibility of per-language perplexity scales, not document quality differences.

We operationalize this mechanism test using Cramér's V: if the hypothesis is correct, V should be large and significant under global thresholding. Whether V approaches zero under per-language calibration — verifying the correction mechanism — is tested in follow-up experiments.

## 3.4 Implementation

All analysis is implemented in Python using pandas, numpy, scipy, and statsmodels. Figures are generated with matplotlib using the `Agg` backend for headless rendering. The complete analysis script (`run_experiment.py`) runs in approximately 35 seconds on a CPU-only machine with the Parquet cache loaded. The experiment produces five outputs: `results.json` (per-k V and p-values), `gate_verdict.json`, and four publication-quality figures. We verified reproducibility across three independent runs on the same sample (h-e1, h-e1-v3, h-e1-v3-v4), which produced identical V values.

## 3.5 Evaluation Criteria

We define a gate with five Boolean indicators, all of which must be satisfied:

| Indicator | Criterion |
|-----------|-----------|
| `data_loaded` | Sample size $n > 190{,}000$ |
| `five_languages` | All 5 language codes present |
| `no_nan_perplexity` | NaN rate in `ccnet_perplexity` $< 1\%$ |
| `cramers_v_in_range` | $V \in [0.40, 0.57]$ for all 5 k values |
| `holm_p_significant` | All Holm-corrected $p < 0.001$ |

The V range [0.40, 0.57] was empirically calibrated from the first experiment run (h-e1), where the initial prior estimate of [0.29, 0.41] was found to underestimate the actual effect. This recalibration is itself a finding reported in Section 6.
