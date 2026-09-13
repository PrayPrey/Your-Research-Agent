# Methodology

We designed an experiment to test whether coefficient of variation (CV) of linear probe accuracy trajectories can distinguish spurious from core features. The methodology consists of three components: feature extraction, CV measurement, and classification evaluation.

## Feature Extraction

We use CLIP ViT-B/16 (Radford et al., 2021) as the feature extractor. CLIP was pretrained on 400 million image-text pairs using contrastive learning. For each Waterbirds image, we extract the 512-dimensional embedding from the final layer.

**Rationale**: CLIP is widely used for representation analysis and contains visual concepts relevant to Waterbirds (backgrounds, bird types). Using frozen pretrained features tests whether emergence dynamics can be recovered post-hoc.

## CV Measurement Protocol

### Probe Training

For each concept (background, bird\_type), we train logistic regression probes with scikit-learn's `LogisticRegression`:

```
C_values = [0.001, 0.01, 0.1, 1, 10, 100]
```

The regularization strength C serves as an "epoch proxy" — lower C corresponds to stronger regularization and potentially earlier stopping in an analogous training process.

### Subset Sampling

To measure emergence uniformity, we train probes on multiple random subsets:

- **n\_subsets**: 5 random 20% samples of training data
- **seed**: 42 for reproducibility

### CV Computation

For each concept:
1. Train probes on each subset across all C values
2. Record accuracy at each (subset, C) combination
3. Compute improvement rate: `acc[C_i] - acc[C_{i-1}]`
4. Calculate CV of improvement rates across subsets

$$\text{CV} = \frac{\sigma(\text{improvement rates})}{\mu(\text{improvement rates})}$$

**Hypothesis**: Spurious features (background) should show low CV (uniform emergence); core features (bird\_type) should show high CV (differential emergence across implicit groups).

## Classification Evaluation

### Ground Truth Labels

Waterbirds provides ground truth for which features are spurious vs. core:
- **background**: Spurious (land/water, 95% correlated with label)
- **bird\_type**: Core (landbird/waterbird, the actual classification target)

### Metrics

- **AUC**: Area under ROC curve for CV-based classification
- **Gate threshold**: AUC ≥ 0.75 for hypothesis validation

The AUC metric is appropriate for binary classification (2 feature types). A random classifier achieves AUC = 0.5; our gate requires substantial discriminative power.

## Experimental Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Feature extractor | CLIP ViT-B/16 | Standard, captures visual concepts |
| Embedding dim | 512 | CLIP default |
| Probe | LogisticRegression | Convex, reproducible |
| C sweep | [0.001, 0.01, 0.1, 1, 10, 100] | Standard range |
| n\_subsets | 5 | Balance variance estimation / cost |
| subset\_fraction | 0.2 | Sufficient samples per subset |
| Dataset | Waterbirds (train split) | 4795 samples |
| Gate | AUC ≥ 0.75 | MUST\_WORK threshold |

## Design Decisions

**Why frozen features?** Testing whether emergence dynamics can be recovered from pretrained models without additional training. If successful, this enables efficient single-run detection.

**Why C-sweep as epoch proxy?** Regularization strength affects convergence behavior similarly to early stopping. Lower C → more regularized → analogous to fewer epochs.

**Why CV across subsets?** Emergence uniformity should manifest as consistent learning across sample subsets. Spurious features, correlated with labels universally, should emerge uniformly. Core features, relevant to specific subgroups, should emerge with higher variance.

## Limitations of Design

The methodology tests one operationalization of emergence uniformity. Alternative approaches (actual training epochs, loss curves, layer-wise probing) may yield different results. This design specifically tests post-hoc probing on frozen pretrained features.
