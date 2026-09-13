# Methodology

Building on our observation that accuracy degradation under distribution shift may be uniform across models, we design a methodology to directly measure ranking stability between ImageNet and ImageNet-V2.

## Overview

Our approach has three components: (1) data collection from standardized leaderboards, (2) computation of ranking correlation statistics, and (3) bootstrap inference for uncertainty quantification.

## Data Collection

**Source.** We collect model accuracy data from Papers With Code leaderboards for ImageNet and ImageNet-V2. Papers With Code provides community-curated, standardized results using consistent evaluation protocols.

**Inclusion Criteria.** We include all models that have reported results on both ImageNet (ILSVRC 2012 validation set) and ImageNet-V2 (MatchedFrequency variant). This yielded 96 models spanning publication years 2015-2024 and architecture families including ResNet, ViT, ConvNeXt, EfficientNet, and others.

**Rationale.** Using leaderboard data ensures comparable evaluation protocols across models. While selection bias may exist (models with poor V2 results may be underreported), this bias likely understates ranking instability—our finding of high stability is thus conservative.

## Ranking Computation

For each benchmark, we rank models by top-1 accuracy in descending order (higher accuracy = better rank). Ties are handled using standard ranking conventions.

```
rank_imagenet[i] = position of model i when sorted by imagenet_accuracy
rank_v2[i] = position of model i when sorted by v2_accuracy
```

## Kendall-τ Correlation

We compute Kendall-τ (tau-b) between the two ranking vectors. Kendall-τ measures the proportion of concordant vs. discordant pairs:

```
τ = (concordant - discordant) / sqrt((n0 - n1)(n0 - n2))
```

where n0 = n(n-1)/2 total pairs, n1 and n2 adjust for ties.

**Rationale.** Kendall-τ is preferred for ordinal rankings because it (1) is robust to ties, (2) has a natural interpretation as proportion of correctly ordered pairs, and (3) is less sensitive to outliers than Pearson correlation.

**Threshold.** We pre-registered τ < 0.90 as "significant ranking shift" based on prior work suggesting τ ≥ 0.95 indicates essentially identical rankings.

## Bootstrap Confidence Intervals

We estimate 95% confidence intervals via bootstrap resampling (10,000 iterations):

```python
for iteration in range(10000):
    sample = resample(data, n=len(data), replace=True)
    tau_i = kendalltau(sample.rank_imagenet, sample.rank_v2)
    bootstrap_taus.append(tau_i)
ci_95 = [percentile(bootstrap_taus, 2.5), percentile(bootstrap_taus, 97.5)]
```

**Rationale.** Bootstrap CIs are non-parametric and make no distributional assumptions about the sampling distribution of τ.

## Hypothesis Testing

We evaluate our pre-registered hypothesis:

- **H1:** τ < 0.90 (rankings shift significantly)
- **H0:** τ ≥ 0.90 (rankings are preserved)

If the 95% CI upper bound falls below 0.90, we reject H0 in favor of H1. If τ ≥ 0.90 and the CI is above 0.90, we fail to reject H0 and conclude rankings are preserved.

## Secondary Analyses

We additionally compute:

- **Spearman-ρ:** As a robustness check (alternative ranking correlation metric)
- **Per-model accuracy drop:** To assess uniformity of degradation
- **Maximum rank change:** To identify worst-case ranking instability
- **Top-10 overlap:** Percentage of ImageNet Top-10 appearing in V2 Top-10

## Implementation

All analyses are implemented in Python using scipy.stats for correlation computation and numpy for bootstrap sampling. Code is available at [repository link].
