# Phase 2C: Experiment Design Brief
**Hypothesis ID:** h-c1  
**Generated:** 2026-08-19  
**Status:** READY FOR PHASE 3

---

## 1. Hypothesis Statement

**H-C1 (SHOULD_WORK):** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair), demonstrating model-specific fingerprints.

**Type:** CONDITION  
**Gate:** SHOULD_WORK (failure does NOT block Phase 5)  
**Prerequisites:** h-e1 (PASS), h-m2 (FAILED)

---

## 2. Research Objective

### Primary Goal
Determine whether coupling patterns across trustworthiness dimensions are model-specific (behavioral fingerprints) or universal (architectural property shared across all LLMs).

### Success Criterion
- Mantel test correlation r < 0.7 between ≥1 model pair among:
  - GPT-4 vs Claude 3
  - GPT-4 vs Llama 3
  - Claude 3 vs Llama 3
- Low correlation (r < 0.7) indicates distinct coupling profiles → model-specific fingerprints
- High correlation (r > 0.9) indicates universal coupling → reframe as "architectural property"

### Scientific Contribution
- **IF PASS:** "Model-specific coupling fingerprints enable evidence-based model selection for deployment"
- **IF FAIL:** "Universal coupling architecture is a fundamental transformer property" (still publishable, alternative framing)

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Primary Dataset:** Real trustworthiness benchmark (NOT synthetic)

**Candidate Options (in priority order):**

1. **TrustLLM Benchmark** (Sun et al., 2024, 361 citations)
   - Covers 6 dimensions: truthfulness, safety, fairness, robustness, privacy, ethics
   - 30+ datasets, 16 models evaluated
   - API-based evaluation (no internal states required)
   - **Availability:** Publicly available via Hugging Face
   - **URL:** https://github.com/HowieHwong/TrustLLM

2. **DecodingTrust** (Wang et al., 2024)
   - 8 trustworthiness dimensions
   - Standardized evaluation protocol
   - Multiple model families tested
   - **URL:** https://decodingtrust.github.io/

3. **Fallback:** Composite from existing benchmarks
   - TruthfulQA (truthfulness)
   - AdvGLUE (robustness)
   - BBQ (fairness)
   - CValues (safety)
   - ConfAIde (privacy)

### 3.2 Sample Size

**Target:** 500 instances per model (NOT 10-50 trivial samples)

**Distribution:**
- 100 instances per dimension × 5 dimensions = 500 total
- Ensures statistical power for phi coefficient (minimum n=100 per contingency table)
- Balances computation cost vs. statistical validity

**Rationale for 500:**
- Chi-square test validity requires expected frequency ≥5 per cell
- Phi coefficient effect size detection (medium effect φ=0.3) needs n≥100 per pair
- 500 instances across 5 dimensions = 10 pairwise comparisons with sufficient power

### 3.3 Data Preparation

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

**Binary Classification:**
- Convert multi-class/regression scores to binary (pass/fail)
- Threshold: median split or domain-specific cutoff (e.g., truthfulness >0.7 = pass)
- Required for 2×2 contingency tables

**Preprocessing Steps:**
1. Load TrustLLM/DecodingTrust benchmark data
2. Sample 100 instances per dimension (stratified random sampling)
3. Binarize labels per dimension
4. Construct contingency tables for 10 dimension pairs per model

---

## 4. Experimental Protocol

### 4.1 Coupling Matrix Construction

**Per Model (3 models × 10 pairs = 30 phi coefficients):**

For each model (GPT-4, Claude-3, Llama-3):
1. Construct 10 pairwise 2×2 contingency tables:
   - (truthfulness, robustness)
   - (truthfulness, fairness)
   - (truthfulness, safety)
   - (truthfulness, privacy)
   - (robustness, fairness)
   - (robustness, safety)
   - (robustness, privacy)
   - (fairness, safety)
   - (fairness, privacy)
   - (safety, privacy)

2. Calculate phi coefficient for each pair:
   ```python
   from sklearn.metrics import matthews_corrcoef
   phi = matthews_corrcoef(dim1_labels, dim2_labels)
   ```

