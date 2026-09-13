# Phase 2C: Experiment Design Brief

## Hypothesis: H-E1 (Existence)

**Statement:** λ₁,residual exceeds 95th percentile of permutation distribution after controlling for log(params) and release date.

**Type:** EXISTENCE | **Gate:** MUST_WORK

---

## 1. Experiment Overview

### 1.1 Objective
Test whether a dominant latent factor (PC1) remains after regressing out model scale and temporal confounds from LLM benchmark correlation matrix.

### 1.2 Statistical Test
- **Method:** PCA on residualized benchmark scores + permutation test for eigenvalue significance
- **Null Hypothesis:** No latent structure beyond scale/time confounds (λ₁,residual ≤ permutation null)
- **Alternative:** Residual factor structure exists (λ₁,residual > 95th percentile)

---

## 2. Data Specification

### 2.1 Primary Dataset
| Field | Value |
|-------|-------|
| Name | Open LLM Leaderboard Results |
| Source | `huggingface.co/datasets/open-llm-leaderboard/results` |
| Type | programmatic-api |
| Size | ~4,500 models × 6 benchmarks |
| Format | Parquet/JSON via HuggingFace datasets API |

### 2.2 Supplementary Dataset
| Field | Value |
|-------|-------|
| Name | HELM Benchmark Results |
| Source | `gs://crfm-helm-public/lite/benchmark_output` |
| Type | programmatic-api |
| Access | Google Cloud Storage (public, no auth) |

### 2.3 Required Variables

**Benchmark Scores (Y matrix):**
- IFEval (instruction following)
- BBH (reasoning)
- MATH-Hard (mathematical reasoning)
- GPQA (graduate-level QA)
- MUSR (multi-step reasoning)
- MMLU-Pro (knowledge)

**Confound Variables (X matrix):**
- `log_params`: log₁₀(parameter count)
- `release_date`: Unix timestamp or ordinal encoding
- `model_family`: Categorical (optional stratification)

### 2.4 Inclusion Criteria
- Parameter count available
- ≥4 of 6 benchmark scores non-missing
- Released between 2023-01-01 and 2025-12-31

### 2.5 Expected Sample Size
- **Minimum viable:** N ≥ 80 models (for stable PCA with 6 variables)
- **Target:** N ≈ 200-500 models (after filtering)
- **Available:** ~4,500 raw entries (many will filter out due to missing metadata)

---

## 3. Analysis Pipeline

### 3.1 Data Preparation
```
1. Load Open LLM Leaderboard via datasets API
2. Extract benchmark scores + model metadata
3. Filter: non-null param count, ≥4 benchmarks, date range
4. Impute remaining missing values (column mean or drop)
5. Standardize benchmark scores (z-score)
```

### 3.2 Confound Residualization
```
For each benchmark column y_i:
    y_i_resid = y_i - OLS(y_i ~ log_params + release_date).predict()
    
Result: Residualized benchmark matrix Y_resid (N × 6)
```

### 3.3 PCA on Residuals
```
pca = PCA(n_components=6)
pca.fit(Y_resid)
lambda_1_observed = pca.explained_variance_[0]
pc1_scores = pca.transform(Y_resid)[:, 0]
loadings = pca.components_[0, :]
```

### 3.4 Permutation Test
```
n_permutations = 1000
null_lambda_1 = []

for i in range(n_permutations):
    Y_perm = np.apply_along_axis(np.random.permutation, 0, Y_resid)
    pca_null = PCA(n_components=1)
    pca_null.fit(Y_perm)
    null_lambda_1.append(pca_null.explained_variance_[0])

p_value = (sum(null_lambda_1 >= lambda_1_observed) + 1) / (n_permutations + 1)
threshold_95 = np.percentile(null_lambda_1, 95)
```

### 3.5 Success Criteria
| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| p-value | < 0.05 | λ₁ significantly exceeds null |
| λ₁,obs > λ₁,95th | True | Confirms residual factor |
| Variance explained by PC1 | > 20% | Meaningful factor strength |

---

## 4. Implementation Requirements

### 4.1 Dependencies
```
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3
pandas>=2.0
datasets>=2.14  # HuggingFace datasets
statsmodels>=0.14  # OLS residualization
matplotlib>=3.7  # Visualization
```

### 4.2 Compute Requirements
- **CPU:** Standard (no GPU needed)
- **Memory:** 8GB sufficient
- **Runtime:** <5 minutes for full pipeline with 1000 permutations

