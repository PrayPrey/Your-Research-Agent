# Product Requirements Document: H-M1
# Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis

**Version:** 1.0
**Date:** 2026-05-04
**Hypothesis:** H-M1 (MECHANISM — MUST_WORK)
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [step-01, step-02]

---

## 1. Executive Summary

This PRD defines implementation requirements for H-M1: a survival analysis study testing whether higher F-UJI **Findable** sub-criteria scores (persistent IDs, metadata richness, search indexing) cause shorter **time-to-first-run** in OpenML post-2018 tabular datasets.

The experiment extends the H-E1 validated cohort (5,000 scored datasets) by adding run timestamp data and applying propensity-score-matched Kaplan-Meier + Cox proportional hazards regression. Gate: **log-rank p < 0.05 AND Cox HR > 1.2** (MUST_WORK).

**Success = datasets with higher Findable sub-scores get their first experimental run significantly faster, after controlling for creation year, task type, and dataset size.**

---

## 2. Problem Statement

H-E1 established sufficient variance in FAIR compliance across OpenML datasets (CV=0.1597, bimodal distribution confirmed). H-M1 tests the *causal mechanism*: does the **Findable** dimension specifically reduce discovery friction, measured as time-to-first-run?

**Null hypothesis (H0):** Findable sub-criteria score has no significant association with time-to-first-run after propensity matching (log-rank p ≥ 0.05).

**Research gap:** While FAIR principles are widely advocated, quantitative evidence that specific FAIR dimensions (especially Findable) reduce time-to-adoption in ML repositories is sparse. Survival analysis on matched cohorts provides the most rigorous causal evidence.

---

## 3. Functional Requirements

### FR-1: Data Ingestion Pipeline

**Source:** OpenML Python API (`openml` library)
**Base population:** H-E1 cohort — 5,000 post-2018 OpenML tabular datasets with FAIR proxy scores
**Extension:** Fetch run timestamps per dataset via `openml.runs.list_runs(dataset_id=...)`

**Required fields per dataset:**
- `dataset_id`: OpenML dataset identifier
- `upload_date`: Dataset upload timestamp (ISO8601)
- `first_run_timestamp`: Earliest recorded run timestamp (from runs API)
- `run_count`: Total number of recorded runs
- `fair_proxy_score`: FAIR composite score (from H-E1 outputs)
- `findable_score`: Computed Findable sub-criteria composite (see FR-3)
- `creation_year_quartile`: Year quartile for propensity matching covariate
- `task_type`: Task type category (~8 levels) for propensity matching
- `size_decile`: Dataset size decile (1-10) for propensity matching

**Filter:** Retain only datasets with ≥ 10 recorded runs (expected: ~500–1,500 datasets)

**Derived fields:**
- `time_to_first_run`: `(first_run_timestamp − upload_date).days`; right-censor at `observation_window_days` for datasets with 0 runs
- `event`: 1 if first run observed; 0 if right-censored

### FR-2: H-E1 Cohort Integration

**Requirement:** Reuse FAIR proxy scores from H-E1 (do NOT re-score)
- Load H-E1 scored cohort from `h-e1/` results or recompute if cache unavailable
- Merge on `dataset_id`
- Validate merge: all matched datasets must have FAIR scores

**Reuse strategy:** H-E1 code pipeline handles scoring; H-M1 extends with run data only.

### FR-3: Findable Sub-Score Extraction

**Findable composite** (F-UJI specification):
```
findable_score = 0.25 × F1_PID + 0.50 × F2_metadata + 0.25 × F3_search_indexed
```

**Proxy mapping** (F-UJI API unavailable — same proxy as H-E1):
- `F1_PID`: 1.0 if dataset has persistent DOI/URL; 0.0 otherwise (approximated from metadata)
- `F2_metadata`: Proportion of non-null metadata fields (title, description, tags, creator, license)
- `F3_search_indexed`: 1.0 if dataset is tagged/categorized; 0.0 otherwise

**Binary treatment variable:**
```
high_findable = (findable_score > median(findable_score)).astype(int)
```

### FR-4: Propensity Score Matching

**Matching variables (covariates):**
- `creation_year_quartile` (ordinal: Q1–Q4 of 2018–2025)
- `task_type` (categorical: classification, regression, clustering, etc.)
- `size_decile` (ordinal: 1–10)

**Propensity model:** Logistic regression (`sklearn.linear_model.LogisticRegression`, max_iter=500)

**Matching protocol:**
1. Fit logistic model on covariates → compute `propensity_score`
2. 1:1 nearest-neighbor matching with `caliper = 0.2 × SD(logit(propensity_score))`
3. Validate balance: SMD < 0.1 for all covariates post-matching
4. If SMD > 0.1: try entropy balancing or relax caliper to 0.3×SD

**Minimum matched pairs:** ≥ 100 pairs required (gate pre-condition)

### FR-5: Baseline Model — Unadjusted Kaplan-Meier

