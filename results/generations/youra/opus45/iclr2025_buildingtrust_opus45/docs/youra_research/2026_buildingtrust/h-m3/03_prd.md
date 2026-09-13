# Product Requirements Document: H-M3
# Geometric vs Scalar Distortion via Brier Decomposition

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

This PRD defines requirements for validating that RLHF-induced confidence distortion is geometric (affects probability landscape shape) rather than scalar (temperature-like rescaling). We measure this via Murphy Brier Score Decomposition, specifically testing whether Refinement (discrimination) degrades in instruction-tuned models.

**Key Deliverable:** Statistical analysis showing Refinement_instruct < Refinement_base with bootstrap confidence intervals.

---

## Problem Statement

### Background
The hypothesis chain has established:
- **H-E1 (PASS):** AUROC discriminative degradation exists (Qwen: +0.0222, Mistral: +0.0385)
- **H-M1 (PASS):** E[margin|incorrect] inflation confirmed (Qwen 3.06x, Mistral 16.79x)
- **H-M2 (PASS):** β_percentile attenuation confirmed (Qwen Δβ=0.76, Mistral Δβ=0.63)

This hypothesis tests the nature of the distortion mechanism:
- **Geometric:** Affects the SHAPE of the probability landscape (Refinement degrades)
- **Scalar:** Temperature-like rescaling (only Reliability changes)

### Hypothesis Statement
> The distortion is geometric (affects probability landscape shape) rather than scalar (temperature-like rescaling), evidenced by Brier decomposition showing Refinement degradation in instruct models.

### Success Criteria
1. **Primary:** Refinement_instruct < Refinement_base (discrimination degrades)
2. **Primary:** Effect direction consistent across BOTH model families (Qwen, Mistral)
3. **Primary:** Bootstrap 95% CI for difference excludes zero
4. **Secondary:** Reliability may improve (temperature-like calibration effect coexists)

---

## Functional Requirements

### FR-1: Data Loading Module

**Priority:** P0 (Critical)

Load cached inference results from H-E1 hypothesis folder.

| Requirement | Specification |
|-------------|---------------|
| FR-1.1 | Load .npy cache files from `../h-e1/cache/` directory |
| FR-1.2 | Load raw logits array (N, 4) for each model |
| FR-1.3 | Load correctness labels (N,) |
| FR-1.4 | Support all 4 model variants: Qwen-base, Qwen-instruct, Mistral-base, Mistral-instruct |
| FR-1.5 | Validate cache integrity (14,042 samples per model) |

**Data Schema:**
```python
{
    "logits": np.ndarray,  # Shape: (14042, 4) - logits for 4 options
    "labels": np.ndarray,  # Shape: (14042,) - correct answer indices (0-3)
    "model": str,          # model identifier
}
```

### FR-2: Probability Computation Module

**Priority:** P0 (Critical)

Convert raw logits to probability distributions via softmax.

| Requirement | Specification |
|-------------|---------------|
| FR-2.1 | Apply scipy.special.softmax(logits, axis=1) |
| FR-2.2 | Verify probabilities sum to 1.0 per sample |
| FR-2.3 | Handle numerical stability (log-sum-exp trick) |
| FR-2.4 | Output probability matrix (N, 4) |

**Formula:** p_i = exp(z_i) / Σ exp(z_j)

### FR-3: Murphy Brier Decomposition Module

**Priority:** P0 (Critical)

Implement Murphy (1973) Brier Score decomposition into Reliability, Resolution, Uncertainty.

| Requirement | Specification |
|-------------|---------------|
| FR-3.1 | Compute one-hot encoding of labels: y_onehot = np.eye(C)[labels] |
| FR-3.2 | Compute Brier score: mean squared error between probs and one-hot |
| FR-3.3 | Compute Uncertainty: Σ ȳ(1 - ȳ) where ȳ is base rate per class |
| FR-3.4 | Bin by top-class probability using n_bins=15 |
| FR-3.5 | Compute Reliability: Σ(nk/n)(fk - ȳk)² across bins |
| FR-3.6 | Compute Resolution/Refinement: Σ(nk/n)(ȳk - ȳ)² across bins |
| FR-3.7 | Verify decomposition: BS ≈ REL - RES + UNC (within tolerance 1e-6) |

**Murphy Formula:**
```
BS = REL - RES + UNC

where:
  REL = Σ(nk/n)(fk - ȳk)²  # Reliability (calibration error) - LOWER is better
  RES = Σ(nk/n)(ȳk - ȳ)²   # Resolution/Refinement (discrimination) - HIGHER is better
  UNC = ȳ(1 - ȳ)           # Uncertainty (base rate entropy) - constant
```

**Output:** dict with keys: brier_score, reliability, resolution, uncertainty, refinement

### FR-4: Bootstrap Confidence Interval Module

**Priority:** P0 (Critical)

Compute 95% confidence intervals via bootstrap resampling.

