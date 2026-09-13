---
stepsCompleted:
  - "Executive Summary"
  - "Problem Statement"
  - "Functional Requirements"
  - "Non-Functional Requirements"
  - "Data Specification"
  - "Success Criteria"
  - "Dependencies"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
date: "2026-08-25"
---

# Product Requirements Document: H-E1

## Executive Summary

This PoC experiment validates whether Papers With Code leaderboard timeseries data for GLUE and SuperGLUE benchmarks has sufficient coverage of growth, inflection, and plateau phases for `scipy.optimize.curve_fit` to converge on a 3-parameter logistic model with R² > 0.9.

This is a MUST_WORK gate for the entire research chain (H-M1 through H-C1). If the logistic fit fails, all downstream hypotheses are blocked.

**Scope:** EXISTENCE (PoC) — direction-only validation. No comparative study, no ablation variants, no training. Statistical fitting only.

---

## Problem Statement

### Background

Benchmark performance on NLP datasets (GLUE, SuperGLUE) follows a characteristic S-curve: rapid gains in early years, inflection as state-of-the-art approaches human parity, and plateau once human parity is exceeded. Quantitatively modeling this lifecycle requires fitting a logistic growth function to the score-over-time timeseries.

### Research Question

Does the Papers With Code leaderboard API provide timeseries data with sufficient temporal and score coverage for `scipy.optimize.curve_fit` to converge on a 3-parameter logistic model (R² > 0.9) for both GLUE and SuperGLUE?

### Hypothesis Gate

MUST_WORK: Both convergence AND R² > 0.9 for BOTH benchmarks. Failure blocks H-M1 through H-C1.

---

## Functional Requirements

### FR-1: Data Retrieval

**FR-1.1:** The system SHALL retrieve all leaderboard results for GLUE benchmark via `paperswithcode-client` library using `benchmark_id='glue'`.

**FR-1.2:** The system SHALL retrieve all leaderboard results for SuperGLUE benchmark via `paperswithcode-client` library using `benchmark_id='super-glue'`.

**FR-1.3:** The system SHALL paginate through all available results until exhausted.

**FR-1.4:** The system SHALL extract `(date_str, composite_score)` pairs from each result object.

### FR-2: Data Preprocessing

**FR-2.1:** The system SHALL filter out entries with null date fields.

**FR-2.2:** The system SHALL filter entries with date < 2019-01-01.

**FR-2.3:** The system SHALL convert date strings to `months_since_release` (float): `(date - release_date).days / 30.44`.
- GLUE release date: 2019-02-01
- SuperGLUE release date: 2019-05-01

**FR-2.4:** The system SHALL normalize composite scores to [0, 1] by dividing by 100.0.

**FR-2.5:** The system SHALL deduplicate by keeping the maximum score per month-bin (group by integer month).

**FR-2.6:** The system SHALL verify ≥ 50 entries remain after deduplication (hypothesis eligibility criterion).

### FR-3: Baseline Model

**FR-3.1:** The system SHALL fit a linear trend model using `numpy.polyfit(t_months, scores, deg=1)`.

**FR-3.2:** The system SHALL compute R² for the linear fit.

**FR-3.3:** The system SHALL compute AIC for the linear fit: `AIC = n * ln(RSS/n) + 2*k` where k=2.

### FR-4: Logistic Growth Model

**FR-4.1:** The system SHALL implement the 3-parameter logistic function:
```
f(t, K, r, t0) = K / (1 + exp(-r * (t - t0)))
```

**FR-4.2:** The system SHALL fit the logistic model using `scipy.optimize.curve_fit` with:
- Initial parameters: `p0 = [0.9, 0.5, median(t_months)]`
- Bounds: `K ∈ [0.8, 1.05]`, `r ∈ [0.01, 5.0]`, `t0 ∈ [0.0, 60.0]`
- `maxfev=10000`

**FR-4.3:** The system SHALL detect convergence failure by catching `scipy.optimize.OptimizeWarning` and `RuntimeError`.

**FR-4.4:** The system SHALL compute R² for the logistic fit.

**FR-4.5:** The system SHALL compute 95% confidence intervals from `pcov` diagonal: `CI = 1.96 * sqrt(pcov[i,i])`.

**FR-4.6:** The system SHALL compute ΔAIC = AIC(logistic) - AIC(linear).

### FR-5: Evaluation and Reporting

**FR-5.1:** The system SHALL report `converged` (bool) for each benchmark.

**FR-5.2:** The system SHALL report `r_squared` (float) for each benchmark.

**FR-5.3:** The system SHALL report fitted parameters (K, r, t0) with 95% CIs.

**FR-5.4:** The system SHALL report ΔAIC for each benchmark.

**FR-5.5:** The system SHALL emit a PoC pass/fail verdict: PASS if converged==True AND r_squared>0.9 for BOTH benchmarks.

### FR-6: Visualization

**FR-6.1 (MANDATORY):** The system SHALL generate a bar chart of R² values for GLUE and SuperGLUE with a 0.9 threshold line. Saved to `figures/gate_metrics.png`.

**FR-6.2:** The system SHALL generate scatter plots of raw (t_months, score) for GLUE and SuperGLUE with fitted logistic curve overlays. Saved to `figures/logistic_fit_glue.png` and `figures/logistic_fit_superglue.png`.

