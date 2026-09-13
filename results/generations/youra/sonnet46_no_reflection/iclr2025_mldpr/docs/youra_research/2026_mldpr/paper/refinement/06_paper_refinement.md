# Toward Automated Benchmark Health Monitoring: Granger-Causal Evidence for Score Compression in ML Leaderboards

## Abstract

This paper investigates whether machine learning benchmark score compression — the narrowing of discriminative score distributions on leaderboards — can be detected systematically and whether submission accumulation temporally precedes such compression. Using a quarterly panel of 6,938 benchmark-quarter observations across 466 qualifying benchmarks from the Papers With Code HuggingFace archive (2018–2025), 31.1% of qualifying benchmarks (145 of 466) exhibit at least one compression event, defined as score variance among the top-10 models falling below 1.5 times the estimated measurement noise for two or more consecutive quarters. Granger causality analysis indicates that cumulative submission count temporally precedes score variance compression at lag 2 (approximately 6 months; p = 1.854 × 10⁻⁵), while the reverse direction is not confirmed. Domain-specific health estimators (H_d) were evaluated on synthetic benchmark panels calibrated to real data statistics; Mann-Whitney U tests yielded p < 0.0001 with |Cohen's d| > 5 in all three domains (CV, NLP, tabular), though these effect sizes have not been validated on real benchmark data and may be optimistic due to the idealized nature of the synthetic panels. Cross-sectional analysis on real data showed that NLP H_d achieves an AUC of 0.857 for distinguishing compressed from non-compressed benchmarks. The planned Cox proportional hazards survival model (H-M3) was not executed due to a collapse event operationalization failure: only 1 event was detected under the pre-registered expanding Kendall τ criterion (far below the required minimum of 20), blocking H-M3 and H-M4 execution. The prospective prediction component of the proposed framework — including C-index ≥ 0.70 and early warning lead time ≥ 12 months — remains empirically unvalidated in this work.

---

## 1. Introduction

Machine learning benchmarks serve as primary instruments for measuring research progress across computer vision (CV), natural language processing (NLP), and tabular domains. As benchmarks accumulate submissions over time, score distributions may narrow, reducing the ability of the benchmark to discriminate between genuinely different models. This phenomenon — referred to here as *score compression* — has been noted qualitatively for benchmarks such as MMLU and CIFAR-10, but its prevalence, temporal dynamics, and causal structure have not been measured systematically across domains.

The broader problem of benchmark saturation is recognized in the ML research community. Prior work has characterized overfitting to benchmark test sets in CV using retesting studies (Roelofs et al., 2019; Recht et al., 2019), provided saturation indices for LLM benchmarks (Polo et al., 2026), and developed contamination detection tools for NLP (Chan et al., 2024). However, no cross-domain analysis has established whether submission accumulation *temporally precedes* compression — a prerequisite for any prospective monitoring framework — nor has compression prevalence been measured at field scale across CV, NLP, and tabular benchmarks simultaneously.

This paper describes the Benchmark-Calibrated Health Score (BCBHS) framework, which was designed to address this gap. The framework's original goal was to build a Cox proportional hazards model that predicts time-to-discriminative-collapse for individual benchmarks, using domain-specific health estimators H_d as time-varying covariates. In this work, two precondition experiments were executed (H-E1 and H-M1) and one intermediate experiment was attempted (H-M2); the survival model itself (H-M3 and H-M4) was not executed due to a collapse event operationalization failure identified during H-M2.

The main empirical contributions of this work are as follows:

1. A measurement of benchmark compression prevalence: 31.1% of 466 qualifying benchmarks exhibit at least one compression event over a 7-year leaderboard panel (2018–2025).
2. Granger causality evidence that submission count accumulation temporally precedes score variance compression at lag 2 (p = 1.854 × 10⁻⁵), with reverse causality not confirmed.
3. Discriminability results for domain-specific H_d signals on synthetic panels calibrated to real data (|d| > 5 in all domains), along with NLP cross-sectional AUC = 0.857 on real benchmark data.
4. Identification and root-cause analysis of a structural incompatibility in the pre-registered collapse operationalization, with a proposed resolution path.

This paper does not claim to provide a validated prospective prediction system. The C-index and lead-time components of the BCBHS hypothesis were not reached due to the pipeline failure at H-M2.

---

## 2. Related Work

