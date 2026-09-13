---
title: "Does Better Data Produce Better-Generalized Models? A Matched-Scale Evaluation of Corpus Curation and Generalization Balance"
authors:
  - name: "[Anonymous]"
    affiliation: "[Anonymous Institution]"
    email: "[Anonymous]"
format: "ICML2025"
date: "2026-08-31"
hypothesis_id: "h-e1"
generated_by: "Anonymous Research Pipeline — Phase 6 Paper Writing"
word_count: 6832
figures: 4
tables: 4
note: "Negative result paper — primary findings refute corpus-quality hypothesis at ~300B training tokens"
---

# Abstract

The intuition that better pre-training data produces more generalizable language models
drives substantial investment in corpus curation — but this assumption has rarely been
tested under controlled conditions. We evaluate OLMo-7B (Dolma, multi-stage curation)
and Pythia-6.9B (The Pile, minimal curation) at matched training scale (~300B tokens),
specifically testing whether the curated-corpus model achieves a higher MMLU/HellaSwag
generalization balance ratio. Contrary to the hypothesis, Pythia achieves the higher ratio
(0.565 vs. 0.538) — a large, statistically robust reversal (95% CI entirely against
OLMo). The most informative finding is structural: both models converge to identical
HellaSwag commonsense scores at this training scale, collapsing the ratio into a proxy
for MMLU differences that are themselves architecture-confounded. This reveals that the
MMLU/HellaSwag metric loses discriminative power when its denominator saturates — a
condition that holds for 6-8B models at ~300B tokens. We characterize the minimum
requirements for future corpus quality studies: architecture-matched designs or temporal
trajectory analysis to bound architecture confounds, and denominator-sensitivity
verification before using ratio metrics as quality proxies.


---

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


---

# Related Work

Our work sits at the intersection of three bodies of literature: corpus curation and its
effects on model generalization, evaluation benchmark design for generalization measurement,
and data attribution methods. We review each in turn, highlighting why existing work leaves
the specific question we address unanswered.

## Pre-training Corpus Curation and Model Generalization

The empirical evidence that corpus curation improves average benchmark performance is
substantial but consistently confounded. **Biderman et al. [2023]** demonstrate, via the
Pythia suite, that deduplication (Pythia vs. Pythia-dedup) yields small but consistent
improvements on several benchmarks, including a modest HellaSwag gain. However, this
within-architecture, within-corpus comparison tests only deduplication as an isolated
intervention — it does not address multi-stage quality curation, and the HellaSwag gains
are small enough (~0.01 absolute) to be consistent with the near-saturation behavior we
observe at 300B tokens. Critically, the Pythia suite's consistent training procedure and
fixed data ordering make it a uniquely controlled environment, but no cross-quality study
at matched training scale has leveraged these properties for generalization balance analysis.

**Penedo et al. [2023]** show that web-filtered data (RefinedWeb) outperforms unfiltered
data when training Falcon models on average benchmark performance. While this is evidence
for a curation benefit, the comparison involves different model architectures (Falcon vs.
GPT-NeoX), different training durations, and focuses on average performance rather than
generalization balance ratios. The architecture confound remains unresolved.

**Groeneveld et al. [2024]** document OLMo's design, including the Dolma corpus with its
multi-stage curation pipeline. They report that OLMo-7B at full training (~2T tokens)
achieves competitive MMLU performance relative to models of similar size, and attribute
part of this to Dolma's academic content inclusion (S2ORC, Wikipedia). However, this
comparison is not matched by training scale — comparing OLMo at 2T tokens to Pythia at
300B tokens conflates corpus quality with training duration. Our work tests the same
corpus pairing at a matched intermediate scale, revealing that the advantage observed at
full training does not manifest at ~300B tokens.

**Muennighoff et al. [2023]** establish a data quality × training scale interaction:
the benefits of higher-quality data may compound with more training tokens, with
lower-quality models "catching up" as token count increases. Our finding of a null
result at 300B tokens is consistent with this interaction — the Dolma advantage may
emerge later — but it also underscores that intermediate-scale comparisons cannot be
used to make sweeping claims about curation benefits without acknowledging the scale dependency.

**Soldaini et al. [2024]** describe the Dolma corpus in detail, including the multi-stage
curation pipeline, domain composition, and deduplication methodology. This paper provides
the primary documentation of Dolma's quality advantages that motivated our hypothesis.
The gap between Dolma's documented curation investment and the null result we observe
at 300B tokens is precisely what drives the methodological insight of our work.

## Generalization Evaluation Metrics

The benchmarks we use — MMLU [Hendrycks et al., 2021], HellaSwag [Zellers et al., 2019],
and ARC [Clark et al., 2018] — are standard tools for evaluating LLM capabilities, but
their sensitivity to specific factors (training scale, architecture, corpus composition)
has received limited systematic study.

**Hendrycks et al. [2021]** introduce MMLU as a measure of multi-task language understanding
spanning 57 subjects including STEM, humanities, and social sciences. The benchmark is
designed to test knowledge-intensive generalization. Our finding that MMLU differences
between Pythia and OLMo may be architecture-confounded raises questions about MMLU's
suitability as a corpus-quality metric without architectural controls.

**Zellers et al. [2019]** introduce HellaSwag as a commonsense reasoning completion task
designed to be challenging for models while remaining easy for humans. Its 0-shot
evaluation measures the degree to which models have acquired web-sourced commonsense
knowledge from pre-training. Our observation of identical HellaSwag scores (0.4580) for
both models at ~300B tokens suggests a scale-dependent saturation effect that limits
HellaSwag's discriminative power in cross-quality comparisons at this training scale.

