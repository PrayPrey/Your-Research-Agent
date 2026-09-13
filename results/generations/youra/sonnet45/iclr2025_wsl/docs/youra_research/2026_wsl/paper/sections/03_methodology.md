# Methodology

## Overview

Building on our observation that diverse weight types can be projected into a shared representation space while preserving architecture-specific information, we design a **Compositional Architecture-Agnostic Weight Encoder (CAWE)**. The key insight is to decouple structural diversity handling (via architecture-specific tokenizers) from quality learning (via shared NFT backbone). This compositional approach enables cross-architecture generalization gap prediction without requiring architecture-specific end-to-end pipelines or losing family-specific signals.

CAWE consists of three main components: (1) architecture-specific tokenizers that project CNN kernels, Transformer Q/K/V matrices, and MLP weights to D=128 token sequences, (2) a shared Neural Functional Transformer backbone that processes these tokens with permutation-equivariant attention, and (3) a regression head that predicts generalization gap from the learned weight-space embeddings.

## Architecture-Specific Tokenizers

### Rationale

Different neural network architectures store fundamentally different information in their weights. Convolutional kernels encode spatial locality patterns, Transformer attention matrices capture relationship structures, and fully-connected layers represent direct input-output mappings. Forcing these diverse weight types into a single preprocessing format would destroy architecture-specific inductive biases. Therefore, we design specialized tokenizers for each family.

### CNN Tokenizer

For convolutional neural networks, we extract weight tensors layer-by-layer and flatten each kernel to create token sequences:

1. For each conv layer with weights W ∈ R^(C_out × C_in × K_h × K_w), extract individual kernels
2. Flatten each kernel to a vector and project to D=128 via learned linear layer
3. Concatenate tokens from all layers to form a sequence of length T_CNN

This preserves spatial structure information while normalizing dimensionality across different kernel sizes.

### Transformer Tokenizer

For Vision Transformers, we extract Query/Key/Value projection matrices from each attention head:

1. For each transformer layer, extract Q, K, V weight matrices from all attention heads
2. Flatten each matrix and project to D=128 via learned linear layer
3. Concatenate tokens from all layers and heads to form sequence of length T_ViT

This captures the relationship-learning structure encoded in attention mechanisms while abstracting away specific embedding dimensions.

### MLP Tokenizer

For fully-connected networks, we process layer-wise weight matrices:

1. For each FC layer with weights W ∈ R^(n_out × n_in), flatten the weight matrix
2. Project to D=128 via learned linear layer
3. Concatenate tokens from all layers to form sequence of length T_MLP

This representation preserves layer-wise transformation patterns characteristic of MLPs.

### Design Decision: D=128 Token Dimension

**Rationale**: The shared token dimension D=128 balances expressivity and computational efficiency. D=64 proved insufficient to preserve discriminative information in preliminary experiments, while D=256 incurred unnecessary computational overhead without performance gains. D=128 provides sufficient capacity for the NFT attention mechanism to discover cross-layer quality patterns.

## Shared NFT Backbone

### Rationale

Once diverse weight types are projected to the shared D=128 token space, we need an architecture-agnostic processing mechanism that can learn quality-predictive patterns. Standard transformers would break under neuron permutation symmetries inherent to neural network weights. Therefore, we adopt Neural Functional Transformers with permutation-equivariant attention.

### NFT Architecture

We use the NFT implementation from the `nfn` library [Zhou et al., 2023], which provides:

1. **Permutation-equivariant self-attention**: Attention mechanism that respects neuron reordering symmetries
2. **Parameter sharing across layers**: Reduces parameter count while maintaining expressivity
3. **Layer-wise aggregation**: Combines information across tokens to produce fixed-size embeddings

Configuration:
- Number of attention heads: 8
- Number of NFT layers: 4
- Hidden dimension: 512
- Dropout: 0.1

### Why NFT Over Standard Transformers

Standard transformer attention is not equivariant to neuron permutations. If we reorder neurons in a neural network (which doesn't change its function), standard attention would produce different representations. NFTs handle this symmetry through specialized attention mechanisms, making them suitable for weight-space processing.

## Regression Head

The final component maps NFT embeddings to generalization gap predictions:

1. NFT backbone produces embedding e ∈ R^512
2. Two-layer MLP with ReLU activation
3. Output: scalar generalization gap prediction ĝ

Loss function: Mean Squared Error between predicted and actual generalization gaps (test accuracy - train accuracy).

## Training Protocol

**Hyperparameters**:
- Optimizer: AdamW with learning rate 1e-4
- Batch size: 16 (for 150-model PoC) / 32 (for planned 750-model full-scale)
- Training epochs: 100 with early stopping (patience=10)
- Weight decay: 1e-5
- Learning rate scheduler: ReduceLROnPlateau (factor=0.5, patience=5)

**Data Split**:
- 80% training, 10% validation, 10% test
- Stratified sampling to ensure balanced architecture family representation

**Early Stopping**: Monitor validation Spearman ρ. Stop training if no improvement for 10 consecutive epochs. This prevents overfitting on small-scale proof-of-concept experiments.

## Alternative Designs Considered

**Flat Weight Concatenation**: Concatenating all weights into a single vector and processing with standard MLP. This destroys structural information and fails to leverage architecture-specific patterns.

**Graph Neural Networks**: Representing neural networks as computation graphs. While conceptually appealing, GNN approaches require explicit graph construction and don't leverage the sequential processing efficiency of transformers.

**Learned Token Dimension**: Allowing the model to learn optimal token dimensions per architecture. This adds complexity without clear benefits, as fixed D=128 proved sufficient.

**Architecture-Specific End-to-End Pipelines**: Training separate models for CNN, Transformer, and MLP families. This loses the opportunity for cross-architecture transfer and requires 3× the training compute.

Our compositional design balances simplicity (single shared backbone), expressivity (architecture-specific tokenization), and efficiency (fixed token dimension, permutation-equivariant attention).
