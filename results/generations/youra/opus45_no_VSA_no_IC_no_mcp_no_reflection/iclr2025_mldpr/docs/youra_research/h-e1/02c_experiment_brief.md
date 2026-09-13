# Experiment Design: h-e1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Rankings shift significantly between ImageNet and ImageNet-V2 (Kendall-τ < 0.90 with p < 0.001)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for h-e1)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
- Type: MUST_WORK
- Condition: Kendall-τ < 0.90 with p < 0.001
- If Fail: Core phenomenon not present; revisit Phase 2A

---

## Continuation Context

This is the first hypothesis in the verification chain. No prior hypothesis results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - h-e1 is the first hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP unavailable in ablation mode

**Known Literature:**
1. **Recht et al. (2019)** "Do ImageNet Classifiers Generalize to ImageNet?"
   - Documented 11-14% accuracy drops on ImageNet-V2
   - Did not compute ranking correlations (gap this experiment addresses)
   - Official repo: https://github.com/modestyachts/ImageNetV2

2. **Papers With Code Leaderboards**
   - ImageNet: https://paperswithcode.com/sota/image-classification-on-imagenet
   - ImageNet-V2: https://paperswithcode.com/sota/image-classification-on-imagenet-v2
   - Provides standardized accuracy data for 100+ models

3. **Kendall-τ for Ranking Comparison**
   - Standard statistical measure for ordinal correlation
   - scipy.stats.kendalltau provides implementation with p-values
   - Bootstrap confidence intervals via scipy or custom implementation

### Archon Code Examples

**MCP Status:** Archon MCP unavailable in ablation mode

**Standard Implementation Patterns:**
```python
from scipy.stats import kendalltau
import numpy as np

# Compute Kendall-τ between two rankings
tau, p_value = kendalltau(ranking_imagenet, ranking_v2)

# Bootstrap confidence interval
def bootstrap_kendall_ci(x, y, n_bootstrap=10000, ci=0.95):
    taus = []
    n = len(x)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        tau, _ = kendalltau(x[idx], y[idx])
        taus.append(tau)
    alpha = (1 - ci) / 2
    return np.percentile(taus, [alpha*100, (1-alpha)*100])
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP unavailable in ablation mode

**Known Relevant Repositories:**
1. **modestyachts/ImageNetV2** - Official ImageNet-V2 repository
   - URL: https://github.com/modestyachts/ImageNetV2
   - Contains: Dataset download scripts, evaluation code
   - Language: Python

2. **Papers With Code API** - Programmatic leaderboard access
   - URL: https://paperswithcode.com/api/v1/
   - Endpoint: `/evaluations/` for model results
   - Documentation: https://paperswithcode.com/api/docs/

3. **timm (PyTorch Image Models)**
   - URL: https://github.com/huggingface/pytorch-image-models
   - Contains: Pre-trained models with ImageNet/V2 benchmarks
   - Stars: 30k+

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis experiment, not model training**

**Priority Order:**
1. **Data Collection** - Papers With Code API or manual extraction
2. **Statistical Analysis** - scipy.stats for Kendall-τ computation
3. **Visualization** - matplotlib for ranking comparison plots

**Recommended Implementation Path:**
- Primary: Papers With Code API for standardized accuracy data
- Fallback: Manual extraction from leaderboard tables + original papers
- Justification: Papers With Code provides community-curated, comparable results under standard evaluation protocols

### Code Analysis (Serena MCP)

**MCP Status:** Serena MCP unavailable in ablation mode

**Analysis Summary:**
- No custom codebase to analyze
- Implementation uses standard scipy/numpy statistical functions
- Data collection is the primary challenge, not algorithmic complexity

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | ImageNet Model Rankings (Papers With Code) |
| **Type** | standard |
| **Source** | Papers With Code Leaderboards |
| **Format** | Tabular (model name, accuracy, publication year) |
| **Size** | ~100-200 models with both ImageNet and ImageNet-V2 results |
| **Splits** | N/A (ranking data, not train/test split) |

**Data Fields Required:**
- `model_name`: Unique model identifier
- `imagenet_top1`: Top-1 accuracy on ImageNet validation set
- `imagenet_v2_top1`: Top-1 accuracy on ImageNet-V2 (MatchedFrequency)
- `architecture_family`: ResNet, ViT, ConvNeXt, EfficientNet, etc.
- `publication_year`: Year model was published (for h-m3)
- `params_millions`: Parameter count (for controls)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: Papers With Code API v1 + manual augmentation
- Code:
```python
import requests
import pandas as pd

