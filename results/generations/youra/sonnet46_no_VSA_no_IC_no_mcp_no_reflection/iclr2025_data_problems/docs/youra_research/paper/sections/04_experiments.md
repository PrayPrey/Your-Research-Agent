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
