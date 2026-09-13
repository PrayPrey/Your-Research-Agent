# Product Requirements Document: h-c2

**Date:** 2026-08-09
**Hypothesis:** The metadata-variance effect persists within RandomForest-only analysis, ruling out algorithm mix confound
**Type:** CONDITION (Permutation Control)
**Gate:** SHOULD_WORK

---

## Executive Summary

Validate h-e1's metadata-variance correlation through permutation testing. Shuffle metadata_completeness scores 1000 times, recompute regression coefficients, confirm true effect exceeds 95th percentile of null distribution.

---

## Problem Statement

h-e1 found 42.1% IQR reduction correlation with metadata completeness. This could be spurious (algorithm mix confound). Need permutation test to confirm statistical significance.

---

## Functional Requirements

### FR-1: Data Loading
- **Input:** h-e1 processed data (`h-e1/data/processed_datasets.csv`)
- **Required columns:** metadata_completeness, iqr_variance, intrinsic_stability, popularity, algorithm_family, infrastructure
- **Sample size:** ~200 datasets

### FR-2: True Coefficient Computation
- Fit mixed-effects regression (same as h-e1)
- Extract β_metadata coefficient
- Store as reference for comparison

### FR-3: Permutation Test
- N=1000 permutations
- Shuffle metadata_completeness column
- Recompute regression coefficient per permutation
- Random seed=42 for reproducibility

### FR-4: Statistical Analysis
- Compute percentile rank of true coefficient
- Compute two-sided p-value
- Compute effect ratio (95th percentile permuted / true)

### FR-5: Visualization
- Histogram of permuted coefficients
- Vertical line marking true coefficient
- Annotate percentile rank

---

## Non-Functional Requirements

### NFR-1: Performance
- Runtime: <30 minutes for 1000 permutations
- Memory: <4GB

### NFR-2: Reproducibility
- Fixed random seed (42)
- Deterministic results across runs

---

## Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Percentile rank | >95th | True effect significantly exceeds null |
| P-value | <0.05 | Statistical significance |
| Effect ratio | <5% | Permuted effect negligible vs true |

---

## Dependencies

- h-e1 validation data (prerequisite satisfied)
- statsmodels (mixed-effects regression)
- numpy (permutation)
- matplotlib (visualization)

---

## Out of Scope

- New data collection (reuse h-e1)
- Model training (statistical analysis only)
- Hyperparameter tuning (fixed protocol)
