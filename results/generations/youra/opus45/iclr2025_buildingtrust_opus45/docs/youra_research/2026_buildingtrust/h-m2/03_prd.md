# Product Requirements Document: H-M2
# Percentile-Normalized Monotonicity Attenuation

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This PRD defines requirements for validating that margin inflation (confirmed in H-M1) decouples the confidence-correctness relationship. We measure this via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2×2 prompt design controls.

**Key Deliverable:** Statistical analysis showing β_percentile attenuation with p < 0.05.

---

## Problem Statement

### Background
H-M1 confirmed that instruction-tuned LLMs exhibit margin inflation for incorrect predictions (Qwen 3.06x, Mistral 16.79x). However, inflated margins alone don't prove confidence-correctness decoupling. This hypothesis tests whether inflation manifests as reduced monotonicity between confidence and correctness.

### Hypothesis Statement
> Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2×2 prompt controls.

### Success Criteria
1. **Primary:** β_percentile_instruct < β_percentile_base (direction)
2. **Primary:** Statistical significance with p < 0.05
3. **Secondary:** Effect persists across 2×2 prompt conditions

---

## Functional Requirements

### FR-1: Data Loading Module

**Priority:** P0 (Critical)

Load cached inference results from H-E1 hypothesis folder.

| Requirement | Specification |
|-------------|---------------|
| FR-1.1 | Load JSON cache files from `../h-e1/cache/` directory |
| FR-1.2 | Parse logit margins array for each sample |
| FR-1.3 | Parse correctness labels (binary: 0/1) |
| FR-1.4 | Support all 4 model variants: Qwen-base, Qwen-instruct, Mistral-base, Mistral-instruct |
| FR-1.5 | Validate cache integrity (14,042 samples per model) |

**Data Schema:**
```python
{
    "sample_id": int,
    "margins": float,  # max_logit - second_max_logit
    "correct": bool,   # true if predicted == ground_truth
    "model": str,      # model identifier
}
```

### FR-2: Percentile Normalization Module

**Priority:** P0 (Critical)

Apply z-score normalization to convert raw margins to percentile-normalized values.

| Requirement | Specification |
|-------------|---------------|
| FR-2.1 | Apply scipy.stats.zscore() to margin array |
| FR-2.2 | Normalize within each model separately (not across models) |
| FR-2.3 | Handle edge cases: constant margins (std=0) |
| FR-2.4 | Output normalized margins with mean=0, std=1 |

**Formula:** z_i = (margin_i - μ) / σ

### FR-3: Logistic Regression Module

**Priority:** P0 (Critical)

Fit logistic regression to estimate β_percentile coefficient.

| Requirement | Specification |
|-------------|---------------|
| FR-3.1 | Use sklearn LogisticRegression with 'lbfgs' solver |
| FR-3.2 | Fit model: Pr(correct) = σ(α + β·z_margin) |
| FR-3.3 | Extract coefficient β (coef_[0][0]) |
| FR-3.4 | Set max_iter=1000 for convergence |
| FR-3.5 | Use regularization C=1e6 (effectively unregularized) |

**Output:** β_percentile coefficient per model

### FR-4: Bootstrap Confidence Interval Module

**Priority:** P0 (Critical)

Compute 95% confidence intervals via bootstrap resampling.

| Requirement | Specification |
|-------------|---------------|
| FR-4.1 | Perform 1000 bootstrap iterations per model |
| FR-4.2 | Resample with replacement using sklearn.utils.resample |
| FR-4.3 | Compute β_percentile for each bootstrap sample |
| FR-4.4 | Calculate 2.5th and 97.5th percentiles for 95% CI |
| FR-4.5 | Set random seed=42 for reproducibility |

**Output:** (β_mean, β_ci_lower, β_ci_upper) per model

### FR-5: Statistical Comparison Module

**Priority:** P0 (Critical)

Compare β_percentile between base and instruct models.

| Requirement | Specification |
|-------------|---------------|
| FR-5.1 | Compute Δβ = β_base - β_instruct |
| FR-5.2 | Bootstrap difference test: sample Δβ across iterations |
| FR-5.3 | Calculate p-value: proportion of samples where Δβ ≤ 0 |
| FR-5.4 | Report effect significance at α=0.05 level |
| FR-5.5 | Compute effect size: Δβ / pooled_std |

**Gate Criterion:** Δβ > 0 with p < 0.05

### FR-6: 2×2 Factorial Analysis Module

**Priority:** P1 (High)

Analyze effect across prompt format conditions.

