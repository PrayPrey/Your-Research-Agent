# Experiment Design: H-M5

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Post-2021 Pearson correlation between CV and NLP Gini series drops below 0.4 from pre-2020 baseline of >0.6
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests modality divergence as phase transition indicator.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M4 COMPLETED, PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M5
- **Type:** MECHANISM
- **Prerequisites:** H-M4 (Traditional Benchmark Persistence with Reduced Dominance)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** Pre-2020 r > 0.6; Post-2021 r < 0.4
- **Fail Action:** Pivot to domain-pair specific analysis (CV-NLP vs CV-Audio vs NLP-Audio)

---

## Continuation Context

H-M5 is the final hypothesis in the chain, testing whether foundation models caused modality-differentiated dynamics. This is the key test of phase transition: unified concentration dynamics should fragment into modality-specific patterns.

### Previous Hypothesis Results (H-M4)

From 04_validation.md:
- **Result:** PASS
- **Key Findings:**
  - Traditional benchmark share: 11.70% (reduced dominance)
  - Traditional paper count: 47,068 (persistence confirmed)
  - Emergent benchmark share: 4.01%
  - Chi-square: 16,447.83, p < 10^-308
- **Insight:** Traditional benchmarks persist with reduced dominance, confirming ecosystem fragmentation pattern

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant entries for Gini correlation analysis. Standard statistical methods apply.

### Archon Code Examples

No specific Gini time-series correlation code found. Falling back to standard pandas/scipy implementations.

### Exa GitHub Implementations

**Key Implementation Resources:**

1. **pandas.rolling.corr** (pandas 2.3+)
   - Source: https://pandas.pydata.org/pandas-docs/version/2.3.1/reference/api/pandas.core.window.rolling.Rolling.corr.html
   - Usage: `df['cv_gini'].rolling(6).corr(df['nlp_gini'])`
   - Returns Pearson correlation over rolling window

2. **Fisher Z-Transformation**
   - Source: https://github.com/Himangshu4Das/Fisher-Transformation
   - Formula: z' = 0.5 * [ln(1+r) - ln(1-r)] = arctanh(r)
   - Use for comparing correlations between periods

3. **p-value from correlation coefficient**
   - Source: scipy.stats.pearsonr, scipy.special.betainc
   - Vectorized p-value: `2 * betainc(0.5*df, 0.5, df/(df+t_squared))` where `t_squared = r**2 * (n-2) / (1-r**2)`

4. **Papers With Code Data**
   - Source: https://github.com/paperswithcode/paperswithcode-data
   - HuggingFace: pwc-archive/datasets, pwc-archive/evaluation-tables
   - Contains task-dataset-metric triplets with modality classification

### 🎯 Implementation Priority Assessment

**CRITICAL: Use standard statistical libraries (pandas, scipy, numpy)**

**Recommended Implementation Path:**
- Primary: pandas rolling correlation + scipy Fisher z-test
- Fallback: Manual correlation computation with numpy
- Justification: Well-documented, numerically stable, vectorized implementations

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. Fresh implementation from specification.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Historical Dataset
**Type:** standard (HuggingFace)
**Version:** pwc-archive/datasets (daily dumps)
**Source:** https://huggingface.co/datasets/pwc-archive/datasets

**Structure:**
- datasets.json: Contains `task` field with modality classification
- Modality extraction via task hierarchy (Computer Vision, NLP, Audio, etc.)

**Preprocessing:**
1. Load datasets from HuggingFace
2. Extract modality from task field using PWC hierarchy
3. Map datasets to modality categories: {CV, NLP, Audio, Tabular, Multimodal}
4. Compute monthly paper counts per modality
5. Calculate Gini coefficient per modality per month

**Sample Size:** Full dataset (2018-2024 monthly aggregation, ~72 time points)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets library
- Identifier: pwc-archive/datasets
- Code:
```python
from datasets import load_dataset
datasets = load_dataset("pwc-archive/datasets", split="train")
```

### Models

#### Baseline Model

**Name:** Unified Concentration Model (Null Hypothesis)
**Description:** Assumes all modalities follow same concentration dynamics with correlation r > 0.5 throughout study period.

**Specification:**
- Compute overall Gini time series (all modalities combined)
- Expect high correlation (r > 0.6) between any two modality Gini series

**Loading Information** (for Phase 4 download):
- Method: Pure computation (no pretrained model)
- Identifier: N/A
- Code: N/A (statistical computation only)

#### Proposed Model

**Architecture:** Modality-Divergence Correlation Analysis

**Core Mechanism Implementation:**