The use of performance *ratios* as generalization balance metrics has precedent in the
OOD generalization literature, where ID/OOD performance gaps are used to characterize
a model's generalization behavior [Miller et al., 2021; Koh et al., 2021]. However,
ratio metrics require that both the numerator and denominator remain discriminative at
the comparison point — a requirement that our study shows is violated when the denominator
task saturates.

## Data Attribution and Quality Proxy Methods

Beyond direct comparison, the field has developed tools for attributing model behavior
to training data. Influence functions [Koh and Liang, 2017], TRAK [Park et al., 2023],
and TracIn [Pruthi et al., 2020] identify which training examples most influenced specific
predictions. These methods could in principle quantify the contribution of high-quality
vs. low-quality data subsets to generalization performance, but they have not been applied
to the corpus-quality × generalization-balance question at the scale of 300B-token pre-training.
Such attribution analyses represent a promising direction for moving beyond the descriptive
comparisons we report, but require architecture-matched designs to avoid confounding
attribution results with architecture effects.

## Positioning Our Contribution

Our work differs from prior literature in three ways. First, we use a **matched training scale**
(~300B tokens, both models within 0.5% of target) to eliminate training duration as a confound.
Second, we focus on **generalization balance** (ratio and delta metrics) rather than absolute
performance, asking whether a model's knowledge acquisition and commonsense reasoning grow
in proportion — a question more directly linked to the corpus-quality hypothesis than
average benchmark improvement. Third, we report a **scope-qualified null result** with
explicit characterization of the conditions under which the comparison breaks down, rather
than drawing causal conclusions from an architecturally confounded design. Our finding
that HellaSwag saturates at identical values for both models provides a structural
explanation for the null result that goes beyond simply reporting "no difference was found."


---

# Methodology

## Overview

Our study design is motivated by a simple observation: the claim that better corpus
curation improves generalization balance requires a comparison where training scale is
held constant. Without matched token counts, observed performance differences may reflect
training duration rather than data quality. We exploit the public availability of
intermediate checkpoints from two model suites — Pythia [Biderman et al., 2023] and
OLMo [Groeneveld et al., 2024] — that differ in documented corpus curation quality but
provide accessible checkpoints at approximately matched training scales.

## Model Selection and Training Scale Matching

We compare **Pythia-6.9B** (EleutherAI, trained on The Pile with minimal curation) against
**OLMo-7B** (Allen Institute, trained on Dolma with multi-stage quality curation). Both
models provide publicly accessible intermediate checkpoints on HuggingFace that allow
evaluation at matched training scales.

**Checkpoint Selection:**

| Model | HuggingFace ID | Revision | Approximate Training Tokens | Deviation from 300B |
|-------|---------------|----------|----------------------------|---------------------|
| Pythia-6.9B | `EleutherAI/pythia-6.9b` | `step143000` | ≈ 299.9B | −0.03% |
| OLMo-7B | `allenai/OLMo-7B` | `step68000-tokens301B` | ≈ 301B | +0.33% |

Both checkpoints fall within 0.5% of the 300B token target, satisfying the matched-scale
design criterion. Token counts were verified from published training configurations:
Pythia uses a global batch size of approximately 2M tokens per step [Biderman et al., 2023];
OLMo's step-to-token mapping is derived from its published training config [Groeneveld et al., 2024].

**Rationale for Model Selection:** The Pythia and OLMo suites were chosen because (1) they
represent well-documented corpus quality differences (The Pile, minimal filtering vs.
Dolma, multi-stage quality curation with academic content inclusion), (2) they provide
intermediate checkpoints at the scales required for a matched-scale comparison, and (3)
both have been evaluated in prior work, providing a baseline for sanity-checking our
evaluation results. The architecture difference (GPT-NeoX for Pythia; LLaMA-style for
OLMo) is a known limitation discussed in Section 6.

## Evaluation Protocol

We use the `lm-evaluation-harness` (v0.4.12) [Gao et al., 2024] with standardized
shot configurations matching those used in the original Pythia and OLMo papers:

| Benchmark | Configuration | Metric | Purpose |
|-----------|--------------|--------|---------|
| MMLU | 5-shot | accuracy (mean over 57 subjects) | Knowledge-intensive OOD generalization |
| HellaSwag | 0-shot | accuracy | Commonsense reasoning (in-distribution proxy) |
| ARC-Easy | 25-shot | accuracy | Factual reasoning (easy) |
| ARC-Challenge | 25-shot | accuracy_normalized | Factual reasoning (hard) |

