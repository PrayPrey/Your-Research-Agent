# Product Requirements Document: H-M1

**Hypothesis:** High HHI indicates community convergence on few datasets
**Type:** MECHANISM (Validation)
**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Gate:** MUST_WORK

---

## Executive Summary

Validate that HHI concentration metric correctly indicates benchmark concentration by testing correlation with top-5 dataset share. This MECHANISM hypothesis confirms HHI interpretation is valid for ML benchmark concentration analysis before proceeding with causal chain.

---

## Problem Statement

### Background
H-E1 established HHI can be computed from PWC data (21 venue-years, mean HHI 0.0171). However, HHI validity for ML benchmark concentration is unproven. We must verify high HHI actually means "few datasets dominate" before using HHI as concentration proxy in downstream hypotheses.

### Objective
Prove HHI correlates with intuitive concentration measure (top-5 dataset share) with statistical significance.

---

## Functional Requirements

### FR-1: Data Loading (Reuse H-E1)
- **FR-1.1:** Load cached PWC data from H-E1 (`h-e1/data/pwc_papers_filtered.parquet`)
- **FR-1.2:** Fallback: Re-run HuggingFace load if cache unavailable
- **FR-1.3:** Load pre-computed HHI scores from H-E1 results

### FR-2: Top-5 Share Computation
- **FR-2.1:** For each venue-year, compute task category counts
- **FR-2.2:** Sort by count descending, sum top 5
- **FR-2.3:** Divide by total to get top-5 concentration ratio
- **FR-2.4:** Store as `top5_share` per venue-year

### FR-3: Group Split
- **FR-3.1:** Compute median HHI across 21 venue-years
- **FR-3.2:** Split into high-HHI group (>median) and low-HHI group (≤median)
- **FR-3.3:** Verify balanced split (~10-11 per group)

### FR-4: Statistical Tests
- **FR-4.1:** Mann-Whitney U test (non-parametric): high-HHI top5_share > low-HHI top5_share
- **FR-4.2:** One-sided test: alternative='greater'
- **FR-4.3:** Spearman rank correlation: HHI vs top5_share
- **FR-4.4:** Report p-values and correlation coefficient

### FR-5: Gate Evaluation
- **FR-5.1:** Primary gate: Mann-Whitney p < 0.05
- **FR-5.2:** Secondary criterion: Spearman ρ > 0.7
- **FR-5.3:** Return gate_passed boolean

### FR-6: Visualization
- **FR-6.1:** Bar chart: high-HHI vs low-HHI mean top-5 share with error bars
- **FR-6.2:** Scatter plot: HHI vs top-5 share, color by venue
- **FR-6.3:** Distribution comparison: side-by-side histograms
- **FR-6.4:** Save all figures to `h-m1/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete analysis in < 1 minute (21 data points only)
- Memory < 2GB (reusing cached data)

### NFR-2: Reproducibility
- Deterministic (no random seeds needed)
- All scipy.stats functions are deterministic
- Output includes exact test statistics

### NFR-3: Statistical Validity
- Mann-Whitney U: non-parametric, no normality assumption required
- Spearman: rank-based, robust to outliers
- Sample size: 21 (adequate for group comparison)

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Mann-Whitney p-value | < 0.05 (one-sided) | MUST |
| High-HHI mean > Low-HHI mean | True | MUST |
| Spearman ρ | > 0.7 | SHOULD |
| Spearman p-value | < 0.05 | SHOULD |

**Gate Logic:**
```python
results = validate_hhi_interpretation(venue_year_data)
if results['mann_whitney_p'] < 0.05:
    gate_status = "PASSED"
    proceed_to = "H-M2"
else:
    gate_status = "FAILED"
    action = "REASSESS HHI metric validity"
```

---

## Data Sources

| Source | Type | Identifier |
|--------|------|------------|
| PWC Data | Cached Parquet | `h-e1/data/pwc_papers_filtered.parquet` |
| HHI Scores | H-E1 Results | `h-e1/04_validation.md` or recompute |
| Fallback | HuggingFace | `pwc-archive/papers-with-abstracts` |

---

## Dependencies

- Python 3.8+
- pandas, numpy
- scipy.stats (mannwhitneyu, spearmanr)
- matplotlib/seaborn (visualization)
- H-E1 cached data (prerequisite)

---

## Out of Scope

- New data collection (use H-E1 cache)
- Alternative correlation methods (Pearson, Kendall)
- Bootstrap confidence intervals
- Multiple hypothesis correction

---

## Appendix: Statistical Methods

### Mann-Whitney U Test
Non-parametric test for difference between two independent samples. Tests whether high-HHI group consistently has higher top-5 share than low-HHI group.

### Spearman Rank Correlation
Measures monotonic relationship between HHI and top-5 share. ρ > 0.7 indicates strong positive correlation.

### Sample Size Adequacy
With n=21 split into two groups (~10-11 each), Mann-Whitney U has adequate power to detect medium-large effect sizes (Cohen's d > 0.8).
