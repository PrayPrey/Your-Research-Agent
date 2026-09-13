# Product Requirements Document: H-M1

**Hypothesis:** Spurious features produce stronger gradient signal than core features (gradient norm ratio > 1.5 in early epochs)
**Type:** MECHANISM
**Date:** 2026-08-28
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This experiment tests the mechanism behind spurious feature dominance observed in H-E1. We measure gradient norms for spurious (background) vs core (bird) regions during ERM training to verify that spurious features receive stronger gradient signals, explaining their preferential learning.

---

## Problem Statement

H-E1 established that GradCAM attribution favors spurious features (ratio 1.35-1.59). The underlying mechanism remains unverified. This experiment directly measures gradient signal strength to test whether gradient-based optimization preferentially updates toward spurious features.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load Waterbirds v1.0 dataset from kohpangwei/group_DRO
- Include ground-truth bird segmentation masks
- Train/Val/Test splits preserved
- Preprocessing: 224×224, ImageNet normalization

### FR-2: Model Setup
- ResNet-50 with ImageNet pretrained weights (IMAGENET1K_V1)
- Modify final layer for 2-class output
- Register forward/backward hooks on layer4[-1]

### FR-3: Gradient Norm Tracking
- GradientNormTracker class with hook registration
- Compute regional gradient norms using masks
- Separate spurious (background) vs core (bird) regions
- Store per-batch gradient norms

### FR-4: Training Loop
- SGD optimizer: momentum=0.9, weight_decay=0.0001
- Learning rate: 0.001 with step decay at epochs 60, 120
- Batch size: 128
- Epochs: 50
- Seeds: 3 runs

### FR-5: Metric Computation
- Per-epoch spurious/core gradient norm ratio
- Aggregate statistics across batches
- Track ratio trend over epochs

### FR-6: Visualization
- Gate metrics: Gradient norm ratio bar chart (epochs 1-10)
- Line plot: Ratio trajectory across 50 epochs
- Gradient magnitude heatmaps on sample images

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seeds (42, 123, 456)
- Deterministic operations where possible

### NFR-2: Efficiency
- GPU utilization for training
- Batch gradient norm aggregation

### NFR-3: Compatibility
- PyTorch 2.0+
- Compatible with H-E1 codebase

---

## Success Criteria

1. **Primary:** Gradient norm ratio > 1.5 in epochs 1-10
2. **Secondary:** Ratio decreases over training epochs
3. **Tertiary:** Effect consistent across 3 seeds

**Gate Type:** MUST_WORK
**If Fail:** PIVOT (mechanism description invalid)

---

## Dependencies

### From H-E1 (Prerequisite)
- Waterbirds dataset: verified working
- ResNet-50 training: verified working
- Training protocol: SGD, LR=0.001, batch=128

### External
- pytorch-grad-cam: hook patterns reference
- captum: validation cross-check
- kohpangwei/group_DRO: dataset source

---

## Data Flow

```
Input: Waterbirds images + segmentation masks
  ↓
Model: ResNet-50 with gradient hooks on layer4
  ↓
Forward: Capture activations
  ↓
Loss: CrossEntropyLoss
  ↓
Backward: Capture gradients via hooks
  ↓
Regional Norm: Apply masks, compute ||grad||₂
  ↓
Output: Per-epoch spurious/core ratio
```

---

## Deliverables

1. `train_gradient_tracking.py` - Main training script
2. `gradient_norm_tracker.py` - Hook-based tracker class
3. `evaluate_gradient_ratios.py` - Analysis script
4. `figures/` - Visualization outputs
5. `04_validation.md` - Results report
