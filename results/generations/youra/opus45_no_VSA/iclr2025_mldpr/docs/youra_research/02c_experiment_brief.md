# Phase 2C: Experiment Brief for h-e1

**Hypothesis:** h-e1 (EXISTENCE, MUST_WORK)  
**Generated:** 2026-08-09  
**Source:** 02b_verification_plan.md  

---

## 1. Hypothesis Statement

Metadata completeness score correlates with reduced reproducibility variance (≥20% IQR reduction, ≥0.01 absolute) after controlling for intrinsic stability, popularity, algorithm family, and infrastructure.

**Prediction P1:** Top-quartile metadata completeness predicts ≥20% reduction in IQR vs bottom quartile.

---

## 2. Dataset Specification

### 2.1 Data Source

| Field | Value |
|-------|-------|
| **Type** | programmatic-api |
| **Source** | OpenML REST API |
| **Endpoint** | `openml.org/api/v1/` |
| **Time Window** | 2019-01-01 to 2024-12-31 |

### 2.2 Inclusion Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Minimum runs per dataset | ≥10 matched runs | Statistical power for IQR computation |
| Same flow, same hyperparameters | Exact match | Isolate reproducibility variance from hyperparameter variance |
| sklearn version | ≥0.22 | Consistent API, seed logging available |
| Task type | Supervised classification | Standardized evaluation metrics |

### 2.3 Sample Size Estimate

| Component | Estimate |
|-----------|----------|
| OpenML datasets (all) | ~3,000 |
| Datasets with ≥10 runs | ~800 |
| Datasets meeting all criteria | 200-400 (target: 200+) |
| Total runs analyzed | 5,000-20,000 |

### 2.4 Variables

**Independent Variable (IV):**
- Metadata Completeness Score (M): 0-5 scale based on 5-field checklist
  - Feature description present (+1)
  - Target description present (+1)
  - Missing value handling documented (+1)
  - Data collection context documented (+1)
  - Version/changelog present (+1)

**Dependent Variable (DV):**
- Reproducibility Variance: IQR of predictive_accuracy across matched runs

**Control Variables:**
- Intrinsic stability: Coefficient of variation of features
- Popularity: log(run_count)
- Algorithm family: RandomForest, GBM, SVM, Neural Network, etc.
- Infrastructure: sklearn version distribution

---

## 3. Data Collection Pipeline

### 3.1 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Dataset Discovery                                       │
│  ├── openml.datasets.list_datasets(tag='OpenML-CC18')           │
│  ├── Filter: upload_date >= 2019-01-01                          │
│  └── Output: dataset_ids.json (~3000 IDs)                       │
│                                                                  │
│  Step 2: Run Aggregation (per dataset)                          │
│  ├── openml.evaluations.list_evaluations(                       │
│  │       function='predictive_accuracy',                        │
│  │       data=dataset_id)                                       │
│  ├── Group by (flow_id, setup_id)                               │
│  ├── Filter: group_size >= 10                                   │
│  └── Output: matched_runs.parquet                               │
│                                                                  │
│  Step 3: Metadata Extraction                                     │
│  ├── openml.datasets.get_dataset(dataset_id)                    │
│  ├── Extract: description, default_target_attribute,            │
│  │           ignore_attribute, row_id_attribute, version        │
│  ├── Compute: metadata_completeness_score                       │
│  └── Output: metadata_scores.parquet                            │
│                                                                  │
│  Step 4: Reproducibility Metric Computation                      │
│  ├── For each (dataset, flow, setup) group:                     │
│  │   └── IQR = Q3(accuracy) - Q1(accuracy)                      │
│  └── Output: reproducibility_metrics.parquet                    │
│                                                                  │
│  Step 5: Feature Engineering                                     │
│  ├── Merge metadata_scores + reproducibility_metrics            │
│  ├── Add controls: intrinsic_stability, popularity, algo_family │
│  └── Output: analysis_dataset.parquet                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Code Template: Data Collection

