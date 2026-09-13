# Product Requirements Document: H-E1

**Hypothesis:** SR ≈ 1 at initialization (no intrinsic curvature asymmetry)
**Date:** 2026-08-09
**Author:** Anonymous
**Type:** EXISTENCE (Proof-of-Concept)
**Budget Tier:** LIGHT (max 15 tasks)

---

## Executive Summary

Validate that Sharpness Ratio (SR) equals approximately 1.0 at random initialization, confirming no intrinsic curvature asymmetry exists between minority and majority groups before training. This is a measurement-only experiment (no training required).

---

## Problem Statement

**Research Question:** Does the loss landscape exhibit group-dependent curvature asymmetry at random initialization?

**Null Hypothesis:** SR₀ ≈ 1.0 (symmetric curvature across groups)

**Gate Condition:** SR₀ ∈ [0.9, 1.1] with 95% CI including 1.0

---

## Functional Requirements

### FR-1: Dataset Loading
- Load Waterbirds dataset with 4-group labels
- Source: kohpangwei/group_DRO
- Groups: landbird/land (0), landbird/water (1), waterbird/land (2), waterbird/water (3)
- Minority: groups 1, 2; Majority: groups 0, 3

### FR-2: Model Initialization
- ResNet-50 with random initialization
- Final layer: Linear(2048, 2)
- 5 independent random seeds

### FR-3: Sharpness Computation
- Implement Hessian-vector product via PyTorch autograd
- Power iteration for top eigenvalue (20 iterations)
- Group-wise loss computation

### FR-4: SR Calculation
- SR = sharpness(minority) / sharpness(majority)
- Compute per-seed SR values
- Calculate mean and 95% CI

### FR-5: Visualization
- SR values with error bars across seeds
- Horizontal reference line at SR = 1.0

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for initialization
- Deterministic data loading order

### NFR-2: Compute Efficiency
- ~5 minutes per seed (single GPU)
- Total: ~25 minutes for 5 seeds

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| SR₀ mean | ∈ [0.9, 1.1] |
| 95% CI | Includes 1.0 |
| Code execution | No errors |

---

## Data Specifications

### Input
- Waterbirds: ~4,795 train, ~5,794 test samples
- ImageNet normalization
- 224×224 resolution

### Output
- `results/sr_values.json`: Per-seed SR values
- `figures/sr_comparison.png`: Visualization
- `04_validation.md`: Gate result

---

## Dependencies

### External
- PyTorch >= 1.9
- torchvision (ResNet-50)
- scipy (statistics)
- matplotlib (visualization)

### Data
- CUB-200-2011 images
- Places365 backgrounds
- Waterbirds metadata (group labels)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Hessian computation OOM | Batch gradient accumulation |
| Numerical instability | Gradient clipping, double precision |

---

*PRD generated for EXISTENCE hypothesis - minimal infrastructure, measurement-only protocol*
