# Experiment Design: H-M3

**Date:** 2026-03-21
**Author:** Anonymous
**Hypothesis Statement:** Bootstrap CI width ≤ 50% for variance estimates from N=30 samples
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Analysis-only validation of variance estimation stability.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m2 (COMPLETED - PASS)
**Gate Status:** SHOULD_WORK gate

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (Different local minima validation)

### Gate Condition
**SHOULD_WORK** - If fails: EXPLORE - N=30 may be insufficient for stable estimation despite Rajput 2023, add N sensitivity analysis

---

## Continuation Context

This is the final mechanism hypothesis in the causal validation chain:
1. H-E1: Variance exists (PASSED)
2. H-M1: Seed independence creates different weights (PASSED)
3. H-M2: Different weights converge to different local minima (PASSED)
4. **H-M3: Variance estimates from different minima are statistically stable**

### Previous Hypothesis Results (if applicable)

**From h-e1 (PASSED):**
- 30 test accuracy samples per condition (4 conditions total)
- Fashion-MNIST variance: 0.3468% (1L), 0.5918% (2L)
- MNIST variance: 0.0387% (1L), 0.0594% (2L)
- Artifact location: `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-e1/results`

**From h-m2 (PASSED):**
- Different initial weights confirmed to lead to different final weights
- All 4 conditions passed mechanism validation
- Mean pairwise distances: 1layer=22.73, 2layer=27.31
- CV final loss: 1layer=2.12%, 2layer=3.04%

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Bootstrap Variance Estimation for Neural Networks**
- **Result:** No direct matches found in Archon KB for bootstrap variance estimation in neural network training contexts
- **Alternative results:** Diffusion models, consistency models (not relevant to hypothesis)
- **Insight:** Limited coverage of statistical validation methods for ML variance measurement in current KB

**Query 2: Bootstrap Resampling Confidence Intervals**
- **Result:** No relevant statistical validation resources found
- **Alternative results:** Consistency models, diffusion pipelines (not applicable)
- **Insight:** Archon KB focuses on generative models, lacks classical statistical methods coverage

**Query 3: Sample Size N=30 Variance Stability**
- **Result:** No matches for sample size validation or variance stability studies
- **Insight:** This is a classical statistics problem not well-covered in deep learning focused KB

**Overall Assessment:** Archon KB does not contain relevant prior art for bootstrap-based variance estimation in neural network training. This hypothesis requires classical statistical methods (scipy.stats, numpy) rather than deep learning frameworks.

### Archon Code Examples

**Query 1: Bootstrap Resampling Python Implementation**
- **No relevant code examples found** - Results returned unrelated numpy examples (incidence matrix generation, image processing)
- **Implication:** Implementation will rely on standard scipy.stats.bootstrap or manual numpy implementation

**Query 2: Variance Confidence Interval Statistical Methods**
- **No relevant code examples found** - Results returned diffusion model installation commands and variance scheduling (unrelated context)
- **Implication:** Will use scipy.stats for percentile-based CI computation

**Code Pattern Conclusion:** Standard Python statistical libraries (scipy, numpy) will be sufficient. No specialized deep learning code needed for this analysis-only hypothesis.

### Exa GitHub Implementations

**Query 1: Bootstrap Confidence Interval Variance Estimation**

**Resource 1**: Medium - Bootstrap Confidence Interval in Python
- **URL**: https://medium.com/@jumbongjunior/bootstrap-confidence-interval-in-python-8de3455158c3
- **Relevance**: Three bootstrap CI methods (Normal, Percentile, Pivot) with Python implementation
- **Key Methods**:
  - Percentile Method: CI = [percentile(2.5), percentile(97.5)] of bootstrap distribution
  - Normal Method: θ ± z(α/2) × SE_boot
  - Pivot Method: Uses bootstrap quantiles for CI construction
- **Code Pattern**:
  ```python
  # Bootstrap resampling B=1000 times
  theta_hats = []
  for b in range(B):
      resample = np.random.choice(data, size=n, replace=True)
      theta_hats.append(statistic(resample))

  # Percentile CI
  ci_lower = np.percentile(theta_hats, 2.5)
  ci_upper = np.percentile(theta_hats, 97.5)
  ```
- **Implementation**: Uses numpy.percentile() for CI calculation

