# Product Requirements Document: h-m2
## Accessible FAIR Dimension → 12-Month Run Count (OpenML)

---

**Hypothesis ID:** h-m2
**Type:** MECHANISM (INCREMENTAL — extends h-m1)
**Gate:** SHOULD_WORK
**Date:** 2026-05-04
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

This experiment tests whether F-UJI Accessible sub-criteria scores causally drive early experimental engagement (12-month run count) for post-2018 OpenML tabular datasets. Building on h-m1's proven propensity-matching infrastructure, h-m2 replaces the survival analysis (time-to-first-run) with a count outcome analysis (total runs in 12 months), using Mann-Whitney U testing and OLS regression with standardized coefficients.

**Core Question:** Does higher Accessible sub-criteria score (open license, standard format, documented access) translate into more experimental runs within 12 months of upload?

**Expected Outcome:** Matched MWU p < 0.05 with directional confirmation; Accessible β > 0.10 in multi-variate OLS. SHOULD_WORK gate — partial results acceptable; pipeline continues regardless.

---

## 2. Problem Statement

### 2.1 Research Gap

While h-m1 confirmed that Findable FAIR sub-criteria reduce time-to-first-run (log-rank p=0.0053, Cox HR=3.159), the independent contribution of Accessible sub-criteria to initial engagement volume has not been verified. Accessible sub-criteria (open licenses, standard formats, no authentication barriers) theoretically lower the barrier to initial experimental use — but this must be empirically validated with count outcome analysis.

### 2.2 Causal Chain

```
H-E1: FAIR variance exists (CV=0.1597, bimodal confirmed)
  ↓
H-M1: Findable → faster time-to-first-run (p=0.0053, HR=3.159)
  ↓
H-M2: Accessible → higher 12-month run count volume [THIS EXPERIMENT]
  ↓
H-M3: Reusable → sustained long-term engagement (months 13-36)
```

### 2.3 Scope

- **In scope:** OpenML post-2018 tabular datasets; 12-month run count window; Accessible sub-criteria as IV; propensity matching on creation_year × task_type × size
- **Out of scope:** HuggingFace (h-m4); survival analysis (h-m1); long-term engagement (h-m3); GPU training (statistical analysis only)

---

## 3. Functional Requirements

### FR-1: Data Ingestion (Reuse h-m1 ingest.py)

**Requirement:** Load OpenML post-2018 tabular cohort with run timestamps
- Load datasets via `openml.datasets.list_datasets(output_format='dataframe')`
- Filter: `upload_date >= 2018-01-01 AND task_type = tabular`
- Load run timestamps via `openml.runs.list_runs(dataset=dataset_id)`
- Expected cohort: ~5,000 datasets
- **Reuse:** h-m1 `src/ingest.py` (validated, 29/29 tests passed)

### FR-2: 12-Month Run Count Computation (NEW MODULE)

**Requirement:** Compute DV = total run count within [upload_date, upload_date + 365 days]
- For each dataset, filter run timestamps to 12-month window
- Output: `run_count_12m` column added to datasets DataFrame
- After filtering (≥1 run): expected ~2,000–3,000 datasets
- Smoke test: synthetic cohort n=200 (same as h-m1)
- Production: full cohort (~5,000 datasets, ≥500 matched pairs required)
- **New file:** `src/accessible_prep.py`

### FR-3: Accessible Sub-Criteria Extraction

**Requirement:** Extract Accessible sub-score from F-UJI scoring results (h-e1)
- Sub-criteria: A1_access_protocol, A1.1_standardized_protocol, A1.2_authentication (composite, 0–1)
- Source: F-UJI scoring output from h-e1 (5,000 datasets scored)
- Split at median Accessible sub-score → high/low groups
- Expected variance: lower than Findable (A1.2 is primary driver — most OpenML datasets open via API)

### FR-4: Propensity Score Matching (Reuse h-m1 matching.py)

**Requirement:** 1:1 propensity matching on creation_year_quartile × task_type × size_decile
- Match high/low Accessible groups using proven h-m1 matching pipeline
- Caliper: 0.8 (smoke test); 0.2 (production)
- Min matched pairs: 30 (smoke test); 500 (production)
- Validate balance: SMD < 0.1 for all covariates
- **Reuse:** h-m1 `src/matching.py` (validated)

### FR-5: Baseline Analysis — Unadjusted Mann-Whitney U

