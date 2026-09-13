# Product Requirements Document: H-M3
# Post-Breakpoint CoV Directional Skewness Analysis (Goodhart Ceiling Specificity)

**Hypothesis:** H-M3 (MECHANISM / INCREMENTAL)
**Prerequisites:** H-E1 (VALIDATED), H-M1 (VALIDATED), H-M2 (VALIDATED)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md
**Gate:** SHOULD_WORK

---

## Executive Summary

Implement and validate directional skewness analysis to determine whether post-breakpoint residual CoV is concentrated downward (consistent with Goodhart ceiling pressure) rather than symmetrically reduced (general convergence). H-M2 confirmed 5× variance compression (variance_ratio=0.1981, BF p=0.0099). H-M3 asks: is this compression directional (ceiling saturation) or symmetric (general convergence)?

**Gate (SHOULD_WORK):** At least 2 of 4 directional metrics consistent with Goodhart ceiling compression. Failure response: EXPLORE — variance reduction real (H-M2 confirmed) but distributional shape does not confirm ceiling pressure specifically.

---

## Problem Statement

Post-breakpoint variance compression is confirmed (H-M2 PASS). The mechanism question: is the compression directional (values pile at lower end = ceiling optimization pressure) or symmetric (general regression-to-mean convergence)? Distinguishing these distinguishes Goodhart saturation from benign standardization.

**Current State:** Post-segment variance confirmed 5× lower than pre-segment (H-M2 PASS). Distributional shape not yet analyzed.

**Desired State:** Post-segment residual CoV shows directional lower-tail concentration (negative skew shift, 10th percentile below pre-segment 10th percentile, Mann-Whitney stochastic dominance pre > post), confirming ceiling pressure mechanism.

---

## Functional Requirements

### FR-1: Load H-E1/H-M2 Outputs
- **FR-1.1:** Load residual_cov series from H-E1 output: `data/pwc_cov_computed.csv` (columns: benchmark_name, paper_count, cov, residual_cov); sort by paper_count ascending
- **FR-1.2:** Load paper_count_star (integer) from H-E1 experiment_results.json (`docs/youra_research/h-e1/experiment_results.json`); if not present, recompute with ruptures PELT (same params as H-E1)
- **FR-1.3:** Validate: len(residual_cov) == 111
- **FR-1.4:** Validate: paper_count_star is not a boundary value (not min or max of paper_count)
- **FR-1.5:** Early-fail with clear message if paper_count_star not recoverable: "H-E1 paper_count* required — run H-E1 first"
- **FR-1.6:** Early-fail if len(pre_segment) < 3 OR len(post_segment) < 3

### FR-2: Pre/Post Segment Split
- **FR-2.1:** Split: `pre_segment = residual_cov[paper_count < paper_count_star]`, `post_segment = residual_cov[paper_count >= paper_count_star]`
- **FR-2.2:** Record n_pre = len(pre_segment), n_post = len(post_segment); validate n_pre + n_post == 111
- **FR-2.3:** Log: `"Segments: n_pre={n_pre}, n_post={n_post}"`

### FR-3: Distributional Moments (Both Segments)
- **FR-3.1:** Compute `scipy.stats.describe(pre_segment, bias=False)` → desc_pre (nobs, minmax, mean, variance, skewness, kurtosis)
- **FR-3.2:** Compute `scipy.stats.describe(post_segment, bias=False)` → desc_post
- **FR-3.3:** `bias=False` MANDATORY — applies adjusted Fisher-Pearson G1 (appropriate for small N)
- **FR-3.4:** Log: `"Skewness pre={desc_pre.skewness:.4f}, post={desc_post.skewness:.4f}"`
- **FR-3.5:** Log: `"Kurtosis pre={desc_pre.kurtosis:.4f}, post={desc_post.kurtosis:.4f}"`