**Resource 2**: UVA Library - Bootstrap Estimates of Confidence Intervals
- **URL**: http://library.virginia.edu/data/articles/bootstrap-estimates-of-confidence-intervals
- **Relevance**: Complete worked example with scipy.stats.bootstrap
- **Key Pattern**: scipy.stats.bootstrap() built-in function
- **Code Example**:
  ```python
  from scipy.stats import bootstrap
  import numpy as np

  # Resample 10,000 times
  betas = []
  for i in range(10000):
      indices = np.random.choice(len(data), size=len(data), replace=True)
      # Compute statistic on bootstrap sample
      betas.append(compute_statistic(data[indices]))

  # 95% CI using percentiles
  conf_interval = np.percentile(betas, [2.5, 97.5])
  ```

**Resource 3**: Machine Learning Mastery - Bootstrap Confidence Intervals
- **URL**: https://www.machinelearningmastery.com/calculate-bootstrap-confidence-intervals-machine-learning-results-python/
- **Relevance**: Bootstrap for ML algorithm evaluation (directly applicable)
- **Key Insight**: "A robust way to calculate confidence intervals for ML algorithms is to use the bootstrap"
- **Recommended Parameters**: B=1000 iterations minimum, percentile method for CI
- **Code Pattern**:
  ```python
  # Bootstrap for variance estimation
  stats = []
  for i in range(n_iterations):
      boot_sample = resample(data, n_samples=n_size)
      stat = calculate_variance(boot_sample)
      stats.append(stat)

  # 95% CI
  alpha = 0.95
  p = ((1.0-alpha)/2.0) * 100
  lower = numpy.percentile(stats, p)
  p = (alpha+((1.0-alpha)/2.0)) * 100
  upper = numpy.percentile(stats, p)
  ```

**Query 2: Bootstrap for Neural Network Variance**

**Resource 4**: MDPI - Estimating Neural Network's Performance with Bootstrap
- **URL**: https://www.mdpi.com/2504-4990/3/2/18
- **Relevance**: ⭐⭐⭐ HIGHEST - Tutorial on bootstrap for NN performance variance estimation
- **Key Insight**: "Determination of the distribution of a statistical estimator (MSE or accuracy) is fundamental to evaluate NN performance"
- **Method**: Bootstrap resampling to estimate variance of MSE/accuracy without training hundreds of models
- **Computational Note**: "Resampling techniques are computationally intensive but avoid training thousands of models"
- **Application**: Directly applicable to variance estimation from 30 test accuracy samples

**Resource 5**: arXiv - Confident Neural Network Regression with Bootstrapped Deep Ensembles
- **URL**: https://arxiv.org/pdf/2202.10903
- **Relevance**: Parametric bootstrap for uncertainty quantification in NNs
- **Key Formula**: Variance V(f̂*(x)) = σ²_classical(x) + σ²_optim(x)/M
- **Insight**: Bootstrap explicitly accounts for finite data effects on variance

**Resource 6**: Neuromatch Tutorial - Confidence Intervals and Bootstrapping
- **URL**: https://compneuro.neuromatch.io/tutorials/W1D2_ModelFitting/student/W1D2_Tutorial3.html
- **Code Pattern**:
  ```python
  def bootstrap_estimates(x, y, n=2000):
      theta_hats = []
      for _ in range(n):
          indices = np.random.choice(len(x), size=len(x), replace=True)
          theta_hats.append(fit_model(x[indices], y[indices]))
      return np.array(theta_hats)

  # Percentile CI
  ci_95 = [np.percentile(theta_hats, 2.5), np.percentile(theta_hats, 97.5)]
  ```

**Serena Analysis Needed**: False - Code patterns are clear and standard (scipy.stats, numpy)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Not applicable** - This is a classical statistical method (bootstrap resampling), not a novel paper method requiring author implementation.

**Recommended Implementation Path:**
- Primary: scipy.stats.bootstrap (standard library implementation)
- Fallback: Manual numpy implementation (based on Medium tutorial and ML Mastery patterns)
- Justification:
  - scipy.stats.bootstrap provides clean, vetted API for bootstrap CI estimation (since scipy 1.7.0)
  - If scipy unavailable, manual implementation is straightforward (25 lines, well-documented in 6 web sources)
  - No deep learning framework dependencies - pure statistical analysis
  - Both approaches implement percentile method for 95% CI as per literature standard

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Bootstrap variance estimation uses standard scipy.stats and numpy functions with well-documented APIs. No complex architecture or custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: Test Accuracy Artifacts from h-e1 (Analysis-only - No new data collection)
**Type**: reuse (artifact from previous hypothesis)

