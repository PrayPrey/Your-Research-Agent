# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Popular benchmarks attract intensive architecture and hyperparameter search investment
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM (Bibliometric Study) Template** - Validates causal mechanism via publication analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASS)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition

| Gate Type | Pass Condition | Fail Action |
|-----------|----------------|-------------|
| MUST_WORK | High-use datasets have 3:1 more optimization papers | PIVOT: Alternative intensity metrics |

---

## Continuation Context

Building on h-e1 validation which confirmed popularity-gap correlation exists (CIFAR-10 gap=18.86%, SVHN gap=-2.35%, gap difference=21.21%). Now testing whether this gap is caused by differential optimization investment.

### Previous Hypothesis Results (h-e1)

| Metric | Value |
|--------|-------|
| CIFAR-10 generalization gap | 18.86% |
| SVHN generalization gap | -2.35% |
| Gap difference | 21.21% |
| Cohen's d | > 0.3 (PASS) |
| Direction check | True |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP tools unavailable in this session. Research synthesized from Phase 2B documentation.

Key patterns from ML benchmarking literature:
1. **OpenML API** provides run counts per dataset
2. **Semantic Scholar API** enables paper search with dataset mentions
3. **Bibliometric analysis** standard methodology: count papers mentioning specific datasets in title/abstract

### Archon Code Examples

Standard bibliometric pipeline pattern:
```python
# Pattern: API-based paper counting
papers = semantic_scholar.search(query=f'"{dataset_name}" architecture OR NAS OR hyperparameter')
count = len([p for p in papers if is_optimization_paper(p)])
```

### Exa GitHub Implementations

**Note:** MCP tools unavailable. Using established bibliometric methods.

Reference implementations:
1. **OpenML-Python library**: `openml.datasets.list_datasets()` with run counts
2. **Semantic Scholar API**: `https://api.semanticscholar.org/graph/v1/paper/search`
3. **Papers With Code API**: Dataset mention counts

### Implementation Priority Assessment

**CRITICAL: This is a bibliometric study, not a model training experiment**

**Recommended Implementation Path:**
- Primary: OpenML API + Semantic Scholar API
- Fallback: Manual paper counting via Google Scholar
- Justification: OpenML has authoritative run counts; Semantic Scholar has free API

### Code Analysis (Serena MCP)

**Note:** MCP tools unavailable. Implementation uses standard REST APIs.

---

## Experiment Specification

### Dataset

**This hypothesis uses dataset metadata, not dataset contents.**

| Component | Specification |
|-----------|---------------|
| **Type** | programmatic-api |
| **Source** | OpenML API |
| **High-use datasets** | Top-10 by run-rate in image classification |
| **Low-use datasets** | Bottom-10 by run-rate in image classification |
| **Minimum samples** | 20 datasets total (10 high-use + 10 low-use) |

**Loading Information** (for Phase 4):
- Method: openml-python
- Identifier: `openml.datasets.list_datasets()`
- Code:
```python
import openml
datasets = openml.datasets.list_datasets(output_format='dataframe')
image_datasets = datasets[datasets['format'] == 'image']
sorted_by_runs = image_datasets.sort_values('runs', ascending=False)
high_use = sorted_by_runs.head(10)
low_use = sorted_by_runs.tail(10)
```

### Models

#### Baseline Model

**N/A - This is a bibliometric study, not model training.**

No model training required. Baseline comparison is between high-use and low-use dataset groups.

#### Proposed Model

**N/A - Analysis method, not ML model.**

**Core Mechanism Implementation:**

```python
# Core bibliometric analysis (20-30 lines)

import openml
import requests
from collections import defaultdict

def get_openml_datasets():
    """Fetch image classification datasets sorted by run count."""
    datasets = openml.datasets.list_datasets(output_format='dataframe')
    # Filter for image/vision datasets
    vision_keywords = ['cifar', 'mnist', 'imagenet', 'svhn', 'fashion']
    is_vision = datasets['name'].str.lower().str.contains('|'.join(vision_keywords))
    return datasets[is_vision].sort_values('NumberOfInstances', ascending=False)

def count_optimization_papers(dataset_name):
    """Count papers about architecture/hyperparameter optimization for dataset."""
    query = f'"{dataset_name}" AND (architecture OR NAS OR hyperparameter OR tuning)'
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": 100, "fields": "title,year"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('total', 0)
    return 0

def compute_optimization_ratio(high_use_datasets, low_use_datasets):
    """Compute ratio of optimization papers between high-use and low-use datasets."""
    high_counts = [count_optimization_papers(d) for d in high_use_datasets]
    low_counts = [count_optimization_papers(d) for d in low_use_datasets]
    
    avg_high = sum(high_counts) / len(high_counts)
    avg_low = sum(low_counts) / len(low_counts) if sum(low_counts) > 0 else 1
    
    return {
        'high_use_avg': avg_high,
        'low_use_avg': avg_low,
        'ratio': avg_high / avg_low,
        'pass_gate': (avg_high / avg_low) >= 3.0
    }
```

### Training Protocol

**N/A - No model training required.**

This hypothesis uses API queries only:
1. Query OpenML for dataset run counts
2. Select top-10 and bottom-10 datasets by run count
3. Query Semantic Scholar for paper counts per dataset
4. Compute ratio and statistical significance

### Evaluation

| Metric | Description | Pass Threshold |
|--------|-------------|----------------|
| **Optimization paper ratio** | avg(high-use papers) / avg(low-use papers) | >= 3.0 |
| **Statistical significance** | Mann-Whitney U test p-value | < 0.05 |
| **Consistency** | Trend direction across domains | Positive |

**Metrics Loading Information**:
- Task Type: bibliometric-analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import mannwhitneyu
stat, p_value = mannwhitneyu(high_use_paper_counts, low_use_paper_counts, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing average optimization papers for high-use vs low-use datasets with 3:1 threshold line

#### Additional Figures (LLM Autonomous)

1. **Per-dataset paper counts**: Grouped bar chart for all 20 datasets
2. **Ratio distribution**: Box plot of paper count distributions for high-use vs low-use groups
3. **Correlation plot**: Run count vs optimization paper count scatter plot

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (API queries complete)
2. `optimization_ratio >= 3.0`

---

## Appendix: Reference Implementations

### OpenML API Documentation
- Official: https://openml.github.io/openml-python/
- Dataset listing: `openml.datasets.list_datasets()`
- Run counts available in dataset metadata

### Semantic Scholar API Documentation
- Official: https://api.semanticscholar.org/api-docs/
- Paper search endpoint: `/graph/v1/paper/search`
- Rate limit: 100 requests/5 minutes (free tier)

### Alternative APIs
- Papers With Code: https://paperswithcode.com/api/v1/
- Google Scholar (via scholarly): https://github.com/scholarly-python-package/scholarly

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

| Timestamp | Event | Phase | Details |
|-----------|-------|-------|---------|
| 2026-08-19T03:34:56 | Status set to IN_PROGRESS | Hypothesis Loop | Starting Phase 2C → 3 → 4 for h-m1 |
| 2026-08-19 | h-e1 PASS | Phase 4 | Prerequisite satisfied |

---

*Research synthesized from Phase 2B documentation (MCP tools unavailable)*
*All specifications grounded in standard bibliometric methods*
*Next Phase: Phase 3 - Implementation Planning*
