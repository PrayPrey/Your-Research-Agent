# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** High HHI indicates community convergence on few datasets
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Validates HHI interpretation for ML benchmark context.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 COMPLETED (gate satisfied)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
- **Type:** MUST_WORK
- **Primary:** High-HHI group top-5 share > low-HHI group (p < 0.05)
- **Secondary:** Spearman ρ > 0.7 between HHI and top-5 share

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Status:** PASSED
- **Data Source:** HuggingFace `pwc-archive/papers-with-abstracts`
- **Coverage:** 21/21 venue-years with valid HHI scores
- **HHI Range:** [0.0066, 0.0455]
- **Mean HHI:** 0.0171
- **Total Papers:** 12,600 (NeurIPS, ICML, ICLR 2018-2024)
- **Task Categories:** 1,666 unique (used as dataset proxy)

**Reusable from H-E1:**
- PWC data loading pipeline (cached)
- HHI computation function
- Venue-year aggregation structure

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct HHI/concentration analysis found in Archon KB. General ML patterns available but not specific to econometric concentration metrics.

### Archon Code Examples

No direct HHI calculation code in Archon KB. Will use established `concentrationMetrics` library pattern.

### Exa GitHub Implementations

**Key Findings:**

1. **concentrationMetrics Library** (open-risk/concentrationMetrics)
   - URL: https://github.com/open-risk/concentrationMetrics
   - MIT License, 44 stars
   - Provides: `hhi()`, `cr()` (concentration ratio), `gini()`, `entropy()`
   - Install: `pip install concentrationMetrics`

2. **HHI Calculation Pattern** (Stack Overflow + Gists)
   ```python
   def compute_hhi(shares):
       """HHI = Σ(share²), where shares sum to 1"""
       return sum(s**2 for s in shares)
   
   def compute_top_k_share(counts, k=5):
       """Top-k concentration ratio"""
       sorted_counts = sorted(counts, reverse=True)
       total = sum(counts)
       return sum(sorted_counts[:k]) / total if total > 0 else 0
   ```

3. **Merger Simulation HHI Analyzer** (thanhan25/merger-simulation-hhi-analyzer)
   - DOJ/FTC thresholds: <1500 competitive, 1500-2500 moderate, >2500 concentrated
   - Note: Our HHI is normalized [0,1], not [0,10000]

### 🎯 Implementation Priority Assessment

**For H-M1 (validation of HHI interpretation):**
- No external implementation needed
- Use H-E1 validated HHI data
- Implement correlation analysis with scipy.stats

**Recommended Implementation Path:**
- Primary: scipy.stats + pandas (standard statistical libraries)
- Fallback: statsmodels for robust tests
- Justification: Simple statistical validation, no ML training required

### Code Analysis (Serena MCP)

Not applicable for H-M1 - this is a statistical validation hypothesis, not a code implementation task.

---

## Experiment Specification

### Dataset

**Dataset:** PWC Papers with Abstracts (from H-E1)
- **Source:** HuggingFace `pwc-archive/papers-with-abstracts`
- **Type:** standard (programmatic-api via HuggingFace)
- **Cached:** Yes (from H-E1 validation run)

**Statistics:**
- Total papers: 12,600
- Venue-years: 21 (7 years × 3 venues)
- Task categories: 1,666 unique

**Loading Information** (for Phase 4):
- Method: HuggingFace datasets
- Identifier: `pwc-archive/papers-with-abstracts`
- Code: 
  ```python
  from datasets import load_dataset
  ds = load_dataset("pwc-archive/papers-with-abstracts", split="train")
  # Or load from H-E1 cache
  import pandas as pd
  df = pd.read_parquet("h-e1/data/pwc_papers_filtered.parquet")
  ```

### Models

#### Baseline Model

**Architecture:** N/A - Statistical Analysis (not ML model)

This is an econometric validation hypothesis. We validate that HHI correctly reflects concentration by testing correlation with top-5 dataset share.

**Analysis Model:**
- Split venue-years into high-HHI (>median) and low-HHI groups
- Compare top-5 dataset concentration between groups
- Validate with Spearman correlation

**Loading Information** (for Phase 4):
- Method: scipy.stats
- Identifier: N/A
- Code:
  ```python
  from scipy.stats import mannwhitneyu, spearmanr
  import numpy as np
  ```

#### Proposed Model

**Architecture:** Statistical validation of HHI interpretation

**Core Mechanism Implementation:**

