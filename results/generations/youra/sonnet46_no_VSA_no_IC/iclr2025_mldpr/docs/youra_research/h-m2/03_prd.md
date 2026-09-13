# Product Requirements Document: H-M2
# Post-Breakpoint Residual CoV Variance Compression Validation

**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL)
**Prerequisites:** H-E1 (VALIDATED — paper_count* confirmed), H-M1 (VALIDATED — pre-segment high variance confirmed)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md

---

## Executive Summary

Implement and validate a post-breakpoint variance compression analysis comparing pre-segment vs post-segment residual CoV variance. The experiment tests whether the post-breakpoint segment exhibits significantly lower variance than the pre-breakpoint segment (Brown-Forsythe p < 0.05 AND variance_ratio post/pre < 1.0), confirming Goodhart saturation compression. This is the second mechanism hypothesis: H-M1 confirmed the pre-segment is high-variance (3.81× global), and H-M2 asks whether the post-segment is compressed (lower variance).

**Gate:** MUST_WORK — if FAIL, the change-point reflects mean shift only (not variance homogenization); the Goodhart saturation mechanism as described is not operating.

---

## Problem Statement

H-E1 confirmed paper_count* structural break. H-M1 confirmed pre-segment variance is 3.81× global (F-test p=0.0009, BF p=0.0099). H-M2 asks: does the post-breakpoint segment exhibit significantly lower variance than the pre-breakpoint segment, confirming compression? This is a two-sample variance comparison, not a comparison to the global series.

**Current State:** Pre-segment confirmed high-variance (H-M1 PASS). Post-segment variance not yet compared to pre-segment.

**Desired State:** Post-segment variance confirmed significantly lower than pre-segment variance (Brown-Forsythe p < 0.05, variance_ratio post/pre < 1.0), directly confirming Goodhart saturation compression.

---

## Functional Requirements

### FR-1: Load H-E1/H-M1 Outputs
- **FR-1.1:** Load residual_cov series from H-E1 output: `data/pwc_cov_computed.csv` (columns: benchmark_name, paper_count, cov, residual_cov); series must be sorted by paper_count ascending
- **FR-1.2:** Load paper_count_star (integer paper_count value) from H-E1 experiment_results.json (`docs/youra_research/h-e1/experiment_results.json`); if not present, recompute from H-E1 code using same parameters (ruptures PELT, l2 model, BIC penalty)
- **FR-1.3:** Validate: len(residual_cov) == 111 (N=111 benchmarks)
- **FR-1.4:** Validate: paper_count_star is within valid range (not boundary value)
- **FR-1.5:** Early-fail with clear message if paper_count_star not recoverable: "H-E1 paper_count* required — run H-E1 first"
- **FR-1.6:** Early-fail if len(pre_segment) < 3 OR len(post_segment) < 3 (insufficient observations for variance test)

### FR-2: Pre/Post Segment Split
- **FR-2.1:** Split residual_cov at paper_count_star: `pre_segment = residual_cov[paper_count < paper_count_star]`, `post_segment = residual_cov[paper_count >= paper_count_star]`
- **FR-2.2:** Record n_pre = len(pre_segment), n_post = len(post_segment); validate n_pre + n_post == 111
- **FR-2.3:** Compute var_pre = np.var(pre_segment, ddof=1), var_post = np.var(post_segment, ddof=1)
- **FR-2.4:** Compute mean_pre = np.mean(pre_segment), mean_post = np.mean(post_segment)
- **FR-2.5:** Log: `"Segments: n_pre={n_pre}, n_post={n_post}, var_pre={var_pre:.6f}, var_post={var_post:.6f}"`

### FR-3: Brown-Forsythe Test (Primary Gate — Test 1)
- **FR-3.1:** Execute `stats.levene(pre_segment, post_segment, center='median')` → bf_stat, bf_p_two_tailed
- **FR-3.2:** NOTE: `center='median'` is mandatory — this IS the Brown-Forsythe variant; `center='mean'` is Levene's test (different robustness)
- **FR-3.3:** Compute one-tailed p-value: bf_p_one_tailed = bf_p_two_tailed / 2 IF variance_ratio < 1.0 (direction confirmed), ELSE bf_p_one_tailed = 1.0
- **FR-3.4:** Log: `"Brown-Forsythe: stat={bf_stat:.4f}, p_two={bf_p_two_tailed:.4f}, p_one={bf_p_one_tailed:.4f}"`

### FR-4: Variance Ratio Computation (Primary Gate — Test 2)
- **FR-4.1:** Compute variance_ratio = var_post / var_pre (H1: ratio < 1.0)
- **FR-4.2:** Check direction_confirmed = (variance_ratio < 1.0)
- **FR-4.3:** Log: `"Variance ratio (post/pre): {variance_ratio:.4f}, direction_confirmed={direction_confirmed}"`

### FR-5: Gate Check (Combined)
- **FR-5.1:** gate_passed = (bf_p_two_tailed < 0.05) AND (variance_ratio < 1.0)
- **FR-5.2:** Log: `"GATE: {'PASS' if gate_passed else 'FAIL'} — BF p={bf_p_two_tailed:.4f} (threshold 0.05), ratio={variance_ratio:.4f} (threshold 1.0)"`
- **FR-5.3:** If gate fails, log failure reason: which condition(s) failed

