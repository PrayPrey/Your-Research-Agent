# Product Requirements Document: h-c2

**Hypothesis:** Mode profiles transfer across model families: cross-model Pearson r > 0.7 (LLaMA, Mistral, Qwen)
**Type:** CONDITION
**Gate:** SHOULD_WORK
**Date:** 2026-08-24

---

## Executive Summary

Validate that attribution method mode profiles (memorization, feature transfer, spurious sensitivity) exhibit stable transfer across architecturally distinct model families. Success criterion: all pairwise cross-model Pearson correlations r > 0.7.

---

## Problem Statement

### Background
h-m1 established that different attribution methods create distinct mode sensitivity profiles. This hypothesis tests whether these profiles are model-invariant—a critical property for generalizable data influence understanding.

### Goal
Demonstrate cross-architecture stability of mode profiles using vision models: ResNet-18, ViT-Small, ConvNeXt-Tiny.

---

## Functional Requirements

### FR-1: Multi-Model Training Pipeline
- Train 3 architecturally distinct models on CIFAR-10
- Models: ResNet-18 (CNN), ViT-Small (Transformer), ConvNeXt-Tiny (Modern CNN)
- Checkpoints: Save every 10 epochs
- Minimum test accuracy: >85% per model

### FR-2: Consistent Probe Application
- Reuse h-m1 probe pairs across all models
- 1000 pairs × 3 modes (memorization, feature_transfer, spurious)
- Identical probe indices for all models

### FR-3: Attribution Computation
- Primary method: TRAK (fast, cross-architecture support)
- Verification: Kronfluence (accuracy validation)
- Output: mode_profile[model][mode] = mean influence score

### FR-4: Cross-Model Correlation
- Compute pairwise Pearson r for profile vectors
- Pairs: ResNet-ViT, ResNet-ConvNeXt, ViT-ConvNeXt
- Bootstrap 95% CI for each correlation

### FR-5: Statistical Testing
- Bonferroni correction for 3 comparisons (α = 0.05/3)
- Report p-values for all correlations

### FR-6: Visualization
- Cross-model profile heatmap (3×3 models × modes)
- Correlation bar chart with r > 0.7 threshold line
- Profile radar charts per model

---

## Non-Functional Requirements

### NFR-1: Computational
- Single GPU execution (≤24GB VRAM)
- Training: <4 hours total (3 models)
- Attribution: <2 hours per model

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic dataloaders
- Version-pinned dependencies

---

## Dependencies

### From h-m1
- Probe pair indices (memorization, feature_transfer, spurious)
- TRAK/Kronfluence integration patterns
- Mode profile computation methodology

### External
- torchvision (CIFAR-10, ResNet-18)
- timm (ViT-Small, ConvNeXt-Tiny)
- trak, kronfluence (attribution)
- scipy (Pearson correlation)

---

## Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| All pairwise r | > 0.7 | PASS |
| Mean r > 0.7, some pairs below | 0.5-0.7 | PARTIAL |
| Mean r < 0.7 | < 0.5 | FAIL |

---

## Data Specifications

### Dataset
- **Name:** CIFAR-10
- **Source:** torchvision.datasets.CIFAR10
- **Train:** 50,000 images
- **Test:** 10,000 images

### Models
| Model | Architecture | Params | Source |
|-------|--------------|--------|--------|
| ResNet-18 | CNN + residual | 11M | torchvision |
| ViT-Small | Transformer | 22M | timm |
| ConvNeXt-Tiny | Modern CNN | 28M | timm |

---

## Ablation Variants

### ABL-1: Attribution Method Comparison
- TRAK vs Kronfluence profile correlations
- Expected: similar transfer patterns

### ABL-2: Probe Subset Sensitivity
- Random 50% probe subset
- Check correlation stability

---

## Traceability

| Requirement | Phase 2C Source |
|-------------|-----------------|
| FR-1 | Models section |
| FR-2 | Contrastive Probes |
| FR-3 | Core Mechanism Implementation |
| FR-4 | Evaluation section |
| FR-5 | Statistical Tests |
| FR-6 | Visualization Requirements |
