# Experimental Setup

We design experiments to test whether hallucination detection methods generalize across benchmarks under matched computational budgets. Our evaluation addresses the following research questions:

**RQ1:** Do semantic entropy and self-consistency detect hallucinations above random on each benchmark?

**RQ2:** Does method ranking differ across benchmarks (benchmark sensitivity)?

**RQ3:** Are observed differences statistically significant given our sample size?

## Datasets

We evaluate on two hallucination detection benchmarks with different hallucination definitions:

| Dataset | Samples | Task | Hallucination Definition | Why Chosen |
|---------|---------|------|--------------------------|------------|
| TruthfulQA | 817 | Factual QA | Deviation from "Best Answer" | Standard benchmark from Kuhn et al. |
| HaluEval-QA | 10,000 | Factual QA | Explicit hallucination labels | Different labeling methodology |

**TruthfulQA** [Lin et al., 2022] contains questions designed to elicit common misconceptions. Responses are labeled truthful if they match the annotated "Best Answer." This benchmark tests whether methods can distinguish factually grounded responses from plausible-sounding falsehoods.

**HaluEval-QA** [Li et al., 2023] provides paired correct and hallucinated responses with explicit binary labels. Unlike TruthfulQA's answer-matching approach, HaluEval directly annotates hallucination presence.

We include both benchmarks because their different labeling methodologies may interact differently with uncertainty-based detection—a hypothesis we test directly.

**Pilot Mode.** For pipeline validation, we sample N=20 questions per dataset. Full-scale evaluation requires the complete dataset splits.

## Baselines

We compare two uncertainty-based detection methods:

**Semantic Entropy** [Kuhn et al., 2023]: Clusters responses by semantic equivalence via bidirectional NLI, then computes entropy over the cluster distribution. Higher entropy indicates greater uncertainty.
- *Why included:* State-of-the-art on TruthfulQA; represents semantic-level uncertainty quantification.

**Self-Consistency** [Manakul et al., 2023]: Measures pairwise agreement across generated responses using BERTScore. Lower consistency indicates potential hallucination.
- *Why included:* Prominent alternative approach; represents surface-level consistency measurement.

Both methods share the same computational budget (N=10 generations per query) for fair comparison.

## Implementation Details

**Generation Model:** Meta-Llama-3-8B-Instruct via HuggingFace Transformers
- Temperature: 0.7
- Max tokens: 256
- Samples per query (N): 10

**Semantic Entropy Components:**
- NLI Model: DeBERTa-large-mnli [He et al., 2021]
- Entailment threshold: 0.5 (bidirectional)

**Self-Consistency Components:**
- Similarity metric: BERTScore F1 (roberta-large)

**Compute:** Single NVIDIA GPU, ~5 minutes for PoC mode (N=20 samples per dataset)

**Reproducibility:** Seed fixed at 42 for all experiments.

## Evaluation Metrics

**Primary Metric:** AUROC (Area Under ROC Curve)
- Measures discrimination ability independent of threshold selection
- Suitable for imbalanced datasets

**Confidence Intervals:** Bootstrap resampling (1,000 iterations) for 95% CI

**Gate Threshold:** AUROC > 0.55 (above random + 0.05 margin) as minimum threshold for "method works on this benchmark"

**Statistical Significance:** Due to small pilot sample size (N=20), we report confidence intervals rather than p-values. Wide intervals indicate insufficient power for definitive conclusions.
