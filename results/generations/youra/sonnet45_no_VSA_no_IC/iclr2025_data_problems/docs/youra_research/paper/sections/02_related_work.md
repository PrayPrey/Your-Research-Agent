# Related Work

Our work builds on established quality and diversity metrics while challenging order-invariance assumptions in data mixing literature. We organize related work by three themes: quality-based curation, diversity-based curation, and mixture optimization.

## Quality-Based Data Curation

Quality filtering aims to remove low-value documents that slow learning. **V-Information** [arXiv:2507.00038] provides a principled approach using pointwise information content, demonstrating that quality-based reduction maintains performance at small scale (<1M tokens). However, V-Information's evaluation focused on reduction rates, not scale-dependent trajectories. We extend this work by quantifying how quality filtering effectiveness decreases with scale (slope −2.62pp/log-scale, p=0.008).

**DATAMASK** (ByteDance 2025) made the key qualitative observation that quality-only metrics show diminishing returns while diversity metrics remain effective across scales. This observation motivated our hypothesis but lacked quantitative rigor—no regression analysis, no significance tests, no ordering experiments. Our contribution is to measure these trajectories as continuous functions and test compositional effects.

Other quality-focused approaches include perplexity-based filtering and classifier-based scoring, but these methods saturate similarly at large scale and do not address sequential ordering.

## Diversity-Based Data Curation

Diversity sampling preserves long-tail coverage that quality filtering may exclude. **Feature Activation Coverage (FAC)** [arXiv:2602.10388] demonstrated ρ=0.90 correlation with downstream performance on large-scale datasets, validating feature-based diversity as a robust metric. FAC-Synthesis showed effectiveness across domains but did not analyze scale-dependent trends. We extend FAC by testing diversity-only improvement trajectories and showing persistence (+2.5pp/log-scale slope).

**DsDm and DataComp** explored diversity through deduplication and cross-domain sampling, but these works focused on corpus-level decisions rather than sequential interaction with quality filters. Our ordering experiments (QD vs DQ) reveal that diversity sampling effectiveness depends on whether it operates on quality-filtered or raw noisy data.

## Data Mixing and Composition

**Data Mixing Laws** [arXiv:2403.16952] established that small proxy models can predict large-scale mixture performance, validating our use of GPT-2 Small (124M) for experiments. However, Mixing Laws assume data sources mix independently with additive contributions—an order-invariance assumption we challenge. Our QD vs DQ experiments demonstrate compositional interactions where sequential ordering produces Cohen's d=0.76–2.48 effect sizes.

**RegMix** [arXiv:2407.01492] optimizes mixture proportions via regression but similarly assumes order-invariant additive effects. RegMix focuses on "how much of each source" while we address "in what order to apply curation steps." Our findings suggest RegMix could improve by incorporating sequential ordering: apply quality filters before diversity sampling within each source, then optimize proportions.

**FastMix** [arXiv CITATION_NEEDED] uses gradient descent for mixture optimization but inherits the same order-invariance limitation.

## Contamination Detection

Test set contamination threatens benchmark reliability. **ConStat** and **DyePack** [CITATION_NEEDED] provide detection methods, but these are not integrated into curation pipeline design. We use standard benchmarks (MMLU, BEIR, GSM8K) and acknowledge contamination risk as a limitation, deferring detection to future work.

## Positioning of Our Work

Prior work established individual metrics (V-Info for quality, FAC for diversity) and mixture proportion optimization (RegMix, Mixing Laws). We extend this foundation in three ways: (1) quantifying saturation and persistence as scale-dependent trajectories, not binary observations; (2) demonstrating compositional ordering effects that contradict order-invariance assumptions; (3) providing prescriptive guidance (quality-first universality) grounded in real training experiments. Our quality-gated diversity framework—diversity is only effective on quality-filtered subsets—offers a new theoretical lens for understanding multi-stage curation.
