# Phase 2B Context: H-E1

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK

## Hypothesis Statement

Layer-wise weight tokenization preserves sufficient structural signal for backbone comparison tasks (property prediction, symmetry tests)

## Prerequisites

None (foundation hypothesis)

## Status

READY

## Rationale

Before testing backbone complementarity, must verify that layer-wise processing doesn't destroy the signal. This is Assumption A1 from Phase 2A.

## Test Plan

- Train single backbone (Transformer or GNN) on layer-wise tokenized weights
- Measure property prediction accuracy on held-out models
- Success: Accuracy significantly above random baseline (e.g., >60% on test accuracy prediction)
- Failure: Accuracy near random (layer-wise processing loses too much information)

## Controlled Variables (from Phase 2A)

| Variable | Control Method |
|----------|----------------|
| Dataset | timm Model Zoo (standard pre-trained models) + Backdoor Benchmark |
| Model | Transformer, Equivariant GNN, MLP backbones |
| Architecture Capacity | Parameter-matched (same model size) |
| Training Procedure | Same optimizer, learning rate schedule, epochs |
| Input Preprocessing | Layer-wise weight tokenization (consistent) |

## Success Criteria

Property prediction accuracy >60% (significantly above random)

## Risk Analysis

- **Risk**: Layer-wise processing loses critical cross-layer dependencies
- **Impact**: Blocks all downstream hypotheses (H-M1, H-M2, H-C1)
- **Mitigation**: Two-stage validation (synthetic networks with known structure → real model zoo)
- **Contingency**: If failed, route to Phase 2A-Dialogue for hypothesis modification (consider full-network processing alternatives)

## Main Hypothesis Context

**Main Hypothesis ID**: H-WeightOrthogonality-v1  
**Title**: Orthogonal Expressivity of Weight-Processing Backbones

**Statement**: Under the domain of neural network weight-space learning, if we process weights with multiple backbone architectures (transformer, equivariant GNN, MLP) that target orthogonal structural properties (global dependencies, permutation symmetry, local patterns), then combining their learned representations will significantly outperform individual backbones on weight-to-property prediction and anomaly detection tasks (>5% on property prediction, >10% on backdoor detection), because each architecture captures complementary aspects of weight structure that individual backbones miss.

## Key Related Work (from Phase 2A)

**Baselines to Compare**:
1. Transformer-based weight embeddings (lacks permutation equivariance)
2. Equivariant GNN weight processors (limited global dependency modeling)
3. Model stitching (Lenc & Vedaldi, 2015) - validates layer-wise assumption but not a weight-processing backbone

**Best Baseline Performance**: To be established in Phase 4 (synthetic networks) → Phase 5 (real model zoo comparison)
