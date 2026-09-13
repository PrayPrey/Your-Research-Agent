# Product Requirements Document: h-e1

**Date:** 2026-08-28
**Hypothesis:** Locality inductive bias difference exists between DWS and NFT architectures
**Type:** EXISTENCE (PoC)
**Author:** PrayPrey

---

## Executive Summary

Validate that DWS and NFT architectures exhibit measurably distinct processing patterns on weight-space inputs. DWS uses locality-preserving equivariant layers (per-layer processing before aggregation) while NFT uses global attention across all weight tokens. Success demonstrates fundamental architectural differences in inductive bias.

---

## Problem Statement

Weight-space learning architectures (DWS, NFT) claim different inductive biases but empirical evidence of distinct processing patterns is limited. This experiment establishes existence of measurable locality bias differences.

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1**: Download MNIST INRs dataset from DWSNets Dropbox
- **FR-1.2**: Load SIREN weight tensors from .pt files
- **FR-1.3**: Normalize weights (zero mean, unit variance per layer)
- **FR-1.4**: Create train/test DataLoaders (batch_size=64)

### FR-2: Baseline Model (Flattened MLP)
- **FR-2.1**: Implement FlattenedMLP with layers [512, 256, 128]
- **FR-2.2**: Input: concatenated flattened weight vectors
- **FR-2.3**: Output: 10-class logits
- **FR-2.4**: ReLU activation, Dropout(0.1)

### FR-3: DWS Model
- **FR-3.1**: Implement DWSLayer with per-layer weight processing
- **FR-3.2**: Cross-layer aggregation after local processing
- **FR-3.3**: Hook for extracting layer activations
- **FR-3.4**: Locality score computation

### FR-4: NFT Model
- **FR-4.1**: Implement WeightTokenizer for weight-to-token conversion
- **FR-4.2**: TransformerEncoder with 4 heads, 2 layers
- **FR-4.3**: Hook for extracting attention weights
- **FR-4.4**: Attention entropy computation

### FR-5: Training
- **FR-5.1**: AdamW optimizer (lr=1e-3, weight_decay=1e-4)
- **FR-5.2**: CosineAnnealingLR (T_max=50)
- **FR-5.3**: CrossEntropyLoss
- **FR-5.4**: 50 epochs, seed=42

### FR-6: Evaluation Metrics
- **FR-6.1**: Test accuracy (torchmetrics)
- **FR-6.2**: Attention entropy for NFT
- **FR-6.3**: Layer activation variance for DWS
- **FR-6.4**: Mechanism verification checks

### FR-7: Visualization
- **FR-7.1**: Gate metrics bar chart (accuracy comparison)
- **FR-7.2**: Attention pattern heatmap (NFT)
- **FR-7.3**: Layer activation profile (DWS)
- **FR-7.4**: Representation t-SNE

---

## Non-Functional Requirements

- **NFR-1**: Single GPU execution (CUDA)
- **NFR-2**: Reproducibility via fixed seed
- **NFR-3**: Training completion under 2 hours
- **NFR-4**: Memory footprint under 8GB VRAM

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| All models train without error | Required |
| Accuracy > 90% (all models) | Required |
| DWS locality score < 1.0 | Expected |
| NFT attention entropy > 2.0 | Expected |
| Measurable pattern difference | Required |

---

## Dependencies

- PyTorch 1.12+
- torchmetrics
- matplotlib
- scikit-learn (t-SNE)

---

## Out of Scope

- Multi-seed statistical analysis
- Hyperparameter optimization
- Large-scale datasets beyond MNIST INRs
- Production deployment

---

*PRD generated for EXISTENCE hypothesis - minimal viable scope for PoC validation*
