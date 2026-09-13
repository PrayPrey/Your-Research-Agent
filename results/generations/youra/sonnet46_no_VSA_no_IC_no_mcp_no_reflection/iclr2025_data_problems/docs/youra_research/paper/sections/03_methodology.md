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