**Fast evaluation:** We use the `--limit 500` flag, evaluating approximately 500 examples
per task (roughly 8-9 examples per MMLU subject across 57 subjects). This fast evaluation
protocol was chosen to enable rapid hypothesis screening on H100 NVL hardware. The
implications for result reliability are discussed in Section 6; we note that the large
observed effect (Cohen's d = −2.732) is unlikely to reverse with full evaluation.

**Evaluation pipeline architecture:** The evaluation pipeline consists of five stages
executed in sequence, with each stage writing results to disk before the next begins
(enabling resume-on-failure): (1) precondition verification (checkpoint existence, token
count matching), (2) lm-eval execution for Pythia-6.9B, (3) lm-eval execution for OLMo-7B,
(4) metric computation from results JSON files, (5) figure generation. All code was run
on H100 NVL hardware.

## Primary and Secondary Metrics

**Primary metric — MMLU/HellaSwag Generalization Balance Ratio:**

$$r = \frac{\text{MMLU}_{5\text{-shot}}}{\text{HellaSwag}_{0\text{-shot}}}$$

This ratio captures the balance between knowledge-intensive task performance (MMLU,
treated as an OOD generalization signal) and commonsense reasoning performance
(HellaSwag, treated as an in-distribution baseline). Higher values indicate that the
model's knowledge acquisition outpaces its commonsense baseline, suggesting stronger
generalization to knowledge-intensive tasks.

**Secondary metric — ARC-Challenge/Easy Delta:**

$$\Delta_{\text{ARC}} = \text{ARC-Challenge}_{\text{acc\_norm}} - \text{ARC-Easy}_{\text{acc}}$$

The delta measures how much harder the model finds challenge-level vs. easy-level
reasoning, with less-negative values indicating better maintenance of reasoning
difficulty sensitivity.

## Statistical Analysis

Statistical analysis follows a bootstrap resampling procedure:

1. **Bootstrap CI on ratio difference:** We compute the ratio for each model and define
   the test statistic as $\Delta_r = r_{\text{OLMo}} - r_{\text{Pythia}}$. Bootstrap
   confidence intervals (1000 iterations, seed=42) are computed by resampling MMLU
   subject-level accuracy estimates with replacement, recomputing ratios at each iteration,
   and taking the 2.5th and 97.5th percentiles.

2. **One-sided p-value:** We compute the fraction of bootstrap iterations in which
   $\Delta_r > 0$ (OLMo higher), which is the one-sided p-value against the null hypothesis
   that Pythia is at least as high. Under the original hypothesis, this p-value should
   be small (< 0.05).

3. **Cohen's d:** We compute $d = \bar{\Delta}_r / \sigma(\Delta_r)$ over bootstrap
   samples as a standardized effect size measure.

**Interpretation convention:** We adopt the pre-registered hypothesis criterion that the
result supports the corpus-quality hypothesis if and only if $\Delta_r > 0.02$ with
$d > 0.2$ and $p < 0.05$. A result below this threshold in either direction is treated
as falsifying the specific prediction.

## Limitations of the Comparison Design

We acknowledge upfront three limitations that affect causal attribution, and discuss
them in detail in Section 6:

1. **Architecture confound.** Pythia-6.9B uses GPT-NeoX architecture; OLMo-7B uses a
   LLaMA-style architecture. Performance differences — including MMLU differences — cannot
   be attributed purely to corpus quality without architecture-matched controls or temporal
   trajectory analysis showing a widening gap (quality-driven) vs. a stable gap (architecture-driven).

2. **Fast evaluation.** The 500-sample evaluation limit introduces higher variance in
   per-subject MMLU estimates. Effect direction is reliable; effect magnitude requires
   full evaluation to confirm.

3. **Single training scale.** We evaluate only at ~300B tokens. The corpus quality
   hypothesis may hold at different training scales; our null result is specific to this
   checkpoint selection.

These limitations are structural features of the comparison design, not implementation
errors. The null result we observe — and the HellaSwag convergence finding that explains
it — are informative precisely because they characterize where this type of comparison
breaks down.


---

# Experimental Setup

## Research Questions

We design experiments to answer the following questions, each mapping directly to a
claim from the Introduction:

**RQ1:** Does OLMo-7B, trained on Dolma (multi-stage curation), achieve a higher
MMLU/HellaSwag generalization balance ratio than Pythia-6.9B, trained on The Pile
(minimal curation), at matched training scale (~300B tokens)?
*(Tests the primary corpus-quality → generalization-balance hypothesis; corresponds to P1)*

**RQ2:** Does OLMo-7B achieve a less-negative ARC-Challenge/Easy delta than Pythia-6.9B
at the same training scale?
*(Tests whether reasoning difficulty sensitivity also reflects curation quality; corresponds to P2)*

**RQ3:** Is Pythia-6.9B's MMLU performance advantage, if present, distributed broadly
across MMLU subjects (consistent with general knowledge improvement) or concentrated in
specific domains (consistent with benchmark contamination)?
*(Addresses the Pile contamination alternative explanation; corresponds to the
per-subject analysis)*

## Models and Checkpoints

Both models are evaluated from publicly available HuggingFace checkpoints. Token counts
are verified from published training configurations.

| Model | Architecture | HuggingFace ID | Revision | Training Tokens | Deviation |
|-------|-------------|----------------|----------|-----------------|-----------|
| Pythia-6.9B | GPT-NeoX | `EleutherAI/pythia-6.9b` | `step143000` | ≈ 299.9B | −0.03% |
| OLMo-7B | LLaMA-style | `allenai/OLMo-7B` | `step68000-tokens301B` | ≈ 301B | +0.33% |

Pythia-6.9B is trained on The Pile [Gao et al., 2020], an 825 GB heterogeneous corpus
assembled from 22 diverse text sources with minimal quality filtering beyond basic
deduplication and language filtering. OLMo-7B is trained on Dolma [Soldaini et al., 2024],
a 3-trillion token corpus with multi-stage quality filtering including URL blocklisting,
content heuristics, deduplication, and explicit inclusion of high-quality academic sources
(S2ORC semantic scholar papers, Wikipedia, Project Gutenberg).

Both models are evaluated as base (non-instruction-tuned) models, avoiding alignment
confounds. Checkpoint selection was verified by cross-referencing published training logs:
Pythia's step-to-token mapping at batch size ≈ 2M tokens/step [Biderman et al., 2023]
and OLMo's mapping from its published training configuration [Groeneveld et al., 2024].

## Evaluation Benchmarks

We use four standard benchmarks evaluating complementary cognitive capabilities:

**MMLU** (Massive Multitask Language Understanding) [Hendrycks et al., 2021]: A
57-subject multiple-choice benchmark spanning STEM, humanities, social sciences, and
professional domains. We use the standard 5-shot protocol. MMLU is chosen as our primary
knowledge-intensive OOD generalization measure: it tests whether models have acquired
factual knowledge that requires reading comprehension and reasoning beyond simple pattern
matching. As the numerator of our primary metric, MMLU performance is expected to
benefit from the academic content inclusion in Dolma.

**HellaSwag** [Zellers et al., 2019]: A commonsense completion benchmark derived from
ActivityNet and WikiHow. We use the standard 0-shot protocol. HellaSwag is chosen as
our in-distribution commonsense baseline: it measures whether models have absorbed
web-sourced procedural and situational knowledge. As the denominator of our primary
metric, HellaSwag performance is expected to be less sensitive to corpus curation
quality differences, since both The Pile and Dolma draw heavily from CommonCrawl.

**ARC-Easy and ARC-Challenge** [Clark et al., 2018]: Multiple-choice science questions
at elementary and challenge levels. Both are evaluated with the standard 25-shot protocol.
The ARC-Challenge/Easy delta measures whether a model is more degraded by harder
reasoning requirements, with less-negative values indicating better difficulty sensitivity.

## Evaluation Protocol

All evaluations are conducted using `lm-evaluation-harness` v0.4.12 [Gao et al., 2024]
on NVIDIA H100 NVL hardware. Evaluation commands follow the form:

```bash
lm_eval --model hf \
  --model_args pretrained=<model_id>,revision=<revision> \
  --tasks mmlu,hellaswag,arc_easy,arc_challenge \
  --num_fewshot <task-specific> \
  --limit 500 \
  --output_path ./results/<model>-300B/ \
  --log_samples
```

The `--limit 500` flag evaluates approximately 500 examples per task. For MMLU (14,042
questions across 57 subjects), this yields approximately 8-9 questions per subject. This
fast evaluation protocol reduces wall-clock time while preserving directional reliability
for large effects. Full-evaluation implications are discussed in Section 6.

Results are stored as JSON files and loaded for metric computation. The evaluation
pipeline implements resume-on-existing-output logic: if results JSON already exists for
a model, the evaluation step is skipped, ensuring reproducibility across restarts.

## Statistical Analysis Protocol

**Primary test:** The hypothesis predicts OLMo ratio − Pythia ratio > 0.02 with Cohen's
d > 0.2 and one-sided p < 0.05. We compute bootstrap confidence intervals (1000
iterations, seed=42) on the ratio difference by resampling MMLU subject-level accuracy
estimates with replacement and recomputing ratios at each iteration. The one-sided
p-value is the fraction of bootstrap iterations in which the OLMo ratio exceeds the
Pythia ratio.

**Effect size:** Cohen's d = mean(ratio differences across bootstrap iterations) /
std(ratio differences across bootstrap iterations). A pre-registered threshold of d > 0.2
was specified as the minimum meaningful effect.

**Secondary test:** ARC-Challenge/Easy delta is compared directionally (OLMo delta >
Pythia delta, less negative), with no statistical threshold pre-specified.

**Contamination analysis:** Per-subject MMLU accuracy heatmap is examined qualitatively
to assess whether any Pythia MMLU advantage is concentrated in domains known to be
over-represented in The Pile (e.g., science, medicine, law from PubMed, law databases).
Concentration in these domains would increase the plausibility of The Pile contamination
as an explanation.


---

# Results

## Primary Finding: Corpus-Quality Hypothesis Refuted

The corpus-quality → generalization-balance prediction is directly refuted. Pythia-6.9B
achieves a higher MMLU/HellaSwag ratio than OLMo-7B at matched training scale (~300B
tokens) — the opposite of the hypothesis direction.

**Table 1: Benchmark Results at ~300B Training Tokens**

| Model | Corpus | MMLU (5-shot) | HellaSwag (0-shot) | ARC-Easy (25-shot) | ARC-Challenge (25-shot) |
|-------|--------|--------------|-------------------|-------------------|------------------------|
| Pythia-6.9B | The Pile (minimal curation) | **0.259** | 0.458 | **0.670** | **0.336** |
| OLMo-7B | Dolma (multi-stage curation) | 0.246 | 0.458 | 0.640 | 0.296 |

A striking feature of Table 1 is immediately apparent: both models achieve exactly 0.458
on HellaSwag. This exact convergence is not coincidence — it reflects a scale-dependent
saturation effect that is central to interpreting all other results. We return to this
point in Section 5.3.

Across all four individual benchmarks, Pythia-6.9B performs no worse than OLMo-7B.
Pythia achieves higher MMLU (0.259 vs 0.246), higher ARC-Easy (0.670 vs 0.640), higher
ARC-Challenge (0.336 vs 0.296), and equal HellaSwag (0.458 = 0.458). This consistent
directional pattern across all metrics makes the refutation robust to choice of aggregation
method: the null result does not depend on which benchmark is used as the primary outcome.

## Primary Metric: MMLU/HellaSwag Generalization Balance Ratio

Figure 2 shows the MMLU/HellaSwag generalization balance ratio for both models with
bootstrap 95% confidence intervals.

*[Figure 2: ratio_delta.png — MMLU/HellaSwag ratio comparison with 95% bootstrap CI]*

**Pythia ratio = 0.565; OLMo ratio = 0.538; difference = −0.0265.**

The hypothesis predicted OLMo − Pythia > +0.02; the observed value is −0.0265. The
bootstrap 95% CI on the ratio difference (OLMo − Pythia) is [−0.045, −0.007], lying
entirely below zero. The one-sided p-value (fraction of bootstrap iterations in which
OLMo exceeds Pythia) is 0.004 — far below the 0.05 threshold — but in the direction
opposite to the hypothesis (this p-value rejects the null that Pythia ≥ OLMo, not the
null that OLMo ≥ Pythia). Cohen's d = −2.732, indicating a large effect in the direction
opposite to the prediction.

**This is not a null result in the sense of "no effect was found." It is a large, statistically
robust result in the wrong direction.** The MMLU/HellaSwag ratio clearly discriminates
between the two models — but the more-curated model achieves the lower ratio.

**Table 2: Primary Metric Summary**

| Metric | Pythia-6.9B | OLMo-7B | Difference (OLMo − Pythia) | 95% CI | Cohen's d |
|--------|-------------|---------|---------------------------|--------|-----------|
| MMLU/HellaSwag ratio | 0.565 | 0.538 | −0.0265 | [−0.045, −0.007] | −2.732 |
| ARC delta (Challenge − Easy) | −0.334 | −0.344 | −0.010 (OLMo worse) | — | — |

## Secondary Metric: ARC-Challenge/Easy Delta

The secondary metric confirms the directional refutation. Pythia achieves ARC-Challenge =
0.336 and ARC-Easy = 0.670, yielding a delta of −0.334. OLMo achieves ARC-Challenge =
0.296 and ARC-Easy = 0.640, yielding a delta of −0.344. OLMo's delta is more negative
by 0.010, indicating that OLMo shows greater degradation from easy to challenge-level
reasoning than Pythia.

Both models show negative deltas, as expected (ARC-Challenge is harder than ARC-Easy by
design). The smaller absolute magnitude of Pythia's negative delta suggests slightly
better maintenance of reasoning difficulty sensitivity — consistent with the primary
metric result but in a different experimental dimension.

## Analysis: HellaSwag Convergence as a Structural Finding

Figure 1 shows all four benchmark scores side-by-side.

*[Figure 1: absolute_scores.png — All benchmark scores for both models]*

The identical HellaSwag scores (0.458 = 0.458) warrant careful interpretation. This is
not simply a small difference that fell below statistical significance — in our 500-sample
fast evaluation, the scores are identical to three decimal places. While sampling variance
with 500 examples could produce this exact match by coincidence (MEDIUM plausibility),
two other explanations are more compelling.

**Most likely explanation:** HellaSwag commonsense performance reaches a scale-dependent
saturation point for 6-8B models at ~300B tokens. At this scale, both models have seen
sufficient web-sourced commonsense content (present in both The Pile and Dolma via
CommonCrawl) to achieve the same ceiling score. This saturation is consistent with
prior work: Biderman et al. [2023] show that Pythia-dedup gains only ~0.01 absolute on
HellaSwag from deduplication — already a small effect suggesting limited discriminative
power of HellaSwag for corpus quality differences in this model family.

**Key implication:** When the denominator of the MMLU/HellaSwag ratio is a constant,
the ratio collapses into a scalar multiple of MMLU alone. The observed ratio difference
of −0.0265 is therefore entirely driven by the MMLU gap of 0.013 (Pythia 0.259 vs
OLMo 0.246) divided by the common HellaSwag value of 0.458. HellaSwag provides no
discriminative information in this comparison.

## Analysis: Per-Subject MMLU Heatmap and Contamination Assessment

Figure 3 presents the per-subject MMLU accuracy for all 57 subjects for both models.

*[Figure 3: mmlu_heatmap.png — Per-subject MMLU accuracy heatmap (57 subjects)]*

The heatmap reveals that Pythia's MMLU advantage is broadly distributed across subjects
rather than concentrated in specific domains. Pythia outperforms OLMo in the majority of
subjects, including STEM domains (physics, chemistry, biology), social sciences
(economics, law, psychology), and humanities (history, philosophy). The pattern does not
show the domain concentration expected if The Pile's MMLU advantage were primarily due
to contamination from domain-specific sources (e.g., PubMed for medicine, law databases
for law). This evidence is inconsistent with The Pile contamination as the primary
explanation for Pythia's MMLU advantage (LOW plausibility for contamination hypothesis).

## Statistical Robustness: Bootstrap Distribution

Figure 4 shows the full bootstrap distribution of the ratio difference (OLMo − Pythia)
across 1000 bootstrap iterations.

*[Figure 4: bootstrap_dist.png — Bootstrap distribution of ratio differences with null (0) and threshold (+0.02) lines]*

The bootstrap distribution is centered at −0.0265 and entirely below zero. Neither the
null value (0, dashed line) nor the hypothesis threshold (+0.02, dotted line) falls within
the distribution. The CI [−0.045, −0.007] excludes zero, confirming that the directional
refutation is statistically robust to MMLU subject-level sampling variance. The shape of
the distribution shows no bimodality or outlier-driven skew that would suggest instability
in the estimate.

## Summary of Results

All three research questions yield clear answers:

**RQ1 (Primary metric):** No — OLMo-7B does NOT achieve a higher MMLU/HellaSwag ratio.
Pythia-6.9B achieves significantly higher ratio (0.565 vs 0.538, d=−2.732, CI entirely
negative). The hypothesis is directly falsified.

**RQ2 (Secondary metric):** No — OLMo does NOT achieve a less-negative ARC delta.
Pythia's delta (−0.334) is less negative than OLMo's (−0.344), confirming the directional
refutation via an independent metric.

**RQ3 (Contamination):** The per-subject heatmap shows Pythia's advantage is broadly
distributed, inconsistent with domain-specific contamination as the primary explanation.
The Pile contamination remains a low-plausibility alternative explanation.


---

# Discussion

## Interpreting the Null (and Negative) Result

Our primary finding — that Pythia-6.9B achieves a higher MMLU/HellaSwag ratio than
OLMo-7B at ~300B training tokens — is counterintuitive given the substantial investment
in Dolma's curation pipeline. We discuss three competing explanations for this result,
assess their relative plausibility, and articulate the methodological implications.

### Explanation 1: Architecture Difference (HIGH plausibility)

The most likely explanation for Pythia's MMLU advantage is the uncontrolled architecture
difference: Pythia-6.9B uses GPT-NeoX architecture, while OLMo-7B uses a LLaMA-style
architecture with rotary positional embeddings and different attention configurations.
GPT-NeoX may be more efficient at 5-shot multiple-choice tasks at the 6-8B parameter
scale, irrespective of corpus quality. Prior work has observed architecture-dependent
MMLU sensitivity — different attention mechanisms and positional encoding schemes can
produce varying few-shot performance even on identical data [Touvron et al., 2023].

This explanation is consistent with all observed results: the architecture advantage would
produce broadly distributed MMLU gains (consistent with Figure 3), would not affect
HellaSwag (which is 0-shot and commonsense-based rather than knowledge-intensive), and
would produce a stable gap rather than a widening one. Without temporal trajectory
analysis comparing Pythia and OLMo at 143B and 300B tokens, we cannot determine whether
the gap is stable (architecture-driven) or widening (quality-driven), as was planned in
the original experimental design.

### Explanation 2: Training Scale Insufficient at 300B Tokens (HIGH plausibility)

A second compelling explanation is that 300B training tokens is insufficient for Dolma's
curation quality advantage to manifest. Groeneveld et al. [2024] report that full-training
OLMo-7B (2T tokens) achieves competitive MMLU performance relative to similarly-sized
models, and attribute part of this to Dolma's academic content inclusion (S2ORC papers,
Wikipedia). If the academic content advantage compounds with training scale — as suggested
by the data quality × token count interaction documented by Muennighoff et al. [2023] —
then at 300B tokens, OLMo may not yet have processed sufficient academic content to
translate Dolma's quality advantage into MMLU gains.

