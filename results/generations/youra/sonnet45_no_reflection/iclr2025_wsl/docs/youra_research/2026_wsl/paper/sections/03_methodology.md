# Methodology

We design a cross-architecture quotient space encoder that extends NFN's approach to heterogeneous model populations. Our method combines Deep Sets for permutation invariance, architecture embeddings to provide family-specific context, and an explicit MSE-based equivariance loss to encourage factorization of architecture-specific conventions. While this approach failed (as documented in Section 5), understanding the design rationale illuminates why alternative approaches are necessary.

## Problem Formulation

Let $\mathcal{M} = \{M_1, ..., M_N\}$ be a model zoo containing neural networks from multiple architecture families $\mathcal{A} = \{\text{CNN}, \text{Transformer}, \text{RNN}\}$. Each model $M_i$ has weights $\mathbf{w}_i \in \mathbb{R}^{d_a}$ where dimensionality $d_a$ varies by architecture family. Each architecture family $a \in \mathcal{A}$ has a permutation group $G_a$ representing valid neuron reorderings, layer swaps, and structural permutations that preserve the computed function.

**Goal**: Learn an encoder $E_a: \mathbb{R}^{d_a} \to \mathbb{R}^K$ that projects model weights into a shared $K$-dimensional quotient space $\mathcal{Z}$ such that:

1. **Quotient space property**: Permutation-equivalent weights map to the same point: $E_a(g \cdot \mathbf{w}) = E_a(\mathbf{w})$ for $g \in G_a$
2. **Architecture-independence**: The quotient space is shared across architectures: $\mathcal{Z}_{\text{CNN}} = \mathcal{Z}_{\text{Transformer}} = \mathcal{Z}_{\text{RNN}}$
3. **Task-relevant structure**: The quotient representation preserves information relevant to the model's task while factoring out coordinate conventions

## Architecture Overview

### Deep Sets Backbone

**Design Choice**: We adopt Deep Sets [Zaheer et al., 2017] as our encoder backbone, processing model weights as sets of parameter groups.

**Rationale**: Deep Sets provides permutation invariance by construction through its aggregation step, ensuring that reordering parameter groups does not change the final encoding. This is a natural fit for weight-space learning where neuron permutations are a fundamental symmetry. NFN demonstrated this architecture's effectiveness on homogeneous model populations, making it the natural starting point for extension to heterogeneous populations.

**Implementation**: Given model weights $\mathbf{w} = \{\mathbf{w}_1, ..., \mathbf{w}_m\}$ partitioned into $m$ parameter groups (layers or modules), the encoder computes:

$$\mathbf{z} = \rho\left(\sum_{i=1}^{m} \phi(\mathbf{w}_i, \mathbf{c}_a)\right)$$

where $\phi: \mathbb{R}^{d} \times \mathbb{R}^{64} \to \mathbb{R}^{256}$ is a per-element encoding network, $\mathbf{c}_a \in \mathbb{R}^{64}$ is the architecture embedding for family $a$, and $\rho: \mathbb{R}^{256} \to \mathbb{R}^K$ is the final projection to quotient space. Both $\phi$ and $\rho$ are implemented as MLPs with ReLU activations.

**Alternatives Considered**: We considered Slot Attention [Locatello et al., 2020] which uses learned attention-based aggregation instead of fixed sum pooling, potentially capturing richer structural relationships. However, we prioritized starting with the proven Deep Sets approach before exploring more complex alternatives. Our failure suggests Slot Attention should be tested in future work.

### Architecture Embeddings

**Design Choice**: We inject 64-dimensional learnable architecture embeddings $\mathbf{c}_a$ for each family $a \in \{\text{CNN}, \text{Transformer}, \text{RNN}\}$ before the per-element encoding step.

