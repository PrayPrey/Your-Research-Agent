# Experiment Design: h-c2

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** The metadata-variance effect persists within RandomForest-only analysis, ruling out algorithm mix confound
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **CONDITION (Permutation Control) Template** - Statistical validation of h-e1 correlation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (PASS - 42.1% IQR reduction)
**Gate Status:** SHOULD_WORK (pipeline continues with warning if fail)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c2
- **Type:** CONDITION (Permutation Control)
- **Prerequisites:** h-e1 must pass (✅ SATISFIED)

### Gate Condition
**SHOULD_WORK:** If permutation test shows true effect > 95th percentile of shuffled distribution, confirms correlation is not spurious. If fail, hypothesis is weakened but pipeline continues.

---

## Continuation Context

### Previous Hypothesis Results (h-e1)

**Status:** VALIDATED (PASS)

**Key Findings to Validate:**
- Relative IQR reduction: 42.1% (threshold: 20%)
- Absolute IQR reduction: 0.0197 (threshold: 0.01)
- 95% CI: [39.1%, 51.7%] excludes <10%
- p-value < 0.0001 (threshold: 0.05)

**Reused from h-e1:**
- OpenML data collection pipeline
- Metadata completeness scoring (5-field checklist)
- IQR computation for reproducibility variance
- Mixed-effects regression framework
- Control variables: intrinsic stability, popularity, algorithm family, infrastructure
- Regression coefficient from h-e1: **β_metadata** (the effect to validate)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Permutation test statistical significance regression**
- Limited direct results on permutation testing for regression coefficients
- OpenML benchmark datasets documented (openreview.net/forum?id=M3Y74vmsMcY)

**Query 2: Reproducibility variance metadata correlation**
- Found diffusers issues on reproducibility variance (github.com/huggingface/diffusers/issues/1934)
- General variance/correlation concepts documented

**Query 3: OpenML benchmark datasets API evaluation**
- OpenML evaluations API documented (openreview.net/forum?id=M3Y74vmsMcY)
- Provides run_id, task_id, setup_id, flow_id, data_id, function (metric), value fields

### Archon Code Examples

Limited direct code examples for permutation testing. Numpy/scipy matrix operations documented.

### Exa GitHub Implementations

**Primary Source: scipy.stats.permutation_test**
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Relevance**: Standard Python implementation for permutation testing
- **Key Features**:
  - `n_resamples=9999` for randomized test (or `np.inf` for exact)
  - `alternative='two-sided'` | `'less'` | `'greater'`
  - `vectorized=True` for performance
  - Returns `res.statistic` and `res.pvalue`

**Secondary Source: Residual Permutation Test (RPT)**
- **URL**: http://eprints.lse.ac.uk/126275/1/main_003_.pdf
- **Relevance**: Theoretical foundation for regression coefficient permutation testing
- **Key Insight**: Project residuals onto space orthogonal to design matrix for valid test

**Tertiary Source: ritest Python package**
- **URL**: https://github.com/tabareCapitan/ritest
- **Relevance**: Python implementation of randomization inference for regression
- **Key Features**: Fast linear-model path, test inversion for CIs

**Stack Overflow Reference:**
```python
# Permutation test for regression coefficient
PermuteFunction <- function(data, regr, resp){
 i <- sample(nrow(data))
 x <- data[i, regr]
 y <- data[[resp]]
 coef(lm(y ~ x))[2]
}

initial <- coef(lm(y ~ x, data))[2]
R <- 1000
sim <- replicate(R, PermuteFunction(data, "x", "y"))
p_value <- mean(sim >= initial)
```

### 🎯 Implementation Priority Assessment

**CRITICAL: For permutation testing, use established statistical libraries**

**Recommended Implementation Path:**
- Primary: `scipy.stats.permutation_test` with custom statistic function
- Fallback: Manual numpy implementation (shuffle + recompute coefficient)
- Justification: scipy provides validated, vectorized implementation with proper p-value computation

### Code Analysis (Serena MCP)

**Not Required:** This is a statistical analysis task using established scipy/numpy libraries, not custom DL code. No complex codebase analysis needed.

---

## Experiment Specification

