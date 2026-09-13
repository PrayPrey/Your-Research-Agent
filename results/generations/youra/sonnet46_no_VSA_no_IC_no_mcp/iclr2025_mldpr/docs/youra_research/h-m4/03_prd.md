# Product Requirements Document: H-M4

---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-M4
type: MECHANISM
tier: FULL
created_at: 2026-08-25
author: yoon303@ust.ac.kr
---

## 1. Executive Summary

H-M4 validates that the dual-criterion saturation detection method (top-3 models exceed 0.99×K AND monthly gain rate < 5% of peak rate) produces saturation dates for GLUE and SuperGLUE benchmarks that match community-recognized ground truth dates within ±6 months. This is an incremental experiment extending H-M3's validated curve_fit pipeline (K, r, t0 extraction) by adding a saturation detection layer on top of the fitted parameters.

**Gate (SHOULD_WORK):** |detected_date − ground_truth_date| < 6 months for BOTH GLUE and SuperGLUE. Failure → EXPLORE (alternative criteria Alt-1/Alt-2), document limitation, proceed to H-C1.

**Ground truth:**
- GLUE: September 2019 (~18 months after April 2018 launch)
- SuperGLUE: June 2021 (~25 months after May 2019 launch)

**Expected outcome:** PASS based on H-M3 fitted K values (GLUE: 0.8955, SuperGLUE: 0.8858) and known leaderboard history.

---

## 2. Problem Statement

H-M3 confirmed that logistic model parameters (K, r, t0) are physically plausible for GLUE and SuperGLUE benchmarks. The next mechanism question is whether the fitted saturation ceiling K can be operationalized into a precise saturation DATE that matches known benchmark lifecycle events. H-M4 tests the dual-criterion saturation detector:

1. **K exceedance:** top-3 model mean score exceeds 0.99×K (99% of fitted ceiling)
2. **Rate collapse:** monthly score gain < 5% of peak monthly gain

The hypothesis claims that when BOTH criteria are simultaneously satisfied for the first time, the resulting calendar month is the benchmark saturation date, matching community consensus within ±6 months.

---

## 3. Functional Requirements

### FR-1: Data Pipeline (Inherited from H-M3)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load GLUE leaderboard timeseries from H-M3 cache (`h-m3/code/outputs/results.csv`) or re-fetch | H-M3 reuse |
| FR-1.2 | Load SuperGLUE leaderboard timeseries from same source | H-M3 reuse |
| FR-1.3 | Apply deduplication (best score per model per month) | H-M3 reuse |
| FR-1.4 | Normalize scores to [0,1] range | H-M3 reuse |
| FR-1.5 | Month-level aggregation (max score per month, monotonized via cumulative max) | H-M3 reuse |
| FR-1.6 | Compute top-3 monthly mean: rolling mean of top-3 scores per month | H-M4 new |
| FR-1.7 | Compute month-over-month gain series: `monthly_gain[t] = top3_mean[t] - top3_mean[t-1]` | H-M4 new |
| FR-1.8 | Attach `calendar_month` (YYYY-MM) column aligned with month index | H-M4 new |

**GLUE reference:** Launch April 2018, ground truth saturation September 2019 (month 17).
**SuperGLUE reference:** Launch May 2019, ground truth saturation June 2021 (month 25).

### FR-2: Logistic Fit (Inherited from H-M3)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Re-run `extract_params(df, benchmark)` from H-M3 to obtain K for each benchmark | H-M3 reuse |
| FR-2.2 | Bounds: K∈[0.5,1.05], r∈[0.01,3.0], t0∈[−24,72] | H-M3 confirmed |
| FR-2.3 | Initialization: p0=[0.92, 0.15, 12.0] | H-M3 confirmed |
| FR-2.4 | pcov fallback: bootstrap CI with 500 resamples if pcov diagonal contains inf | H-M3 reuse |

