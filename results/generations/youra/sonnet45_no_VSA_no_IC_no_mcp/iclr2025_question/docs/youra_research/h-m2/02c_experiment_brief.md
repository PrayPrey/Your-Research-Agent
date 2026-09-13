# Experiment Design: h-m2

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under hypotheses that reach Gate 2 (100 samples), if we apply Bayesian updates combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full), then posterior prediction error will be >40% lower than Gate 1 prior error, because Bayesian inference reduces uncertainty by incorporating new evidence.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 completed with PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** Mechanism
- **Prerequisites:** H-M1

### Gate Condition
SHOULD_WORK gate: If Bayesian updates do NOT reduce error >40%, framework still works with Gate 1 only (nice-to-have refinement, not core claim).

---

## Continuation Context

H-M2 builds on H-M1 (validated: correlation r=1.000 between O_10 and O_full). Tests whether adding Gate 2 measurements (O_100) improves predictions via Bayesian updates.

### Previous Hypothesis Results (if applicable)
**H-M1 (Prerequisite) Results:**
- Pearson correlation: r=1.000 (p<0.0001)
- Perfect linear fit: R²=1.000, k=1.000
- All thresholds exceeded: r>0.7, p<0.05, CV<30%
- Gate 1 prediction baseline established for error comparison

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable* — Proceeding with scipy.stats documentation and standard Bayesian inference patterns.

**Key Resources (from standard documentation):**
- scipy.stats.norm for Gaussian priors and likelihoods
- Standard Bayesian update formula: posterior ∝ prior × likelihood
- Mean prediction: weighted average of prior and likelihood means
- Variance reduction: 1/σ²_post = 1/σ²_prior + 1/σ²_likelihood

### Archon Code Examples

*Archon MCP unavailable* — Using scipy.stats standard patterns.

### Exa GitHub Implementations

*Exa MCP unavailable* — Proceeding with scipy.stats reference implementations from official documentation.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*Not applicable* — This is a statistical validation of the Pilot Gates framework using standard Bayesian inference, not paper reproduction.

**Recommended Implementation Path:**
- Primary: scipy.stats Gaussian inference (standard library)
- Fallback: Manual Bayesian calculation from first principles
- Justification: Standard statistical method, no external implementations needed

### Code Analysis (Serena MCP)

*Skipped* — scipy.stats API is well-documented and straightforward

---

## Experiment Specification

### Dataset

**Dataset Name:** Retrospective ML Projects Corpus (H-M1 subset with Gate 2 data)
**Type:** custom (derived from H-M1 validation results)
**Source:** H-M1 validation output (overhead measurements from H-E1 corpus)

**Structure:**
- Required fields per hypothesis: O_10, O_100, O_full (overhead measurements at 10, 100, full samples)
- Minimum sample size: 10 hypotheses with complete Gate 2 data (per H-M2 success criteria)
- Format: CSV or JSON with columns [hypothesis_id, type, O_10, O_100, O_full]

**Loading Information** (for Phase 4 download):
- Method: custom (load from H-M1 validation results)
- Identifier: h-m1/04_validation_data.csv (or equivalent output from H-M1)
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv("../h-m1/04_validation_data.csv")
  # Filter for hypotheses with Gate 2 data (non-null O_100)
  gate2_data = df[df['O_100'].notna()]
  ```

### Models

#### Baseline Model

**Model Name:** Gate 1 Prior Predictor (from H-M1)
**Type:** Linear extrapolation model
**Architecture:** O_pred = k × O_10, where k is the scaling factor from H-M1 (k=1.000)

**Function:**
- Input: O_10 (micro-pilot overhead)
- Output: O_full prediction
- No trainable parameters (k is fixed from H-M1 validation)

**Loading Information** (for Phase 4 download):
- Method: Manual implementation (no pretrained weights)
- Identifier: N/A (simple formula)
- Code:
  ```python
  # Gate 1 prior predictor (baseline from H-M1)
  k = 1.000  # From H-M1 validation
  
  def gate1_predictor(O_10):
      """
      Linear extrapolation from Gate 1 micro-pilot.
      Returns prior mean and variance.
      """
      prior_mean = k * O_10
      prior_variance = 0.01  # Assumed uncertainty (to be tuned)
      return prior_mean, prior_variance
  ```

#### Proposed Model

**Architecture:** Gate 2 Bayesian Posterior Predictor

**Core Mechanism Implementation:**

```python
# Core Mechanism: Bayesian Update for Gate 2 Posterior Prediction
# Based on: scipy.stats Gaussian inference

import numpy as np
from scipy.stats import norm

class BayesianGate2Predictor:
    """
    Bayesian predictor combining Gate 1 prior with Gate 2 likelihood.
    Tests whether adding O_100 reduces prediction error vs Gate 1 only.
    """
    def __init__(self, k=1.000):
        """
        Args:
            k: Scaling factor from H-M1 (default 1.000)
        """
        self.k = k
        self.prior_variance = 0.01  # Tunable uncertainty
    
    def gate1_prior(self, O_10):
        """Gate 1 prediction (baseline)"""
        prior_mean = self.k * O_10
        return prior_mean, self.prior_variance
    
    def gate2_posterior(self, O_10, O_100):
        """Gate 2 Bayesian update (proposed)"""
        # Gate 1 prior
        prior_mean, prior_var = self.gate1_prior(O_10)
        
        # Gate 2 likelihood (assume O_100 is noisy measurement of O_full)
        likelihood_mean = O_100 * (1.0 / self.k)  # Inverse scaling
        likelihood_var = 0.005  # Lower uncertainty at 100 samples
        
        # Bayesian update: posterior ∝ prior × likelihood
        posterior_var = 1.0 / (1.0/prior_var + 1.0/likelihood_var)
        posterior_mean = posterior_var * (prior_mean/prior_var + likelihood_mean/likelihood_var)
        
        return posterior_mean, posterior_var