### 4.3 Output Artifacts
```
outputs/
├── h_e1_results.json          # Main results
├── benchmark_matrix.csv       # Filtered data
├── residualized_matrix.csv    # After confound removal
├── permutation_dist.png       # Null distribution plot
├── scree_plot.png             # Eigenvalue plot
└── pc1_loadings.png           # Factor loadings
```

---

## 5. Validation Checkpoints

### 5.1 Data Quality Checks
- [ ] N ≥ 80 models after filtering
- [ ] No benchmark with >30% missing values
- [ ] Confound variables have expected distributions

### 5.2 Statistical Assumptions
- [ ] Residuals approximately normal (Shapiro-Wilk or visual)
- [ ] No extreme multicollinearity in confounds (VIF < 5)
- [ ] Sample size adequate for 6-variable PCA (Kaiser-Meyer-Olkin ≥ 0.6)

### 5.3 Robustness Checks
- [ ] Rerun with different confound sets (scale only, time only)
- [ ] Sensitivity to missing data imputation method
- [ ] Bootstrap confidence interval for λ₁

---

## 6. Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Insufficient models after filtering | Medium | Relax inclusion criteria; merge HELM data |
| Confounds explain all variance | Low | Report attenuation; proceed to H-M1 if modest |
| Non-normal residuals | Low | Use rank-based permutation; report both |

---

## 7. Baseline Comparison (Phase 5 Preview)

**Naive Baseline:** Raw correlation PCA without confound control
- Expected: Higher λ₁ (inflated by scale)
- Comparison: λ₁,residual / λ₁,raw = attenuation ratio

**Literature Baseline:** Schumacher et al. (2024) g-factor analysis
- Reported strong first factor in LLM benchmarks
- Our test: Does factor survive confound control?

---

## 8. Timeline

| Step | Duration | Output |
|------|----------|--------|
| Data acquisition | 1 hour | Raw datasets cached |
| Preprocessing | 2 hours | Filtered benchmark matrix |
| Analysis | 1 hour | Results + visualizations |
| Documentation | 1 hour | Final report |

**Total:** ~5 hours

---

## 9. Code Skeleton

```python
# h_e1_eigenvalue_test.py
from datasets import load_dataset
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

def load_benchmark_data():
    """Load Open LLM Leaderboard results."""
    ds = load_dataset("open-llm-leaderboard/results", split="train")
    return ds.to_pandas()

def filter_models(df, min_benchmarks=4):
    """Apply inclusion criteria."""
    # Filter by parameter availability and benchmark coverage
    pass

def residualize(Y, X):
    """OLS residualization of benchmarks on confounds."""
    residuals = np.zeros_like(Y)
    for i in range(Y.shape[1]):
        model = sm.OLS(Y[:, i], sm.add_constant(X)).fit()
        residuals[:, i] = model.resid
    return residuals

def permutation_test(Y_resid, n_perms=1000):
    """Test eigenvalue significance via permutation."""
    pca = PCA(n_components=1)
    pca.fit(Y_resid)
    lambda_obs = pca.explained_variance_[0]
    
    null_dist = []
    for _ in range(n_perms):
        Y_perm = np.apply_along_axis(np.random.permutation, 0, Y_resid)
        pca.fit(Y_perm)
        null_dist.append(pca.explained_variance_[0])
    
    p_value = (np.sum(null_dist >= lambda_obs) + 1) / (n_perms + 1)
    return lambda_obs, null_dist, p_value

def main():
    # 1. Load data
    df = load_benchmark_data()
    df = filter_models(df)
    
    # 2. Extract matrices
    benchmarks = ['ifeval', 'bbh', 'math_hard', 'gpqa', 'musr', 'mmlu_pro']
    Y = df[benchmarks].values
    X = df[['log_params', 'release_date']].values
    
    # 3. Standardize and residualize
    Y = StandardScaler().fit_transform(Y)
    Y_resid = residualize(Y, X)
    
    # 4. Permutation test
    lambda_obs, null_dist, p_value = permutation_test(Y_resid)
    
    # 5. Report
    print(f"λ₁,observed: {lambda_obs:.4f}")
    print(f"95th percentile null: {np.percentile(null_dist, 95):.4f}")
    print(f"p-value: {p_value:.4f}")
    print(f"H-E1 PASSED: {p_value < 0.05}")

if __name__ == "__main__":
    main()
```

---

## 10. References

1. PCAtest R package: Permutation-based eigenvalue significance (Vieira 2012)
2. Open LLM Leaderboard: `huggingface.co/spaces/open-llm-leaderboard`
3. HELM: Stanford CRFM holistic evaluation framework
4. Kaiser-Meyer-Olkin (KMO) test for sampling adequacy
