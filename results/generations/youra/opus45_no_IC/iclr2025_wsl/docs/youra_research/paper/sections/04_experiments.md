# Experimental Setup

Our experiments are designed to answer four research questions:

**Q1:** Does NFN outperform MLP at small data scales? (H-E1)
**Q2:** Is NFN truly permutation invariant? (H-M1, H-M2)
**Q3:** Does MLP lack inherent invariance? (H-M3)
**Q4:** Does MLP learn invariance at large scale? (H-M4, H-M5)

## Dataset

We use the Model Zoo dataset [Schürholt et al., 2022], which contains 50K+ CNN models trained on CIFAR-10 under varying conditions (hyperparameters, training duration, random seeds). We select a homogeneous subset of ~42K models sharing the same architecture to ensure a consistent permutation group.

**Rationale:** Homogeneous architecture ensures valid permutation symmetry—all models have identical layer shapes, so permutations are well-defined. Mixed architectures would confound equivariance effects with architecture variation.

### Data Characteristics

| Property | Value |
|----------|-------|
| Total models | ~42,000 |
| Architecture | CIFAR-10 CNN (fixed) |
| Accuracy range | 10% - 95% |
| Weight dimensions | ~50K parameters/model |
| Train/test split | 80/20 (fixed) |

## Scale Conditions

We evaluate at multiple data scales to characterize how the NFN-MLP gap evolves:

| Scale | Training Models | Purpose |
|-------|-----------------|---------|
| N=1K | 1,000 | Small-scale efficiency (H-E1) |
| N=40K | ~34,000 | Large-scale convergence (H-M5) |

The test set is fixed across all conditions (8,000 models), ensuring comparable evaluation.

## Models

### NFN Configuration

```yaml
architecture:
  channels: 32
  layers: [NPLinear, ReLU, NPLinear, ReLU, HNPPool, Linear(1)]

training:
  optimizer: AdamW
  learning_rate: 1e-3
  weight_decay: 1e-4
  scheduler: CosineAnnealingLR
  epochs: 50
  batch_size: 32
```

### MLP-Matched Configuration

```yaml
architecture:
  hidden_dim: 256  # Matched to NFN parameter count
  layers: [Linear, ReLU, Linear, ReLU, Linear(1)]

training:
  optimizer: AdamW
  learning_rate: 1e-3
  weight_decay: 1e-4
  scheduler: CosineAnnealingLR
  epochs: 50
  batch_size: 32
```

## Evaluation Metrics

### Primary Metric: R²

Coefficient of determination on held-out test set:

$$R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}$$

where $y_i$ is true accuracy, $\hat{y}_i$ is predicted accuracy, and $\bar{y}$ is mean accuracy.

### Mechanism Metric: Probe Invariance

For a trained model M:

1. Generate K=10 random permutations per test sample
2. Compute predictions under each permutation
3. Average pairwise correlations: $I = \text{mean}(\text{corr}(\hat{y}_{\pi_i}, \hat{y}_{\pi_j}))$

For mathematically invariant models: I = 1.0
For models without invariance: I < 1.0

### Auxiliary Metrics

- **Deviation under permutation:** max|ŷᵢ - ŷⱼ| across permutations (for H-M1, H-M2)
- **Coefficient of variation:** std/mean of predictions across permutations (for H-M3)

## Experimental Protocol

### H-E1: NFN vs MLP at N=1K

Train both models on N=1K, evaluate R² on test set. Success: NFN R² > MLP R² + 0.05.

### H-M1: NFN Layer Equivariance

Apply NFN to weight tensor W and permuted version π(W). Measure deviation in intermediate representations. Success: max deviation < 1e-5.

### H-M2: NFN Prediction Invariance

Generate 10 permutations of test weights. Measure prediction correlation. Success: correlation > 0.99.

### H-M3: MLP Lacks Inherent Invariance

Apply untrained (random initialization) MLP to permuted weights. Measure coefficient of variation. Success: CV > 0.1 (confirming no built-in invariance).

### H-M4: MLP Invariance at N=1K

Train MLP on N=1K, measure probe invariance on test set. Expected: low invariance if MLP hasn't learned symmetry.

### H-M5: MLP Invariance at N=40K

Train MLP on N=40K, measure probe invariance on test set. This tests the "data teaches invariance" hypothesis. Success criterion: invariance > 0.8.

## Reproducibility

All experiments use fixed random seeds for train/test splits. Code and model checkpoints available at [anonymous repository].