**Loading Information** (for Phase 4):
- Method: Load saved test accuracy results from h-e1 experiment
- Identifier: `h-e1/results/test_accuracies.npy` (or equivalent artifact file)
- Code:
  ```python
  import numpy as np
  import os

  # Load test accuracies from h-e1 artifacts
  h_e1_folder = "../h-e1/results"

  # Expected structure: 4 conditions × 30 samples each
  # Conditions: (1layer_mnist, 1layer_fashion_mnist, 2layer_mnist, 2layer_fashion_mnist)
  test_accuracies = {}
  for condition in ["1layer_mnist", "1layer_fashion_mnist", "2layer_mnist", "2layer_fashion_mnist"]:
      filepath = os.path.join(h_e1_folder, f"{condition}_test_accuracies.npy")
      test_accuracies[condition] = np.load(filepath)  # Shape: (30,)
  ```

**Statistics**:
- Total samples: 30 test accuracies per condition
- Conditions: 4 (2 architectures × 2 datasets)
- Data type: Float32 (test accuracy percentages)

**Preprocessing**: None required (data already cleaned and validated in h-e1)

**Augmentation**: N/A (analysis-only)

### Models

#### Baseline Model

**Architecture**: N/A (Analysis-only hypothesis - no model training)
**Type**: Statistical analysis (bootstrap resampling)

**Loading Information**: Not applicable - this hypothesis performs statistical analysis on existing test accuracy data, not model training.

**Bootstrap Implementation Details**:
- Library: scipy.stats (for bootstrap function) + numpy (for percentile CI computation)
- Function: `scipy.stats.bootstrap()` or manual implementation with `np.random.choice()`
- Parameters:
  - B=1000 bootstrap resamples (standard from literature)
  - Statistic: variance (np.var with ddof=1)
  - CI method: Percentile method [2.5, 97.5] for 95% CI
- Reference: MDPI tutorial on bootstrap for NN performance estimation

**Configuration**: No model configuration needed

#### Proposed Model

**Architecture:** Analysis-only (no model training required)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Bootstrap Variance Estimation with Confidence Intervals
# Based on: scipy.stats.bootstrap + numpy percentile method
# References: MDPI Tutorial (Michelucci 2021), Machine Learning Mastery, UVA Library

import numpy as np
from typing import Tuple

def bootstrap_variance_ci(data: np.ndarray, n_resamples: int = 1000,
                          confidence_level: float = 0.95) -> Tuple[float, float, float, float]:
    """
    Estimate variance and 95% CI using bootstrap resampling.

    Args:
        data: Test accuracy samples (shape: (30,))
        n_resamples: Number of bootstrap iterations (default: 1000)
        confidence_level: CI level (default: 0.95 for 95% CI)

    Returns:
        Tuple of (variance_estimate, ci_lower, ci_upper, ci_width_percent)
    """
    # Bootstrap resampling
    variance_estimates = []
    n = len(data)

    for _ in range(n_resamples):
        # Resample with replacement
        bootstrap_sample = np.random.choice(data, size=n, replace=True)

        # Compute variance on bootstrap sample
        variance_estimates.append(np.var(bootstrap_sample, ddof=1))

    variance_estimates = np.array(variance_estimates)

    # Point estimate: mean of bootstrap distribution
    variance_point = np.mean(variance_estimates)

    # Percentile CI method
    alpha = 1 - confidence_level
    ci_lower = np.percentile(variance_estimates, (alpha/2) * 100)
    ci_upper = np.percentile(variance_estimates, (confidence_level + alpha/2) * 100)

    # CI width as percentage of point estimate
    ci_width_percent = ((ci_upper - ci_lower) / variance_point) * 100

    return variance_point, ci_lower, ci_upper, ci_width_percent