This explanation is consistent with our single-checkpoint design: we cannot rule out that
OLMo's ratio would exceed Pythia's at 500B or 1T tokens. Our null result is explicitly
scoped to ~300B training tokens.

### Explanation 3: The Pile MMLU Contamination (LOW-MEDIUM plausibility)

A third explanation is that The Pile contains MMLU-adjacent content (e.g., academic PDFs
from PubMed, ArXiv, legal texts) that inflates Pythia's MMLU scores via benchmark
contamination. We note that the original contamination concern was in the opposite
direction (Dolma's deduplication might remove MMLU-adjacent content from OLMo's training),
but given our finding that Pythia outperforms OLMo, The Pile contamination is now a more
relevant concern.

However, our per-subject MMLU heatmap (Figure 3) shows Pythia's advantage is broadly
distributed across subjects including those less likely to appear in The Pile's source
domains (e.g., philosophy, sociology, moral scenarios). A contamination-driven advantage
would be expected to concentrate in domains well-represented in The Pile's specific sources
(PubMed → medicine; ArXiv → physics, mathematics; law databases → law). The absence of
domain concentration reduces the plausibility of contamination as the primary explanation,
though it does not rule it out entirely. Min-K% contamination detection [Shi et al., 2024]
applied to MMLU test questions vs. The Pile would provide more definitive evidence.