### FR-3: Saturation Detection (H-M4 New)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Implement `detect_saturation_date(monthly_df, K, threshold_k=0.99, threshold_rate=0.05)` | Must |
| FR-3.2 | Compute peak_rate: `monthly_df["monthly_gain"].max()` | Must |
| FR-3.3 | Apply K exceedance criterion: `top3_mean >= threshold_k * K` | Must |
| FR-3.4 | Apply rate-collapse criterion: `monthly_gain <= threshold_rate * peak_rate` | Must |
| FR-3.5 | Return first month where BOTH criteria are simultaneously met (AND logic) | Must |
| FR-3.6 | Return `None` if criterion never met within full timeseries | Must |
| FR-3.7 | Return `(sat_date: str "YYYY-MM", sat_month_idx: int)` | Must |

### FR-4: Error Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Implement `compute_saturation_error(detected_date, ground_truth_date)` using `dateutil.relativedelta` | Must |
| FR-4.2 | Return absolute error in months: `abs(delta.months + delta.years * 12)` | Must |
| FR-4.3 | Handle `None` detected date: return `float('inf')` (criterion never fired) | Must |
| FR-4.4 | Log sat_error_GLUE and sat_error_SuperGLUE | Must |

### FR-5: Baseline

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Implement null baseline: `sat_date = None` (never saturated) for all benchmarks | Must |
| FR-5.2 | Compute null_error = `float('inf')` for comparison | Must |
| FR-5.3 | Report: "H-M4 criterion reduces error from inf (null) to N months" | Must |

### FR-6: Mechanism Activation Verification

| ID | Requirement | Code Location |
|----|-------------|---------------|
| FR-6.1 | Implement `verify_mechanism_activated(results)` checking criterion fired + error threshold | run.py |
| FR-6.2 | Pre-run assertions: K > 0, len(monthly_df) >= 12, required columns present | run.py |
| FR-6.3 | Log activation indicators: criterion_fired_GLUE, criterion_fired_SuperGLUE, error_below_threshold_GLUE, error_below_threshold_SuperGLUE | run.py |

### FR-7: Ablation Variants

| ID | Variant | Description |
|----|---------|-------------|
| FR-7.1 | Primary criterion | threshold_k=0.99, threshold_rate=0.05 (hypothesis statement) |
| FR-7.2 | Alt-1: strict rate | threshold_k=0.99, threshold_rate=0.02 (stricter rate collapse) |
| FR-7.3 | Alt-2: lower exceedance | threshold_k=0.95, threshold_rate=0.05 (lower ceiling bar) |
| FR-7.4 | Prospective test (P3) | Truncate GLUE at T_sat − 6 months, re-fit logistic on truncated data, forecast saturation |
| FR-7.5 | Sensitivity grid | 3×3 grid of threshold_k ∈ {0.95, 0.99, 1.00} × threshold_rate ∈ {0.02, 0.05, 0.10} |

### FR-8: Visualization

| ID | Figure | Type | Priority |
|----|--------|------|----------|
| FR-8.1 | Gate Metrics Comparison | Bar chart: sat_error_GLUE and sat_error_SuperGLUE vs. 6-month threshold | Must (mandatory) |
| FR-8.2 | Saturation Detection Timeline | Full GLUE/SuperGLUE timeseries with logistic fit, detected T_sat marked, ground truth marked | Should |
| FR-8.3 | Dual-Criterion Activation Plot | Two-panel: top3_mean vs. 0.99K threshold; monthly_gain vs. 5% rate threshold | Should |
| FR-8.4 | Prospective Forecast Plot (P3) | GLUE truncated timeseries, re-fitted logistic, forecast vs. actual T_sat | Should |
| FR-8.5 | Sensitivity Analysis Heatmap | threshold_k × threshold_rate grid vs. sat_error (GLUE and SuperGLUE) | Should |

All figures saved to `docs/youra_research/h-m4/figures/`.

---

## 4. Data Specification

**Dataset:** Papers With Code Leaderboard Timeseries (GLUE + SuperGLUE) — cached from H-M3