**Requirement:** Establish pre-matching baseline
- Apply MWU directly on unmatched high/low Accessible groups
- Expected: non-significant (p > 0.1), same as h-m1 unadjusted p=0.583
- Purpose: Demonstrates why propensity matching is essential
- Library: `scipy.stats.mannwhitneyu(alternative='greater')`

### FR-6: Proposed Analysis — Matched Mann-Whitney U

**Requirement:** Primary statistical test on matched groups
- Apply MWU on propensity-matched high/low Accessible groups on `run_count_12m`
- Directional test: `alternative='greater'` (high > low)
- Report: MWU statistic, p-value, effect size (rank-biserial r)
- Gate: p < 0.05 AND high_mean > low_mean (PRIMARY GATE)
- **New module:** `src/mwu_analysis.py`

### FR-7: Proposed Analysis — OLS Regression with Standardized Coefficients

**Requirement:** Secondary multi-variate analysis
- DV: log1p(run_count_12m) — normalized for right-skewed counts
- Predictors: All F-UJI sub-criteria (Findable, Accessible, Interoperable, Reusable), standardized (z-score)
- Extract Accessible standardized β; compare to Findable β from h-m1
- Gate: Accessible β > 0.10 (SECONDARY GATE)
- Library: `statsmodels.OLS` + `sklearn.StandardScaler`
- **Part of:** `src/mwu_analysis.py`

### FR-8: Ablation A — Aggregate Threshold vs Sub-Criteria Split

**Requirement:** Test whether Accessible sub-criteria specificity matters
- Replace: median Accessible split → F-UJI aggregate threshold (≥0.5)
- Apply same MWU + matching pipeline
- Expected: weaker result than sub-criteria split (confirmed pattern from h-m1 ablation A)

### FR-9: Ablation B — 6-Month Window Sensitivity

**Requirement:** Failure fallback — test shorter adoption window
- Replace: 12-month run window → 6-month run window
- Apply same MWU + matching pipeline
- Purpose: If 12-month analysis fails, check if shorter window shows effect

### FR-10: Ablation C — Matching Sensitivity (Caliper)

**Requirement:** Matching parameter sensitivity check
- Compare: relaxed caliper (0.8) vs strict caliper (0.2) results
- Purpose: Validate robustness of matching configuration

### FR-11: Mechanism Verification

**Requirement:** Verify mechanism activates correctly
```python
assert results['n_matched_pairs'] >= 30
assert results['smd_max_after'] < 0.1
assert results['high_mean_12m'] >= 0
print(f"[MECHANISM CHECK] MWU p={results['p_value']:.4f}, "
      f"direction={'PASS' if results['high_mean_12m'] > results['low_mean_12m'] else 'FAIL'}, "
      f"Accessible_beta={results['accessible_beta']:.3f}")
```

### FR-12: Visualization (6 Figures)

**Requirement:** Generate 6 figures saved to `figures/`
1. `fig1_gate_metrics.png` — Primary gate metric summary (p-value, β, direction)
2. `fig2_boxplot_12m_counts.png` — Box plot: high vs low Accessible matched groups
3. `fig3_ps_distribution.png` — Propensity score distribution before/after matching
4. `fig4_love_plot.png` — Love plot (SMD before/after for all covariates)
5. `fig5_ols_coefficients.png` — Standardized β forest plot for all F-UJI sub-criteria
6. `fig6_window_sensitivity.png` — p-value comparison: 6-month vs 12-month windows
- **Reuse:** h-m1 `src/visualize.py` + new figure types

### FR-13: Results Serialization

**Requirement:** Save results to structured YAML/JSON for Phase 4 validation
- Save: MWU stat, p-value, effect size, β coefficients, matched pair counts, SMD
- **Reuse:** h-m1 `src/serialize.py` (validated)

### FR-14: Unit Tests (≥25 tests)

**Requirement:** Test coverage for all new and modified modules
- Test new: `accessible_prep.py`, `mwu_analysis.py`
- Verify reused modules: `ingest.py`, `matching.py`, `serialize.py`, `visualize.py`
- Smoke test with synthetic cohort n=200

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | OpenML post-2018 tabular cohort (12-month run window) |
| **Source** | OpenML Python API (openml.org) |
| **Access** | Programmatic API — auto-download via `openml` library |
| **Filter** | upload_date >= 2018-01-01, task_type = tabular |
| **Expected size** | ~5,000 datasets (same as h-e1/h-m1 cohort) |
| **After filter** | ~2,000–3,000 datasets with ≥1 run in 12 months |
| **Loading code** | `import openml; datasets = openml.datasets.list_datasets(output_format='dataframe')` |
| **Run timestamps** | `openml.runs.list_runs(dataset=dataset_id, output_format='dataframe')` |