| Requirement | Specification |
|-------------|---------------|
| FR-4.1 | Perform 1000 bootstrap iterations per model |
| FR-4.2 | Resample with replacement (sample indices) |
| FR-4.3 | Compute full Brier decomposition for each bootstrap sample |
| FR-4.4 | Calculate 2.5th and 97.5th percentiles for 95% CI |
| FR-4.5 | Set random seed=42 for reproducibility |
| FR-4.6 | Bootstrap the difference (base - instruct) for paired test |

**Output:** (metric_mean, metric_ci_lower, metric_ci_upper) per component per model

### FR-5: Statistical Comparison Module

**Priority:** P0 (Critical)

Compare Brier decomposition components between base and instruct models.

| Requirement | Specification |
|-------------|---------------|
| FR-5.1 | Compute ΔRefinement = Refinement_base - Refinement_instruct |
| FR-5.2 | Compute ΔReliability = Reliability_base - Reliability_instruct |
| FR-5.3 | Bootstrap difference test: sample Δ across iterations |
| FR-5.4 | Calculate p-value: proportion of samples where Δ ≤ 0 |
| FR-5.5 | Report effect significance at α=0.05 level |
| FR-5.6 | Compute effect size: Δ / pooled_std |

**Gate Criterion:** ΔRefinement > 0 (base has higher refinement) with 95% CI excluding zero

### FR-6: Visualization Module

**Priority:** P1 (High)

Generate publication-quality figures.

| Requirement | Specification |
|-------------|---------------|
| FR-6.1 | Brier decomposition bar chart: grouped bars (Base vs Instruct) showing REL, RES, UNC |
| FR-6.2 | Reliability diagram: calibration curve (predicted prob vs observed freq) |
| FR-6.3 | Refinement delta forest plot: effect sizes with 95% CIs per family |
| FR-6.4 | Decomposition verification scatter: BS_computed vs (REL - RES + UNC) |
| FR-6.5 | Save all figures to `{hypothesis_folder}/figures/` |
| FR-6.6 | Use matplotlib with publication style (fontsize 12, dpi 300) |

### FR-7: Results Reporting Module

**Priority:** P0 (Critical)

Generate structured results for Phase 4 validation.

| Requirement | Specification |
|-------------|---------------|
| FR-7.1 | Output results as YAML file (experiment_results.yaml) |
| FR-7.2 | Include all decomposition components with CIs |
| FR-7.3 | Include p-values and effect sizes for differences |
| FR-7.4 | Include gate evaluation (PASS/FAIL) |
| FR-7.5 | Generate human-readable summary table |
| FR-7.6 | Include decomposition verification (sanity check) |

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
| NFR-2.2 | Version-pinned dependencies (scipy, numpy) |
| NFR-2.3 | Deterministic results across runs |

### NFR-3: Code Quality

| Requirement | Specification |
|-------------|---------------|
| NFR-3.1 | Type hints for all function signatures |
| NFR-3.2 | Docstrings with Args/Returns sections |
| NFR-3.3 | Unit tests for decomposition verification |

---

## Data Requirements

### Input Data

| Source | Path | Description |
|--------|------|-------------|
| H-E1 Cache | `../h-e1/cache/qwen_base_logits.npy` | Qwen base logits (14042, 4) |
| H-E1 Cache | `../h-e1/cache/qwen_instruct_logits.npy` | Qwen instruct logits (14042, 4) |
| H-E1 Cache | `../h-e1/cache/mistral_base_logits.npy` | Mistral base logits (14042, 4) |
| H-E1 Cache | `../h-e1/cache/mistral_instruct_logits.npy` | Mistral instruct logits (14042, 4) |
| H-E1 Cache | `../h-e1/cache/labels.npy` | Correct answer indices (14042,) |

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
| H-E1 | COMPLETED | Data (cached inference logits) |
| H-M1 | COMPLETED | Theoretical (margin inflation confirmed) |
| H-M2 | COMPLETED | Theoretical (monotonicity attenuation confirmed) |

### Python Dependencies

```
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
pyyaml>=6.0
```

---

## Success Metrics

### Primary Gate (SHOULD_WORK)

| Metric | Criterion | Measurement |
|--------|-----------|-------------|
| Direction | Refinement_instruct < Refinement_base | Both families |
| CI | 95% CI for ΔRefinement excludes zero | Bootstrap test |

### Secondary Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Reliability Change | Report direction | Temperature-like effect coexistence |
| Decomposition Verification | BS ≈ REL - RES + UNC | Implementation correctness |
| CI Width | Reasonable precision | Analysis quality |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| H-E1 cache missing/corrupted | Blocker | Verify cache before analysis |
| Empty bins in decomposition | Numerical error | Skip empty bins in calculation |
| Decomposition verification fails | Implementation bug | Add tolerance check (1e-6) |
| Effect inconsistent across families | Hypothesis weakened | Report both families separately |

---

## Appendix: Traceability

| PRD Item | Source |
|----------|--------|
| Hypothesis Statement | verification_state.yaml (h-m3) |
| Methodology | 02c_experiment_brief.md |
| Murphy Formula | Murphy (1973), TensorFlow Probability |
| Success Criteria | Phase 2B verification plan |
| Prerequisites | verification_state.yaml |
| Reference Implementation | tfp.stats.brier_decomposition |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-m3/02c_experiment_brief.md*