3. Assemble coupling matrix (5×5 symmetric, 10 unique values):
   ```
   Coupling Matrix (Model X):
             truth  robust  fair  safe  priv
   truth     1.0    φ_1     φ_2   φ_3   φ_4
   robust    φ_1    1.0     φ_5   φ_6   φ_7
   fair      φ_2    φ_5     1.0   φ_8   φ_9
   safe      φ_3    φ_6     φ_8   1.0   φ_10
   priv      φ_4    φ_7     φ_9   φ_10  1.0
   ```

### 4.2 Mantel Test Procedure

**Implementation:**
```python
import mantel  # pip install mantel (jwcarr/mantel, 37 stars, MIT)
# OR
from skbio.stats.distance import mantel  # scikit-bio

# Pairwise Mantel tests
models = ["GPT-4", "Claude-3", "Llama-3"]
for i, model_a in enumerate(models):
    for model_b in models[i+1:]:
        matrix_a = coupling_matrices[model_a]  # 5×5 phi matrix
        matrix_b = coupling_matrices[model_b]  # 5×5 phi matrix
        
        result = mantel.test(matrix_a, matrix_b, 
                            perms=10000, 
                            method='pearson', 
                            tail='two-tail')
        print(f"{model_a} vs {model_b}: r={result.r:.3f}, p={result.p:.4f}")
```

**Interpretation:**
- r < 0.7: Models have distinct coupling profiles → PASS
- 0.7 ≤ r < 0.9: Moderate similarity → PARTIAL
- r ≥ 0.9: Nearly identical coupling → FAIL (universal coupling)

### 4.3 Statistical Significance

**Hypothesis Test:**
- H0: Coupling matrices are identical (permutation null)
- Ha: Coupling matrices differ significantly
- Significance level: α = 0.05
- Permutations: 10,000 (sufficient for p-value precision)

**Bonferroni Correction:**
- 3 pairwise comparisons → adjusted α = 0.05/3 = 0.0167
- Conservative correction for multiple testing

---

## 5. Baseline Comparison (NOT APPLICABLE)

**Note:** H-C1 does not compare against baselines. It measures cross-model matrix correlation. Baseline comparison occurs in Phase 5 for the overall hypothesis verification.

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

1. **Mantel Correlation Coefficient (r)**
   - Range: [-1, 1]
   - Measures linear correlation between coupling matrices
   - Threshold: r < 0.7 for PASS

2. **Mantel Test p-value**
   - Permutation-based significance
   - Threshold: p < 0.0167 (Bonferroni-corrected)

### 6.2 Secondary Metrics

3. **Frobenius Norm Distance**
   - ||Matrix_A - Matrix_B||_F
   - Measures element-wise dissimilarity
   - Provides absolute distance metric

4. **Phi Coefficient Statistics (per model)**
   - Mean phi across 10 pairs
   - Max/min phi values
   - Number of significant pairs (phi ≥ 0.3, p < 0.01)

### 6.3 Visualization

**Heatmaps:**
- 3 coupling matrices (one per model)
- Side-by-side comparison
- Diverging colormap (blue-white-red, centered at 0)

**Scatter Plot:**
- X-axis: Model A phi values (flattened upper triangle)
- Y-axis: Model B phi values (flattened upper triangle)
- Linear regression line + r² value
- Annotate dimension pairs

---

## 7. Implementation Code Examples

### 7.1 Phi Coefficient Calculation

**Source:** sklearn.metrics.matthews_corrcoef  
**Verified:** [VERIFIED - EXA - CODE_CONTEXT]

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
    # Phi coefficient (Matthews correlation coefficient)
    phi = matthews_corrcoef(dim1_labels, dim2_labels)
    
    # Construct 2×2 contingency table
    contingency = np.array([
        [np.sum((dim1_labels == 1) & (dim2_labels == 1)),  # both pass
         np.sum((dim1_labels == 1) & (dim2_labels == 0))], # dim1 pass, dim2 fail
        [np.sum((dim1_labels == 0) & (dim2_labels == 1)),  # dim1 fail, dim2 pass
         np.sum((dim1_labels == 0) & (dim2_labels == 0))]  # both fail
    ])
    
    # Chi-square test for significance
    chi2, p_value, dof, expected = chi2_contingency(contingency)
    
    return phi, p_value

