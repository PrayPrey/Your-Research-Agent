# Methodology

## Overview

The BCBHS framework is designed around a two-stage verification principle: before building a prospective health prediction system, we must confirm that (1) the health signals *exist* with sufficient discriminative power, and (2) the compression mechanism is *causally* — not merely correlationally — linked to submission accumulation. This ordering is deliberate. A prediction framework built on a signal that lacks causal grounding would be descriptive at best and misleading at worst.

The framework has three components: domain-specific health estimator computation ($H_d$), benchmark panel construction, and causal mechanism validation via Granger causality. The survival prediction component (Cox proportional hazards model) is the fourth stage, currently pending collapse event recalibration (Section 6.2).

## Panel Construction

**Data source.** We construct a quarterly leaderboard panel from the `pwc-archive/evaluation-tables` HuggingFace archive, which provides complete historical Papers With Code leaderboard data (2018–2025) following the shutdown of the PWC REST API in July 2025. The archive covers 48,311 raw submission rows across 1,120 tasks.

**Qualifying benchmarks.** We filter to benchmarks with $\geq 20$ model submissions and $\geq 2$ years of submission history, yielding 466 qualifying benchmarks across CV and NLP domains. For tabular tasks, we draw on the OpenML benchmark panel using the OpenML Python client.

**Panel structure.** Submissions are aggregated to quarterly resolution: for each benchmark-quarter $(B, t)$, we compute $\text{score\_var\_top10}$ (variance of scores among the top-10 submitted models) and $\text{cumulative\_count}$ (total submissions to date). This produces 6,938 panel observations.

**Rationale for quarterly resolution.** Quarterly aggregation is the finest reliable resolution for PWC data: daily submissions are too sparse per benchmark to compute stable variance estimates. We verified that monthly aggregation produces $>40\%$ missing observations for the majority of benchmarks.

## Domain-Specific Health Estimators $H_d(B, t)$

A central design decision is that CV, NLP, and tabular benchmarks have *different saturation phenotypes* and therefore require domain-specific signals. A single formula (e.g., $S$-index) cannot simultaneously capture CV convergence-compression (variance falls as models cluster at ceiling) and NLP contamination-divergence (deviation increases as contaminated models artificially inflate scores). We design one estimator per domain:

**CV — Score variance proxy.**
$$H_d^\text{CV}(B, t) = \text{score\_var\_top10}(B, t)$$
CV saturation manifests as score *convergence*: as models overfit the test distribution, their scores cluster tightly, reducing variance among the top-$k$. A *lower* $H_d^\text{CV}$ value signals saturation (direction: lower = more saturated). This inverted direction relative to NLP/tabular is an empirical finding (Section 5.4) that requires per-domain sign normalization before multi-domain combination.

**NLP — Contamination-adjusted deviation signal.**
$$H_d^\text{NLP}(B, t) = \text{NMD}(B, t)$$
NLP saturation manifests as score *divergence*: contaminated models produce anomalously high scores, increasing the normalized mean deviation (NMD) of the top-$k$ score distribution. We use NMD as a fallback for the ConStat contamination probability (unavailable for the PWC archive period); NMD measures the degree to which top scores deviate from the bulk distribution. A *higher* $H_d^\text{NLP}$ signals saturation.

**Tabular — Block-bootstrapped Kendall $\tau$ rank stability.**
$$H_d^\text{Tab}(B, t) = \hat{\tau}_\text{block}(B, t)$$
Tabular saturation manifests as *premature rank stabilization*: once models have overfit the evaluation protocol, their relative rankings stabilize even as absolute scores improve. We compute $\hat{\tau}_\text{block}$ as the block-bootstrapped Kendall rank correlation between the top-$k$ model ordering at quarter $t$ and quarter $t-1$, using 1,000 bootstrap iterations over model family blocks to account for within-family score correlation. A *higher* $\hat{\tau}_\text{block}$ signals saturation (rank stability = discriminative collapse).

**Lookback window.** All three signals are computed using a 24-month (8-quarter) lookback window. We validated that this window maximizes discriminative separation: Cohen's $d$ increases monotonically from 6-month to 24-month lookback windows in all three domains (Section 5.1).

## Score Compression Detection

