# Experimental Setup

We design experiments to answer the following questions:

**RQ1:** Is the Kendall-τ correlation between ImageNet and ImageNet-V2 rankings below 0.90 (our threshold for "significant ranking shift")?

**RQ2:** What is the statistical confidence in our correlation estimate?

**RQ3:** What is the distribution of per-model rank changes, and what explains ranking preservation?

## Data Collection

### Source

We collect model accuracy data from Papers With Code leaderboards:
- **ImageNet:** Top-1 accuracy on ILSVRC 2012 validation set
- **ImageNet-V2:** Top-1 accuracy on MatchedFrequency variant

Papers With Code aggregates community-reported results using standardized evaluation protocols, ensuring comparability across models.

### Inclusion Criteria

We include all models with reported results on both benchmarks. This yielded:

| Attribute | Value |
|-----------|-------|
| Total models | 96 |
| Publication years | 2015-2024 |
| Architecture families | ResNet, ViT, ConvNeXt, EfficientNet, Swin, DeiT, others |
| Accuracy range (ImageNet) | 76.1% - 91.1% |
| Accuracy range (V2) | 63.8% - 81.4% |

### Selection Bias Considerations

Models with poor V2 results may be underreported, which would *understate* ranking instability. Our finding of high stability is thus conservative—if selection bias exists, true stability is likely lower (not higher).

## Evaluation Metrics

### Primary Metric: Kendall-τ

Kendall-τ (tau-b) measures ordinal correlation between two rankings:

- τ = 1.0: Perfect agreement (identical rankings)
- τ = 0.0: No correlation (random orderings)
- τ = -1.0: Perfect disagreement (reversed rankings)

**Pre-registered threshold:** We consider τ < 0.90 as "significant ranking shift" based on prior ranking stability literature suggesting τ ≥ 0.95 indicates essentially identical rankings.

### Secondary Metrics

- **Spearman-ρ:** Alternative ranking correlation for robustness
- **Mean accuracy drop:** Average (ImageNet - V2) accuracy difference
- **Maximum rank change:** Largest |rank_ImageNet - rank_V2| across models
- **Top-10 overlap:** Proportion of ImageNet Top-10 appearing in V2 Top-10

## Statistical Inference

### Bootstrap Confidence Intervals

We estimate 95% confidence intervals via bootstrap resampling:
- 10,000 iterations
- Percentile method: [2.5th percentile, 97.5th percentile]
- Non-parametric (no distributional assumptions)

### Hypothesis Test

- **H1 (original hypothesis):** τ < 0.90 (rankings shift significantly)
- **H0 (null hypothesis):** τ ≥ 0.90 (rankings preserved)

If the 95% CI falls entirely above 0.90, we fail to reject H0 and conclude rankings are preserved.

## Implementation

- **Language:** Python 3.10
- **Libraries:** scipy 1.10 (kendalltau, spearmanr), numpy 1.24 (bootstrap)
- **Compute:** Standard laptop (no GPU required for statistical analysis)
- **Runtime:** < 1 minute for full analysis including bootstrap
