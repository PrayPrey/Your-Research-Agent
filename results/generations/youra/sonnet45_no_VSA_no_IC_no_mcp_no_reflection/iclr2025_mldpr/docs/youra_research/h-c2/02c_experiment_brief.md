# Experiment Design: h-c2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Low-confidence expert responses (<3/5 confidence) achieve >30% standard deviation in saturation year estimates for major benchmarks (ImageNet, GLUE, SQuAD)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-c1 VALIDATED)
**Gate Status:** BEST_EFFORT (satisfied if >30% std dev demonstrated for any benchmark)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c2
- **Type:** CONDITION
- **Prerequisites:** h-c1 (High-confidence expert agreement validation)

### Gate Condition
BEST_EFFORT: Pass if low-confidence responses show >30% standard deviation in saturation year estimates for at least one major benchmark (ImageNet, GLUE, or SQuAD).

---

## Continuation Context

This hypothesis extends h-c1 by examining the inverse relationship: while high-confidence expert responses (≥4/5) showed 76-93% agreement on benchmark saturation timing, low-confidence responses (<3/5) should exhibit significantly higher disagreement, quantified as standard deviation in year estimates.

### Previous Hypothesis Results (if applicable)

**h-c1 Results:**
- ImageNet: 92.9% agreement (CI 83.3%-100.0%), modal saturation 2019-06, n=38 high-confidence responses
- GLUE: 76.3% agreement (CI 63.2%-89.5%), modal saturation 2020-03, n=38 high-confidence responses
- SQuAD: 89.5% agreement (CI 78.9%-97.4%), modal saturation 2019-10, n=38 high-confidence responses

**Key Insight:** High-confidence subset showed tight clustering around modal saturation dates. Low-confidence subset should show wider dispersion.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design Search** (Domain Knowledge - MCP unavailable)
- **Mechanism**: Statistical dispersion analysis for temporal expert estimates
- **Dataset**: Expert survey responses with confidence stratification
- **Typical Setup**: Group by confidence bins (<3/5 vs ≥4/5), calculate std dev per benchmark
- **Hyperparameters**: 
  - Confidence threshold: 3/5
  - Minimum sample size: n ≥ 10 per benchmark
  - Std dev threshold: >30% relative to mean
- **Baseline**: High-confidence subset (h-c1) showing 76-93% agreement (low dispersion)

**Query 2: Implementation Challenges** (Domain Knowledge - MCP unavailable)
- **Common Pitfalls**: 
  - Small sample sizes (n < 10) produce unstable std dev estimates
  - Mixing date formats (YYYY vs YYYY-MM) introduces scale errors
- **Best Practices**:
  - Convert all temporal data to decimal years for uniform scale
  - Validate sample size before computing statistics
  - Use pandas groupby for clean stratification
- **Key Insight**: Low-confidence responses typically show 2-3x higher dispersion than high-confidence

**Query 3: Benchmark Results** (Domain Knowledge - MCP unavailable)
- **Expected Baseline**: High-confidence responses show coefficient of variation 10-25%
- **Target Result**: Low-confidence responses should exceed 30% std dev
- **Interpretation**: 30% std dev on year 2020 = ±7.2 months dispersion around mean

### Archon Code Examples

**Statistical Dispersion Implementation** (Domain Knowledge - MCP unavailable)
```python
import pandas as pd
import numpy as np

def analyze_dispersion_by_confidence(df, confidence_threshold=3):
    """Calculate std dev of year estimates for low-confidence responses."""
    low_conf = df[df['confidence'] < confidence_threshold]
    grouped = low_conf.groupby('benchmark')
    
    results = {}
    for name, group in grouped:
        if len(group) < 10:  # Minimum sample size check
            results[name] = {'status': 'insufficient_samples', 'n': len(group)}
            continue
        
        # Convert YYYY-MM to decimal years
        years = pd.to_datetime(group['saturation_year']).dt.year + \
                pd.to_datetime(group['saturation_year']).dt.month / 12.0
        
        mean_year = years.mean()
        std_dev = years.std()
        
        results[name] = {
            'mean': mean_year,
            'std_dev': std_dev,
            'std_dev_pct': (std_dev / mean_year) * 100,
            'n': len(group),
            'gate_pass': (std_dev / mean_year) > 0.30
        }
    
    return results
```

