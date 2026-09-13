# Product Requirements Document (PRD): h-m2

**Document Version:** 1.0
**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis:** H-M2 - Bayesian Gate 2 Posterior Prediction
**Status:** Draft

---

## Executive Summary

### Purpose
Implement and validate a Bayesian inference mechanism that combines Gate 1 prior predictions with Gate 2 likelihood measurements to improve overhead prediction accuracy for machine learning hypotheses that reach the 100-sample validation stage.

### Scope
- Implement Bayesian posterior predictor using scipy.stats Gaussian inference
- Reuse Gate 1 baseline predictor from H-M1 (k=1.000)
- Validate against H-M1 corpus subset with Gate 2 data
- Measure error reduction: Gate 2 vs Gate 1 predictions

### Success Criteria
1. Mean prediction error reduction >40% (Gate 1 → Gate 2)
2. Statistical significance: paired t-test p<0.05
3. Minimum 10 hypotheses with complete Gate 2 data

### Dependencies
- H-M1 validation results (prerequisite, status: COMPLETED)
- H-M1 corpus with O_10, O_100, O_full measurements
- scipy.stats for Bayesian inference

---

## Problem Statement

### Context
H-M1 validated perfect correlation (r=1.000) between micro-pilot overhead (O_10) and full-scale overhead (O_full), establishing Gate 1 linear extrapolation. However, for hypotheses that reach Gate 2 (100 samples), we have additional measurement O_100 that could refine predictions via Bayesian updates.

### Problem
Gate 1 predictions use only O_10. When Gate 2 data (O_100) becomes available, we need a mechanism to incorporate this new evidence to reduce prediction uncertainty.

### Impact
If Bayesian updates reduce error >40%, framework gains incremental refinement capability. If not, framework remains effective with Gate 1 only (SHOULD_WORK gate — nice-to-have feature).

---

## Functional Requirements

### FR-1: Data Loading
**Priority:** P0 (Critical)

Load retrospective ML corpus from H-M1 validation results.

**Acceptance Criteria:**
- Read H-M1 validation output file (CSV/JSON format)
- Filter for hypotheses with non-null O_100 (Gate 2 data available)
- Verify minimum sample size: ≥10 hypotheses
- Extract fields: hypothesis_id, type, O_10, O_100, O_full

**Data Format:**
```python
{
    "hypothesis_id": "str",
    "type": "str",  # EXISTENCE/MECHANISM/COMPARISON
    "O_10": "float",  # Micro-pilot overhead (10 samples)
    "O_100": "float",  # Gate 2 overhead (100 samples)
    "O_full": "float"  # Full-scale overhead (ground truth)
}
```

**Source:** `../h-m1/04_validation_data.csv` or equivalent H-M1 output

---

### FR-2: Gate 1 Baseline Predictor
**Priority:** P0 (Critical)

Implement Gate 1 prior prediction using H-M1 validated scaling factor.

**Acceptance Criteria:**
- Use k=1.000 from H-M1 validation results
- Compute prior mean: O_pred = k × O_10
- Assign prior variance: σ²_prior = 0.01 (tunable uncertainty parameter)
- Return (prior_mean, prior_variance) for each hypothesis

**Implementation:**
```python
def gate1_predictor(O_10: float, k: float = 1.000) -> tuple[float, float]:
    """
    Gate 1 linear extrapolation (baseline from H-M1).
    
    Args:
        O_10: Micro-pilot overhead (10 samples)
        k: Scaling factor from H-M1 (default 1.000)
    
    Returns:
        (prior_mean, prior_variance)
    """
    prior_mean = k * O_10
    prior_variance = 0.01
    return prior_mean, prior_variance
```

**Reuse:** Mechanism validated in H-M1 (perfect correlation, R²=1.000)

---

### FR-3: Gate 2 Bayesian Posterior Predictor
**Priority:** P0 (Critical)

Implement Bayesian update combining Gate 1 prior with Gate 2 likelihood.

**Acceptance Criteria:**
- Compute Gate 1 prior: (μ_prior, σ²_prior) from FR-2
- Compute Gate 2 likelihood: μ_likelihood = O_100 / k, σ²_likelihood = 0.005
- Apply Bayesian update formula:
  - Posterior variance: 1/σ²_post = 1/σ²_prior + 1/σ²_likelihood
  - Posterior mean: μ_post = σ²_post × (μ_prior/σ²_prior + μ_likelihood/σ²_likelihood)
- Return (posterior_mean, posterior_variance) for each hypothesis