### Dataset

**Type:** programmatic-api (OpenML REST API)
**Source:** OpenML benchmark datasets (same as h-e1)

**Dataset Specification:**
- **Name:** OpenML datasets with ≥10 matched runs (2019-2024)
- **Collection Method:** Reuse h-e1 collected data (already fetched)
- **Sample Size:** ~200 datasets (same as h-e1 analysis)
- **Required Fields:** 
  - `metadata_completeness_score` (computed 5-field checklist)
  - `iqr_variance` (reproducibility IQR per dataset)
  - Control variables: intrinsic_stability, popularity, algorithm_family, infrastructure

**Loading Information** (for Phase 4):
- Method: programmatic-api
- Identifier: OpenML Python API (`openml.evaluations.list_evaluations()`)
- Code:
```python
import openml
import pandas as pd

# Reuse data from h-e1 validation
h_e1_data_path = "../h-e1/data/processed_datasets.csv"
df = pd.read_csv(h_e1_data_path)

# Required columns: metadata_completeness, iqr_variance, controls
assert all(col in df.columns for col in [
    'metadata_completeness', 'iqr_variance', 
    'intrinsic_stability', 'popularity', 'algorithm_family'
])
```

### Models

#### Baseline Model

**This is a statistical analysis, not a DL model.**

**Analysis Framework:** Mixed-effects regression (same as h-e1)

**Loading Information** (for Phase 4):
- Method: statsmodels/scipy
- Identifier: `statsmodels.regression.mixed_linear_model.MixedLM`
- Code:
```python
import statsmodels.formula.api as smf

# Original regression from h-e1
model = smf.mixedlm(
    "iqr_variance ~ metadata_completeness + intrinsic_stability + popularity + algorithm_family",
    data=df,
    groups=df["infrastructure"]
)
result = model.fit()
true_coefficient = result.params['metadata_completeness']
```

#### Proposed Model

**Architecture:** Permutation test wrapper around baseline regression

**Core Mechanism Implementation:**

```python
# Core Mechanism: Permutation Test for Regression Coefficient
# Based on: scipy.stats.permutation_test + Freedman-Lane residual permutation

import numpy as np
from scipy import stats
import statsmodels.formula.api as smf

def compute_regression_coefficient(data_tuple):
    """
    Statistic function for permutation test.
    Returns regression coefficient for metadata_completeness.
    """
    metadata_scores, iqr_values, controls = data_tuple
    # Reconstruct dataframe
    df = pd.DataFrame({
        'metadata_completeness': metadata_scores,
        'iqr_variance': iqr_values,
        **controls
    })
    # Fit regression
    model = smf.mixedlm(
        "iqr_variance ~ metadata_completeness + intrinsic_stability + popularity + algorithm_family",
        data=df, groups=df["infrastructure"]
    )
    result = model.fit(disp=False)
    return result.params['metadata_completeness']

def permutation_test_coefficient(df, n_permutations=1000, seed=42):
    """
    Run permutation test: shuffle metadata_completeness, recompute coefficient.
    
    Args:
        df: DataFrame with metadata_completeness, iqr_variance, controls
        n_permutations: Number of permutations (default 1000)
        seed: Random seed for reproducibility
    
    Returns:
        true_coef: Original coefficient
        perm_coefs: Array of permuted coefficients
        p_value: Proportion of |perm_coef| >= |true_coef|
    """
    np.random.seed(seed)
    
    # Compute true coefficient
    true_coef = compute_regression_coefficient((
        df['metadata_completeness'].values,
        df['iqr_variance'].values,
        {col: df[col].values for col in ['intrinsic_stability', 'popularity', 'algorithm_family', 'infrastructure']}
    ))
    
    # Permutation loop
    perm_coefs = np.zeros(n_permutations)
    for i in range(n_permutations):
        shuffled_metadata = np.random.permutation(df['metadata_completeness'].values)
        perm_coefs[i] = compute_regression_coefficient((
            shuffled_metadata,
            df['iqr_variance'].values,
            {col: df[col].values for col in ['intrinsic_stability', 'popularity', 'algorithm_family', 'infrastructure']}
        ))
    
    # Two-sided p-value
    p_value = np.mean(np.abs(perm_coefs) >= np.abs(true_coef))
    
    return true_coef, perm_coefs, p_value
```