# Usage for hypothesis validation:
# For each of 4 conditions, verify CI width ≤ 50%
```

### Training Protocol

**N/A - Analysis-Only Hypothesis**

This hypothesis performs statistical analysis on existing test accuracy data from h-e1. No model training is required.

**Analysis Parameters** (from research):
- **Bootstrap Resamples (B)**: 1000
  - **Source**: Standard from Machine Learning Mastery tutorial, MDPI bootstrap tutorial
  - **Justification**: Sufficient for stable CI estimation (most tutorials use 1000-10000)
- **Confidence Level**: 95% (α=0.05)
  - **Source**: Standard statistical practice, all referenced tutorials
  - **CI Method**: Percentile method (2.5th and 97.5th percentiles)
- **Variance Estimator**: Sample variance with Bessel's correction (ddof=1)
  - **Source**: Unbiased variance estimation standard
- **Random Seed**: Fixed seed for reproducibility
  - **Justification**: Ensures consistent bootstrap resampling across runs

### Evaluation

**Primary Metrics**:
1. **CI Width Percentage**: (CI_upper - CI_lower) / variance × 100%
   - Computed for each of 4 conditions independently
   - Success threshold: ≤ 50% for all 4 conditions

2. **Bootstrap Variance Estimate**: Mean of bootstrap distribution
   - Used as point estimate for variance in each condition

**Success Criteria** (from Phase 2B):
- **Primary**: CI width ≤ 50% for all 4 conditions (stable variance estimation)
- **Secondary**: Statistical triangulation agreement - if time permits, compare bootstrap percentile method with:
  - Normal approximation method
  - Pivot method (advanced)
  - Agreement within 10% validates bootstrap assumptions

**Expected Results** (from Rajput 2023):
- N=30 should provide stable variance estimates with power ≈ 0.85
- CI width around 30-40% typical for well-powered studies
- Failure (CI width > 50%) would suggest N=30 insufficient despite Rajput 2023 criterion

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (variance estimation)
- Library: numpy (for percentile, var, mean), scipy.stats (optional - for scipy.stats.bootstrap)
- Code:
  ```python
  # Manual implementation
  ci_width_pct = ((ci_upper - ci_lower) / variance_point) * 100

  # Or use scipy.stats.bootstrap (simpler)
  from scipy.stats import bootstrap
  result = bootstrap((data,), np.var, n_resamples=1000, method='percentile')
  ci_lower, ci_upper = result.confidence_interval
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Bootstrap CI Width Comparison**: CI width % for all 4 conditions vs 50% threshold

#### Additional Figures (LLM Autonomous)

Recommended visualizations for bootstrap variance estimation validation:

1. **Bootstrap Distribution Histograms** (4 subplots, one per condition)
   - X-axis: Bootstrap variance estimates
   - Y-axis: Frequency
   - Overlay: Point estimate (red line), CI bounds (blue dashed lines), 50% width threshold indicator
   - Purpose: Visualize bootstrap distribution shape and CI coverage

2. **CI Width Comparison Across Conditions** (bar chart)
   - X-axis: 4 conditions (1L-MNIST, 1L-FashionMNIST, 2L-MNIST, 2L-FashionMNIST)
   - Y-axis: CI width percentage
   - Threshold line at 50%
   - Purpose: Direct visualization of primary success criterion

3. **Variance vs CI Width Scatter** (optional, for insight)
   - X-axis: Variance point estimate
   - Y-axis: CI width percentage
   - Purpose: Explore if higher variance correlates with wider CIs (expected)

4. **Statistical Triangulation Comparison** (if secondary analysis performed)
   - Compare percentile vs normal vs pivot methods
   - Show agreement/disagreement across methods

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. CI width ≤ 50% for all 4 conditions (primary criterion)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment**: Archon KB does not contain relevant prior art for bootstrap variance estimation in neural network contexts. All queries returned unrelated content (diffusion models, consistency models).

**Queries Executed**:
1. "bootstrap variance estimation neural networks" - No relevant matches
2. "bootstrap resampling confidence intervals statistical validation" - No statistical methods content
3. "sample size N=30 variance stability machine learning" - No sample size validation resources

**Conclusion**: Archon KB is optimized for deep learning frameworks, lacks classical statistical methods coverage. Implementation will rely on standard scipy/numpy libraries.

### Archon Code Examples

**Assessment**: No relevant code examples found in Archon KB for bootstrap implementation patterns.

**Queries Executed**:
1. "bootstrap resampling Python numpy" - Returned unrelated matrix operations
2. "variance confidence interval scipy statistics" - Returned diffusion model variance scheduling (irrelevant)

**Conclusion**: Standard library documentation (scipy.stats, numpy) will be the code reference.

### B. GitHub Implementations (Exa)

**Resource 1**: Medium - Bootstrap Confidence Interval in Python by Jumbong junior
- **URL**: https://medium.com/@jumbongjunior/bootstrap-confidence-interval-in-python-8de3455158c3
- **Query Used**: "bootstrap confidence interval variance estimation Python scipy"
- **Relevance**: Complete tutorial on three bootstrap CI methods (Percentile, Normal, Pivot)
- **Key Code** (annotated):
  ```python
  # Percentile Method - Used in our implementation
  for _ in range(n_resamples):
      bootstrap_sample = np.random.choice(data, size=n, replace=True)
      variance_estimates.append(np.var(bootstrap_sample, ddof=1))

  # 95% CI using percentiles
  ci_lower = np.percentile(variance_estimates, 2.5)
  ci_upper = np.percentile(variance_estimates, 97.5)
  ```
