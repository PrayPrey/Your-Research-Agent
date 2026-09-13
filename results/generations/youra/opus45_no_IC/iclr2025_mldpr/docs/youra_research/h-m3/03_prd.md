# Product Requirements Document: H-M3

**Hypothesis:** Papers follow standards for comparability - if authors cite prior work, they use same benchmarks as cited papers
**Type:** MECHANISM
**Date:** 2026-08-10
**Version:** 1.0

---

## Executive Summary

This experiment tests whether citation relationships predict benchmark dataset overlap. If citing papers use the same datasets as their cited papers more often than random pairs, this demonstrates that comparability requirements drive benchmark homogeneity through citation networks.

**Core Question:** Do citing-cited paper pairs have higher dataset overlap (Jaccard) than random pairs?

---

## Problem Statement

H-M2 established that high HHI predicts standard benchmark adoption (β=56.75, p<0.001). H-M3 extends this by testing the mechanism: do papers follow their citations when choosing evaluation benchmarks?

**Gate Condition:** SHOULD_WORK
- Pass: Mann-Whitney U p < 0.01 AND Cohen's d > 0.3
- Fail: Document as limitation, proceed to H-M4

---

## Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: PWC Data Loading**
- Load Papers With Code archive from `pwc-archive/papers-with-abstracts` (HuggingFace)
- Filter to NeurIPS, ICML, ICLR (2018-2024)
- Extract paper IDs, venues, years, dataset tags
- Expected: ~12,000 papers

**FR-1.2: Semantic Scholar Citation Data**
- Query S2 API for intra-venue citations
- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/{id}/citations`
- Filter to papers within our PWC scope
- Expected: ~50,000+ citation pairs
- API Key: `S2_API_KEY` environment variable

**FR-1.3: Citation Pair Construction**
- Build citing→cited pairs within venue-years
- Both papers must have dataset tags in PWC
- Store: (citing_id, cited_id, citing_datasets, cited_datasets)

### FR-2: Overlap Computation

**FR-2.1: Jaccard Similarity**
```python
def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0
```

**FR-2.2: Citing Pair Overlap**
- For each citation pair: compute Jaccard of dataset sets
- Aggregate across all venue-years
- Store distribution: citing_overlaps[]

**FR-2.3: Random Pair Baseline**
- For each venue-year: sample N random pairs (N = citation pair count)
- Compute Jaccard for random pairs
- Store distribution: random_overlaps[]

### FR-3: Statistical Analysis

**FR-3.1: Mann-Whitney U Test**
- Compare citing_overlaps vs random_overlaps
- Alternative: 'greater' (citing > random)
- Extract: U statistic, p-value

**FR-3.2: Effect Size (Cohen's d)**
```python
pooled_std = sqrt((var(citing) + var(random)) / 2)
cohens_d = (mean(citing) - mean(random)) / pooled_std
```

**FR-3.3: Descriptive Statistics**
- Mean, median, std for both distributions
- Sample sizes (n_citing, n_random)
- Histogram bins

### FR-4: Evaluation Metrics

**FR-4.1: Primary Metrics (Gate)**
| Metric | Threshold | Description |
|--------|-----------|-------------|
| Mann-Whitney p-value | < 0.01 | Citing > random (one-tailed) |
| Cohen's d | > 0.3 | Medium effect size |

**FR-4.2: Secondary Metrics**
| Metric | Purpose |
|--------|---------|
| Mean citing overlap | Average Jaccard for citation pairs |
| Mean random overlap | Average Jaccard for random pairs |
| N citing pairs | Sample size validation (≥1000) |
| N random pairs | Should equal N citing |

### FR-5: Visualization

**FR-5.1: Required Figure (Gate)**
- Bar chart: mean Jaccard overlap for citing vs random
- Error bars: 95% CI
- Annotation: p-value, Cohen's d
- Save to: `h-m3/figures/gate_metrics.png`

**FR-5.2: Additional Figures**
1. **Overlap Distribution**: Side-by-side histograms (citing vs random)
2. **Venue-Year Heatmap**: Effect size per venue-year cell
3. **Citation Depth**: Overlap by citation distance (if time permits)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42
- All API responses cached locally
- Environment: Python 3.10+, scipy, numpy, pandas, requests

### NFR-2: Statistical Rigor
- Minimum 1000 citation pairs for analysis
- Report exact p-values (not stars)
- Include effect sizes with interpretation

### NFR-3: API Rate Limiting
- S2 API: 100 requests/second with key
- Implement exponential backoff
- Cache all responses to `h-m3/cache/`

### NFR-4: Data Quality
- Log papers without dataset tags (excluded)
- Validate Jaccard range [0, 1]
- Handle missing S2 records gracefully

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate Pass | p < 0.01 AND d > 0.3 | Primary hypothesis test |
| Sample Size | ≥ 1000 pairs | Sufficient statistical power |
| Effect Direction | mean_citing > mean_random | Confirms hypothesis direction |

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| H-M2 validation | h-m2/04_validation.md | COMPLETED |
| PWC archive | HuggingFace | External |
| Semantic Scholar API | api.semanticscholar.org | External (requires key) |

---

## Out of Scope

- Multi-hop citation analysis (2+ degree)
- Temporal dynamics within papers
- Author network effects
- Dataset quality assessment

---

## Appendix: Data Schema

### Paper Record
```python
{
    'paper_id': str,        # S2 corpus ID
    'venue': str,           # NeurIPS, ICML, ICLR
    'year': int,            # 2018-2024
    'datasets': List[str],  # PWC dataset tags
}
```

### Citation Pair Record
```python
{
    'citing_id': str,
    'cited_id': str,
    'venue_year': str,
    'jaccard_overlap': float,
}
```

### Analysis Output
```python
{
    'mann_whitney_stat': float,
    'p_value': float,
    'mean_citing_overlap': float,
    'mean_random_overlap': float,
    'cohens_d': float,
    'n_citing_pairs': int,
    'n_random_pairs': int,
    'gate_passed': bool,
}
```
