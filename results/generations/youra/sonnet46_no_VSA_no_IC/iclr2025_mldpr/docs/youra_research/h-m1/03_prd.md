# Product Requirements Document: H-M1
# Pre-Breakpoint Residual CoV Variance Characterization

**Hypothesis:** H-M1 (MECHANISM / INCREMENTAL)
**Prerequisite:** H-E1 (VALIDATED — paper_count* confirmed)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md

---

## Executive Summary

Implement and validate a pre-breakpoint variance characterization analysis on the residual CoV series derived from H-E1 PELT output. The experiment tests whether the pre-breakpoint segment of the residual CoV series exhibits significantly higher variance than the global (full N=111) variance, confirming the early-phase exploration regime of the Goodhart saturation mechanism. Gate: one-sample F-test p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0.

**Gate:** MUST_WORK — if FAIL, Goodhart early-phase exploration mechanism not supported for this dataset.

---

## Problem Statement

H-E1 confirmed a structural break (paper_count*) in the residual CoV vs paper_count relationship. H-M1 asks: is the pre-breakpoint segment genuinely higher-variance than the overall series, as predicted by Goodhart saturation theory (early exploration regime = high variance)? This characterizes the mechanism driving the structural break.

**Current State:** Break detected (H-E1 PASS). Pre-segment variance not yet quantified relative to global.

**Desired State:** Pre-segment variance confirmed significantly greater than global variance (F-test p < 0.10, variance_ratio > 1.0), with directional mean confirmation (pre_mean > 0).

---

## Functional Requirements

### FR-1: Load H-E1 Outputs
- **FR-1.1:** Load residual_cov series from H-E1 output: `data/pwc_cov_computed.csv` (columns: benchmark_name, paper_count, cov, residual_cov); series must be sorted by paper_count ascending
- **FR-1.2:** Load paper_count_star_idx (PELT breakpoint array index, integer) from H-E1 validation output; if not saved, recompute from H-E1 code using same parameters (ruptures PELT, l2 model, BIC penalty)
- **FR-1.3:** Validate: len(residual_cov) == 111 (N=111 benchmarks)
- **FR-1.4:** Validate: 0 < paper_count_star_idx < 111 (non-boundary breakpoint)
- **FR-1.5:** Early-fail if paper_count_star_idx not recoverable
- **FR-1.6:** Early-fail if len(pre_segment) < 3 (insufficient pre-segment observations)

### FR-2: Baseline — Global Variance
- **FR-2.1:** Compute global_variance = np.var(residual_cov, ddof=1) over full N=111 series
- **FR-2.2:** Record global_mean = np.mean(residual_cov) (expected ≈ 0 after OLS detrending)
- **FR-2.3:** Log: `"Global variance (N=111): {global_variance:.6f}"`

### FR-3: Pre/Post Segment Split
- **FR-3.1:** Split residual_cov at paper_count_star_idx: pre = residual_cov[:paper_count_star_idx], post = residual_cov[paper_count_star_idx:]
- **FR-3.2:** Record n_pre = len(pre), n_post = len(post); validate n_pre + n_post == 111
- **FR-3.3:** Compute pre_variance = np.var(pre, ddof=1), pre_mean = np.mean(pre)
- **FR-3.4:** Compute post_variance = np.var(post, ddof=1), post_mean = np.mean(post)
- **FR-3.5:** Log: `"Pre-segment N={n_pre}, variance={pre_variance:.6f}, global_var={global_variance:.6f}"`

### FR-4: One-Sample F-Test (Primary Gate)
- **FR-4.1:** Compute F_stat = pre_variance / global_variance
- **FR-4.2:** df1 = n_pre - 1, df2 = 111 - 1
- **FR-4.3:** Compute p_one_tailed = 1 - scipy.stats.f.cdf(F_stat, df1, df2) (one-tailed, right tail: H1 = pre_var > global_var)
- **FR-4.4:** Compute variance_ratio_pre_global = pre_variance / global_variance
- **FR-4.5:** Gate check: p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0
- **FR-4.6:** Log: `"F-test: F={F_stat:.4f}, p_one_tailed={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f}"`

### FR-5: Directional Confirmation
- **FR-5.1:** Check pre_mean_positive = (pre_mean > 0) (above-trend early-phase behavior)
- **FR-5.2:** Log: `"Pre-segment mean: {pre_mean:.6f} ({'POSITIVE' if pre_mean > 0 else 'NEGATIVE'})"`

### FR-6: Brown-Forsythe Preview (H-M2 Preparation)
- **FR-6.1:** Compute scipy.stats.levene(pre, post, center='median') → bf_stat, bf_p
- **FR-6.2:** Record as secondary metric (not gating for H-M1; informs H-M2)
- **FR-6.3:** Log: `"Brown-Forsythe pre vs post: stat={bf_stat:.4f}, p={bf_p:.4f}"`

