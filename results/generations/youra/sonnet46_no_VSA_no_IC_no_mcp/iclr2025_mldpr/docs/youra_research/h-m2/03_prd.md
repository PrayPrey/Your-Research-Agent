# Product Requirements Document: H-M2
## AIC-Based Model Comparison for Benchmark Score Timeseries

**stepsCompleted:** [Executive Summary, Problem Statement, Functional Requirements, Non-Functional Requirements, Data Specification, Success Criteria, Dependencies]

**Hypothesis:** H-M2 (MECHANISM — INCREMENTAL)
**Type:** Statistical model comparison
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Base Hypothesis:** H-M1 (VALIDATED)

---

## 1. Executive Summary

H-M2 tests whether the logistic (S-curve) model is statistically preferred over linear and power-law alternatives when fitting GLUE and SuperGLUE benchmark score timeseries. Using AIC as the model selection criterion (Burnham & Anderson 2002), the hypothesis passes if ΔAIC(logistic − linear) < −4 for **both** benchmarks, constituting "substantial evidence" that the logistic model captures genuine nonlinear saturation dynamics rather than mere diminishing returns.

This is an incremental experiment: it reuses the validated logistic fit from H-E1 and the confirmed temporal structure from H-M1. The only new logic is AIC computation for all three model families and the formal comparison.

---

## 2. Problem Statement

### 2.1 Research Question
Given confirmed S-curve temporal structure (H-M1), is the logistic model statistically preferred over simpler alternatives (linear, power law) via AIC? And by enough (ΔAIC > 4) to constitute "substantial evidence" per canonical model selection theory?

### 2.2 Gap Addressed
H-M1 established that scores rise monotonically with decelerating gains — consistent with multiple model families. H-M2 formally discriminates: linear growth (constant rate), power-law diminishing returns, or genuine saturation (logistic). Only logistic implies a hard asymptote, which is the signature of benchmark-specific overfitting saturation.

### 2.3 Scope
- **In scope:** Fit 3 models × 2 benchmarks; compute AIC; compare; generate figures
- **Out of scope:** Neural architectures, gradient-based training, new data collection

---

## 3. Functional Requirements

### FR-1: Data Loading (Reuse H-E1 Output)
- **FR-1.1:** Load `glue_timeseries.csv` from `../h-e1/code/` relative to experiment directory
- **FR-1.2:** Load `superglue_timeseries.csv` from `../h-e1/code/`
- **FR-1.3:** Validate columns: `month_idx` (int, 0-based), `max_score` (float, 0–1)
- **FR-1.4:** Fail with descriptive error if files not found (no re-download logic needed)
- **FR-1.5:** Log dataset statistics: n_points GLUE, n_points SuperGLUE

### FR-2: Logistic Model Fitting (Proposed Model)
- **FR-2.1:** Fit 3-parameter logistic `K / (1 + exp(-r*(t-t0)))` via `scipy.optimize.curve_fit`
- **FR-2.2:** Use H-E1 validated bounds: K∈[0.8,1.0], r∈[0.1,2.0], t0∈[6,36]; p0=[0.95,0.5,18]
- **FR-2.3:** maxfev=5000; raise descriptive error if RuntimeError (convergence failure)
- **FR-2.4:** k=3 parameters for AIC computation
- **FR-2.5:** Log fitted params: K, r, t0 for each benchmark

### FR-3: Linear Baseline Fitting (Baseline Model)
- **FR-3.1:** Fit linear model y = a*t + b via `scipy.stats.linregress`
- **FR-3.2:** k=2 parameters for AIC computation
- **FR-3.3:** No bounds or initialization needed (closed-form OLS)
- **FR-3.4:** Log slope and intercept for each benchmark

### FR-4: Power Law Fitting (Secondary Comparison)
- **FR-4.1:** Fit power law `a * (t+1)^b` via `scipy.optimize.curve_fit`
- **FR-4.2:** Bounds: a∈[0,2], b∈[0,1]; p0=[0.5, 0.3]
- **FR-4.3:** k=2 parameters for AIC computation
- **FR-4.4:** +1 to t to avoid singularity at t=0

### FR-5: AIC Computation
- **FR-5.1:** Implement `compute_aic(y_true, y_pred, k)` using formula: `n * log(RSS/n) + 2k`
- **FR-5.2:** Apply to all 3 models for each benchmark
- **FR-5.3:** Compute ΔAIC(logistic vs. linear) = AIC_logistic − AIC_linear (negative = logistic preferred)
- **FR-5.4:** Compute ΔAIC(logistic vs. power law) = AIC_logistic − AIC_power_law
- **FR-5.5:** Log all raw AIC values and ΔAIC values

