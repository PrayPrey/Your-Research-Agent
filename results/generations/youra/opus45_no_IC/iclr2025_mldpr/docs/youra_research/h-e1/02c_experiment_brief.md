# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** HHI concentration measurable from PWC data for NeurIPS/ICML/ICLR (2018-2024)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Critical foundation hypothesis

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
This is a MUST_WORK gate. If HHI cannot be computed from PWC data for all 21 venue-years (3 venues x 7 years), the entire verification pipeline stops and must pivot to alternative data sources (Semantic Scholar, OpenAlex).

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant HHI or market concentration implementations found in Archon KB. The knowledge base primarily contains ML model implementations rather than econometric analysis code.

### Archon Code Examples

No HHI-specific code examples available. Searched for "HHI concentration calculation pandas" - returned unrelated ML model examples.

### Exa GitHub Implementations

**Key Finding 1: Papers With Code Data Access**
- Official Python client: `paperswithcode-client` (PyPI)
- HuggingFace datasets available:
  - `pwc-archive/papers-with-abstracts` - All papers with metadata
  - `pwc-archive/evaluation-tables` - Benchmark evaluation data
  - `pwc-archive/datasets` - Dataset metadata
- API documentation: https://paperswithcode.com/api/v1/docs/

**Key Finding 2: HHI Calculation in Pandas**
Source: Stack Overflow + DOJ Antitrust Division
```python
# Standard HHI calculation
HHI = ((df[col].value_counts() / df[col].count()) ** 2).sum()
```
- HHI range: 0 to 10,000 (when using percentage shares)
- Or 0 to 1 (when using decimal shares)
- Market interpretation: <1500 competitive, 1500-2500 moderate, >2500 concentrated

**Key Finding 3: Merger Simulation HHI Analyzer**
Repository: `thanhan25/merger-simulation-hhi-analyzer`
- Production-ready HHI calculation with DOJ/FTC methodology
- BigQuery integration for large-scale analysis

### Implementation Priority Assessment

**CRITICAL: For this EXISTENCE hypothesis, use official PWC data sources**

- Primary: HuggingFace `pwc-archive` datasets (pre-processed, daily updates)
- Fallback: PWC REST API via `paperswithcode-client`
- Justification: HuggingFace datasets are bulk downloads, faster than API pagination

**Recommended Implementation Path:**
- Primary: `datasets.load_dataset("pwc-archive/papers-with-abstracts")` + `pwc-archive/evaluation-tables`
- Fallback: `PapersWithCodeClient().paper_list()` with venue filtering
- Justification: HuggingFace bulk download avoids API rate limits; evaluation-tables contains paper-dataset links

### Code Analysis (Serena MCP)

N/A - This is a statistics/data analysis experiment, not codebase modification. No local code to analyze.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | Papers With Code Dataset-Paper Links |
| **Type** | standard (programmatic-api) |
| **Source** | HuggingFace Hub / PWC API |
| **Version** | Daily snapshot (2026-08-10) |
| **Size** | ~200K+ papers with dataset tags |

**Splits:**
- Full dataset: All papers from NeurIPS, ICML, ICLR (2018-2024)
- No train/val/test split needed (observational analysis)

**Preprocessing:**
1. Filter papers by venue (NeurIPS, ICML, ICLR)
2. Filter by year (2018-2024)
3. Extract dataset tags per paper
4. Aggregate by venue-year

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `pwc-archive/papers-with-abstracts`, `pwc-archive/evaluation-tables`
- Code:
```python
from datasets import load_dataset

# Load papers with abstracts
papers = load_dataset("pwc-archive/papers-with-abstracts", split="train")

# Load evaluation tables (contains paper-dataset links)
eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train")

# Alternative: PWC Client API
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()
papers_page = client.paper_list(items_per_page=50)
```

### Models

#### Baseline Model

N/A - This is an EXISTENCE hypothesis validating data availability, not a model comparison. The "baseline" is whether we can successfully compute HHI scores.

**Loading Information** (for Phase 4 download):
- Method: N/A (statistical analysis, no model)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Econometric Analysis (Panel Data)

**Core Mechanism Implementation:**

