# Experiment Design: h-m2

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under post-2018 OpenML tabular datasets matched on creation year × task type × size, if F-UJI Accessible sub-criteria score is higher, then total run count within the first 12 months post-upload will be significantly higher (Mann-Whitney U p < 0.05; Accessible β > 0.10 standardized), because open licenses and standard formats lower the barrier to initial experimental use.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 (VALIDATED, MUST_WORK ✅), h-m1 (VALIDATED, MUST_WORK ✅)
**Gate Status:** SHOULD_WORK — failure does not stop pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1, h-m1

### Gate Condition
SHOULD_WORK: Mann-Whitney U p < 0.05 AND high-Accessible mean 12-month run count > low-Accessible; secondary: Accessible standardized β > 0.10. Failure → document as non-significant dimension, pipeline continues.

---

## Continuation Context

This is a **continuation experiment** — h-m2 reuses proven infrastructure from h-m1.

### Previous Hypothesis Results (h-m1)

| Metric | Value | Status |
|--------|-------|--------|
| Log-rank p (matched KM) | 0.0053 | PASS |
| Cox HR | 3.159 [1.032, 9.672] | PASS |
| SMD max (after matching) | 0.098 | Balanced |
| Matched pairs | 35 |  |

**Reusable proven components from h-m1:**
- `src/ingest.py` — data ingestion pipeline (validated)
- `src/matching.py` — propensity score matching (validated)
- `src/survival_prep.py` — data preparation (validated)
- `src/serialize.py` — results serialization (validated)
- `src/visualize.py` — figure generation (validated)

**Optimal hyperparameters inherited from h-m1:**
```yaml
caliper_factor: 0.8
min_matched_pairs: 30  # smoke test; production >= 500
seed: 42
matching_covariates: [creation_year_quartile, task_type, size_decile]
log_rank_alpha: 0.05
```

**Key lesson from h-m1:** Propensity matching essential — unadjusted p=0.583 vs matched p=0.005. Same pattern expected for Accessible analysis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Mode:** no-mcp (Archon unavailable) — domain knowledge substitution applied per established pipeline pattern (h-e1, h-m1).

**Query 1: Mann-Whitney U test for count outcomes in observational studies**
- Standard non-parametric test for comparing two independent groups on ordinal/count data
- Preferred over t-test when count distributions are right-skewed (as expected for run counts)
- Key insight: Use on matched pairs after propensity score matching for valid causal inference
- Source: scipy.stats.mannwhitneyu documentation; Rosenbaum & Rubin (1983) matching framework

**Query 2: F-UJI Accessible sub-criteria implementation**
- A1_access_protocol: Dataset accessible via standard protocol (HTTP, FTP, API)
- A1.1_standardized_protocol: Uses standardized protocol (not proprietary)
- A1.2_authentication: Access does not require authentication
- OpenML datasets: Most score high on A1/A1.1 (API accessible), variance mainly in A1.2 (some require login)
- Key insight: Accessible score on OpenML may have less variance than Findable → expect weaker effect than h-m1

**Query 3: OLS regression with standardized coefficients for FAIR sub-criteria**
- Log-transform DV (run_count + 1) to normalize right-skewed count distribution
- Standardize all predictors (z-score) before regression to obtain comparable β coefficients
- Include Findable β from h-m1 as control variable to test independent contribution of Accessible
- Source: Cohen et al. (2003) Applied Multiple Regression; statsmodels OLS

### Archon Code Examples

**MCP Mode:** no-mcp — code patterns derived from domain knowledge and h-m1 proven codebase.

**Pattern 1: Mann-Whitney U on matched pairs (scipy)**
```python
from scipy import stats
stat, p_value = stats.mannwhitneyu(
    high_accessible_run_count,
    low_accessible_run_count,
    alternative='greater'  # directional: high > low
)
```

**Pattern 2: OLS with standardized predictors (statsmodels)**
```python
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_std = scaler.fit_transform(X[fair_sub_criteria_cols])
model = sm.OLS(np.log1p(y), sm.add_constant(X_std)).fit()
accessible_beta = model.params['Accessible']
```