### FR-7: Mechanism Verification
- **FR-7.1:** Implement `verify_mechanism_activated(results)` returning (all_pass, indicators_dict)
- **FR-7.2:** Indicators: pre_var_computed (not None), global_var_computed (not None), ratio_above_one (variance_ratio_pre_global > 1.0), f_stat_computed (not None), p_value_computed (not None)
- **FR-7.3:** Gate pass condition: p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0
- **FR-7.4:** Log: `"GATE: {'PASS' if gate_passed else 'FAIL'} (p={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f})"`

### FR-8: Visualization
- **FR-8.1:** Gate metrics comparison bar chart: global_var vs pre_var vs post_var with F-test p annotation (MANDATORY)
- **FR-8.2:** Residual CoV scatter vs paper_count with vertical line at paper_count*, colored pre (blue) / post (red)
- **FR-8.3:** KDE distribution overlay: pre-segment vs post-segment vs full-series residual_CoV
- **FR-8.4:** Box plots: pre-segment vs post-segment vs full-series residual_CoV distributions
- **FR-8.5:** Save all figures to `docs/youra_research/h-m1/figures/`

### FR-9: Results Output
- **FR-9.1:** Save `docs/youra_research/h-m1/experiment_results.json` with all metrics
- **FR-9.2:** JSON schema: {n_pre, n_post, global_variance, pre_variance, post_variance, pre_mean, post_mean, F_stat, p_one_tailed, variance_ratio_pre_global, pre_mean_positive, bf_stat, bf_p, gate_passed}
- **FR-9.3:** Print gate pass/fail summary to stdout

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- **NFR-1.1:** Deterministic (no random operations beyond inherited H-E1 seed=42)
- **NFR-1.2:** Results identical across runs given same H-E1 outputs

### NFR-2: Performance
- **NFR-2.1:** Full pipeline completes in < 10 seconds on CPU (N=111, no iterations)
- **NFR-2.2:** No GPU required

### NFR-3: Code Quality
- **NFR-3.1:** Each module independently testable
- **NFR-3.2:** Type hints on all public functions
- **NFR-3.3:** Docstrings on all public functions

---

## Data Specification

### Section 4: Primary Dataset
- **Name:** PwC CoV Computed — H-E1 derive.py output
- **Source:** `data/pwc_cov_computed.csv` (local, produced by H-E1 pipeline)
- **Loading:** `pd.read_csv('data/pwc_cov_computed.csv')`
- **Columns:** benchmark_name, paper_count, cov, residual_cov
- **N:** 111 benchmarks (sorted by paper_count ascending)
- **Manual download:** No — inherited from H-E1 (already present)

### Derived Variables
| Variable | Type | Source | Description |
|----------|------|--------|-------------|
| residual_cov | float array | H-E1 derive.py output | OLS-detrended CoV, N=111, sorted by paper_count |
| paper_count_star_idx | int | H-E1 PELT output | Breakpoint array index (0-based) |
| pre | float array | slice residual_cov[:idx] | Pre-breakpoint observations |
| post | float array | slice residual_cov[idx:] | Post-breakpoint observations |

### H-E1 Output Reference
- `docs/youra_research/h-e1/code/` — ingest_pwc.py, derive.py, pipeline.py
- `docs/youra_research/h-e1/experiment_results.json` — contains paper_count_star value
- `docs/youra_research/h-e1/04_validation.md` — Phase 4 validation output

---

## Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| p_one_tailed | < 0.10 | PRIMARY GATE |
| variance_ratio_pre_global | > 1.0 | PRIMARY GATE |
| pre_mean_positive | True (pre_mean > 0) | Directional confirmation |
| bf_p | (recorded, not gating) | Secondary (H-M2 preview) |
| Code runs without error | True | PoC prerequisite |

**PASS:** p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0
**FAIL:** Goodhart early-phase exploration mechanism not supported for this dataset

---

## Section 7: Dependencies

### Section 7.1: Python Packages
```
ruptures>=1.1.9
scipy>=1.11.0
statsmodels>=0.14.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```
*(Inherited from H-E1 environment — no new packages required)*

### Section 7.2: External Repositories (Reference Only)
- deepcharles/ruptures — PELT segment indexing (reused from H-E1)
- scipy/scipy — stats.f.cdf, stats.levene

---

## Phase 2C Completeness Check

| Item | Present in FRs | Location |
|------|---------------|----------|
| H-E1 outputs loaded (residual_cov, paper_count_star_idx) | ✅ | FR-1 |
| Baseline (global variance) | ✅ | FR-2 |
| Pre/post segment split | ✅ | FR-3 |
| One-sample F-test (primary gate) | ✅ | FR-4 |
| Directional confirmation (pre_mean > 0) | ✅ | FR-5 |
| Brown-Forsythe preview (H-M2) | ✅ | FR-6 |
| Gate metrics (p<0.10, ratio>1.0) | ✅ | Success Criteria |
| Visualization (4 figures) | ✅ | FR-8 |
| Mechanism verification | ✅ | FR-7 |
| Early-fail guards | ✅ | FR-1.4, FR-1.5, FR-1.6 |