- **Used For**: Core bootstrap algorithm structure, percentile CI method
- **Implementation Pattern**: Manual numpy-based bootstrap (used in our pseudo-code)

**Resource 2**: UVA Library - Bootstrap Estimates of Confidence Intervals
- **URL**: http://library.virginia.edu/data/articles/bootstrap-estimates-of-confidence-intervals
- **Query Used**: "bootstrap confidence interval variance estimation Python scipy"
- **Relevance**: Worked example with Hubble constant dataset using scipy.stats.bootstrap
- **Key Code**:
  ```python
  from scipy.stats import bootstrap
  result = bootstrap((data,), statistic_function, n_resamples=10000, method='percentile')
  conf_interval = result.confidence_interval
  ```
- **Used For**: Alternative implementation using scipy.stats (simpler API)
- **Configuration**: B=10000 resamples (we use B=1000 for efficiency)

**Resource 3**: Machine Learning Mastery - Bootstrap Confidence Intervals for ML
- **URL**: https://www.machinelearningmastery.com/calculate-bootstrap-confidence-intervals-machine-learning-results-python/
- **Query Used**: "bootstrap confidence interval variance estimation Python scipy"
- **Relevance**: Bootstrap for ML algorithm performance estimation (directly applicable)
- **Key Insight**: "A robust way to calculate confidence intervals for ML algorithms is to use the bootstrap"
- **Parameters**: B=1000 minimum, percentile method recommended
- **Used For**: Validation of bootstrap applicability to ML variance estimation

**Resource 4**: MDPI - Estimating Neural Network's Performance with Bootstrap (Michelucci 2021)
- **URL**: https://www.mdpi.com/2504-4990/3/2/18
- **Query Used**: "bootstrap resampling neural network variance PyTorch"
- **Relevance**: ⭐⭐⭐ HIGHEST - Tutorial specifically on bootstrap for NN performance variance
- **Key Insight**: "Determination of distribution of statistical estimators (MSE/accuracy) fundamental for NN evaluation"
- **Method**: Bootstrap estimates MSE/accuracy variance without training thousands of models
- **Used For**: Conceptual validation that bootstrap is standard for NN performance estimation

**Resource 5**: arXiv 2202.10903 - Bootstrapped Deep Ensembles
- **URL**: https://arxiv.org/pdf/2202.10903
- **Query Used**: "bootstrap resampling neural network variance PyTorch"
- **Relevance**: Parametric bootstrap for NN uncertainty quantification
- **Key Formula**: V(f̂*(x)) = σ²_classical(x) + σ²_optim(x)/M
- **Insight**: Bootstrap accounts for finite data effects on variance (theoretical justification)
- **Used For**: Understanding bootstrap validity for NN variance estimation

**Resource 6**: Neuromatch Tutorial - Confidence Intervals and Bootstrapping
- **URL**: https://compneuro.neuromatch.io/tutorials/W1D2_ModelFitting/student/W1D2_Tutorial3.html
- **Query Used**: "bootstrap resampling neural network variance PyTorch"
- **Relevance**: Educational tutorial with complete bootstrap workflow
- **Implementation Pattern**:
  ```python
  def bootstrap_estimates(x, y, n=2000):
      theta_hats = []
      for _ in range(n):
          indices = np.random.choice(len(x), size=len(x), replace=True)
          theta_hats.append(fit_model(x[indices], y[indices]))
      return np.array(theta_hats)
  ```
- **Used For**: Bootstrap resampling workflow structure

### C. Code Analysis (Serena)

**Status**: Skipped - Code patterns from Exa search were sufficiently clear.

**Rationale**: Bootstrap variance estimation uses standard scipy.stats and numpy APIs with well-documented interfaces. No complex custom architecture or layers requiring semantic analysis.

### D. Implementation Priority Assessment

**Primary Implementation**: scipy.stats.bootstrap (if available) OR manual numpy implementation

**Justification**:
- scipy.stats.bootstrap provides clean API with built-in percentile method
- Fallback to manual numpy implementation is straightforward (25 lines, based on Medium tutorial)
- No dependency on deep learning frameworks (PyTorch/TF) - pure statistical analysis

**References Summary**:
- 6 Exa web resources (tutorials, papers, documentation)
- 0 Archon KB resources (not covered in current KB)
- 0 Serena analyses (not needed for statistical methods)
- Total: 6 researched sources cited

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-21T04:49:00Z

### Workflow History for This Hypothesis
- h-m3 set to IN_PROGRESS (Phase 2C started)
- Prerequisites: h-m2 COMPLETED with PASS status

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