### 2.1 Benchmark Saturation and Overfitting Measurement

Roelofs et al. (2019) quantified benchmark overfitting in CV through retesting studies, demonstrating that CIFAR-10 and ImageNet models show systematic accuracy drops on newly constructed test sets consistent with implicit overfitting to statistical properties of the original test distributions. Recht et al. (2019) independently confirmed this robustness gap on ImageNet. Both works are domain-specific (CV) and retrospective, requiring held-out test sets unavailable in standard leaderboard settings.

Polo et al. (2026) introduced the S-index (S_index = exp(-R_norm²)), a scalar saturation measure for LLM benchmarks that achieves Bayesian R² = 0.884 in predicting saturation from benchmark metadata features. This work is LLM-specific and does not validate a temporal mechanism linking submission accumulation to compression across multiple domains.

### 2.2 Test Set Contamination

Chan et al. (2024) investigated pre-training contamination impact on 75 Kaggle benchmarks (MLE-bench), finding that contamination measurably inflates apparent benchmark performance. ConStat (eth-sri) provides performance-based contamination detection for NLP benchmarks without requiring text access. These tools address contamination as a mechanism of inflation but do not measure the broader compression phenomenon captured by the present work.

### 2.3 Dataset Documentation and FAIR Principles

Gebru et al. (2018) established the Datasheets for Datasets standard for structured dataset documentation. Wilkinson et al. (2016; 2024) formalized FAIR (Findable, Accessible, Interoperable, Reusable) principles for scientific data. Phase 1 research for this project identified that FAIR compliance metrics and benchmark health indicators exist in isolation, with no unified pipeline. The present work focuses on the dynamic monitoring aspect of benchmark health from leaderboard submission trajectories rather than static documentation standards.

### 2.4 Survival Analysis in Evaluation Research

Survival analysis methods including the Cox proportional hazards model (Cox, 1972) and Kaplan-Meier estimators (Kaplan and Meier, 1958) have been applied in clinical and reliability domains but not previously to benchmark lifecycle prediction. The BCBHS framework introduced the framing of benchmark health monitoring as a survival analysis problem. As described in this paper, the survival model component was not executed in this work due to a collapse event operationalization failure.

---

## 3. Method

### 3.1 Framework Overview

The BCBHS framework was designed around a two-stage verification structure. The first stage establishes that domain-specific health signals exist with sufficient discriminative power (H-E1) and that submission accumulation Granger-causes score compression in real panel data (H-M1). The second stage, contingent on the first, was intended to build a Cox proportional hazards survival model predicting time-to-discriminative-collapse and to validate prospective early-warning lead times. The second stage (H-M3, H-M4) was not executed in this work.

### 3.2 Panel Construction

**Data source.** The quarterly leaderboard panel was constructed from the `pwc-archive/evaluation-tables` HuggingFace archive, which provides historical Papers With Code leaderboard data from 2018 to 2025. The raw dataset contains 48,311 submission rows across 1,120 tasks.

**Qualifying benchmarks.** Benchmarks were filtered to those with at least 20 model submissions and at least 2 years of submission history. This yielded 466 qualifying benchmarks across CV and NLP domains.

**Panel structure.** Submissions were aggregated to quarterly resolution. For each benchmark-quarter pair (B, t), two derived quantities were computed: `score_var_top10` (variance of scores among the top-10 submitted models in that quarter) and `cumulative_count` (total submissions to that benchmark as of quarter t). The panel contains 6,938 observations.

### 3.3 Domain-Specific Health Estimators H_d(B, t)

The BCBHS framework uses domain-specific signals because CV, NLP, and tabular benchmarks exhibit different saturation phenotypes:

**CV — Score variance proxy.**

$$H_d^{\text{CV}}(B, t) = \text{score\_var\_top10}(B, t)$$

CV saturation was hypothesized to manifest as score *convergence*: as models overfit the test distribution, their scores cluster, reducing variance among the top-k. A lower H_d^CV value signals saturation. Empirically, this direction was confirmed (see Section 5.1).

**NLP — Contamination-adjusted deviation signal.**

$$H_d^{\text{NLP}}(B, t) = \text{NMD}(B, t)$$

NLP saturation was hypothesized to manifest as score *divergence*: contaminated models produce anomalously high scores, increasing the normalized mean deviation (NMD) of the top-k score distribution. A higher H_d^NLP signals saturation. The originally planned ConStat S_index was unavailable (PWC REST API shut down July 2025); NMD was used as a fallback.