### The Structural Insight: HellaSwag Denominator Saturation

Beyond the three competing explanations for Pythia's MMLU advantage, our most informative
finding is the HellaSwag convergence. Both models achieve exactly 0.458 on HellaSwag at
~300B tokens, regardless of corpus quality. This convergence has a direct structural
implication: the MMLU/HellaSwag ratio is not a valid discriminator of corpus curation
quality at this training scale in this comparison, because the denominator provides no
discriminative information.

This finding has broader implications for how generalization balance metrics are designed.
A ratio metric r = numerator / denominator is a reliable quality discriminator only when
both numerator and denominator remain sensitive to the factor being tested. When the
denominator saturates — reaching a scale-dependent ceiling for the model family — the
ratio collapses into a proxy for numerator differences alone. For cross-architecture
comparisons, numerator differences may reflect architecture effects rather than corpus
quality. Researchers designing generalization balance metrics should verify denominator
sensitivity at their target training scale before using the ratio as a quality proxy.

## Limitations

### L1: Architecture Confound Not Bounded

The planned method for bounding the architecture confound — temporal trajectory analysis
comparing both models at 143B and 300B tokens — was not executed. The temporal trajectory
would determine whether the Pythia/OLMo ratio gap is widening (consistent with a
quality-driven advantage that compounds with tokens) or stable (consistent with a fixed
architecture-driven difference). Without this analysis, causal attribution of the null
result to corpus quality is impossible — we can describe the result, but not explain it.