### Exa GitHub Implementations

**MCP Mode:** no-mcp (Exa unavailable) — implementation patterns from h-m1 proven codebase and domain knowledge.

**Repository 1: h-m1 proven codebase** (internal)
- **URL:** `docs/youra_research/20260504_mldpr/h-m1/code/`
- **Relevance:** Same OpenML pipeline; replace KM analysis with Mann-Whitney U + OLS
- **Key files for reuse:**
  - `src/ingest.py` — OpenML API data ingestion (validated)
  - `src/matching.py` — propensity score 1:1 matching (validated)
  - `src/survival_prep.py` → adapt to `accessible_prep.py` for 12-month count window
- **New module needed:** `src/mwu_analysis.py` — Mann-Whitney U + OLS regression
- **Training Config (inherited):**
  - Seed: 42
  - Caliper: 0.8 (smoke test)
  - Min pairs: 30 (smoke test)

**Repository 2: OpenML Python API** (external reference)
- **URL:** https://github.com/openml/openml-python
- **Relevance:** Programmatic access to run timestamps for 12-month window computation
- **Key API:** `openml.runs.list_runs(dataset=dataset_id)` returns run timestamps
- **Loading code:** `import openml; runs = openml.runs.list_runs(dataset=dataset_id, output_format='dataframe')`

**Serena Analysis Needed:** false — code patterns are clear from h-m1 codebase

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis study, not a paper reproduction experiment.**

**Recommended Implementation Path:**
- Primary: Reuse h-m1 proven codebase; add `src/accessible_prep.py` + `src/mwu_analysis.py`
- Fallback: Implement from scratch using scipy + statsmodels + sklearn (well-documented APIs)
- Justification: h-m1 infrastructure proven stable (29/29 tests passed, clean dry-run); controlled experiment design requires same matching pipeline

### Code Analysis (Serena MCP)

*Skipped* — Code from h-m1 proven codebase and domain knowledge was sufficiently clear. No complex unfamiliar architecture patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** OpenML post-2018 tabular cohort (12-month run window)
**Type:** programmatic-api
**Source:** OpenML Python API (openml.org)
**Hypothesis Fit:** OpenML run timestamps enable exact 12-month window [upload_date, upload_date + 365 days] computation; same cohort as h-e1/h-m1 enables controlled comparison with matched propensity structure

**Statistics:**
- Expected cohort size: ~5,000 datasets (post-2018 tabular, same as h-e1)
- After filtering (≥1 run in first 12 months): ~2,000–3,000 datasets expected
- Matched pairs (smoke test): ~35 pairs (same as h-m1 cohort structure)
- Matched pairs (production): ≥500 pairs required

**Preprocessing:**
1. Filter: upload_date >= 2018-01-01 AND task_type = tabular
2. Compute 12-month run count: filter run timestamps to [upload_date, upload_date + 365 days]
3. Extract Accessible sub-score from F-UJI results (from h-e1 scoring pass)
4. Log-transform DV: log1p(run_count_12m) for regression
5. Standardize all F-UJI sub-criteria for OLS β comparison

**No augmentation** — observational study; data used as-is

**Evaluation split:** Full cohort used for analysis (no train/val/test split — observational study)
- Smoke test: synthetic dry-run cohort n=200 (same as h-m1)
- Production: full OpenML post-2018 cohort (~5,000 datasets)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (OpenML Python library)
- Identifier: openml post-2018 tabular cohort
- Code: `import openml; datasets = openml.datasets.list_datasets(output_format='dataframe')`

### Models

#### Baseline Model

**Architecture:** Unadjusted Mann-Whitney U (no propensity matching)
**Purpose:** Establish pre-matching baseline; expected non-significant (same pattern as h-m1 unadjusted p=0.583)
**Configuration:**
- scipy.stats.mannwhitneyu(alternative='greater')
- No covariate control
- Direct split at median Accessible sub-score

**Rationale:** Demonstrates why propensity matching is essential (same as h-m1 finding)