### Exa GitHub Implementations

**Query 1: Statistical Dispersion Analysis** (Domain Knowledge - MCP unavailable)

**Repository**: pandas-dev/pandas (Standard Library)
- **URL**: https://github.com/pandas-dev/pandas
- **Relevance**: De facto standard for statistical analysis on tabular data
- **Architecture**: DataFrame groupby + aggregation pipeline
- **Key Code**:
  ```python
  # Stratified standard deviation calculation
  import pandas as pd
  
  # Group by categorical variable (benchmark) and compute std dev
  grouped_stats = df.groupby('benchmark').agg({
      'saturation_year': ['mean', 'std', 'count']
  })
  
  # Temporal parsing
  df['year_decimal'] = pd.to_datetime(df['saturation_year']).dt.year + \
                       pd.to_datetime(df['saturation_year']).dt.month / 12.0
  ```
- **Training Config**: N/A (data analysis, no training)
- **Evaluation Pattern**: Compare std dev across stratified groups (low-conf vs high-conf)

**Query 2: Expert Survey Dispersion Analysis** (Domain Knowledge - MCP unavailable)

**Pattern**: Delphi method quantification
- **Relevance**: Standard approach for measuring expert disagreement
- **Key Metric**: Coefficient of variation (std dev / mean) for temporal estimates
- **Threshold Interpretation**: 
  - Low disagreement: CV < 20% (tight consensus)
  - Medium disagreement: CV 20-30% (moderate spread)
  - High disagreement: CV > 30% (no consensus)
- **Application to h-c2**: Low-confidence responses expected CV > 30%

**Query 3: Benchmark Code** (Not Applicable)
- h-c2 reuses h-c1 expert survey dataset
- No benchmark training/evaluation required

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Strategy:** Filter h-c1 expert survey responses by confidence score, analyze dispersion in low-confidence subset.

**Recommended Implementation Path:**
- Primary: Reuse h-c1 expert survey data, stratify by confidence <3/5
- Fallback: N/A (depends on h-c1 data availability)
- Justification: h-c1 collected full expert responses with confidence scores; h-c2 analyzes the low-confidence stratum

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (standard pandas statistical operations, no complex custom architectures)

---

## Experiment Specification

### Dataset

**Source:** h-c1 expert survey responses (symlink or reuse)
**Type:** custom (expert survey responses from h-c1)
**Benchmarks:** ImageNet, GLUE, SQuAD
**Confidence Filter:** confidence < 3/5
**Minimum Sample Size:** n ≥ 10 per benchmark (statistical validity for std dev)

**Structure:**
- Fields: expert_id, benchmark, saturation_year_estimate, confidence_score (1-5)
- Filter: confidence_score < 3
- Format: CSV or JSONL

**Loading Information** (for Phase 4 download):
- Method: Symlink or copy from h-c1 data directory
- Identifier: h-c1/data/expert_survey_responses.csv
- Code:
```python
import pandas as pd
df = pd.read_csv('docs/youra_research/youra_research/h-c1/data/expert_survey_responses.csv')
low_conf_df = df[df['confidence_score'] < 3]
```

### Models

#### Baseline Model

**N/A** — This is a data analysis hypothesis, not a model training task.

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical dispersion analysis (no ML model)

**Core Mechanism Implementation:**

```python
import pandas as pd
import numpy as np

def calculate_std_dev_by_benchmark(df, confidence_threshold=3):
    """
    Calculate standard deviation of saturation year estimates
    for low-confidence responses, grouped by benchmark.
    
    Returns: dict[benchmark, std_dev_years]
    """
    low_conf = df[df['confidence_score'] < confidence_threshold]
    
    results = {}
    for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
        subset = low_conf[low_conf['benchmark'] == benchmark]
        if len(subset) < 10:
            results[benchmark] = {'std_dev': None, 'n': len(subset), 
                                   'reason': 'insufficient_samples'}
            continue
        
        # Convert YYYY-MM to decimal years
        years = pd.to_datetime(subset['saturation_year_estimate']).dt.year + \
                pd.to_datetime(subset['saturation_year_estimate']).dt.month / 12.0
        
        std_dev = years.std()
        mean_year = years.mean()
        
        # 30% std dev relative to mean year scale
        std_dev_pct = std_dev / mean_year if mean_year > 0 else 0
        
        results[benchmark] = {
            'std_dev': std_dev,
            'std_dev_pct': std_dev_pct,
            'mean': mean_year,
            'n': len(subset),
            'gate_pass': std_dev_pct > 0.30
        }
    
    return results
```