```python
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.special import betainc

def compute_gini(counts):
    """Compute Gini coefficient from benchmark usage counts."""
    if len(counts) == 0 or counts.sum() == 0:
        return np.nan
    sorted_counts = np.sort(counts)
    n = len(sorted_counts)
    cumsum = np.cumsum(sorted_counts)
    return (2 * np.sum((np.arange(1, n+1) * sorted_counts)) / (n * cumsum[-1])) - (n + 1) / n

def compute_modality_gini_series(df, modality_col, date_col, count_col):
    """Compute monthly Gini per modality."""
    df['month'] = pd.to_datetime(df[date_col]).dt.to_period('M')
    
    gini_series = {}
    for modality in df[modality_col].unique():
        mod_df = df[df[modality_col] == modality]
        monthly = mod_df.groupby('month')[count_col].apply(compute_gini)
        gini_series[modality] = monthly
    
    return pd.DataFrame(gini_series)

def rolling_correlation_analysis(gini_df, window=6):
    """Compute rolling window correlations between modality pairs."""
    cv_gini = gini_df['CV']
    nlp_gini = gini_df['NLP']
    
    rolling_corr = cv_gini.rolling(window).corr(nlp_gini)
    return rolling_corr

def fisher_z_test(r1, n1, r2, n2):
    """Fisher z-test for comparing two correlations."""
    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)
    
    se1 = 1 / np.sqrt(n1 - 3)
    se2 = 1 / np.sqrt(n2 - 3)
    
    z_stat = (z1 - z2) / np.sqrt(se1**2 + se2**2)
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    return z_stat, p_value

def validate_modality_divergence(gini_df, pre_cutoff='2020-01', post_cutoff='2021-01'):
    """Main validation: compare pre vs post correlations."""
    pre_data = gini_df[gini_df.index < pre_cutoff]
    post_data = gini_df[gini_df.index >= post_cutoff]
    
    # Compute period correlations
    r_pre, _ = pearsonr(pre_data['CV'].dropna(), pre_data['NLP'].dropna())
    r_post, _ = pearsonr(post_data['CV'].dropna(), post_data['NLP'].dropna())
    
    n_pre = len(pre_data['CV'].dropna())
    n_post = len(post_data['CV'].dropna())
    
    # Fisher z-test
    z_stat, p_value = fisher_z_test(r_pre, n_pre, r_post, n_post)
    
    # Gate check
    gate_pass = (r_pre > 0.6) and (r_post < 0.4) and (p_value < 0.05)
    
    return {
        'r_pre': r_pre,
        'r_post': r_post,
        'n_pre': n_pre,
        'n_post': n_post,
        'z_stat': z_stat,
        'p_value': p_value,
        'gate_pass': gate_pass
    }
```

### Training Protocol

**Not Applicable** - This is a statistical analysis, not ML training.

**Analysis Protocol:**
1. Load PWC datasets from HuggingFace
2. Extract modality classification from task hierarchy
3. Compute monthly benchmark usage counts per modality
4. Calculate Gini coefficient per modality per month
5. Build time-indexed DataFrame of modality Gini series
6. Compute rolling 6-month correlations between CV and NLP
7. Split into pre-2020 and post-2021 periods
8. Calculate period correlations and Fisher z-test
9. Evaluate gate criteria

### Evaluation

**Primary Metrics:**

| Metric | Expected Baseline | Success Threshold |
|--------|------------------|-------------------|
| r_pre (pre-2020 CV-NLP correlation) | >0.6 | >0.6 |
| r_post (post-2021 CV-NLP correlation) | <0.4 | <0.4 |
| Fisher z-test p-value | <0.05 | <0.05 |

**Secondary Metrics:**
- Rolling correlation trajectory visualization
- Other modality pairs (CV-Audio, NLP-Audio) for comparison
- Correlation drop magnitude (r_pre - r_post)

**Gate Pass Condition:**
1. Pre-2020 correlation > 0.6 (unified dynamics)
2. Post-2021 correlation < 0.4 (diverged dynamics)
3. Fisher z-test significant at α=0.05

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis testing
- Library: scipy.stats, scipy.special, numpy
- Code:
```python
from scipy.stats import pearsonr, norm
from scipy.special import betainc
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r_pre vs r_post with threshold lines at 0.6 and 0.4

#### Additional Figures (LLM Autonomous)

1. **Rolling Correlation Time Series**: Line plot of 6-month rolling CV-NLP correlation over time, with vertical lines at 2020 and 2021 markers
2. **Modality Gini Trajectories**: Multi-line plot showing monthly Gini for each modality (CV, NLP, Audio, Tabular)
3. **Correlation Heatmap**: Pre vs post correlation matrices for all modality pairs
4. **Fisher Z-Test Visualization**: Effect size and confidence intervals

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. r_pre > 0.6 (pre-2020 CV-NLP correlation)
3. r_post < 0.4 (post-2021 CV-NLP correlation)
4. Fisher z-test p < 0.05

**Failure Pivot:**
If gate fails, pivot to domain-pair specific analysis:
- Test CV-Audio, NLP-Audio pairs
- Identify which modality pairs diverged vs remained correlated
- Document as partial support for phase transition hypothesis

---

## Appendix: Reference Implementations

### A. Rolling Correlation (pandas)
```python
# 6-month rolling Pearson correlation
rolling_corr = df['cv_gini'].rolling(6).corr(df['nlp_gini'])
```

### B. Fisher Z-Transformation
```python
import numpy as np
from scipy.stats import norm

def fisher_z_test(r1, n1, r2, n2):
    z1, z2 = np.arctanh(r1), np.arctanh(r2)
    se = np.sqrt(1/(n1-3) + 1/(n2-3))
    z_stat = (z1 - z2) / se
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    return z_stat, p_value
```

### C. Gini Coefficient
```python
def gini(x):
    x = np.sort(x)
    n = len(x)
    return (2 * np.sum((np.arange(1, n+1) * x)) / (n * x.sum())) - (n + 1) / n
```

### D. PWC Data Loading
```python
from datasets import load_dataset

# Load datasets metadata
ds = load_dataset("pwc-archive/datasets", split="train")

# Extract modality from task field
def extract_modality(task):
    task_lower = task.lower() if task else ""
    if any(kw in task_lower for kw in ['image', 'vision', 'object detection', 'segmentation']):
        return 'CV'
    elif any(kw in task_lower for kw in ['text', 'language', 'nlp', 'translation', 'summarization']):
        return 'NLP'
    elif any(kw in task_lower for kw in ['audio', 'speech', 'sound']):
        return 'Audio'
    elif any(kw in task_lower for kw in ['tabular', 'structured']):
        return 'Tabular'
    else:
        return 'Other'
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T15:45:00+00:00

### Workflow History for This Hypothesis
- 2026-08-18T15:39:06: h-m5 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-08-18T15:45:00: Phase 2C experiment design initiated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