# Example usage
dim1 = np.array([1, 1, 0, 1, 0, 0, 1, 1, 0, 1])  # truthfulness
dim2 = np.array([1, 0, 0, 1, 0, 1, 1, 0, 0, 1])  # robustness
phi, p = compute_phi_coefficient(dim1, dim2)
print(f"Phi coefficient: {phi:.3f}, p-value: {p:.4f}")
```

### 7.2 Mantel Test Implementation

**Source:** jwcarr/mantel (PyPI package)  
**Verified:** [VERIFIED - EXA] - https://github.com/jwcarr/mantel (37 stars, MIT license)

```python
import mantel
import numpy as np

def compare_coupling_matrices(matrix_a, matrix_b, perms=10000):
    """
    Compare two coupling matrices using Mantel test.
    
    Args:
        matrix_a: np.array (5×5) coupling matrix for model A
        matrix_b: np.array (5×5) coupling matrix for model B
        perms: int, number of permutations for significance test
    
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

# Example usage
coupling_gpt4 = np.array([
    [1.0, 0.35, 0.28, 0.31, 0.22],
    [0.35, 1.0, 0.40, 0.33, 0.25],
    [0.28, 0.40, 1.0, 0.38, 0.30],
    [0.31, 0.33, 0.38, 1.0, 0.27],
    [0.22, 0.25, 0.30, 0.27, 1.0]
])

coupling_claude = np.array([
    [1.0, 0.42, 0.20, 0.25, 0.18],
    [0.42, 1.0, 0.35, 0.28, 0.22],
    [0.20, 0.35, 1.0, 0.45, 0.38],
    [0.25, 0.28, 0.45, 1.0, 0.32],
    [0.18, 0.22, 0.38, 0.32, 1.0]
])

r, p, z = compare_coupling_matrices(coupling_gpt4, coupling_claude)
print(f"GPT-4 vs Claude-3: r={r:.3f}, p={p:.4f}, z={z:.2f}")
```

**Alternative Implementation (scikit-bio):**
```python
from skbio.stats.distance import mantel

# Convert coupling matrices to distance matrices (1 - phi)
dist_a = 1 - coupling_gpt4
dist_b = 1 - coupling_claude

r, p, n = mantel(dist_a, dist_b, 
                 method='pearson', 
                 permutations=10000, 
                 alternative='two-sided')
```

---

## 8. Expected Outcomes

### 8.1 Scenario A: PASS (r < 0.7 for ≥1 pair)

**Example Result:**
```
GPT-4 vs Claude-3: r = 0.58, p = 0.003
GPT-4 vs Llama-3:  r = 0.65, p = 0.012
Claude-3 vs Llama-3: r = 0.72, p = 0.028
```

**Interpretation:**
- GPT-4 and Claude-3 show distinct coupling profiles (r=0.58 < 0.7)
- Model-specific fingerprints confirmed
- **Contribution:** "Coupling patterns as model selection criteria for deployment"

### 8.2 Scenario B: FAIL (r ≥ 0.9 for all pairs)

**Example Result:**
```
GPT-4 vs Claude-3: r = 0.94, p = 0.321
GPT-4 vs Llama-3:  r = 0.92, p = 0.412
Claude-3 vs Llama-3: r = 0.96, p = 0.287
```

**Interpretation:**
- All models exhibit nearly identical coupling patterns
- Universal coupling is a transformer architectural property
- **Reframe Contribution:** "First characterization of universal coupling architecture in LLMs"
- **Still publishable:** Negative result refutes model-specific hypothesis but establishes new fundamental property

### 8.3 Scenario C: PARTIAL (0.7 ≤ r < 0.9)

**Example Result:**
```
GPT-4 vs Claude-3: r = 0.78, p = 0.045
GPT-4 vs Llama-3:  r = 0.82, p = 0.067
Claude-3 vs Llama-3: r = 0.75, p = 0.038
```

**Interpretation:**
- Moderate similarity with some model-specific variation
- **Contribution:** "Coupling shows both universal and model-specific components"

---

## 9. Risk Mitigation

### 9.1 Risk: Cross-Model Homogeneity (40% likelihood)

**Symptom:** Mantel r > 0.9 for all pairs

**Mitigation:**
1. **Pre-experiment check:** Verify that prerequisite h-m2 showed variation in coupling strength across models (even if FAILED on multi-pair criterion)
2. **Alternative framing:** Prepare "universal coupling" narrative for publication
3. **Additional analysis:** Compute partial correlations controlling for model size/architecture to identify residual model-specific effects

**Fallback Success Tier:** Tier 2 (publishable negative result)

### 9.2 Risk: Insufficient Coupling Variation (30% likelihood)

**Symptom:** All phi coefficients in narrow range (e.g., 0.25-0.35) across all models

**Mitigation:**
1. Increase sample size to 1000 instances per model (improves phi estimate precision)
2. Use dimension-specific thresholds for binarization (instead of median split)
3. Report narrow effect sizes honestly with confidence intervals

### 9.3 Risk: Dataset Unavailability (10% likelihood)

**Symptom:** TrustLLM/DecodingTrust data not accessible or insufficient coverage

**Mitigation:**
1. **Fallback 1:** Composite benchmark from individual datasets (TruthfulQA + AdvGLUE + BBQ + CValues + ConfAIde)
2. **Fallback 2:** Use API calls to evaluate models on benchmark instances (reproduce evaluations)
3. **Timeline impact:** +1 week for data collection

---

## 10. Academic Literature Context

### 10.1 Multi-Dimensional Trustworthiness Evaluation

**[VERIFIED - SCHOLAR]** "TrustLLM: Trustworthiness in Large Language Models" (Sun et al., 2024)
- **Citations:** 361
- **Semantic Scholar ID:** fb4dc0178e5d7347b1615c48caf05347b6e5eb48
- **URL:** https://www.semanticscholar.org/paper/fb4dc0178e5d7347b1615c48caf05347b6e5eb48
- **Key Contribution:** 8-dimension trustworthiness framework (truthfulness, safety, fairness, robustness, privacy, ethics, toxicity, bias)
- **Relevance:** Provides standardized benchmark and evaluation protocol for our coupling analysis
- **Search Query:** "multi-dimensional trustworthiness evaluation large language models"

**[VERIFIED - SCHOLAR]** "Enhancing Multiple Dimensions of Trustworthiness in LLMs via Sparse Activation Control" (Xiao et al., 2024)
- **Citations:** 9
- **Semantic Scholar ID:** 09992d02d809c9598c192277ec24c918849beca0
- **URL:** https://www.semanticscholar.org/paper/09992d02d809c9598c192277ec24c918849beca0
- **Key Contribution:** Demonstrates coupling between honesty, safety, and factuality dimensions via sparse activation control
- **Relevance:** Provides mechanistic evidence for dimension coupling (supports our behavioral coupling hypothesis)
- **Search Query:** "model-specific coupling patterns trustworthiness dimensions language models"

### 10.2 Trade-offs Between Trustworthiness Dimensions

**[VERIFIED - SCHOLAR]** "Triangular Trade-off between Robustness, Accuracy, and Fairness in Deep Neural Networks: A Survey" (Li & Li, 2024)
- **Citations:** 32
- **Semantic Scholar ID:** 13b0444d079bea1c8c57a6082200b67ab5f4616e
- **URL:** https://www.semanticscholar.org/paper/13b0444d079bea1c8c57a6082200b67ab5f4616e
- **Key Contribution:** Systematic analysis of trade-offs between robustness, accuracy, and fairness
- **Relevance:** Establishes precedent for dimension coupling (trade-offs = negative coupling)
- **Search Query:** "correlation analysis fairness robustness safety neural networks"

### 10.3 Mantel Test Applications

**[VERIFIED - EXA]** jwcarr/mantel - Python implementation
- **GitHub:** https://github.com/jwcarr/mantel
- **Stars:** 37 | **License:** MIT
- **PyPI:** https://pypi.org/project/mantel/ (v2.2.3, updated 2025-12-09)
- **Dependencies:** numpy ≥1.10, scipy ≥1.0
- **Relevance:** Production-ready Mantel test implementation for coupling matrix comparison

**[VERIFIED - EXA - CODE_CONTEXT]** scikit-bio Mantel implementation
- **GitHub:** https://github.com/scikit-bio/scikit-bio/blob/main/skbio/stats/distance/_mantel.py
- **Function:** `skbio.stats.distance.mantel(x, y, method='pearson', permutations=999)`
- **Features:** Pearson/Spearman/Kendall correlation, automatic ID matching for distance matrices
- **Relevance:** Alternative implementation with additional statistical tests

### 10.4 Phi Coefficient Resources

**[VERIFIED - EXA - CODE_CONTEXT]** sklearn.metrics.matthews_corrcoef
- **Documentation:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html
- **Equivalence:** Matthews correlation coefficient = phi coefficient for 2×2 tables
- **Formula:** φ = (n11·n00 - n10·n01) / √(n1·n0·n·0·n·1)
- **Relevance:** Standard implementation for binary coupling measurement

**[VERIFIED - EXA]** KaveIO/PhiK - Advanced phi_k correlation library
- **GitHub:** https://github.com/kaveio/phik
- **Stars:** 171 | **License:** Apache 2.0
- **Features:** Works with categorical, ordinal, and interval variables
- **Paper:** Frontiers in Applied Mathematics and Statistics (2020)
- **Relevance:** Generalization of phi coefficient for non-binary data (future extension)

---

## 11. Implementation Resources

### 11.1 GitHub Repositories

1. **[VERIFIED - EXA]** jwcarr/mantel
   - **URL:** https://github.com/jwcarr/mantel
   - **Priority:** 1
   - **Stars:** 37 | **Language:** Python
   - **Last Updated:** 2025-12-09
   - **Key Features:** Pearson/Spearman correlation, permutation testing, deterministic mode
   - **Integration:** `pip install mantel` → Direct import

2. **[VERIFIED - EXA]** scikit-bio (Mantel module)
   - **URL:** https://github.com/scikit-bio/scikit-bio/blob/main/skbio/stats/distance/_mantel.py
   - **Priority:** 2
   - **Language:** Python (with Cython/Numba optimization)
   - **Key Features:** Multiple correlation methods, automatic ID matching, engine selection
   - **Integration:** `pip install scikit-bio` → `from skbio.stats.distance import mantel`

### 11.2 Tutorial Resources

**[VERIFIED - EXA - TUTORIAL]** Phi Coefficient Wikipedia
- **URL:** https://en.wikipedia.org/wiki/Phi_coefficient
- **Content:** Mathematical derivation, relationship to chi-square, interpretation guidelines
- **Key Insight:** φ² = χ²/n (phi squared equals chi-square statistic divided by sample size)

**[VERIFIED - EXA - CODE_CONTEXT]** SciPy Contingency Analysis
- **URL:** https://docs.scipy.org/doc/scipy/reference/stats.contingency.html
- **Functions:** `chi2_contingency`, `association` (Cramer's V, Tschuprow's T, Pearson's C)
- **Relevance:** Provides statistical significance tests for coupling measurements

---

## 12. Success Criteria Summary

### 12.1 Technical Validation

✅ **Coupling matrices constructed:** 3 models × 5×5 matrices (10 unique phi values each)  
✅ **Mantel tests executed:** 3 pairwise comparisons (GPT-4 vs Claude, GPT-4 vs Llama, Claude vs Llama)  
✅ **Statistical significance:** p < 0.0167 (Bonferroni-corrected) for ≥1 pair with r < 0.7  
✅ **Sample size:** 500 instances per model (100 per dimension)  
✅ **Real data:** TrustLLM or equivalent benchmark (NOT synthetic)

### 12.2 Gate Decision

**PASS:** Mantel r < 0.7 for ≥1 model pair (p < 0.0167)  
**PARTIAL:** 0.7 ≤ r < 0.9 (moderate similarity)  
**FAIL:** r ≥ 0.9 for all pairs (universal coupling)

**Impact on Phase 5 Progression:**
- PASS/PARTIAL/FAIL → All routes proceed to Phase 5 (SHOULD_WORK gate)
- Failure does NOT block pipeline
- Contribution framing adjusted based on outcome

---

## 13. Next Steps (Automatic Transition)

**Phase 2C → Phase 3 Trigger:**
1. Generate implementation plan (PRD, Architecture, Logic, Config)
2. Create Archon task breakdown (Epic-level decomposition)
3. Determine implementation tier (LIGHT vs FULL)
4. Estimate token budget for Phase 4 coding

**Expected Timeline:**
- Phase 3 (Implementation Planning): 3 hours
- Phase 4 (PoC Validation): 6 hours
- Total: 9 hours for h-c1

---

**Experiment Design Status:** COMPLETED  
**Phase 2C Output:** /docs/youra_research/h-c1/02c_experiment_brief.md  
**Ready for Phase 3:** YES