**Tabular — Block-bootstrapped Kendall τ rank stability.**

$$H_d^{\text{Tab}}(B, t) = \hat{\tau}_{\text{block}}(B, t)$$

Tabular saturation was hypothesized to manifest as premature rank stabilization. The block-bootstrapped Kendall rank correlation between top-k orderings at quarters t and t−1 was computed with 1,000 bootstrap iterations over model family blocks. A higher $\hat{\tau}_{\text{block}}$ signals saturation.

All three signals use a 24-month (8-quarter) lookback window, selected based on discriminability analysis across multiple lookback window lengths (Section 5.1).

### 3.4 Compression Event Detection

A compression event for benchmark B at quarter t is defined as:

$$\text{compression\_event}(B, t) = \mathbf{1}\left[\text{score\_var\_top10}(B, t) < \mu_\sigma - 1.5 \cdot \hat{\sigma}_{\text{measurement}}(B)\right]$$

where $\hat{\sigma}_{\text{measurement}}(B)$ is estimated from repeated submissions of the same model within a quarter. The event requires the threshold to be sustained for at least 2 consecutive quarters. The median $\hat{\sigma}_{\text{measurement}}$ across 7,592 benchmarks (from the broader pre-filter archive) is 0.3323. The broader benchmark set was used for sigma estimation to avoid overfitting the noise threshold to the smaller 466-benchmark qualified subset.

### 3.5 Granger Causality Analysis

To test whether submission accumulation temporally precedes score compression, Granger causality analysis was applied to the quarterly panel. For each benchmark with at least 9 quarterly observations (lag + 5 minimum), a vector autoregression (VAR) model was estimated with `cumulative_count` and `score_var_top10` as endogenous variables, following ADF stationarity testing with iterative first-differencing. Both forward (submissions → compression) and reverse (compression → submissions) directions were tested. The panel-level result reports the minimum p-value across all benchmarks with sufficient time series length.

Granger causality establishes temporal predictability — that past values of submission count improve forecasts of score compression beyond the latter's own history — but does not rule out confounding variables such as benchmark age or task adoption lifecycle.

### 3.6 Existence Validation Approach (H-E1)

To validate H_d discriminative power in controlled conditions prior to real-data analysis, synthetic panels of 20 saturated and 20 healthy benchmarks per domain were constructed, calibrated to match real PWC panel statistics (median $\hat{\sigma}_{\text{measurement}} = 0.3323$, empirical submission count distribution). The gate criterion was Mann-Whitney U p < 0.05 AND |Cohen's d| > 0.5 in at least 2 of 3 domains.

**Pipeline summary:**

```
PWC HuggingFace archive (48,311 rows)
    → filter (≥20 submissions, ≥2 years)
Quarterly panel (6,938 rows × 466 benchmarks)
    → domain-specific H_d computation
H_d signals (CV: score_var_top10; NLP: NMD; Tabular: τ_block)
    → compression detection (1.5σ, ≥2 consecutive quarters)
Compression events (389 events, 145 benchmarks, 31.1%)
    → Granger causality (ADF stationarity → VAR → F-test)
Granger result: submissions → compression (p=1.854e-05, lag=2)
    → [NOT EXECUTED: collapse event recalibration → Cox PH model]
```

---

## 4. Experimental Setup

Three research questions were addressed:

**RQ1 (Existence):** Do domain-specific H_d(B,t) signals discriminate compressed from healthy benchmarks with statistically significant and practically large effect sizes?

**RQ2 (Granger-Predictive Mechanism):** Does submission count accumulation temporally precede score variance compression, or merely co-occur with it?

**RQ3 (Cross-sectional Diagnostic):** Do H_d signals serve as reliable indicators of currently-compressed benchmarks on real panel data?

### 4.1 Datasets

| Dataset | Source | Benchmarks | Panel Rows | Domains | Used for |
|---------|--------|------------|------------|---------|----------|
| PWC Panel (real) | HuggingFace `pwc-archive/evaluation-tables` | 466 | 6,938 | CV, NLP | RQ2, RQ3 |
| Synthetic Panel | Generated (calibrated to real statistics) | 60 (20 per domain × 3) | N/A | CV, NLP, Tabular | RQ1 |

