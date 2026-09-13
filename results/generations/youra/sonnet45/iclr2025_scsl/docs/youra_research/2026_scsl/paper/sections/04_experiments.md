# Experimental Setup

We designed experiments to test three specific mechanism hypotheses about geometric structure in SSL embeddings. This section describes datasets, implementation details, evaluation metrics, and success criteria.

## Datasets

### Waterbirds

Waterbirds (Sagawa et al., 2020) contains 11,788 images from two bird types (landbirds, waterbirds) placed on two background types (land, water). The spurious correlation is 93% in training data: landbirds predominantly appear on land backgrounds, waterbirds on water backgrounds. The dataset has 4 spurious groups with severe class imbalance:
- Group 0 (landbird, land): 3,498 samples (56%)
- Group 1 (landbird, water): 184 samples (3%)  [minority]
- Group 2 (waterbird, water): 1,640 samples (27%)
- Group 3 (waterbird, land): 133 samples (2%)  [minority]

**Rationale:** Strong spurious correlation (93%) maximizes cluster formation probability. If clusters don't form under these conditions, they are unlikely to form with weaker correlations.

## Implementation Details

### SimCLR Baseline

- **Architecture**: ResNet-50 encoder (pretrained=False) + 2-layer MLP projection head (2048 → 128)
- **InfoNCE loss**: Temperature $\tau=0.5$, batch size 32
- **Augmentations**: RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter(0.4, 0.4, 0.4, 0.1), RandomGrayscale(0.2)
- **Optimizer**: SGD with momentum 0.9
- **Learning rate**: Grid search over {0.01, 0.001, 0.0001}
- **Weight decay**: Grid search over {1e-4, 1e-5, 1e-6}
- **Training**: 20 epochs (POC), planned 100 epochs (full-scale)

### LA-SSL Variant

Identical to SimCLR except:
- **Learning-speed tracking**: Compute $v_i = |\mathcal{L}_e(x_i) - \mathcal{L}_{e-1}(x_i)|$ over epochs 10-15
- **Resampling**: Sample with probability $\propto \exp(-\alpha v_i)$ where $\alpha=0.1$
- **Schedule**: Start resampling at epoch 16 (after learning speeds stabilize)

### Cluster-Balanced Retraining

- **Clustering**: k-means with k=4 on L2-normalized embeddings from final epoch
- **Linear probe**: Single linear layer (2048 → 2) trained with cluster-balanced cross-entropy
- **Hyperparameters**: Learning rate 0.001, batch size 32, 10 epochs

## Evaluation Metrics

### Clusterability Metrics

1. **Adjusted Mutual Information (AMI)**: Measures cluster-label agreement adjusted for chance. Range [0, 1], threshold 0.4 for "high clusterability"
2. **Silhouette Score**: Measures cluster separation/compactness. Range [-1, 1], threshold 0.3 for "well-separated clusters"

### Fairness Metrics

1. **Worst-Group Accuracy (WGA)**: $\min_{g \in \{0,1,2,3\}} \text{Acc}_g$ - Minimum accuracy across 4 spurious groups
2. **$\Delta$WGA**: Improvement in WGA from cluster-balanced retraining vs standard linear probe
3. **Average Accuracy**: Overall classification accuracy (for reference, not primary metric)

### Linear Separability Metrics

1. **Linear Probe AUC**: Binary classification AUC (minority vs majority groups) using linear probe on frozen embeddings
2. **$\Delta$AUC**: Difference in linear AUC between LA-SSL and SimCLR (measures whether separability is preserved)

## Experimental Questions and Success Criteria

### Q1: Does InfoNCE create spurious clusters? (M1)

**Experiment**: Train SimCLR on Waterbirds, extract final-epoch embeddings, compute AMI and Silhouette.

**Success Criteria**:
- AMI ≥ 0.4 (indicates reliable cluster-label agreement)
- Silhouette ≥ 0.3 (indicates well-separated clusters)
- **Gate Type**: MUST_WORK (primary hypothesis)

**Falsifier**: If AMI ≈ 0 (chance level), spurious features don't form discrete clusters.

### Q2: Does clusterability predict intervention efficacy? (M2)

**Experiment**: Stratify models by AMI (high vs low), apply cluster-balanced retraining, measure $\Delta$WGA.

**Success Criteria**:
- Positive correlation between AMI and $\Delta$WGA (Pearson r > 0, p < 0.05)
- High-AMI models achieve $\Delta$WGA ≥ 2.0pp
- Low-AMI models achieve $\Delta$WGA < 0.5pp
- **Gate Type**: MUST_WORK (diagnostic requires predictive power)

**Falsifier**: If no correlation or negative correlation, AMI cannot serve as fairness diagnostic.

### Q3: Does LA-SSL disperse clusters while preserving separability? (M3)

**Experiment**: Train SimCLR and LA-SSL with identical hyperparameters, compare AMI and linear AUC.

**Success Criteria**:
- AMI reduction ≥ 30% (LA-SSL vs SimCLR)
- $\Delta$AUC < 0.05 (separability preserved)
- **Gate Type**: Secondary (can fail gracefully if M1+M2 pass)

**Falsifier**: If AMI and AUC both drop ≥30%, LA-SSL suppresses signal entirely (undesirable).

## Training Infrastructure

All experiments conducted on:
- **Hardware**: Single NVIDIA GPU (selected via `nvidia-smi` for availability)
- **Framework**: PyTorch 1.13, Python 3.9
- **Reproducibility**: 5 random seeds per configuration
- **Validation**: Code quality verified via 43/43 tests passing (h-e1), 5/5 tests passing (h-m-integrated), 100% SDD compliance

**Note**: POC experiments (20 epochs) validate implementation feasibility. Full-scale experiments (100 epochs, planned as future work) will definitively test whether clusters emerge at scale.