**Loading Information** (for Phase 4):
- Method: scipy (pip install scipy)
- Identifier: scipy.stats.mannwhitneyu
- Code: `from scipy import stats; stat, p = stats.mannwhitneyu(group_high, group_low, alternative='greater')`

#### Proposed Model

**Architecture:** Propensity-matched Mann-Whitney U + OLS multi-variate regression

**Core Mechanism Implementation:**

```python
# Core Mechanism: Accessible Sub-Criteria → 12-Month Run Count
# Based on: h-m1 proven matching pipeline + scipy/statsmodels
# Statistical analysis pipeline (not neural network)

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

def compute_12m_run_counts(datasets_df, runs_df):
    """
    Input: datasets_df with upload_date, runs_df with run timestamps
    Output: datasets_df with run_count_12m column
    """
    results = []
    for _, row in datasets_df.iterrows():
        mask = (
            (runs_df['dataset_id'] == row['dataset_id']) &
            (runs_df['run_date'] >= row['upload_date']) &
            (runs_df['run_date'] < row['upload_date'] + pd.Timedelta(days=365))
        )
        results.append(mask.sum())
    datasets_df['run_count_12m'] = results
    return datasets_df

def run_mannwhitney_matched(matched_df, dv_col='run_count_12m'):
    """
    Input: matched_df with high/low Accessible groups (matched pairs)
    Output: Mann-Whitney U statistic and p-value
    """
    high = matched_df[matched_df['accessible_group'] == 'high'][dv_col]
    low = matched_df[matched_df['accessible_group'] == 'low'][dv_col]
    stat, p_val = stats.mannwhitneyu(high, low, alternative='greater')
    return {'mwu_stat': stat, 'p_value': p_val, 'n_high': len(high), 'n_low': len(low)}

def run_ols_standardized(df, fair_cols, dv_col='run_count_12m'):
    """
    Input: df with F-UJI sub-criteria + DV; fair_cols = list of sub-criteria columns
    Output: dict of standardized beta coefficients per sub-criterion
    """
    scaler = StandardScaler()
    X_std = scaler.fit_transform(df[fair_cols].fillna(0))
    y = np.log1p(df[dv_col].values)
    model = sm.OLS(y, sm.add_constant(X_std)).fit()
    return dict(zip(['const'] + fair_cols, model.params)), model.pvalues
```

### Training Protocol

**From Previous Hypothesis (h-m1) — Reusing for controlled experiment:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Seed | 42 | h-m1 optimal |
| Caliper factor | 0.8 (smoke test) / 0.2 (production) | h-m1 lesson learned |
| Min matched pairs | 30 (smoke test) / 500 (production) | h-m1 lesson learned |
| Observation window | 365 days (12-month) | h-m2 hypothesis definition |
| IV split | Median Accessible sub-score | Protocol step 2 |
| DV transform | log1p(run_count_12m) | Normalization for OLS |
| Standardization | z-score all F-UJI sub-criteria | For comparable β |
| Matching covariates | creation_year_quartile, task_type, size_decile | Phase 2A design |
| Mann-Whitney alternative | 'greater' (directional) | Hypothesis direction |
| OLS significance | α = 0.05 | Standard |

**Rationale:** Reusing h-m1 optimal hyperparameters enables controlled experiment — only the IV (Accessible vs Findable) and DV (12-month count vs TTFR) change. This isolates the mechanism effect.

**No GPU required** — statistical analysis only (scipy, statsmodels, sklearn)

### Evaluation

**Primary Metrics:**
- Mann-Whitney U p-value: < 0.05 (SHOULD_WORK gate primary)
- Direction check: mean(high_accessible_12m_count) > mean(low_accessible_12m_count)
- Accessible standardized β: > 0.10 in multi-variate OLS

**Success Criteria (SHOULD_WORK gate):**
- PRIMARY: Mann-Whitney U p < 0.05 AND direction confirmed
- SECONDARY: Accessible β > 0.10 (standardized, multi-variate)
- PoC Pass: code runs without error AND proposed metric satisfies primary gate