**Purpose:** Show raw (confounded) association; establishes magnitude of confounding
**Implementation:**
```python
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# No propensity matching — all datasets with ≥10 runs
kmf_high_unadj = KaplanMeierFitter()
kmf_low_unadj  = KaplanMeierFitter()
kmf_high_unadj.fit(high_raw['time_to_first_run'], high_raw['event'])
kmf_low_unadj.fit(low_raw['time_to_first_run'],   low_raw['event'])
results_unadj = logrank_test(
    high_raw['time_to_first_run'], low_raw['time_to_first_run'],
    event_observed_A=high_raw['event'], event_observed_B=low_raw['event']
)
```
**Expected:** Overestimated HR due to confounding from dataset age and popularity

### FR-6: Proposed Model — Propensity-Matched KM + Cox PH

**Primary analysis:**
```python
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test

# After propensity matching (FR-4)
high_matched = matched_df[matched_df['high_findable'] == 1]
low_matched  = matched_df[matched_df['high_findable'] == 0]

# KM curves + log-rank test (PRIMARY GATE)
results_matched = logrank_test(
    high_matched['time_to_first_run'], low_matched['time_to_first_run'],
    event_observed_A=high_matched['event'], event_observed_B=low_matched['event']
)
log_rank_p = results_matched.p_value

# Cox PH regression (SECONDARY GATE)
cph = CoxPHFitter()
cph.fit(matched_df[['time_to_first_run', 'event', 'findable_score']],
        duration_col='time_to_first_run', event_col='event')
cox_hr = float(np.exp(cph.params_['findable_score']))
```

### FR-7: Ablation Variants

**Ablation A — F-UJI aggregate threshold split:**
- Replace median Findable split with `fair_proxy_score >= 0.5` binary split
- Re-run full matching + KM + Cox pipeline
- Compare log-rank p and HR to primary analysis
- Purpose: test whether aggregate FAIR vs. Findable-specific produces different results

**Ablation B — Alternative IV: Accessible sub-criteria:**
- Compute `accessible_score = 0.5 × A1_open_license + 0.5 × A2_standard_format`
- Re-run full pipeline substituting `accessible_score` for `findable_score`
- Purpose: failure-response exploration; validates Findable-specificity of mechanism

**Ablation C — Relaxed caliper matching (5:1 ratio):**
- If primary matched pairs < 100: relax to caliper=0.3×SD + ratio=5:1 matching
- Report matched N and SMD results
- Purpose: sample size robustness check

### FR-8: Sensitivity Analysis

**SA-1 (F-UJI ≥ 0.5 threshold):** Already covered in Ablation A above
**SA-2 (Schoenfeld residuals PH check):**
```python
cph.check_assumptions(matched_df, p_value_threshold=0.05)
# If PH violated: use stratified Cox or time-varying model
```
**SA-3 (Observation window sensitivity):**
- Re-run with observation_window = [180, 365, 730] days
- Report stability of HR and p-values across windows

### FR-9: Evaluation & Gate Metrics

**Primary gate (MUST_WORK):**
- `log_rank_p < 0.05` (two-sided)
- `median_high_findable < median_low_findable` (directionality check)

**Secondary gate:**
- `cox_hr > 1.2` for Findable sub-criteria

**Balance checks (pre-conditions):**
- SMD < 0.1 for all covariates post-matching
- n_matched_pairs ≥ 100

**Metrics to report:**
```python
results = {
    'log_rank_p': float,           # Primary gate
    'cox_hr': float,               # Secondary gate
    'median_ttfr_high': float,     # Days, high-Findable group
    'median_ttfr_low': float,      # Days, low-Findable group
    'n_matched_pairs': int,        # Pairs after matching
    'smd_max': float,              # Max SMD across covariates post-matching
    'n_cohort_filtered': int,      # Datasets with ≥10 runs
    'baseline_log_rank_p': float,  # Unadjusted comparison
    'baseline_cox_hr': float,      # Unadjusted HR
}
```

### FR-10: Visualization

**Required figures (mandatory):**
1. **Gate Metrics Bar Chart:** log-rank p vs. threshold (0.05) and Cox HR vs. threshold (1.2)
2. **Kaplan-Meier Survival Curves:** High vs. Low Findable matched groups; 95% CI bands; annotated median TTFRs and log-rank p
3. **Propensity Score Distribution:** Histograms before/after matching (balance visualization)
4. **Love Plot (SMD):** SMD before vs. after matching for each covariate
5. **Cox PH Forest Plot:** HR point estimate + 95% CI for Findable sub-criteria
6. **Sensitivity Analysis Comparison:** Log-rank p and HR across primary + ablation analyses

**Output path:** `h-m1/figures/`
**Format:** PNG (300 DPI), SVG optional

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | OpenML post-2018 tabular cohort (run timestamps extension) |
| Type | programmatic-api |
| Source | OpenML Python API (`openml` package) |
| Download method | `pip install openml` + programmatic API calls |
| Base population | H-E1 scored cohort (5,000 datasets) |
| Post-filter expected | ~500–1,500 datasets (≥10 run filter) |
| After matching | ~N matched pairs (N = min(high, low) after filter) |