**Note:** Auto-download via OpenML API — no manual download task required.

### 4.2 Evaluation Split

- **Smoke test:** Synthetic dry-run cohort n=200 (same as h-m1)
- **Production:** Full OpenML post-2018 cohort (~5,000 datasets)
- **No train/val/test split** — observational study uses full cohort for analysis
- **Minimum matched pairs:** 500 (production requirement per gate condition)

### 4.3 Preprocessing Steps

1. Filter: upload_date >= 2018-01-01 AND task_type = tabular
2. Compute 12-month run count: filter run timestamps to [upload_date, upload_date + 365 days]
3. Extract Accessible sub-score from F-UJI results (h-e1 scoring pass)
4. Log-transform DV: log1p(run_count_12m) for OLS regression
5. Standardize all F-UJI sub-criteria (z-score) for comparable β

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Statistical analysis completes within 10 minutes for full cohort (~5,000 datasets)
- No GPU required (scipy, statsmodels, sklearn — CPU-only)

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic matching with caliper=0.8 (smoke test), 0.2 (production)
- All random operations seeded

### NFR-3: Code Quality
- Reuse h-m1 validated modules where possible
- Unit tests ≥25 covering new modules
- Type hints on all new functions

### NFR-4: Environment
- Python 3.8+
- Libraries: scipy, statsmodels, sklearn, openml, numpy, pandas, matplotlib, seaborn, PyYAML

---

## 6. Success Criteria

| Priority | Metric | Threshold | Gate |
|----------|--------|-----------|------|
| PRIMARY | Mann-Whitney U p-value | p < 0.05 | SHOULD_WORK |
| PRIMARY | Direction | high-Accessible mean 12m count > low-Accessible | SHOULD_WORK |
| SECONDARY | Accessible standardized β | β > 0.10 | SHOULD_WORK |
| CODE | Unit tests pass | 100% (≥25 tests) | Always |
| CODE | Smoke test runs without error | No exceptions | Always |

**Gate Type:** SHOULD_WORK — failure documents non-significant Accessible dimension; pipeline continues to h-m3.

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.7.0
statsmodels>=0.13.0
scikit-learn>=0.24.0
openml>=0.12.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
PyYAML>=5.4.0
```

### 7.2 Internal Dependencies (h-m1 Codebase)

| Module | Path | Status |
|--------|------|--------|
| Data ingestion | h-m1/code/src/ingest.py | Validated (reuse) |
| Propensity matching | h-m1/code/src/matching.py | Validated (reuse) |
| Data prep | h-m1/code/src/survival_prep.py | Validated (adapt → accessible_prep.py) |
| Serialization | h-m1/code/src/serialize.py | Validated (reuse) |
| Visualization | h-m1/code/src/visualize.py | Validated (reuse + extend) |

### 7.3 External Repositories

- OpenML Python API: https://github.com/openml/openml-python (reference)

---

## 8. File Structure

```
h-m2/
  code/
    src/
      ingest.py          # Reused from h-m1
      matching.py        # Reused from h-m1
      accessible_prep.py # NEW: 12-month run count computation
      mwu_analysis.py    # NEW: Mann-Whitney U + OLS regression
      serialize.py       # Reused from h-m1
      visualize.py       # Reused/extended from h-m1
    tests/
      test_accessible_prep.py
      test_mwu_analysis.py
      test_integration.py
    run_experiment.py    # Main entry point
    config.yaml          # Experiment configuration
  figures/
    fig1_gate_metrics.png
    fig2_boxplot_12m_counts.png
    fig3_ps_distribution.png
    fig4_love_plot.png
    fig5_ols_coefficients.png
    fig6_window_sensitivity.png
  04_validation.md       # Phase 4 output
```

---

*Generated by Phase 3 PRD step (inline execution — no BMAD workflow infrastructure available)*
*Input: h-m2/02c_experiment_brief.md*
*MCP Mode: no-mcp (domain knowledge substitution)*