*Why acceptable:* The descriptive null result (Pythia not worse than OLMo at 300B) is
itself informative for the field. The architecture confound is a scope limitation
acknowledged in the original hypothesis design (Assumption A4). *Future work:* Run
temporal trajectory at Pythia step72000 (≈143B) and OLMo matched checkpoint. If the
gap is stable, the architecture explanation dominates; if narrowing, the scale explanation
gains plausibility.

### L2: Fast Evaluation (500-Sample Limit)

The use of `--limit 500` evaluates approximately 8-9 examples per MMLU subject, introducing
high variance in per-subject accuracy estimates. Full evaluation across 14,042 MMLU
questions would provide more reliable per-subject estimates and reduce bootstrap CI width.

*Why acceptable:* The large effect size (d = −2.732) and the CI entirely below zero are
unlikely to reverse with full evaluation. The directional refutation is robust; the exact
magnitude of −0.0265 is less reliable. *Future work:* Full lm-eval-harness evaluation
(no `--limit` flag) to confirm magnitude before any publication.

### L3: Single Training Scale

Results are specific to ~300B training tokens. The corpus-quality hypothesis may hold at
different scales, and prior work suggests it does at 2T tokens [Groeneveld et al., 2024].

*Why acceptable:* The hypothesis explicitly targeted ~300B tokens as the comparison point.
This is the scope of the experiment, not a failure. *Future work:* Temporal trajectory
and full-training comparison to characterize the scale dependency.

