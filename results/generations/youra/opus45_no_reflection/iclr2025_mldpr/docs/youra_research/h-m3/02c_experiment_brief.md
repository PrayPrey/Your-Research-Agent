# Experiment Design: H-M3

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Paper counts on MMLU/BIG-Bench/HumanEval leaderboards increased relative to traditional benchmarks post-2021
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing researcher attention shift from traditional to emergent benchmarks.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 PASS: 85.13% emergent benchmarks post-2020)
**Gate Status:** SHOULD_WORK (document limitation if fails)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Emergent-Capability Benchmark Creation) - PASS

### Gate Condition
Emergent-capability benchmark share of total benchmark usage increases post-2021. Absolute paper counts on emergent benchmarks exceed traditional benchmarks by 2024.

---

## Continuation Context

H-M2 established that 85.13% of emergent-capability benchmarks were created post-2020, with a 19x acceleration in creation rate. This validates the supply side (benchmarks exist). H-M3 now tests the demand side: did researchers actually shift attention to these new benchmarks?

### Previous Hypothesis Results
- H-M2 PASS: 1,225 emergent benchmarks post-2020 vs 214 pre-2020
- PWC dataset contains 15,008 benchmarks total
- Data source validated: `pwc-archive/datasets` via HuggingFace

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant prior implementations found in Archon KB for benchmark paper count analysis. General time series analysis and benchmark comparison patterns available but not specific to PWC leaderboard analysis.

### Archon Code Examples

No specific PWC API code examples found. General Python benchmarking patterns available but not applicable.

### Exa GitHub Implementations

**Primary Finding:** `paperswithcode-client` Python package (189 stars)
- Official API client: https://github.com/paperswithcode/paperswithcode-client
- Installation: `pip install paperswithcode-client`
- Key methods:
  - `client.paper_list()` - paginated paper listing
  - `client.dataset_list()` - benchmark/dataset listing
  - Evaluation table models for leaderboard data

**API Documentation:** https://paperswithcode-client.readthedocs.io/en/latest/

### 🎯 Implementation Priority Assessment

**CRITICAL: PWC API provides direct access to benchmark leaderboard data**

**Recommended Implementation Path:**
- Primary: Papers With Code API via `paperswithcode-client` library
- Fallback: Direct HuggingFace `pwc-archive/datasets` for metadata, scrape leaderboard counts
- Justification: Official API is authoritative source; HuggingFace fallback ensures data availability

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. New implementation required.

---

## Experiment Specification

### Dataset

| Attribute | Specification |
|-----------|---------------|
| **Name** | Papers With Code Leaderboard Data |
| **Type** | programmatic-api |
| **Source** | Papers With Code API + HuggingFace `pwc-archive/datasets` |
| **Time Range** | 2018-2024 (monthly aggregation) |
| **Coverage** | All benchmarks with paper submissions |

**Benchmark Categories:**
1. **Emergent-capability benchmarks:** MMLU, BIG-Bench, HumanEval, GSM8K, MATH, ARC, HellaSwag, WinoGrande, TruthfulQA, LAMBADA
2. **Traditional benchmarks:** ImageNet, CIFAR-10, CIFAR-100, MNIST, SQuAD, GLUE, CoNLL, Penn Treebank

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: `paperswithcode-client` + `datasets` library
- Code:
```python
from paperswithcode import PapersWithCodeClient
from datasets import load_dataset

# PWC API for leaderboard data
client = PapersWithCodeClient()

# Fallback: HuggingFace for metadata
pwc_data = load_dataset("pwc-archive/datasets", split="train")
```

### Models

#### Baseline Model

**Type:** Statistical comparison model
**Description:** Chi-square test for independence between benchmark category (emergent vs traditional) and time period (pre-2021 vs post-2021)

**Loading Information** (for Phase 4 download):
- Method: stdlib
- Identifier: `scipy.stats.chi2_contingency`
- Code:
```python
from scipy.stats import chi2_contingency
import pandas as pd
```

#### Proposed Model

**Architecture:** Time series share analysis with chi-square significance testing

**Core Mechanism Implementation:**