**FR-6.3:** The system SHALL generate residual plots (predicted vs actual) for both benchmarks. Saved to `figures/residuals.png`.

**FR-6.4:** The system SHALL generate a parameter summary table (K, r, t0 with 95% CI). Saved to `figures/parameter_summary.png`.

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**NFR-1.1:** All random seeds are not applicable (scipy curve_fit is deterministic given p0 and bounds).

**NFR-1.2:** The experiment SHALL be fully reproducible by re-running the script.

### NFR-2: Performance

**NFR-2.1:** Total runtime SHALL complete within 5 minutes on standard hardware (API calls dominate).

**NFR-2.2:** API calls SHALL include retry logic with exponential backoff (max 3 retries).

### NFR-3: Error Handling

**NFR-3.1:** API failures SHALL be reported with HTTP status code and retry count.

**NFR-3.2:** Convergence failures SHALL be reported with last parameter values attempted.

**NFR-3.3:** Insufficient data (< 50 entries) SHALL raise a descriptive exception.

### NFR-4: Output

**NFR-4.1:** All figures SHALL be saved to `docs/youra_research/h-e1/figures/`.

**NFR-4.2:** A results summary SHALL be printed to stdout in structured format.

**NFR-4.3:** A results JSON file SHALL be saved to `docs/youra_research/h-e1/results.json`.

---

## Data Specification

### Primary Datasets

| Benchmark | API ID | Release Date | Expected Entries (post-filter) | Composite Metric |
|-----------|--------|--------------|-------------------------------|------------------|
| GLUE | `glue` | 2019-02-01 | ~400–550 | Average of 9 task scores (0–100) |
| SuperGLUE | `super-glue` | 2019-05-01 | ~250–350 | Average of 8 task scores (0–100) |

**Retrieval method:** `paperswithcode-client` Python library (pip installable, official)

**No manual download required** — data retrieved programmatically via API.

### Data Pipeline Summary

1. API retrieval (paginated)
2. Date filtering (non-null, ≥ 2019-01-01)
3. Month conversion (months_since_release float)
4. Score normalization (÷ 100)
5. Deduplication (max score per month-bin)
6. Eligibility check (≥ 50 entries)

---

## Success Criteria

### Primary Success Criteria (Gate Metrics)

| Criterion | Benchmark | Threshold | Measurement |
|-----------|-----------|-----------|-------------|
| Convergence | GLUE | True | `curve_fit` completes without RuntimeError |
| Convergence | SuperGLUE | True | `curve_fit` completes without RuntimeError |
| R² | GLUE | > 0.9 | OLS R² of logistic fit |
| R² | SuperGLUE | > 0.9 | OLS R² of logistic fit |

**PoC PASS:** ALL 4 criteria met.
**PoC FAIL:** ANY criterion fails → H-M1 through H-C1 blocked.

### Secondary Metrics (Informational)

| Metric | Expected Range | Notes |
|--------|----------------|-------|
| K (carrying capacity) | [0.88, 0.95] | Normalized performance ceiling |
| r (growth rate) | [0.3, 0.8] | Exploitation speed |
| t0 (inflection) | 12–24 months | Months post-release |
| ΔAIC (logistic - linear) | < -4 | Logistic preferred |
| Entry count (GLUE) | 400–550 | Post-dedup |
| Entry count (SuperGLUE) | 250–350 | Post-dedup |

---

## Dependencies

### 7.1 Python Packages

```
paperswithcode-client>=0.1.0    # Official Papers With Code API client
scipy>=1.9.0                     # curve_fit, optimize
numpy>=1.21.0                    # polyfit, array ops
matplotlib>=3.5.0                # Figure generation
requests>=2.28.0                 # HTTP (transitive dep of pwc client)
```

### 7.2 External References

- Papers With Code API: `https://paperswithcode.com/api/v1/`
- paperswithcode-client: `https://github.com/paperswithcode/paperswithcode-client`
- SciPy curve_fit docs: `https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html`

### 7.3 No Model Downloads Required

This experiment uses only statistical fitting libraries — no neural network weights, no model checkpoints, no dataset downloads from external storage.

---

## Phase 2C Completeness Check

| Item from 02c_experiment_brief.md | In PRD |
|-----------------------------------|--------|
| Dataset: GLUE (`glue`) | ✅ FR-1.1, Data Spec |
| Dataset: SuperGLUE (`super-glue`) | ✅ FR-1.2, Data Spec |
| Baseline: numpy.polyfit linear | ✅ FR-3 |
| Proposed: scipy curve_fit logistic | ✅ FR-4 |
| Metric: `converged` (bool) | ✅ FR-5.1, Success Criteria |
| Metric: `r_squared` > 0.9 | ✅ FR-5.2, Success Criteria |
| Preprocessing: null filter, dedup, normalize | ✅ FR-2 |
| Bounds: K[0.8,1.05], r[0.01,5.0], t0[0,60] | ✅ FR-4.2 |
| Figures: gate_metrics bar chart | ✅ FR-6.1 |
| Figures: scatter+fit, residuals, params | ✅ FR-6.2–6.4 |
| Dependencies: paperswithcode-client, scipy, numpy | ✅ Section 7.1 |
