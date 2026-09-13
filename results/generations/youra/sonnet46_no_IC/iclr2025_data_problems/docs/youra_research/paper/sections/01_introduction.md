# 1. Introduction

The standard practice in language model pre-training treats data curation as a model-agnostic step: a team chooses a perplexity filtering threshold, a deduplication aggressiveness level, and applies this recipe uniformly across all models in a training cascade. Our experiments challenge this assumption. When we filter the same FineWeb corpus at perplexity threshold τ=20, a 14M-parameter Pythia model achieves its best HellaSwag score. When we apply the same recipe to a 31M-parameter model, it is the *worst* configuration we tested — the 31M model peaks instead at τ=50. The optimal filtering threshold spans the full range of our experimental design space across a 2.2× scale difference.

This observation has a concrete practical implication. A perplexity threshold of τ=20 retains only 176 of 5000 FineWeb documents (3.5%) — it applies extreme selectivity, keeping only the most "standard-English," lowest-perplexity text. A threshold of τ=50 retains 2074 documents (41.5%) — it accepts more diverse, higher-entropy content. Practitioners who apply τ=50 uniformly to a training cascade that includes a 14M-parameter model are training that model on 12× more data than optimal, at the cost of reduced data quality per token.

## 1.1 The Problem: Scale-Independent Curation Recipes

Data curation for language model pre-training has attracted substantial recent attention. Methods including perplexity-based filtering [Zhou et al., 2024; Peng et al., 2025], near-duplicate removal [He et al., 2024; Penedo et al., 2025], and domain mixing [Wettig et al., 2025] each demonstrate improvements in downstream benchmark performance. Yet a consistent pattern runs through this literature: each method is evaluated at a single model scale, and the optimal recipe is reported as a universal recommendation.

The deeper problem is that this implicit scale-independence assumption has never been tested in a controlled multi-scale experiment. The capacity-quality trade-off hypothesis — grounded in Bayesian in-context learning theory [Xie et al., 2022] and capacity-constrained learning dynamics — predicts that smaller models, unable to efficiently extract signal from high-diversity, noisy distributions, should benefit from stricter quality filtering, while larger models should leverage the diversity preserved by looser filtering. This prediction cannot be evaluated from single-scale ablations.

The gap is methodological: testing the Scale × Curation interaction requires a factorial experiment varying both model scale and curation aggressiveness simultaneously. Such experiments are computationally expensive, and prior work on scalable ablation methodology [Na et al., 2024] proposes small proxy models (≪100M parameters) as a shortcut — an approach our results show is insufficient for scale-dependent interaction studies specifically.

## 1.2 Key Insight

The optimal perplexity filtering threshold is model-scale-dependent. Small models (14M parameters) learn best from highly curated, low-diversity data; larger models (31M parameters) learn best from more diverse, less aggressively filtered data. This means that a curation recipe optimized at one scale is suboptimal — and potentially harmful — at another scale.

Building on this insight, we run the first controlled factorial experiment directly testing the Scale × Curation interaction in language model pre-training, using real FineWeb data, real GPT-2 perplexity scoring, and standard lm-evaluation-harness evaluation.

## 1.3 Contributions

Our work makes three contributions:

1. **Scale-dependent optimal PPL threshold confirmed at PoC scale.** We demonstrate that τ*(14M)=20 and τ*(31M)=50 in a 24-run factorial experiment (3 PPL thresholds × 2 dedup levels × 2 scales × 2 seeds) on FineWeb data with Pythia-architecture models. The interaction direction is consistent across all experimental conditions.

2. **PoC scale feasibility boundary for proxy models.** We show empirically that proxy models below approximately 14M parameters with a 2.2× scale ratio are insufficient to exhibit the Scale × Curation interaction — an important methodological observation for the scalable ablation literature.

3. **MMLU floor documented at sub-100M scale.** We confirm that MMLU 4-shot accuracy is at the random baseline (0.25) for all sub-100M models at short pre-training runs, establishing HellaSwag 0-shot as the appropriate metric for pre-training ablations at this scale.

We organize the paper as follows: Section 2 surveys related work on data curation and positions our contribution; Section 3 describes our experimental methodology; Section 4 presents experimental setup; Section 5 reports results; Section 6 discusses implications and limitations; Section 7 concludes.
