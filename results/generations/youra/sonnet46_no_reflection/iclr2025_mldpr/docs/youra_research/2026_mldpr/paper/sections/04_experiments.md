# Experimental Setup

We design experiments to answer three research questions that map directly to the claims in Section 1:

**RQ1 (Existence):** Do domain-specific health estimators $H_d(B,t)$ discriminate compressed from healthy benchmarks with statistically significant and practically large effect sizes across CV, NLP, and tabular domains?

**RQ2 (Causal Mechanism):** Does submission count accumulation causally precede score variance compression in ML benchmarks, or does compression merely co-occur with submission volume?

**RQ3 (Cross-sectional Diagnostic):** Even absent temporal ordering confirmation, do $H_d$ signals serve as reliable diagnostic indicators of currently-compressed benchmarks?

## Datasets

**Papers With Code Leaderboard Panel (CV and NLP).** We load the complete `pwc-archive/evaluation-tables` HuggingFace archive, which provides historical Papers With Code leaderboard data from 2018 to 2025 following the PWC REST API shutdown in July 2025. From 48,311 raw submission rows across 1,120 tasks, we construct a quarterly panel by filtering to benchmarks with $\geq 20$ model submissions and $\geq 2$ years of submission history, yielding 6,938 panel observations across 466 qualifying benchmarks. This dataset is the primary source for RQ2 (Granger causality) and RQ3 (cross-sectional diagnostics).

**Synthetic Benchmark Panel (RQ1 — H-E1 existence test).** For controlled existence validation, we construct synthetic benchmark panels of 20 saturated and 20 healthy benchmarks per domain. Synthetic panel statistics match the real PWC panel: submission counts drawn from the empirical distribution, score values calibrated to match $\hat{\sigma}_\text{measurement}$ estimated from real data (median 0.3323 across 7,592 benchmarks), and temporal structure matching quarterly panel resolution. Synthetic panels allow controlled testing of $H_d$ discriminative power before committing to the real panel; real-data validation is a planned follow-up (FW1).

| Dataset | Source | Benchmarks | Rows | Domains | Used for |
|---------|--------|------------|------|---------|----------|
| PWC Panel (real) | HuggingFace archive | 466 | 6,938 | CV, NLP | RQ2, RQ3 |
| Synthetic Panel | Generated | 60 (20×3) | N/A | CV, NLP, Tabular | RQ1 |

## Baselines

**Score variance + slope (naive baseline).** A Cox model using only the linear slope of score improvement over trailing 8 quarters and the score variance across top-$k$ models. This represents what can be inferred without domain-specific $H_d$ design and serves as the primary benchmark for the BCBHS advantage.

**Spearman correlation (contemporaneous).** Cross-sectional Spearman $\rho$ between cumulative submission count and score variance across all benchmark-quarter observations. This tests whether submission count and compression are linearly correlated — a weaker claim than Granger causality. We include this as a reference to illustrate the difference between contemporaneous correlation and lagged causal structure.

**Granger null (reverse direction).** Granger causality from score variance to submission count (reverse direction). We use this as a falsification check: confirming the forward direction (submissions $\to$ compression) while not confirming the reverse validates causal directionality.

**S-index baseline (NLP only).** For NLP-domain cross-sectional diagnostics, we include the $S$-index signal (Polo et al. 2026) as a comparison point for $H_d^\text{NLP}$ classification performance.

## Implementation Details

All experiments are implemented in Python 3.10+ using the following libraries:

| Component | Library | Version |
|-----------|---------|---------|
| Granger causality, ADF stationarity | `statsmodels` | 0.14+ |
| Mann-Whitney U, Spearman $\rho$ | `scipy.stats` | 1.11+ |
| Block-bootstrap Kendall $\tau$ | `numpy` | 1.24+ |
| Kaplan-Meier survival analysis | `lifelines` | 0.27+ |
| HuggingFace archive loading | `datasets` | 2.14+ |

All experiments run on CPU (no GPU required — purely statistical pipeline). Compression detection uses the `compression_detector.py` module with threshold $1.5\hat{\sigma}_\text{measurement}$ and minimum 2 consecutive quarters. Granger tests use a maximum lag of 4 quarters with lag 2 as the primary evaluation point; ADF stationarity is enforced via iterative first-differencing before each Granger test.

**Reproducibility.** All experiments use seed 42. The quarterly panel is constructed deterministically from the HuggingFace archive with fixed date range (2018-01-01 to 2025-12-31) and fixed top-$k = 10$ for score variance computation.

## Evaluation Metrics

**Mann-Whitney U $p$-value and Cohen's $d$ (RQ1).** Non-parametric test appropriate for skewed score distributions; Cohen's $d$ provides standardized effect size for cross-domain comparison. Gate criterion: $p < 0.05$ AND $|d| > 0.5$ in $\geq 2/3$ domains.

**Granger causality $p$-value at lag 2 (RQ2).** $F$-test $p$-value from VAR model for the null that past values of cumulative\_count do not improve prediction of score\_var\_top10 beyond its own history. Evaluated at lag = 2 quarters ($\approx 6$ months). Gate criterion: $p < 0.05$.

**AUC for binary classification (RQ3).** Area under the ROC curve for classifying compressed vs. non-compressed benchmarks using $H_d$ as the diagnostic score. AUC $> 0.8$ indicates strong diagnostic power.

**Compression rate (descriptive).** Fraction of qualifying benchmarks exhibiting at least one compression event (count of benchmarks with $\geq 1$ event / 466 qualifying benchmarks). This quantifies field-scale prevalence.

Statistical significance is reported at $\alpha = 0.05$ throughout. For Granger causality, we report the minimum $p$-value across 41 benchmarks with sufficient time-series length ($\geq 9$ quarters) as the panel-level test statistic.
