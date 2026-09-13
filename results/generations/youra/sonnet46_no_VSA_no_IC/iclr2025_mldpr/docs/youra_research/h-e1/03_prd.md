# Product Requirements Document: H-E1
# PELT Change-Point Detection on PwC Benchmark CoV Series

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md

---

## Executive Summary

Implement and validate a PELT (Pruned Exact Linear Time) change-point detection pipeline on the linearly detrended residual Coefficient of Variation (CoV) series derived from PaperWithCode (PwC) N=111 benchmark data sorted by paper_count. The experiment determines whether a statistically significant structural break (paper_count*) exists in the CoV-vs-paper_count relationship, confirmed by permutation test p < 0.05 and paper_count* ∈ [10, 120].

**Gate:** MUST_WORK — if FAIL, pipeline stops; null result published (H0 = smooth monotonic rho=−0.28 is best description).

---

## Problem Statement

The PwC leaderboard CoV series exhibits a known negative correlation (rho=−0.28) with paper_count. The question is whether this relationship is smooth monotonic (H0) or contains a structural break at some paper_count* (H1). Detection of paper_count* is foundational for downstream hypotheses H-M1, H-M2, H-M3 which model regime-specific dynamics.

**Current State:** OLS linear model only; R²≈0.08 (8% variance explained). No change-point analysis performed on this dataset.

**Desired State:** PELT detection identifies paper_count* with permutation p < 0.05 and paper_count* ∈ [10, 120].

---

## Functional Requirements

### FR-1: Data Loading and Preprocessing
- **FR-1.1:** Load PwC evaluation tables from HuggingFace `pwc-archive/evaluation-tables` (split="train")
- **FR-1.2:** Reuse existing `ingest_pwc.py::fetch_pwc_benchmarks()` and `derive.py::compute_result_cov()` from archive (confirmed working, returns N=111 benchmarks)
- **FR-1.3:** Filter: benchmarks with ≥ 3 result rows for CoV computation (CoV = std(ddof=1)/mean)
- **FR-1.4:** Filter: benchmarks with ≥ MIN_PAPERS unique paper titles (MIN_PAPERS configurable, default=5)
- **FR-1.5:** Produce `result_CoV` per benchmark (float, from derive.py)
- **FR-1.6:** Produce `paper_count` per benchmark (integer, count of unique paper_titles)
- **FR-1.7:** Early-fail if N < 10 after filtering (insufficient data for min_size=3)
- **FR-1.8:** Early-fail if residual_cov.std() == 0 (degenerate input)

### FR-2: OLS Detrending (Baseline)
- **FR-2.1:** Fit OLS: `result_CoV ~ paper_count` using `scipy.stats.linregress`
- **FR-2.2:** Extract residuals: `residual_CoV = result_CoV - (slope * paper_count + intercept)`
- **FR-2.3:** Sort `residual_CoV` ascending by `paper_count` → PELT input series (length N)
- **FR-2.4:** Record OLS metrics: slope, intercept, rho, R² (baseline performance)
- **FR-2.5:** Expected baseline: rho=−0.28, R²≈0.08 (validation check from prior work)

### FR-3: PELT Change-Point Detection
- **FR-3.1:** Implement `run_pelt_changepoint(paper_counts, cov_values, pen_range=(1,50), n_pen=20, min_size=3)` returning results dict
- **FR-3.2:** Use `ruptures.Pelt(model="l2", min_size=3, jump=1)` (L2 cost, no subsampling for N=111)
- **FR-3.3:** Compute BIC penalty: `pen = sigma² * log(T)` where sigma=std(residual_CoV, ddof=1), T=N
- **FR-3.4:** Sensitivity sweep: `np.logspace(log10(1), log10(50), 20)` penalty values; elbow plot
- **FR-3.5:** Primary detection at BIC penalty; elbow as sensitivity check
- **FR-3.6:** Extract `paper_count_star = sorted_pc[bkps[0] - 1]` if breakpoint detected
- **FR-3.7:** Return: paper_count_star, breakpoint_idx, pen_used, n_bkps, residual_cov_sorted, sorted_paper_counts
- **FR-3.8:** Log: `"PELT detected {n} breakpoint(s) at index {bkp_idx} → paper_count* = {val}"`

### FR-4: Permutation Test (Primary Gate)
- **FR-4.1:** Implement `run_permutation_test(paper_counts, cov_values, n_permutations=1000, seed=42)`
- **FR-4.2:** Null statistic: shuffle paper_count labels, rerun full pipeline (sort→detrend→PELT), record breakpoint position
- **FR-4.3:** Observed statistic: breakpoint_idx from actual data
- **FR-4.4:** p-value: fraction of null statistics ≤ observed statistic
- **FR-4.5:** Gate: permutation_p < 0.05

### FR-5: Bootstrap CI for paper_count*
- **FR-5.1:** Implement bootstrap CI with N_resamples=1000, method='percentile', seed=42
- **FR-5.2:** Resample benchmarks with replacement; rerun full pipeline each bootstrap
- **FR-5.3:** Report 95% CI: [lower, upper] for paper_count*
- **FR-5.4:** Check CI width ≤ 20 papers (reliability criterion)