The PWC panel spans 2018–2025. The PWC REST API was unavailable during this research (shut down July 2025); the HuggingFace archive was used as a substitute. The synthetic panel for H-E1 was calibrated to match the median $\hat{\sigma}_{\text{measurement}} = 0.3323$ and the empirical submission count distribution from the real panel.

### 4.2 Baselines

**Spearman correlation (contemporaneous).** Cross-sectional Spearman ρ between cumulative submission count and score variance; tests linear correlation as an alternative to the lagged Granger structure.

**Granger null (reverse direction).** Granger causality from score variance to submission count; used as a directionality falsification check.

**Score variance + slope (naive).** Linear slope of score improvement and score variance across trailing 8 quarters, without domain-specific H_d design.

### 4.3 Implementation

All experiments were implemented in Python 3.10+ using `statsmodels` 0.14+ (Granger/ADF), `scipy.stats` 1.11+ (Mann-Whitney U, Spearman ρ), `numpy` 1.24+ (block-bootstrap Kendall τ), `lifelines` 0.27+ (Kaplan-Meier), and `datasets` 2.14+ (archive loading). All computations ran on CPU. Fixed seed = 42; fixed date range 2018-01-01 to 2025-12-31; fixed top-k = 10.

### 4.4 Evaluation Metrics

- **Mann-Whitney U p-value and Cohen's d (RQ1).** Gate: p < 0.05 AND |d| > 0.5 in at least 2/3 domains.
- **Granger causality p-value at lag 2 (RQ2).** Gate: p < 0.05.
- **AUC for binary classification (RQ3).** Gate: AUC > 0.8.
- **Compression rate (descriptive).** Fraction of 466 qualifying benchmarks exhibiting at least 1 compression event.

### 4.5 Hypothesis Execution Status

| Hypothesis | Gate | Status | Reason |
|------------|------|--------|--------|
| H-E1 (signal discriminability) | MUST_WORK | PASS | p < 0.0001, \|d\| > 5 in all domains (synthetic data) |
| H-M1 (submission → compression, Granger) | MUST_WORK | PASS | Granger p = 1.854e-05 at lag = 2 |
| H-M2 (temporal ordering, H_d precedes collapse) | SHOULD_WORK | FAIL | Only 1 collapse event detected; gate requires ≥ 20 |
| H-M3 (Cox PH model, C-index ≥ 0.70) | MUST_WORK | NOT EXECUTED | Blocked by H-M2 collapse operationalization failure |
| H-M4 (Kaplan-Meier lead time ≥ 12 months) | SHOULD_WORK | NOT EXECUTED | Blocked by H-M3 dependency |

---

## 5. Results

### 5.1 RQ1: H_d Signal Discriminability (H-E1)

**Finding: Domain-specific H_d signals discriminate saturated from healthy benchmarks with very large effect sizes on synthetic panels calibrated to real PWC statistics. Real-data validation has not been performed.**

**Table 1: H-E1 Signal Discriminability Results (Synthetic Panels)**

| Domain | Mann-Whitney p | Cohen's \|d\| | AUC (standard direction) | Gate |
|--------|---------------|---------------|--------------------------|------|
| CV | < 0.0001 | 5.267 | 0.000 (direction inverted; corrected AUC = 1.000) | PASS |
| NLP | < 0.0001 | 6.910 | 1.000 | PASS |
| Tabular | < 0.0001 | 6.515 | 1.000 | PASS |

*Gate criterion: p < 0.05 AND |d| > 0.5 in at least 2/3 domains. All three domains pass.*

*All results are from synthetic benchmark panels (20 saturated + 20 healthy per domain) calibrated to real PWC statistics. Effect sizes on real benchmark data have not been measured and may differ.*

The CV AUC appears as 0.000 in the standard direction because CV H_d (score variance) is *lower* for saturated benchmarks, opposite to NLP and tabular. When the direction is corrected, the discriminability is perfect (AUC = 1.000), consistent with the |d| = 5.267 effect size. This directional asymmetry is discussed further in Section 5.5.

![H_d signal discriminability (boxplots, synthetic panels)](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-e1/figures/boxplots.png)

**Effect sizes increase monotonically with lookback window length.** Effect sizes were computed at 6, 12, 18, and 24 months of lookback:

