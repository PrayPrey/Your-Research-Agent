# Phase 2B Context: H-M1

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK

## Hypothesis Statement

Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%)

## Prerequisites

- h-e1 (VALIDATED)

## Status

IN_PROGRESS

## Rationale

Tests Prediction P2 from Phase 2A. Core mechanism claim: architectural inductive biases lead to preferential property capture.

## Test Plan

- Train Transformer and GNN backbones on unperturbed weights
- Apply within-layer permutations (symmetry-preserving)
- Apply across-layer permutations (symmetry-breaking)
- Measure prediction accuracy under each perturbation
- Success: GNN shows >30% differential, Transformer <10%
- Failure: No differential OR both show similar differential

## Controlled Variables (from Phase 2A)

| Variable | Control Method |
|----------|----------------|
| Dataset | timm Model Zoo (standard pre-trained models) |
| Model | Transformer, Equivariant GNN backbones |
| Architecture Capacity | Parameter-matched (same model size) |
| Training Procedure | Same optimizer, learning rate schedule, epochs |
| Input Preprocessing | Layer-wise weight tokenization (consistent) |

## Success Criteria

GNN symmetry differential >30%, Transformer <10%

## Risk Analysis

- **Risk**: Architectural priors don't align with weight-space properties as predicted
- **Impact**: Blocks H-C1, weakens main hypothesis
- **Mitigation**: Theory-grounded taxonomy (permutation equivariance, locality/globality)
- **Contingency**: If failed, route to Phase 0 (fundamental mechanism assumption violated)

## Main Hypothesis Context

**Main Hypothesis ID**: H-WeightOrthogonality-v1  
**Title**: Orthogonal Expressivity of Weight-Processing Backbones

**Statement**: Under the domain of neural network weight-space learning, if we process weights with multiple backbone architectures (transformer, equivariant GNN, MLP) that target orthogonal structural properties (global dependencies, permutation symmetry, local patterns), then combining their learned representations will significantly outperform individual backbones on weight-to-property prediction and anomaly detection tasks (>5% on property prediction, >10% on backdoor detection), because each architecture captures complementary aspects of weight structure that individual backbones miss.

## Key Related Work (from Phase 2A)

**Baselines to Compare**:
1. Transformer-based weight embeddings (lacks permutation equivariance)
2. Equivariant GNN weight processors (limited global dependency modeling)

## Prerequisite Results

**H-E1 Key Findings** (VALIDATED):
- Layer-wise tokenization preserves structural signal (80% test accuracy)
- Weight transformer achieved 80% accuracy, exceeding 60% gate threshold
- Baseline MLP also achieved 80% accuracy with per-layer statistics
- Both models significantly outperform random baseline (25%)
- Tokenization strategy (flatten + pad + normalize) validated for weight-space learning

**Proven Components from H-E1**:
- Layer-wise weight flattening and padding
- Per-layer normalization (mean 0, std 1)
- Property prediction as validation task (test accuracy prediction)
- timm Model Zoo as dataset source
- Transformer architecture for weight processing
