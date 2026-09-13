# Product Requirements Document (PRD)
**Hypothesis ID:** h-c1  
**Date:** 2026-08-19  
**Phase:** 3 (Implementation Planning)

---

## Executive Summary

**Objective:** Implement experiment to test whether coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair), demonstrating model-specific fingerprints.

**Hypothesis Statement:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair), demonstrating model-specific fingerprints.

**Gate Type:** SHOULD_WORK (failure does NOT block Phase 5)

**Success Criterion:** Mantel correlation r < 0.7 between ≥1 model pair among GPT-4 vs Claude-3, GPT-4 vs Llama-3, Claude-3 vs Llama-3, with p < 0.0167 (Bonferroni-corrected).

---

## Problem Statement

### Research Question
Are coupling patterns across trustworthiness dimensions model-specific (behavioral fingerprints) or universal (architectural property shared across all LLMs)?

### Prerequisites
- **h-e1 (PASS):** Confirmed coupling exists between trustworthiness dimensions
- **h-m2 (FAILED):** Multi-pair coupling not established across models

### Expected Contribution
- **IF PASS:** "Model-specific coupling fingerprints enable evidence-based model selection for deployment"
- **IF FAIL:** "Universal coupling architecture is a fundamental transformer property" (publishable negative result)

---

## Functional Requirements

### FR-1: Dataset Loading and Preparation
**Priority:** P0  
**Description:** Load TrustLLM benchmark data with 500 instances per model (100 per dimension × 5 dimensions)

**Acceptance Criteria:**
- Load TrustLLM benchmark data for 3 models: GPT-4, Claude-3, Llama-3
- Extract 5 dimensions: truthfulness, robustness, fairness, safety, privacy
- Sample 100 instances per dimension (stratified random sampling)
- Binarize labels per dimension (pass/fail threshold)
- Total: 500 instances × 3 models = 1500 data points

**Fallback:** If TrustLLM unavailable, use DecodingTrust or composite benchmark (TruthfulQA + AdvGLUE + BBQ + CValues + ConfAIde)

**Input Format:**
```python
{
  "instance_id": str,
  "dimension": str,  # truthfulness, robustness, fairness, safety, privacy
  "prompt": str,
  "reference_answer": str,
  "model": str,      # GPT-4, Claude-3, Llama-3
  "binary_label": int  # 0=fail, 1=pass
}
```

---

### FR-2: Phi Coefficient Calculation
**Priority:** P0  
**Description:** Compute phi coefficients for 10 dimension pairs per model (30 total coefficients)

**Acceptance Criteria:**
- For each model, construct 10 pairwise 2×2 contingency tables
- Calculate phi coefficient using `sklearn.metrics.matthews_corrcoef`
- Calculate chi-square test p-value using `scipy.stats.chi2_contingency`
- Return 5×5 symmetric coupling matrix per model (diagonal = 1.0, 10 unique off-diagonal values)

**Dimension Pairs (10 combinations):**
1. truthfulness ↔ robustness
2. truthfulness ↔ fairness
3. truthfulness ↔ safety
4. truthfulness ↔ privacy
5. robustness ↔ fairness
6. robustness ↔ safety
7. robustness ↔ privacy
8. fairness ↔ safety
9. fairness ↔ privacy
10. safety ↔ privacy

**Output:**
```python
coupling_matrix = np.array([
    [1.0, φ_1, φ_2, φ_3, φ_4],
    [φ_1, 1.0, φ_5, φ_6, φ_7],
    [φ_2, φ_5, 1.0, φ_8, φ_9],
    [φ_3, φ_6, φ_8, 1.0, φ_10],
    [φ_4, φ_7, φ_9, φ_10, 1.0]
])
```

---

### FR-3: Mantel Test Execution
**Priority:** P0  
**Description:** Compare coupling matrices across 3 model pairs using Mantel test

**Acceptance Criteria:**
- Perform 3 pairwise Mantel tests:
  - GPT-4 vs Claude-3
  - GPT-4 vs Llama-3
  - Claude-3 vs Llama-3