**Expected Performance (from domain knowledge + h-m1 pattern):**
- Unadjusted p: expected non-significant (p > 0.1) — confounding by age/size
- Matched p: expected < 0.05 if Accessible truly drives early adoption
- Accessible β: expected 0.08–0.15 (weaker than Findable HR=3.16 — Accessible has less variance on OpenML)
- Note: SHOULD_WORK gate — partial result acceptable; pipeline continues regardless

**Ablation variants:**
- A: F-UJI aggregate threshold (≥0.5) vs median Accessible split — tests whether sub-criteria specificity matters
- B: 6-month window vs 12-month window — failure fallback per protocol
- C: Relaxed caliper (0.8) vs strict caliper (0.2) — matching sensitivity

**Metrics Loading Information:**
- Task Type: observational statistical analysis (count outcome)
- Library: scipy.stats + statsmodels
- Code: `from scipy import stats; stats.mannwhitneyu(high, low, alternative='greater')`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Mann-Whitney U p-value vs threshold (0.05) bar chart; Accessible β vs threshold (0.10) comparison

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (MECHANISM, count outcome, propensity-matched observational study):

1. **fig1_gate_metrics.png** — Primary gate metric summary (p-value, β, direction)
2. **fig2_boxplot_12m_counts.png** — Box plot of 12-month run counts: high vs low Accessible (matched)
3. **fig3_ps_distribution.png** — Propensity score distribution before/after matching
4. **fig4_love_plot.png** — Love plot (SMD before/after matching for all covariates)
5. **fig5_ols_coefficients.png** — Standardized β forest plot for all F-UJI sub-criteria
6. **fig6_window_sensitivity.png** — p-value comparison across 6-month vs 12-month windows

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/20260504_mldpr/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism:** F-UJI Accessible sub-criteria → 12-month run count (observational statistical analysis)

**Pre-conditions:**
- mechanism_exists: true — OpenML provides run timestamps; Accessible sub-scores computed by h-e1
- mechanism_isolatable: true — propensity matching on creation_year × task_type × size isolates Accessible effect
- baseline_measurable: true — unadjusted Mann-Whitney U establishes pre-matching baseline

**Architecture Compatibility:**
- architecture_compatibility: CONFIRMED — same statistical pipeline as h-m1; replacing survival analysis module with count analysis module; no structural conflicts
- Reused modules: ingest.py, matching.py, survival_prep.py → adapted to accessible_prep.py
- New module: mwu_analysis.py (Mann-Whitney U + OLS regression)

**Activation Indicators:**
- mechanism_log_message: "Mann-Whitney U: high_accessible_mean={:.1f}, low_accessible_mean={:.1f}, p={:.4f}"
- tensor_shape_change: N/A (statistical analysis, not neural network) — instead: matched_pairs_count >= 30 confirms matching succeeded
- metric_delta_expected: high_accessible_mean - low_accessible_mean > 0 (positive direction)

**Mechanism Verification Code:**
```python
# Verify mechanism activates correctly
assert results['n_matched_pairs'] >= 30, "Insufficient matched pairs"
assert results['smd_max_after'] < 0.1, "Matching balance failed"
assert results['high_mean_12m'] >= 0, "Invalid run count"
print(f"[MECHANISM CHECK] MWU p={results['p_value']:.4f}, "
      f"direction={'PASS' if results['high_mean_12m'] > results['low_mean_12m'] else 'FAIL'}, "
      f"Accessible_beta={results['accessible_beta']:.3f}")
```

**hypothesis_support_threshold:** p < 0.05 (primary); β > 0.10 (secondary)
**hypothesis_support_metric:** Mann-Whitney U p-value (primary); OLS standardized β for Accessible (secondary)

**Failure Detection:**
- IF matched_pairs < 30: STOP — insufficient data for analysis
- IF smd_max_after > 0.1: WARN — matching balance poor; check caliper settings
- IF p >= 0.05: DOCUMENT — SHOULD_WORK failure; test 6-month window fallback
- IF accessible_beta <= 0.05: DOCUMENT — Accessible non-significant dimension

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: Mann-Whitney U for count outcomes in matched observational studies**
- Type: Domain knowledge (no-mcp substitution)
- Relevance: Non-parametric test robust to right-skewed count distributions
- Key insights: (1) Use directional alternative='greater'; (2) Apply after matching; (3) Report effect size (rank-biserial r)
- Used For: Primary statistical test design

