# Experimental Setup

We design experiments to answer five research questions, each mapping to a sub-hypothesis in our mechanism verification chain.

## Research Questions

**RQ1 (h-e1):** Does the aggregate Gini coefficient time series exhibit statistically significant structural breaks within the 2019-2022 window?

**RQ2 (h-m1):** Did foundation model papers (GPT-3, ViT, BERT variants) achieve exceptional citation impact relative to the field?

**RQ3 (h-m2):** Did emergent-capability benchmark creation accelerate post-2020?

**RQ4 (h-m3):** Did researcher attention shift from traditional to emergent benchmarks post-2021?

**RQ5 (h-m5):** Did modality-specific Gini trajectories diverge after foundation model emergence?

## Dataset

We use Papers With Code (PWC) benchmark data spanning January 2018 through December 2024 (84 months). PWC provides task-dataset-metric triplets linking papers to their benchmark evaluations.

| Statistic | Value |
|-----------|-------|
| Time range | 2018-01 to 2024-12 |
| Total months | 84 |
| Aggregation | Monthly |
| Primary metric | Gini coefficient |

**Rationale:** PWC is the standard source for benchmark usage analysis (used by Koch et al., 2021), provides the temporal granularity needed for change-point detection, and covers the foundation model emergence period.

## Baselines

We compare against two baselines:

**Monotonic Trend (Null Hypothesis):** A single monotonic trend over the full 2018-2024 period. This baseline represents the claim that benchmark dynamics followed a consistent trajectory without structural breaks.

**Koch et al. (2021) Methodology:** We replicate their Gini coefficient approach on PWC data, enabling direct comparison. Their reported Gini of 0.6-0.7 for 2015-2020 serves as the baseline concentration level.

## Hypothesis-Specific Designs

### h-e1: Phase Transition Signal

- **Method:** PELT change-point detection on monthly Gini series
- **Model:** RBF kernel, minimum segment size 3
- **Success criterion:** Segmented model BIC < monotonic model BIC; change points within 2019-2022
- **Falsification:** No change points detected, or single monotonic trend fits better

### h-m1: Foundation Model Emergence

- **Method:** Citation z-score analysis for five foundation papers
- **Papers:** GPT-3 (Brown et al., 2020), ViT (Dosovitskiy et al., 2020), BERT (Devlin et al., 2019), T5 (Raffel et al., 2020), CLIP (Radford et al., 2021)
- **Success criterion:** ≥3/5 papers exceed 2σ above field mean
- **Falsification:** <3/5 papers exceed threshold

### h-m2: Emergent Benchmark Creation

- **Method:** Temporal analysis of emergent-capability benchmark introduction dates
- **Emergent benchmarks:** MMLU, BIG-Bench, HumanEval, and similar reasoning/capability benchmarks
- **Success criterion:** >80% of emergent benchmarks created post-2020
- **Falsification:** ≤80% post-2020, or no acceleration observed

### h-m3: Researcher Attention Shift

- **Method:** Chi-square test comparing pre-2021 vs post-2021 paper distributions
- **Metric:** Proportion of papers evaluating on emergent vs traditional benchmarks
- **Success criterion:** Significant increase in emergent benchmark share (p<0.05)
- **Falsification:** No significant change or decrease in emergent share

### h-m4: Traditional Benchmark Persistence

- **Method:** Share and absolute count analysis for ImageNet, CIFAR, and similar traditional benchmarks
- **Success criterion:** Share <50% (reduced dominance) AND absolute papers >10,000 (persistence)
- **Falsification:** Share ≥50% (maintained dominance) OR papers <10,000 (decline)

### h-m5: Modality Divergence

- **Method:** Fisher z-test comparing pre-2020 vs post-2021 CV-NLP Gini correlations
- **Success criterion:** Pre-2020 r > 0.6 drops to post-2021 r < 0.4
- **Falsification:** Correlation remains above 0.5 in both periods

## Evaluation Metrics

| Metric | Definition | Usage |
|--------|------------|-------|
| BIC | Bayesian Information Criterion | Model comparison (h-e1) |
| Z-score | (citation - mean) / std | Impact assessment (h-m1) |
| Ratio | post-2020 count / total count | Creation timing (h-m2) |
| χ² | Chi-square statistic | Share comparison (h-m3, h-m4) |
| Fisher z | Correlation comparison | Divergence test (h-m5) |

Statistical significance is evaluated at α=0.05 throughout.

## Implementation Details

All experiments were implemented in Python 3.10+. Key libraries:
- `ruptures` 1.1.8 for PELT change-point detection
- `scipy` 1.11+ for statistical tests
- `pandas` for data manipulation
- `matplotlib` for visualization

Experiments were run on a single CPU; no GPU required. Total compute time was approximately 30 minutes for all hypotheses.