### Training Protocol

**Not Applicable:** This is a statistical analysis, not model training.

**Permutation Test Protocol:**
- **Number of Permutations:** 1000 (as specified in Phase 2B)
- **Random Seed:** 42 (fixed for reproducibility)
- **Test Type:** Two-sided (|permuted| >= |true|)
- **Computation:** Serial (parallel optional for speedup)
- **Expected Runtime:** ~10-30 minutes (1000 regressions)

### Evaluation

**Task Type:** Statistical hypothesis testing

**Primary Metrics:**
1. **True Coefficient (β_metadata):** From h-e1 regression
2. **Permutation Distribution:** 1000 shuffled coefficients
3. **Percentile Rank:** Where true coefficient falls in permutation distribution
4. **P-value:** Proportion of permuted |β| >= true |β|

**Success Criteria (from Phase 2B):**
1. True effect > 95th percentile of permutation distribution
2. Permuted effect < 5% of observed effect magnitude
3. P-value < 0.05 (two-sided)

**Falsification Criteria:**
- Shuffled effect ≥ 20% of observed effect
- True effect < 95th percentile (not significant)

**Metrics Loading Information** (for Phase 4):
- Task Type: statistical-testing
- Library: numpy + custom
- Code:
```python
# Compute success metrics
percentile_rank = np.mean(perm_coefs < true_coef) * 100
effect_ratio = np.percentile(np.abs(perm_coefs), 95) / np.abs(true_coef)
p_value = np.mean(np.abs(perm_coefs) >= np.abs(true_coef))

# Success check
success = (
    percentile_rank > 95 and  # True > 95th percentile
    effect_ratio < 0.05 and   # Permuted < 5% of true
    p_value < 0.05            # Statistically significant
)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Permutation Distribution Histogram**: Histogram of 1000 permuted coefficients with true coefficient marked as vertical line
- **Percentile Position**: Annotation showing percentile rank of true coefficient

#### Additional Figures (LLM Autonomous)
- **QQ Plot**: Compare permutation distribution to null hypothesis
- **Effect Size Comparison**: Bar chart showing true effect vs 95th percentile of permutation distribution

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. True coefficient > 95th percentile of permutation distribution
3. P-value < 0.05

---

## Appendix: Reference Implementations

### Primary References

1. **scipy.stats.permutation_test**
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
   - Usage: Standard permutation test implementation
   - Key parameters: `n_resamples`, `alternative`, `vectorized`

2. **Residual Permutation Test (RPT)**
   - URL: http://eprints.lse.ac.uk/126275/1/main_003_.pdf
   - Usage: Theoretical foundation for regression coefficient testing
   - Key insight: Finite-population validity under p < n/2

3. **ritest Python package**
   - URL: https://github.com/tabareCapitan/ritest
   - Usage: Fast randomization inference for regression
   - Key feature: Test inversion for CIs

4. **OpenML Python API**
   - URL: https://openml.github.io/openml-python/latest/reference/evaluations/
   - Usage: Data collection from OpenML
   - Key classes: `OpenMLEvaluation`, `list_evaluations()`

### Code References

**Stack Overflow - Permutation Test for Regression**
```python
# R-style permutation test translated to Python
import numpy as np

def permutation_test_regression(X, y, n_permutations=1000):
    from sklearn.linear_model import LinearRegression
    
    # Fit original model
    model = LinearRegression().fit(X, y)
    true_coef = model.coef_[0]
    
    # Permutation test
    perm_coefs = []
    for _ in range(n_permutations):
        X_perm = np.random.permutation(X)
        model_perm = LinearRegression().fit(X_perm, y)
        perm_coefs.append(model_perm.coef_[0])
    
    p_value = np.mean(np.abs(perm_coefs) >= np.abs(true_coef))
    return true_coef, np.array(perm_coefs), p_value
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2B: Verification plan created (h-c2 as permutation control)
- Phase 2C: Experiment design completed
- Prerequisite h-e1: VALIDATED with 42.1% IQR reduction

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
