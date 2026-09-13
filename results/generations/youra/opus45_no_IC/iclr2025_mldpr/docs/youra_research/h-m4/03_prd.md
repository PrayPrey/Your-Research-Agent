# Product Requirements Document: H-M4

**Hypothesis:** Reduced diversity hides benchmark-specific overfitting
**Type:** MECHANISM
**Date:** 2026-08-10
**Version:** 1.0

---

## Executive Summary

This experiment tests whether low benchmark diversity (entropy) correlates with high cross-benchmark performance variance. If papers evaluated on few benchmarks show higher variance when tested across multiple benchmarks, this demonstrates that concentrated evaluation hides benchmark-specific overfitting.

**Core Question:** Do venue-years with low entropy show higher cross-benchmark variance?

---

## Problem Statement

H-M3 established that citation-linked papers have 23x higher benchmark overlap (Cohen's d = 1.93). H-M4 extends this by testing the harm mechanism: does reduced diversity actually hide overfitting?

**Gate Condition:** SHOULD_WORK
- Pass: Spearman ρ < 0 with p < 0.05 AND effect in ≥2/3 venues
- Fail: Document as limitation, proceed to H-M5

---

## Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: PWC Data Loading**
- Load Papers With Code archive from `pwc-archive/papers-with-abstracts`
- Filter to NeurIPS, ICML, ICLR (2018-2024)
- Extract paper IDs, venues, years, benchmark results
- Expected: ~12,000 papers total

**FR-1.2: Multi-Benchmark Paper Selection**
- Filter to papers with results on 2+ benchmarks
- Same task type required (e.g., image classification)
- Reported metrics available in PWC
- Expected: 500-1,200 papers (5-10% of total)

**FR-1.3: Entropy Data from H-E1**
- Load HHI/entropy values per venue-year from H-E1 results
- 21 venue-year combinations (3 venues × 7 years)
- Use Shannon entropy or inverse HHI as diversity metric

### FR-2: Cross-Benchmark Variance Computation

**FR-2.1: Metric Normalization**
- Normalize all metrics to [0, 1] range
- Accuracy already 0-1, others need min-max scaling
- Handle metric direction (higher-is-better vs lower-is-better)

**FR-2.2: Paper-Level Variance**
```python
def compute_cross_benchmark_variance(paper):
    """Coefficient of variation as scale-invariant variance proxy."""
    benchmarks = paper['benchmark_results']
    if len(benchmarks) < 2:
        return None
    normalized = normalize_metrics(benchmarks)
    values = [m['normalized_score'] for m in normalized]
    cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
    return cv
```

**FR-2.3: Venue-Year Aggregation**
- Group papers by (venue, year)
- Compute mean CV per venue-year
- Minimum 10 papers per venue-year for inclusion

### FR-3: Statistical Analysis

**FR-3.1: Spearman Correlation**
- Test correlation between entropy and variance
- Variables: entropy_by_venue_year vs variance_by_venue_year
- Expected direction: ρ < 0 (negative correlation)

**FR-3.2: Per-Venue Analysis**
- Compute Spearman correlation within each venue
- Minimum 3 venue-years per venue for computation
- Secondary criterion: effect in ≥2/3 venues

**FR-3.3: Descriptive Statistics**
- Mean, median, std for variance by entropy quartile
- Sample sizes per venue-year
- Distribution statistics

### FR-4: Evaluation Metrics

**FR-4.1: Primary Metrics (Gate)**
| Metric | Threshold | Description |
|--------|-----------|-------------|
| Spearman ρ | < 0 | Negative correlation required |
| p-value | < 0.05 | Statistical significance |
| Venue coverage | ≥ 2/3 | Effect in at least 2 venues |

**FR-4.2: Secondary Metrics**
| Metric | Purpose |
|--------|---------|
| N venue-years | Sample size (expect 21) |
| N multi-bench papers | Per venue-year counts |
| Per-venue ρ | Individual venue correlations |

### FR-5: Visualization

**FR-5.1: Required Figure (Gate)**
- Scatter plot: entropy vs cross-benchmark variance
- Regression line with confidence band
- Color-coded by venue
- Annotation: ρ, p-value
- Save to: `h-m4/figures/gate_metrics.png`

**FR-5.2: Additional Figures**
1. **entropy_variance_scatter.png**: Detailed scatter with venue markers
2. **per_venue_correlation.png**: Bar chart of ρ per venue
3. **variance_by_entropy_quartile.png**: Box plots by entropy quartile

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42
- All intermediate data cached
- Environment: Python 3.10+, scipy, numpy, pandas, matplotlib

### NFR-2: Statistical Rigor
- Minimum 500 multi-benchmark papers
- Report exact p-values
- Include effect sizes and confidence intervals

### NFR-3: Data Quality
- Log papers with insufficient benchmarks (excluded)
- Validate CV range ≥ 0
- Handle missing/malformed metrics gracefully

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate Pass | ρ < 0, p < 0.05, 2/3 venues | Primary hypothesis test |
| Sample Size | ≥ 500 papers | Sufficient statistical power |
| Effect Direction | Negative correlation | Low entropy → high variance |

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| H-M3 validation | h-m3/04_validation.md | COMPLETED |
| H-E1 entropy data | h-e1/results/ | COMPLETED |
| PWC archive | HuggingFace cache | External |

---

## Out of Scope

- Model retraining or new benchmarks
- Causal inference beyond correlation
- Paper quality assessment
- Temporal dynamics within years

---

## Appendix: Data Schema

### Paper Record
```python
{
    'paper_id': str,
    'venue': str,           # NeurIPS, ICML, ICLR
    'year': int,            # 2018-2024
    'benchmark_results': List[{
        'benchmark': str,
        'metric_name': str,
        'metric_value': float,
        'higher_is_better': bool,
    }],
}
```

### Venue-Year Record
```python
{
    'venue': str,
    'year': int,
    'entropy': float,        # From H-E1
    'mean_cv': float,        # Cross-benchmark variance
    'n_papers': int,
    'paper_ids': List[str],
}
```

### Analysis Output
```python
{
    'spearman_rho': float,
    'p_value': float,
    'n_venue_years': int,
    'per_venue': {
        'NeurIPS': {'rho': float, 'p': float, 'n': int},
        'ICML': {'rho': float, 'p': float, 'n': int},
        'ICLR': {'rho': float, 'p': float, 'n': int},
    },
    'hypothesis_supported': bool,
}
```