# Integration: Replaces Gate 1 linear predictor for hypotheses with Gate 2 data
```

### Training Protocol

**No Training Required** — Statistical validation only

**Data Processing:**
1. Load H-M1 validation results (O_10, O_100, O_full for each hypothesis)
2. Filter for hypotheses with non-null O_100 (Gate 2 data available)
3. Verify minimum sample size: ≥10 hypotheses (per H-M2 success criteria)

**Experiment Steps:**
1. For each hypothesis with Gate 2 data:
   - Compute Gate 1 prediction error: |prior_mean - O_full| / O_full
   - Compute Gate 2 prediction error: |posterior_mean - O_full| / O_full
2. Compute error reduction per hypothesis: (Error_G1 - Error_G2) / Error_G1 × 100%
3. Aggregate: Mean error reduction across all hypotheses
4. Statistical test: Paired t-test (Gate 1 vs Gate 2 errors, p<0.05)

**Seeds**: N/A (deterministic statistical computation)

**Rationale**: This is a mechanism validation experiment testing Bayesian inference, not ML model training.

### Evaluation

**Primary Metrics:**
1. **Mean Error Reduction**: (Error_G1 - Error_G2) / Error_G1 × 100%
   - Measures improvement from Gate 1 to Gate 2
   - Expected: >40% (per H-M2 success criteria)

2. **Paired t-test p-value**: Statistical significance test
   - Null hypothesis: No difference between Gate 1 and Gate 2 errors
   - Threshold: p < 0.05

**Success Criteria (PoC):**
- PASS if: Mean error reduction >40% AND p<0.05
- PARTIAL if: 20% ≤ error reduction <40% (explore alternative strategies)
- FAIL if: Error reduction <20% (Bayesian updates add no value)

**Expected Performance:**
- Gate 1 error: Baseline from H-M1 validation
- Gate 2 error: Lower than Gate 1 (uncertainty reduction)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_validation
- Library: scipy.stats (paired t-test), numpy (error computation)
- Code:
  ```python
  from scipy.stats import ttest_rel
  import numpy as np
  
  # Compute errors
  errors_g1 = np.abs(prior_predictions - O_full) / O_full
  errors_g2 = np.abs(posterior_predictions - O_full) / O_full
  
  # Error reduction
  error_reduction = (errors_g1 - errors_g2) / errors_g1 * 100
  mean_reduction = np.mean(error_reduction)
  
  # Paired t-test
  t_stat, p_value = ttest_rel(errors_g1, errors_g2)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Error Reduction Distribution**: Histogram of per-hypothesis error reduction percentages
2. **Gate 1 vs Gate 2 Scatter**: O_pred vs O_full for both gates (show reduction in scatter)
3. **Paired Error Comparison**: Paired plot showing Error_G1 and Error_G2 for each hypothesis
4. **Statistical Test Visualization**: Box plot of errors (Gate 1 vs Gate 2) with p-value annotation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status**: Archon MCP unavailable during design phase

### Archon Code Examples

**Status**: Archon MCP unavailable during design phase

### B. GitHub Implementations (Exa)

**Status**: Exa MCP unavailable during design phase

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — scipy.stats API is well-documented and straightforward

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-M1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: Retrospective ML corpus from H-E1
  - Scaling factor k=1.000 (proven from H-M1)
  - Gate 1 baseline predictor (linear extrapolation)
- **Why Reused**: Enables controlled experiment (only Bayesian update mechanism changes)

### E. Primary References

**Source 1**: scipy.stats documentation
- **Type**: Standard library reference
- **Relevance**: Gaussian prior/likelihood inference
- **Key Functions**:
  - `scipy.stats.norm`: Normal distribution PDF/CDF
  - Bayesian update formula: 1/σ²_post = 1/σ²_prior + 1/σ²_likelihood
- **Used For**: Pseudo-code generation, posterior computation

**Source 2**: H-M1 Validation Results
- **Type**: Previous hypothesis validation
- **Relevance**: Provides scaling factor k and Gate 1 baseline
- **Key Results**:
  - k=1.000 (scaling from O_10 to O_full)
  - r=1.000 correlation (validated extrapolation)
- **Used For**: Prior mean computation, baseline comparison

**Source 3**: Phase 2B Verification Plan (02b_verification_plan.md)
- **Type**: Hypothesis specification
- **Relevance**: Success criteria, protocol definition
- **Key Details**:
  - Error reduction threshold: >40%
  - Statistical test: paired t-test (p<0.05)
  - Minimum sample size: ≥10 hypotheses with Gate 2 data
- **Used For**: Evaluation metrics, success criteria

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Previous (H-M1) | H-M1 validation output |
| Baseline model | Previous (H-M1) | Gate 1 linear predictor (k=1.000) |
| Mechanism design | scipy.stats | Gaussian Bayesian inference |
| Pseudo-code | scipy.stats | Standard Bayesian update formula |
| Training protocol | N/A | Statistical validation (no training) |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md Section 2.2 H-M2 |
| Success criteria | Phase 2B | Error reduction >40%, p<0.05 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T07:00:00Z

### Workflow History for This Hypothesis

- 2026-08-25T07:00:00Z: Experiment design started
- 2026-08-25T07:20:00Z: Experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