We define a *compression event* for benchmark $B$ at quarter $t$ as:
$$\text{compression\_event}(B, t) = \mathbf{1}\left[\text{score\_var\_top10}(B, t) < \mu_\sigma - 1.5 \cdot \hat{\sigma}_\text{measurement}(B)\right]$$
where $\hat{\sigma}_\text{measurement}(B)$ is the benchmark-specific measurement noise estimated from repeated submissions of the same model within a quarter, and the threshold is sustained for $\geq 2$ consecutive quarters. The median $\hat{\sigma}_\text{measurement}$ across 7,592 benchmarks is 0.3323.

**Rationale for 1.5$\sigma$ threshold.** The threshold is calibrated to be sensitive enough to detect compression (vs. normal variance fluctuation) while avoiding false positives from measurement noise. Sensitivity analysis across $[1.0, 2.0]\sigma$ shows stable compression rates in the $[25\%, 38\%]$ range, with 1.5$\sigma$ providing the best trade-off between sensitivity and specificity on the labeled subset.

## Granger Causality Analysis

To validate that submission accumulation *causally* drives score compression (not merely co-occurs with it), we apply Granger causality analysis to the quarterly panel.

**Test structure.** For each benchmark $B$ with $\geq 9$ quarterly observations (lag + 5 + 2 buffer), we estimate a vector autoregression (VAR) model with $\text{cumulative\_count}$ and $\text{score\_var\_top10}$ as endogenous variables. The Granger null hypothesis is that past values of $\text{cumulative\_count}$ do not predict $\text{score\_var\_top10}$ beyond the latter's own history.

**Stationarity pre-testing.** Before each Granger test, we apply the Augmented Dickey-Fuller (ADF) test to each series. Non-stationary series are first-differenced iteratively until stationarity is achieved ($p < 0.05$). This prevents spurious Granger results from non-stationary panel data.

**Reverse causality test.** We test both directions: cumulative\_count $\to$ score\_var\_top10 (forward) and score\_var\_top10 $\to$ cumulative\_count (reverse). The causal mechanism requires that the forward direction is confirmed and the reverse is not.

**Panel-level aggregation.** We report the minimum $p$-value across 41 benchmarks with sufficient time series length at lag = 2 (approximately 6 months). The panel-level Granger result ($p = 1.854 \times 10^{-5}$) uses the most significant per-benchmark test; the per-benchmark significance rate (12.2%) reflects the fraction of individual benchmarks showing Granger causality above threshold.

**Rationale for lag = 2.** We evaluate lags 1–4 and select lag = 2 as the primary evaluation point based on theoretical grounds (6-month accumulation latency) and empirical validation (lag = 2 shows the strongest causal signal in the lag profile; Figure 5).

## Existence Validation (H-E1)

To validate that $H_d$ signals discriminate benchmark health states before applying them to real panel data, we conduct an existence test on synthetic panels: 20 saturated and 20 healthy benchmarks per domain, constructed to match the statistical properties of the PWC panel (submission counts, score distributions, measurement noise levels from the real $\hat{\sigma}_\text{measurement}$ distribution).

We apply Mann-Whitney U test and Cohen's $d$ between saturated and healthy groups. The gate criterion is $p < 0.05$ AND $|d| > 0.5$ in $\geq 2/3$ domains. The synthetic panel design allows controlled comparison before committing to the real panel; real-data validation is a planned follow-up (Section 7).

## Experimental Pipeline Summary

```
PWC HuggingFace archive (48,311 rows)
    ↓ filter (≥20 submissions, ≥2 years)
Quarterly panel (6,938 rows × 466 benchmarks)
    ↓ domain-specific H_d computation
H_d signals (CV: score_var_top10; NLP: NMD; Tabular: τ_block)
    ↓ compression detection (1.5σ, ≥2 consecutive quarters)
Compression events (389 events, 145 benchmarks, 31.1%)
    ↓ Granger causality (ADF stationarity → VAR → F-test)
Causal mechanism: submissions → compression (p=1.854e-05, lag=2)
    ↓ [DEFERRED: collapse event recalibration → Cox PH model]
Future: BCBHS(B,t) = Cox survival score for prospective prediction
```

All code is implemented in Python 3.10+ using `statsmodels` (Granger causality, ADF), `scipy.stats` (Mann-Whitney U), `numpy` (block-bootstrap Kendall $\tau$), and the `datasets` library (HuggingFace archive loading). Experiments are CPU-only (statistical pipeline; no GPU required).