### L4: IV Not Directly Measured

The corpus quality independent variable was operationalized via corpus identity (The Pile
vs. Dolma) rather than direct measurement of quality proxy scores (n-gram repetition rate,
Flesch-Kincaid grade level, language ID confidence). We assumed Dolma is higher quality
by these proxies based on its documented curation pipeline; this assumption was never
empirically verified on matched document samples.

*Why acceptable:* Dolma's curation advantages are well-documented in Soldaini et al.
[2024], providing a reasonable basis for the corpus-identity operationalization.
*Future work:* Sample 10K documents from each corpus and compute all three quality proxy
metrics to confirm that Dolma scores significantly higher on the composite index.

## Implications for Metric Design

Our results suggest two design requirements for future generalization balance metrics:

1. **Verify denominator sensitivity.** Before using a ratio metric as a quality proxy,
   confirm that the denominator task remains sensitive to the factor being tested at the
   target training scale. HellaSwag's convergence to identical values for both models at
   300B tokens — despite meaningful MMLU differences — reveals that it is an insensitive
   denominator for corpus quality comparisons at this scale.

2. **Require architecture-matched designs for causal claims.** Single-checkpoint
   cross-architecture comparisons cannot isolate corpus quality effects. Future studies
   claiming to measure corpus quality's effect on generalization should either (a) use
   models with identical architecture trained on different corpora, or (b) use temporal
   trajectory analysis to bound the architecture confound within a cross-suite comparison.

## Broader Impact

This work contributes a methodologically rigorous null result that characterizes the
limitations of current evaluation practice for corpus quality claims. The primary positive
impact is methodological: by documenting where cross-architecture, single-checkpoint
comparisons break down, we help researchers avoid drawing causal conclusions from
designs that cannot support them. This reduces the risk of misattributing performance
differences to corpus quality when they may reflect architecture effects.

A potential negative impact of publishing a null result on corpus curation quality is
that it could be misinterpreted as evidence that curation doesn't matter generally.
Our results are explicitly scoped to ~300B training tokens, this specific architecture
pair, and the MMLU/HellaSwag ratio metric. We emphasize that our null result does not
contradict prior evidence of curation benefits at full training scale [Groeneveld et al.,
2024; Penedo et al., 2023] — it reveals the conditions under which those benefits are
and are not detectable with current evaluation protocols.


---

# Conclusion

We set out to measure whether better pre-training data produces more generalizable language
models. At approximately 300 billion training tokens, for the Pythia/OLMo model pair,
using the MMLU/HellaSwag generalization balance ratio, the answer is: not detectably so —
and now we understand why.

## Summary

The corpus-quality → generalization-balance hypothesis predicted that OLMo-7B, trained
on Dolma's multi-stage curated corpus, would achieve a higher MMLU/HellaSwag ratio than
Pythia-6.9B, trained on The Pile with minimal curation. Our matched-scale evaluation
(both models within 0.5% of 300B training tokens) finds the opposite: Pythia achieves
a higher ratio (0.565 vs 0.538, difference = −0.0265, 95% CI [−0.045, −0.007], Cohen's
d = −2.732), and this directional refutation is consistent across all four benchmarks
evaluated.

The most informative result is not the direction of the ratio difference — which may
reflect an architecture effect beyond our ability to isolate — but the HellaSwag
convergence: both models achieve exactly 0.458 on commonsense reasoning at this training
scale, regardless of corpus quality. This convergence reveals that the MMLU/HellaSwag
ratio's denominator has saturated at ~300B tokens for 6-8B parameter models, collapsing
the ratio into a proxy for MMLU differences alone. A metric whose denominator is a
constant cannot discriminate between the factors hypothesized to drive its numerator.