```python
import openml
import pandas as pd
import numpy as np
from collections import defaultdict

def collect_datasets(min_date='2019-01-01'):
    """Fetch OpenML datasets uploaded after min_date."""
    datasets = openml.datasets.list_datasets(output_format='dataframe')
    datasets['upload_date'] = pd.to_datetime(datasets['upload_date'])
    return datasets[datasets['upload_date'] >= min_date]

def get_matched_runs(dataset_id, min_runs=10):
    """Get runs with ≥min_runs identical (flow, setup) configurations."""
    evals = openml.evaluations.list_evaluations(
        function='predictive_accuracy',
        data=[dataset_id],
        output_format='dataframe'
    )
    if evals.empty:
        return pd.DataFrame()
    
    grouped = evals.groupby(['flow_id', 'setup_id'])
    matched = grouped.filter(lambda x: len(x) >= min_runs)
    return matched

def compute_metadata_score(dataset):
    """Compute 5-field metadata completeness score."""
    score = 0
    desc = dataset.description or ''
    
    # Feature description
    if len(desc) > 100 and 'feature' in desc.lower():
        score += 1
    # Target description
    if dataset.default_target_attribute:
        score += 1
    # Missing value handling
    if 'missing' in desc.lower() or dataset.ignore_attribute:
        score += 1
    # Data collection context
    if any(kw in desc.lower() for kw in ['collected', 'source', 'origin']):
        score += 1
    # Version/changelog
    if dataset.version and dataset.version > 1:
        score += 1
    
    return score

def compute_reproducibility_iqr(runs_df):
    """Compute IQR of predictive_accuracy per (dataset, flow, setup)."""
    def iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)
    
    return runs_df.groupby(['data_id', 'flow_id', 'setup_id'])['value'].agg([
        ('iqr', iqr),
        ('mean', 'mean'),
        ('std', 'std'),
        ('count', 'count')
    ]).reset_index()
```

---

## 4. Statistical Analysis Plan

### 4.1 Primary Analysis: Mixed-Effects Regression

**Model Specification:**

```
IQR_ij ~ β0 + β1*M_i + β2*stability_i + β3*log(popularity_i) 
         + β4*algo_family_j + (1|dataset_i) + ε_ij
```

Where:
- `IQR_ij`: Reproducibility variance for dataset i, configuration j
- `M_i`: Metadata completeness score (0-5)
- `stability_i`: Intrinsic dataset stability (CV of features)
- `popularity_i`: Total run count for dataset
- `algo_family_j`: Categorical indicator for algorithm type
- `(1|dataset_i)`: Random intercept for dataset

### 4.2 Code Template: Mixed-Effects Model

```python
import statsmodels.formula.api as smf
import numpy as np

def fit_mixed_model(df):
    """Fit mixed-effects model for reproducibility analysis."""
    # Ensure proper types
    df['log_popularity'] = np.log1p(df['run_count'])
    df['algo_family'] = df['algo_family'].astype('category')
    
    # Mixed-effects model
    model = smf.mixedlm(
        "iqr ~ metadata_score + intrinsic_stability + log_popularity + algo_family",
        data=df,
        groups=df["dataset_id"]
    )
    result = model.fit()
    return result

def compute_quartile_effect(df):
    """Compute effect size: top quartile vs bottom quartile."""
    q1 = df['metadata_score'].quantile(0.25)
    q3 = df['metadata_score'].quantile(0.75)
    
    bottom = df[df['metadata_score'] <= q1]['iqr'].mean()
    top = df[df['metadata_score'] >= q3]['iqr'].mean()
    
    effect_pct = (bottom - top) / bottom * 100
    effect_abs = bottom - top
    
    return {
        'bottom_quartile_iqr': bottom,
        'top_quartile_iqr': top,
        'relative_reduction_pct': effect_pct,
        'absolute_reduction': effect_abs
    }
```

### 4.3 Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Relative IQR reduction | ≥20% | `(IQR_bottom - IQR_top) / IQR_bottom` |
| Absolute IQR reduction | ≥0.01 | `IQR_bottom - IQR_top` |
| 95% CI excludes | <10% | Bootstrap CI lower bound >10% |
| p-value for β1 | <0.05 | Mixed-effects coefficient test |

### 4.4 Falsification Criteria

| Condition | Action |
|-----------|--------|
| Effect <10% | FAIL: Effect too weak |
| CI includes 0 | FAIL: Effect not significant |
| Direction reversed (positive β1) | FAIL: Opposite to hypothesis |