# Papers With Code API endpoint
PWC_API = "https://paperswithcode.com/api/v1"

def fetch_imagenet_leaderboard():
    """Fetch ImageNet classification leaderboard."""
    url = f"{PWC_API}/evaluations/"
    params = {"task": "image-classification", "dataset": "imagenet"}
    response = requests.get(url, params=params)
    return response.json()

def fetch_imagenet_v2_leaderboard():
    """Fetch ImageNet-V2 classification leaderboard."""
    url = f"{PWC_API}/evaluations/"
    params = {"task": "image-classification", "dataset": "imagenet-v2"}
    response = requests.get(url, params=params)
    return response.json()

# Merge on model name, keep models with both results
df_imagenet = pd.DataFrame(fetch_imagenet_leaderboard())
df_v2 = pd.DataFrame(fetch_imagenet_v2_leaderboard())
df_merged = pd.merge(df_imagenet, df_v2, on="model", suffixes=("_in", "_v2"))
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Type** | N/A - This is a ranking analysis, not model training |
| **Models Analyzed** | All ImageNet classifiers with both IN and V2 results |
| **Minimum Sample** | ≥30 models for statistical power |
| **Source** | Papers With Code leaderboards |

**Note:** This experiment analyzes *rankings* of existing models, not training new models. The "baseline" is the null hypothesis expectation (τ ≥ 0.95, rankings preserved).

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A (no model weights needed)
- Code: N/A (analysis of published accuracy values only)

#### Proposed Model

**Architecture:** N/A - Statistical ranking analysis

**Core Mechanism Implementation:**

```python
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
from typing import Tuple, List

def compute_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rankings for both benchmarks."""
    df = df.copy()
    # Rank by accuracy (higher = better = rank 1)
    df['rank_imagenet'] = df['imagenet_top1'].rank(ascending=False)
    df['rank_v2'] = df['imagenet_v2_top1'].rank(ascending=False)
    return df

def compute_kendall_tau(df: pd.DataFrame) -> Tuple[float, float]:
    """Compute Kendall-τ between ImageNet and V2 rankings."""
    tau, p_value = kendalltau(df['rank_imagenet'], df['rank_v2'])
    return tau, p_value

def bootstrap_confidence_interval(
    df: pd.DataFrame,
    n_bootstrap: int = 10000,
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Bootstrap 95% CI for Kendall-τ."""
    taus = []
    n = len(df)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        sample = df.iloc[idx]
        tau, _ = kendalltau(sample['rank_imagenet'], sample['rank_v2'])
        taus.append(tau)
    alpha = (1 - confidence) / 2
    ci_low = np.percentile(taus, alpha * 100)
    ci_high = np.percentile(taus, (1 - alpha) * 100)
    return ci_low, ci_high

def test_hypothesis(
    tau: float,
    p_value: float,
    ci: Tuple[float, float],
    threshold: float = 0.90
) -> dict:
    """Test h-e1 hypothesis: τ < 0.90 with p < 0.001."""
    return {
        'tau': tau,
        'p_value': p_value,
        'ci_95': ci,
        'threshold': threshold,
        'tau_below_threshold': tau < threshold,
        'ci_excludes_095': ci[1] < 0.95,
        'significant': p_value < 0.001,
        'hypothesis_supported': (tau < threshold) and (p_value < 0.001)
    }

# Main analysis pipeline
def run_h_e1_analysis(df: pd.DataFrame) -> dict:
    """Execute h-e1 existence hypothesis analysis."""
    df = compute_rankings(df)
    tau, p_value = compute_kendall_tau(df)
    ci = bootstrap_confidence_interval(df)
    result = test_hypothesis(tau, p_value, ci)
    return result
```

### Training Protocol

**N/A - Statistical Analysis Only**