```python
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def compute_hhi(dataset_counts: pd.Series) -> float:
    """
    Compute Herfindahl-Hirschman Index from dataset usage counts.
    
    HHI = sum(share_i^2) where share_i = count_i / total_count
    
    Returns HHI in range [0, 1] (decimal shares)
    Multiply by 10000 for DOJ/FTC scale [0, 10000]
    """
    total = dataset_counts.sum()
    if total == 0:
        return np.nan
    shares = dataset_counts / total
    hhi = (shares ** 2).sum()
    return hhi

def compute_entropy(dataset_counts: pd.Series) -> float:
    """
    Compute normalized Shannon entropy for evaluation diversity.
    
    H = -sum(p_i * log(p_i)) / log(N)
    
    Returns entropy in range [0, 1]
    """
    total = dataset_counts.sum()
    if total == 0:
        return np.nan
    shares = dataset_counts / total
    shares = shares[shares > 0]  # Remove zeros for log
    entropy = -np.sum(shares * np.log(shares))
    max_entropy = np.log(len(shares)) if len(shares) > 1 else 1
    return entropy / max_entropy if max_entropy > 0 else 0

def extract_venue_year_metrics(
    papers_df: pd.DataFrame,
    venues: list = ["NeurIPS", "ICML", "ICLR"],
    years: list = list(range(2018, 2025))
) -> pd.DataFrame:
    """
    Extract HHI and entropy for each venue-year combination.
    
    Args:
        papers_df: DataFrame with columns ['paper_id', 'venue', 'year', 'datasets']
        venues: List of venue names to filter
        years: List of years to include
    
    Returns:
        DataFrame with columns ['venue', 'year', 'hhi', 'entropy', 'n_papers', 'n_unique_datasets']
    """
    results = []
    
    for venue in venues:
        for year in years:
            # Filter papers for this venue-year
            mask = (papers_df['venue'] == venue) & (papers_df['year'] == year)
            subset = papers_df[mask]
            
            if len(subset) == 0:
                continue
            
            # Explode datasets (one row per paper-dataset pair)
            # Assuming 'datasets' column contains list of dataset names
            exploded = subset.explode('datasets')
            
            # Count dataset usage
            dataset_counts = exploded['datasets'].value_counts()
            
            # Compute metrics
            hhi = compute_hhi(dataset_counts)
            entropy = compute_entropy(dataset_counts)
            
            results.append({
                'venue': venue,
                'year': year,
                'hhi': hhi,
                'entropy': entropy,
                'n_papers': len(subset),
                'n_unique_datasets': len(dataset_counts)
            })
    
    return pd.DataFrame(results)

def validate_hhi_scores(metrics_df: pd.DataFrame) -> Tuple[bool, Dict]:
    """
    Validate that all 21 venue-years have valid HHI scores.
    
    Success criteria:
    - 21/21 venue-years have non-null HHI
    - All HHI values in range [0, 1]
    - HHI variance > 0 (not all identical)
    
    Returns:
        (success: bool, details: dict)
    """
    expected_count = 21  # 3 venues x 7 years
    
    valid_hhi = metrics_df['hhi'].notna()
    valid_count = valid_hhi.sum()
    
    in_range = ((metrics_df['hhi'] >= 0) & (metrics_df['hhi'] <= 1)).all()
    variance = metrics_df['hhi'].var()
    
    success = (valid_count == expected_count) and in_range and (variance > 0)
    
    details = {
        'valid_count': int(valid_count),
        'expected_count': expected_count,
        'coverage': valid_count / expected_count,
        'in_range': bool(in_range),
        'variance': float(variance) if not np.isnan(variance) else 0,
        'min_hhi': float(metrics_df['hhi'].min()),
        'max_hhi': float(metrics_df['hhi'].max()),
        'mean_hhi': float(metrics_df['hhi'].mean())
    }
    
    return success, details
```

### Training Protocol

N/A - No model training required. This is observational data analysis.

**Execution Steps:**
1. Load PWC data from HuggingFace
2. Filter to target venues and years
3. Extract dataset tags per paper
4. Compute HHI per venue-year
5. Validate 21/21 coverage

### Evaluation

| Metric | Type | Success Threshold |
|--------|------|-------------------|
| **Coverage** | Primary | 21/21 venue-years have valid HHI |
| **HHI Range** | Validation | All HHI in [0, 1] |
| **HHI Variance** | Secondary | variance > 0 (not all identical) |
| **Paper Count** | Quality | Mean papers/venue-year > 100 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Data validation / observational study
- Library: pandas, numpy (built-in)
- Code:
```python
# Validation metrics are computed inline
# No external metrics library needed
success, details = validate_hhi_scores(metrics_df)
print(f"Gate passed: {success}")
print(f"Coverage: {details['coverage']*100:.1f}%")
print(f"HHI range: [{details['min_hhi']:.4f}, {details['max_hhi']:.4f}]")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing HHI coverage (21/21 venue-years)

#### Additional Figures (LLM Autonomous)

1. **HHI Heatmap**: Venue (rows) x Year (columns) heatmap of HHI values
2. **HHI Time Series**: Line plot of HHI over years, one line per venue
3. **Entropy vs HHI Scatter**: Scatter plot showing relationship between concentration and diversity
4. **Dataset Distribution**: Top-10 most used datasets per venue (stacked bar)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. 21/21 venue-years return valid HHI scores (non-null, in range [0,1])
3. HHI variance > 0 (variation exists across venue-years)

**Gate Logic:**
```python
if valid_count == 21 and variance > 0:
    gate_status = "PASSED"
    proceed_to = "H-M1"
else:
    gate_status = "FAILED"
    action = "PIVOT to Semantic Scholar or OpenAlex"
```

---

## Appendix: Reference Implementations

### 1. HHI Calculation (Stack Overflow)
```python
# Simple pandas HHI
hhi = ((df[col].value_counts() / df[col].count()) ** 2).sum()
```
Source: https://stackoverflow.com/questions/35156662/compute-concentration-of-pandas-categoricals

### 2. PWC Client Usage
```python
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()
papers = client.paper_list(items_per_page=50)
datasets = client.dataset_list()
```
Source: https://paperswithcode-client.readthedocs.io/

### 3. HuggingFace PWC Datasets
```python
from datasets import load_dataset
papers = load_dataset("pwc-archive/papers-with-abstracts")
eval_tables = load_dataset("pwc-archive/evaluation-tables")
```
Source: https://github.com/paperswithcode/paperswithcode-data

### 4. DOJ HHI Interpretation
- HHI < 1,500: Competitive market
- 1,500 ≤ HHI ≤ 2,500: Moderately concentrated
- HHI > 2,500: Highly concentrated

Source: https://www.justice.gov/atr/herfindahl-hirschman-index

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T12:00:00Z

### Workflow History for This Hypothesis
- 2026-08-10: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-10: Experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