**Implementation:**
```python
def gate2_posterior(O_10: float, O_100: float, k: float = 1.000) -> tuple[float, float]:
    """
    Gate 2 Bayesian update (proposed mechanism).
    
    Args:
        O_10: Micro-pilot overhead (10 samples)
        O_100: Gate 2 overhead (100 samples)
        k: Scaling factor from H-M1 (default 1.000)
    
    Returns:
        (posterior_mean, posterior_variance)
    """
    # Gate 1 prior
    prior_mean, prior_var = gate1_predictor(O_10, k)
    
    # Gate 2 likelihood (assume O_100 measures O_full with noise)
    likelihood_mean = O_100 / k  # Inverse scaling
    likelihood_var = 0.005  # Lower uncertainty at 100 samples
    
    # Bayesian update
    posterior_var = 1.0 / (1.0 / prior_var + 1.0 / likelihood_var)
    posterior_mean = posterior_var * (prior_mean / prior_var + likelihood_mean / likelihood_var)
    
    return posterior_mean, posterior_var
```

**Library:** scipy.stats.norm (for PDF/CDF if needed for diagnostics)

---

### FR-4: Error Computation
**Priority:** P0 (Critical)

Compute prediction errors for Gate 1 and Gate 2 predictions.

**Acceptance Criteria:**
- Gate 1 error: |prior_mean - O_full| / O_full (relative error)
- Gate 2 error: |posterior_mean - O_full| / O_full (relative error)
- Compute per-hypothesis error reduction: (Error_G1 - Error_G2) / Error_G1 × 100%
- Return arrays: errors_g1, errors_g2, error_reduction_pct

**Implementation:**
```python
def compute_errors(prior_predictions: np.ndarray, 
                   posterior_predictions: np.ndarray, 
                   O_full: np.ndarray) -> dict:
    """
    Compute prediction errors for Gate 1 and Gate 2.
    
    Args:
        prior_predictions: Gate 1 predictions (n,)
        posterior_predictions: Gate 2 predictions (n,)
        O_full: Ground truth full-scale overhead (n,)
    
    Returns:
        {
            "errors_g1": Gate 1 relative errors (n,),
            "errors_g2": Gate 2 relative errors (n,),
            "error_reduction_pct": Per-hypothesis reduction % (n,),
            "mean_reduction": Mean error reduction across all hypotheses
        }
    """
    errors_g1 = np.abs(prior_predictions - O_full) / O_full
    errors_g2 = np.abs(posterior_predictions - O_full) / O_full
    error_reduction_pct = (errors_g1 - errors_g2) / errors_g1 * 100
    
    return {
        "errors_g1": errors_g1,
        "errors_g2": errors_g2,
        "error_reduction_pct": error_reduction_pct,
        "mean_reduction": np.mean(error_reduction_pct)
    }
```

---

### FR-5: Statistical Validation
**Priority:** P0 (Critical)

Perform paired t-test to assess statistical significance of error reduction.

**Acceptance Criteria:**
- Use scipy.stats.ttest_rel for paired comparison
- Null hypothesis: No difference between Gate 1 and Gate 2 errors
- Threshold: p<0.05 for significance
- Report: t-statistic, p-value, degrees of freedom

**Implementation:**
```python
from scipy.stats import ttest_rel

def statistical_test(errors_g1: np.ndarray, errors_g2: np.ndarray) -> dict:
    """
    Paired t-test comparing Gate 1 vs Gate 2 errors.
    
    Args:
        errors_g1: Gate 1 relative errors (n,)
        errors_g2: Gate 2 relative errors (n,)
    
    Returns:
        {
            "t_statistic": float,
            "p_value": float,
            "dof": int,
            "significant": bool (p < 0.05)
        }
    """
    t_stat, p_value = ttest_rel(errors_g1, errors_g2)
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "dof": len(errors_g1) - 1,
        "significant": p_value < 0.05
    }
```

---

### FR-6: Success Criteria Evaluation
**Priority:** P0 (Critical)

Evaluate experiment results against H-M2 success criteria.

**Acceptance Criteria:**
- Check mean error reduction >40%
- Check statistical significance p<0.05
- Classify result: PASS / PARTIAL / FAIL

**Decision Rules:**
| Mean Error Reduction | p-value | Result | Interpretation |
|---------------------|---------|--------|----------------|
| >40% | <0.05 | PASS | Bayesian updates validated |
| 20-40% | <0.05 | PARTIAL | Modest improvement, explore alternatives |
| <20% | Any | FAIL | Gate 2 adds no value |
| Any | ≥0.05 | FAIL | Not statistically significant |

