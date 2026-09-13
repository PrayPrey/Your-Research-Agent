# Product Requirements Document: H-M2

**Hypothesis:** Convergence creates implicit evaluation standards
**Type:** MECHANISM
**Date:** 2026-08-10
**Version:** 1.0

---

## Executive Summary

This experiment tests whether high benchmark concentration (measured by HHI) predicts higher adoption of "standard" benchmarks by new papers. If true, this demonstrates that community convergence creates implicit evaluation norms that influence researcher behavior.

**Core Question:** Does prior-year HHI predict current-year standard benchmark adoption?

---

## Problem Statement

H-M1 established that HHI correctly indicates benchmark concentration. H-M2 extends this by testing the causal mechanism: do concentrated evaluation landscapes actually influence individual paper benchmark choices?

**Gate Condition:** SHOULD_WORK
- Pass: β(prior_HHI) > 0, p < 0.05
- Fail: Document as limitation, explore direct norm measurement

---

## Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: PWC Data Loading**
- Load Papers With Code archive from `paperswithcode/paperswithcode-data`
- Parse papers-with-abstracts.json and datasets.json
- Filter to NeurIPS, ICML, ICLR (2018-2024)
- Expected: ~80,000+ papers across 21 venue-years

**FR-1.2: HHI Integration**
- Load H-E1 HHI results from `h-e1/04_validation.md` or recompute
- Merge prior-year HHI with current-year papers
- Validation: 21 venue-year HHI values available

### FR-2: Standard Benchmark Classification

**FR-2.1: Standard Dataset Identification**
- For each venue-year: identify top-5 datasets by usage count in prior year
- These constitute "standard" benchmarks for that venue-year
- Store mapping: {venue, year} → {standard_datasets}

**FR-2.2: Paper Labeling**
- For each paper: check if ANY used dataset is in standard set
- Binary label: standard_benchmark_used (1 if yes, 0 if no)
- Expected distribution: ~60-80% standard adoption

### FR-3: Model Implementation

**FR-3.1: Baseline Model (No HHI)**
- Logistic regression: P(standard) ~ 1
- Purpose: Establish base adoption rate

**FR-3.2: Proposed Model (With HHI)**
- Logistic regression: P(standard) ~ prior_HHI
- Extract: β coefficient, p-value, odds ratio
- 95% confidence intervals required

**FR-3.3: Controlled Model**
- Logistic regression: P(standard) ~ prior_HHI + venue_dummies
- Controls for venue-specific effects
- Compare coefficient stability

### FR-4: Evaluation Metrics

**FR-4.1: Primary Metrics**
- β(prior_HHI): Coefficient value
- p-value: Statistical significance
- Odds Ratio: exp(β) interpretation
- 95% CI for coefficient

**FR-4.2: Model Diagnostics**
- McFadden pseudo-R²
- Log-likelihood ratio test
- Hosmer-Lemeshow goodness of fit

### FR-5: Visualization

**FR-5.1: Required Figure**
- Gate metrics comparison: β with 95% CI, p-value annotation
- Save to: `h-m2/figures/gate_metrics.png`

**FR-5.2: Additional Figures**
- HHI vs adoption rate scatter by venue
- Predicted probability curve across HHI range
- Model comparison table (baseline vs controlled)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42
- All data processing steps logged
- Environment: Python 3.10+, statsmodels, pandas, scipy

### NFR-2: Statistical Rigor
- Minimum 500+ papers per analysis (already satisfied by dataset size)
- Report exact p-values, not just significance stars
- Include effect sizes with confidence intervals

### NFR-3: Data Quality
- Handle missing venue/year gracefully
- Log papers excluded and reasons
- Validate HHI range [0, 1]

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate Pass | β > 0 AND p < 0.05 | Primary hypothesis test |
| Effect Meaningful | OR > 1.5 | Practical significance |
| Robust to Controls | β sign stable | Controlled model check |

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| H-E1 HHI data | h-e1/04_validation.md | COMPLETED |
| H-M1 validation | h-m1/04_validation.md | COMPLETED |
| PWC archive | GitHub | External |

---

## Out of Scope

- Temporal dynamics (year-over-year trends)
- Individual paper content analysis
- Author-level effects
- Citation impact analysis

---

## Appendix: Data Schema

### Paper Record
```python
{
    'paper_id': str,
    'venue': str,  # NeurIPS, ICML, ICLR
    'year': int,   # 2018-2024
    'datasets_used': List[str],
    'standard_benchmark': int,  # 0 or 1
    'prior_hhi': float  # 0.0 - 1.0
}
```

### Analysis Output
```python
{
    'beta_hhi': float,
    'p_value': float,
    'odds_ratio': float,
    'ci_lower': float,
    'ci_upper': float,
    'n_papers': int,
    'n_venue_years': int
}
```