**Source A.2: F-UJI Accessible sub-criteria definition**
- Type: Domain knowledge (FAIR principles literature)
- Relevance: A1_access_protocol, A1.1_standardized_protocol, A1.2_authentication directly map to "open license and standard format" mechanism
- Key insights: A1.2 (no authentication) is primary variance driver on OpenML — most datasets open via API but some require institutional login
- Used For: IV specification and expected effect direction

**Source A.3: OLS with standardized coefficients for multi-dimensional comparison**
- Type: Domain knowledge (Cohen et al. 2003; statsmodels docs)
- Relevance: Standardized β enables direct comparison of Accessible vs Findable contribution
- Key insights: Log-transform DV before standardizing predictors; report 95% CI for β
- Used For: Secondary analysis design; β > 0.10 threshold

### B. GitHub Implementations (Exa)

**Repository B.1: h-m1 proven codebase** (internal, no-mcp substitution)
- URL: `docs/youra_research/20260504_mldpr/h-m1/code/`
- Query used: Internal reference (Exa unavailable)
- Relevance: Identical OpenML pipeline infrastructure
- Key code reused: ingest.py, matching.py, survival_prep.py, serialize.py, visualize.py
- Configuration extracted: caliper=0.8, seed=42, min_pairs=30
- Their results: Matched KM p=0.0053, Cox HR=3.159, n=35 pairs
- Used For: Infrastructure reuse; controlled experiment baseline

**Repository B.2: OpenML Python API** (external reference)
- URL: https://github.com/openml/openml-python
- Relevance: Run timestamp retrieval for 12-month window computation
- Key API: `openml.runs.list_runs(dataset=dataset_id)` → run timestamps
- Used For: Dataset loading specification

### C. Code Analysis (Serena)

*Not performed* — Code from h-m1 proven codebase and domain knowledge was sufficiently clear. Statistical analysis patterns (scipy.stats, statsmodels) are well-documented. No complex unfamiliar architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1 (2026-05-04T05:31:00Z)
- **File:** `docs/youra_research/20260504_mldpr/h-m1/04_validation.md`
- **Reused Components:**
  - Dataset: OpenML post-2018 tabular cohort — proven stable
  - Propensity matching: caliper=0.8, seed=42, matching covariates — optimal values
  - Code structure: ingest → prep → match → analyze → serialize → visualize pipeline
- **Why Reused:** Enables controlled experiment — only IV (Accessible vs Findable) and DV (12-month count vs TTFR) change; confound control identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset selection | h-m1 proven + hypothesis definition | B.1 + Phase 2B Section 2.2 |
| 12-month window computation | Hypothesis definition | Phase 2B H-M2 Protocol step 1 |
| Propensity matching hyperparameters | h-m1 optimal | D.1 (04_validation.md) |
| Mann-Whitney U design | Domain knowledge | A.1 |
| OLS standardized β design | Domain knowledge | A.3 |
| Accessible sub-criteria IV | FAIR literature | A.2 |
| Pseudo-code structure | h-m1 codebase pattern | B.1 |
| Evaluation thresholds | Phase 2B success criteria | Phase 2B H-M2 success criteria |
| Visualization plan | h-m1 figures + hypothesis-specific additions | B.1 + autonomous judgment |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T06:34:00Z

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| h-m2 set to IN_PROGRESS | 2026-05-04T06:33:59Z | External loop starting Phase 2C → 3 → 4 for h-m2 |
| Phase 2C experiment design started | 2026-05-04 | Step 1 initialized; context JIT-generated |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Domain knowledge substitution (no-mcp mode — Archon/Exa/Serena unavailable)*
*All specifications grounded in h-m1 proven codebase + statistical analysis domain knowledge*
*Next Phase: Phase 3 - Implementation Planning*
