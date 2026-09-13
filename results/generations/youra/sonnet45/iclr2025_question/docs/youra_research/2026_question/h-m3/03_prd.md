# Product Requirements Document (PRD): H-M3 Bootstrap CI Stability

**Date:** 2026-03-21
**Author:** Anonymous
**Hypothesis:** H-M3 - CLT-Predicted Slope
**Type:** MECHANISM (Analysis-Only)
**Gate:** MUST_WORK

---

## Executive Summary

This PRD specifies the implementation requirements for validating H-M3: variance estimation stability through bootstrap confidence intervals. The hypothesis tests whether N=30 test accuracy samples provide statistically stable variance estimates by computing bootstrap confidence intervals and verifying CI width ≤ 50% for all 4 experimental conditions.

**Key Characteristics:**
- **Analysis-Only**: No model training, uses artifacts from h-e1
- **Statistical Focus**: Bootstrap resampling with CI estimation
- **Prerequisites**: h-m1 (PASSED), h-m2 (PASSED)
- **Dependencies**: Test accuracy data from h-e1/results/

---

## Problem Statement

### Research Question
Does N=30 provide sufficient sample size for stable variance estimation in neural network training stochasticity, as measured by bootstrap confidence interval width?

### Success Criteria
**Primary (Gate Condition):**
- CI width ≤ 50% of variance point estimate for all 4 conditions:
  - 1layer_mnist
  - 1layer_fashion_mnist
  - 2layer_mnist
  - 2layer_fashion_mnist

**Secondary:**
- Statistical triangulation: bootstrap percentile vs normal approximation methods agree within 10%
- Visualization: Bootstrap distribution histograms with CI bounds

### Failure Modes
- CI width > 50% for any condition → N=30 insufficient, requires N sensitivity analysis
- Missing h-e1 artifact files → Cannot proceed with analysis
- Bootstrap implementation diverges from literature standards

---

## Functional Requirements

### FR-1: Data Loading from h-e1 Artifacts
**Priority:** CRITICAL
**Description:** Load pre-computed test accuracy data from h-e1 experiment results

**Acceptance Criteria:**
- Load 4 condition files from `../h-e1/results/`:
  - `1layer_mnist_test_accuracies.npy` (30 samples)
  - `1layer_fashion_mnist_test_accuracies.npy` (30 samples)
  - `2layer_mnist_test_accuracies.npy` (30 samples)
  - `2layer_fashion_mnist_test_accuracies.npy` (30 samples)
- Validate each file contains exactly 30 float32 values
- Error handling for missing files with clear message

### FR-2: Bootstrap Resampling Implementation
**Priority:** CRITICAL
**Description:** Implement bootstrap variance estimation with percentile CI method

**Acceptance Criteria:**
- B=1000 bootstrap resamples per condition
- Resample with replacement using `np.random.choice(data, size=n, replace=True)`
- Compute variance on each bootstrap sample using `np.var(bootstrap_sample, ddof=1)`
- Store all 1000 variance estimates per condition
- Fixed random seed for reproducibility

**Technical Specification:**
```python
def bootstrap_variance_ci(data: np.ndarray,
                          n_resamples: int = 1000,
                          confidence_level: float = 0.95) -> Tuple[float, float, float, float]:
    """
    Bootstrap variance estimation with percentile CI.

    Args:
        data: Test accuracy samples (30,)
        n_resamples: Bootstrap iterations (default: 1000)
        confidence_level: CI level (default: 0.95)

    Returns:
        (variance_point, ci_lower, ci_upper, ci_width_percent)
    """
    pass  # Implementation per Phase 2C pseudo-code
```

### FR-3: Confidence Interval Calculation
**Priority:** CRITICAL
**Description:** Compute 95% CI using percentile method

**Acceptance Criteria:**
- CI bounds: [percentile(2.5), percentile(97.5)] of bootstrap distribution
- Variance point estimate: mean of bootstrap distribution
- CI width percentage: `((ci_upper - ci_lower) / variance_point) * 100`
- Output format: Dict with keys `variance`, `ci_lower`, `ci_upper`, `ci_width_pct`

### FR-4: Multi-Condition Analysis
**Priority:** CRITICAL
**Description:** Run bootstrap analysis independently for all 4 conditions

**Acceptance Criteria:**
- Process 4 conditions sequentially or in parallel
- Store results in structured format (condition → metrics dict)
- Log progress for each condition
- Aggregate pass/fail status across all conditions

### FR-5: Gate Validation Logic
**Priority:** CRITICAL
**Description:** Evaluate MUST_WORK gate condition

**Acceptance Criteria:**
- Check: `ci_width_pct ≤ 50` for ALL 4 conditions
- Gate PASS if all 4 conditions satisfy threshold
- Gate FAIL if any condition exceeds 50% CI width
- Generate pass/fail report with condition-specific metrics

### FR-6: Results Logging and Output
**Priority:** HIGH
**Description:** Save analysis results and generate validation report

**Acceptance Criteria:**
- Save per-condition results to `results/bootstrap_results.json`:
  ```json
  {
    "1layer_mnist": {
      "variance": 0.00015,
      "ci_lower": 0.00010,
      "ci_upper": 0.00020,
      "ci_width_pct": 33.3,
      "n_samples": 30,
      "n_resamples": 1000
    },
    ...
  }
  ```
- Generate `04_validation.md` with gate result and per-condition summary
- Log to `experiment.log` with timestamps

### FR-7: Visualization Generation
**Priority:** HIGH
**Description:** Create diagnostic plots for bootstrap analysis

