# Product Requirements Document (PRD): H-M1

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-08-28  
**Author:** Anonymous

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: "Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%)."

The implementation builds on validated H-E1 infrastructure (layer-wise weight tokenization, timm Model Zoo dataset, Transformer baseline) and adds E(n)-Equivariant GNN backbone with symmetry perturbation analysis.

**Success Criteria:** GNN symmetry differential >30% AND Transformer symmetry differential <10%

---

## Problem Statement

### Context

H-E1 validated that layer-wise weight tokenization preserves structural signal (80% test accuracy). H-M1 tests whether different backbone architectures capture complementary structural properties through their inductive biases.

### Prerequisites

- H-E1 (VALIDATED): Layer-wise tokenization, Transformer baseline, timm Model Zoo dataset

### Hypothesis Statement

Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%).

---

## Functional Requirements

### FR-1: Dataset Infrastructure (Reuse from H-E1)

**Description:** Load and preprocess timm Model Zoo with layer-wise weight tokenization.

**Acceptance Criteria:**
- Load 50-100 pretrained models from timm registry
- Split: 70% train, 15% val, 15% test
- Tokenize: Flatten + pad + per-layer normalize
- Output: [num_layers, max_length] per model
- Property labels: 4-class test accuracy bins

### FR-2: Baseline Model - Transformer

**Description:** Reuse Transformer backbone from H-E1 (validated at 80% accuracy).

**Acceptance Criteria:**
- Architecture: 2-layer Transformer encoder, 128 hidden dim, 4 heads
- Parameter count: ~50K
- Input: [batch, num_layers, max_length]
- Output: [batch, 4] class predictions
- Training: Adam lr=1e-3, batch=32, epochs=50

### FR-3: Proposed Model - E(n)-Equivariant GNN

**Description:** Implement permutation-equivariant GNN backbone for weight processing.

**Acceptance Criteria:**
- Architecture: 2-layer E(n)-Equivariant GNN (EGNNConv or vgsatorras/egnn)
- Parameter count: ~50K (matched with Transformer)
- Graph construction: k-NN or fully connected from weight tokens
- Input: [batch, num_nodes=num_layers, max_length]
- Output: [batch, 4] class predictions
- Equivariance: Preserve permutation symmetry through message passing

### FR-4: Perturbation Protocol

**Description:** Implement within-layer and across-layer permutation perturbations.

**Acceptance Criteria:**
- Within-layer permutation: Shuffle neuron indices within same layer
- Across-layer permutation: Shuffle neuron indices across different layers
- Preserve tensor shapes (pad before permute)
- Apply to test set only

### FR-5: Training Pipeline

**Description:** Train both models on unperturbed weights with identical hyperparameters.

**Acceptance Criteria:**
- Optimizer: Adam (lr=1e-3, weight_decay=1e-4)
- Scheduler: ReduceLROnPlateau (patience=10, factor=0.5)
- Batch size: 32
- Epochs: 50
- Loss: CrossEntropyLoss
- Seeds: Fixed seed=42

### FR-6: Evaluation Metrics

**Description:** Compute symmetry differential for both models.

**Acceptance Criteria:**
- Unperturbed accuracy on test set
- Within-layer perturbed accuracy
- Across-layer perturbed accuracy
- Symmetry differential: |Acc(within) - Acc(across)|
- Compute per model (Transformer and GNN)

### FR-7: Visualization

**Description:** Generate symmetry differential comparison figure.

**Acceptance Criteria:**
- Bar chart: Transformer vs GNN differential
- Accuracy degradation heatmap (2 models × 3 perturbation types)
- Save to h-m1/figures/ (PNG and PDF)

---

## Non-Functional Requirements

### NFR-1: Code Quality

- Modular design: Separate dataset, model, training, evaluation
- Type hints for all functions
- Docstrings for public APIs

### NFR-2: Reproducibility

- Fixed random seeds (torch, numpy, random)
- Checkpoint saving: Best model per validation accuracy
- Log all hyperparameters and metrics

### NFR-3: Performance

- GPU support (CUDA if available)
- Training time: <2 hours on single GPU
- Memory: <8GB GPU RAM

### NFR-4: Dependencies

- PyTorch ≥2.0
- timm (pretrained models)
- torch_geometric (EGNNConv)
- torchmetrics (accuracy)
- matplotlib, seaborn (visualization)

---

## Success Criteria

### Gate Condition (MUST_WORK)

1. Code runs without error
2. GNN symmetry differential >30%
3. Transformer symmetry differential <10%

**IF NOT MET:** Route to Phase 0 (fundamental mechanism re-evaluation)

### Expected Performance

- Unperturbed accuracy: ~80% (both models, from H-E1 baseline)
- GNN: High within-layer acc (~70-75%), low across-layer acc (~40-45%) → differential ~30%+
- Transformer: Similar degradation for both perturbations → differential <10%

---

## Dependencies

### Prerequisites

- H-E1 validation complete (PASS)
- timm library installed
- PyTorch Geometric installed
- GPU available (recommended)

### Reused Components from H-E1

- Dataset: timm Model Zoo
- Tokenization: Layer-wise flatten + pad + normalize
- Hyperparameters: Adam lr=1e-3, batch=32, epochs=50
- Baseline: Transformer architecture

---

## Out of Scope

- Multi-seed experiments (MECHANISM hypothesis - focus on differential measurement)
- Hyperparameter tuning (reuse validated H-E1 settings)
- Additional backbone architectures beyond Transformer and GNN
- Cross-dataset validation (focus on timm Model Zoo)

---

## References

- H-E1 Validation Report: `/docs/youra_research/h-e1/04_validation.md`
- Phase 2C Experiment Brief: `/docs/youra_research/h-m1/02c_experiment_brief.md`
- E(n)-Equivariant GNN Paper: Satorras et al., 2021
- Implementation: vgsatorras/egnn, PyTorch Geometric EGNNConv
