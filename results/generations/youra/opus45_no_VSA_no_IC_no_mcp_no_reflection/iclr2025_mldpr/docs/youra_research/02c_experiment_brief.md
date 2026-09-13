# Experiment Brief: h-e1 Ranking Shift Existence

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-29

---

## 1. Statement

Under controlled evaluation conditions, if we compute Kendall-τ between ImageNet and ImageNet-V2 model rankings, then τ < 0.90 with p < 0.001, because benchmark-specific optimizations create non-uniform performance degradation.

---

## 2. Dataset Specification

| Field | Value |
|-------|-------|
| **Type** | standard |
| **Name** | ImageNet Model Rankings (Papers With Code) |
| **Source** | Papers With Code leaderboard + published papers |
| **URL** | paperswithcode.com/sota/image-classification-on-imagenet |
| **Minimum Size** | 30 models with both ImageNet and ImageNet-V2 results |
| **Target Size** | 50-100 models |

### Data Collection Protocol

1. **Primary Source:** Papers With Code "Image Classification on ImageNet" leaderboard
2. **Secondary Source:** Recht et al. (2019) supplementary materials
3. **Tertiary Source:** Individual paper tables (cross-validation)

### Required Fields Per Model

| Field | Type | Required |
|-------|------|----------|
| model_name | string | ✓ |
| imagenet_top1 | float | ✓ |
| imagenet_v2_top1 | float | ✓ |
| architecture_family | string | ✓ |
| publication_year | int | ✓ |
| param_count | float | optional |
| paper_source | string | ✓ |

### Data Quality Checks

- [ ] Minimum 30 models collected
- [ ] No duplicate model entries
- [ ] All accuracy values in [0, 100] range
- [ ] ImageNet-V2 accuracy < ImageNet accuracy (expected drop)
- [ ] 10% random sample cross-validated against original papers

---

## 3. Experimental Design

### 3.1 Variables

| Type | Variable | Operationalization |
|------|----------|-------------------|
| IV | Benchmark variant | ImageNet (original) vs ImageNet-V2 (matched frequency) |
| DV | Ranking correlation | Kendall-τ coefficient |
| CV | Model set | Same models evaluated on both benchmarks |
| CV | Task semantics | 1000-class ImageNet classification |
| CV | Evaluation protocol | Top-1 accuracy, standard preprocessing |

### 3.2 Analysis Pipeline

```
Step 1: Data Collection
├── Scrape Papers With Code leaderboard
├── Parse model names, ImageNet acc, V2 acc
├── Augment with architecture family, year
└── Quality checks (min 30 models)

Step 2: Ranking Computation
├── Rank models by ImageNet top-1 accuracy
├── Rank models by ImageNet-V2 top-1 accuracy
└── Handle ties with average ranks

Step 3: Statistical Analysis
├── Compute Kendall-τ coefficient
├── Bootstrap 95% confidence interval (10000 resamples)
├── Test H0: τ ≥ 0.95
└── Compute p-value for observed τ

Step 4: Sensitivity Analysis
├── Exclude models with <1% accuracy difference
├── Stratify by architecture family
└── Stratify by publication year bucket
```

### 3.3 Implementation

```python
# Core analysis (scipy implementation)
from scipy.stats import kendalltau
import numpy as np

def compute_ranking_correlation(df):
    """
    Compute Kendall-τ between ImageNet and V2 rankings.
    
    Args:
        df: DataFrame with columns [imagenet_top1, imagenet_v2_top1]
    
    Returns:
        tau: Kendall-τ coefficient
        p_value: Two-tailed p-value
        ci_low, ci_high: 95% bootstrap CI
    """
    # Compute ranks (higher accuracy = lower rank number)
    rank_imagenet = df['imagenet_top1'].rank(ascending=False)
    rank_v2 = df['imagenet_v2_top1'].rank(ascending=False)
    
    # Kendall-τ
    tau, p_value = kendalltau(rank_imagenet, rank_v2)
    
    # Bootstrap CI
    n_bootstrap = 10000
    tau_samples = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(df), len(df), replace=True)
        r1 = rank_imagenet.iloc[idx]
        r2 = rank_v2.iloc[idx]
        tau_samples.append(kendalltau(r1, r2)[0])
    
    ci_low = np.percentile(tau_samples, 2.5)
    ci_high = np.percentile(tau_samples, 97.5)
    
    return tau, p_value, ci_low, ci_high

def test_hypothesis(tau, ci_high, threshold=0.90):
    """
    Test h-e1: τ < 0.90 with 95% CI not including 0.95
    
    Returns:
        result: "PASS" | "FAIL" | "INCONCLUSIVE"
    """
    if tau < threshold and ci_high < 0.95:
        return "PASS"
    elif tau >= 0.95:
        return "FAIL"
    else:
        return "INCONCLUSIVE"
```

---

## 4. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary | τ < 0.90 | Kendall-τ coefficient |
| Secondary | 95% CI excludes 0.95 | Bootstrap upper bound |
| Tertiary | p < 0.001 | Statistical significance |

### Decision Matrix

| τ Value | CI Upper | Interpretation | Action |
|---------|----------|----------------|--------|
| < 0.85 | < 0.90 | Strong ranking shift | PASS → h-m1 |
| 0.85-0.90 | < 0.95 | Moderate ranking shift | PASS → h-m1 |
| 0.85-0.90 | ≥ 0.95 | Uncertain | INCONCLUSIVE |
| ≥ 0.90 | any | Weak/no ranking shift | FAIL |
| ≥ 0.95 | any | Rankings preserved | FAIL (H0 confirmed) |

---

## 5. Baseline Comparison

| Baseline | Expected τ | Purpose |
|----------|------------|---------|
| Random permutation | ~0.0 | Lower bound (no correlation) |
| Perfect correlation | 1.0 | Upper bound (identical rankings) |
| Measurement noise | ~0.98 | Expected under H0 with noise |
| Prior work (Recht 2019) | Not reported | Reference for accuracy drops |

---

## 6. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| <30 models available | Medium | High | Expand to secondary sources |
| Protocol inconsistencies | Low | High | Cross-validate 10% sample |
| τ near threshold | Medium | Medium | Report CI, interpret cautiously |
| Selection bias | Medium | Medium | Note as limitation |

---

## 7. Resource Requirements

| Resource | Specification |
|----------|---------------|
| Compute | Minimal (statistical analysis) |
| Data collection | 2-4 hours manual |
| Libraries | scipy, pandas, numpy |
| Validation | ~1 hour cross-check |

---

## 8. Deliverables

1. **data/imagenet_rankings.csv** - Collected model data
2. **scripts/h_e1_analysis.py** - Analysis implementation
3. **results/h_e1_results.json** - Statistical outputs
4. **04_validation.md** - Hypothesis validation report

---

## 9. Verification Protocol Summary

1. Collect ≥30 models with ImageNet + V2 results
2. Compute rankings for each benchmark
3. Calculate Kendall-τ with scipy.stats.kendalltau
4. Bootstrap 10000 samples for 95% CI
5. Test: τ < 0.90 AND CI_high < 0.95
6. Record result: PASS/FAIL/INCONCLUSIVE

---

*Generated by Phase 2C Experiment Design*
*Hypothesis: h-e1 (EXISTENCE, MUST_WORK)*