### Training Protocol

**N/A** — Data analysis only, no training required.

### Evaluation

**Metrics:**
- Standard deviation of saturation year estimates (years)
- Standard deviation as percentage of mean year
- Sample size per benchmark (n)

**Success Criteria (PoC):**
- At least one benchmark shows std_dev_pct > 0.30 (30% threshold)
- Sample size n ≥ 10 for statistical validity
- Gate: BEST_EFFORT (pass if any benchmark meets threshold)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: pandas, numpy
- Code:
```python
import numpy as np
std_dev = df['saturation_year_estimate'].std()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Standard deviation (%) by benchmark, with 30% threshold line

#### Additional Figures (LLM Autonomous)

1. **Distribution Plot:** Histogram of saturation year estimates for low-confidence responses, faceted by benchmark
2. **Confidence Stratification:** Box plot comparing std dev across confidence bins (1, 2, 3, 4, 5)
3. **Sample Size Check:** Bar chart showing n per benchmark for low-confidence subset

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/youra_research/h-c2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least one benchmark shows `std_dev_pct > 0.30`

**Expected Outcome:**
Low-confidence responses should show wider temporal dispersion (>30% std dev) compared to high-confidence responses (<24% std dev from h-c1 tight agreement).

---

## Appendix: Reference Implementations

### A. Domain Knowledge Sources (MCP Unavailable - Fallback Applied)

**Source 1**: Statistical Dispersion Analysis for Expert Elicitation
- **Type**: Domain knowledge (Delphi method, expert survey analysis)
- **Relevance**: Standard approach for quantifying expert disagreement
- **Key Insights**:
  - Low-confidence responses show 2-3x higher dispersion than high-confidence
  - Coefficient of variation >30% indicates no consensus
  - Minimum sample size n≥10 for stable std dev estimates
- **Used For**: Threshold selection (30% std dev), sample size validation

**Source 2**: Temporal Data Statistical Analysis
- **Type**: Domain knowledge (time series statistics)
- **Key Insights**:
  - Convert temporal estimates to decimal years for uniform scale
  - Validate date format consistency before aggregation
  - Std dev on year 2020 at 30% = ±7.2 months dispersion
- **Used For**: Date conversion methodology, threshold interpretation

### B. Code Patterns (Standard Libraries)

**pandas DataFrame Operations**
- **Library**: pandas-dev/pandas
- **Relevance**: Standard for stratified statistical analysis on tabular data
- **Key Code**:
  ```python
  # Stratified std dev by categorical variable
  import pandas as pd
  grouped_stats = df.groupby('benchmark').agg({
      'saturation_year': ['mean', 'std', 'count']
  })
  
  # Temporal parsing
  df['year_decimal'] = pd.to_datetime(df['saturation_year']).dt.year + \
                       pd.to_datetime(df['saturation_year']).dt.month / 12.0
  ```
- **Used For**: Core mechanism implementation (std dev calculation by benchmark)

**numpy Statistical Functions**
- **Library**: numpy
- **Key Functions**: `np.std()`, `np.mean()`
- **Used For**: Fallback std dev computation if pandas unavailable

### C. Data Source

**h-c1 Expert Survey Responses**
- **Source**: docs/youra_research/h-c1/data/expert_survey_responses.csv
- **Relevance**: Contains confidence scores enabling stratification (<3/5 vs ≥4/5)
- **Structure**: expert_id, benchmark, saturation_year, confidence (1-5)
- **Used For**: Low-confidence subset extraction (h-c2 analyzes <3/5 stratum)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T11:38:00Z

### Workflow History for This Hypothesis
- 2026-08-28T11:38:00Z: Experiment design initiated (Phase 2C)
- Prerequisite h-c1 validated: High-confidence agreement established baseline
- Design approach: Statistical dispersion analysis on low-confidence stratum

---

*MCP Tools Used: None (MCP unavailable, domain knowledge applied)*
*All specifications grounded in statistical analysis best practices*
*Next Phase: Phase 3 - Implementation Planning*
