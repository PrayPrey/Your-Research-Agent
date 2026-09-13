# Introduction

Quality filtering—the foundation of modern LLM data curation—systematically amplifies benchmark contamination rather than reducing it. This counterintuitive finding challenges the widespread assumption that filtering for "high-quality" training data uniformly improves model capabilities. We demonstrate that perplexity-based filtering, one of the most commonly deployed curation strategies, preferentially retains benchmark-overlapping content, creating models whose performance causally depends on contaminated training examples.

The consequences are significant. Removing just 1-5% of high-contamination-contribution examples causes nearly double the accuracy degradation (1.97×) compared to random removal. This means a substantial portion of benchmark performance may reflect memorization of evaluation content rather than genuine language understanding. Without methods to detect and quantify this phenomenon, practitioners cannot distinguish authentic capabilities from inflated scores.

## The Problem of Curation-Contamination Coupling

Test data contamination—the presence of benchmark questions or answers in training corpora—is a recognized threat to reliable LLM evaluation. Prior work has developed sophisticated detection methods including n-gram overlap analysis, membership inference attacks, and output distribution comparisons. Separately, the data curation community has established that filtering strategies profoundly affect downstream performance, with perplexity-based selection emerging as a preferred approach in large-scale training pipelines.

What remains unexplored is the *coupling* between these domains: how do specific curation decisions affect contamination rates? We observe that filtering mechanisms designed to select "high-quality" text inadvertently introduce systematic bias. Perplexity-based filtering favors documents with low perplexity—structured, predictable text that scores well against reference language models trained on Wikipedia. Yet benchmark content (educational text, Q&A forums, multiple-choice questions) exhibits precisely these low-perplexity characteristics. The filter does not merely retain contaminated examples proportionally; it actively concentrates them.

This coupling creates a deeper challenge: attribution. Even when contamination is detected, we lack methods to quantify how much benchmark performance derives from contaminated versus legitimate training examples. Without attribution, we cannot determine whether removing contaminated data would improve evaluation integrity at acceptable cost to model capabilities.

## Key Insight: Connecting Attribution to Contamination

Our central insight is that data attribution methods—originally designed to identify influential training examples—can bridge contamination detection and curation analysis. By combining contamination detection (which identifies *which* examples overlap with benchmarks) with attribution methods (which measure *how much* each example contributes to benchmark performance), we can quantify the contamination contribution ratio (CCR): the fraction of benchmark-specific attribution mass originating from contaminated examples.

This connection enables three advances:
1. **Measurement**: CCR quantifies how curation strategies differentially amplify contamination
2. **Causation**: Targeted removal experiments verify whether high-CCR examples are genuinely necessary for benchmark performance
3. **Comparison**: The Amplification Index (AI) measures differential contamination effects across strategies

## Contributions

We present a systematic study connecting data curation, contamination detection, and attribution methods. Our contributions are:

First, we introduce **Contamination Contribution Ratio (CCR)**, a novel metric combining n-gram contamination detection with TRAK attribution to quantify benchmark-specific influence from contaminated training examples. We validate CCR through synthetic injection experiments, demonstrating linear scaling with contamination rate (R² = 0.9998).

Second, we establish that **perplexity filtering amplifies contamination** relative to random sampling. In controlled experiments with matched corpora, CCR increases by 0.1594 under perplexity filtering (p < 0.0001, bootstrap test with 1000 resamples), representing a 16% increase in contamination-attributed benchmark performance.

Third, we demonstrate **causal necessity** of high-CCR examples through removal interventions. Removing the top 1-5% of high-CCR examples causes 1.97× greater accuracy degradation than random removal (95% CI: [1.53, 2.34]), proving that contaminated examples drive benchmark performance beyond correlation.

Fourth, we introduce **Influence Fragility Ratio (IFR)**, characterizing the structural difference between contaminated and non-contaminated high-influence examples. Contaminated examples exhibit 4.1× higher IFR, indicating they cannot be easily substituted by other training content.

These findings have immediate implications for evaluation integrity: benchmark scores from perplexity-filtered training may overestimate genuine model capabilities by a quantifiable margin.
