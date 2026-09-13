# Experimental Setup

## Experimental Questions

Our experiments address three questions corresponding to the ablation ladder:

**EQ1 (H-E1)**: Does the CIFAR-10 Model Zoo provide sufficient accuracy variance for meaningful property prediction evaluation?

**EQ2 (H-M1)**: Does layer-wise encoding significantly outperform Flatten+MLP baseline?

**EQ3 (H-M2)**: Does Git Re-Basin alignment preprocessing further improve layer-wise encoding?

## Dataset Details

### CIFAR-10 Model Zoo

We use the publicly available Model Zoo dataset containing 61,335 CNN checkpoints trained on CIFAR-10 with varying hyperparameters:

| Property | Value |
|----------|-------|
| Total models | 61,335 |
| Architecture family | CNN (VGG-style, ResNet-style) |
| Accuracy range | 10% – 95% |
| Accuracy mean | 72.3% |
| Accuracy std (σ) | 15.62% |

The dataset was obtained from Zenodo following the Model Zoos publication protocol.

### Data Splits

- **Training**: 80% (49,068 models)
- **Test**: 20% (12,267 models)
- **Split method**: Random stratified by accuracy bins
- **Consistency**: Same split used for all embedding methods

## Baselines and Methods

### Methods Evaluated

| Method | Description | Status |
|--------|-------------|--------|
| Flatten+MLP | Flatten weights, MLP encoder | Completed |
| Layer-wise | Per-layer statistics (mean, std, min, max) | Completed |
| Layer-wise+GRB | Layer-wise with Git Re-Basin alignment | Resource-limited |
| NFN | Neural Functional Transformer | Blocked |

### Baseline Selection Rationale

**Flatten+MLP** represents the simplest possible embedding approach, ignoring all structure. This establishes the floor performance.

**Layer-wise** adds minimal structural bias: per-layer statistics. If this fails to improve over Flatten+MLP, more complex approaches are unlikely to help.

## Implementation Details

### Layer-wise Encoder

```
Input: Model weights θ with L layers
For each layer l:
    s_l = [mean(θ_l), std(θ_l), min(θ_l), max(θ_l)]
Concatenate: S = [s_1; s_2; ...; s_L]
Encode: e = MLP(S)
Output: 128-dim embedding
```

**MLP Architecture**:
- Input: 4 × L (statistics per layer)
- Hidden: 256 units, ReLU
- Output: 128-dim embedding

### Regressor Head

Both methods use identical regressor for fair comparison:
- Input: 128-dim embedding
- Hidden: 64 units, ReLU
- Output: 1 (predicted accuracy)

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | 0.001 |
| Weight decay | 0.0001 |
| LR schedule | ReduceLROnPlateau |
| Schedule factor | 0.5 |
| Schedule patience | 5 epochs |
| Batch size | 256 |
| Max epochs | 50 |
| Early stopping | 10 epochs patience |

### Computational Resources

- **Hardware**: CPU-only environment
- **Training time**: ~15 min per seed (Layer-wise)
- **Total experiments**: 2 methods × 5 seeds = 10 runs

## Evaluation Protocol

### Metrics

- **Pearson correlation (r)**: Primary metric measuring linear relationship between predicted and ground-truth accuracy
- **Mean Absolute Error (MAE)**: Secondary metric in accuracy percentage points

### Statistical Testing

- **Test**: Paired t-test comparing r values across 5 seeds
- **Significance level**: α = 0.05
- **Effect size thresholds**: Δr > 0.1 (P1), Δr > 0.05 (P2, P3)

### Success Criteria

| Prediction | Criterion | What it Tests |
|------------|-----------|---------------|
| P1 | Layer-wise r > Flatten r + 0.1, p < 0.05 | Layer-wise structure helps |
| P2 | GRB r > Layer-wise r + 0.05, p < 0.05 | Alignment helps |
| P3 | NFN r > GRB r + 0.05, p < 0.05 | Equivariance helps |

## Scope Limitations

### What We Evaluate

- CNN architectures on CIFAR-10
- Accuracy as target property
- Single model zoo dataset

### What We Do Not Evaluate

- Cross-architecture generalization (CNN → ViT)
- Multi-property prediction (robustness, domain)
- Other model zoo datasets

These limitations are explicit scope boundaries, not confounds. Generalization is future work.