### FR-6: Piecewise Linear Regression F-test (Independent Check)
- **FR-6.1:** Fit piecewise linear model at detected paper_count* using statsmodels
- **FR-6.2:** F-test: compare piecewise model vs single linear model
- **FR-6.3:** Report piecewise_f_p (secondary metric, not gating)

### FR-7: Mechanism Verification
- **FR-7.1:** Implement `verify_mechanism_activated(results)` returning (all_pass, indicators_dict)
- **FR-7.2:** Indicators: pelt_detected_breakpoint (n_bkps ≥ 1), paper_count_star_in_range (10 ≤ val ≤ 120), permutation_p_significant (p < 0.05)
- **FR-7.3:** Log verification result with paper_count* value and p-value

### FR-8: Visualization
- **FR-8.1:** Gate metrics bar chart: permutation_p vs 0.05 threshold, paper_count* vs [10,120] range (MANDATORY)
- **FR-8.2:** CoV vs paper_count scatter with paper_count* vertical dashed line and OLS trend
- **FR-8.3:** Residual CoV series (sorted) with PELT segmentation shading (pre/post regimes)
- **FR-8.4:** Permutation null distribution histogram with observed paper_count* marked
- **FR-8.5:** Bootstrap CI distribution plot (1000 estimates + 95% CI bounds)
- **FR-8.6:** Penalty sensitivity plot: n_bkps vs penalty value (log scale)
- **FR-8.7:** Save all figures to `h-e1/figures/` directory

### FR-9: Results Output
- **FR-9.1:** Save `experiment_results.json` with all primary and secondary metrics
- **FR-9.2:** JSON schema: {permutation_p, paper_count_star, bootstrap_ci_lower, bootstrap_ci_upper, bootstrap_ci_width, n_bkps_detected, piecewise_f_p, ols_rho, ols_r2, gate_passed}
- **FR-9.3:** Print gate pass/fail summary to stdout

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- **NFR-1.1:** Fixed seed=42 for all random operations (permutation, bootstrap)
- **NFR-1.2:** Deterministic sorting (stable sort on paper_count)
- **NFR-1.3:** All results reproducible across runs with same seed

### NFR-2: Performance
- **NFR-2.1:** Full pipeline completes in < 5 minutes on CPU (N=111, N_permutations=1000)
- **NFR-2.2:** No GPU required (scipy/ruptures CPU-only)

### NFR-3: Code Quality
- **NFR-3.1:** Each module independently testable
- **NFR-3.2:** Type hints on all public functions
- **NFR-3.3:** Docstrings on all public functions

---

## Data Specification

### Primary Dataset
- **Name:** PwC Evaluation Tables
- **Source:** HuggingFace `pwc-archive/evaluation-tables`, split="train"
- **Loading:** `load_dataset("pwc-archive/evaluation-tables", split="train")`
- **N:** 111 benchmarks (after filtering)
- **Auto-download:** Yes (HuggingFace datasets) — no manual download task needed

### Derived Variables
| Variable | Type | Source | Description |
|----------|------|--------|-------------|
| paper_count | int | ingest_pwc.py | Count of unique papers per benchmark |
| result_CoV | float | derive.py | CoV of metric_value per benchmark (std/mean, ddof=1) |
| residual_CoV | float | pipeline.py | OLS-detrended CoV (residuals from linregress) |

### Archive Reference
- `docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/ingest_pwc.py`
- `docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/derive.py`

---

## Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| permutation_p | < 0.05 | PRIMARY GATE |
| paper_count_star | ∈ [10, 120] | PRIMARY GATE |
| bootstrap_ci_width | ≤ 20 papers | Secondary |
| n_bkps_detected | = 1 | Secondary (parsimony) |
| piecewise_f_p | < 0.05 | Secondary (independent check) |
| Code runs without error | True | PoC prerequisite |

**PASS:** permutation_p < 0.05 AND paper_count_star ∈ [10, 120]
**FAIL → STOP:** H0 supported (smooth monotonic rho=−0.28)

---

## Dependencies

### Section 7.1: Python Packages
```
ruptures>=1.1.9
scipy>=1.11.0
statsmodels>=0.14.0
numpy>=1.24.0
pandas>=2.0.0
datasets>=2.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Section 7.2: External Repositories (Reference Only)
- deepcharles/ruptures (2K stars) — canonical PELT implementation
- scipy/scipy — permutation_test, bootstrap

---

## Phase 2C Completeness Check

| Item | Present in FRs | Location |
|------|---------------|----------|
| Baseline model (OLS linregress) | ✅ | FR-2 |
| Proposed model (PELT ruptures) | ✅ | FR-3 |
| Dataset (pwc-archive/evaluation-tables) | ✅ | Data Spec |
| Permutation test (N=1000) | ✅ | FR-4 |
| Bootstrap CI (N=1000) | ✅ | FR-5 |
| Piecewise F-test | ✅ | FR-6 |
| Gate metrics (p<0.05, pc*∈[10,120]) | ✅ | Success Criteria |
| Visualization (6 figures) | ✅ | FR-8 |
| Mechanism verification | ✅ | FR-7 |
| Early-fail guards | ✅ | FR-1.7, FR-1.8 |
