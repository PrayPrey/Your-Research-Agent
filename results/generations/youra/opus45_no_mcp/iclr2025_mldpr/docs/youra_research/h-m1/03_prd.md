# Product Requirements Document: H-M1

**Hypothesis:** Popular benchmarks attract intensive architecture and hyperparameter search investment
**Date:** 2026-08-19
**Author:** Anonymous
**Type:** MECHANISM (Bibliometric Study)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for validating hypothesis H-M1: that popular machine learning benchmarks receive disproportionately more architecture and hyperparameter optimization research investment compared to less popular benchmarks.

**Key Deliverable:** Bibliometric analysis pipeline that queries OpenML and Semantic Scholar APIs to compare optimization paper counts between high-use and low-use image classification datasets.

**Success Criteria:** High-use datasets have ≥3:1 more optimization papers than low-use datasets with p<0.05 statistical significance.

---

## 2. Problem Statement

H-E1 confirmed that popular datasets (CIFAR-10) exhibit larger generalization gaps than unpopular datasets (SVHN). H-M1 tests the causal mechanism: whether this gap arises from differential optimization investment.

**Research Question:** Do popular benchmarks attract significantly more architecture and hyperparameter search papers?

---

## 3. Functional Requirements

### FR-1: OpenML Dataset Discovery
- Query OpenML API for image classification datasets
- Sort datasets by run count (number of experiments)
- Select top-10 (high-use) and bottom-10 (low-use) datasets
- Store dataset metadata (name, run_count, num_instances)

### FR-2: Semantic Scholar Paper Search
- For each dataset, query Semantic Scholar API
- Search terms: "{dataset_name}" AND (architecture OR NAS OR hyperparameter OR tuning)
- Extract paper counts per dataset
- Handle API rate limiting (100 req/5 min free tier)

### FR-3: Statistical Analysis
- Compute average paper count per group (high-use, low-use)
- Calculate optimization ratio: avg(high) / avg(low)
- Run Mann-Whitney U test for significance
- Output: ratio, p-value, pass/fail decision

### FR-4: Visualization Generation
- Bar chart: average optimization papers (high vs low) with 3:1 threshold line
- Grouped bar chart: per-dataset paper counts
- Box plot: paper count distributions
- Scatter plot: run count vs optimization papers correlation

### FR-5: Gate Evaluation
- Pass condition: ratio ≥ 3.0 AND p < 0.05
- Generate gate result report with metrics

---

## 4. Data Specification

### 4.1 Primary Data Source
| Component | Value |
|-----------|-------|
| Source | OpenML API |
| Type | Dataset metadata |
| Access | `openml.datasets.list_datasets()` |
| Format | DataFrame |

### 4.2 Secondary Data Source
| Component | Value |
|-----------|-------|
| Source | Semantic Scholar API |
| Type | Paper search results |
| Access | REST API (`/graph/v1/paper/search`) |
| Format | JSON |

### 4.3 Dataset Selection Criteria
- Domain: Image classification
- Filter: Vision keywords (cifar, mnist, imagenet, svhn, fashion)
- High-use: Top 10 by run count
- Low-use: Bottom 10 by run count
- Total: 20 datasets

**Note:** No manual data download required — all data accessed via API.

---

## 5. Evaluation Metrics

### 5.1 Primary Metrics
| Metric | Description | Threshold |
|--------|-------------|-----------|
| Optimization Ratio | avg(high_use) / avg(low_use) | ≥ 3.0 |
| Statistical Significance | Mann-Whitney U p-value | < 0.05 |

### 5.2 Secondary Metrics
| Metric | Description |
|--------|-------------|
| Consistency | Trend direction positive |
| Correlation | Spearman r between run_count and paper_count |

---

## 6. Non-Functional Requirements

### NFR-1: API Reliability
- Implement retry logic with exponential backoff
- Handle rate limiting gracefully
- Cache API responses to avoid redundant queries

### NFR-2: Reproducibility
- Log all API queries and responses
- Save intermediate results to files
- Document API versions used

### NFR-3: Performance
- Complete analysis within 30 minutes
- Handle potential API timeouts

---

## 7. Dependencies

### 7.1 Python Packages
```
openml>=0.12.0
requests>=2.28.0
scipy>=1.9.0
matplotlib>=3.6.0
seaborn>=0.12.0
pandas>=1.5.0
pyyaml>=6.0
```

### 7.2 External APIs
- OpenML API: https://openml.github.io/openml-python/
- Semantic Scholar API: https://api.semanticscholar.org/api-docs/

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| API Queries Complete | All 20 datasets queried successfully |
| Optimization Ratio | ≥ 3.0 |
| Statistical Significance | p < 0.05 |
| Figures Generated | 4 visualization files |
| Gate Result | PASS |

---

## 9. Out of Scope

- Model training (this is bibliometric analysis only)
- Manual paper review (automated API counting only)
- Citation analysis (paper count only, not citation metrics)
- Temporal analysis (aggregate counts, not trends over time)

---

## Appendix: Phase 2C Reference

Source: `h-m1/02c_experiment_brief.md`
Gate: MUST_WORK
Pass Condition: High-use datasets have 3:1 more optimization papers
Fail Action: PIVOT to alternative intensity metrics