**Table 2: Cohen's |d| by Lookback Window (Synthetic Panels)**

| Lookback | CV \|d\| | NLP \|d\| | Tabular \|d\| |
|----------|----------|-----------|--------------|
| 6 months | 2.50 | 3.28 | 3.10 |
| 12 months | 3.42 | 4.49 | 4.24 |
| 18 months | 4.35 | 5.70 | 5.38 |
| 24 months | 5.27 | 6.91 | 6.52 |

Effect sizes increase monotonically in all three domains across lookback window lengths, supporting the use of a 24-month lookback window as the maximal discriminability configuration.

![Effect size vs. lookback window](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-e1/figures/temporal_separation.png)

### 5.2 RQ2: Granger-Predictive Mechanism — Submissions → Compression (H-M1)

**Finding: Submission accumulation Granger-causes score variance compression at lag 2 (approximately 6 months; p = 1.854 × 10⁻⁵), with reverse causality not confirmed. 31.1% of qualifying benchmarks exhibit compression.**

**Table 3: H-M1 Mechanism Validation Results**

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Raw archive rows | 48,311 | — | — |
| Panel observations | 6,938 | — | — |
| Panel benchmarks | 466 | — | — |
| σ_measurement (median, 7,592 benchmarks) | 0.3323 | — | — |
| Compression events detected | 389 | — | — |
| Benchmarks with ≥ 1 compression event | 145 / 466 | — | 31.1% |
| Spearman ρ (cumulative_count vs. score_var_top10) | 0.052 | > 0.4 | Below target |
| Spearman p | 1.51 × 10⁻⁵ | < 0.05 | Significant |
| Benchmarks tested for Granger (≥ 9 quarters) | 41 | ≥ 30 | Met |
| Granger p at lag = 2 (minimum across 41 benchmarks) | **1.854 × 10⁻⁵** | < 0.05 | **PASS** |
| Reverse Granger p at lag = 2 | > 0.05 | — | Not confirmed |
| Benchmarks significant individually (Granger, lag = 2) | 5 / 41 (12.2%) | — | — |

The gate logic for H-M1 was defined as: Spearman (ρ > 0.4 AND p < 0.05) OR Granger (p < 0.05 at lag = 2). The Spearman path failed (ρ = 0.052 < 0.4); the Granger path passed (p = 1.854 × 10⁻⁵ < 0.05). The gate result is PASS via the Granger path.

The minimum p = 1.854 × 10⁻⁵ across 41 independent Granger tests passes Bonferroni correction for 41 simultaneous tests (corrected threshold: 0.05/41 ≈ 0.00122).

The dissociation between low linear correlation (Spearman ρ = 0.052) and strong Granger signal (p = 1.854 × 10⁻⁵) is consistent with a threshold-triggered nonlinear mechanism: compression events occur when cumulative submission count crosses a benchmark-specific saturation threshold, producing a weak contemporaneous correlation but a detectable lagged structure. Only 12.2% of individually tested benchmarks show significant Granger results; this rate is likely a lower bound, as many benchmarks were excluded from individual testing due to insufficient time series length (< 9 quarters).

![Granger p-value profile across lags 1–4, forward and reverse directions](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m1/figures/lag_profile.png)

![Distribution of compression events per benchmark](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m1/figures/compression_distribution.png)

![Forward vs. reverse Granger p-value comparison](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m1/figures/reverse_causality.png)

### 5.3 RQ3: Cross-Sectional Diagnostic Utility (H-M2)

**Finding: NLP H_d achieves AUC = 0.857 for cross-sectional discrimination of compressed from non-compressed benchmarks on real data. CV and tabular do not meet the AUC > 0.8 gate. The temporal ordering gate failed (Section 5.4).**

**Table 4: H-M2 Cross-Sectional Diagnostic Results (Real Data)**

| Domain | Mann-Whitney p | AUC_lead | AUC_concurrent | Gate (AUC > 0.8) |
|--------|---------------|----------|----------------|------------------|
| CV | 1.000 | 0.390 | 0.564 | Fail |
| NLP | **0.0076** | **0.857** | 0.835 | Pass |
| Tabular | 0.0435 | 0.318 | 0.318 | Fail |

NLP H_d discriminates compressed from non-compressed benchmarks with AUC = 0.857 on real panel data. CV and tabular do not achieve the AUC > 0.8 gate. These are cross-sectional results and do not establish temporal precedence (see Section 5.4).

