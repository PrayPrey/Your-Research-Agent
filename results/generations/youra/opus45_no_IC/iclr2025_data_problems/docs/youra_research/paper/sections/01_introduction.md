# Introduction

Large language models trained on massive web corpora achieve impressive benchmark scores, but how much of this performance reflects genuine capability versus memorization of test data encountered during training? While n-gram contamination in training corpora has been extensively documented—with studies finding 8-18% overlap between common corpora and evaluation benchmarks [Yang et al., 2023]—no prior work has quantified how this contamination translates to benchmark score inflation.

This gap is consequential. Benchmark scores guide model selection, research direction, and deployment decisions across the field. If contamination inflates scores unpredictably, the entire evaluation paradigm becomes compromised. A model appearing 5% better on MMLU may simply have encountered more test questions during training, not developed superior reasoning capabilities.

## The Problem at Three Levels

**Surface problem.** Test set contamination exists in LLM training corpora. Prior work has established this through n-gram matching [Brown et al., 2020] and demonstrated that 8-18% of benchmark content appears verbatim in common pretraining corpora [Yang et al., 2023].

**Deeper problem.** Existing detection methods identify contamination but do not quantify its performance impact. The field has developed sophisticated tools for contamination detection—13-gram overlap analysis, membership inference attacks, output distribution analysis—yet the question of "how much does contamination matter?" remains unanswered. We know contamination exists; we do not know how much it inflates scores.

**The gap.** No quantitative model maps contamination levels to score inflation. Constructing such a model requires analyzing checkpoints at different training stages with varying contamination exposure—most studies examine only final models, missing the opportunity to observe contamination effects accumulate.

## Our Key Insight

Model checkpoints during training provide a natural contamination gradient, enabling correlation analysis without requiring contamination-free baseline models. By comparing checkpoints at different training stages, we observe varying levels of cumulative benchmark exposure as models progress through the training corpus. Early checkpoints have seen less training data, thus less benchmark-overlapping content, while later checkpoints have encountered more. This checkpoint-gradient methodology bypasses the fundamental obstacle that no truly "clean" baseline models exist—all large-scale pretraining corpora contain some benchmark content.

We isolate contamination effects from legitimate capability gains through capability detrending: regressing benchmark scores against WikiText-103 perplexity (a contamination-independent capability measure) and analyzing the residuals. Positive residuals indicate scores higher than capability would predict—potential contamination inflation.

## Contributions

Building on this insight, we present the first quantitative evidence for contamination-inflation correlation in language model benchmarks:

1. **Checkpoint-gradient methodology.** We demonstrate that model checkpoints across training provide a natural experiment for studying contamination-performance relationships, enabling correlation analysis without clean baseline models.

2. **Quantitative correlation.** We establish that contamination-inflation correlation exists at moderate strength (Spearman r ≈ 0.3, p < 0.01) across Pythia model checkpoints, showing that contamination impact is measurable, not merely detectable.

3. **N-gram overlap validation.** We confirm that 13-gram contamination is detectable in standard benchmarks (up to 17.4% individual item overlap in MMLU), validating the contamination measurement methodology.

4. **Capability detrending framework.** We introduce a principled approach for separating capability gains from contamination inflation using out-of-distribution perplexity regression.

Our findings suggest that contamination-aware benchmark evaluation is both necessary and feasible. The correlation we observe, while moderate, demonstrates that contamination effects are systematic enough to model—opening possibilities for contamination-adjusted benchmark scores.

We organize the paper as follows: Section 2 positions our work against prior contamination detection methods. Section 3 details the checkpoint-gradient methodology and capability detrending. Section 4 describes our experimental setup. Section 5 presents correlation results and overlap measurements. Section 6 discusses implications and limitations. Section 7 concludes with directions for contamination-aware evaluation.