| Requirement | Specification |
|-------------|---------------|
| FR-6.1 | Load prompt format labels from cache (zero-shot vs few-shot) |
| FR-6.2 | Compute β_percentile for each cell in 2×2 design |
| FR-6.3 | Test main effect of model type (base vs instruct) |
| FR-6.4 | Test interaction effect (model_type × prompt_format) |
| FR-6.5 | Report ANOVA or equivalent analysis |

**Note:** If H-E1 cache only contains zero-shot data, simplify to 1×2 design.

### FR-7: Visualization Module

**Priority:** P1 (High)

Generate publication-quality figures.

| Requirement | Specification |
|-------------|---------------|
| FR-7.1 | β_percentile bar chart with error bars (95% CI) |
| FR-7.2 | Bootstrap distribution histograms (base vs instruct) |
| FR-7.3 | Logistic regression curves: Pr(correct) vs z(margin) |
| FR-7.4 | Forest plot: effect sizes (Δβ) with CIs per family |
| FR-7.5 | Save all figures to `{hypothesis_folder}/figures/` |
| FR-7.6 | Use matplotlib with publication style (fontsize 12, dpi 300) |

### FR-8: Results Reporting Module

**Priority:** P0 (Critical)

Generate structured results for Phase 4 validation.

| Requirement | Specification |
|-------------|---------------|
| FR-8.1 | Output results as YAML file (experiment_results.yaml) |
| FR-8.2 | Include all β_percentile values with CIs |
| FR-8.3 | Include p-values and effect sizes |
| FR-8.4 | Include gate evaluation (PASS/FAIL) |
| FR-8.5 | Generate human-readable summary table |

---

## Non-Functional Requirements

### NFR-1: Performance

| Requirement | Specification |
|-------------|---------------|
| NFR-1.1 | Complete analysis in <5 minutes on CPU |
| NFR-1.2 | Memory usage <4GB (no GPU required) |
| NFR-1.3 | Bootstrap parallelizable (optional joblib) |

### NFR-2: Reproducibility

| Requirement | Specification |
|-------------|---------------|
| NFR-2.1 | Fixed random seed (42) for all stochastic operations |
| NFR-2.2 | Version-pinned dependencies (scipy, sklearn, numpy) |
| NFR-2.3 | Deterministic results across runs |

### NFR-3: Code Quality

| Requirement | Specification |
|-------------|---------------|
| NFR-3.1 | Type hints for all function signatures |
| NFR-3.2 | Docstrings with Args/Returns sections |
| NFR-3.3 | Unit tests for core functions |

---

## Data Requirements

### Input Data

| Source | Path | Description |
|--------|------|-------------|
| H-E1 Cache | `../h-e1/cache/` | Cached inference results |
| Models | N/A | No model loading (statistical analysis only) |

### Output Data

| Artifact | Path | Description |
|----------|------|-------------|
| Results | `experiment_results.yaml` | Structured analysis results |
| Figures | `figures/*.png` | Publication-quality visualizations |
| Report | `04_validation.md` | Validation report |

---

## Dependencies

### Prerequisites

| Hypothesis | Status | Dependency Type |
|------------|--------|-----------------|
| H-E1 | COMPLETED | Data (cached inference) |
| H-M1 | COMPLETED | Theoretical (margin inflation confirmed) |

### Python Dependencies

```
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
pyyaml>=6.0
```

---

## Success Metrics

### Primary Gate (MUST_WORK)

| Metric | Criterion | Measurement |
|--------|-----------|-------------|
| Direction | β_instruct < β_base | Both families |
| Significance | p < 0.05 | Bootstrap test |

### Secondary Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Effect Size | Report Δβ magnitude | Practical significance |
| 2×2 Robustness | Effect survives controls | Validity |
| CI Width | <0.1 for β estimates | Precision |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| H-E1 cache missing | Blocker | Verify cache before analysis |
| Zero std margins | Analysis error | Add constant check in FR-2.3 |
| Bootstrap variance high | Wide CIs | Increase iterations to 2000 |
| 2×2 data unavailable | Reduced scope | Fallback to 1×2 design |

---

## Appendix: Traceability

| PRD Item | Source |
|----------|--------|
| Hypothesis Statement | 02b_context.md |
| Methodology | 02c_experiment_brief.md |
| Bootstrap Pattern | Exa GitHub search results |
| Success Criteria | Phase 2B verification plan |
| Prerequisites | verification_state.yaml |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-m2/02c_experiment_brief.md*