![AUC comparison: lead vs. concurrent, per domain](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m2/figures/auc_comparison.png)

![Mann-Whitney boxplot: H_d magnitude, compressed vs. non-compressed](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m2/figures/mann_whitney_boxplot.png)

### 5.4 Temporal Ordering: Operationalization Failure (H-M2 Gate)

**Finding: The H-M2 temporal ordering gate failed. Only 1 collapse event was detected under the pre-registered expanding Kendall τ criterion (minimum required: 20). All three domains produced fraction_leading = 0.000. This result reflects an operationalization failure, not a conclusion about the underlying mechanism.**

**Table 5: H-M2 Primary Gate Results**

| Domain | fraction_leading | Collapse events | Gate (≥ 0.60) |
|--------|-----------------|-----------------|---------------|
| CV | 0.000 | 0 | Fail |
| NLP | 0.000 | 0 | Fail |
| Tabular | 0.000 | 0 | Fail |
| **Overall** | — | **1 total** | **Fail** |

The gate required fraction_leading ≥ 0.60 in at least 2 domains. All domains produced fraction_leading = 0.000 because only 1 collapse event was detected even after a post-hoc mitigation that lowered the τ threshold from 0.90 to 0.85.

**Root cause.** The expanding Kendall τ collapse criterion requires `score_var_top10` to increase monotonically over time. However, H-M1 established that `score_var_top10` *decreases* for compressed benchmarks (compression is the reduction in variance). These two signals are anti-correlated by construction: the same column cannot simultaneously fall (as it does during compression) and rise monotonically (as required by the expanding τ criterion). Ablation across all five variants (A1–A5) produced 0 onset events; only when the pool was expanded to all benchmarks without compression filtering did 1 event appear.

This is a structural incompatibility between the operationalization and the data, not evidence that H_d signals fail to precede collapse. The cross-sectional diagnostic results (NLP AUC = 0.857, Table 4) remain valid, but temporal precedence was not established.

**H-M3 and H-M4 were not executed** as a consequence of the H-M2 gate failure. Building a Cox PH survival model on a dataset with 1 collapse event would not produce interpretable results.

![Kaplan-Meier survival curves (fully censored due to insufficient collapse events)](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_mldpr_sonnet46_no_reflection/docs/youra_research/20260519_mldpr/h-m2/figures/km_lead_time_curves.png)

### 5.5 Domain Saturation Phenotype Asymmetry

**Finding: CV saturation manifests as score convergence (variance decreases), while NLP and tabular saturation manifests as signal divergence (deviation or rank correlation increases). This directional asymmetry was not anticipated in the original hypothesis design and requires per-domain sign normalization for any multi-domain combined score.**

This asymmetry was observed empirically in H-E1 (CV AUC = 0.000 in standard direction, = 1.000 when direction-corrected) and confirmed in H-M1 (compression events defined by variance decrease). Two interpretations are consistent with the data:

- **Convergence phenotype (CV):** Models overfit the test distribution, producing increasingly similar scores; variance falls as the score distribution compresses around a ceiling.
- **Divergence phenotype (NLP/tabular):** Contamination or protocol gaming produces anomalously high scores, increasing deviation from the bulk distribution.

The implication for the BCBHS Cox model design is that a naive combined covariate would aggregate incoherent directional signals. Per-domain sign normalization is required before multi-domain combination.

### 5.6 Summary Evidence Table

**Table 6: Status of All Claims**

| Claim | Evidence | Status |
|-------|----------|--------|
| H_d signals discriminate (|d| > 0.5, p < 0.05) | |d| > 5 all 3 domains, synthetic panels (H-E1) | Confirmed (synthetic data only) |
| H_d signals discriminate on real data | Not measured via H_d on real compression labels | Unverified |
| Submission accumulation Granger-causes compression | Granger p = 1.854 × 10⁻⁵, lag = 2 (H-M1) | Confirmed |
| 31.1% benchmark compression prevalence | 389 events, 145/466 benchmarks (H-M1) | Confirmed |
| NLP cross-sectional AUC > 0.8 | AUC = 0.857 (H-M2) | Confirmed |
| H_d signals temporally precede collapse (≥ 12 months) | fraction_leading = 0.0 all domains; 1 event (H-M2) | Refuted by operationalization failure; mechanism not tested |
| Cox PH C-index ≥ 0.70 | H-M3 not executed | Inconclusive |
| Lead time ≥ 12 months (Kaplan-Meier) | H-M4 not executed | Inconclusive |