**Loading code:**
```python
import openml
datasets = openml.datasets.list_datasets(output_format='dataframe')
# Filter: upload_date >= 2018-01-01, data_format='ARFF' (tabular)
# Merge with H-E1 FAIR scores
# Fetch runs: openml.runs.list_runs(dataset_id=dataset_id)
```

**No manual download required** — fully programmatic via `openml` package.

### 4.2 Static Benchmark Datasets (Baseline Reference)

No separate static datasets; OpenML serves as both the data source and benchmark population.

### 4.3 Preprocessing Pipeline

1. Load H-E1 FAIR proxy scores (from `h-e1/` cache or recompute)
2. Fetch run lists for each dataset_id via OpenML runs API
3. Compute `time_to_first_run` in days (upload_date → earliest run timestamp)
4. Apply ≥10 run filter
5. Extract Findable sub-score from proxy scoring (FR-3)
6. Encode categorical covariates (task_type → one-hot or label encoding)
7. Compute `creation_year_quartile` and `size_decile`
8. Apply right-censoring (event=0) for datasets with no runs

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | `numpy.random.seed(42)` set before propensity matching |
| Performance | Full analysis completes in < 30 min on single CPU |
| Sample size | Minimum 100 matched pairs; warn if < 50 |
| Code quality | Minimum 3 unit tests per module; docstrings on public functions |
| Logging | Structured logging with key checkpoints and metrics |
| Output | All results saved to `h-m1/results/` as JSON + CSV |

---

## 6. Success Criteria

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| Log-rank p-value | p < 0.05 | PRIMARY (MUST_WORK) |
| Directionality | median_high < median_low | PRIMARY |
| Cox Hazard Ratio | HR > 1.2 | SECONDARY |
| Covariate balance | SMD < 0.1 | Pre-condition |
| Matched pairs | n ≥ 100 | Pre-condition |

**PASS:** log_rank_p < 0.05 AND median_high < median_low
**SECONDARY PASS:** cox_hr > 1.2
**FAIL:** Gate not met → MUST_WORK triggers; H-M2/H-M3 blocked

---

## 7. Dependencies

### 7.1 Python Packages

```
openml>=0.14.0          # OpenML API access (dataset listing + run timestamps)
lifelines>=0.27.0       # Kaplan-Meier, CoxPHFitter, logrank_test
scikit-learn>=1.0.0     # LogisticRegression for propensity model; NearestNeighbors
pandas>=1.3.0           # DataFrame operations
numpy>=1.21.0           # Array operations, random seed
scipy>=1.7.0            # Statistical utilities
matplotlib>=3.4.0       # Figure generation
seaborn>=0.11.0         # Love plots, distribution plots
pyyaml>=5.4.0           # Results serialization
```

**Optional (fallback):**
```
causalml>=0.13.0        # NearestNeighborMatcher alternative to sklearn
scikit-survival>=0.17   # Fallback Cox regression if lifelines convergence fails
```

### 7.2 External Repositories (Reference Only)

| Repository | Purpose | URL |
|------------|---------|-----|
| lifelines | KM + Cox PH primary library | https://github.com/CamDavidsonPilon/lifelines |
| uber/causalml | Propensity matching alternative | https://github.com/uber/causalml |
| scikit-survival | Fallback Cox regression | https://github.com/sebp/scikit-survival |

### 7.3 Internal Dependencies

| Dependency | Source | Required |
|------------|--------|----------|
| H-E1 FAIR proxy scores | `h-e1/` results or recompute | REQUIRED |
| H-E1 dataset cohort | 5,000 post-2018 OpenML tabular datasets | REQUIRED |
| OpenML API access | Internet connection | REQUIRED |

---

## 8. Out of Scope

- Neural network or ML model training (statistical analysis only)
- HuggingFace datasets (covered by H-M4)
- Accessible, Interoperable, Reusable sub-criteria (covered by H-M2, H-M3)
- Paper writing (Phase 6)
- Phase 5 baseline repository comparison (skip_baseline_comparison=true)

---

## 9. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| OpenML API rate limits | Medium | Cache API responses; retry with backoff |
| < 100 matched pairs after filter | High | Relax matching caliper; try 5:1 ratio (Ablation C) |
| PH assumption violation | Medium | Schoenfeld test; use stratified Cox or time-varying |
| F-UJI API unavailable | Low | Already mitigated by proxy scoring (H-E1 pattern) |
| Sparse run timestamps for early datasets | Medium | Right-censoring handles this correctly via KM |

---

*PRD generated by Phase 3 Step 2 (no-mcp mode — inline generation from 02c_experiment_brief.md)*
*All specifications derived from: h-m1/02c_experiment_brief.md, h-m1/02b_context.md, H-E1 validation results*
