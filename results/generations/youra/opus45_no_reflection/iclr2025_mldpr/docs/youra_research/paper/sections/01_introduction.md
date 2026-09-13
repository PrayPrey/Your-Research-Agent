# Introduction

The rise of foundation models didn't just change what AI can do—it transformed how we measure progress. In April 2019 and March 2021, the ML benchmark ecosystem underwent two statistically significant structural breaks, coinciding with the emergence of transformative models like GPT-3 and ViT. These breaks mark a phase transition in how the research community evaluates AI systems, yet no prior work has quantitatively characterized this shift.

Understanding benchmark dynamics matters because benchmark choice shapes what problems researchers pursue. When 26.5% of researcher attention flows toward emergent-capability benchmarks like MMLU, BIG-Bench, and HumanEval—up from just 7.5% before 2021—the entire field's trajectory shifts. Without understanding these dynamics, we cannot distinguish genuine AI progress from benchmark artifact.

## The Problem of Static Analysis

Prior work has documented benchmark concentration. Koch et al. (2021) found Gini coefficients of 0.6-0.7 for 2015-2020, demonstrating that research concentrates on fewer datasets over time, with elite institutions dominating dataset creation. However, this analysis provides only static snapshots ending at 2020—precisely when foundation models began reshaping the landscape.

The deeper problem is that foundation models may have caused a *structural break* in benchmark dynamics, fundamentally altering how concentration evolves. Yet no quantitative evidence exists for this claim. The gap arises because detecting structural breaks requires time-series methods (change-point detection, trend analysis) rather than periodic snapshots. This methodological mismatch has left a critical question unanswered: did foundation models cause a measurable phase transition in benchmark usage patterns?

## Our Key Insight

We treat benchmark usage as a dynamic system that can exhibit phase transitions—sudden shifts in behavior analogous to water freezing or markets crashing. Applying PELT change-point detection to 84 months of Papers With Code data (2018-2024), we identify two structural breaks with a BIC improvement of 17.13 over the monotonic-trend null hypothesis.

The mechanism is not what we initially expected. We hypothesized that foundation models would fragment previously unified modality dynamics (CV and NLP benchmarks moving in opposite directions). Instead, we discovered that modalities were *never* unified—the pre-2020 CV-NLP Gini correlation was -0.13, not the >0.6 we assumed. Foundation models restructured the ecosystem through attention reallocation, not fragmentation: emergent benchmarks attracted 19% more researcher attention while traditional benchmarks (ImageNet, CIFAR) persisted with reduced dominance.

## Contributions

Building on this insight, we make the following contributions:

1. **First quantitative evidence of phase transition in benchmark dynamics.** Using PELT change-point detection, we identify two structural breaks (April 2019, March 2021) with BIC improvement of 17.13 over monotonic trend, providing the first statistical evidence that foundation model emergence coincided with measurable ecosystem restructuring.

2. **A complete mechanism verification chain.** We test five causal steps from foundation model emergence through benchmark ecosystem restructuring, validating four of five hypotheses. The fifth (modality divergence) was refuted, yielding the unexpected finding that modality dynamics were always independent.

3. **Quantified attention shift from traditional to emergent benchmarks.** We document that emergent-capability benchmark share increased from 7.53% to 26.54% post-2021 (χ²=1025, p<10⁻²²⁴), while traditional benchmarks persisted with 47,068 papers but reduced relative dominance (11.7% share).

The paper proceeds as follows. Section 2 reviews related work on benchmark concentration and meta-science of ML. Section 3 describes our methodology, including PELT-based change-point detection and mechanism verification design. Section 4 presents experimental setup, and Section 5 reports results across six sub-hypotheses. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
