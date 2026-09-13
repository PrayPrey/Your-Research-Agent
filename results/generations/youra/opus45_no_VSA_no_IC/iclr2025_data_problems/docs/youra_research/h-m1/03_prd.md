# Product Requirements Document: h-m1

**Date:** 2026-08-24
**Hypothesis:** Different mathematical operations (gradient projection, checkpoint proximity, K-FAC) create systematically different sensitivities to influence modes
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This experiment compares three mathematically distinct training data attribution methods (TRAK, TracIn, Kronfluence) to determine whether they exhibit systematically different sensitivities to influence modes (memorization, feature transfer, spurious association).

---

## Problem Statement

Current understanding lacks empirical evidence for how mathematical differences in attribution methods (random projection vs checkpoint gradient dot product vs K-FAC Hessian approximation) translate to different sensitivity patterns when attributing model behavior to training data.

---

## Functional Requirements

### FR-1: Attribution Method Implementation

**FR-1.1: TRAK (Gradient Projection)**
- Use official MadryLab/trak library
- Parameters: proj_dim=2048, use_half_precision=True
- Compute influence scores for all probe pairs

**FR-1.2: TracIn (Checkpoint Proximity)**
- Use captum or KuchikiRenji/Empirical-Influence-Function
- Require checkpoints every 20 epochs (10 total for 200 epochs)
- Formula: TracIn(z,z') = Σ_k η_k * ∇ℓ(w_k, z) · ∇ℓ(w_k, z')

**FR-1.3: Kronfluence (K-FAC)**
- Use official pomonam/kronfluence library
- Eigenvalue-corrected Kronecker-factored curvature approximation
- Support for ResNet-18 architecture

### FR-2: Dataset and Probes

**FR-2.1: CIFAR-10 Dataset**
- 50,000 training images, 10,000 test images
- Standard torchvision preprocessing (normalize to ImageNet stats)

**FR-2.2: Contrastive Probes**
- 1000 probe pairs per mode (3000 total)
- Memorization: Near-duplicate train-test pairs
- Feature Transfer: Same-class pairs with different visual features
- Spurious Association: Pairs sharing spurious correlation (background)

### FR-3: Model Training

**FR-3.1: Baseline Model**
- ResNet-18 pretrained on ImageNet
- Fine-tune on CIFAR-10 (fc layer replaced for 10 classes)
- SGD optimizer: momentum=0.9, weight_decay=5e-4
- Learning rate: 0.1 with cosine annealing
- Epochs: 200, Batch size: 128
- Save checkpoints every 20 epochs

### FR-4: Evaluation Metrics

**FR-4.1: Mode Sensitivity Scores**
- Mean influence score per mode per method
- Compute: `mean(scores[mode_labels == mode])` for each mode

**FR-4.2: Method × Mode Interaction Matrix**
- 3×3 matrix of normalized sensitivities
- Rows: methods (TRAK, TracIn, Kronfluence)
- Columns: modes (memorization, feature_transfer, spurious)

**FR-4.3: Mode Ranking Comparison**
- Rank modes by sensitivity within each method
- Success: At least one method has different mode ranking than others

### FR-5: Visualization

**FR-5.1: Gate Metrics Comparison (Required)**
- Method × Mode heatmap showing sensitivity patterns

**FR-5.2: Additional Figures (Autonomous)**
- Mode sensitivity radar chart per method
- Influence score distributions per mode
- Method correlation matrix

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Set random seeds (42) for all stochastic operations
- Log all hyperparameters to experiment config

### NFR-2: Performance
- Support GPU acceleration (CUDA)
- Use AMP where supported (Kronfluence)

### NFR-3: Modularity
- Separate attribution computation from evaluation
- Each method in its own module/function

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Code runs for all 3 methods | No runtime errors |
| Non-trivial scores | Variance > 0 for all methods |
| Mode differentiation | At least 2 methods show different mode rankings |

---

## Dependencies

### External Libraries
- trak (pip install traker[fast])
- kronfluence (pip install kronfluence)
- captum or Empirical-Influence-Function (TracIn)
- torchvision (dataset, model)
- scipy, numpy (statistics)
- matplotlib/seaborn (visualization)

### Compute Requirements
- GPU with 16GB+ VRAM recommended
- ~10GB disk for checkpoints

---

## Constraints

- Task Budget: FULL tier (max 30 tasks)
- Epic Range: 6-12 epics
- No VSA (Visual Semantic Alignment) or IC (Instance Conditioned) components per project scope

---

*Generated from Phase 2C experiment brief: 02c_experiment_brief.md*