- Use `mantel` package (jwcarr/mantel) OR `skbio.stats.distance.mantel`
- Permutations: 10,000 (for p-value precision)
- Method: Pearson correlation
- Tail: two-tailed test
- Return: (r, p-value, z-score) per pair

**Statistical Significance:**
- Bonferroni correction: α = 0.05/3 = 0.0167
- Significant if p < 0.0167

**Implementation:**
```python
import mantel
result = mantel.test(matrix_a, matrix_b, perms=10000, method='pearson', tail='two-tail')
# Returns: result.r (correlation), result.p (p-value), result.z (z-score)
```

---

### FR-4: Secondary Metrics Calculation
**Priority:** P1  
**Description:** Compute Frobenius norm distance and phi coefficient statistics

**Acceptance Criteria:**
- **Frobenius Norm:** ||Matrix_A - Matrix_B||_F for each model pair
- **Phi Statistics (per model):**
  - Mean phi across 10 pairs
  - Max/min phi values
  - Number of significant pairs (phi ≥ 0.3, p < 0.01)

---

### FR-5: Visualization Generation
**Priority:** P1  
**Description:** Generate heatmaps and scatter plots for coupling matrix comparison

**Acceptance Criteria:**
- **Heatmaps:** 3 coupling matrices (one per model), side-by-side, diverging colormap (blue-white-red, centered at 0)
- **Scatter Plot:** X-axis = Model A phi values (flattened upper triangle), Y-axis = Model B phi values, linear regression line + r² value, annotate dimension pairs

---

### FR-6: Results Reporting
**Priority:** P0  
**Description:** Generate validation report with gate decision

**Acceptance Criteria:**
- Display Mantel test results table (3 rows: model pairs, r, p-value, significance)
- Gate decision logic:
  - **PASS:** r < 0.7 for ≥1 pair with p < 0.0167
  - **PARTIAL:** 0.7 ≤ r < 0.9 for ≥1 pair
  - **FAIL:** r ≥ 0.9 for all pairs
- Save report to `04_validation.md`

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Chi-square test validity: expected frequency ≥5 per cell in 2×2 tables
- Sample size: minimum 100 instances per dimension pair for phi coefficient

### NFR-2: Reproducibility
- Random seed for stratified sampling
- Deterministic permutation test mode (if available)
- Log random seed in validation report

### NFR-3: Performance
- Mantel test execution time: <10 seconds per pair (30 seconds total for 3 pairs)
- Total experiment runtime: <5 minutes (data loading + phi calculation + Mantel tests)

### NFR-4: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Unit tests for phi coefficient calculation
- Integration test for full pipeline

---

## Dependencies

### External Libraries
- `numpy` ≥1.20
- `scipy` ≥1.7 (chi2_contingency)
- `scikit-learn` ≥1.0 (matthews_corrcoef)
- `mantel` ≥2.0 (jwcarr/mantel) OR `scikit-bio` ≥0.5
- `matplotlib` ≥3.5 (visualization)
- `pandas` ≥1.3 (data handling)

### Prerequisite Hypotheses
- **h-e1:** Provides validated coupling measurement methodology (phi coefficient + chi-square test)

---

## Data Requirements