This experiment does not involve model training. It is a statistical analysis of existing benchmark results.

**Analysis Protocol:**
1. **Data Collection** (~1 hour)
   - Fetch leaderboards from Papers With Code API
   - Merge datasets on model name
   - Filter to models with both ImageNet and V2 results
   - Augment with publication year and architecture family

2. **Data Validation** (~30 min)
   - Verify minimum 30 models available
   - Cross-validate 10% of entries with original papers
   - Flag and document any inconsistencies

3. **Statistical Analysis** (~30 min)
   - Compute rankings for each benchmark
   - Calculate Kendall-τ correlation
   - Bootstrap 95% confidence intervals (10,000 iterations)
   - Test against threshold (τ < 0.90)

4. **Visualization** (~30 min)
   - Generate ranking comparison scatter plot
   - Create accuracy drop distribution histogram
   - Produce summary statistics table

### Evaluation

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| **Kendall-τ** | Rank correlation coefficient | τ < 0.90 |
| **p-value** | Statistical significance | p < 0.001 |
| **95% CI upper** | Bootstrap confidence interval | CI_upper < 0.95 |
| **Sample size** | Number of models analyzed | n ≥ 30 |

**Primary Gate Metric:** Kendall-τ < 0.90 with p < 0.001

**Secondary Metrics:**
- Spearman-ρ (for comparison)
- Top-10 overlap percentage (preview of h-m2)
- Mean accuracy drop (descriptive)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-analysis
- Library: scipy, numpy, pandas
- Code:
```python
from scipy.stats import kendalltau, spearmanr
import numpy as np

# Primary metric
tau, p_tau = kendalltau(rank_in, rank_v2)

# Secondary metrics
rho, p_rho = spearmanr(rank_in, rank_v2)
top10_overlap = len(set(top10_in) & set(top10_v2)) / 10
mean_drop = np.mean(acc_in - acc_v2)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Ranking Scatter Plot**: ImageNet rank vs V2 rank with diagonal reference line
2. **Accuracy Drop Histogram**: Distribution of per-model accuracy drops
3. **Rank Change Distribution**: Histogram of |rank_in - rank_v2| per model
4. **Architecture-wise Box Plot**: Accuracy drops grouped by architecture family

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Kendall-τ < 0.90 with statistical significance (p < 0.001)

---

## Appendix: Reference Implementations

### Primary References

1. **Recht et al. (2019)** "Do ImageNet Classifiers Generalize to ImageNet?"
   - Paper: https://arxiv.org/abs/1902.10811
   - Code: https://github.com/modestyachts/ImageNetV2
   - Relevance: Original ImageNet-V2 dataset and accuracy drop analysis

2. **Papers With Code Leaderboards**
   - ImageNet: https://paperswithcode.com/sota/image-classification-on-imagenet
   - ImageNet-V2: https://paperswithcode.com/sota/image-classification-on-imagenet-v2
   - API: https://paperswithcode.com/api/v1/
   - Relevance: Source of standardized accuracy data

### Statistical Methods

3. **SciPy kendall-τ implementation**
   - Documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html
   - Handles ties correctly
   - Returns two-sided p-value

4. **Bootstrap CI methodology**
   - Reference: Efron & Tibshirani (1993) "An Introduction to the Bootstrap"
   - Implementation: Standard percentile method with 10,000 iterations

### Related Work

5. **Dehghani et al. (2021)** "The Benchmark Lottery"
   - Paper: https://arxiv.org/abs/2107.07002
   - Relevance: Benchmark selection analysis in NLU (methodological parallel)

6. **Miller et al. (2020)** "The Effect of Natural Distribution Shift on Question Answering Models"
   - Paper: https://arxiv.org/abs/2004.14444
   - Relevance: Distribution shift analysis methodology

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C experiment design initiated
- 2026-08-29: Implementation research completed (ablation mode - MCP unavailable)
- 2026-08-29: Experiment specification finalized

---

*MCP Tools: Unavailable in ablation mode - used known literature and standard implementations*
*All specifications grounded in published research and standard statistical methods*
*Next Phase: Phase 3 - Implementation Planning*
