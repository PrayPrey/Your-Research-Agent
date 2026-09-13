# Product Requirements Document: h-m2

**Hypothesis:** A weighted ensemble of SA metrics achieves higher correlation with pass@1 than any single metric (r_ensemble > max(r_individual)).

**Date:** 2026-08-24
**Author:** Anonymous
**Type:** MECHANISM (INCREMENTAL from h-m1)

---

## Executive Summary

This experiment tests whether combining pylint_score and radon_cc via weighted linear ensemble yields stronger correlation with pass@1 than individual metrics. Building on h-m1 validated results (pylint r=0.873, radon r=-0.569), we optimize ensemble weights to maximize correlation while controlling for code length.

---

## Problem Statement

Individual SA metrics correlate with pass@1 but may capture orthogonal quality dimensions. An optimally weighted ensemble could leverage complementary signal to achieve higher predictive power than any single metric.

---

## Functional Requirements

### FR-1: Data Loading
- Load h-m1 cached SA metrics (pylint_score, radon_cc, loc, pass_at_1)
- Source: `../h-m1/data/sa_metrics_combined.csv`
- 591 samples (HumanEval 164 + MBPP 427)

### FR-2: Metric Normalization
- Min-max normalize pylint_score to [0,1]
- Min-max normalize radon_cc to [0,1]
- Preserve original values for validation

### FR-3: Ensemble Score Computation
- Compute weighted ensemble: `ensemble = w_pylint * norm_pylint + w_radon * norm_radon`
- Constraint: w_pylint + w_radon = 1.0

### FR-4: Weight Optimization (Grid Search)
- Search space: w_pylint ∈ [0.1, 0.9] step 0.1
- w_radon = 1.0 - w_pylint
- Select weights maximizing |r_ensemble|

### FR-5: Correlation Analysis
- Compute partial point-biserial correlation controlling LOC
- Use pingouin.partial_corr for LOC-controlled analysis
- Report r, p-value, 95% CI

### FR-6: Baseline Comparison
- Individual baselines from h-m1:
  - pylint_score: r=0.873
  - radon_cc: r=-0.569
- max(r_individual) = 0.873

### FR-7: Gate Evaluation
- Success: r_ensemble > 0.873 AND p < 0.05
- Failure: r_ensemble ≤ 0.873 OR p ≥ 0.05

### FR-8: Visualization
- Bar chart: r_ensemble vs max(r_individual)
- Weight sensitivity curve: r vs w_pylint
- Save to figures/

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed: 42
- Deterministic computation (no stochastic elements)

### NFR-2: Dependencies
- scipy >= 1.9.0
- pingouin >= 0.5.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- matplotlib >= 3.6.0

### NFR-3: Performance
- Complete in < 60 seconds
- Memory < 1GB

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary | r_ensemble > 0.873 | Partial correlation |
| Significance | p < 0.05 | Two-tailed test |
| Improvement | r_ensemble - max(r_individual) > 0 | Delta |

---

## Dependencies

- h-m1 validation data (COMPLETED)
- h-m1 SA metrics cache (EXISTS)

---

## Out of Scope

- Neural network models
- Additional SA metrics beyond pylint/radon
- Cross-dataset generalization testing