```python
# Core Mechanism: HHI Interpretation Validation
# Based on: Phase 2B verification protocol

import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

def compute_top5_share(task_counts: pd.Series) -> float:
    """Compute top-5 dataset concentration ratio."""
    sorted_counts = task_counts.sort_values(ascending=False)
    total = sorted_counts.sum()
    return sorted_counts.head(5).sum() / total if total > 0 else 0

def validate_hhi_interpretation(venue_year_data: pd.DataFrame) -> dict:
    """
    Validate that high HHI correctly indicates concentration.
    
    Args:
        venue_year_data: DataFrame with columns [venue, year, hhi, task_counts]
    
    Returns:
        dict with statistical test results
    """
    # Compute top-5 share for each venue-year
    venue_year_data['top5_share'] = venue_year_data['task_counts'].apply(compute_top5_share)
    
    # Split by median HHI
    median_hhi = venue_year_data['hhi'].median()
    high_hhi = venue_year_data[venue_year_data['hhi'] > median_hhi]['top5_share']
    low_hhi = venue_year_data[venue_year_data['hhi'] <= median_hhi]['top5_share']
    
    # Mann-Whitney U test (non-parametric)
    stat, p_value = mannwhitneyu(high_hhi, low_hhi, alternative='greater')
    
    # Spearman correlation
    rho, p_spearman = spearmanr(venue_year_data['hhi'], venue_year_data['top5_share'])
    
    return {
        'high_hhi_mean': high_hhi.mean(),
        'low_hhi_mean': low_hhi.mean(),
        'mann_whitney_stat': stat,
        'mann_whitney_p': p_value,
        'spearman_rho': rho,
        'spearman_p': p_spearman,
        'gate_passed': p_value < 0.05 and rho > 0.7
    }
```

### Training Protocol

**N/A for H-M1** - This is a statistical validation, not a training experiment.

**Analysis Protocol:**
1. Load HHI data from H-E1 (21 venue-years)
2. For each venue-year, compute top-5 task category share
3. Split into high-HHI (>median) and low-HHI groups
4. Run Mann-Whitney U test (one-sided: high > low)
5. Compute Spearman correlation between HHI and top-5 share
6. Report results against success criteria

**Seeds:** N/A (deterministic statistical analysis)

### Evaluation

**Primary Metrics:**
- Mann-Whitney U test p-value (primary gate: p < 0.05)
- Spearman correlation coefficient ρ (secondary: ρ > 0.7)

**Success Criteria:**
- **Gate Pass:** p < 0.05 for high-HHI group > low-HHI group top-5 share
- **Secondary:** Spearman ρ > 0.7 between HHI and top-5 share

**Expected Baseline Performance:**
- HHI mathematically weights larger shares more heavily (Σshare²)
- Top-5 share directly measures concentration of top datasets
- Strong correlation expected if HHI is valid metric for this context

**Metrics Loading Information** (for Phase 4):
- Task Type: statistical_validation
- Library: scipy.stats
- Code:
  ```python
  from scipy.stats import mannwhitneyu, spearmanr
  # Mann-Whitney U: mannwhitneyu(group1, group2, alternative='greater')
  # Spearman: spearmanr(x, y)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing high-HHI vs low-HHI top-5 share means with error bars

#### Additional Figures (LLM Autonomous)
1. **HHI vs Top-5 Share Scatter**: X=HHI, Y=Top-5 share, color by venue
2. **Distribution Comparison**: Side-by-side histograms of top-5 share for high/low HHI groups
3. **Venue-Year Heatmap**: Matrix showing top-5 share by venue and year

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- [x] `mechanism_exists`: HHI concentration metric mathematically defined (Σshare²)
- [x] `mechanism_isolatable`: Can compute HHI and top-5 share independently
- [x] `baseline_measurable`: Top-5 share is straightforward to compute

### Architecture Compatibility
- Data structure: venue-year aggregated task counts from H-E1
- HHI already computed and validated in H-E1
- Top-5 share computation is additive decomposition

### Activation Indicators
- `mechanism_log_message`: "Computing top-5 share for {venue}-{year}..."
- `tensor_shape_change`: N/A (statistical analysis)
- `metric_delta_expected`: High-HHI group mean > Low-HHI group mean

### Mechanism Verification Code
```python
def verify_mechanism_activation(results: dict) -> bool:
    """Verify H-M1 mechanism activated correctly."""
    checks = {
        'groups_differ': results['high_hhi_mean'] > results['low_hhi_mean'],
        'correlation_positive': results['spearman_rho'] > 0,
        'sufficient_samples': True,  # 21 venue-years
    }
    print(f"Mechanism checks: {checks}")
    return all(checks.values())
```

### Hypothesis Support
- `hypothesis_support_threshold`: p < 0.05 AND ρ > 0.7
- `hypothesis_support_metric`: Mann-Whitney p-value, Spearman ρ

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. High-HHI group has higher mean top-5 share than low-HHI group
3. Spearman correlation is positive

**Gate Pass Condition (MUST_WORK):**
1. Mann-Whitney U test: p < 0.05 (one-sided)
2. Spearman ρ > 0.7

---

## Appendix: Reference Implementations

### HHI Calculation (from H-E1)
```python
def compute_hhi(task_counts: pd.Series) -> float:
    """Compute Herfindahl-Hirschman Index."""
    total = task_counts.sum()
    if total == 0:
        return 0
    shares = task_counts / total
    return (shares ** 2).sum()
```

### Statistical Libraries
- **scipy.stats**: Mann-Whitney U, Spearman correlation
- **pandas**: Data manipulation, groupby operations
- **numpy**: Numerical operations

### concentrationMetrics Library Reference
- URL: https://concentrationmetrics.readthedocs.io/
- GitHub: https://github.com/open-risk/concentrationMetrics
- Alternative implementation if needed

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- H-E1 COMPLETED: 21/21 venue-years validated
- H-M1 IN_PROGRESS: Experiment design complete

---

*MCP Tools Used: Archon (Knowledge), Exa (GitHub + Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
