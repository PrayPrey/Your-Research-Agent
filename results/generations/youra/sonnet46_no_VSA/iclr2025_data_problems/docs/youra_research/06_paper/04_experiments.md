# Experiments

## 4.1 Setup

**Dataset.** We use a stratified sample of 208,262 documents drawn from the RedPajama-V2 quality signal metadata (head + middle partitions), covering five languages: de, en, es, fr, it. Per-language counts are approximately balanced (~41,600–42,000 per language). The pre-computed `ccnet_perplexity` score is the sole quality signal used; no model inference or external API calls are required.

**Environment.** All experiments run CPU-only on a single machine. The Parquet cache is loaded in under 5 seconds; total per-run wall time is approximately 35 seconds. We use Python 3.10 with the following key packages: `pandas==2.x`, `numpy==1.x`, `scipy==1.x`, `statsmodels==0.14.x`, `matplotlib==3.x`. The full conda environment specification is available in the code release.

**Threshold levels.** We apply global k-th percentile thresholds for k ∈ {10, 20, 30, 40, 50}. These five values span the practical range from aggressive filtering (retain bottom 10% by perplexity) to permissive filtering (retain bottom 50%). The resulting raw threshold values are: k=10: 175.0, k=20: 224.0, k=30: 261.7, k=40: 295.1, k=50: 328.9.

## 4.2 Implementation Details

The analysis proceeds in four stages:

1. **Data loading and validation.** The Parquet cache is loaded with PyArrow fallback to Apache Arrow IPC format if the Parquet engine is unavailable. Validation checks: row count $> 190{,}000$; exactly 5 language codes present; NaN rate in `ccnet_perplexity` $< 1\%$.

2. **Threshold computation and document labeling.** For each k, `numpy.percentile` computes the global k-th percentile of all 208,262 `ccnet_perplexity` values. Documents with perplexity below this threshold are labeled `retained=1`; all others `retained=0`.

3. **Contingency table and effect size.** For each k, a 5×2 contingency table is constructed via `pandas.crosstab(language, retained)`. Cramér's V is computed via `scipy.stats.contingency.association(contingency.values, method='cramer')` — the `.values` call converts to a NumPy array, which is required to avoid a known dtype issue in scipy when passing a DataFrame. The chi-squared statistic and raw p-value are from `scipy.stats.chi2_contingency`.

4. **Multiple testing correction.** Raw p-values from the 5 threshold levels are passed to `statsmodels.stats.multitest.multipletests(method='holm')` (Holm-Bonferroni). All `numpy.bool_` outputs are cast to Python `bool()` before JSON serialization to avoid a known serialization error.

5. **Visualization.** Four publication-quality figures are generated with matplotlib (Agg backend, 150 DPI): Cramér's V bar chart with gate bounds (Figure 1), per-language retention rate heatmap (Figure 2), max–min retention gap vs. k (Figure 3), and ccnet_perplexity KDE per language on a log scale (Figure 4).

## 4.3 Reproducibility

The experiment code (`h-e1-v3-v4/code/run_experiment.py`) was run three times across three hypothesis iterations (h-e1, h-e1-v3, h-e1-v3-v4). All three runs on the same cached Parquet sample produced identical V values (V = 0.4021, 0.5193, 0.5629, 0.5696, 0.5293 for k=10–50 respectively), confirming that the result is deterministic and stable. The iterations differed only in the gate bounds used to evaluate success; the statistical analysis was unchanged. Random seed 42 was used for stratified subsampling during cache construction.

The experiment exits with code 0 on gate pass. Output files include `results.json` (full per-k statistics), `gate_verdict.json` (gate_passed: true), and the four figure files. All outputs are committed to the research archive alongside the analysis script.