**Implementation:**
```python
def evaluate_success(mean_reduction: float, p_value: float) -> dict:
    """
    Evaluate against H-M2 success criteria.
    
    Args:
        mean_reduction: Mean error reduction % across hypotheses
        p_value: Paired t-test p-value
    
    Returns:
        {
            "result": "PASS" | "PARTIAL" | "FAIL",
            "mean_reduction": float,
            "p_value": float,
            "criteria_met": {
                "error_reduction_40pct": bool,
                "statistical_significance": bool
            }
        }
    """
    error_reduction_ok = mean_reduction > 40.0
    significance_ok = p_value < 0.05
    
    if error_reduction_ok and significance_ok:
        result = "PASS"
    elif 20.0 <= mean_reduction < 40.0 and significance_ok:
        result = "PARTIAL"
    else:
        result = "FAIL"
    
    return {
        "result": result,
        "mean_reduction": mean_reduction,
        "p_value": p_value,
        "criteria_met": {
            "error_reduction_40pct": error_reduction_ok,
            "statistical_significance": significance_ok
        }
    }
```

---

### FR-7: Visualization Generation
**Priority:** P1 (High)

Generate visualizations for error reduction analysis.

**Acceptance Criteria:**
- Figure 1: Error reduction distribution histogram
- Figure 2: Gate 1 vs Gate 2 scatter plot (O_pred vs O_full)
- Figure 3: Paired error comparison (errors connected by lines)
- Figure 4: Box plot (Gate 1 vs Gate 2 errors with p-value annotation)
- Save all figures to `h-m2/figures/` folder

**Required Visualizations (from Phase 2C):**
1. Gate Metrics Comparison (mandatory): Target vs actual metrics bar chart
2. Error Reduction Distribution (recommended)
3. Gate 1 vs Gate 2 Scatter (recommended)
4. Paired Error Comparison (recommended)

**Figure Paths:**
- `h-m2/figures/error_reduction_histogram.png`
- `h-m2/figures/gate_comparison_scatter.png`
- `h-m2/figures/paired_errors.png`
- `h-m2/figures/statistical_comparison_boxplot.png`
- `h-m2/figures/metrics_comparison.png` (mandatory)

---

### FR-8: Validation Report Generation
**Priority:** P0 (Critical)

Generate `04_validation.md` report summarizing results.

**Acceptance Criteria:**
- Report sections: Hypothesis, Results, Statistical Analysis, Figures, Conclusion
- Include key findings: mean error reduction, p-value, sample size
- Include result classification: PASS/PARTIAL/FAIL
- Save to `h-m2/04_validation.md`

**Report Template:**
```markdown
# Validation Report: h-m2

## Hypothesis
[Statement from verification_state.yaml]

## Results
- Sample size: {n} hypotheses with Gate 2 data
- Mean error reduction: {mean_reduction:.2f}%
- Statistical significance: p={p_value:.4f}

## Statistical Analysis
- Paired t-test: t={t_statistic:.3f}, p={p_value:.4f}, dof={dof}
- Gate 1 mean error: {mean_error_g1:.4f}
- Gate 2 mean error: {mean_error_g2:.4f}

## Success Criteria
- Error reduction >40%: {✓/✗}
- Statistical significance p<0.05: {✓/✗}
- **Result:** {PASS/PARTIAL/FAIL}

## Figures
[List of generated figures with paths]

## Conclusion
[Interpretation of results and implications for Pilot Gates framework]
```

---

## Non-Functional Requirements

### NFR-1: Code Quality
- Type hints for all function signatures
- Docstrings for all public functions
- PEP 8 compliance

### NFR-2: Performance
- Execution time: <5 seconds for full validation (10-20 hypotheses)
- Memory: <100MB peak usage

### NFR-3: Reproducibility
- Deterministic computation (no random seeds needed)
- All intermediate results logged

### NFR-4: Error Handling
- Graceful failure if <10 hypotheses with Gate 2 data
- Warning if any O_10, O_100, O_full values are missing or negative

---

## Data Requirements

### Input Data
**Source:** H-M1 validation results
**Format:** CSV or JSON
**Required Fields:**
- hypothesis_id: str
- type: str
- O_10: float (micro-pilot overhead)
- O_100: float (Gate 2 overhead)
- O_full: float (full-scale overhead)

**Sample Size:** Minimum 10 hypotheses with complete Gate 2 data

### Output Data
**Validation Report:** `h-m2/04_validation.md`
**Figures Folder:** `h-m2/figures/`
**Results JSON:** `h-m2/04_results.json` (optional, for pipeline integration)

---

## Evaluation Metrics

