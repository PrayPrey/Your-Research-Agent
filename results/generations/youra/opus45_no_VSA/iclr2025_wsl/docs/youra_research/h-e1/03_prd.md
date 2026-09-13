# Product Requirements Document: H-E1

**Date:** 2026-08-10
**Hypothesis:** CV_PR can be reliably extracted from 100+ timm models using randomized SVD with 20 seeds
**Type:** EXISTENCE (Proof of Concept)

---

## Executive Summary

Develop extraction pipeline to compute Coefficient of Variation of Participation Ratio (CV_PR) across 100+ pretrained timm models. Validates feasibility of spectral analysis methodology for subsequent hypotheses.

---

## Problem Statement

Need to verify that CV_PR metric can be reliably computed across diverse neural network architectures using randomized SVD with multiple random seeds for variance estimation.

---

## Functional Requirements

### FR-1: Model Loading
- Load 100+ pretrained models from timm library
- Filter models with ImageNet-1K weights and reported top-1 accuracy
- Architecture families: ResNet, ViT, EfficientNet, ConvNeXt, DenseNet, etc.

### FR-2: Weight Extraction
- Extract weight matrices from conv2d and linear layers
- Reshape 4D conv weights to 2D (out_channels × flattened)
- Skip bias terms and non-weight parameters

### FR-3: Randomized SVD Implementation
- Implement Halko algorithm with random projection
- Support configurable rank (default: 50)
- Support seed control for reproducibility

### FR-4: Participation Ratio Computation
- Compute PR = (Σλ)² / Σλ² from singular values
- Handle edge cases (zero eigenvalues, numerical stability)

### FR-5: CV_PR Aggregation
- Run 20 seeds per layer
- Compute mean, std, CV across seeds
- Aggregate per-layer CV_PR to model-level metric

### FR-6: Results Logging
- Log extraction progress (model count, time)
- Save per-model CV_PR results to CSV/JSON
- Generate summary statistics

---

## Non-Functional Requirements

### NFR-1: Performance
- Process each model in < 60 seconds
- Total extraction time < 4 hours for 100+ models

### NFR-2: Reliability
- Handle model loading failures gracefully
- Continue extraction on individual layer failures

### NFR-3: Reproducibility
- Fixed seed sequence across all runs
- Deterministic results for same input

---

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Extraction completion rate | ≥ 95% |
| CV_PR values finite | 100% in range (0, 10) |
| Within-model variance | CV of CV < 100% |

---

## Dependencies

- PyTorch ≥ 1.9
- timm library (latest)
- NumPy, SciPy

---

## Out of Scope

- Training or fine-tuning models
- Correlation analysis (H-E2)
- Model comparison (H-M series)
