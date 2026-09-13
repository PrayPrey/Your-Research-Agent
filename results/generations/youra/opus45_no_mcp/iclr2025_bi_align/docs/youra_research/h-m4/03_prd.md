# Product Requirements Document: H-M4

**Hypothesis:** Bidirectional Tasks Show Miscalibrated Confidence
**Date:** 2026-08-19
**Author:** Anonymous
**Type:** MECHANISM
**Tier:** FULL

---

## Executive Summary

H-M4 tests the final causal step: whether tasks requiring bidirectional adaptation correlate with calibration inversion clusters. This analysis experiment extends H-E1 cluster results by scoring tasks on 3 bidirectional features and computing correlation with inversion cluster membership.

---

## Problem Statement

Prior phases established:
- H-E1: Calibration inversion clusters exist (silhouette=0.6016)
- H-M1: RLHF optimizes for annotator approval (overlap=0.647)
- H-M2: Annotators conflate correctness with user-state modeling (rate_diff=0.001)
- H-M3: Single reward signal misses bidirectional nuance (separation=0.024)

H-M4 must show that bidirectional features (user belief reference, context dependence, hedged answers) correlate with calibration inversion to complete the causal chain.

---

## Functional Requirements

### FR-1: Data Loading
- Load H-E1 cluster assignments from `h-e1/code/outputs/results.json`
- Load task metadata including task texts and cluster labels
- Total samples: 2212 tasks

### FR-2: Bidirectional Feature Scoring
- Implement 3-feature scoring system:
  - **user_belief_reference**: Detects "you think", "you believe", etc.
  - **context_dependent**: Detects "in this context", "given that", etc.
  - **hedged_answer**: Detects "might be", "could be", "possibly", etc.
- Score each task 0-3 (sum of binary features)

### FR-3: Confound Variable Extraction
- **Length**: Character count of task text
- **Topic**: Dataset source (TruthfulQA/ETHICS/HHH) - one-hot encoded
- **Format**: Question format - one-hot encoded
- **Difficulty**: Cross-model accuracy from H-E1

### FR-4: Correlation Analysis
- Compute point-biserial correlation (binary cluster vs continuous score)
- Compute Cohen's d effect size between clusters
- Compute partial correlation controlling for confounds

### FR-5: Cross-Model Validation
- Repeat analysis for Llama-2-7B, Llama-2-13B, Mistral-7B results
- Report consistency across models

### FR-6: Visualization
- Required: Gate metrics bar chart (r, d, partial_r vs thresholds)
- Optional: Violin plot of scores by cluster
- Optional: Feature breakdown stacked bar chart
- Optional: Scatter plot with cluster coloring

---

## Non-Functional Requirements

### NFR-1: Dependencies
- numpy, scipy, sklearn, matplotlib
- No model inference required (analysis only)

### NFR-2: Performance
- Single-pass analysis, <1 minute runtime
- No GPU required

### NFR-3: Reproducibility
- Random seed: 42
- Save all intermediate results to JSON

---

## Success Criteria

### Primary Gate Condition
```
(point_biserial_r > 0.4) OR (cohens_d > 0.3 AND partial_r > 0.3)
```

### Secondary Metrics
- Cross-model consistency (similar correlations across 3 models)
- Feature breakdown shows differential prevalence in inversion cluster

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| H-E1 cluster results | h-e1/code/outputs/results.json | Required |
| H-M3 validation | 04_validation.md | Completed |

---

## Output Files

| File | Description |
|------|-------------|
| code/h_m4_experiment.py | Main analysis script |
| code/outputs/results.json | Correlation metrics |
| figures/gate_metrics.png | Required visualization |
| 04_validation.md | Validation report |