---

## 5. Baseline Experiment Design

### 5.1 Null Baseline

**Purpose:** Establish what "no effect" looks like.

```python
def null_baseline(df, n_permutations=100):
    """Permutation test: shuffle metadata scores."""
    effects = []
    for _ in range(n_permutations):
        df_perm = df.copy()
        df_perm['metadata_score'] = np.random.permutation(df['metadata_score'])
        effect = compute_quartile_effect(df_perm)
        effects.append(effect['relative_reduction_pct'])
    
    return {
        'null_mean': np.mean(effects),
        'null_std': np.std(effects),
        'null_95_upper': np.percentile(effects, 95)
    }
```

### 5.2 Alternative Baseline

**Purpose:** Compare metadata effect to known strong predictor (dataset size).

```python
def size_baseline(df):
    """Use dataset size as predictor instead of metadata."""
    model = smf.mixedlm(
        "iqr ~ log_n_instances + intrinsic_stability + log_popularity + algo_family",
        data=df,
        groups=df["dataset_id"]
    )
    result = model.fit()
    return result.params['log_n_instances'], result.pvalues['log_n_instances']
```

---

## 6. Implementation Checklist

### 6.1 Phase 3 Tasks

| Task | Priority | Complexity | Estimated Time |
|------|----------|------------|----------------|
| OpenML API data collection script | P0 | Low | 2h |
| Metadata completeness scorer | P0 | Low | 1h |
| IQR computation module | P0 | Low | 1h |
| Mixed-effects model fitting | P0 | Medium | 2h |
| Quartile effect computation | P0 | Low | 1h |
| Permutation test baseline | P1 | Low | 1h |
| Bootstrap CI computation | P1 | Medium | 2h |
| Results visualization | P2 | Low | 1h |

### 6.2 Dependencies

```
openml>=0.14.0
pandas>=2.0.0
numpy>=1.24.0
statsmodels>=0.14.0
scipy>=1.10.0
```

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Insufficient datasets (< 200) | Medium | High | Relax matched-runs threshold to ≥5 |
| Metadata scores cluster (low variance) | Medium | High | Use continuous feature extraction instead of binary |
| OpenML API rate limits | Low | Medium | Cache responses, batch requests |
| Effect confounded by dataset quality | Medium | Medium | Include quality proxy controls |

---

## 8. Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Raw dataset metadata | Parquet | `data/raw/metadata.parquet` |
| Matched runs | Parquet | `data/raw/matched_runs.parquet` |
| Analysis dataset | Parquet | `data/processed/analysis.parquet` |
| Model results | JSON | `results/h_e1_model.json` |
| Effect sizes | JSON | `results/h_e1_effects.json` |
| Figures | PNG | `figures/h_e1_*.png` |

---

## 9. Validation Protocol

### 9.1 Pre-Analysis Checks

1. **Data Quality:** No missing IQR values, metadata scores in [0,5]
2. **Sample Size:** n_datasets ≥ 200, total_runs ≥ 5000
3. **Variance:** metadata_score std > 0.5 (sufficient spread)

### 9.2 Post-Analysis Checks

1. **Model Convergence:** No convergence warnings
2. **Residual Diagnostics:** No severe heteroscedasticity
3. **Influential Points:** Cook's D < 1 for all observations

---

## Appendix A: Metadata Completeness Scoring Rubric

| Field | Score | Detection Method |
|-------|-------|------------------|
| Feature description | +1 | `len(description) > 100 AND 'feature' in description` |
| Target description | +1 | `default_target_attribute IS NOT NULL` |
| Missing value handling | +1 | `'missing' in description OR ignore_attribute IS NOT NULL` |
| Data collection context | +1 | Keywords: 'collected', 'source', 'origin', 'study' |
| Version/changelog | +1 | `version > 1 OR 'version' in description` |

---

## Appendix B: OpenML API Reference

Key endpoints used:
- `openml.datasets.list_datasets()` - Dataset discovery
- `openml.datasets.get_dataset(id)` - Metadata extraction
- `openml.evaluations.list_evaluations()` - Run results
- `openml.flows.get_flow(id)` - Algorithm metadata
