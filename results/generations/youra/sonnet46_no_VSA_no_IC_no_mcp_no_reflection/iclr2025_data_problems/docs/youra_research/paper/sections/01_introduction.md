# Introduction

We set out to measure whether better pre-training data produces more generalizable language
models — and found the opposite. OLMo-7B, trained on Dolma, one of the most carefully
curated pre-training corpora to date with multi-stage quality filtering and explicit
inclusion of academic content, achieves a lower knowledge-to-commonsense generalization
balance ratio than Pythia-6.9B, trained on The Pile with minimal curation. More
strikingly, both models converge to *identical* commonsense reasoning scores, suggesting
that web-sourced commonsense knowledge saturates at similar levels regardless of curation
quality at this training scale.

The intuition that better-curated data produces better-generalized models drives enormous
resource investment across industry and academia. Dolma's curators deduplicated, filtered
for quality, and explicitly included academic sources (S2ORC, Wikipedia) precisely because
these choices were expected to yield models with stronger knowledge acquisition and more
robust generalization. Yet at approximately 300 billion training tokens — a scale at which
both OLMo-7B and Pythia-6.9B have been released with documented checkpoints — the
model trained on the less-curated corpus achieves a higher MMLU/HellaSwag generalization
balance ratio (Pythia: 0.565 vs OLMo: 0.538; difference = −0.0265, 95% CI [−0.045, −0.007],
Cohen's d = −2.732).

The question of whether better data produces better-generalized models is not merely academic.
Curation pipelines represent a significant fraction of pre-training cost; decisions about
what to filter, how aggressively to deduplicate, and which domains to include are made
under the assumption that these choices improve not just average benchmark performance but
the model's ability to generalize across task types. Without controlled tests of this
assumption at matched training scales, practitioners cannot know whether their curation
investments yield the generalization benefits they are designed to produce.

**The deeper problem** is methodological: prior work comparing curated and uncurated corpora
(e.g., RefinedWeb vs. The Pile on Falcon [Penedo et al., 2023]; Pythia-dedup vs. Pythia
[Biderman et al., 2023]) has consistently confounded corpus quality with training duration,
model architecture, or both. When models from different architecture families are compared
at their respective full-training checkpoints, the differences observed cannot be attributed
to data quality alone. What has been missing is a simple, targeted test: holding training
scale constant, does a measurably higher-quality corpus produce a measurably higher
generalization balance?

**The gap** our work addresses is precisely this: no prior study has evaluated MMLU/HellaSwag
generalization balance ratios for an architecture-paired comparison at matched training
token counts. The Pythia and OLMo model suites provide natural variation in documented
data recipes with publicly released intermediate checkpoints — an opportunity that, to
our knowledge, has not previously been exploited to test the corpus-quality → generalization
balance hypothesis under controlled scale conditions.

**Our finding** reveals not just a null result but a structural insight about the evaluation
metric itself. At ~300B training tokens, both 6-8B parameter models achieve exactly the
same HellaSwag 0-shot accuracy (0.4580). When the denominator of the generalization balance
ratio is a constant, the ratio collapses into a noisy proxy for MMLU alone — and MMLU
differences between architecturally distinct models cannot be attributed to corpus quality
without architecture-matched controls. The metric's discriminative power fails precisely
because the commonsense reasoning task saturates at this training scale.

This paper makes the following contributions:

1. **Matched-scale empirical evaluation.** We provide, to our knowledge, the first
   evaluation of MMLU/HellaSwag generalization balance ratios comparing Pythia-6.9B
   (The Pile, step143000 ≈ 299.9B tokens) and OLMo-7B (Dolma, step68000 ≈ 301B tokens)
   at controlled matched training scale. We find that the corpus-quality → generalization-
   balance prediction is directly refuted: Pythia achieves significantly higher ratio
   (p=0.996 one-sided, d=−2.732).

2. **Metric sensitivity analysis.** We demonstrate that HellaSwag 0-shot commonsense
   performance converges to identical values for both models at ~300B tokens, revealing
   that the MMLU/HellaSwag ratio is not a reliable discriminator of corpus curation quality
   at this training scale in a cross-architecture comparison.

3. **Methodological characterization.** We characterize the conditions under which
   cross-architecture, single-checkpoint comparisons fail to support causal corpus-quality
   claims: when a ratio metric's denominator task saturates, the ratio loses its intended
   discriminative property. We propose concrete requirements — architecture-matched pairs
   or temporal trajectory analysis — for future studies that aim to isolate corpus quality
   effects.

4. **Scope-qualified null result.** Our negative finding is precisely scoped: it applies to
   ~300B training tokens, the GPT-NeoX/LLaMA-style architecture pairing, and the
   MMLU/HellaSwag ratio metric. It does not rule out corpus quality effects at other scales,
   with architecture-matched designs, or using different generalization metrics.

The remainder of this paper is organized as follows: Section 2 surveys related work on
corpus curation, generalization evaluation, and data attribution. Section 3 describes our
methodology and study design. Section 4 presents experimental setup and evaluation protocol.
Section 5 reports results. Section 6 discusses competing explanations, limitations, and
implications for metric design. Section 7 concludes with future directions.
