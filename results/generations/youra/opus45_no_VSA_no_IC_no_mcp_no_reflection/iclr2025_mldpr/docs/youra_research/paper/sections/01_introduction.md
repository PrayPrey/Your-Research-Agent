# Introduction

While prior work has established that deep learning models lose 10-14% accuracy when evaluated on ImageNet-V2, an independently-collected variant of ImageNet, we demonstrate that their *relative rankings* remain remarkably stable. Across 96 models with results on both benchmarks, we measure Kendall-τ = 0.96—indicating that the model you would choose based on ImageNet performance is almost certainly the same model you would choose based on ImageNet-V2 performance. This finding has immediate practical implications: benchmark-based model selection decisions generalize to novel test distributions, at least within the ImageNet family.

## The Problem

The concentration of research attention on a small set of benchmark datasets is well documented. The top 10% of datasets account for 90% of benchmark usage in machine learning research [Koch et al., 2021]. For computer vision, ImageNet dominates: a decade of model development has been optimized against its validation set. When Recht et al. (2019) created ImageNet-V2 by replicating the original data collection methodology, models universally experienced 11-14% accuracy drops—raising concerns about "benchmark overfitting."

But accuracy degradation is not the same as *ranking instability*. A model ranked 10th on ImageNet might still be ranked 10th on ImageNet-V2, even if both accuracy values are lower. The critical question for practitioners is not whether absolute accuracy transfers, but whether *relative model quality* transfers. If rankings are preserved, then benchmark-based model selection remains valid despite distribution shift.

This distinction has been overlooked. Prior work focused on absolute accuracy metrics, documenting drops but not systematically analyzing whether those drops preserve or disrupt the relative ordering of models. We address this gap directly.

## Our Approach

We conduct the first systematic measurement of ranking stability between ImageNet and ImageNet-V2. Our methodology is straightforward:

1. **Data Collection.** We collect accuracy results for 96 models evaluated on both ImageNet and ImageNet-V2 from Papers With Code leaderboards.

2. **Ranking Correlation.** We compute Kendall-τ, the standard ordinal correlation metric, between the two ranking lists. We pre-register a threshold of τ < 0.90 as "significant ranking shift."

3. **Statistical Inference.** We bootstrap 95% confidence intervals (10,000 iterations) to quantify uncertainty.

## Key Insight

Our central finding is that accuracy degradation is approximately *uniform* across models. When all models lose roughly the same percentage of accuracy, their relative rankings are preserved. This explains why τ = 0.96: the distribution shift affects model accuracy but not model ordering.

## Contributions

Building on this insight, we make the following contributions:

- **First systematic ranking stability analysis.** We compute Kendall-τ between ImageNet and ImageNet-V2 leaderboards across 96 models, finding τ = 0.9647 with 95% CI [0.9454, 0.9795].

- **Evidence of uniform degradation.** We show that accuracy drops are approximately uniform (mean 11.68%), explaining why rankings are preserved despite accuracy loss.

- **Practical validation of benchmark-based selection.** Our results indicate that model selection decisions based on ImageNet generalize to ImageNet-V2-like distributions.

The remainder of this paper is organized as follows. Section 2 discusses related work on benchmark evaluation and distribution shift. Section 3 describes our methodology. Section 4 presents experimental setup, Section 5 reports results, and Section 6 discusses implications and limitations. Section 7 concludes.