### FR-6: Gate Evaluation
- **FR-6.1:** Implement `verify_mechanism_activated(results)` returning (pass: bool, indicators: dict)
- **FR-6.2:** Primary gate: ΔAIC(logistic vs. linear) < −4 for BOTH GLUE and SuperGLUE
- **FR-6.3:** Secondary gate: ΔAIC(logistic vs. power law) < −2 for BOTH benchmarks
- **FR-6.4:** Log gate outcome: PASS / FAIL with indicator breakdown
- **FR-6.5:** Write gate result to `results.json`

### FR-7: Visualization (Mandatory)
- **FR-7.1:** Gate metrics bar chart: ΔAIC values for both comparisons × both benchmarks, threshold lines at −4 and −2
- **FR-7.2:** Model fit overlay: scatter + 3 fitted curves per benchmark (2 subplots)
- **FR-7.3:** Residual plot: residuals vs. time for all 3 models × 2 benchmarks
- **FR-7.4:** AIC comparison grouped bar chart: raw AIC values per model × benchmark
- **FR-7.5:** Save all figures to `docs/youra_research/h-m2/figures/`
- **FR-7.6:** Use matplotlib; figures labeled with hypothesis ID and benchmark name

### FR-8: Results Output
- **FR-8.1:** Write `results.json` with: all AIC values, ΔAIC values, logistic params, gate result
- **FR-8.2:** Write `experiment.log` with timestamped execution trace
- **FR-8.3:** Print final summary table to stdout

---

## 4. Non-Functional Requirements

- **NFR-1:** Runtime < 60 seconds (statistical fitting, no training loop)
- **NFR-2:** Reproducible: deterministic optimization (no randomness)
- **NFR-3:** Python ≥ 3.8, scipy ≥ 1.7, numpy ≥ 1.20, matplotlib ≥ 3.3
- **NFR-4:** Fail fast: any convergence failure or missing data raises exception with clear message
- **NFR-5:** Code self-contained in `docs/youra_research/h-m2/code/`
- **NFR-6:** Results interpretable without running code (all values in results.json)

---

## 5. Data Specification

### 5.1 Primary Dataset
- **Name:** GLUE + SuperGLUE Benchmark Score Timeseries
- **Source:** H-E1 curated CSVs (Papers With Code fallback)
- **Location:** `docs/youra_research/h-e1/code/glue_timeseries.csv`, `superglue_timeseries.csv`
- **Download required:** NO — reuse H-E1 output
- **Format:** CSV, columns: `month_idx` (int), `max_score` (float 0–1)
- **Size:** GLUE ~200+ rows, SuperGLUE ~150+ rows
- **Preprocessing:** Already done in H-E1 (monthly aggregation, max score per month)

### 5.2 No Additional Datasets Required

---

## 6. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| ΔAIC(log vs. lin), GLUE | < −4 | PRIMARY (MUST_WORK gate) |
| ΔAIC(log vs. lin), SuperGLUE | < −4 | PRIMARY (MUST_WORK gate) |
| ΔAIC(log vs. power), GLUE | < −2 | SECONDARY |
| ΔAIC(log vs. power), SuperGLUE | < −2 | SECONDARY |
| All 3 models converge | No RuntimeError | REQUIRED |
| Figures generated | 4 figures saved | REQUIRED |
| results.json valid | Gate result present | REQUIRED |

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.20
scipy>=1.7
matplotlib>=3.3
pandas>=1.2
```
All already installed from H-E1 environment.

### 7.2 Internal Dependencies
- `docs/youra_research/h-e1/code/glue_timeseries.csv` — MUST exist (H-E1 validated)
- `docs/youra_research/h-e1/code/superglue_timeseries.csv` — MUST exist (H-E1 validated)
- H-M1 validation results (informational reference only)

### 7.3 External Repositories (Reference Only)
- scipy/scipy: primary fitting engine (already installed)
- paperswithcode/sota-extractor: data provenance (no new download)

---

## 8. Incremental Reuse from H-M1

| Component | Reuse Level | What's New in H-M2 |
|-----------|-------------|---------------------|
| Dataset (CSVs) | 100% reuse | Nothing |
| Logistic fit code | 95% reuse | AIC output added |
| Linear fit | New | FR-3 (2 lines) |
| Power law fit | New | FR-4 (5 lines) |
| AIC computation | New | FR-5 (core contribution) |
| Gate logic | New | FR-6 (ΔAIC threshold check) |
| Figures | Partial reuse | 3 new figures + new gate chart |