### Input Data
- **Primary:** TrustLLM benchmark (https://github.com/HowieHwong/TrustLLM)
- **Format:** JSON or CSV with columns: instance_id, dimension, prompt, reference_answer, model, binary_label
- **Size:** 1500 instances (500 per model × 3 models)

### Output Data
- **Coupling Matrices:** 3 × (5×5 numpy arrays) saved as `.npy` files
- **Mantel Results:** CSV with columns: model_pair, r, p_value, z_score, significant
- **Phi Statistics:** JSON with per-model stats (mean, max, min, n_significant)
- **Validation Report:** Markdown file `04_validation.md`

---

## Success Criteria

### Technical Validation
✅ Coupling matrices constructed: 3 models × 5×5 matrices (10 unique phi values each)  
✅ Mantel tests executed: 3 pairwise comparisons  
✅ Statistical significance: p < 0.0167 for ≥1 pair with r < 0.7  
✅ Sample size: 500 instances per model  
✅ Real data: TrustLLM or equivalent benchmark (NOT synthetic)

### Gate Decision
- **PASS:** Mantel r < 0.7 for ≥1 model pair (p < 0.0167)
- **PARTIAL:** 0.7 ≤ r < 0.9 (moderate similarity)
- **FAIL:** r ≥ 0.9 for all pairs (universal coupling)

### Impact on Phase 5 Progression
All outcomes (PASS/PARTIAL/FAIL) proceed to Phase 5 (SHOULD_WORK gate). Failure does NOT block pipeline. Contribution framing adjusted based on outcome.

---

## Risk Mitigation

### Risk 1: Cross-Model Homogeneity (40% likelihood)
**Symptom:** Mantel r > 0.9 for all pairs  
**Mitigation:**  
1. Pre-experiment check: Verify h-m2 showed variation in coupling strength across models
2. Alternative framing: Prepare "universal coupling" narrative
3. Additional analysis: Partial correlations controlling for model size/architecture

**Fallback Success Tier:** Tier 2 (publishable negative result)

### Risk 2: Insufficient Coupling Variation (30% likelihood)
**Symptom:** All phi coefficients in narrow range (0.25-0.35) across all models  
**Mitigation:**  
1. Increase sample size to 1000 instances per model
2. Use dimension-specific thresholds for binarization
3. Report narrow effect sizes with confidence intervals

### Risk 3: Dataset Unavailability (10% likelihood)
**Symptom:** TrustLLM/DecodingTrust data not accessible  
**Mitigation:**  
1. Fallback 1: Composite benchmark (TruthfulQA + AdvGLUE + BBQ + CValues + ConfAIde)
2. Fallback 2: API calls to reproduce evaluations
3. Timeline impact: +1 week for data collection

---

## Out of Scope

- Mechanistic analysis of why coupling patterns differ (focus: behavioral fingerprints)
- Training new models or fine-tuning (use pre-existing evaluations)
- More than 3 models (limited by computational cost and statistical power)
- Non-trustworthiness dimensions (e.g., performance, efficiency)

---

## Appendix: Code Examples

### Phi Coefficient Calculation
```python
import numpy as np
from sklearn.metrics import matthews_corrcoef
from scipy.stats import chi2_contingency

def compute_phi_coefficient(dim1_labels, dim2_labels):
    """
    Compute phi coefficient for two binary dimension arrays.
    
    Args:
        dim1_labels: np.array of binary labels (0/1) for dimension 1
        dim2_labels: np.array of binary labels (0/1) for dimension 2
    
    Returns:
        phi: float, phi coefficient
        p_value: float, chi-square test p-value
    """
    phi = matthews_corrcoef(dim1_labels, dim2_labels)
    
    contingency = np.array([
        [np.sum((dim1_labels == 1) & (dim2_labels == 1)),
         np.sum((dim1_labels == 1) & (dim2_labels == 0))],
        [np.sum((dim1_labels == 0) & (dim2_labels == 1)),
         np.sum((dim1_labels == 0) & (dim2_labels == 0))]
    ])
    
    chi2, p_value, dof, expected = chi2_contingency(contingency)
    
    return phi, p_value
```

### Mantel Test
```python
import mantel
import numpy as np

def compare_coupling_matrices(matrix_a, matrix_b, perms=10000):
    """
    Compare two coupling matrices using Mantel test.
    
    Args:
        matrix_a: np.array (5×5) coupling matrix for model A
        matrix_b: np.array (5×5) coupling matrix for model B
        perms: int, number of permutations
    
    Returns:
        r: float, Mantel correlation coefficient
        p: float, permutation p-value
        z: float, z-score
    """
    result = mantel.test(matrix_a, matrix_b, 
                         perms=perms, 
                         method='pearson', 
                         tail='two-tail')
    return result.r, result.p, result.z
```

---

**PRD Status:** COMPLETE  
**Next Phase:** Architecture Design (Step 3)
