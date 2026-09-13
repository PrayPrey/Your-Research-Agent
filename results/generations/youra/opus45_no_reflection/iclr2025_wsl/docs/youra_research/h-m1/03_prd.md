# Product Requirements Document: H-M1

**Date:** 2026-08-19
**Hypothesis:** Weight Matrices Encode Behavioral Information
**Type:** MECHANISM
**Phase:** Implementation Planning

---

## Executive Summary

Validate that weight matrix statistics predict class-wise accuracy profiles better than stratified baseline. Uses Small CNN Zoo (~30k models) with Ridge regression probe on per-layer weight statistics.

---

## Problem Statement

H-E1 established behavioral variance exists (residual_ratio=0.6758). H-M1 tests the causal mechanism: do weights encode this behavioral information?

**Gate:** MUST_WORK - proposed_R2 > baseline_R2

---

## Functional Requirements

### FR-1: Data Loading
- Load Small CNN Zoo CIFAR-10 checkpoint weights
- Filter to final epoch (epoch 86) only
- Expected: ~30,000 models × 4,970 parameters
- Split: 80% train / 20% test (~24k/6k)

### FR-2: Class-wise Accuracy Extraction
- Compute per-class accuracy for each model (10 classes)
- Output: (N, 10) matrix of class accuracies

### FR-3: Baseline Model (Stratified)
- Features: [overall_accuracy, class_difficulty_per_class]
- Model: Ridge regression (alpha=1.0)
- Predicts: 10-class accuracy vector

### FR-4: Proposed Model (Weight Statistics)
- Extract per-layer statistics: mean, std, min, max, norm
- 4 layers × 5 stats = 20 features
- Model: Ridge regression with StandardScaler
- Predicts: 10-class accuracy vector

### FR-5: Evaluation
- Primary metric: R² (coefficient of determination)
- Per-class R² and mean R² across 10 classes
- Success: proposed_R2 > baseline_R2

### FR-6: Visualization
- Required: Gate metrics comparison bar chart (proposed vs baseline R²)
- Optional: predicted vs actual scatter, feature importance

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for train/test split
- All hyperparameters documented

### NFR-2: Statistical Validity
- Use full ~30k models (not small subset)
- Report confidence intervals if available

---

## Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| proposed_R2 > baseline_R2 | True | GATE (MUST_WORK) |
| Code executes without error | True | Required |
| Results reproducible | True | Required |

---

## Dependencies

- NumPy, Pandas, scikit-learn
- Small CNN Zoo dataset (pre-downloaded or download script)
- H-E1 completion (SATISFIED)

---

## Data Specifications

### Input
- `cifar10_weights.npy`: (N, 4970) flattened weights
- `metrics.csv.gz`: model metadata including test_accuracy

### Output
- `results.json`: R² scores, gate pass/fail
- `figures/`: visualization outputs

---

## References

- Unterthiner et al. 2020: "Predicting Neural Network Accuracy from Weights" (R² > 0.98)
- Phase 2C Experiment Brief: 02c_experiment_brief.md