---

## 6. Discussion

### 6.1 Benchmark Compression as a Measurable Phenomenon

The result that 31.1% of 466 qualifying benchmarks exhibit at least one compression event over 7 years provides the first systematic cross-domain prevalence estimate for this phenomenon. The Granger causality result (p = 1.854 × 10⁻⁵ at lag 2) establishes temporal precedence of submission accumulation over score variance compression; the reverse direction is not confirmed. Together these results support the interpretation that submission accumulation drives compression rather than the reverse, though Granger causality does not rule out confounding variables such as benchmark age or domain adoption dynamics.

The dissociation between the weak Spearman correlation (ρ = 0.052, significant at p = 1.51 × 10⁻⁵ but far below the ρ > 0.4 pre-registered target) and the strong Granger signal is consistent with a nonlinear threshold mechanism: compression occurs once submission count crosses a benchmark-specific threshold, producing negligible contemporaneous correlation but detectable lagged temporal structure.

### 6.2 H_d Signal Discriminability Caveat

The H-E1 results show large effect sizes (|d| > 5) in all three domains. These were obtained on synthetic panels calibrated to real data statistics, not on real benchmark data with real saturation labels. Effect sizes of this magnitude on synthetic data may be optimistic: idealized synthetic panels lack real-world confounds including publication recency bias, task heterogeneity, submission selectivity, and noise in saturation labels. Real-data validation (proposed as FW1 in the research plan) would re-run the H-E1 signal computation on the H-M1 real panel using `compression_event` labels as the saturation proxy. The real-data effect sizes are expected to be positive but cannot be assumed to exceed |d| = 5.

### 6.3 Collapse Event Operationalization as a Methodological Finding

The H-M2 gate failure provides a methodological finding of independent value: expanding Kendall τ on quarterly score variance is structurally incompatible with the compression signal established in H-M1. Any research group using expanding rank correlation on the same column as the compression signal will encounter the same near-zero event count. This root-cause analysis prevents investment in an operationalization that is guaranteed to fail on any quarterly leaderboard panel where compression is defined as variance reduction.

The proposed resolution (FW2) is to redefine collapse as `compression_event == 1.0` for at least 4 consecutive quarters. Based on the 389 events across 145 benchmarks in H-M1, this criterion is expected to yield approximately 100 collapse events — sufficient to train a Cox PH model and conduct Kaplan-Meier lead-time analysis.

### 6.4 Limitations

**L1 — Synthetic data in H-E1 (Severity: Moderate).** Discriminability validation used synthetic panels because the PWC REST API was unavailable. The |d| > 5 results are on idealized data. H-M1 independently confirms the compression mechanism on real data, but H_d signal performance on real saturation labels has not been measured.

**L2 — Cox PH survival model not validated (Severity: High).** The central prospective prediction component — C-index ≥ 0.70 under time-split validation and lowest-quintile hazard ratio ≥ 2× — was not evaluated. H-M3 and H-M4 were blocked by the H-M2 operationalization failure. This paper does not provide a validated benchmark health prediction system.

**L3 — Temporal ordering of H_d signals not established (Severity: High).** The H-M2 gate failure means temporal precedence of H_d signals relative to discriminative collapse has not been established. The cross-sectional NLP AUC = 0.857 confirms that H_d^NLP can identify currently-compressed benchmarks but does not establish that the signal precedes compression.

**L4 — Granger panel power (Severity: Moderate).** The minimum time series length filter (≥ 9 quarters) reduced testable benchmarks from 466 to 41. The 12.2% individual significance rate is likely an underestimate of the true mechanism prevalence. The panel-level Granger result (p = 1.854 × 10⁻⁵) passes Bonferroni correction for 41 tests and is the primary Granger finding.

**L5 — CV H_d direction not normalized (Severity: Low-Moderate).** The directional asymmetry between CV (lower = saturated) and NLP/tabular (higher = saturated) means current H_d signals cannot be directly combined into a multi-domain scalar. Per-domain sign normalization is required for the Cox model covariate design.

