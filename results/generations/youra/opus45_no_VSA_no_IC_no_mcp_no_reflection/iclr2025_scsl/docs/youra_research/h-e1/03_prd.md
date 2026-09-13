# Product Requirements Document: H-E1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis:** H-E1 (EXISTENCE)
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Validate that early training gradients under spurious correlations primarily capture spurious feature directions. This is a MUST_WORK gate hypothesis - failure stops the pipeline.

**Core Claim:** Gradient subspace S accumulated via incremental SVD during epochs 1-10 aligns with spurious features (>70%) more than core features (<30%).

---

## Problem Statement

Neural networks exhibit simplicity bias, learning spurious correlations before core features. This experiment validates that gradient subspace accumulation can capture and quantify this bias.

**Success Criteria:**
- spurious_alignment > 0.70 at epoch 10
- core_alignment < 0.30 at epoch 10

---

## Functional Requirements

### FR-1: Dataset Loading
- Load Waterbirds dataset (4795 train, 1199 val, 5794 test)
- Apply preprocessing: 224×224 resize, ImageNet normalization
- Train augmentation: RandomResizedCrop, RandomHorizontalFlip
- Maintain group labels for spurious/core direction computation

### FR-2: Baseline Model
- ResNet-50 pretrained on ImageNet (torchvision)
- Replace final FC: Linear(2048, 2)
- Standard ERM training with CrossEntropyLoss

### FR-3: Gradient Subspace Accumulator
- Accumulate flattened gradients during epochs 1-10
- Compute top-50 principal directions via SVD
- Store subspace S as (num_params, 50) matrix

### FR-4: Direction Computation
- Spurious direction: average gradient when background changes, label same
- Core direction: average gradient when bird type changes

### FR-5: Alignment Measurement
- Compute cosine similarity between subspace S and spurious/core directions
- Log alignment at epochs 5, 10, 45

### FR-6: Visualization
- Bar chart: spurious vs core alignment at epochs 5, 10, 45
- Line plot: alignment evolution over training
- Save to h-e1/figures/

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42
- Single seed sufficient for EXISTENCE validation

### NFR-2: Performance
- Training: ~2 hours on single GPU
- Memory: <16GB GPU RAM

### NFR-3: Logging
- Log metrics to console and CSV
- Save model checkpoints at accumulation end (epoch 10)

---

## Training Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | SGD (momentum=0.9, wd=1e-4) | group_DRO |
| Learning Rate | 1e-3 | group_DRO |
| Schedule | StepLR(60,75), gamma=0.1 | ImageNet standard |
| Batch Size | 128 | group_DRO |
| Epochs | 90 | Standard |
| Accumulation | epochs 1-10 | Experiment design |
| Subspace rank | 50 | Experiment design |

---

## Success Metrics

| Metric | Target | Gate |
|--------|--------|------|
| spurious_alignment | > 0.70 | MUST_WORK |
| core_alignment | < 0.30 | MUST_WORK |
| code_runs | no errors | Required |

---

## Dependencies

- PyTorch >= 1.9
- torchvision
- WILDS or manual Waterbirds download
- matplotlib (visualization)

---

## Out of Scope

- Multiple seeds (PoC only)
- Hyperparameter tuning
- Alternative architectures
- Group DRO or other mitigation methods

---

*Generated for Phase 3 Implementation Planning*