### FR-6: Piecewise Regression F-Test (Independent Confirmation)
- **FR-6.1:** Fit OLS on full series: `cov ~ paper_count` (baseline model)
- **FR-6.2:** Fit piecewise OLS with regime indicator: allow different slope+intercept pre/post paper_count_star
- **FR-6.3:** Compare models with F-test via statsmodels `anova_lm` or manual F-statistic
- **FR-6.4:** Record piecewise_f_stat, piecewise_f_p (secondary metric — not gating)
- **FR-6.5:** Log: `"Piecewise regression F-test: F={piecewise_f_stat:.4f}, p={piecewise_f_p:.4f}"`

### FR-7: Mechanism Verification
- **FR-7.1:** Implement `verify_mechanism_activated(results)` returning (all_pass, indicators_dict)
- **FR-7.2:** Indicators: direction_confirmed (variance_ratio < 1.0), statistically_significant (bf_p_two_tailed < 0.05), effect_measured (var_pre != var_post), n_pre_nonzero (n_pre > 0), n_post_nonzero (n_post > 0)
- **FR-7.3:** Gate: all_pass = direction_confirmed AND statistically_significant
- **FR-7.4:** Log: `"Mechanism verification: {indicators}; Gate verdict: {'PASS' if all_pass else 'FAIL'}"`

### FR-8: Visualization
- **FR-8.1:** Gate metrics comparison bar chart — bf_p_two_tailed vs threshold 0.05, variance_ratio vs threshold 1.0 (MANDATORY)
- **FR-8.2:** Side-by-side box plots of pre-segment vs post-segment residual CoV (visual variance comparison)
- **FR-8.3:** Variance magnitude bar chart: var_pre vs var_post with ratio annotation (var_post/var_pre = {ratio:.3f})
- **FR-8.4:** Residual CoV scatter vs paper_count — all N=111 points colored by regime (pre=orange, post=blue) with ±1 SD variance bounds overlaid for each regime
- **FR-8.5:** F-distribution reference plot — annotated F(1, N-2) distribution showing BF test statistic position vs critical value
- **FR-8.6:** Save all figures to `docs/youra_research/h-m2/figures/`

### FR-9: Results Output
- **FR-9.1:** Save `docs/youra_research/h-m2/experiment_results.json` with all metrics
- **FR-9.2:** JSON schema: {n_pre, n_post, var_pre, var_post, mean_pre, mean_post, variance_ratio, bf_stat, bf_p_two_tailed, bf_p_one_tailed, direction_confirmed, piecewise_f_stat, piecewise_f_p, gate_passed}
- **FR-9.3:** Print gate pass/fail summary to stdout

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- **NFR-1.1:** Fully deterministic given fixed paper_count_star from H-E1
- **NFR-1.2:** Results identical across runs given same H-E1 outputs

### NFR-2: Performance
- **NFR-2.1:** Full pipeline completes in < 10 seconds on CPU (N=111, statistical tests only)
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
| paper_count_star | int | H-E1 experiment_results.json | Breakpoint paper_count value |
| pre_segment | float array | residual_cov[paper_count < paper_count_star] | Pre-breakpoint observations |
| post_segment | float array | residual_cov[paper_count >= paper_count_star] | Post-breakpoint observations |

### H-E1/H-M1 Output Reference
- `docs/youra_research/h-e1/code/` — ingest_pwc.py, derive.py, pipeline.py
- `docs/youra_research/h-e1/experiment_results.json` — contains paper_count_star value
- `docs/youra_research/h-m1/experiment_results.json` — contains pre_segment/post_segment arrays (reusable)
- `docs/youra_research/h-m1/code/` — reference segment split implementation

---

## Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| bf_p_two_tailed | < 0.05 | PRIMARY GATE |
| variance_ratio (post/pre) | < 1.0 | PRIMARY GATE |
| Both conditions simultaneously | True | GATE VERDICT |
| direction_confirmed | True | Directional confirmation |
| piecewise_f_p | < 0.05 (expected) | Secondary (independent confirmation) |
| Code runs without error | True | PoC prerequisite |

**PASS:** bf_p_two_tailed < 0.05 AND variance_ratio < 1.0
**FAIL:** Goodhart saturation compression not confirmed — change-point reflects mean shift only

---

## Section 7: Dependencies

### Section 7.1: Python Packages
```
ruptures>=1.1.9
scipy>=1.7.0
statsmodels>=0.14.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```
*(Fully inherited from H-E1/H-M1 environment — no new packages required)*
*(Note: scipy>=1.7.0 required for `stats.levene(..., center='median')` parameter)*

### Section 7.2: External Repositories (Reference Only)
- scipy/scipy — stats.levene (Brown-Forsythe: center='median')
- deepcharles/ruptures — PELT segment indexing (reused from H-E1)
- statsmodels — OLS piecewise regression F-test

---

## Phase 2C Completeness Check

| Item | Present in FRs | Location |
|------|---------------|----------|
| H-E1 outputs loaded (residual_cov, paper_count_star) | ✅ | FR-1 |
| Pre/post segment split at paper_count_star | ✅ | FR-2 |
| Brown-Forsythe test (center='median' mandatory) | ✅ | FR-3 |
| Variance ratio (post/pre, threshold < 1.0) | ✅ | FR-4 |
| Combined gate check (both conditions) | ✅ | FR-5 |
| Piecewise regression F-test (independent confirmation) | ✅ | FR-6 |
| Mechanism verification function | ✅ | FR-7 |
| Visualization (5 figures including mandatory gate chart) | ✅ | FR-8 |
| Results JSON output | ✅ | FR-9 |
| Early-fail guards (missing H-E1 data, empty segments) | ✅ | FR-1.5, FR-1.6 |
| One-tailed vs two-tailed interpretation | ✅ | FR-3.3 |
| center='median' enforcement (not center='mean') | ✅ | FR-3.2 |
