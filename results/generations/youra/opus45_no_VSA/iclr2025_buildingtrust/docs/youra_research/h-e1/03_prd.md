# Phase 3: Product Requirements Document (PRD)

## Hypothesis: H-E1 (Existence)

**Statement:** λ₁,residual exceeds 95th percentile of permutation distribution after controlling for log(params) and release date.

**Type:** EXISTENCE | **Gate:** MUST_WORK

---

## 1. Executive Summary

### 1.1 Purpose
Implement a statistical analysis pipeline to test whether LLM benchmark correlations contain a latent factor structure (Generalized Representational Coherence) that survives confound control for model scale and release date.

### 1.2 Success Criteria
- λ₁,observed > 95th percentile of permutation null distribution
- p-value < 0.05
- PC1 variance explained > 20%

### 1.3 Scope
Single-hypothesis validation: existence of residual factor in LLM benchmarks.

---

## 2. Functional Requirements

### FR-01: Data Acquisition
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01.1 | Load Open LLM Leaderboard via HuggingFace datasets API | P0 |
| FR-01.2 | Extract 6 benchmark scores: IFEval, BBH, MATH-Hard, GPQA, MUSR, MMLU-Pro | P0 |
| FR-01.3 | Extract metadata: parameter count, release date, model family | P0 |
| FR-01.4 | Cache downloaded data locally | P1 |

### FR-02: Data Preprocessing
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-02.1 | Filter models with non-null parameter count | P0 |
| FR-02.2 | Filter models with ≥4 of 6 benchmark scores | P0 |
| FR-02.3 | Filter models released 2023-01-01 to 2025-12-31 | P0 |
| FR-02.4 | Compute log₁₀(parameter_count) | P0 |
| FR-02.5 | Standardize benchmark scores (z-score) | P0 |
| FR-02.6 | Handle missing values via column-mean imputation | P1 |

### FR-03: Confound Residualization
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-03.1 | OLS regression of each benchmark on log_params + release_date | P0 |
| FR-03.2 | Extract residuals as confound-controlled scores | P0 |
| FR-03.3 | Store residualized matrix for downstream analysis | P0 |

### FR-04: PCA Analysis
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-04.1 | Fit PCA on residualized benchmark matrix | P0 |
| FR-04.2 | Extract λ₁ (first eigenvalue) and variance explained | P0 |
| FR-04.3 | Extract PC1 loadings for interpretability | P0 |

### FR-05: Permutation Test
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-05.1 | Generate 1000 column-wise permuted null datasets | P0 |
| FR-05.2 | Compute λ₁ for each permuted dataset | P0 |
| FR-05.3 | Calculate p-value: (sum(null ≥ observed) + 1) / (n + 1) | P0 |
| FR-05.4 | Determine 95th percentile threshold | P0 |

### FR-06: Output Generation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-06.1 | Save results JSON with λ₁, p-value, variance explained | P0 |
| FR-06.2 | Generate permutation distribution plot | P1 |
| FR-06.3 | Generate scree plot of eigenvalues | P1 |
| FR-06.4 | Generate PC1 loadings bar chart | P1 |

---

## 3. Non-Functional Requirements

### NFR-01: Performance
- Complete full pipeline with 1000 permutations in < 5 minutes
- Handle up to 5000 models without memory issues

### NFR-02: Reproducibility
- Set random seed for permutation test
- Log all filtering decisions
- Version all dependencies in requirements.txt

### NFR-03: Validation
- Assert N ≥ 80 after filtering or raise informative error
- Report assumption checks (normality, VIF)

---

## 4. Data Contract

### 4.1 Input Schema
```yaml
open_llm_leaderboard:
  model_name: string
  ifeval: float [0-1] | null
  bbh: float [0-1] | null
  math_hard: float [0-1] | null
  gpqa: float [0-1] | null
  musr: float [0-1] | null
  mmlu_pro: float [0-1] | null
  params: int | null
  release_date: datetime | null
```

### 4.2 Output Schema
```yaml
h_e1_results:
  n_models: int
  lambda_1_observed: float
  lambda_1_95th_null: float
  p_value: float
  variance_explained_pc1: float
  pc1_loadings:
    ifeval: float
    bbh: float
    math_hard: float
    gpqa: float
    musr: float
    mmlu_pro: float
  hypothesis_passed: bool
```

---

## 5. Acceptance Criteria

| Criterion | Test |
|-----------|------|
| Data loads successfully | N > 0 after API call |
| Filtering works | N ≥ 80 after all filters |
| Residualization correct | OLS R² reported for each benchmark |
| PCA executes | 6 eigenvalues returned |
| Permutation valid | 1000 null λ₁ values stored |
| Output complete | All required fields in results JSON |
| Hypothesis decision | hypothesis_passed == (p_value < 0.05) |

---

## 6. Dependencies

```
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3
pandas>=2.0
datasets>=2.14
statsmodels>=0.14
matplotlib>=3.7
```

---

## 7. Deliverables

1. `h_e1_eigenvalue_test.py` - Main analysis script
2. `data_loader.py` - Data acquisition module
3. `preprocessing.py` - Filtering and standardization
4. `analysis.py` - PCA and permutation test
5. `visualization.py` - Plot generation
6. `outputs/h_e1_results.json` - Primary results
7. `outputs/*.png` - Visualizations

---

## 8. Timeline

| Phase | Duration |
|-------|----------|
| Implementation | 2 hours |
| Testing | 1 hour |
| Validation | 1 hour |
| Documentation | 30 min |

**Total:** ~4.5 hours
