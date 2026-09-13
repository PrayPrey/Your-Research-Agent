# Product Requirements Document: h-e1

**Hypothesis:** Metadata completeness score correlates with reduced reproducibility variance (≥20% IQR reduction, ≥0.01 absolute) after controlling for intrinsic stability, popularity, algorithm family, and infrastructure.

**Generated:** 2026-08-09  
**Type:** EXISTENCE | Gate: MUST_WORK

---

## 1. Executive Summary

This experiment tests whether higher metadata completeness in OpenML datasets predicts lower reproducibility variance (IQR of predictive_accuracy) across matched experimental runs. The core claim: richer documentation constrains preprocessing degrees of freedom, reducing variance.

---

## 2. Problem Statement

Reproducibility in ML experiments varies widely. We hypothesize that datasets with more complete metadata documentation exhibit lower variance in replicated runs because practitioners have clearer guidance on preprocessing choices.

---

## 3. Functional Requirements

### FR-1: Data Collection Module
- **FR-1.1**: Query OpenML API for datasets uploaded 2019-2024
- **FR-1.2**: Filter to supervised classification tasks
- **FR-1.3**: Aggregate runs by (dataset_id, flow_id, setup_id) with ≥10 matched runs
- **FR-1.4**: Extract metadata fields for completeness scoring

### FR-2: Metadata Completeness Scorer
- **FR-2.1**: Compute 5-field score (0-5 scale):
  - Feature description present (+1)
  - Target description present (+1)
  - Missing value handling documented (+1)
  - Data collection context documented (+1)
  - Version/changelog present (+1)

### FR-3: Reproducibility Metric Computation
- **FR-3.1**: Compute IQR of predictive_accuracy per (dataset, flow, setup) group
- **FR-3.2**: Compute mean, std, count per group

### FR-4: Control Variable Extraction
- **FR-4.1**: Intrinsic stability (CV of features)
- **FR-4.2**: Popularity (log run count)
- **FR-4.3**: Algorithm family classification
- **FR-4.4**: sklearn version distribution

### FR-5: Statistical Analysis
- **FR-5.1**: Mixed-effects regression with random intercepts per dataset
- **FR-5.2**: Quartile effect computation (top vs bottom quartile)
- **FR-5.3**: Bootstrap 95% CI for effect size

### FR-6: Baseline Comparisons
- **FR-6.1**: Null baseline via permutation test (100 permutations)
- **FR-6.2**: Size baseline using log(n_instances) as predictor

---

## 4. Non-Functional Requirements

### NFR-1: Data Quality
- No missing IQR values
- Metadata scores in valid range [0,5]
- n_datasets ≥ 200, total_runs ≥ 5000

### NFR-2: Statistical Rigor
- Model convergence without warnings
- Residual diagnostics pass (no severe heteroscedasticity)
- Cook's D < 1 for all observations

### NFR-3: Performance
- API rate limiting compliance (batch requests, caching)
- Total execution time < 30 minutes

---

## 5. Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Relative IQR reduction | ≥20% | (IQR_bottom - IQR_top) / IQR_bottom |
| Absolute IQR reduction | ≥0.01 | IQR_bottom - IQR_top |
| 95% CI lower bound | >10% | Bootstrap CI |
| p-value for β1 | <0.05 | Mixed-effects coefficient test |

---

## 6. Falsification Criteria

| Condition | Result |
|-----------|--------|
| Effect <10% | FAIL |
| CI includes 0 | FAIL |
| Direction reversed (positive β1) | FAIL |

---

## 7. Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Raw metadata | Parquet | data/raw/metadata.parquet |
| Matched runs | Parquet | data/raw/matched_runs.parquet |
| Analysis dataset | Parquet | data/processed/analysis.parquet |
| Model results | JSON | results/h_e1_model.json |
| Effect sizes | JSON | results/h_e1_effects.json |
| Figures | PNG | figures/h_e1_*.png |

---

## 8. Dependencies

```
openml>=0.14.0
pandas>=2.0.0
numpy>=1.24.0
statsmodels>=0.14.0
scipy>=1.10.0
```

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Insufficient datasets (<200) | Medium | High | Relax threshold to ≥5 runs |
| Metadata scores cluster | Medium | High | Use continuous extraction |
| API rate limits | Low | Medium | Cache responses |
| Confounding by quality | Medium | Medium | Add quality controls |
