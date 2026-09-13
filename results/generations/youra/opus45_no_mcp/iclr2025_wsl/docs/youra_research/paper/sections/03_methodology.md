# Methodology

## Ablation Ladder Design

Our goal is isolating the contribution of structural inductive biases to property prediction. We design a four-step ablation ladder where each step adds exactly one bias:

| Step | Method | Structural Bias Added |
|------|--------|----------------------|
| 1 | Flatten+MLP | None (baseline) |
| 2 | Layer-wise | Per-layer processing |
| 3 | Layer-wise+GRB | Permutation alignment |
| 4 | NFN | Permutation equivariance |

This design enables direct measurement: if Step 2 outperforms Step 1, layer-wise processing provides benefit. If Step 3 outperforms Step 2, alignment adds further improvement.

## Embedding Architectures

### Flatten+MLP (Baseline)

All network parameters are concatenated into a single vector and passed through an MLP encoder:

$$\mathbf{e} = \text{MLP}(\text{flatten}(\theta))$$

This baseline ignores network structure entirely, treating weights as an unordered collection.

### Layer-wise Encoding

For each layer $l$, we compute four statistics: mean, standard deviation, minimum, and maximum of the weight values. These statistics are concatenated across layers:

$$\mathbf{s}_l = [\mu(\theta_l), \sigma(\theta_l), \min(\theta_l), \max(\theta_l)]$$
$$\mathbf{e} = \text{MLP}([\mathbf{s}_1; \mathbf{s}_2; \ldots; \mathbf{s}_L])$$

This preserves layer-level structure: conv1 statistics remain separate from fc3 statistics.

### Layer-wise+GRB

Before computing layer-wise statistics, we align each model to a reference using Git Re-Basin:

$$\theta' = \text{GRB\_align}(\theta, \theta_{\text{ref}})$$
$$\mathbf{e} = \text{LayerWise}(\theta')$$

This removes permutation-induced variance, ensuring functionally equivalent networks have similar representations.

### Neural Functional Transformer

NFN processes weights using permutation-equivariant layers by design, avoiding explicit alignment. We add a permutation-invariant pooling head to extract fixed-dimensional embeddings.

## Regression Head

All embeddings feed into the same MLP regressor for fair comparison:

- Hidden dimension: 64
- Output dimension: 1 (predicted accuracy)
- Activation: ReLU
- Loss: MSE between predicted and ground-truth accuracy

## Dataset

We use the CIFAR-10 Model Zoo containing N = 61,335 pretrained CNN checkpoints with ground-truth accuracy labels from standardized evaluation. Key properties:

- **Accuracy variance**: σ = 15.62% (above 10% threshold)
- **Architecture**: CNN variants (similar to ResNet)
- **Split**: 80% train / 20% test, fixed across methods

The substantial variance confirms the benchmark is non-trivial—high-variance prediction is required, not just predicting the mean.

## Training Protocol

- **Optimizer**: AdamW (lr=0.001, weight_decay=0.0001)
- **Schedule**: ReduceLROnPlateau (factor=0.5, patience=5)
- **Epochs**: 50 with early stopping (patience=10)
- **Batch size**: 256
- **Seeds**: 5 independent runs (0, 1, 2, 3, 4)

## Evaluation Metrics

- **Primary**: Pearson correlation (r) between predicted and ground-truth accuracy
- **Secondary**: Mean absolute error (MAE)
- **Statistical test**: Paired t-test across seeds (α = 0.05)

## Success Criteria

From our hypothesis:
- **P1**: Layer-wise > Flatten+MLP by Δr > 0.1 (p < 0.05)
- **P2**: Layer-wise+GRB > Layer-wise by Δr > 0.05 (p < 0.05)
- **P3**: NFN > Layer-wise+GRB by Δr > 0.05 (p < 0.05)

These thresholds were calibrated against baseline variance to represent meaningful improvements.