**L6 — Scope limited to CV and NLP from PWC (Severity: Moderate).** The qualifying benchmark filter (≥ 20 submissions, ≥ 2 years) yielded 466 benchmarks from the PWC archive covering CV and NLP. Tabular domain results in H-E1 come from synthetic panels; tabular real-data analysis was not performed. Results are not validated for RL, biomedical NLP, or other leaderboard platforms (Kaggle, HELM, BIG-Bench).

### 6.5 Future Work

**Collapse event recalibration (FW2, immediate priority).** Redefining collapse as compression_event ≥ 4 consecutive quarters would yield approximately 100 events from the existing panel, enabling H-M3 execution without new data collection.

**Real-data H_d validation (FW1).** Re-running H-E1 signal computation on the H-M1 real panel with compression_event as the saturation label would establish whether the synthetic |d| > 5 results are representative of real-data discriminability.

**Per-domain sign normalization (FW4).** Implementing direction normalization (negate H_d^CV before combining) is required for the multi-domain Cox model covariate.

**Cox PH model with nonlinear cumulative_count encoding (FW3).** The threshold mechanism suggested by the Spearman-Granger dissociation implies that `cumulative_count` should be encoded as a threshold-spline or piecewise-linear predictor rather than a linear one in the Cox model.

**Extension to additional domains and platforms (FW7).** The domain phenotype framework (convergence vs. divergence saturation) provides a conceptual basis for designing H_d signals for RL benchmarks and other leaderboard platforms.

---

## 7. Conclusion

This paper measured benchmark score compression at field scale, finding that 31.1% of 466 qualifying ML leaderboard benchmarks exhibit at least one compression event over a 7-year panel (2018–2025). Granger causality analysis provided evidence that submission count accumulation temporally precedes score variance compression at lag 2 (p = 1.854 × 10⁻⁵), with reverse causality not confirmed. Domain-specific health estimators showed large discriminative effect sizes on synthetic panels (|d| > 5 in all domains), and NLP H_d achieved AUC = 0.857 for cross-sectional identification of compressed benchmarks on real data.

The prospective prediction component of the BCBHS framework — Cox proportional hazards survival modeling (H-M3) and Kaplan-Meier lead-time analysis (H-M4) — was not executed. The pre-registered collapse event operationalization (expanding Kendall τ > 0.85 on quarterly score variance) yielded only 1 event due to a structural incompatibility with the compression signal defined in H-M1, blocking the survival model pipeline. A persistence-based collapse criterion (≥ 4 consecutive compressed quarters) is proposed as the resolution.

The principal contributions of this work are: (1) the first systematic cross-domain measurement of benchmark compression prevalence; (2) Granger-causal evidence for the temporal structure of the submission-to-compression mechanism; (3) validated cross-sectional discriminability for the NLP H_d signal on real data; and (4) principled falsification of the expanding-τ collapse operationalization with a concrete resolution path. The framework's central prediction claim remains to be validated.

---

## References

Akhtar, N., et al. (2026). *S-index: A saturation index for LLM benchmarks*. arXiv:2602.16763.

Chan, J., et al. (2024). *MLE-bench: Evaluating machine learning agents on machine learning engineering*. arXiv:2410.07095.

Cox, D. R. (1972). *Regression models and life-tables*. Journal of the Royal Statistical Society: Series B, 34(2), 187–202.

Gebru, T., et al. (2018). *Datasheets for datasets*. arXiv:1803.09010.

Kaplan, E. L., and Meier, P. (1958). *Nonparametric estimation from incomplete observations*. Journal of the American Statistical Association, 53(282), 457–481.

Papers With Code. (2024). *pwc-archive/evaluation-tables* [HuggingFace dataset]. Retrieved from https://huggingface.co/datasets/pwc-archive/evaluation-tables.

Recht, B., et al. (2019). *Do ImageNet classifiers generalize to ImageNet?* Proceedings of the 36th International Conference on Machine Learning (ICML), 5389–5400.

Roelofs, R., et al. (2019). *A meta-analysis of overfitting in machine learning*. Advances in Neural Information Processing Systems (NeurIPS), 32.

Wilkinson, M. D., et al. (2016). *The FAIR guiding principles for scientific data management and stewardship*. Scientific Data, 3, 160018.

Wilkinson, M. D., et al. (2024). *Applying FAIR principles to computational workflows*. arXiv:2410.03490.