**Rationale**: Architecture embeddings provide family-specific context to help the encoder learn which permutation symmetries are relevant. The intuition is that knowing "this is a CNN" allows the encoder to apply CNN-specific permutation invariances (spatial locality, channel permutations) rather than trying to learn a single universal permutation operator. This design follows standard practice in multi-domain learning where domain embeddings improve generalization.

**Implementation**: The architecture embedding $\mathbf{c}_a$ is concatenated with each weight group before processing through $\phi$: $\phi(\mathbf{w}_i, \mathbf{c}_a) = \text{MLP}([\mathbf{w}_i; \mathbf{c}_a])$. The embeddings are learned end-to-end during training.

**Failure Insight**: Frozen-K generalization results (10.31% error) suggest this design may be counterproductive. Architecture embeddings may anchor representations to family-specific coordinates, preventing the cross-architecture abstraction we sought. Domain adversarial training [Ganin et al., 2016] explicitly removes domain information to encourage shared representations—our approach does the opposite. Future work should test pure architecture-agnostic encoders.

### MSE-Based Equivariance Loss

**Design Choice**: We augment the standard reconstruction loss with an explicit MSE-based equivariance loss that encourages permutation invariance:

$$\mathcal{L}_{\text{equiv}} = \mathbb{E}_{M \sim \mathcal{M}, g \sim G_a} \|E_a(g \cdot \mathbf{w}) - \rho(g) E_a(\mathbf{w})\|^2$$

where $\rho(g): \mathbb{R}^K \to \mathbb{R}^K$ is a learned slot permutation operator approximating the quotient group action.

**Rationale**: While Deep Sets provides permutation invariance within the aggregation step, it does not guarantee that the overall encoding $E_a$ is invariant to weight permutations. The equivariance loss provides explicit gradient signal for learning this property. We use MSE distance as a natural extension of the reconstruction loss, maintaining differentiability and computational efficiency.

**Implementation**: During training, for each batch we sample random permutations $g$ from the architecture-specific permutation group (implemented as random neuron reorderings) and compute the loss on both original and permuted weights. The slot permutation operator $\rho$ is implemented as a lightweight MLP that maps permutation structure to quotient space transformations. The total loss is:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{recon}} + \lambda_{\text{equiv}} \mathcal{L}_{\text{equiv}}$$

with $\lambda_{\text{equiv}} = 0.5$ balancing reconstruction accuracy and equivariance.

**Critical Failure**: Kernel robustness of 0.00% reveals this loss design is fundamentally inadequate. MSE encourages similarity between $E_a(g \cdot \mathbf{w})$ and $\rho(g) E_a(\mathbf{w})$ but does not enforce the group homomorphism constraint needed for true equivariance. Gradient descent finds local minima where the encoder ignores permutations entirely. This suggests successful approaches will require either contrastive learning (positive pairs: permuted weights; negative pairs: different models) or explicit group constraints built into the architecture (à la group-equivariant networks [Cohen & Welling, 2016]).

**Alternatives Not Tested**: InfoNCE contrastive loss $\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(z, z_{\text{perm}})/\tau)}{\sum_j \exp(\text{sim}(z, z_j)/\tau)}$ where $z = E(\mathbf{w})$, $z_{\text{perm}} = E(g \cdot \mathbf{w})$, and $z_j$ are negative samples from different models. This provides stronger signal by explicitly pushing away non-permuted models while pulling together permuted versions.

## Training Procedure

**Dataset**: We generate a synthetic ModelZoo-14K containing 1000 models split 70% train, 15% validation, 15% test. The model zoo consists of 40% CNNs, 40% Transformers, and 20% RNNs with random weight initialization. While simplified compared to real pretrained models, this synthetic approach enables rapid prototyping and clear failure signal isolation.

**Optimization**: We use Adam optimizer with learning rate 1e-3, weight decay 1e-4, and cosine annealing schedule. Training runs for 20 epochs with early stopping (patience=10). The equivariance loss weight is fixed at $\lambda_{\text{equiv}} = 0.5$.

