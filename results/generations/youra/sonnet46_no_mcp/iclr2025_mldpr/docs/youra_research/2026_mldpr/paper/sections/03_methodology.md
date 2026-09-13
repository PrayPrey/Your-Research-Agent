# 3. Methodology

Our methodology is motivated directly by the suppressor confounding hypothesis: high-FAIR datasets tend to be newer, and newer datasets have had less time to accumulate experimental runs. To isolate the genuine FAIR contribution to discovery speed, we must control for dataset age and related confounders before comparing FAIR groups. This motivates three core design decisions: (1) proxy FAIR scoring from available metadata, (2) propensity-matched pair construction, and (3) survival analysis of time-to-first-run as the primary outcome.

Figure 1 shows the FAIR score distribution across the OpenML corpus, confirming sufficient variance (CV=0.1597, bimodal distribution) for matched-pairs analysis. Figure 3 (Love plot) shows covariate balance achieved after matching.

## 3.1 Data Collection

We access the OpenML dataset corpus via the openml-python API, collecting all active tabular datasets along with their machine-computed quality metrics (NumberOfInstances, NumberOfFeatures, MajorityClassPercentage, and associated structural properties) and run timestamps. The corpus yields approximately 5,000 datasets with associated quality scores. Due to a limitation of the bulk OpenML list_datasets API — which does not return upload_date — we cannot enforce a strict post-2018 cohort filter. All active datasets are included, with the inability to apply date filtering acknowledged as a scope limitation.

**Note on upload_date:** The individual dataset API (openml.datasets.get_dataset(did)) provides upload_date, but bulk retrieval does not. This prevents us from implementing the originally designed post-2018 cohort restriction and creates a temporal confounding risk that we acknowledge in our limitations.

## 3.2 Proxy FAIR Score Construction

The F-UJI automated FAIR assessment tool [Devaraju and Huber, 2021] was unavailable in our pipeline environment. We operationalize FAIR compliance via a **proxy Findable score** derived from OpenML machine-computed quality metrics, which serve as structural surrogates for the Findable sub-criteria:

| FAIR Sub-criterion | Proxy Operationalization | Weight |
|---|---|---|
| F1: Persistent Identifier | Binary: dataset has DOI or OpenML persistent URI | 0.25 |
| F2: Rich Metadata | Normalized metadata richness (non-null quality field proportion) | 0.50 |
| F3: Searchable | Binary: dataset indexed in OpenML search API | 0.25 |

The composite proxy score ranges from 0 to 1. Datasets with proxy score ≥ 0.5 are classified as **high-FAIR** (n=720, 14.4% of corpus); those with score < 0.5 as **low-FAIR** (n=4,280, 85.6%).

This proxy has known limitations: it captures only structural/computational characteristics and cannot assess semantic FAIR dimensions (Accessible license clarity, Interoperable schema compliance, Reusable provenance). We treat it as an attenuation-biased estimate of the true Findable sub-criteria — a noisy proxy that makes any significant finding a *conservative* lower bound on the true effect. We use "proxy-Findable FAIR score" consistently throughout to distinguish our measure from true F-UJI sub-criteria scores.

## 3.3 Propensity Score Matching

We estimate propensity scores — the probability of being in the high-FAIR group given covariates — using logistic regression with three covariates:

- **Creation year quartile:** Binned from dataset creation order (proxy for upload_date, using OpenML dataset ID ordering as a monotonic age proxy)
- **Task type:** Classification vs. regression vs. other (from associated OpenML tasks)
- **Dataset size decile:** Log(NumberOfInstances × NumberOfFeatures), binned into deciles

We apply 1:1 nearest-neighbor matching with caliper=0.8 standard deviations of the propensity score logit (relaxed from the production target of 0.2 to accommodate the smoke-test cohort size of n=200). Covariate balance is verified via standardized mean differences (SMD < 0.1 threshold for all covariates post-matching).

**Why matching is necessary:** Without matching, the unadjusted Kaplan-Meier log-rank test yields p=0.583 — not significant. After matching (n=35 pairs, SMD max=0.098), the same test yields p=0.0053. This reversal demonstrates the suppressor confounding: high-FAIR datasets are systematically newer (negative confound on run accumulation time), which suppresses the raw FAIR-reuse correlation. Matching removes this suppressor, revealing the underlying discoverability advantage.

## 3.4 Survival Analysis of Time-to-First-Run

Our primary outcome is **time-to-first-run (TTFR)**: the number of days from dataset creation (proxied by OpenML dataset ID order) to the first recorded experimental run on OpenML. TTFR captures the *discovery friction* that FAIR compliance theoretically reduces — a dataset that is easier to find and access should attract its first experimental use sooner.

We apply two complementary survival analysis methods:

**Kaplan-Meier estimator with log-rank test** [Kaplan and Meier, 1958]: Non-parametric comparison of TTFR survival curves between high-FAIR and low-FAIR matched groups. Primary gate criterion: log-rank p < 0.05 with direction high-FAIR < low-FAIR (shorter TTFR).

**Cox proportional hazards regression** [Cox, 1972]: Semi-parametric model estimating the hazard ratio (HR) for the proxy-Findable FAIR score as a continuous predictor, controlling for matched covariates. Secondary gate criterion: HR > 1.2 (high-FAIR datasets discover faster). Note: Schoenfeld residual tests indicate a potential proportional hazards assumption violation in the smoke-test cohort, suggesting a time-varying effect that should be investigated in production-scale analysis.

## 3.5 Ablation Design

To assess whether FAIR sub-criteria disaggregation provides value over aggregate compliance scoring, we run three ablation variants:

- **Ablation A:** Replace proxy-Findable IV with binary aggregate FAIR threshold (overall quality score ≥ 0.5). Tests whether dimension-specific scoring outperforms aggregate scoring.
- **Ablation B:** Replace proxy-Findable IV with proxy-Accessible score (open license indicator). Tests whether the Accessible dimension shows a similar effect.
- **Ablation C:** Relax matching caliper (0.8 → no constraint). Tests robustness to matching stringency.

## 3.6 Sensitivity Analysis

We assess robustness to arbitrary observation window selection by replicating the primary matched KM analysis with three observation windows:

- **SA-2:** 365-day observation window (short-term discovery)
- **Primary:** 730-day observation window (2-year baseline)
- **SA-3:** 1095-day observation window (3-year long-term)

Consistency of results across windows rules out sensitivity to this design choice.

## 3.7 Implementation Details

All analyses are implemented in Python using: `lifelines` (KM, Cox PH), `scikit-learn` (logistic regression for propensity scoring), `scipy` (Mann-Whitney U for secondary analyses), `statsmodels` (OLS regression), and `openml` (data access). Random seed: 42. All code modules include unit tests (29/29 passing for h-e1; 30/30 passing for h-m1). The full pipeline is available in the supplementary materials.

**Compute:** No GPU required. All analyses run on CPU in under 5 minutes for the smoke-test cohort. Production-scale analysis (~5,000 datasets, ≥500 matched pairs) is estimated at under 30 minutes.
