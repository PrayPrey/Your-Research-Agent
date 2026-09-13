# Methodology

## Task Definition

Given a neural network's weight matrices W = {W₁, W₂, ..., Wₗ}, predict its test accuracy a ∈ [0, 1]. The challenge: hidden unit permutations within each layer create equivalent weight configurations. For a layer with N hidden units, there are N! equivalent orderings—all representing identical functions.

## Dataset

We use a synthetic ResNet-20/CIFAR-10 model zoo of 6,000 models. Each model has ~270K parameters across 21 weight layers. Accuracy ranges from 70% to 95%, with variation introduced through training noise. We use fixed splits: train sizes N ∈ {100, 250, 500, 1000, 2500, 5000}, test size 500 (held constant). All experiments use 10 random seeds for confidence intervals.

## Methods

### Statistics Baseline

Following Unterthiner et al. (2020), we extract 7 statistics per weight layer:
- Mean, standard deviation, min, max
- L1 norm, L2 norm, spectral norm

For ResNet-20's 9 relevant layers, this produces 63 features. We apply RidgeCV regression (α selected via cross-validation). This approach is permutation-invariant by construction—layer-wise aggregations are order-independent.

### MLP Baseline

Raw weights are flattened to a single vector (~270K dimensions) and fed to a 2-layer MLP (256 hidden units, ReLU, BatchNorm, Dropout=0.3). This baseline has no inductive bias for permutation symmetry—it treats weights as arbitrary vectors.

### NFN Model (Permutation-Equivariant)

We implement a DeepSets-style equivariant predictor:

1. **Per-neuron encoding**: Each neuron's incoming/outgoing weights are processed by a shared MLP
2. **Equivariant layers**: 2 layers of (shared linear → LayerNorm → ReLU)
3. **Invariant pooling**: Mean aggregation across neurons within each layer
4. **Prediction head**: Layer embeddings concatenated → MLP → scalar output

This architecture guarantees: permuting hidden units produces identical predictions. Training uses Adam (lr=1e-3), batch size 64, early stopping (patience=10).

## Evaluation Metrics

**Primary**: R² coefficient of determination on held-out test set (500 models)

R² = 1 - (Σ(yᵢ - ŷᵢ)²) / (Σ(yᵢ - ȳ)²)

R² < 0 indicates predictions worse than the mean baseline.

**Secondary**: 
- Equivariance error: max|f(Perm(W)) - f(W)| over random permutations
- Statistical significance: two-sample t-test across seeds

## Hypotheses Tested

- **H-E1**: Statistics baseline achieves R² > 0.85 at N=5000 (existence)
- **H-M1**: NFN passes equivariance test with >95% success rate (mechanism)
- **H-M2**: NFN R² exceeds MLP R² by ≥0.1 at N=500, p<0.05 (mechanism)
- **H-C1**: All methods converge within ±0.03 R² at N=5000 (condition)
- **H-C2**: Crossing point N* < 2500 exists where NFN matches Statistics (condition)