| Property | Value |
|----------|-------|
| Source | H-M3 cache: `h-m3/code/outputs/results.csv` OR re-fetch from H-M3 data loading code |
| Access | Local cache (no API calls needed; PWC shut down July 2025) |
| GLUE entries | ~200+ entries, April 2018 onward |
| SuperGLUE entries | ~150+ entries, May 2019 onward |
| Split | None — full timeseries for each benchmark |
| Preprocessing | Inherited from H-M3 + new: top-3 mean, gain series, calendar_month column |

**No manual download required** — data cached at `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data/`.

**Ground truth dates (fixed reference):**
- GLUE saturation: 2019-09 (September 2019)
- SuperGLUE saturation: 2021-06 (June 2021)
- Sources: arXiv:1905.00537 (SuperGLUE NeurIPS 2019), arXiv:2206.04615 (BIG-bench)

---

## 5. Non-Functional Requirements

| ID | Requirement | Value |
|----|-------------|-------|
| NFR-1 | Reproducibility | Deterministic (scipy curve_fit deterministic given same data+init; fixed seed=1) |
| NFR-2 | Runtime | < 5 minutes total (statistical detection is trivial) |
| NFR-3 | Code location | `docs/youra_research/h-m4/code/run.py` (extends H-M3 code structure) |
| NFR-4 | Results storage | Save to `h-m4/code/outputs/results.json` |
| NFR-5 | Figures location | `docs/youra_research/h-m4/figures/` |
| NFR-6 | Import from H-M3 | Import/copy `extract_params`, `bootstrap_ci`, `check_pcov_validity` from H-M3 |

---

## 6. Success Criteria

**Primary Gate (SHOULD_WORK):**

| Criterion | Threshold | Expected |
|-----------|-----------|----------|
| sat_error_GLUE | < 6 months | PASS (based on H-M3 K=0.8955, GLUE plateau well-documented) |
| sat_error_SuperGLUE | < 6 months | PASS (based on H-M3 K=0.8858) |
| criterion_fired_GLUE | True | PASS (top-3 likely exceeded 0.99K) |
| criterion_fired_SuperGLUE | True | PASS |

**Secondary (P3 prospective):**

| Criterion | Threshold |
|-----------|-----------|
| forecast_error_GLUE | < 3 months |

**Failure handling:** If sat_error > 6 months, run Alt-1/Alt-2, report closest alternative, document limitation, do NOT block H-C1.

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.7.0
numpy>=1.21.0
matplotlib>=3.4.0
pandas>=1.3.0
python-dateutil>=2.8.0
seaborn>=0.11.0
```

### 7.2 External Repositories / References

| Reference | Purpose |
|-----------|---------|
| `h-m3/code/run.py` | Base fitting code (extract_params, bootstrap_ci, check_pcov_validity) |
| `h-m3/code/outputs/results.csv` | Cached timeseries data with logistic fit results |
| `h-m3/experiment_results.json` | Stored K, r, t0, pcov values for GLUE and SuperGLUE |
| `scipy.optimize.curve_fit` | Logistic fitting (inherited) |
| `dateutil.relativedelta` | Month arithmetic for saturation error |

### 7.3 Prerequisite Data

| Data | Source | Required |
|------|--------|---------|
| H-M3 fitted params (K, r, t0) | `h-m3/experiment_results.json` | Must exist |
| H-M3 cleaned timeseries | `h-m3/code/outputs/results.csv` OR H-M3 data loading | Must exist |
| Ground truth dates (hardcoded) | arXiv:1905.00537, arXiv:2206.04615 | Hardcoded in run.py |

---

## 8. Out of Scope

- Re-running AIC comparison (H-M2, already PASSED)
- Re-validating logistic parameter plausibility (H-M3, already PASSED)
- Extending to benchmarks beyond GLUE and SuperGLUE (H-C1 scope)
- Training any neural network model
- Collecting new benchmark data (data already cached)