### FR-4: Skewness Direction Check (Metric 1)
- **FR-4.1:** skew_pre = desc_pre.skewness, skew_post = desc_post.skewness
- **FR-4.2:** Directional criterion: skew_post < skew_pre (post more negatively skewed = downward concentration)
- **FR-4.3:** Alternatively: skew_post negative (post values concentrated below median)
- **FR-4.4:** metric1_pass = (skew_post < skew_pre) OR (skew_post < 0)
- **FR-4.5:** Log: `"Metric 1 (skewness direction): skew_pre={skew_pre:.4f}, skew_post={skew_post:.4f}, pass={metric1_pass}"`

### FR-5: 10th Percentile Lower-Tail Concentration (Metric 2)
- **FR-5.1:** p10_pre = np.percentile(pre_segment, 10)
- **FR-5.2:** p10_post = np.percentile(post_segment, 10)
- **FR-5.3:** metric2_pass = (p10_post < p10_pre)
- **FR-5.4:** Log: `"Metric 2 (lower tail): p10_pre={p10_pre:.4f}, p10_post={p10_post:.4f}, pass={metric2_pass}"`

### FR-6: Permutation Test on Skewness Difference (Metric 3)
- **FR-6.1:** Define statistic: `skew_diff_stat(x, y, axis=0) = scipy.stats.skew(y, axis=axis) - scipy.stats.skew(x, axis=axis)`
- **FR-6.2:** Execute `scipy.stats.permutation_test((pre_segment, post_segment), skew_diff_stat, permutation_type='independent', n_resamples=9999, alternative='two-sided', random_state=42)`
- **FR-6.3:** metric3_pass = (perm_result.pvalue < 0.10) (SHOULD_WORK threshold)
- **FR-6.4:** Log: `"Metric 3 (perm test skewness diff): p={perm_result.pvalue:.4f}, pass={metric3_pass}"`

### FR-7: Mann-Whitney U Stochastic Dominance (Metric 4)
- **FR-7.1:** Execute `scipy.stats.mannwhitneyu(pre_segment, post_segment, alternative='greater')` (H1: pre > post stochastically)
- **FR-7.2:** metric4_pass = (mw_result.pvalue < 0.10)
- **FR-7.3:** Log: `"Metric 4 (Mann-Whitney, pre>post): p={mw_result.pvalue:.4f}, pass={metric4_pass}"`

### FR-8: Gate Check (SHOULD_WORK)
- **FR-8.1:** metrics_passed = sum([metric1_pass, metric2_pass, metric3_pass, metric4_pass])
- **FR-8.2:** gate_passed = (metrics_passed >= 2)
- **FR-8.3:** Log: `"GATE: {'PASS' if gate_passed else 'EXPLORE'} — {metrics_passed}/4 directional metrics consistent with H1"`
- **FR-8.4:** On EXPLORE: log "Variance reduction real (H-M2) but distributional shape does not confirm ceiling specificity; document as scope limitation"

### FR-9: Mechanism Verification
- **FR-9.1:** Implement `verify_directional_specificity(results)` returning (gate_passed, metrics_dict)
- **FR-9.2:** metrics_dict: {metric1_skew_direction, metric2_lower_tail, metric3_perm_skew, metric4_mann_whitney}
- **FR-9.3:** gate_passed = metrics_passed >= 2
- **FR-9.4:** Log full verification summary

### FR-10: Visualization
- **FR-10.1 (MANDATORY):** Gate metrics comparison bar chart — all 4 metrics with pass/fail coloring, metrics_passed count annotation
- **FR-10.2:** Histogram overlay — pre vs post residual_CoV (same x-axis, semi-transparent, KDE overlay, vertical line at p10 for each)
- **FR-10.3:** Distribution moments table figure — mean, variance, skewness, kurtosis side-by-side for pre and post (matplotlib table or bar pairs)
- **FR-10.4:** Empirical CDF — pre vs post residual_CoV (highlight lower-tail region p10-p25 with shaded region)
- **FR-10.5:** Q-Q plot — pre-segment vs post-segment quantiles (deviation from diagonal shows directional asymmetry)
- **FR-10.6:** Save all figures to `docs/youra_research/h-m3/figures/`

