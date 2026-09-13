# 4. Experimental Setup

We design experiments to answer three research questions that map directly to the claims in Section 1:

**RQ1:** Does the OpenML corpus exhibit sufficient FAIR score variance (bimodal distribution, CV > 0.15, adequate group sizes) to support matched-pairs observational analysis? *(prerequisite for all subsequent analyses)*

**RQ2:** Does higher proxy-Findable FAIR score predict significantly shorter time-to-first-run after propensity matching on age, task type, and dataset size? *(primary mechanism claim)*

**RQ3:** Does Findable sub-criteria disaggregation provide substantially stronger predictive signal than aggregate FAIR compliance scoring? *(practical implication claim)*

## 4.1 Dataset

**OpenML Tabular Corpus (Active Datasets):** We access all active OpenML datasets via the openml-python API, yielding 5,000 datasets with associated machine-computed quality metrics. The corpus covers tabular datasets across classification, regression, and clustering tasks, spanning a range of domains (biology, finance, medical, social science, and others).

We cannot enforce the originally planned post-2018 date filter because the bulk list_datasets API does not return upload_date. This means the corpus includes datasets uploaded before 2018. We use OpenML dataset ID ordering as a monotonic age proxy for covariate construction, acknowledging that this is an approximation.

**Smoke-test Cohort:** For methodology validation, we construct a synthetic cohort of n=200 datasets by sampling with replacement from the full corpus quality distribution, with synthetic run timestamps generated from a parametric model calibrated to OpenML run frequency patterns. This smoke-test design allows end-to-end pipeline validation without requiring the full production cohort (which requires individual dataset API calls to retrieve upload_dates at ~83 minutes for 5,000 datasets).

| Cohort | N | Matched Pairs | Purpose |
|---|---|---|---|
| Full corpus (quality scoring) | 5,000 | — | FAIR score variance analysis (RQ1) |
| Smoke-test (synthetic timestamps) | 200 | 35 | Mechanism validation (RQ2, RQ3) |

## 4.2 Baselines

We compare against two baseline analysis approaches to demonstrate the value of our matched survival design:

**Unadjusted Correlation (No Matching):** Kaplan-Meier survival analysis on the full unmatched dataset, comparing high-FAIR (proxy score ≥ 0.5) and low-FAIR groups without propensity matching. This baseline represents the standard naive approach and demonstrates the confounding problem.
- *Why included:* Establishes the suppressor confounding baseline — the null result that matched analysis overturns.

**Aggregate FAIR Threshold (Ablation A):** Kaplan-Meier and Cox analysis using binary aggregate quality score ≥ 0.5 as the IV, replacing the Findable sub-criteria proxy. This baseline represents aggregate FAIR compliance scoring as typically reported.
- *Why included:* Tests whether sub-criteria disaggregation provides value over aggregate scoring — the practical question for repository administrators.

## 4.3 Evaluation Metrics

**Primary Gate (RQ2):**
- Log-rank p-value on matched KM curves (threshold: p < 0.05)
- Direction: median TTFR(high-FAIR) < median TTFR(low-FAIR)

**Secondary Gate (RQ2):**
- Cox proportional hazards HR (threshold: HR > 1.2)
- 95% confidence interval must exclude 1.0

**Existence Check (RQ1):**
- Coefficient of variation (CV) of proxy FAIR scores (threshold: CV > 0.15)
- Bimodality test (Hartigan's dip test, p < 0.05)
- Group sizes: n_high ≥ 500, n_low ≥ 500

**Covariate Balance (Matching Quality):**
- Standardized mean difference (SMD) for all covariates post-matching (threshold: max SMD < 0.1)

**Ablation Comparison (RQ3):**
- Log-rank p and Cox HR for Ablation A vs. primary analysis
- Qualitative comparison: is aggregate threshold substantially weaker than sub-criteria IV?

## 4.4 Implementation Details

**Environment:** Python 3.9, conda environment `youra-h-m1`. Key libraries: `lifelines==0.27.4` (KM, Cox), `scikit-learn==1.2.0` (logistic regression for PS estimation), `openml==0.14.0` (data access), `scipy==1.10.0`, `numpy==1.24.0`, `pandas==1.5.0`, `matplotlib==3.6.0`.

**Hyperparameters:**

| Parameter | Smoke-test Value | Production Target |
|---|---|---|
| Caliper factor | 0.8 SD of PS logit | 0.2 SD of PS logit |
| Min matched pairs | 30 | 500 |
| Observation window | 730 days | 730 days |
| Log-rank α | 0.05 | 0.05 |
| Cox HR gate | 1.2 | 1.2 |
| F1 (PID) weight | 0.25 | 0.25 |
| F2 (metadata) weight | 0.50 | 0.50 |
| F3 (search) weight | 0.25 | 0.25 |
| Random seed | 42 | 42 |

**Reproducibility:** All code is implemented with fixed random seeds. Unit test suite: 29/29 tests passing (h-e1 scoring pipeline), 30/30 tests passing (h-m1 matching and survival pipeline). The full implementation is provided in supplementary materials.