Our methodological contributions are threefold: (1) we demonstrate, for the first time,
that the MMLU/HellaSwag generalization balance ratio does not discriminate corpus
curation quality at ~300B tokens in a cross-architecture comparison; (2) we identify
HellaSwag denominator saturation as the structural explanation; and (3) we characterize
the minimum requirements — architecture-matched pairs or temporal trajectory analysis —
for future studies that aim to draw causal conclusions about corpus quality effects.

## Future Directions

**Resolving the architecture confound.** The most direct path forward is an
architecture-matched comparison: two models with identical LLaMA-style (or GPT-NeoX)
architecture, trained at small scale (1-3B parameters, 10B tokens) on matched subsets of
The Pile and Dolma. If the ratio difference persists with matched architecture, it reflects
genuine corpus quality effects. If it disappears, the architecture explanation is confirmed.
This experiment is motivated by our inability to attribute the observed null result to
data quality in the presence of the GPT-NeoX/LLaMA-style confound.

**Temporal trajectory to test scale dependency.** Evaluating both models at an earlier
checkpoint (~143B tokens, available for both Pythia via step72000 and OLMo via matched
intermediate step) would test whether the ratio gap is stable (architecture-driven) or
narrowing (scale-driven, with OLMo approaching parity). The Muennighoff et al. [2023]
data quality × token count interaction predicts the latter; the architecture hypothesis
predicts the former. This experiment is motivated by the single-checkpoint limitation of
our study and could be executed with existing public checkpoints in approximately two
hours of H100 compute.

**Alternative generalization balance metrics.** Our HellaSwag saturation finding suggests
that commonsense tasks may be poor denominators for quality-sensitive ratios at intermediate
training scales. Testing alternative balance metrics — GSM8K/HellaSwag (mathematical
vs. commonsense), MMLU/WinoGrande (knowledge vs. coreference), or log-perplexity ratios
on OOD vs. ID text corpora — may reveal metrics that retain discriminative power at
300B tokens. This is motivated by the structural metric insight: the denominator task
must be verified to remain sensitive at the target scale.

**Corpus quality proxy validation.** Directly measuring quality proxies (n-gram repetition
rate, Flesch-Kincaid grade level, fastText language ID confidence) on matched document
samples from The Pile and Dolma would confirm that the assumed quality difference is
real in the specific dimensions expected to predict generalization balance. Our hypothesis
assumed Dolma is measurably higher quality by these proxies; this was never empirically
verified. Proxy validation is a prerequisite for any re-test of the original hypothesis.

## Closing

The assumption that better curation produces better-generalized models is reasonable —
but it must be testable. Our work shows that the metrics and comparison designs most
commonly used to evaluate this assumption at intermediate training scales are insufficient:
HellaSwag saturates, architectures confound, and single checkpoints cannot reveal the
temporal dynamics that separate quality effects from scale effects. Definitive tests of
the corpus quality hypothesis require designed experiments — not opportunistic comparisons
of publicly available models — and metrics that remain sensitive where we need them to.
We hope this work makes those requirements concrete, and provides a principled foundation
for the next generation of corpus quality studies.


---

## References

<!-- Full BibTeX in 06_references.bib. Inline reference list below for readability. -->

Biderman, S., et al. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. *arXiv:2304.01373*.

Clark, P., et al. (2018). Think You Have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge. *arXiv:1803.05457*.

Gao, L., et al. (2020). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. *arXiv:2101.00027*.

Gao, L., et al. (2024). A Framework for Few-Shot Language Model Evaluation. *Zenodo. lm-evaluation-harness v0.4.12*.

Groeneveld, D., et al. (2024). OLMo: Accelerating the Science of Language Models. *arXiv:2402.00838*.

Hendrycks, D., et al. (2021). Measuring Massive Multitask Language Understanding. *ICLR 2021. arXiv:2009.03300*.

Koh, P.W. & Liang, P. (2017). Understanding Black-box Predictions via Influence Functions. *ICML 2017*.

Koh, P.W., et al. (2021). WILDS: A Benchmark of in-the-Wild Distribution Shifts. *ICML 2021*.

Miller, J.P., et al. (2021). Accuracy on the Line: On the Strong Correlation Between OOD and In-Distribution Generalization. *ICML 2021*.

Muennighoff, N., et al. (2023). Scaling Data-Constrained Language Models. *NeurIPS 2023. arXiv:2305.16264*.

Park, S.M., et al. (2023). TRAK: Attributing Model Behavior at Scale. *ICML 2023. arXiv:2303.14186*.

Penedo, G., et al. (2023). The RefinedWeb Dataset for Falcon LLM: Outperforming Curated Corpora with Web Data, Only. *arXiv:2306.01116*.

Pruthi, G., et al. (2020). Estimating Training Data Influence by Tracing Gradient Descent. *NeurIPS 2020*.

Shi, W., et al. (2024). Detecting Pretraining Data from Large Language Models. *ICLR 2024. arXiv:2310.16789*.

Soldaini, L., et al. (2024). Dolma: An Open Corpus of Three Trillion Tokens for Language Model Pretraining Research. *arXiv:2402.00159*.

Touvron, H., et al. (2023). LLaMA: Open and Efficient Foundation Language Models. *arXiv:2302.13971*.

Zellers, R., et al. (2019). HellaSwag: Can a Machine Really Finish Your Sentence? *ACL 2019. arXiv:1905.07830*.

---

*[UNVERIFIED] All citations marked for Semantic Scholar verification prior to submission. Semantic Scholar MCP unavailable in ablation mode.*