**Acceptance Criteria:**
- **Figure 1:** Bootstrap distribution histograms (4 subplots, one per condition)
  - X-axis: Bootstrap variance estimates
  - Y-axis: Frequency
  - Overlay: Point estimate (red line), CI bounds (blue dashed), 50% width threshold
- **Figure 2:** CI Width Comparison Bar Chart
  - X-axis: 4 conditions
  - Y-axis: CI width percentage
  - Threshold line at 50%
  - Color: green (pass) / red (fail)
- Save to `figures/bootstrap_analysis.png`

### FR-8: Statistical Triangulation (Secondary)
**Priority:** LOW
**Description:** Compare bootstrap percentile with normal approximation method

**Acceptance Criteria:**
- Implement normal approximation: `variance ± z(α/2) * SE_boot`
- Compute agreement: `|percentile_CI - normal_CI| / percentile_CI * 100 ≤ 10%`
- Report agreement status in validation report
- Optional: include in figures

---

## Non-Functional Requirements

### NFR-1: Performance
- Bootstrap analysis completes in < 30 seconds for all 4 conditions (CPU-only, no GPU needed)
- Memory footprint < 100MB (storing 4000 variance estimates)

### NFR-2: Reproducibility
- Fixed random seed (e.g., `np.random.seed(42)`) for bootstrap resampling
- Document seed value in results metadata
- All results deterministic across runs

### NFR-3: Dependency Management
- Python 3.8+
- Required libraries: numpy>=1.20, scipy>=1.7.0, matplotlib>=3.3.0
- Optional: pandas for result formatting

### NFR-4: Code Quality
- Type hints for all public functions
- Docstrings following numpy style
- Unit tests for bootstrap function (validate against known distributions)

### NFR-5: Error Handling
- Graceful failure if h-e1 artifacts missing
- Validate input data shape (30 samples per condition)
- Detect NaN/Inf values in loaded data

---

## Data Specifications

### Input Data

**Source:** h-e1 experiment artifacts
**Location:** `../h-e1/results/`
**Files:**
- `1layer_mnist_test_accuracies.npy`
- `1layer_fashion_mnist_test_accuracies.npy`
- `2layer_mnist_test_accuracies.npy`
- `2layer_fashion_mnist_test_accuracies.npy`

**Format:**
- Type: numpy array (.npy)
- Shape: (30,) per file
- Dtype: float32
- Range: [0, 100] (test accuracy percentages)

**Validation:**
- Check file existence before loading
- Verify shape == (30,)
- Check no NaN/Inf values
- Validate range [0, 100]

### Output Data

**Results File:** `results/bootstrap_results.json`
**Validation Report:** `04_validation.md`
**Figures:** `figures/bootstrap_analysis.png`

---

## Dependencies

### Prerequisite Hypotheses
- **h-m1** (PASSED): Validates seed independence mechanism
- **h-m2** (PASSED): Validates trajectory divergence to different minima

### External Dependencies
- h-e1 test accuracy artifacts (30 samples × 4 conditions)
- No external datasets or pretrained models needed

### Library Dependencies
```python
numpy>=1.20  # Bootstrap resampling, percentile CI
scipy>=1.7.0  # Optional: scipy.stats.bootstrap
matplotlib>=3.3.0  # Visualization
```

---

## Success Metrics

### Primary Metrics (Gate Condition)
| Metric | Target | Measurement |
|--------|--------|-------------|
| CI Width (1layer_mnist) | ≤ 50% | Bootstrap percentile method |
| CI Width (1layer_fashion_mnist) | ≤ 50% | Bootstrap percentile method |
| CI Width (2layer_mnist) | ≤ 50% | Bootstrap percentile method |
| CI Width (2layer_fashion_mnist) | ≤ 50% | Bootstrap percentile method |

**Gate:** MUST_WORK - ALL 4 conditions must pass

### Secondary Metrics
- Statistical triangulation agreement ≤ 10%
- Bootstrap distribution normality (optional QQ-plot)

---

## Implementation Constraints

### Analysis-Only Nature
- **No model training**: This hypothesis performs statistical analysis only
- **No GPU required**: CPU-only numpy/scipy operations
- **No dataset downloads**: Uses pre-existing artifacts from h-e1

### Computational Budget
- Runtime: < 30 seconds (4 conditions × 1000 bootstrap resamples)
- Memory: < 100MB
- Storage: < 10MB (results + figures)

### Scope Boundaries
- **In Scope:** Bootstrap variance estimation, CI width validation, visualization
- **Out of Scope:** Alternative CI methods (BCa, ABC), Bayesian variance estimation, N sensitivity analysis (unless gate fails)

---

## References

### Literature
1. **Rajput 2023** - Sample size criterion N≥30 for stable estimation (power ≈ 0.85)
2. **MDPI Tutorial (Michelucci 2021)** - Bootstrap for neural network performance estimation
3. **Machine Learning Mastery** - Bootstrap CI implementation best practices

### Implementation Patterns
- Percentile method: Most robust for non-normal distributions
- B=1000: Standard from literature (balance between accuracy and computation)
- ddof=1: Unbiased variance estimator (Bessel's correction)

---

## Appendix: Phase 2C Traceability

| Phase 2C Section | PRD Section | Mapping |
|------------------|-------------|---------|
| Dataset (Artifacts from h-e1) | FR-1 | Data loading specification |
| Core Mechanism (Bootstrap pseudo-code) | FR-2, FR-3 | Bootstrap implementation |
| Evaluation (CI width threshold) | FR-5 | Gate validation logic |
| Visualization Requirements | FR-7 | Figure specifications |
| Success Criteria | Success Metrics | Primary/secondary metrics |

---

*Generated for Phase 3 Implementation Planning*
*Next: 03_architecture.md (Epic task decomposition)*
