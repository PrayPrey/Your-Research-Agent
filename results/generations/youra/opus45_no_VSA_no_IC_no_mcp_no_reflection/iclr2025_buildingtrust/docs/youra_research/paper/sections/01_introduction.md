# Introduction

Uncertainty-based hallucination detection methods report impressive results—semantic entropy achieves AUROC 0.85 on TruthfulQA [Kuhn et al., 2023], self-consistency reaches 0.80 on WikiBio [Manakul et al., 2023]—yet our pilot study reveals these methods can perform at random or even *inverted* on different benchmarks under identical conditions. This gap between published performance and observed behavior poses a critical challenge for practitioners selecting detection methods: without controlled comparison under matched computational budgets, method selection remains guesswork.

The surface problem is well-known: large language models hallucinate confidently, generating plausible-sounding but factually incorrect outputs [Lin et al., 2022]. Multiple uncertainty-based detection methods have emerged, each demonstrating strong performance on their chosen benchmarks. Semantic entropy clusters generated responses by semantic equivalence via NLI, computing entropy over the cluster distribution [Kuhn et al., 2023]. Self-consistency measures agreement across multiple generations using surface similarity metrics [Manakul et al., 2023]. Contextual calibration adjusts confidence scores using content-free inputs [Zhao et al., 2021].

However, a deeper problem underlies these isolated evaluations. Each method has been evaluated on different benchmarks with different sample counts and different models. Semantic entropy reports AUROC on TruthfulQA using specific NLI models; SelfCheckGPT reports on WikiBio using BERTScore. No study compares these methods head-to-head on the same benchmarks under matched computational budgets. This leaves practitioners unable to make informed choices—published results are incomparable, and method selection lacks principled guidance.

This gap exists because method papers optimize for demonstrating novelty, not for establishing fair comparison infrastructure. Each paper naturally focuses on conditions favorable to its proposed approach. The consequence: practitioners deploying hallucination detection in production systems have no way to predict which method will work for their specific benchmark or task.

**Key Insight.** Our pilot study reveals that hallucination detection method effectiveness is benchmark-sensitive in ways not previously reported. Under identical conditions (N=10 samples, same model, same temperature), semantic entropy achieved AUROC 0.551 on HaluEval but only 0.289 on TruthfulQA—the latter worse than random, with uncertainty scores *inverted* relative to ground truth labels. Self-consistency performed near random on both datasets. This suggests that benchmark design fundamentally affects method evaluation, and results from one benchmark may not transfer to another.

Building on this finding, we make the following contributions:

1. **Matched-Budget Evaluation Framework.** We establish a pilot comparison protocol that tests semantic entropy and self-consistency under identical computational budgets (same sample count, model, and temperature) across multiple benchmarks, enabling direct performance comparison.

2. **Benchmark Sensitivity Finding.** We provide empirical evidence that detection method performance varies dramatically across benchmarks—semantic entropy shows marginal signal on HaluEval but inverted results on TruthfulQA—suggesting benchmark-method alignment as a critical evaluation consideration.

3. **Methodological Recommendations.** Based on our observations, we identify labeling methodology and benchmark design as potential sources of evaluation inconsistency, providing directions for more rigorous future comparisons.

We organize the paper as follows. Section 2 surveys related work in hallucination detection and uncertainty quantification. Section 3 describes our matched-budget evaluation methodology. Section 4 details our experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