```python
def analyze_attention_shift(paper_counts: pd.DataFrame) -> dict:
    """
    Analyze researcher attention shift from traditional to emergent benchmarks.
    
    Args:
        paper_counts: DataFrame with columns [benchmark, category, year_month, paper_count]
                      category in ['emergent', 'traditional']
    
    Returns:
        dict with share_change, chi2_stat, p_value, absolute_comparison
    """
    # 1. Aggregate by category and period
    paper_counts['period'] = paper_counts['year_month'].apply(
        lambda x: 'post_2021' if x >= '2021-01' else 'pre_2021'
    )
    
    # 2. Compute shares per period
    period_totals = paper_counts.groupby(['period', 'category'])['paper_count'].sum().unstack()
    period_totals['emergent_share'] = (
        period_totals['emergent'] / (period_totals['emergent'] + period_totals['traditional'])
    )
    
    # 3. Chi-square test for independence
    contingency_table = period_totals[['emergent', 'traditional']].values
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    # 4. Compute share change
    pre_share = period_totals.loc['pre_2021', 'emergent_share']
    post_share = period_totals.loc['post_2021', 'emergent_share']
    share_increase = post_share - pre_share
    
    # 5. Check 2024 absolute comparison
    latest_year = paper_counts[paper_counts['year_month'].str.startswith('2024')]
    emergent_2024 = latest_year[latest_year['category'] == 'emergent']['paper_count'].sum()
    traditional_2024 = latest_year[latest_year['category'] == 'traditional']['paper_count'].sum()
    
    return {
        'pre_2021_emergent_share': pre_share,
        'post_2021_emergent_share': post_share,
        'share_increase': share_increase,
        'chi2_statistic': chi2,
        'p_value': p_value,
        'emergent_exceeds_traditional_2024': emergent_2024 > traditional_2024,
        'emergent_2024_count': emergent_2024,
        'traditional_2024_count': traditional_2024
    }
```

### Training Protocol

**Not applicable** - Statistical analysis, no model training required.

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Aggregation | Monthly | Match H-E1 temporal resolution |
| Time window | 2018-01 to 2024-12 | Cover pre/post foundation model era |
| Normalization | Publication volume normalized | Control for field growth (R5 mitigation) |

### Evaluation

| Metric | Threshold | Description |
|--------|-----------|-------------|
| **Emergent share increase** | > 0 | Primary: share must increase post-2021 |
| **Chi-square p-value** | < 0.05 | Statistical significance of shift |
| **Absolute comparison 2024** | emergent > traditional | Secondary: emergent exceeds traditional by 2024 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-hypothesis-testing
- Library: scipy, pandas
- Code:
```python
from scipy.stats import chi2_contingency
import pandas as pd
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing pre-2021 vs post-2021 emergent share

#### Additional Figures (LLM Autonomous)

1. **share_timeline.png**: Line plot of emergent vs traditional benchmark share over time (monthly)
2. **absolute_counts.png**: Stacked area chart of paper counts by category (2018-2024)
3. **benchmark_heatmap.png**: Heatmap of top 20 benchmarks by paper count per year
4. **chi_square_residuals.png**: Residual plot from chi-square test

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `post_2021_emergent_share > pre_2021_emergent_share`
3. Chi-square test p-value < 0.05 (statistical significance)

**Secondary (informative):**
- `emergent_2024_count > traditional_2024_count` (absolute comparison)

---

## Appendix: Reference Implementations

### Papers With Code API Usage

```python
from paperswithcode import PapersWithCodeClient

client = PapersWithCodeClient()

# Get evaluation tables (leaderboards)
# Note: May need pagination for full coverage
papers = client.paper_list(items_per_page=50)
datasets = client.dataset_list(items_per_page=50)
```

### Chi-Square Test Pattern

```python
from scipy.stats import chi2_contingency
import numpy as np

# Contingency table: rows=periods, cols=categories
observed = np.array([
    [pre_emergent, pre_traditional],
    [post_emergent, post_traditional]
])

chi2, p, dof, expected = chi2_contingency(observed)
print(f"Chi2: {chi2:.2f}, p-value: {p:.4f}")
```

### Data Collection Strategy

1. **PWC API approach** (preferred):
   - Iterate through evaluation tables
   - Extract paper counts per benchmark
   - Aggregate by benchmark category and date

2. **HuggingFace fallback**:
   - Load `pwc-archive/datasets` 
   - Use `introduced_date` for benchmark metadata
   - Cross-reference with paper metadata from `pwc-archive/papers`

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS: 2026-08-18T14:54:59
- Predecessor H-M2 PASS: 85.13% emergent benchmarks post-2020
- Phase 2C experiment design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