### FR-11: Results Output
- **FR-11.1:** Save `docs/youra_research/h-m3/experiment_results.json` with all metrics
- **FR-11.2:** JSON schema: {n_pre, n_post, skew_pre, skew_post, kurt_pre, kurt_post, p10_pre, p10_post, perm_p_skew_diff, mw_pvalue, metric1_pass, metric2_pass, metric3_pass, metric4_pass, metrics_passed, gate_passed, gate_type}
- **FR-11.3:** Print gate verdict to stdout

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- **NFR-1.1:** random_state=42 for permutation test
- **NFR-1.2:** Fully deterministic given fixed paper_count_star from H-E1

### NFR-2: Performance
- **NFR-2.1:** Full pipeline completes in < 30 seconds on CPU (N=111, permutation 9999 resamples)
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
| residual_cov | float array | H-E1 derive.py output | OLS-detrended CoV, N=111 |
| paper_count_star | int | H-E1 experiment_results.json | Breakpoint split value |
| pre_segment | float array | residual_cov[paper_count < paper_count_star] | Pre-breakpoint observations |
| post_segment | float array | residual_cov[paper_count >= paper_count_star] | Post-breakpoint observations |

### H-E1/H-M1/H-M2 Output Reference
- `docs/youra_research/h-e1/code/` — ingest_pwc.py, derive.py, pipeline.py
- `docs/youra_research/h-e1/experiment_results.json` — contains paper_count_star
- `docs/youra_research/h-m2/code/` — reference segment split and variance comparison implementation
- `docs/youra_research/h-m2/experiment_results.json` — variance_ratio=0.1981 confirmed (context only)

---

## Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| metric1 (skewness direction) | skew_post < skew_pre OR skew_post < 0 | Directional |
| metric2 (lower tail) | p10_post < p10_pre | Directional |
| metric3 (permutation p) | < 0.10 | Statistical |
| metric4 (Mann-Whitney p) | < 0.10 | Statistical |
| metrics_passed | >= 2 | PRIMARY GATE |
| Code runs without error | True | PoC prerequisite |

**PASS:** metrics_passed >= 2 (SHOULD_WORK gate)
**EXPLORE:** metrics_passed < 2 — variance reduction real but not directional; document as scope limitation

---

## Section 7: Dependencies

### Section 7.1: Python Packages
```
scipy>=1.9.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```
*(scipy>=1.9.0 required for `scipy.stats.permutation_test` with vectorized statistic)*
*(All other packages inherited from H-E1/H-M2 environment — no new packages required)*

### Section 7.2: External Repositories (Reference Only)
- scipy/scipy — stats.describe, stats.skew, stats.permutation_test, stats.mannwhitneyu
- deepcharles/ruptures — PELT (H-E1 reuse; paper_count* pre-computed)

---

## Phase 2C Completeness Check

| Item | Present in FRs | Location |
|------|---------------|----------|
| H-E1 outputs loaded (residual_cov, paper_count_star) | ✅ | FR-1 |
| Pre/post segment split at paper_count_star | ✅ | FR-2 |
| Distributional moments (describe, bias=False) | ✅ | FR-3 |
| Skewness direction metric | ✅ | FR-4 |
| Lower-tail (10th percentile) concentration metric | ✅ | FR-5 |
| Permutation test on skewness difference | ✅ | FR-6 |
| Mann-Whitney stochastic dominance test | ✅ | FR-7 |
| Combined SHOULD_WORK gate (≥2 of 4 metrics) | ✅ | FR-8 |
| Mechanism verification function | ✅ | FR-9 |
| Visualization (5 figures + mandatory gate chart) | ✅ | FR-10 |
| Results JSON output | ✅ | FR-11 |
| Early-fail guards | ✅ | FR-1.5, FR-1.6 |
| bias=False enforcement (adjusted G1) | ✅ | FR-3.3 |
| random_state=42 (reproducibility) | ✅ | FR-6.2 |
| EXPLORE failure response documented | ✅ | FR-8.4 |