### Primary Metrics
1. **Mean Error Reduction (%):** (Error_G1 - Error_G2) / Error_G1 × 100
   - Target: >40%
   - Measures improvement from Bayesian updates

2. **Paired t-test p-value:** Statistical significance test
   - Target: <0.05
   - Measures confidence in error reduction

### Secondary Metrics
3. **Error Variance Reduction:** Measure whether posterior predictions are more consistent
4. **Coverage Analysis:** Percentage of hypotheses where Gate 2 reduces error

---

## Success Criteria

### Validation Outcomes

| Outcome | Conditions | Interpretation |
|---------|-----------|----------------|
| **PASS** | Mean reduction >40% AND p<0.05 | Bayesian updates validated, framework enhanced |
| **PARTIAL** | 20% ≤ reduction <40% AND p<0.05 | Modest improvement, explore alternatives |
| **FAIL** | Reduction <20% OR p≥0.05 | Gate 2 adds no value, use Gate 1 only |

### Gate Condition
**Gate Type:** SHOULD_WORK
**Consequence if FAIL:** Framework remains effective with Gate 1 only (nice-to-have refinement)

---

## Dependencies

### Prerequisite Hypotheses
- **H-M1:** Micro-Pilot Overhead Correlates with Full-Scale Overhead
  - Status: COMPLETED (validation.result = PASS)
  - Provides: Scaling factor k=1.000, retrospective corpus, baseline predictor
  - Required outputs: 04_validation_data.csv, k value

### External Libraries
- numpy: Array operations, error computation
- scipy.stats: Gaussian inference (norm), paired t-test (ttest_rel)
- matplotlib: Visualization generation
- pandas: Data loading and manipulation

### Internal Components
- Gate 1 predictor (from H-M1, reused here)
- Verification state system (for result reporting)

---

## Implementation Constraints

### Budget Allocation
- **Hypothesis Type:** MECHANISM
- **Tier:** FULL
- **Total Task Budget:** 30 tasks maximum
- **Epic Range:** 6-12 Epic-level tasks

### Complexity Considerations
- Low complexity (statistical validation, no ML training)
- Reuses H-M1 infrastructure (data, baseline)
- Standard library only (scipy.stats)

### Timeline
- Estimated implementation: 2-4 hours
- Validation runtime: <5 minutes

---

## Risks and Mitigations

### Risk 1: Insufficient Gate 2 Data
**Impact:** Cannot validate if <10 hypotheses have O_100
**Mitigation:** Filter H-M1 corpus early, fail fast if sample size too small

### Risk 2: Prior/Likelihood Variance Tuning
**Impact:** Results sensitive to σ²_prior and σ²_likelihood values
**Mitigation:** Use reasonable defaults (0.01, 0.005), document assumptions

### Risk 3: SHOULD_WORK Gate Failure
**Impact:** If FAIL, framework loses incremental refinement capability
**Mitigation:** Framework remains functional with Gate 1 only (low consequence)

---

## Appendix

### A. Traceability to Phase 2C

| PRD Section | Phase 2C Source | Location |
|-------------|-----------------|----------|
| FR-1 Data Loading | Dataset specification | 02c_experiment_brief.md § Dataset |
| FR-2 Baseline | Baseline model | 02c_experiment_brief.md § Baseline Model |
| FR-3 Proposed | Proposed model | 02c_experiment_brief.md § Proposed Model |
| FR-4/FR-5 Evaluation | Evaluation metrics | 02c_experiment_brief.md § Evaluation |
| FR-7 Visualization | Visualization requirements | 02c_experiment_brief.md § Visualization |

### B. Phase 2C Completeness Check

✅ **All Phase 2C items included:**
- Dataset: Retrospective ML corpus (H-M1 subset) → FR-1
- Baseline model: Gate 1 Prior Predictor → FR-2
- Proposed model: Gate 2 Bayesian Posterior → FR-3
- Primary metrics: Error reduction, p-value → FR-4, FR-5
- Visualizations: 4 recommended + 1 mandatory → FR-7
- Success criteria: >40% reduction, p<0.05 → FR-6

### C. Hypothesis Context

**Hypothesis Statement:**
Under hypotheses that reach Gate 2 (100 samples), if we apply Bayesian updates combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full), then posterior prediction error will be >40% lower than Gate 1 prior error, because Bayesian inference reduces uncertainty by incorporating new evidence.

**Hypothesis Type:** MECHANISM (validates incremental refinement claim)

**Gate Type:** SHOULD_WORK (framework works with Gate 1 only if this fails)

---

**Document Status:** Ready for Architecture Design (Step 3)
**Next Phase:** Phase 3 Step 3 - Architecture Agent