**Quotient Space Dimension**: We set $K=32$ based on initial experiments balancing expressiveness and computational cost. This proved severely insufficient (19.18% reconstruction error), suggesting $K \sim 100-200$ may be needed for even synthetic 1000-dimensional weights, and $K \sim 1000-2000$ for real 100K-dimensional model weights based on Johnson-Lindenstrauss bounds.

## Evaluation Protocol

We design three complementary gate metrics to comprehensively evaluate whether quotient space learning succeeds:

### Reconstruction Error

**Metric**: Mean squared error between original weights and reconstructed weights after encoding-decoding through quotient space: $R = \mathbb{E}[\|\mathbf{w} - D(E(\mathbf{w}))\|^2 / \|\mathbf{w}\|^2]$ where $D: \mathbb{R}^K \to \mathbb{R}^{d_a}$ is a learned decoder.

**Success Criterion**: $R < 10\%$ (target <10% information loss).

**Purpose**: Tests whether the $K$-dimensional quotient space has sufficient capacity to capture task-relevant structure. High reconstruction error indicates quotient dimensionality is insufficient.

### Frozen-K Generalization

**Metric**: Train encoder on CNN+Transformer models, then test reconstruction error on held-out RNN models with frozen quotient dimension $K$: $R_{\text{RNN}} = \mathbb{E}_{M \in \text{RNN}_{\text{test}}}[\|\mathbf{w} - D(E(\mathbf{w}))\|^2 / \|\mathbf{w}\|^2]$.

**Success Criterion**: $R_{\text{RNN}} < 10\%$ (similar to training architectures).

**Purpose**: Tests whether the quotient space is truly architecture-independent. If $R_{\text{RNN}} \gg R_{\text{CNN/Transformer}}$, the encoder learned architecture-specific representations rather than a shared canonical space.

### Kernel Robustness

**Metric**: For each test model, apply 1000 random weight permutations $g \sim G_a$ and measure quotient space divergence $D = \|E(g \cdot \mathbf{w}) - E(\mathbf{w})\|$. Report percentage of permutations with $D < 0.01$.

**Success Criterion**: ≥90% of permutations should preserve quotient representation (divergence <0.01).

**Purpose**: Directly tests the quotient space property—permutation-equivalent weights must map to the same point. This is the most critical metric: without permutation invariance, quotient-level canonicalization is impossible regardless of reconstruction quality.

## Implementation Details

Code is implemented in PyTorch with the following structure:
- **Data module**: Synthetic model zoo generation with configurable architecture distributions
- **Model module**: Deep Sets encoder with architecture embeddings, learned slot permutation operator, reconstruction decoder
- **Loss module**: Combined reconstruction + equivariance loss with configurable $\lambda_{\text{equiv}}$
- **Training module**: Adam optimizer, cosine annealing, early stopping, gradient clipping (max_norm=1.0)
- **Evaluation module**: Three gate metrics computed on held-out test set

All experiments use a single GPU (CUDA device selection based on availability). Training takes approximately 2 hours for 20 epochs on the 1000-model synthetic zoo. Full code and hyperparameters are provided in the supplementary material.

## Why This Design Failed

Our approach failed comprehensively across all three metrics (detailed in Section 5), revealing fundamental issues with each design component:

1. **MSE equivariance loss**: 0.00% kernel robustness shows it does not enforce group structure. Contrastive learning or explicit constraints needed.
2. **Architecture embeddings**: 10.31% frozen-K error suggests they prevent cross-architecture abstraction. Pure architecture-agnostic encoding should be tested.
3. **Quotient dimensionality**: 19.18% reconstruction error at $K=32$ indicates severe underestimation. Real applications likely need $K \sim 1000-2000$.

These failures provide concrete guidance for future work: replace MSE loss with InfoNCE contrastive learning, ablate architecture embeddings, increase $K$ by 4-8×, and validate on homogeneous populations (CNN-only) before attempting cross-architecture extension.
